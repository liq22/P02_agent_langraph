#!/usr/bin/env python3
"""Build scope rollup projection for dashboard and agent app views."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ACTIVE_STATUSES = {"active", "review", "fix"}
TRUTH_BLOCKED_HANDOFFS = {"blocked_truth", "blocked_parent_rollup", "blocked_unknown"}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dashboard scope rollup projection.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args()


def build_rollups(
    hierarchy: dict[str, Any],
    graph_status: dict[str, Any],
    node_details: dict[str, Any],
) -> dict[str, Any]:
    blocked = set(graph_status.get("blocked_nodes", []) or [])
    next_node = graph_status.get("next_node")
    scopes: dict[str, Any] = {}

    def walk(node: dict[str, Any]) -> dict[str, Any]:
        node_id = str(node.get("id", ""))
        children = [child for child in (node.get("children", []) or []) if isinstance(child, dict)]
        child_rollups = [walk(child) for child in children]
        detail = node_details.get(node_id, {}) if isinstance(node_details, dict) else {}
        status = detail.get("status") or node.get("status") or "seed"
        handoff = str(detail.get("handoff_readiness") or "blocked_unknown")
        placeholder_risk = str(detail.get("placeholder_risk") or "none")
        flags = detail.get("flags", []) if isinstance(detail.get("flags"), list) else []

        rollup = {
            "id": node_id,
            "path": node.get("path"),
            "children_count": len(children),
            "leaf_count": sum(child["leaf_count"] for child in child_rollups),
            "active_count": sum(child["active_count"] for child in child_rollups),
            "scheduler_ready_count": sum(child["scheduler_ready_count"] for child in child_rollups),
            "scheduler_blocked_count": sum(child["scheduler_blocked_count"] for child in child_rollups),
            "truth_ready_count": sum(child["truth_ready_count"] for child in child_rollups),
            "truth_blocked_count": sum(child["truth_blocked_count"] for child in child_rollups),
            "review_blocked_count": sum(child["review_blocked_count"] for child in child_rollups),
            "execution_blocked_count": sum(child["execution_blocked_count"] for child in child_rollups),
            "handoff_ready_count": sum(child["handoff_ready_count"] for child in child_rollups),
            "placeholder_confirmed_count": sum(child["placeholder_confirmed_count"] for child in child_rollups),
            "review_due_count": sum(child["review_due_count"] for child in child_rollups),
            "zero_progress_active_count": sum(child["zero_progress_active_count"] for child in child_rollups),
            "missing_local_entry_count": sum(child["missing_local_entry_count"] for child in child_rollups),
            "missing_node_skill_count": sum(child["missing_node_skill_count"] for child in child_rollups),
            "missing_sop_count": sum(child["missing_sop_count"] for child in child_rollups),
            "unexpected_node_skill_count": sum(child["unexpected_node_skill_count"] for child in child_rollups),
            "unexpected_sop_count": sum(child["unexpected_sop_count"] for child in child_rollups),
            "unexpected_local_execution_count": sum(child["unexpected_local_execution_count"] for child in child_rollups),
            "missing_execution_binder_count": sum(child["missing_execution_binder_count"] for child in child_rollups),
            "thin_local_entry_count": sum(child["thin_local_entry_count"] for child in child_rollups),
            "scheduler_next_descendants": sum(child["scheduler_next_descendants"] for child in child_rollups),
        }

        if not children:
            review_gate = detail.get("review_gate", {}) if isinstance(detail.get("review_gate"), dict) else {}
            rollup.update(
                {
                    "leaf_count": 1,
                    "active_count": 1 if status in ACTIVE_STATUSES else 0,
                    "scheduler_ready_count": 1 if detail.get("scheduler_ready") is True else 0,
                    "scheduler_blocked_count": 1 if node_id in blocked else 0,
                    "truth_ready_count": 1 if detail.get("truth_ready") is True else 0,
                    "truth_blocked_count": 1 if handoff in TRUTH_BLOCKED_HANDOFFS else 0,
                    "review_blocked_count": 1 if handoff == "blocked_review" else 0,
                    "execution_blocked_count": 1 if handoff == "blocked_execution" else 0,
                    "handoff_ready_count": 1 if handoff == "ready" else 0,
                    "placeholder_confirmed_count": 1 if placeholder_risk == "confirmed" else 0,
                    "review_due_count": 1 if handoff == "blocked_review" else 0,
                    "zero_progress_active_count": 1 if status == "active" and detail.get("progress_pct") in (0, None) else 0,
                    "missing_local_entry_count": 1 if "missing-local-entry" in flags else 0,
                    "missing_node_skill_count": 1 if "missing-node-skill" in flags else 0,
                    "missing_sop_count": 1 if "missing-sop" in flags else 0,
                    "unexpected_node_skill_count": 1 if "unexpected-node-skill" in flags else 0,
                    "unexpected_sop_count": 1 if "unexpected-sop" in flags else 0,
                    "unexpected_local_execution_count": 1 if "unexpected-local-execution" in flags else 0,
                    "missing_execution_binder_count": 1 if "missing-execution-binder" in flags else 0,
                    "thin_local_entry_count": 1 if "thin-local-entry" in flags else 0,
                    "scheduler_next_descendants": 1 if node_id == next_node else 0,
                }
            )
        elif node_id == next_node:
            rollup["scheduler_next_descendants"] += 1

        scopes[node_id] = rollup
        return rollup

    walk(hierarchy)
    return scopes


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    graph_dir = root / "backend" / "graph"

    hierarchy = load_json(graph_dir / "hierarchy.json")
    graph_status = load_json(graph_dir / "graph_status.json")
    node_details = load_json(graph_dir / "node_details.json").get("nodes", {})
    if not isinstance(node_details, dict):
        raise RuntimeError("node_details.json must contain a 'nodes' object")

    scopes = build_rollups(hierarchy, graph_status, node_details)
    out_path = graph_dir / "scope_rollup.json"
    atomic_write_json(out_path, {"scopes": scopes})
    print(f"[scope_rollup_ok] scopes={len(scopes)} output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
