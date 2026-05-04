#!/usr/bin/env python3
"""Validate a P02 `/goal` FSM state file.

Supports the v4 actual-repo FSM used by the optimized package. The validator is
strict for real state files but allows an initial template to have an empty
history when `current_state` is the first state.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ORDER = [
    "S0_REPO_FACT_SYNC",
    "S1_P1_01_NODE_PACKAGE",
    "S2_DATA_RESOURCE_AUDIT",
    "S3_VIBENCH_READ_BOUNDARY",
    "S4_PHMGA_HANDOFF_AND_PREFLIGHT",
    "S5_PHMGA_FORMAL_EXPERIMENTS",
    "S6_PAPER_EVIDENCE_LOCK",
    "S7_FINAL_SUBMISSION_VALIDATION",
    "COMPLETE",
]

LEGACY_ORDER = [
    "S0_BOOTSTRAP",
    "S1_DATA_RESOURCE_AUDIT",
    "S2_VIBENCH_READ_BOUNDARY",
    "S3_PHMGA_HANDOFF",
    "S4_PHMGA_FORMAL_EXPERIMENTS",
    "S5_PAPER_EVIDENCE_LOCK",
    "S6_FINAL_SUBMISSION_VALIDATION",
    "COMPLETE",
]

FORBIDDEN = {
    ("S1_P1_01_NODE_PACKAGE", "S5_PHMGA_FORMAL_EXPERIMENTS"),
    ("S2_DATA_RESOURCE_AUDIT", "S5_PHMGA_FORMAL_EXPERIMENTS"),
    ("S3_VIBENCH_READ_BOUNDARY", "S6_PAPER_EVIDENCE_LOCK"),
    ("S5_PHMGA_FORMAL_EXPERIMENTS", "S7_FINAL_SUBMISSION_VALIDATION"),
}


def parse(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except Exception:
        import yaml  # type: ignore

        return yaml.safe_load(text)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", required=True)
    parser.add_argument("--allow-template", action="store_true")
    args = parser.parse_args()

    data = parse(Path(args.state))
    blockers: list[str] = []
    warnings: list[str] = []

    cur = data.get("current_state")
    nxt = data.get("next_state")
    order = ORDER if cur in ORDER or nxt in ORDER else LEGACY_ORDER

    if cur not in order:
        blockers.append(f"invalid current_state: {cur}")
    if nxt is not None and nxt not in order:
        blockers.append(f"invalid next_state: {nxt}")
    if nxt is not None and (cur, nxt) in FORBIDDEN:
        blockers.append(f"forbidden transition: {cur} -> {nxt}")
    if cur in order and nxt in order and order.index(nxt) < order.index(cur):
        warnings.append(f"backward transition: {cur} -> {nxt}")

    state_history = data.get("state_history", data.get("state_log", []))
    if not state_history:
        if args.allow_template or cur == order[0]:
            warnings.append("state history is empty; acceptable only for initial templates")
        else:
            blockers.append("state_history/state_log missing or empty")

    # Actual-repo required fields.
    if cur in ORDER:
        if not data.get("expected_next_node"):
            warnings.append("expected_next_node missing")
        if not data.get("selected_node_path"):
            warnings.append("selected_node_path missing")
        if not data.get("phmga_submodule_path"):
            warnings.append("phmga_submodule_path missing")

    result = {
        "fsm_state_valid": not blockers,
        "current_state": cur,
        "next_state": nxt,
        "blockers": blockers,
        "warnings": warnings,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["fsm_state_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
