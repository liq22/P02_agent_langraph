#!/usr/bin/env python3
"""Refresh all derived graph, projection, and Canvas views."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


GRAPH_ONLY_STEPS = (
    "refresh_hypergraph.py",
)

FULL_ONLY_STEPS = (
    "build_hierarchy_projection.py",
    "build_node_details.py",
    "build_scope_rollup.py",
    "build_board_state.py",
    "build_canvas_from_graph.py",
)

FULL_STEPS = (
    "refresh_hypergraph.py",
    *FULL_ONLY_STEPS,
)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh all derived research OS views.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--mode",
        choices=("graph_only", "full"),
        default="full",
        help="Refresh mode. `graph_only` updates only graph truth/status; `full` also refreshes projections and Canvas.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    scripts_dir = Path(__file__).resolve().parent
    steps = GRAPH_ONLY_STEPS if args.mode == "graph_only" else FULL_STEPS

    for script_name in steps:
        script_path = scripts_dir / script_name
        command = [sys.executable, str(script_path), "--root", str(root)]
        print(f"[refresh_views] mode={args.mode} running {' '.join(command)}", flush=True)
        result = subprocess.run(command, cwd=root)
        if result.returncode != 0:
            print(
                f"[refresh_views_failed] mode={args.mode} step={script_name} exit={result.returncode}",
                file=sys.stderr,
            )
            return result.returncode

    print(f"[refresh_views_ok] mode={args.mode}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
