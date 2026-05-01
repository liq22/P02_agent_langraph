#!/usr/bin/env python3
"""Apply explicit low-risk maintenance actions inside the optimizer allowlist."""

from __future__ import annotations

import argparse
import fnmatch
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
DEFAULT_POLICY = SKILL_DIR / "config" / "optimization_loop.yaml"
DEFAULT_IMMUTABLE = SKILL_DIR / "config" / "immutable_core_rules.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def matches_any(rel_path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def resolve_target_path(target_path: str | None) -> Path | None:
    if not target_path:
        return None
    path = Path(target_path)
    return path if path.is_absolute() else REPO_ROOT / path


def apply_operation(target: Path, operation: str, payload: dict[str, Any]) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if operation == "write_file":
        target.write_text(str(payload.get("content", "")), encoding="utf-8")
        return
    current = target.read_text(encoding="utf-8") if target.exists() else ""
    if operation == "append_text":
        target.write_text(current + str(payload.get("text", "")), encoding="utf-8")
        return
    if operation == "prepend_text":
        target.write_text(str(payload.get("text", "")) + current, encoding="utf-8")
        return
    if operation == "replace_text":
        old = str(payload.get("old", ""))
        new = str(payload.get("new", ""))
        count = payload.get("count")
        if old not in current:
            raise ValueError(f"`{old}` not found in {target}")
        replaced = current.replace(old, new, count if isinstance(count, int) else -1)
        target.write_text(replaced, encoding="utf-8")
        return
    raise ValueError(f"unsupported operation: {operation}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply low-risk optimization actions.")
    parser.add_argument("--actions", type=Path, required=True, help="Action plan YAML path.")
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY, help="Optimization loop policy.")
    parser.add_argument("--report", type=Path, required=True, help="Markdown report path.")
    parser.add_argument("--summary", type=Path, default=None, help="Optional YAML summary path.")
    parser.add_argument("--dry-run", action="store_true", help="Plan changes without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    policy = load_yaml(args.policy)
    immutable = load_yaml(DEFAULT_IMMUTABLE)
    action_plan = load_yaml(args.actions)
    actions = action_plan.get("actions") if isinstance(action_plan.get("actions"), list) else []
    allowed = [str(item) for item in policy.get("allowed_auto_apply_paths", [])]
    forbidden = [str(item) for item in policy.get("forbidden_auto_apply_paths", [])]
    immutable_paths = [str(item) for item in immutable.get("immutable_paths", [])]

    applied: list[str] = []
    planned: list[str] = []
    manual: list[str] = []
    failures: list[str] = []
    immutable_anchor_hits: list[str] = []
    blocked_reason_codes: list[str] = []

    for action in actions:
        if not isinstance(action, dict):
            continue
        action_id = str(action.get("id", "unknown"))
        lane = str(action.get("lane", ""))
        disposition = str(action.get("disposition", ""))
        target_path = str(action.get("target_path") or "")
        rel_path = str(Path(target_path)) if target_path else ""
        resolved = resolve_target_path(target_path)
        operation = action.get("operation")
        payload = action.get("payload") if isinstance(action.get("payload"), dict) else {}
        reason_code = str(action.get("reason_code") or "")

        if lane != "maintenance":
            if reason_code:
                blocked_reason_codes.append(reason_code)
            manual.append(f"{action_id}: lane={lane} is not auto-applicable")
            continue
        if disposition != "auto_apply":
            if reason_code:
                blocked_reason_codes.append(reason_code)
            manual.append(f"{action_id}: disposition={disposition}")
            continue
        if not action.get("auto_apply"):
            if reason_code:
                blocked_reason_codes.append(reason_code)
            manual.append(f"{action_id}: auto_apply=false")
            continue
        if not rel_path:
            if reason_code:
                blocked_reason_codes.append(reason_code)
            manual.append(f"{action_id}: missing target_path")
            continue
        if matches_any(rel_path, immutable_paths) or bool(action.get("immutable_anchor_hit", False)):
            immutable_anchor_hits.append(rel_path)
            blocked_reason_codes.append(reason_code or "immutable_path")
            manual.append(f"{action_id}: immutable anchor `{rel_path}`")
            continue
        if matches_any(rel_path, forbidden):
            blocked_reason_codes.append(reason_code or "forbidden_surface")
            manual.append(f"{action_id}: forbidden path `{rel_path}`")
            continue
        if not matches_any(rel_path, allowed):
            blocked_reason_codes.append(reason_code or "forbidden_surface")
            manual.append(f"{action_id}: outside allowlist `{rel_path}`")
            continue
        if not isinstance(operation, str) or not operation:
            blocked_reason_codes.append(reason_code or "validator_failure")
            manual.append(f"{action_id}: missing explicit operation")
            continue

        try:
            if args.dry_run:
                planned.append(f"{action_id}: {operation} -> {rel_path}")
            else:
                assert resolved is not None
                apply_operation(resolved, operation, payload)
                applied.append(f"{action_id}: {operation} -> {rel_path}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{action_id}: {exc}")

    report_lines = [
        "# Applied Changes",
        "",
        f"generated_at: {datetime.now().isoformat()}",
        "",
        "## Applied",
    ]
    report_lines.extend([f"- {item}" for item in applied] or ["- none"])
    report_lines.extend(["", "## Planned (Dry Run)"])
    report_lines.extend([f"- {item}" for item in planned] or ["- none"])
    report_lines.extend(["", "## Manual Tickets"])
    report_lines.extend([f"- {item}" for item in manual] or ["- none"])
    report_lines.extend(["", "## Immutable Anchor Hits"])
    report_lines.extend([f"- {item}" for item in immutable_anchor_hits] or ["- none"])
    report_lines.extend(["", "## Failures"])
    report_lines.extend([f"- {item}" for item in failures] or ["- none"])

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    summary = {
        "generated_at": datetime.now().isoformat(),
        "dry_run": args.dry_run,
        "applied_paths": [item.split("->", 1)[1].strip() for item in applied if "->" in item],
        "planned_paths": [item.split("->", 1)[1].strip() for item in planned if "->" in item],
        "manual_tickets": manual,
        "blocked_reason_codes": blocked_reason_codes,
        "immutable_anchor_hits": immutable_anchor_hits,
        "failures": failures,
    }
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(yaml.safe_dump(summary, allow_unicode=True, sort_keys=False), encoding="utf-8")

    if failures:
        print(f"apply_low_risk_actions: {len(failures)} failure(s)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
