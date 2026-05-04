#!/usr/bin/env python3
"""Validate the actual P1_01 node outputs for P02_agent_langraph.

This validator is intentionally structural. It checks that Codex has produced
the node-local artifacts required by the actual P1_01 contract before moving to
review or global gates.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

REQUIRED = [
    "docs/manuscript.md",
    "artifacts/data_lineage.yaml",
    "artifacts/submodule_ref.yaml",
    "artifacts/claim_evidence_registry.yaml",
    "artifacts/failure_register.yaml",
    "artifacts/negative_result_note.md",
    "artifacts/keep_discard_ledger.yaml",
]

RECOMMENDED = [
    "artifacts/vibench_data_factory_binding.yaml",
    "artifacts/data_reading_boundary.yaml",
    "artifacts/phmga_data_protocol_handoff.yaml",
    "artifacts/result_source_map.yaml",
    "logs/codex_run_001.md",
]

REVIEW_REQUIRED = [
    "review/AI_001.md",
    "review/verdict.yaml",
    "review/response.yaml",
]

FORBIDDEN_SUBSTRINGS = [
    "is submission-ready",
    "are submission-ready",
    "submission_ready: true",
    "all experiments passed",
    "main tables are complete",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="ignore")


def validate_verdict(path: Path) -> list[str]:
    errors: list[str] = []
    if yaml is None:
        errors.append("PyYAML unavailable; cannot validate review/verdict.yaml content")
        return errors
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    expected = {
        "review_complete": True,
        "overall_verdict": "pass",
        "hard_fail": False,
        "independence_confirmed": True,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"review/verdict.yaml {key} expected {value!r}, got {data.get(key)!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node-dir", required=True)
    parser.add_argument("--require-review", action="store_true")
    args = parser.parse_args()

    node_dir = Path(args.node_dir)
    errors: list[str] = []
    warnings: list[str] = []

    if not node_dir.exists():
        errors.append(f"node directory missing: {node_dir}")
    for rel in REQUIRED:
        path = node_dir / rel
        if not path.exists():
            errors.append(f"required output missing: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"required output is empty: {rel}")
    for rel in RECOMMENDED:
        path = node_dir / rel
        if not path.exists():
            warnings.append(f"recommended output missing: {rel}")

    for rel in ["docs/manuscript.md", "artifacts/claim_evidence_registry.yaml", "artifacts/negative_result_note.md"]:
        path = node_dir / rel
        if path.exists():
            text = read_text(path).lower()
            for bad in FORBIDDEN_SUBSTRINGS:
                if bad in text:
                    warnings.append(f"potential premature completion phrase in {rel}: {bad}")

    if args.require_review:
        for rel in REVIEW_REQUIRED:
            path = node_dir / rel
            if not path.exists():
                errors.append(f"required review output missing: {rel}")
            elif path.stat().st_size == 0:
                errors.append(f"required review output is empty: {rel}")
        verdict = node_dir / "review/verdict.yaml"
        if verdict.exists():
            errors.extend(validate_verdict(verdict))

    if warnings:
        print("WARNINGS:")
        for item in warnings:
            print(f"- {item}")
    if errors:
        print("ERRORS:")
        for item in errors:
            print(f"- {item}")
        return 1
    print("P1_01 node structural validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
