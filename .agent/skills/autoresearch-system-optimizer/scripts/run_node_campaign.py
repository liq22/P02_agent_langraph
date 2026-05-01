#!/usr/bin/env python3
"""Run bounded optimizer cycles over every P0-P4 research node."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import uuid
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
DEFAULT_RESULTS_ROOT = REPO_ROOT / "_reference" / "test" / "v2" / "results" / "node_campaigns"
PHASE_RE = re.compile(r"(P[0-4])_")


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def node_phase(node_path: str) -> str:
    match = PHASE_RE.search(node_path)
    return match.group(1) if match else "UNKNOWN"


def discover_nodes(phases: set[str], selected_nodes: set[str]) -> list[str]:
    nodes = sorted(path.parent.as_posix() for path in (REPO_ROOT / "research").glob("P*/**/status.yaml"))
    filtered: list[str] = []
    for node in nodes:
        rel = str(Path(node).relative_to(REPO_ROOT)) if Path(node).is_absolute() else node
        if phases and node_phase(rel) not in phases:
            continue
        if selected_nodes and rel not in selected_nodes:
            continue
        filtered.append(rel)
    return filtered


def parse_cycle_dir(stdout: str) -> str | None:
    for line in stdout.splitlines():
        if line.startswith("cycle_dir:"):
            candidate = line.split(":", 1)[1].strip()
            return candidate or None
    return None


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False)


def run_cycle_for_node(args: argparse.Namespace, *, node: str, cycles_root: Path) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(SKILL_DIR / "scripts" / "run_optimization_cycle.py"),
        "--scope",
        f"node:{node}",
        "--target",
        node,
        "--results-root",
        str(cycles_root),
        "--apply",
        args.apply,
    ]
    if args.enable_teammates:
        cmd.extend(
            [
                "--enable-teammates",
                "--teammate-agent",
                args.teammate_agent,
                "--agents",
                str(args.num_agents),
                "--max-workers",
                str(args.max_workers),
            ]
        )
    if args.dry_run:
        cmd.append("--dry-run")
    if args.skip_recheck:
        cmd.append("--skip-recheck")

    completed = run_command(cmd)
    cycle_dir = parse_cycle_dir(completed.stdout)
    verdict_path = Path(cycle_dir) / "09_cycle_verdict.yaml" if cycle_dir else None
    verdict = load_yaml(verdict_path) if verdict_path else {}
    applied = verdict.get("actions_applied") if isinstance(verdict.get("actions_applied"), list) else []
    manual = verdict.get("manual_tickets") if isinstance(verdict.get("manual_tickets"), list) else []
    return {
        "node": node,
        "phase": node_phase(node),
        "command": cmd,
        "returncode": completed.returncode,
        "status": "success" if completed.returncode == 0 else "failed",
        "cycle_dir": cycle_dir,
        "cycle_verdict": str(verdict_path) if verdict_path else None,
        "stop_reason": verdict.get("stop_reason"),
        "maintenance_lane_status": verdict.get("maintenance_lane_status"),
        "research_lane_status": verdict.get("research_lane_status"),
        "actions_applied_count": len(applied),
        "manual_ticket_count": len(manual),
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def summarize_phase(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "node_count": len(rows),
        "success_count": sum(1 for row in rows if row.get("status") == "success"),
        "failed_count": sum(1 for row in rows if row.get("status") == "failed"),
        "actions_applied_count": sum(int(row.get("actions_applied_count") or 0) for row in rows),
        "manual_ticket_count": sum(int(row.get("manual_ticket_count") or 0) for row in rows),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run optimizer cycles over all P0-P4 nodes.")
    parser.add_argument("--results-root", type=Path, default=DEFAULT_RESULTS_ROOT, help="Campaign result root.")
    parser.add_argument("--phase", action="append", default=[], help="Phase filter such as P0. Repeatable.")
    parser.add_argument("--node", action="append", default=[], help="Explicit research node path. Repeatable.")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many selected nodes.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum nodes to process.")
    parser.add_argument("--apply", choices=("low-risk", "none"), default="low-risk", help="Cycle apply mode.")
    parser.add_argument("--enable-teammates", action=argparse.BooleanOptionalAction, default=False, help="Enable Claude Code teammate evaluators.")
    parser.add_argument("--teammate-agent", default="claude_code", help="External teammate agent template key.")
    parser.add_argument("--num-agents", type=int, default=3, help="Teammate evaluator count.")
    parser.add_argument("--max-workers", type=int, default=3, help="Teammate evaluator concurrency.")
    parser.add_argument("--dry-run", action="store_true", help="Plan cycles without running external validation or patching.")
    parser.add_argument("--skip-recheck", action="store_true", help="Skip cycle rechecks.")
    parser.add_argument("--stop-on-failure", action="store_true", help="Stop campaign after the first failed cycle.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    phases = {phase.strip() for phase in args.phase if phase.strip()} or {f"P{index}" for index in range(5)}
    selected_nodes = {node.strip() for node in args.node if node.strip()}
    nodes = discover_nodes(phases, selected_nodes)
    if args.offset:
        nodes = nodes[args.offset :]
    if args.limit is not None:
        nodes = nodes[: args.limit]
    if not nodes:
        print("error: no P0-P4 nodes selected", file=sys.stderr)
        return 1

    campaign_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    campaign_dir = args.results_root / campaign_id
    cycles_root = campaign_dir / "cycles"
    campaign_dir.mkdir(parents=True, exist_ok=True)

    inventory = {
        "campaign_id": campaign_id,
        "generated_at": datetime.now().isoformat(),
        "node_count": len(nodes),
        "apply_mode": args.apply,
        "dry_run": args.dry_run,
        "teammate_evaluation_enabled": args.enable_teammates,
        "teammate_agent": args.teammate_agent if args.enable_teammates else None,
        "num_agents": args.num_agents if args.enable_teammates else 0,
        "nodes": [{"path": node, "phase": node_phase(node)} for node in nodes],
    }
    write_yaml(campaign_dir / "00_node_inventory.yaml", inventory)

    results: list[dict[str, Any]] = []
    phase_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for node in nodes:
        row = run_cycle_for_node(args, node=node, cycles_root=cycles_root)
        results.append(row)
        phase_rows[str(row["phase"])].append(row)
        write_yaml(campaign_dir / "latest_progress.yaml", {"campaign_id": campaign_id, "completed": len(results), "total": len(nodes), "last": row})
        if row["status"] != "success" and args.stop_on_failure:
            break

    phase_summary = {phase: summarize_phase(rows) for phase, rows in sorted(phase_rows.items())}
    manual_tickets = [row for row in results if int(row.get("manual_ticket_count") or 0) > 0]
    applied_rows = [row for row in results if int(row.get("actions_applied_count") or 0) > 0]
    summary = {
        "campaign_id": campaign_id,
        "generated_at": datetime.now().isoformat(),
        "campaign_dir": str(campaign_dir),
        "node_count": len(nodes),
        "completed_count": len(results),
        "success_count": sum(1 for row in results if row.get("status") == "success"),
        "failed_count": sum(1 for row in results if row.get("status") == "failed"),
        "actions_applied_count": sum(int(row.get("actions_applied_count") or 0) for row in results),
        "manual_ticket_node_count": len(manual_tickets),
        "phase_summary": phase_summary,
        "results": results,
    }
    write_yaml(campaign_dir / "campaign_summary.yaml", summary)
    write_yaml(campaign_dir / "manual_tickets.yaml", {"nodes": manual_tickets})
    (campaign_dir / "applied_changes.md").write_text(
        "# Applied Changes\n\n" + "\n".join(f"- {row['node']}: {row['actions_applied_count']} applied action(s)" for row in applied_rows) + ("\n" if applied_rows else "- none\n"),
        encoding="utf-8",
    )
    print(f"campaign_dir: {campaign_dir}")
    print(f"campaign_summary: {campaign_dir / 'campaign_summary.yaml'}")
    return 1 if any(row.get("status") == "failed" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
