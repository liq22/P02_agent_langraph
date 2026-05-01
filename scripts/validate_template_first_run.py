#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path


GRAPH = Path("backend/graph/graph.json")
GRAPH_STATUS = Path("backend/graph/graph_status.json")
REQUIRED_FILES = (
    "README.md",
    "status.yaml",
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "skills/local_entry.md",
)
WORKER_RE = re.compile(r"(?m)^\s*canonical_global_skill:\s*([A-Za-z0-9_-]+)\s*$")
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Static first-run validation for a minimal template/root.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", help="JSON report path.")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0 after writing the report.")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def resolve_next_node(root: Path) -> tuple[str | None, str | None, list[str]]:
    graph_status = read_json(root / GRAPH_STATUS)
    graph = read_json(root / GRAPH)
    next_node = graph_status.get("next_node")
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    paths = []
    for value in nodes.values():
        if isinstance(value, dict) and isinstance(value.get("path"), str):
            paths.append(value["path"])
    if not isinstance(next_node, str) or not next_node:
        return None, None, paths
    if next_node in nodes and isinstance(nodes[next_node], dict):
        path = nodes[next_node].get("path")
        return next_node, path if isinstance(path, str) else None, paths
    if (root / next_node).exists():
        return next_node, next_node, paths
    return next_node, None, paths


def is_leaf(path: str | None, all_paths: list[str]) -> bool:
    if not path:
        return False
    prefix = path.rstrip("/") + "/"
    return not any(other.startswith(prefix) for other in all_paths if other != path)


def declared_worker_exists(root: Path, node_path: str | None) -> tuple[bool, str | None]:
    if not node_path:
        return False, None
    entry = root / node_path / "skills" / "local_entry.md"
    if not entry.is_file():
        return False, None
    match = WORKER_RE.search(entry.read_text(encoding="utf-8"))
    if not match:
        return True, None
    worker = match.group(1)
    return (root / ".agent" / "skills" / worker / "SKILL.md").is_file(), worker


def broken_readme_links(root: Path) -> list[str]:
    readme = root / "README.md"
    if not readme.is_file():
        return ["README.md missing"]
    broken = []
    for link in LINK_RE.findall(readme.read_text(encoding="utf-8")):
        target = link.split("#", 1)[0]
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (root / target).exists():
            broken.append(target)
    return sorted(set(broken))


def build_report(root: Path, report_only: bool) -> dict:
    started = time.perf_counter()
    next_id, next_path, graph_paths = resolve_next_node(root)
    required_missing = []
    if next_path:
        for item in REQUIRED_FILES:
            if not (root / next_path / item).is_file():
                required_missing.append(f"{next_path}/{item}")
    worker_ok, worker = declared_worker_exists(root, next_path)
    links = broken_readme_links(root)
    metrics = {
        "next_node_exists": bool(next_path and (root / next_path).is_dir()),
        "next_node_is_leaf": is_leaf(next_path, graph_paths),
        "next_node_has_local_entry": bool(next_path and (root / next_path / "skills" / "local_entry.md").is_file()),
        "declared_worker_exists": worker_ok,
        "required_files_exist": not required_missing,
        "dry_run_no_model_no_network": True,
        "dry_run_time": round(time.perf_counter() - started, 4),
        "required_concepts_before_first_run": len(REQUIRED_FILES),
        "broken_readme_links": len(links),
    }
    findings = []
    for key, value in metrics.items():
        if key in {"dry_run_time", "required_concepts_before_first_run", "broken_readme_links"}:
            continue
        if value is not True:
            findings.append({"kind": "template_first_run_check_failed", "check": key})
    for path in required_missing:
        findings.append({"kind": "required_file_missing", "path": path})
    for link in links:
        findings.append({"kind": "broken_readme_link", "target": link})
    return {
        "tool": "validate_template_first_run",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": metrics | {"template_first_run_pass": not findings},
        "next_node": {"id": next_id, "path": next_path, "declared_worker": worker},
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
