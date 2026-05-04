
#!/usr/bin/env python3
"""Validate the current P02_agent_langraph P1_01 node package.

This validator is intentionally narrow. It checks the actual current selected
node expected by the P02 submission-ready package and verifies that the node
has produced the local data/provenance artifacts required before downstream
experiments or paper prose can proceed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

EXPECTED_NEXT_NODE = "research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用"
NODE_PATH = Path("research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用")
PHMGA_SUBMODULE_PATH = Path("research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA")

REQUIRED_NODE_INPUTS = [
    "README.md",
    "status.yaml",
    "skills/local_entry.md",
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
]

REQUIRED_OUTPUTS = [
    "docs/manuscript.md",
    "artifacts/data_lineage.yaml",
    "artifacts/submodule_ref.yaml",
    "artifacts/vibench_data_factory_binding.yaml",
    "artifacts/data_reading_boundary.yaml",
    "artifacts/phmga_data_protocol_handoff.yaml",
    "artifacts/result_source_map.yaml",
    "artifacts/claim_evidence_registry.yaml",
    "artifacts/failure_register.yaml",
    "artifacts/negative_result_note.md",
    "artifacts/keep_discard_ledger.yaml",
    "logs/codex_run_001.md",
]

REVIEW_OUTPUTS = [
    "review/AI_001.md",
    "review/人类_001.md",
    "review/verdict.yaml",
    "review/response.yaml",
]

PLACEHOLDER_MARKERS = [
    "<pending",
    "待补充",
    "TODO",
    "TBD",
    "占位",
]


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(f"Failed to read JSON {path}: {exc}") from exc


def exists(root: Path, rel: str | Path) -> bool:
    return (root / rel).exists()


def parse_scalar_yaml(path: Path) -> dict:
    values: dict[str, object] = {}
    for raw_line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not raw_line or raw_line.startswith((" ", "\t", "-")) or ":" not in raw_line:
            continue
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key:
            continue
        lowered = value.lower()
        if lowered == "true":
            values[key] = True
        elif lowered == "false":
            values[key] = False
        elif lowered in {"null", "~", ""}:
            values[key] = None
        else:
            try:
                values[key] = float(value) if "." in value else int(value)
            except ValueError:
                values[key] = value.strip("'\"")
    return values


def has_placeholder(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return any(marker in text for marker in PLACEHOLDER_MARKERS)


def reviewer_id_is_pending(value: object) -> bool:
    text = str(value or "").strip().lower()
    return not text or text.startswith("<pending") or text in {"pending", "none", "null"}


def validate_review_gate(node_dir: Path, errors: list[str]) -> None:
    for rel in REVIEW_OUTPUTS:
        path = node_dir / rel
        if not path.exists():
            errors.append(f"required review output missing: {NODE_PATH / rel}")

    verdict_path = node_dir / "review/verdict.yaml"
    if verdict_path.exists():
        verdict = parse_scalar_yaml(verdict_path)
        if verdict.get("review_complete") is not True:
            errors.append("review/verdict.yaml review_complete is not true")
        if verdict.get("overall_verdict") != "pass":
            errors.append("review/verdict.yaml overall_verdict is not pass")
        if verdict.get("hard_fail") is not False:
            errors.append("review/verdict.yaml hard_fail is not false")
        if verdict.get("independence_confirmed") is not True:
            errors.append("review/verdict.yaml independence_confirmed is not true")
        if reviewer_id_is_pending(verdict.get("reviewer_agent_id")):
            errors.append("review/verdict.yaml reviewer_agent_id is missing or pending")
        overall_score = verdict.get("overall_score")
        if not isinstance(overall_score, (int, float)) or overall_score < 80:
            errors.append("review/verdict.yaml overall_score is missing or below downstream pass threshold 80")

    for rel in ("review/AI_001.md", "review/人类_001.md", "review/response.yaml"):
        path = node_dir / rel
        if path.exists() and has_placeholder(path):
            errors.append(f"review output still contains placeholder marker: {NODE_PATH / rel}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--require-outputs", action="store_true")
    parser.add_argument("--require-review", action="store_true")
    parser.add_argument("--json", dest="json_output", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    warnings: list[str] = []

    graph_status_path = root / "backend/graph/graph_status.json"
    if not graph_status_path.exists():
        errors.append("backend/graph/graph_status.json missing")
    else:
        status = read_json(graph_status_path)
        next_node = status.get("next_node")
        if next_node != EXPECTED_NEXT_NODE:
            errors.append(f"next_node mismatch: expected {EXPECTED_NEXT_NODE!r}, got {next_node!r}")

    gitmodules = root / ".gitmodules"
    if not gitmodules.exists():
        errors.append(".gitmodules missing")
    else:
        text = gitmodules.read_text(encoding="utf-8", errors="replace")
        if str(PHMGA_SUBMODULE_PATH) not in text:
            errors.append("PHMGA submodule path not found in .gitmodules")
        if "journal_thesis" not in text:
            errors.append("PHMGA submodule branch journal_thesis not found in .gitmodules")

    node_dir = root / NODE_PATH
    if not node_dir.exists():
        errors.append(f"selected node path missing: {NODE_PATH}")
    else:
        for rel in REQUIRED_NODE_INPUTS:
            if not (node_dir / rel).exists():
                errors.append(f"required node input missing: {NODE_PATH / rel}")

    if args.require_outputs and node_dir.exists():
        for rel in REQUIRED_OUTPUTS:
            if not (node_dir / rel).exists():
                errors.append(f"required P1_01 output missing: {NODE_PATH / rel}")
        for rel in REVIEW_OUTPUTS:
            if not (node_dir / rel).exists():
                warnings.append(f"review output missing: {NODE_PATH / rel}")

    if args.require_review and node_dir.exists():
        validate_review_gate(node_dir, errors)

    result = {
        "validator": "validate_p1_01_node_package",
        "repo_root": str(root),
        "expected_next_node": EXPECTED_NEXT_NODE,
        "selected_node_path": str(NODE_PATH),
        "phmga_submodule_path": str(PHMGA_SUBMODULE_PATH),
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
