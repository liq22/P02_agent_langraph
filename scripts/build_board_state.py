#!/usr/bin/env python3
"""Build human-flow board projection from scheduler and truth-facing state."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any


ACTIVE_STATUSES = {"active", "review", "fix"}
LANE_LIMITS = {
    "scheduler_now": 1,
    "truth_ready": 10,
    "review_blocked": 10,
    "execution_blocked": 10,
    "truth_blocked": 12,
    "active_work": 10,
    "parked": 12,
}


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
    parser = argparse.ArgumentParser(description="Build dashboard board state projection.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args()


def infer_lane(node_id: str, graph_status: dict[str, Any], detail: dict[str, Any]) -> str:
    if node_id == graph_status.get("next_node"):
        return "scheduler_now"

    handoff = str(detail.get("handoff_readiness") or "blocked_unknown")
    status = str(detail.get("status") or "seed")

    if handoff == "ready":
        return "truth_ready"
    if handoff == "blocked_review":
        return "review_blocked"
    if handoff == "blocked_execution":
        return "execution_blocked"
    if handoff in {"blocked_truth", "blocked_parent_rollup", "blocked_unknown"}:
        return "truth_blocked"
    if status in ACTIVE_STATUSES:
        return "active_work"
    return "parked"


def sort_key(node_id: str, graph_nodes: dict[str, Any], details: dict[str, Any]) -> tuple[int, int, int, str]:
    meta = graph_nodes.get(node_id, {}) if isinstance(graph_nodes, dict) else {}
    detail = details.get(node_id, {}) if isinstance(details, dict) else {}
    handoff = str(detail.get("handoff_readiness") or "blocked_unknown")
    handoff_rank = {
        "ready": 0,
        "blocked_review": 1,
        "blocked_execution": 2,
        "blocked_truth": 3,
        "blocked_parent_rollup": 4,
        "blocked_unknown": 5,
    }.get(handoff, 99)
    status = detail.get("status") or meta.get("status") or "seed"
    status_rank = {"fix": 0, "review": 1, "active": 2, "seed": 3, "done": 4, "archive": 5}.get(status, 99)
    progress_rank = -(detail.get("progress_pct") or 0)
    return (handoff_rank, status_rank, progress_rank, meta.get("path", node_id))


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    graph_dir = root / "backend" / "graph"

    graph = load_json(graph_dir / "graph.json")
    graph_status = load_json(graph_dir / "graph_status.json")
    details = load_json(graph_dir / "node_details.json").get("nodes", {})
    graph_nodes = graph.get("nodes", {})
    if not isinstance(graph_nodes, dict):
        raise RuntimeError("graph.json must contain a 'nodes' object")
    if not isinstance(details, dict):
        raise RuntimeError("node_details.json must contain a 'nodes' object")

    lanes: dict[str, list[str]] = {key: [] for key in LANE_LIMITS}
    for node_id in graph_nodes:
        lane = infer_lane(node_id, graph_status, details.get(node_id, {}))
        lanes[lane].append(node_id)

    for lane, limit in LANE_LIMITS.items():
        lanes[lane].sort(key=lambda item: sort_key(item, graph_nodes, details))
        lanes[lane] = lanes[lane][:limit]

    out_path = graph_dir / "board_state.json"
    atomic_write_json(out_path, {"lanes": lanes})
    print(f"[board_state_ok] output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
