#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


CATALOG = Path("backend/registry/skill_registry/skill_catalog.yaml")
LOCAL_ENTRY_RE = re.compile(r"(?m)^\s*(canonical_global_skill|local_wrapper_skill|local_execution_skill):\s*([A-Za-z0-9_-]+)\s*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate skill catalog and node-local skill references.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--out", help="JSON report path.")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0 after writing the report.")
    return parser.parse_args()


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def catalog_entries(root: Path) -> list[dict[str, Any]]:
    payload = read_yaml(root / CATALOG)
    skills = payload.get("skills")
    return [item for item in skills if isinstance(item, dict)] if isinstance(skills, list) else []


def global_skill_names(root: Path) -> set[str]:
    base = root / ".agent" / "skills"
    return {path.parent.name for path in base.glob("*/SKILL.md") if path.is_file()} if base.is_dir() else set()


def new_user_fast_path(root: Path) -> str:
    readme = root / "README.md"
    if not readme.is_file():
        return ""
    text = readme.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^## New User Fast Path\b(.*?)(?=^## |\Z)", text)
    return match.group(1) if match else ""


def local_entry_refs(root: Path) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    research = root / "research"
    if not research.is_dir():
        return refs
    for entry in sorted(research.glob("**/skills/local_entry.md")):
        node = entry.parents[1]
        text = entry.read_text(encoding="utf-8")
        for key, value in LOCAL_ENTRY_RE.findall(text):
            refs.append({"path": rel(entry, root), "node": rel(node, root), "kind": key, "target": value})
    return refs


def build_report(root: Path, report_only: bool) -> dict:
    entries = catalog_entries(root)
    catalog_names = {str(item.get("name", "")).strip() for item in entries if str(item.get("name", "")).strip()}
    globals_ = global_skill_names(root)
    fast_path = new_user_fast_path(root)
    findings: list[dict[str, Any]] = []
    warnings: list[str] = []

    missing_catalog_files = sorted(name for name in catalog_names if name not in globals_)
    orphan_global_skills = sorted(name for name in globals_ if name not in catalog_names)
    for name in missing_catalog_files:
        findings.append({"kind": "catalog_skill_missing_file", "skill": name, "expected": f".agent/skills/{name}/SKILL.md"})

    deprecated_without_replacement = []
    deprecated_in_fast_path = []
    operator_only_exposed = []
    for entry in entries:
        name = str(entry.get("name", "")).strip()
        if entry.get("deprecated") is True:
            if not str(entry.get("replacement", "")).strip():
                deprecated_without_replacement.append(name)
            if name and name in fast_path:
                deprecated_in_fast_path.append(name)
        if entry.get("default_visibility") == "operator_only" and name and name in fast_path:
            operator_only_exposed.append(name)

    for name in deprecated_without_replacement:
        findings.append({"kind": "deprecated_without_replacement", "skill": name})
    for name in deprecated_in_fast_path:
        findings.append({"kind": "deprecated_skill_in_new_user_fast_path", "skill": name})
    for name in operator_only_exposed:
        findings.append({"kind": "operator_only_exposed_to_new_user", "skill": name})

    refs = local_entry_refs(root)
    broken: list[dict[str, str]] = []
    for item in refs:
        node = root / item["node"]
        target = item["target"]
        if item["kind"] == "canonical_global_skill" and target not in globals_:
            broken.append({**item, "reason": "missing_global_skill"})
        if item["kind"] == "local_wrapper_skill" and not (node / "skills" / f"{target}.md").is_file():
            broken.append({**item, "reason": "missing_local_wrapper"})
        if item["kind"] == "local_execution_skill" and not (node / "skills" / f"{target}.md").is_file():
            broken.append({**item, "reason": "missing_local_execution"})
    findings.extend({"kind": "broken_skill_ref", **item} for item in broken)

    if orphan_global_skills:
        warnings.append(f"Global skills not listed in catalog: {', '.join(orphan_global_skills)}")

    return {
        "tool": "validate_skill_refs",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": {
            "catalog_skills": len(catalog_names),
            "global_skills": len(globals_),
            "local_entry_refs": len(refs),
            "broken_skill_refs": len(broken),
            "new_broken_refs": 0,
            "deprecated_without_replacement": len(deprecated_without_replacement),
            "operator_only_exposed_to_new_user": len(operator_only_exposed),
        },
        "findings": findings,
        "warnings": warnings,
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
