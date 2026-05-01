#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


GRAPH_PATH = Path("backend/graph/graph.json")
GRAPH_STATUS_PATH = Path("backend/graph/graph_status.json")
GRAPH_TOP_LEVEL_KEYS = {"nodes", "edges"}
NODE_KEYS = {"path", "status"}
EDGE_KEYS = {"src", "rel", "dst"}
STATUS_REQUIRED_KEYS = {"ready_nodes", "blocked_nodes", "next_node", "unfinished_count"}
BODY_LIKE_KEYS = {
    "body",
    "content",
    "markdown",
    "manuscript",
    "review",
    "schema",
    "artifact",
    "artifacts",
    "summary",
    "description",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate minimal scheduler graph files.")
    parser.add_argument("--root", default=".", help="Repository root.")
    return parser.parse_args()


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise RuntimeError(f"missing file: {path}")
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON in {path}: {exc}") from exc


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def node_is_leaf(path: str, graph_paths: list[str]) -> bool:
    prefix = path.rstrip("/") + "/"
    return not any(other != path and other.startswith(prefix) for other in graph_paths)


def graph_path_for_next_node(graph: dict[str, Any], next_node: str) -> str | None:
    nodes = graph.get("nodes")
    if not isinstance(nodes, dict):
        return None
    node_payload = nodes.get(next_node)
    if isinstance(node_payload, dict) and isinstance(node_payload.get("path"), str):
        return node_payload["path"]
    for payload in nodes.values():
        if isinstance(payload, dict) and payload.get("path") == next_node:
            return next_node
    return None


def validate_graph(root: Path) -> list[str]:
    errors: list[str] = []
    graph = load_json(root / GRAPH_PATH)
    graph_status = load_json(root / GRAPH_STATUS_PATH)

    if not isinstance(graph, dict):
        fail(errors, "graph.json must contain a JSON object")
        return errors
    if set(graph) != GRAPH_TOP_LEVEL_KEYS:
        fail(errors, f"graph.json top-level keys must be {sorted(GRAPH_TOP_LEVEL_KEYS)}, got {sorted(graph)}")

    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, dict):
        fail(errors, "graph.json `nodes` must be an object")
        nodes = {}
    if not isinstance(edges, list):
        fail(errors, "graph.json `edges` must be a list")
        edges = []

    graph_paths: list[str] = []
    for node_id, payload in nodes.items():
        if not isinstance(payload, dict):
            fail(errors, f"node `{node_id}` payload must be an object")
            continue
        extra = set(payload) - NODE_KEYS
        missing = NODE_KEYS - set(payload)
        if extra:
            fail(errors, f"node `{node_id}` has extra keys: {sorted(extra)}")
        if missing:
            fail(errors, f"node `{node_id}` missing keys: {sorted(missing)}")
        if BODY_LIKE_KEYS & set(payload):
            fail(errors, f"node `{node_id}` contains body-like keys: {sorted(BODY_LIKE_KEYS & set(payload))}")
        path = payload.get("path")
        status = payload.get("status")
        if not isinstance(path, str) or not path:
            fail(errors, f"node `{node_id}` path must be a non-empty string")
        else:
            graph_paths.append(path)
            if not (root / path).exists():
                fail(errors, f"node `{node_id}` path does not exist: {path}")
        if not isinstance(status, str) or not status:
            fail(errors, f"node `{node_id}` status must be a non-empty string")

    node_ids = set(nodes)
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            fail(errors, f"edge {index} must be an object")
            continue
        extra = set(edge) - EDGE_KEYS
        missing = EDGE_KEYS - set(edge)
        if extra:
            fail(errors, f"edge {index} has extra keys: {sorted(extra)}")
        if missing:
            fail(errors, f"edge {index} missing keys: {sorted(missing)}")
        if BODY_LIKE_KEYS & set(edge):
            fail(errors, f"edge {index} contains body-like keys: {sorted(BODY_LIKE_KEYS & set(edge))}")
        for key in ("src", "dst"):
            value = edge.get(key)
            if not isinstance(value, str) or value not in node_ids:
                fail(errors, f"edge {index} `{key}` does not reference a graph node: {value}")
        rel = edge.get("rel")
        if not isinstance(rel, str) or not rel:
            fail(errors, f"edge {index} rel must be a non-empty string")

    if not isinstance(graph_status, dict):
        fail(errors, "graph_status.json must contain a JSON object")
        return errors
    missing_status = STATUS_REQUIRED_KEYS - set(graph_status)
    if missing_status:
        fail(errors, f"graph_status.json missing keys: {sorted(missing_status)}")
    for key in ("ready_nodes", "blocked_nodes"):
        if not isinstance(graph_status.get(key), list):
            fail(errors, f"graph_status.json `{key}` must be a list")
    if not isinstance(graph_status.get("unfinished_count"), int):
        fail(errors, "graph_status.json `unfinished_count` must be an integer")

    next_node = graph_status.get("next_node")
    if not isinstance(next_node, str) or not next_node:
        fail(errors, "graph_status.json `next_node` must be a non-empty string")
        return errors
    next_path = graph_path_for_next_node(graph, next_node)
    if not next_path:
        fail(errors, f"next_node cannot be resolved in graph.json: {next_node}")
        return errors
    if not node_is_leaf(next_path, graph_paths):
        fail(errors, f"next_node is not a leaf node: {next_node}")
    if not (root / next_path / "skills" / "local_entry.md").is_file():
        fail(errors, f"next_node is missing skills/local_entry.md: {next_path}")

    return errors


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    try:
        errors = validate_graph(root)
    except RuntimeError as exc:
        errors = [str(exc)]

    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1
    print("graph validation: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
