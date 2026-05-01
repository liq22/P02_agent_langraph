#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


VALID_MODES = {"parent", "lite", "standard", "execution"}
VALID_PROFILES = {"routing_parent", "lite_research_leaf", "evidence_leaf", "hard_gate", "normal"}
OVERRIDES = Path("backend/registry/skill_registry/local_skill_overrides.yaml")
CATALOG = Path("backend/registry/skill_registry/skill_catalog.yaml")
GRAPH = Path("backend/graph/graph.json")
GRAPH_STATUS = Path("backend/graph/graph_status.json")
SKILL_REF_RE = re.compile(r"(?m)^\s*(canonical_global_skill|local_wrapper_skill|local_execution_skill):\s*([A-Za-z0-9_-]+)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate node contract convergence baseline.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", help="JSON report path.")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0 after writing the report.")
    return parser.parse_args()


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def node_dirs(root: Path) -> list[Path]:
    research = root / "research"
    if not research.is_dir():
        return []
    return sorted(path.parent for path in research.rglob("status.yaml") if (path.parent / "README.md").is_file())


def catalog_names(root: Path) -> set[str]:
    payload = read_yaml(root / CATALOG)
    skills = payload.get("skills") if isinstance(payload.get("skills"), list) else []
    return {str(item.get("name", "")).strip() for item in skills if isinstance(item, dict) and str(item.get("name", "")).strip()}


def global_skill_names(root: Path) -> set[str]:
    base = root / ".agent" / "skills"
    return {path.parent.name for path in base.glob("*/SKILL.md") if path.is_file()} if base.is_dir() else set()


def duplicate_locations(root: Path, node: Path, key: str) -> list[str]:
    locations = []
    for path in sorted(node.rglob("*")):
        if not path.is_file() or path.name == "status.yaml":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if re.search(rf"(?m)^\s*[-#]*\s*{re.escape(key)}\s*[:`]", text):
            locations.append(rel(path, root))
    return locations


def resolve_next_node(root: Path) -> tuple[str | None, str | None]:
    status = read_json(root / GRAPH_STATUS)
    graph = read_json(root / GRAPH)
    next_node = status.get("next_node")
    if not isinstance(next_node, str) or not next_node:
        return None, None
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    if next_node in nodes and isinstance(nodes[next_node], dict):
        path = nodes[next_node].get("path")
        return next_node, path if isinstance(path, str) else None
    if (root / next_node).exists():
        return next_node, next_node
    return next_node, None


def is_leaf(path: str, all_nodes: list[str]) -> bool:
    prefix = path.rstrip("/") + "/"
    return not any(other.startswith(prefix) for other in all_nodes if other != path)


