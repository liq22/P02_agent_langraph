#!/usr/bin/env python3
"""Build the minimal JSON scheduler graph for the research workspace."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None


ALLOWED_RELATIONS = {"depends_on", "addresses"}
STATUS_PRIORITY = {"fix": 0, "review": 1, "active": 2, "seed": 3}
PHASE_PRIORITY = {"P0": 0, "P1": 1, "P2": 2, "P3": 3, "P4": 4}
VALID_STATUSES = {
    "seed",
    "active",
    "review",
    "fix",
    "done",
    "archive",
}
TERMINAL_STATUSES = {"done", "archive"}
UNFINISHED_STATUSES = {"seed", "active", "review", "fix"}


@dataclass(frozen=True)
class NodeRecord:
    node_id: str
    path: str
    status: str
    phase: str
    kind: str
    paper_gate_readiness: str | None = None
    paper_route: tuple[str, ...] = ()


def fail(message: str) -> None:
    print(f"[error] {message}", file=sys.stderr)
    raise RuntimeError(message)


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def normalize_status(raw_status: str | None, source: str) -> str:
    if raw_status is None:
        fail(f"{source}: missing status")
    normalized = str(raw_status).strip().lower()
    if normalized not in VALID_STATUSES:
        fail(f"{source}: invalid status '{raw_status}'")
    return normalized


def extract_status_from_text(text: str) -> str | None:
    status_match = re.search(r"(?m)^\s*status:\s*([^\s#]+)", text)
    if status_match:
        return status_match.group(1)
    stage_match = re.search(r"(?m)^\s*stage:\s*([^\s#]+)", text)
    if stage_match:
        return stage_match.group(1)
    return None


def normalize_optional_text(raw_value: Any) -> str | None:
    if raw_value is None:
        return None
    normalized = str(raw_value).strip()
    return normalized or None


def read_status(status_path: Path, *, strict: bool = False) -> str:
    text = status_path.read_text(encoding="utf-8")
    parsed_status: str | None = None

    if yaml is not None:
        try:
            data = yaml.safe_load(text)
        except Exception as exc:
            fail(f"{status_path}: YAML parse failed ({exc})")
        else:
            if isinstance(data, dict):
                if "status" in data:
                    parsed_status = data.get("status")
                else:
                    lifecycle = data.get("lifecycle")
                    if isinstance(lifecycle, dict):
                        parsed_status = lifecycle.get("stage")

    if parsed_status is None and not strict:
        parsed_status = extract_status_from_text(text)

    return normalize_status(parsed_status, str(status_path))


def read_status_payload(status_path: Path) -> dict[str, Any]:
    if yaml is None:
        return {}
    text = status_path.read_text(encoding="utf-8")
    try:
        payload = yaml.safe_load(text)
    except Exception as exc:
        fail(f"{status_path}: YAML parse failed ({exc})")
    return payload if isinstance(payload, dict) else {}


def read_paper_gate(status_path: Path) -> tuple[str | None, tuple[str, ...]]:
    payload = read_status_payload(status_path)
    gate = payload.get("paper_iteration_gate")
    if not isinstance(gate, dict):
        return (None, ())

    readiness = normalize_optional_text(gate.get("readiness"))
    route_payload = gate.get("next_route")
    if not isinstance(route_payload, list):
        route_payload = gate.get("recommended_next_route")
    if not isinstance(route_payload, list):
        return (readiness.lower() if readiness else None, ())

    route = tuple(
        normalized
        for item in route_payload
        if (normalized := normalize_optional_text(item)) is not None
    )
    return (readiness.lower() if readiness else None, route)


def is_node_dir(directory: Path) -> bool:
    return directory.is_dir() and (directory / "README.md").is_file() and (directory / "status.yaml").is_file()


def path_to_node_id(path_str: str) -> str:
    return path_str.replace("/", "::")


def phase_from_path(path_str: str, *, strict: bool = False) -> str:
    parts = path_str.split("/")
    if len(parts) < 2:
        if strict:
            fail(f"{path_str}: cannot infer phase from path")
        return "P9"
    phase_name = parts[1]
    match = re.match(r"^(P\d+)", phase_name)
    if not match and strict:
        fail(f"{path_str}: cannot infer phase from path")
    return match.group(1) if match else "P9"


def discover_nodes(root: Path, *, strict: bool = False) -> dict[str, NodeRecord]:
    research_root = root / "research"
    if not research_root.is_dir():
        fail(f"research root not found: {research_root}")

    node_dirs = [directory for directory in research_root.rglob("*") if is_node_dir(directory)]
    node_dir_set = set(node_dirs)
    nodes: dict[str, NodeRecord] = {}

    for directory in sorted(node_dirs):
        rel_path = directory.relative_to(root).as_posix()
        node_id = path_to_node_id(rel_path)
        status_path = directory / "status.yaml"
        status = read_status(status_path, strict=strict)
        paper_gate_readiness, paper_route = read_paper_gate(status_path)
        kind = "parent" if any(child in node_dir_set for child in directory.iterdir() if child.is_dir()) else "leaf"
        nodes[node_id] = NodeRecord(
            node_id=node_id,
            path=rel_path,
            status=status,
            phase=phase_from_path(rel_path, strict=strict),
            kind=kind,
            paper_gate_readiness=paper_gate_readiness,
            paper_route=paper_route,
        )

    return nodes


def load_edge_registry(edge_registry_path: Path, path_to_node: dict[str, str]) -> list[dict[str, str]]:
    if not edge_registry_path.is_file():
        fail(f"edge registry not found: {edge_registry_path}")

    try:
        payload = json.loads(edge_registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid edge registry JSON: {exc}")

    raw_edges = payload.get("edges", [])
    if not isinstance(raw_edges, list):
        fail("edge_registry.json must contain an 'edges' list")

    valid_edges: list[dict[str, str]] = []
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, dict):
            fail(f"edge #{index}: not an object")

        src_path = edge.get("src")
        rel = edge.get("rel")
        dst_path = edge.get("dst")
        if not all(isinstance(item, str) for item in (src_path, rel, dst_path)):
            fail(f"edge #{index}: src/rel/dst must all be strings")
        if rel not in ALLOWED_RELATIONS:
            fail(f"edge #{index}: invalid relation '{rel}'")
        src_id = path_to_node.get(src_path)
        dst_id = path_to_node.get(dst_path)
        if src_id is None or dst_id is None:
            fail(f"edge #{index}: unresolved node path src={src_path} dst={dst_path}")
        valid_edges.append({"src": src_id, "rel": rel, "dst": dst_id})

    valid_edges.sort(key=lambda item: (item["src"], item["rel"], item["dst"]))
    return valid_edges


def detect_depends_on_cycle(nodes: dict[str, NodeRecord], edges: list[dict[str, str]]) -> None:
    adjacency: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for edge in edges:
        if edge["rel"] == "depends_on":
            adjacency[edge["src"]].append(edge["dst"])
    for children in adjacency.values():
        children.sort()

    visiting: set[str] = set()
    visited: set[str] = set()
    trail: list[str] = []

    def dfs(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            cycle_start = trail.index(node_id)
            cycle = trail[cycle_start:] + [node_id]
            fail(f"depends_on cycle detected: {' -> '.join(cycle)}")

        visiting.add(node_id)
        trail.append(node_id)
        for child in adjacency[node_id]:
            dfs(child)
        trail.pop()
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in sorted(nodes):
        dfs(node_id)


def validate_depends_on_leaf_nodes(nodes: dict[str, NodeRecord], edges: list[dict[str, str]]) -> None:
    """Keep scheduler dependencies on executable frontier nodes only."""
    for edge in edges:
        if edge["rel"] != "depends_on":
            continue
        src = nodes[edge["src"]]
        dst = nodes[edge["dst"]]
        if src.kind != "leaf" or dst.kind != "leaf":
            fail(
                "depends_on edges must connect leaf nodes: "
                f"src={src.path}({src.kind}) dst={dst.path}({dst.kind})"
            )


def is_terminal(status: str) -> bool:
    return status in TERMINAL_STATUSES


def node_sort_key(node: NodeRecord) -> tuple[int, int, int, str]:
    phase_rank = PHASE_PRIORITY.get(node.phase, 99)
    status_rank = STATUS_PRIORITY.get(node.status, 99)
    kind_rank = 0 if node.kind == "leaf" else 1
    return (phase_rank, status_rank, kind_rank, node.path)


def resolve_route_target(raw_target: str, nodes: dict[str, NodeRecord], path_to_node: dict[str, str]) -> str | None:
    normalized = normalize_optional_text(raw_target)
    if normalized is None:
        return None
    if normalized in nodes:
        return normalized
    return path_to_node.get(normalized)


def resolve_route_leaf(
    target_id: str,
    nodes: dict[str, NodeRecord],
    depends_on_map: dict[str, list[str]],
) -> str | None:
    node = nodes.get(target_id)
    if node is None or node.kind != "leaf" or is_terminal(node.status):
        return None

    unresolved_dependencies = [
        dep_id
        for dep_id in depends_on_map.get(target_id, [])
        if not is_terminal(nodes[dep_id].status)
    ]
    if not unresolved_dependencies:
        return target_id

    candidates = [
        candidate
        for dep_id in unresolved_dependencies
        if (candidate := resolve_route_leaf(dep_id, nodes, depends_on_map)) is not None
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda node_id: node_sort_key(nodes[node_id]))


def resolve_p3_paper_gate_override(
    nodes: dict[str, NodeRecord],
    depends_on_map: dict[str, list[str]],
    ready_candidate_ids: set[str],
) -> str | None:
    path_to_node = {node.path: node_id for node_id, node in nodes.items()}
    routed_nodes = sorted(
        (
            node
            for node in nodes.values()
            if node.phase == "P3"
            and node.status in UNFINISHED_STATUSES
            and node.paper_gate_readiness == "blocked"
            and node.paper_route
        ),
        key=node_sort_key,
    )
    for node in routed_nodes:
        for raw_target in node.paper_route:
            target_id = resolve_route_target(raw_target, nodes, path_to_node)
            if target_id is None:
                continue
            resolved_leaf = resolve_route_leaf(target_id, nodes, depends_on_map)
            if resolved_leaf is not None and resolved_leaf in ready_candidate_ids:
                return resolved_leaf
    return None


def build_graph_status(nodes: dict[str, NodeRecord], edges: list[dict[str, str]]) -> dict[str, Any]:
    depends_on_map: dict[str, list[str]] = {node_id: [] for node_id in nodes}
    for edge in edges:
        if edge["rel"] == "depends_on":
            depends_on_map[edge["src"]].append(edge["dst"])
    for deps in depends_on_map.values():
        deps.sort()

    unfinished_nodes = [
        node
        for node in nodes.values()
        if node.kind == "leaf" and node.status in UNFINISHED_STATUSES
    ]
    ready_candidates: list[NodeRecord] = []
    blocked_nodes: list[NodeRecord] = []

    for node in unfinished_nodes:
        dependencies = depends_on_map[node.node_id]
        if any(not is_terminal(nodes[dep_id].status) for dep_id in dependencies):
            blocked_nodes.append(node)
        else:
            ready_candidates.append(node)

    unfinished_nodes.sort(key=node_sort_key)
    blocked_nodes.sort(key=node_sort_key)
    ready_candidates.sort(key=node_sort_key)
    ready_candidate_ids = {node.node_id for node in ready_candidates}

    override_next_node = resolve_p3_paper_gate_override(nodes, depends_on_map, ready_candidate_ids)
    if override_next_node is not None:
        current_phase = nodes[override_next_node].phase
        ready_nodes = [nodes[override_next_node]]
        next_node = override_next_node
    else:
        current_phase = unfinished_nodes[0].phase if unfinished_nodes else None
        ready_nodes = [
            node
            for node in ready_candidates
            if node.phase == current_phase
        ]
        ready_nodes.sort(key=node_sort_key)
        next_node = ready_nodes[0].node_id if ready_nodes else None

    return {
        "refresh_ok": True,
        "current_phase": current_phase,
        "ready_nodes": [node.node_id for node in ready_nodes],
        "blocked_nodes": [node.node_id for node in blocked_nodes],
        "next_node": next_node,
        "unfinished_count": len(unfinished_nodes),
    }


def build_graph_payload(nodes: dict[str, NodeRecord], edges: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "nodes": {
            node_id: {
                "path": nodes[node_id].path,
                "status": nodes[node_id].status,
            }
            for node_id in sorted(nodes)
        },
        "edges": edges,
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def atomic_replace_pair(graph_path: Path, graph_text: str, status_path: Path, status_text: str) -> None:
    graph_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.parent.mkdir(parents=True, exist_ok=True)

    old_graph = graph_path.read_text(encoding="utf-8") if graph_path.exists() else None
    old_status = status_path.read_text(encoding="utf-8") if status_path.exists() else None

    graph_fd, graph_tmp_name = tempfile.mkstemp(prefix="graph.", suffix=".tmp", dir=str(graph_path.parent))
    status_fd, status_tmp_name = tempfile.mkstemp(prefix="graph_status.", suffix=".tmp", dir=str(status_path.parent))
    graph_tmp = Path(graph_tmp_name)
    status_tmp = Path(status_tmp_name)

    try:
        with os.fdopen(graph_fd, "w", encoding="utf-8") as handle:
            handle.write(graph_text)
        with os.fdopen(status_fd, "w", encoding="utf-8") as handle:
            handle.write(status_text)

        os.replace(graph_tmp, graph_path)
        os.replace(status_tmp, status_path)
    except Exception:
        if graph_tmp.exists():
            graph_tmp.unlink()
        if status_tmp.exists():
            status_tmp.unlink()
        if old_graph is not None:
            write_text(graph_path, old_graph)
        if old_status is not None:
            write_text(status_path, old_status)
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh the minimal JSON research scheduler graph.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on legacy status parsing or unrecognized node phase instead of applying compatibility fallbacks.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate graph construction without writing graph outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    edge_registry_path = root / "backend" / "relations" / "edge_registry.json"
    graph_path = root / "backend" / "graph" / "graph.json"
    graph_status_path = root / "backend" / "graph" / "graph_status.json"

    try:
        nodes = discover_nodes(root, strict=args.strict)
        path_to_node = {node.path: node.node_id for node in nodes.values()}
        edges = load_edge_registry(edge_registry_path, path_to_node)
        validate_depends_on_leaf_nodes(nodes, edges)
        detect_depends_on_cycle(nodes, edges)

        graph_payload = build_graph_payload(nodes, edges)
        graph_status_payload = build_graph_status(nodes, edges)
        graph_text = json.dumps(graph_payload, ensure_ascii=False, indent=2) + "\n"
        graph_status_text = json.dumps(graph_status_payload, ensure_ascii=False, indent=2) + "\n"

        if not args.check:
            atomic_replace_pair(graph_path, graph_text, graph_status_path, graph_status_text)
    except Exception as exc:
        print(f"[refresh_failed] {exc}", file=sys.stderr)
        return 1

    label = "refresh_check_ok" if args.check else "refresh_ok"
    print(f"[{label}] nodes={len(nodes)} edges={len(edges)} next_node={graph_status_payload['next_node']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
