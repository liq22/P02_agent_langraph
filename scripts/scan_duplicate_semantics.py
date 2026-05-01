#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


OVERRIDES = Path("backend/registry/skill_registry/local_skill_overrides.yaml")
FIELDS = (
    "purpose",
    "outputs",
    "default_delegate",
    "required_local_reads",
    "decision_rule",
    "blocking_failure_modes",
    "node_mode",
    "node_profile",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan registry/local duplicate semantic definitions.")
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


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def local_equivalent(node: Path, field: str) -> tuple[bool, str | None]:
    prompt = text(node / "prompts" / "research_prompt.md")
    checklist_text = text(node / "prompts" / "acceptance_checklist.yaml")
    entry = text(node / "skills" / "local_entry.md")
    status = read_yaml(node / "status.yaml")
    if field == "purpose":
        return bool(prompt.strip()), "prompts/research_prompt.md" if prompt.strip() else None
    if field == "outputs":
        return bool(checklist_text.strip()), "prompts/acceptance_checklist.yaml" if checklist_text.strip() else None
    if field == "default_delegate":
        ok = bool(re.search(r"canonical_global_skill|local_wrapper_skill|local_execution_skill|default_delegate", entry))
        return ok, "skills/local_entry.md" if ok else None
    if field == "required_local_reads":
        ok = bool(re.search(r"required|read order|input refs|allowed reads", entry, re.I))
        return ok, "skills/local_entry.md" if ok else None
    if field == "decision_rule":
        ok = bool(re.search(r"routes|routing|stop_with|stop rules|delegate", entry, re.I))
        return ok, "skills/local_entry.md" if ok else None
    if field == "blocking_failure_modes":
        ok = bool(re.search(r"blocking|hard[_ -]?fail|failure|stop_if", checklist_text, re.I))
        return ok, "prompts/acceptance_checklist.yaml" if ok else None
    if field == "node_mode":
        return "node_mode" in status, "status.yaml" if "node_mode" in status else None
    if field == "node_profile":
        return "node_profile" in status, "status.yaml" if "node_profile" in status else None
    return False, None


def build_report(root: Path, report_only: bool) -> dict:
    overrides = read_yaml(root / OVERRIDES)
    nodes = overrides.get("nodes") if isinstance(overrides.get("nodes"), dict) else {}
    findings: list[dict[str, Any]] = []
    registry_semantics = 0
    covered = 0
    duplicates = 0
    remaining = 0

    for node_path, cfg in sorted(nodes.items()):
        if not isinstance(cfg, dict):
            continue
        node = root / node_path
        for field in FIELDS:
            if field not in cfg:
                continue
            registry_semantics += 1
            ok, location = local_equivalent(node, field)
            if ok:
                covered += 1
                duplicates += 1
                findings.append({
                    "kind": "duplicate_semantic_definition",
                    "node": node_path,
                    "field": field,
                    "registry": rel(root / OVERRIDES, root),
                    "local_equivalent": location,
                })
            else:
                remaining += 1
                findings.append({
                    "kind": "registry_semantic_pending_migration",
                    "node": node_path,
                    "field": field,
                    "registry": rel(root / OVERRIDES, root),
                })

    migration_coverage = covered / registry_semantics if registry_semantics else 1.0
    return {
        "tool": "scan_duplicate_semantics",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": {
            "registry_node_semantics_total": registry_semantics,
            "duplicate_semantic_definitions": duplicates,
            "registry_node_semantics_remaining": remaining,
            "migration_coverage": round(migration_coverage, 4),
        },
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