def build_report(root: Path, report_only: bool) -> dict:
    overrides = read_yaml(root / OVERRIDES)
    override_nodes = overrides.get("nodes") if isinstance(overrides.get("nodes"), dict) else {}
    known_skills = catalog_names(root) | global_skill_names(root)
    nodes = node_dirs(root)
    all_node_paths = [rel(node, root) for node in nodes]
    findings: list[dict[str, Any]] = []
    node_with_findings: set[str] = set()
    duplicate_mode_defs = 0
    duplicate_profile_defs = 0
    execution_nodes = 0
    execution_contract_ok = 0
    local_entry_leaf_count = 0
    leaf_count = 0

    for node in nodes:
        node_path = rel(node, root)
        status = read_yaml(node / "status.yaml")
        cfg = override_nodes.get(node_path) if isinstance(override_nodes.get(node_path), dict) else {}
        mode = str(status.get("node_mode") or cfg.get("node_mode") or "").strip()
        profile = str(status.get("node_profile") or cfg.get("node_profile") or "").strip()
        mode_dupes = duplicate_locations(root, node, "node_mode")
        profile_dupes = duplicate_locations(root, node, "node_profile")
        duplicate_mode_defs += len(mode_dupes)
        duplicate_profile_defs += len(profile_dupes)
        if mode_dupes:
            findings.append({"kind": "duplicate_node_mode_definition", "node": node_path, "locations": mode_dupes})
            node_with_findings.add(node_path)
        if profile_dupes:
            findings.append({"kind": "duplicate_node_profile_definition", "node": node_path, "locations": profile_dupes})
            node_with_findings.add(node_path)
        if not mode:
            findings.append({"kind": "missing_node_mode", "node": node_path})
            node_with_findings.add(node_path)
        elif mode not in VALID_MODES:
            findings.append({"kind": "invalid_node_mode", "node": node_path, "node_mode": mode})
            node_with_findings.add(node_path)
        if mode == "hard_gate":
            findings.append({"kind": "hard_gate_used_as_node_mode", "node": node_path})
            node_with_findings.add(node_path)
        if profile and profile not in VALID_PROFILES:
            findings.append({"kind": "invalid_node_profile", "node": node_path, "node_profile": profile})
            node_with_findings.add(node_path)

        if mode == "parent" and (node / "skills" / "SOP.md").is_file():
            findings.append({"kind": "parent_has_sop", "node": node_path})
            node_with_findings.add(node_path)
        if mode == "lite":
            for required in ("prompts/research_prompt.md", "prompts/acceptance_checklist.yaml", "skills/local_entry.md"):
                if not (node / required).is_file():
                    findings.append({"kind": "lite_missing_required_file", "node": node_path, "path": required})
                    node_with_findings.add(node_path)
        if mode == "execution":
            execution_nodes += 1
            if (node / "artifacts" / "execution_contract.yaml").is_file():
                execution_contract_ok += 1
            else:
                findings.append({"kind": "execution_missing_contract", "node": node_path, "path": "artifacts/execution_contract.yaml"})
                node_with_findings.add(node_path)

        if is_leaf(node_path, all_node_paths):
            leaf_count += 1
            if (node / "skills" / "local_entry.md").is_file():
                local_entry_leaf_count += 1
        entry = node / "skills" / "local_entry.md"
        if entry.is_file():
            text = entry.read_text(encoding="utf-8")
            for key, target in SKILL_REF_RE.findall(text):
                if key == "canonical_global_skill" and target not in known_skills:
                    findings.append({"kind": "local_entry_missing_worker", "node": node_path, "target": target})
                    node_with_findings.add(node_path)
                if key == "local_wrapper_skill" and not (node / "skills" / f"{target}.md").is_file():
                    findings.append({"kind": "local_entry_missing_wrapper", "node": node_path, "target": target})
                    node_with_findings.add(node_path)
                if key == "local_execution_skill" and not (node / "skills" / f"{target}.md").is_file():
                    findings.append({"kind": "local_entry_missing_execution", "node": node_path, "target": target})
                    node_with_findings.add(node_path)

    next_id, next_path = resolve_next_node(root)
    next_exists = bool(next_path and (root / next_path).is_dir())
    next_leaf = bool(next_path and is_leaf(next_path, all_node_paths))
    next_local_entry = bool(next_path and (root / next_path / "skills" / "local_entry.md").is_file())
    if next_id and not next_exists:
        findings.append({"kind": "next_node_not_resolved", "next_node": next_id})
    if next_exists and not next_leaf:
        findings.append({"kind": "next_node_is_not_leaf", "next_node": next_id, "path": next_path})
    if next_exists and not next_local_entry:
        findings.append({"kind": "next_node_missing_local_entry", "next_node": next_id, "path": next_path})

    node_count = len(nodes)
    pass_rate = (node_count - len(node_with_findings)) / node_count if node_count else 1.0
    return {
        "tool": "validate_node_contracts",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": {
            "research_nodes": node_count,
            "node_contract_pass_rate": round(pass_rate, 4),
            "duplicate_node_mode_definitions": duplicate_mode_defs,
            "duplicate_node_profile_definitions": duplicate_profile_defs,
            "selected_leaf_local_entry_coverage": 1.0 if next_leaf and next_local_entry else 0.0,
            "execution_contract_coverage": round(execution_contract_ok / execution_nodes, 4) if execution_nodes else 1.0,
            "leaf_nodes": leaf_count,
            "leaf_local_entry_coverage": round(local_entry_leaf_count / leaf_count, 4) if leaf_count else 1.0,
            "next_node_exists": next_exists,
            "next_node_is_leaf": next_leaf,
            "next_node_has_local_entry": next_local_entry,
        },
        "next_node": {"id": next_id, "path": next_path},
        "findings": findings,
        "warnings": [],
        "errors": [],
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    payload = build_report(root, args.report_only)
    if args.out:
        out = Path(args.out)
        if not out.is_absolute():
            out = root / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if args.report_only or payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
