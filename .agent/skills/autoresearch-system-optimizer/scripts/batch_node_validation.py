#!/usr/bin/env python3
"""Run one bounded validation invocation for the optimizer."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from summarize_validation_results import parse_agent_result


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
PROMPT_PATH = SKILL_DIR / "references" / "node_validation.md"
RESULTS_BASE_DIR = REPO_ROOT / "_reference" / "test" / "v2" / "results"
AGENTS_CONFIG = SKILL_DIR / "config" / "agents.yaml"
DEFAULT_TIMEOUT = 1800


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_prompt(prompt_path: Path) -> str:
    if not prompt_path.exists():
        raise FileNotFoundError(f"missing prompt: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def build_prompt(base_prompt: str, *, target: str | None, role: str = "evaluator", teammate_index: int | None = None) -> str:
    header_lines = [
        "# Optimizer Validation Invocation",
        f"- generated_at: {datetime.now().isoformat()}",
        f"- repo_root: {REPO_ROOT}",
        f"- role: {role}",
    ]
    if target:
        header_lines.append(f"- frozen_target: {target}")
    if teammate_index is not None:
        header_lines.append(f"- teammate_index: {teammate_index}")
    header_lines.extend(["", "---", ""])
    return "\n".join(header_lines) + base_prompt


def resolve_backend(args: argparse.Namespace, config: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    requested = args.backend or str(config.get("default_backend") or "local_command")
    backends = config.get("backends") if isinstance(config.get("backends"), dict) else {}
    backend = backends.get(requested)
    if not isinstance(backend, dict) or not backend.get("enabled", False):
        raise ValueError(f"backend `{requested}` is not enabled")
    return requested, backend


def render_template(template: list[str], prompt: str) -> list[str]:
    return [item.replace("{prompt}", prompt) for item in template]


def resolve_command(
    backend_name: str,
    backend: dict[str, Any],
    *,
    prompt: str,
    agent_command: str | None,
    dry_run: bool,
) -> list[str]:
    if backend_name == "local_command":
        template = backend.get("command_template")
        if not isinstance(template, list) or not template:
            if dry_run:
                return ["<explicit-local-command-required>", "{prompt}"]
            raise ValueError("local_command backend requires a non-empty command_template in agents.yaml")
        return render_template([str(item) for item in template], prompt)

    if backend_name == "external_agent":
        command_templates = backend.get("command_templates") if isinstance(backend.get("command_templates"), dict) else {}
        agent_name = agent_command or str(backend.get("default_agent") or "")
        template = command_templates.get(agent_name)
        if isinstance(template, list) and template:
            return render_template([str(item) for item in template], prompt)
        if agent_command:
            return [agent_command, "-p", prompt]
        raise ValueError("external_agent backend requires a command template or --agent-command")

    raise ValueError(f"unsupported backend: {backend_name}")


def setup_result_dir(results_dir: Path, *, prefix: str = "") -> Path:
    result_dir = results_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_agent"
    if prefix:
        result_dir = results_dir / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}_agent"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def write_manifest(results_dir: Path, payload: dict[str, Any]) -> None:
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "validation_manifest.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def run_validation(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def run_one(command: list[str], *, prompt: str, result_dir: Path, metadata: dict[str, Any], timeout: int) -> dict[str, Any]:
    completed = run_validation(command, timeout=timeout)
    combined_output = completed.stdout
    if completed.stderr:
        combined_output = combined_output + ("\n" if combined_output and not combined_output.endswith("\n") else "") + completed.stderr
    metadata = {
        **metadata,
        "command": command,
        "return_code": completed.returncode,
        "status": "completed" if completed.returncode == 0 else "failed",
        "finished_at": datetime.now().isoformat(),
    }
    (result_dir / "prompt.md").write_text(prompt, encoding="utf-8")
    (result_dir / "result.md").write_text(combined_output, encoding="utf-8")
    (result_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"result_dir": str(result_dir), "return_code": completed.returncode, "status": metadata["status"]}


def finding_key(finding: dict[str, Any]) -> tuple[str, str]:
    root = str(finding.get("root_cause_id") or "").strip()
    surface = str(finding.get("fix_surface") or "").strip()
    fallback = str(finding.get("finding_id") or finding.get("summary") or finding.get("claim_or_surface") or "unknown").strip()
    if root:
        return root, ""
    if surface:
        return "", surface
    return fallback or "unknown", ""


def ensure_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def consensus_severity(rows: list[dict[str, Any]]) -> str:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    values = [str(row.get("severity") or "medium") for row in rows]
    return max(values, key=lambda item: order.get(item, 0)) if values else "medium"


def consensus_confidence(rows: list[dict[str, Any]]) -> str:
    order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    values = [str(row.get("confidence") or "unknown") for row in rows]
    return max(values, key=lambda item: order.get(item, 0)) if values else "unknown"


def build_teammate_consensus(results_dir: Path, run_results: list[dict[str, Any]], *, target: str | None, enabled: bool) -> dict[str, Any]:
    parsed_results: list[dict[str, Any]] = []
    failed_agents: list[str] = []
    unparseable_agents: list[str] = []
    for item in run_results:
        result_dir = Path(str(item.get("result_dir") or ""))
        agent_name = result_dir.name or "unknown"
        if int(item.get("return_code", 1)) != 0:
            failed_agents.append(agent_name)
        parsed = parse_agent_result(result_dir) if result_dir.exists() else None
        if parsed:
            parsed_results.append(parsed)
        else:
            unparseable_agents.append(agent_name)

    threshold = (len(run_results) // 2) + 1 if run_results else 1
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    missing_payload_agents: list[str] = []
    for result in parsed_results:
        if not result.get("structured_payload"):
            missing_payload_agents.append(str(result.get("agent_name") or "unknown"))
        for finding in result.get("maintenance_findings", []):
            grouped[finding_key(finding)].append({"agent_name": result.get("agent_name"), **finding})

    majority_findings: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    for (root_cause_id, fix_surface), rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0][0], item[0][1])):
        support_agents = sorted(str(row.get("agent_name") or "unknown") for row in rows)
        evidence_paths = sorted({path for row in rows for path in ensure_list_of_strings(row.get("evidence_paths"))})
        fix_surfaces = sorted({str(row.get("fix_surface") or "").strip() for row in rows if str(row.get("fix_surface") or "").strip()})
        item = {
            "root_cause_id": root_cause_id,
            "fix_surface": fix_surface or (fix_surfaces[0] if len(fix_surfaces) == 1 else ""),
            "fix_surfaces": fix_surfaces,
            "support_count": len(rows),
            "support_agents": support_agents,
            "majority_required": threshold,
            "severity": consensus_severity(rows),
            "confidence": consensus_confidence(rows),
            "evidence_paths": evidence_paths,
        }
        if len(rows) >= threshold:
            majority_findings.append(item)
        else:
            disagreements.append(item)

    payload = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "enabled": enabled,
            "target": target,
            "evaluator_count": len(run_results),
            "parsed_evaluator_count": len(parsed_results),
            "majority_threshold": threshold,
            "consensus_policy": "majority_same_root_cause_or_fix_surface",
        },
        "majority_findings": majority_findings,
        "disagreements": disagreements,
        "failed_agents": failed_agents,
        "unparseable_agents": unparseable_agents,
        "missing_structured_payload_agents": missing_payload_agents,
        "auto_apply_gate": {
            "majority_passed": bool(majority_findings) and not failed_agents and not unparseable_agents and not missing_payload_agents,
            "downgrade_reason": (
                "agent_failed"
                if failed_agents
                else "unparseable_result"
                if unparseable_agents
                else "missing_structured_payload"
                if missing_payload_agents
                else None
            ),
        },
    }
    (results_dir / "teammate_consensus.yaml").write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one bounded validation invocation for the optimizer.")
    parser.add_argument("-p", "--prompt", type=Path, default=PROMPT_PATH, help="Validation prompt path.")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_BASE_DIR, help="Validation output directory.")
    parser.add_argument("--target", type=str, default=None, help="Frozen target path for this validation step.")
    parser.add_argument("--backend", choices=("local_command", "external_agent"), default=None, help="Validation backend.")
    parser.add_argument("-a", "--agent-command", type=str, default=None, help="External agent command or template key.")
    parser.add_argument("--enable-teammates", action="store_true", help="Run optional teammate evaluator invocations.")
    parser.add_argument("--teammate-agent", default="claude_code", help="External teammate agent template key.")
    parser.add_argument("-t", "--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds.")
    parser.add_argument("-n", "--num-agents", type=int, default=1, help="Number of teammate evaluators when --enable-teammates is used.")
    parser.add_argument("-w", "--max-workers", type=int, default=None, help="Maximum concurrent teammate evaluator invocations.")
    parser.add_argument("-q", "--quiet", action="store_true", help="Reduce stdout noise.")
    parser.add_argument("--dry-run", action="store_true", help="Show the invocation plan without running validation.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_yaml(AGENTS_CONFIG)
    backend_name, backend = resolve_backend(args, config)
    base_prompt = load_prompt(args.prompt)
    prompt = build_prompt(base_prompt, target=args.target)

    supports_parallel = bool(config.get("supports_parallel_validation", False))
    if args.enable_teammates and backend_name != "external_agent":
        print("error: teammate evaluation requires --backend external_agent", file=sys.stderr)
        return 1
    if not args.enable_teammates and not supports_parallel and (args.num_agents != 1 or (args.max_workers not in (None, 1))):
        if args.dry_run:
            pass
        else:
            print("error: bounded validation only supports one invocation per run", file=sys.stderr)
            return 1

    command = resolve_command(
        backend_name,
        backend,
        prompt=prompt,
        agent_command=args.agent_command or (args.teammate_agent if args.enable_teammates else None),
        dry_run=args.dry_run,
    )
    requested_agents = max(1, int(args.num_agents or 1))
    max_workers = int(args.max_workers or requested_agents)

    manifest = {
        "generated_at": datetime.now().isoformat(),
        "backend": backend_name,
        "target": args.target,
        "dry_run": args.dry_run,
        "supports_parallel_validation": supports_parallel,
        "teammate_evaluation_enabled": args.enable_teammates,
        "teammate_agent": args.teammate_agent if args.enable_teammates else None,
        "requested_num_agents": requested_agents,
        "requested_max_workers": max_workers,
        "command_preview": command,
        "results_dir": str(args.results_dir),
    }

    if args.dry_run:
        if not args.quiet:
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0

    args.results_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    if args.enable_teammates:
        teammate_dir = args.results_dir / "teammate_reviews"
        teammate_dir.mkdir(parents=True, exist_ok=True)
        futures = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for index in range(1, requested_agents + 1):
                teammate_prompt = build_prompt(base_prompt, target=args.target, role="teammate_evaluator", teammate_index=index)
                teammate_command = resolve_command(
                    backend_name,
                    backend,
                    prompt=teammate_prompt,
                    agent_command=args.agent_command or args.teammate_agent,
                    dry_run=False,
                )
                result_dir = setup_result_dir(teammate_dir, prefix=f"teammate_{index:02d}")
                metadata = {
                    "generated_at": datetime.now().isoformat(),
                    "backend": backend_name,
                    "target": args.target,
                    "role": "teammate_evaluator",
                    "teammate_index": index,
                    "teammate_agent": args.teammate_agent,
                }
                futures[executor.submit(run_one, teammate_command, prompt=teammate_prompt, result_dir=result_dir, metadata=metadata, timeout=args.timeout)] = result_dir
            for future in as_completed(futures):
                results.append(future.result())
        consensus = build_teammate_consensus(args.results_dir, results, target=args.target, enabled=True)
        manifest["teammate_consensus"] = str(args.results_dir / "teammate_consensus.yaml")
        manifest["teammate_majority_passed"] = consensus.get("auto_apply_gate", {}).get("majority_passed")
    else:
        result_dir = setup_result_dir(args.results_dir)
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "backend": backend_name,
            "target": args.target,
            "role": "evaluator",
        }
        results.append(run_one(command, prompt=prompt, result_dir=result_dir, metadata=metadata, timeout=args.timeout))

    manifest["results"] = results
    write_manifest(args.results_dir, manifest)

    if not args.quiet:
        print(f"backend: {backend_name}")
        print(f"target: {args.target or '<none>'}")
        print(f"results_dir: {args.results_dir}")

    return 1 if any(int(item.get("return_code", 1)) != 0 for item in results) else 0


if __name__ == "__main__":
    sys.exit(main())
