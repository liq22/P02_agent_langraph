#!/usr/bin/env python3
"""Build a folder hierarchy projection from the minimal research graph."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class TreeNode:
    node_id: str
    name: str
    path: str
    status: str | None = None
    children: dict[str, "TreeNode"] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.node_id,
            "name": self.name,
            "path": self.path,
            "status": self.status,
            "children": [
                child.to_dict()
                for child in sorted(self.children.values(), key=lambda item: item.name)
            ],
        }


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def path_to_node_id(path_str: str) -> str:
    return path_str.replace("/", "::")


def ensure_child(parent: TreeNode, name: str, path: str) -> TreeNode:
    if name not in parent.children:
        parent.children[name] = TreeNode(
            node_id=path_to_node_id(path),
            name=name,
            path=path,
        )
    return parent.children[name]


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


def build_hierarchy(nodes: dict[str, Any]) -> TreeNode:
    root = TreeNode(node_id="research", name="research", path="research")

    def sort_key(item: tuple[str, Any]) -> str:
        payload = item[1]
        return str(payload.get("path", ""))

    for node_id, payload in sorted(nodes.items(), key=sort_key):
        if not isinstance(payload, dict):
            continue
        path = payload.get("path")
        if not isinstance(path, str):
            continue

        parts = path.split("/")
        if not parts or parts[0] != "research":
            continue

        current = root
        for index in range(1, len(parts)):
            current_path = "/".join(parts[: index + 1])
            current = ensure_child(current, parts[index], current_path)
            if current.path == path or current.node_id == node_id:
                current.status = payload.get("status")

    return root


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build hierarchy projection for dashboard.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    graph_path = root / "backend" / "graph" / "graph.json"
    out_path = root / "backend" / "graph" / "hierarchy.json"

    graph_payload = load_json(graph_path)
    nodes = graph_payload.get("nodes", {})
    if not isinstance(nodes, dict):
        raise RuntimeError("graph.json must contain a 'nodes' object")

    hierarchy_root = build_hierarchy(nodes)
    atomic_write_json(out_path, hierarchy_root.to_dict())
    print(f"[hierarchy_ok] output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
