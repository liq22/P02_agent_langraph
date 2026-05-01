#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


SKIP_DIRS = {".git", ".mypy_cache", ".pytest_cache", ".ruff_cache"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inventory repository files for source-of-truth convergence.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", required=True, help="JSON report path.")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0 after writing the report.")
    return parser.parse_args()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def report(root: Path, report_only: bool) -> dict:
    files = iter_files(root)
    empty_files = [path for path in files if path.stat().st_size == 0]
    empty_index_files = [path for path in empty_files if path.name == "index.md" and rel(path, root).startswith("research/")]
    pycache_dirs = [
        path
        for path in root.rglob("__pycache__")
        if path.is_dir() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    ]
    pyc_files = [path for path in files if path.suffix == ".pyc"]
    ds_store_files = [path for path in files if path.name == ".DS_Store"]
    research_nodes = [
        path.parent
        for path in (root / "research").rglob("status.yaml")
        if (path.parent / "README.md").is_file()
    ] if (root / "research").is_dir() else []
    skills = list((root / ".agent" / "skills").glob("*/SKILL.md")) if (root / ".agent" / "skills").is_dir() else []
    schemas = [
        path
        for path in (root / "backend" / "registry" / "schema_registry").glob("*")
        if path.is_file()
    ] if (root / "backend" / "registry" / "schema_registry").is_dir() else []

    findings = []
    for label, paths in (
        ("empty_index_files", empty_index_files),
        ("pycache_dirs", pycache_dirs),
        ("pyc_files", pyc_files),
        ("ds_store_files", ds_store_files),
    ):
        if paths:
            findings.append({"kind": label, "count": len(paths), "paths": [rel(path, root) for path in sorted(paths)[:200]]})

    return {
        "tool": "inventory_repo",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": {
            "total_files": len(files),
            "empty_files": len(empty_files),
            "empty_index_files": len(empty_index_files),
            "pycache_dirs": len(pycache_dirs),
            "pyc_files": len(pyc_files),
            "ds_store_files": len(ds_store_files),
            "skills_total": len(skills),
            "schemas_total": len(schemas),
            "research_nodes": len(research_nodes),
        },
        "findings": findings,
        "warnings": [],
        "errors": [],
    }


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    payload = report(root, args.report_only)
    out = Path(args.out)
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if args.report_only or payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
