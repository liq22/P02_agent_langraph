#!/usr/bin/env python3
"""Run one bounded dual-lane optimization cycle for the AutoResearch system."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
CONFIG_DIR = SKILL_DIR / "config"
DEFAULT_POLICY = CONFIG_DIR / "optimization_loop.yaml"
DEFAULT_RESULTS_ROOT = REPO_ROOT / "_reference" / "test" / "v2" / "results"
GRAPH_SKILL_PATH = REPO_ROOT / ".agent" / "skills" / "graph_driven_research_orchestrator" / "SKILL.md"
GRAPH_PATH = REPO_ROOT / "backend" / "graph" / "graph.json"
GRAPH_STATUS_PATH = REPO_ROOT / "backend" / "graph" / "graph_status.json"
PHASE_RE = re.compile(r"(P[0-4])_")


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def run_command(cmd: list[str], *, dry_run: bool) -> dict[str, Any]:
    if dry_run:
        return {"status": "planned", "command": cmd, "returncode": 0, "stdout": "", "stderr": ""}
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO_ROOT)
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "command": cmd,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def scope_target(scope: str) -> str | None:
    if scope.startswith("node:"):
        candidate = scope.split(":", 1)[1].strip()
        return candidate or None
    return None


def scope_phase(scope: str) -> str | None:
    if scope.startswith("phase:"):
        candidate = scope.split(":", 1)[1].strip()
        return candidate or None
    return None


def node_phase(value: str | None) -> str | None:
    if not value:
        return None
    match = PHASE_RE.search(value)
    return match.group(1) if match else None


def graph_node_path(graph_payload: dict[str, Any], node_id: str | None) -> str | None:
    if not node_id:
        return None
    nodes = graph_payload.get("nodes")
    if isinstance(nodes, dict):
        node = nodes.get(node_id)
        if isinstance(node, dict):
            path = node.get("path")
            if isinstance(path, str) and path.strip():
                return path.strip()
    if node_id.startswith("research/"):
        return node_id
    return None


def run_graph_refresh(*, dry_run: bool) -> dict[str, Any]:
    refresh_cmd = [sys.executable, str(REPO_ROOT / "scripts" / "refresh_views.py"), "--mode", "graph_only"]
    return run_command(refresh_cmd, dry_run=dry_run)


def resolve_target(explicit_target: str | None, *, scope: str, dry_run: bool) -> dict[str, Any]:
    if explicit_target:
        return {
            "selected_target": explicit_target,
            "selection_source": "explicit_target",
            "graph_skill_used": False,
            "graph_preview_used": False,
            "graph_contract_status": "not_used",
            "graph_refresh_status": "not_required",
            "graph_skill_path": str(GRAPH_SKILL_PATH.relative_to(REPO_ROOT)),
            "selected_node_id": None,
            "next_node_id": None,
            "notes": [],
        }

    if not GRAPH_SKILL_PATH.exists():
        raise FileNotFoundError(f"missing graph skill truth: {GRAPH_SKILL_PATH}")

    refresh_status = "not_required"
    refresh_result = None
    if not GRAPH_PATH.exists() or not GRAPH_STATUS_PATH.exists():
        refresh_result = run_graph_refresh(dry_run=dry_run)
        refresh_status = refresh_result["status"]
    elif load_json(GRAPH_STATUS_PATH).get("refresh_ok") is False:
        refresh_result = run_graph_refresh(dry_run=dry_run)
        refresh_status = refresh_result["status"]

    if refresh_result and refresh_result.get("returncode") not in (0, None):
        raise RuntimeError("graph refresh failed before target freeze")
    if not GRAPH_PATH.exists() or not GRAPH_STATUS_PATH.exists():
        raise FileNotFoundError("graph artifacts unavailable after graph contract step")

    graph_payload = load_json(GRAPH_PATH)
    graph_status_payload = load_json(GRAPH_STATUS_PATH)
    ready_nodes = [str(item) for item in graph_status_payload.get("ready_nodes", []) if isinstance(item, str)]
    phase = scope_phase(scope)
    next_node_id = graph_status_payload.get("next_node")
    selected_node_id = str(next_node_id) if isinstance(next_node_id, str) and next_node_id else None
    if phase:
        phase_ready_nodes = [node_id for node_id in ready_nodes if node_phase(node_id) == phase]
        if selected_node_id not in phase_ready_nodes:
            selected_node_id = phase_ready_nodes[0] if phase_ready_nodes else None
    elif selected_node_id is None and ready_nodes:
        selected_node_id = ready_nodes[0]
    selected_target = graph_node_path(graph_payload, selected_node_id)
    notes = [
        "No explicit target was provided.",
        "Target was frozen via the `$graph-driven-research-orchestrator` runtime contract.",
    ]
    if phase:
        notes.append(f"Phase-constrained selection was requested for `{phase}`.")
    if selected_node_id:
        notes.append(f"Graph selected node id `{selected_node_id}`.")
    if selected_target:
        notes.append(f"Frozen target path is `{selected_target}`.")
    return {
        "selected_target": selected_target,
        "selection_source": "graph_driven_research_orchestrator_runtime_contract",
        "graph_skill_used": True,
        "graph_preview_used": False,
        "graph_contract_status": "target_frozen" if selected_target else "no_target_available",
        "graph_refresh_status": refresh_status,
        "graph_skill_path": str(GRAPH_SKILL_PATH.relative_to(REPO_ROOT)),
        "selected_node_id": selected_node_id,
        "next_node_id": str(next_node_id) if isinstance(next_node_id, str) and next_node_id else None,
        "notes": notes,
    }


def derive_recheck_commands(applied_paths: list[str], policy: dict[str, Any]) -> list[str]:
    if not applied_paths:
        return []
    if any(path.startswith(".agent/skills/") or "skill_catalog.yaml" in path for path in applied_paths):
        return [str(item) for item in policy.get("post_apply_rechecks", {}).get("skill_surface", [])]
    if any(path.startswith("_reference/test/") for path in applied_paths):
        return [str(item) for item in policy.get("post_apply_rechecks", {}).get("validation_surface", [])]
    if any(path.startswith("research/") for path in applied_paths):
        return [str(item) for item in policy.get("post_apply_rechecks", {}).get("node_prompt_surface", [])]
    return []


def summarize_lane_status(actions_payload: dict[str, Any], apply_summary: dict[str, Any], *, dry_run: bool, apply_mode: str) -> tuple[str, str]:
    actions = actions_payload.get("actions") if isinstance(actions_payload.get("actions"), list) else []
    human_tickets = actions_payload.get("human_gate_tickets") if isinstance(actions_payload.get("human_gate_tickets"), list) else []
    applied_paths = [str(item) for item in apply_summary.get("applied_paths", [])]
    planned_paths = [str(item) for item in apply_summary.get("planned_paths", [])]
    manual_tickets = [str(item) for item in apply_summary.get("manual_tickets", [])]

    if dry_run:
        maintenance_status = "dry_run_completed"
    elif apply_mode == "none":
        maintenance_status = "advisory_only"
    elif applied_paths:
        maintenance_status = "auto_applied"
    elif planned_paths:
        maintenance_status = "planned_only"
    elif any(str(action.get("disposition")) == "no_change" for action in actions):
        maintenance_status = "no_change"
    elif manual_tickets:
        maintenance_status = "manual_only"
    else:
        maintenance_status = "no_auto_apply_eligible_fix"

    if any(str(ticket.get("research_gate_status")) == "exploratory" for ticket in human_tickets):
        research_status = "exploratory"
    elif human_tickets:
        research_status = "human_review_required"
    else:
        research_status = "advisory_only"
    return maintenance_status, research_status


def render_cycle_template(value: str, *, cycle_dir: Path) -> str:
    return value.replace("{cycle_dir}", str(cycle_dir))


def load_structured_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        if path.suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
        else:
            payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def compact_advisory_summary(check_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    if check_id == "redteam":
        return {
            "overall": payload.get("overall"),
            "metrics": payload.get("metrics"),
        }
    if check_id == "single_node_metrics":
        return {
            "total_cases": payload.get("total_cases"),
            "passed_cases": payload.get("passed_cases"),
            "failed_cases": payload.get("failed_cases"),
            "metrics_summary": payload.get("metrics_summary"),
        }
    return payload


def run_advisory_rechecks(policy: dict[str, Any], *, cycle_dir: Path, dry_run: bool, skip_recheck: bool) -> tuple[list[dict[str, Any]], bool]:
    if skip_recheck:
        return [], False
    checks = policy.get("advisory_rechecks") if isinstance(policy.get("advisory_rechecks"), dict) else {}
    results: list[dict[str, Any]] = []
    failed = False
    for check_id, raw_spec in checks.items():
        if not isinstance(raw_spec, dict) or not raw_spec.get("enabled", False):
            continue
        raw_command = str(raw_spec.get("command") or "").strip()
        if not raw_command:
            continue
        summary_path = Path(render_cycle_template(str(raw_spec.get("summary_path") or ""), cycle_dir=cycle_dir))
        command = render_cycle_template(raw_command, cycle_dir=cycle_dir)
        result = run_command(["/bin/bash", "-lc", command], dry_run=dry_run)
        required = bool(raw_spec.get("required", True))
        check_failed = required and result.get("returncode") not in (0, None)
        failed = failed or check_failed
        summary = load_structured_summary(summary_path) if not dry_run else {}
        results.append(
            {
                "id": str(check_id),
                "command": command,
                "status": result["status"],
                "returncode": result.get("returncode"),
                "required": required,
                "summary_path": str(summary_path) if str(summary_path) else None,
                "summary": compact_advisory_summary(str(check_id), summary),
            }
        )
    return results, failed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one bounded optimizer cycle.")
    parser.add_argument("--scope", default="repo", help="repo, phase:P0, or node:<path>")
    parser.add_argument("--target", default=None, help="Explicit target path.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY, help="Optimization policy YAML.")
    parser.add_argument("--validation-results-dir", type=Path, default=None, help="Existing validation results to reuse.")
    parser.add_argument("--actions-file", type=Path, default=None, help="Optional action plan override.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT, help="Cycle results root.")
    parser.add_argument("--agents", type=int, default=None, help="Override agent count.")
    parser.add_argument("--max-workers", type=int, default=None, help="Override validation worker count.")
    parser.add_argument("--max-cycles", type=int, default=None, help="Override policy cycle count.")
    parser.add_argument("--apply", choices=("low-risk", "none"), default=None)
    parser.add_argument("--backend", choices=("local_command", "external_agent"), default=None)
    parser.add_argument("--enable-teammates", action="store_true", help="Enable optional Claude Code teammate evaluators.")
    parser.add_argument("--teammate-agent", default="claude_code", help="External teammate agent template key.")
    parser.add_argument("--runner", choices=("repo-local", "external-batch"), default=None, help=argparse.SUPPRESS)
    parser.add_argument("--dry-run", action="store_true", help="Plan commands without running external tools.")
    parser.add_argument("--skip-recheck", action="store_true", help="Skip the recheck stage.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = load_yaml(args.policy)
    apply_mode = args.apply or ("none" if str(policy.get("default_mode") or "advisory") == "advisory" else "low-risk")
    backend = args.backend
    if backend is None and args.runner:
        backend = "local_command" if args.runner == "repo-local" else "external_agent"
    if backend is None and args.enable_teammates:
        backend = "external_agent"
    backend = backend or str(policy.get("default_validation_backend") or "local_command")
    if args.enable_teammates and backend != "external_agent":
        raise RuntimeError("teammate evaluation requires backend=external_agent")
    cycle_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    cycle_dir = args.results_root / cycle_id
    validation_dir = cycle_dir / "01_validation"
    maintenance_scorecards_dir = cycle_dir / "03_maintenance_scorecards"
    research_scorecards_dir = cycle_dir / "04_research_rigor_scorecards"
    actions_path = cycle_dir / "05_optimization_actions.yaml"
    human_tickets_path = cycle_dir / "06_human_gate_tickets.yaml"
    apply_report = cycle_dir / "07_applied_changes.md"
    apply_summary = cycle_dir / "07_apply_summary.yaml"
    recheck_report = cycle_dir / "08_recheck.md"
    cycle_verdict_path = cycle_dir / "09_cycle_verdict.yaml"
    generated_plan_path = cycle_dir / "_planner_actions.generated.yaml"
    cycle_dir.mkdir(parents=True, exist_ok=True)

    frozen_target = args.target or scope_target(args.scope)
    target_info = resolve_target(frozen_target, scope=args.scope, dry_run=args.dry_run)
    if not target_info["selected_target"]:
        raise RuntimeError("no actionable target after target freeze")
    scope_payload = {
        "cycle_id": cycle_id,
        "generated_at": datetime.now().isoformat(),
        "scope": args.scope,
        "selected_target": target_info["selected_target"],
        "selected_node_id": target_info["selected_node_id"],
        "next_node_id": target_info["next_node_id"],
        "selection_source": target_info["selection_source"],
        "graph_skill_used": target_info["graph_skill_used"],
        "graph_preview_used": target_info["graph_preview_used"],
        "graph_contract_status": target_info["graph_contract_status"],
        "graph_refresh_status": target_info["graph_refresh_status"],
        "graph_skill_path": target_info["graph_skill_path"],
        "notes": target_info["notes"],
        "backend": backend,
        "apply_mode": apply_mode,
        "teammate_evaluation_enabled": args.enable_teammates,
        "teammate_agent": args.teammate_agent if args.enable_teammates else None,
        "dry_run": args.dry_run,
        "default_mode": policy.get("default_mode"),
        "max_targets_per_cycle": policy.get("max_targets_per_cycle", 1),
        "graph_target_freeze_once": bool(policy.get("graph_target_freeze_once", True)),
    }
    write_yaml(cycle_dir / "00_scope.yaml", scope_payload)

    validation_source = args.validation_results_dir
    validation_invocation = None
    if validation_source is None:
        validation_source = validation_dir
        validation_dir.mkdir(parents=True, exist_ok=True)
        batch_cmd = [
            sys.executable,
            str(SKILL_DIR / "scripts" / "batch_node_validation.py"),
            "--prompt",
            str(REPO_ROOT / str(policy["node_validation_prompt"])),
            "--results-dir",
            str(validation_dir),
            "--backend",
            backend,
            "--target",
            str(target_info["selected_target"]),
        ]
        if args.enable_teammates:
            teammate_policy = policy.get("optional_teammate_evaluation") if isinstance(policy.get("optional_teammate_evaluation"), dict) else {}
            batch_cmd.extend(["--enable-teammates", "--teammate-agent", args.teammate_agent])
            if args.agents is not None:
                batch_cmd.extend(["--num-agents", str(args.agents)])
            else:
                batch_cmd.extend(["--num-agents", str(teammate_policy.get("default_count", 3))])
            if args.max_workers is not None:
                batch_cmd.extend(["--max-workers", str(args.max_workers)])
            else:
                batch_cmd.extend(["--max-workers", str(teammate_policy.get("default_count", 3))])
        elif args.agents is not None:
            batch_cmd.extend(["--num-agents", str(args.agents)])
        elif policy.get("default_agent_count") is not None:
            batch_cmd.extend(["--num-agents", str(policy.get("default_agent_count", 1))])
        if not args.enable_teammates and args.max_workers is not None:
            batch_cmd.extend(["--max-workers", str(args.max_workers)])
        elif not args.enable_teammates and policy.get("default_max_workers") is not None:
            batch_cmd.extend(["--max-workers", str(policy.get("default_max_workers", 1))])
        if args.dry_run:
            batch_cmd.append("--dry-run")
        validation_invocation = run_command(batch_cmd, dry_run=False)
        (validation_dir / "invocation.json").write_text(json.dumps(validation_invocation, indent=2, ensure_ascii=False), encoding="utf-8")
        if validation_invocation.get("returncode") not in (0, None):
            (cycle_dir / "02_summary.md").write_text(
                "# Summary\n\nValidation failed; planning and apply stages were not run.\n",
                encoding="utf-8",
            )
            verdict = {
                "cycle_id": cycle_id,
                "generated_at": datetime.now().isoformat(),
                "scope": args.scope,
                "cycle_mode": "dry_run" if args.dry_run else "validation_failed",
                "backend": backend,
                "apply_mode": apply_mode,
                "teammate_evaluation_enabled": args.enable_teammates,
                "teammate_agent": args.teammate_agent if args.enable_teammates else None,
                "selected_target": target_info["selected_target"],
                "selection_source": target_info["selection_source"],
                "targets_validated": str(validation_source),
                "actions_planned": None,
                "actions_applied": [],
                "manual_tickets": [],
                "recheck_passed": False,
                "continue_recommended": False,
                "stop_reason": "validation_failed",
                "validation_invocation_status": validation_invocation.get("status"),
                "validation_returncode": validation_invocation.get("returncode"),
                "summary_status": "not_run",
                "planner_status": "not_run",
                "apply_status": "not_run",
                "maintenance_lane_status": "validation_failed",
                "research_lane_status": "advisory_only",
            }
            write_yaml(cycle_verdict_path, verdict)
            print(f"cycle_dir: {cycle_dir}")
            print(f"cycle_verdict: {cycle_verdict_path}")
            return 1

    summary_cmd = [
        sys.executable,
        str(SKILL_DIR / "scripts" / "summarize_validation_results.py"),
        "--results-dir",
        str(validation_source),
        "--output",
        str(cycle_dir / "02_summary.md"),
    ]
    summary_result = run_command(summary_cmd, dry_run=args.dry_run)
    if args.dry_run:
        (cycle_dir / "02_summary.md").write_text("# Summary\n\nDry run: summarize_validation_results.py was not executed.\n", encoding="utf-8")

    planner_cmd = [
        sys.executable,
        str(SKILL_DIR / "scripts" / "score_and_plan_actions.py"),
        "--results-dir",
        str(validation_source),
        "--output",
        str(generated_plan_path),
        "--maintenance-scorecards-dir",
        str(maintenance_scorecards_dir),
        "--research-scorecards-dir",
        str(research_scorecards_dir),
    ]
    planner_result = run_command(planner_cmd, dry_run=args.dry_run)
    planner_payload = load_yaml(generated_plan_path) if generated_plan_path.exists() else {"actions": [], "human_gate_tickets": [], "summary": {}}

    if args.actions_file is None:
        effective_payload = planner_payload
    else:
        effective_payload = load_yaml(args.actions_file)
    write_yaml(actions_path, effective_payload)

    human_ticket_payload = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "source": str(args.actions_file) if args.actions_file else str(generated_plan_path),
        },
        "tickets": effective_payload.get("human_gate_tickets") if isinstance(effective_payload.get("human_gate_tickets"), list) else planner_payload.get("human_gate_tickets", []),
    }
    write_yaml(human_tickets_path, human_ticket_payload)

    applier_cmd = [
        sys.executable,
        str(SKILL_DIR / "scripts" / "apply_low_risk_actions.py"),
        "--actions",
        str(actions_path),
        "--policy",
        str(args.policy),
        "--report",
        str(apply_report),
        "--summary",
        str(apply_summary),
    ]
    if apply_mode == "none" or args.dry_run:
        applier_cmd.append("--dry-run")
    apply_result = run_command(applier_cmd, dry_run=False)

    apply_payload = load_yaml(apply_summary) if apply_summary.exists() else {}
    applied_paths = [str(item) for item in apply_payload.get("applied_paths", [])]
    manual_tickets = [str(item) for item in apply_payload.get("manual_tickets", [])]
    failures = [str(item) for item in apply_payload.get("failures", [])]
    immutable_anchor_hits = [str(item) for item in apply_payload.get("immutable_anchor_hits", [])]

    recheck_commands = [] if args.skip_recheck else derive_recheck_commands(applied_paths, policy)
    recheck_lines = ["# Recheck", ""]
    recheck_failed = False
    for raw_command in recheck_commands:
        command = ["/bin/bash", "-lc", raw_command]
        result = run_command(command, dry_run=args.dry_run)
        recheck_lines.append(f"## `{raw_command}`")
        recheck_lines.append(f"- status: {result['status']}")
        if result.get("returncode") not in (0, None):
            recheck_failed = True
        if result.get("stdout"):
            recheck_lines.extend(["", "```text", result["stdout"].strip(), "```"])
        if result.get("stderr"):
            recheck_lines.extend(["", "```text", result["stderr"].strip(), "```"])
        recheck_lines.append("")
    if not recheck_commands:
        recheck_lines.append("- none")
    advisory_results, advisory_failed = run_advisory_rechecks(policy, cycle_dir=cycle_dir, dry_run=args.dry_run, skip_recheck=args.skip_recheck)
    if advisory_results:
        recheck_lines.extend(["", "## Advisory Deterministic Checks", ""])
        for item in advisory_results:
            recheck_lines.append(f"### `{item['id']}`")
            recheck_lines.append(f"- status: {item['status']}")
            recheck_lines.append(f"- required: {item['required']}")
            recheck_lines.append(f"- summary_path: {item['summary_path']}")
            recheck_lines.append("")
    recheck_failed = recheck_failed or advisory_failed
    recheck_report.write_text("\n".join(recheck_lines), encoding="utf-8")

    maintenance_lane_status, research_lane_status = summarize_lane_status(
        effective_payload,
        apply_payload,
        dry_run=args.dry_run,
        apply_mode=apply_mode,
    )
    summary = effective_payload.get("summary") if isinstance(effective_payload.get("summary"), dict) else {}
    human_tickets = human_ticket_payload.get("tickets") if isinstance(human_ticket_payload.get("tickets"), list) else []
    teammate_consensus_path = validation_source / "teammate_consensus.yaml" if validation_source else None

    stop_reason = None
    if failures or recheck_failed:
        stop_reason = "recheck_failed"
    elif immutable_anchor_hits:
        stop_reason = "forbidden_change_required"
    elif args.dry_run:
        stop_reason = "dry_run_completed"
    elif apply_mode == "none":
        stop_reason = "advisory_cycle_completed"
    elif apply_mode == "low-risk" and not applied_paths:
        stop_reason = "no_auto_apply_eligible_fix"
    cycle_mode = "dry_run" if args.dry_run else "advisory_only" if apply_mode == "none" else "auto_apply_enabled"

    verdict = {
        "cycle_id": cycle_id,
        "generated_at": datetime.now().isoformat(),
        "scope": args.scope,
        "cycle_mode": cycle_mode,
        "backend": backend,
        "apply_mode": apply_mode,
        "default_mode": policy.get("default_mode"),
        "teammate_evaluation_enabled": args.enable_teammates,
        "teammate_agent": args.teammate_agent if args.enable_teammates else None,
        "teammate_consensus": str(teammate_consensus_path) if teammate_consensus_path and teammate_consensus_path.exists() else None,
        "selected_target": target_info["selected_target"],
        "selected_node_id": target_info["selected_node_id"],
        "next_node_id": target_info["next_node_id"],
        "graph_skill_used": target_info["graph_skill_used"],
        "selection_source": target_info["selection_source"],
        "graph_contract_status": target_info["graph_contract_status"],
        "graph_refresh_status": target_info["graph_refresh_status"],
        "graph_skill_path": target_info["graph_skill_path"],
        "max_targets_per_cycle": policy.get("max_targets_per_cycle", 1),
        "graph_target_freeze_once": bool(policy.get("graph_target_freeze_once", True)),
        "targets_validated": None if args.dry_run else str(validation_source),
        "actions_planned": str(actions_path),
        "actions_applied": applied_paths,
        "critical_findings": manual_tickets,
        "manual_tickets": manual_tickets,
        "recheck_passed": not recheck_failed,
        "advisory_rechecks": advisory_results,
        "continue_recommended": stop_reason is None,
        "stop_reason": stop_reason,
        "validation_invocation_status": validation_invocation["status"] if validation_invocation else "reused",
        "summary_status": summary_result["status"],
        "planner_status": planner_result["status"],
        "apply_status": apply_result["status"],
        "maintenance_lane_status": maintenance_lane_status,
        "research_lane_status": research_lane_status,
        "maintenance_score_summary": summary.get("maintenance_score_summary"),
        "research_rigor_score_summary": summary.get("research_rigor_score_summary"),
        "exploratory_nodes": summary.get("exploratory_nodes", []),
        "human_gate_required": bool(human_tickets),
        "immutable_anchor_hit": bool(immutable_anchor_hits or summary.get("immutable_anchor_hit", False)),
        "no_change_recommended": bool(summary.get("no_change_recommended", False)),
    }
    write_yaml(cycle_verdict_path, verdict)
    print(f"cycle_dir: {cycle_dir}")
    print(f"cycle_verdict: {cycle_verdict_path}")
    return 1 if failures or recheck_failed else 0


if __name__ == "__main__":
    sys.exit(main())
