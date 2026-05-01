#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


SCHEMA_DIR = Path("backend/registry/schema_registry")
VERIFIER_REGISTRY = Path("backend/harness/verifier_registry.yaml")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate schema-to-verifier/script/test/contract use.")
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


def files_under(root: Path, dirs: tuple[str, ...]) -> list[Path]:
    out: list[Path] = []
    for item in dirs:
        base = root / item
        if not base.exists():
            continue
        if base.is_file():
            out.append(base)
            continue
        out.extend(path for path in base.rglob("*") if path.is_file())
    return sorted(out)


def corpus_text(root: Path, dirs: tuple[str, ...]) -> str:
    chunks = []
    for path in files_under(root, dirs):
        if SCHEMA_DIR.as_posix() in rel(path, root):
            continue
        try:
            chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
        except OSError:
            continue
    return "\n".join(chunks)


def has_valid_exemption(payload: dict[str, Any]) -> bool:
    exemption = payload.get("explicit_exemption")
    if not isinstance(exemption, dict):
        return False
    return bool(str(exemption.get("reason", "")).strip() and str(exemption.get("expires", "") or exemption.get("expires_on", "")).strip())


def validators(root: Path) -> dict[str, Any]:
    payload = read_yaml(root / VERIFIER_REGISTRY)
    raw = payload.get("validators")
    return raw if isinstance(raw, dict) else {}


def build_report(root: Path, report_only: bool) -> dict:
    schema_base = root / SCHEMA_DIR
    schemas = sorted(path for path in schema_base.glob("*") if path.is_file()) if schema_base.is_dir() else []
    verifier_text = (root / VERIFIER_REGISTRY).read_text(encoding="utf-8", errors="ignore") if (root / VERIFIER_REGISTRY).is_file() else ""
    script_text = corpus_text(root, ("scripts",))
    test_text = corpus_text(root, ("test", "tests"))
    contract_text = corpus_text(root, ("research", "backend/harness"))
    findings: list[dict[str, Any]] = []
    used = 0
    unused = 0
    orphan_artifact = 0

    for schema in schemas:
        payload = read_yaml(schema)
        name = schema.name
        stem = schema.stem
        use = {
            "verifier_registry": name in verifier_text or stem in verifier_text,
            "scripts": name in script_text or stem in script_text,
            "tests": name in test_text or stem in test_text,
            "active_node_contract": name in contract_text or stem in contract_text,
            "explicit_exemption": has_valid_exemption(payload),
        }
        if any(use.values()):
            used += 1
        else:
            unused += 1
            findings.append({"kind": "active_schema_without_validator", "schema": rel(schema, root), "use": use})
            if name.endswith(".schema.yaml"):
                orphan_artifact += 1
                findings.append({"kind": "orphan_artifact_schema", "schema": rel(schema, root)})

    validator_missing = []
    for name, entry in validators(root).items():
        if not isinstance(entry, dict):
            continue
        has_schema = any(key in entry for key in ("schema", "schema_ref", "schemas"))
        if not has_schema and not has_valid_exemption(entry):
            validator_missing.append(str(name))
            findings.append({"kind": "validator_without_schema_or_exemption", "validator": str(name)})

    total = len(schemas)
    return {
        "tool": "validate_schema_use",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "report_only": report_only,
        "status": "findings" if findings else "pass",
        "metrics": {
            "active_schema_count": total,
            "schema_use_coverage": round(used / total, 4) if total else 1.0,
            "active_schema_without_validator": unused,
            "orphan_artifact_schema": orphan_artifact,
            "validator_without_schema_or_exemption": len(validator_missing),
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
