#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

try:
    import yaml
except Exception:
    yaml = None

DEFAULT_SCORECARDS = {
    "proposal_node": {
        "scientific_question": 0.25,
        "hypothesis_testability": 0.25,
        "route_clarity": 0.20,
        "risk_boundary": 0.15,
        "acceptance_metric": 0.15,
    },
    "experiment_node": {
        "reproducibility": 0.25,
        "baseline_fairness": 0.20,
        "metric_definition": 0.20,
        "data_availability": 0.20,
        "artifact_plan": 0.15,
    },
    "manuscript_node": {
        "structure": 0.20,
        "claim_precision": 0.25,
        "evidence_grounding": 0.25,
        "writing_quality": 0.15,
        "node_completion": 0.15,
    },
    "review_node": {
        "criticism_coverage": 0.30,
        "severity_calibration": 0.20,
        "action_mapping": 0.25,
        "unresolved_issue_tracking": 0.25,
    },
    "response_node": {
        "response_coverage": 0.30,
        "manuscript_change_link": 0.25,
        "evidence_attachment": 0.20,
        "tone_control": 0.15,
        "completeness": 0.10,
    },
}

VALIDATORS = {
    "proposal_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("claim_evidence_check", True),
        ("citation_integrity", True),
        ("edit_scope_check", True),
        ("node_status_check", True),
    ],
    "experiment_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("edit_scope_check", True),
        ("node_status_check", True),
    ],
    "manuscript_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("claim_evidence_check", True),
        ("citation_integrity", True),
        ("edit_scope_check", True),
        ("latex_build", True),
        ("node_status_check", True),
    ],
    "review_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("response_coverage_check", True),
        ("edit_scope_check", True),
        ("node_status_check", True),
    ],
    "response_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("claim_evidence_check", True),
        ("citation_integrity", True),
        ("response_coverage_check", True),
        ("edit_scope_check", True),
        ("node_status_check", True),
    ],
    "generic_node": [
        ("markdown_structure", True),
        ("acceptance_checklist", True),
        ("edit_scope_check", True),
        ("node_status_check", True),
    ],
}


def dump_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if yaml:
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    else:
        import json
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_yaml(path: Path) -> dict:
    if not yaml:
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def node_stage(status_path: Path) -> str:
    data = load_yaml(status_path)
    lifecycle = data.get("lifecycle") if isinstance(data.get("lifecycle"), dict) else {}
    return str(data.get("status") or lifecycle.get("stage") or "seed")


def main() -> int:
    ap = argparse.ArgumentParser(description="Forge a minimal harness pack for a research node.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--node", required=True)
    ap.add_argument("--task-type", default="manuscript_node", choices=["proposal_node", "experiment_node", "manuscript_node", "review_node", "response_node", "generic_node"])
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    node = (root / args.node).resolve()
    if not node.is_dir():
        raise SystemExit(f"Node does not exist: {node}")
    for rel in ["README.md", "status.yaml", "prompts/research_prompt.md", "prompts/acceptance_checklist.yaml"]:
        if not (node / rel).is_file():
            raise SystemExit(f"Missing required node file: {args.node}/{rel}")

    harness = node / "harness.yaml"
    if args.force or not harness.exists():
        expected_primary = ["docs/manuscript.md"]
        if args.task_type == "response_node":
            expected_primary = ["docs/response_matrix.md", "docs/review_response.md"]
        validator_specs = [
            {"id": validator_id, "required": required}
            for validator_id, required in VALIDATORS.get(args.task_type, VALIDATORS["generic_node"])
        ]
        data = {
            "node_id": args.node.replace("/", "::"),
            "node_path": args.node,
            "stage": node_stage(node / "status.yaml"),
            "task_type": args.task_type,
            "inputs": {
                "required_files": [
                    "README.md",
                    "status.yaml",
                    *expected_primary,
                    "prompts/research_prompt.md",
                    "prompts/acceptance_checklist.yaml",
                ]
            },
            "allowed_actions": {
                "can_modify": [
                    "docs/*.md",
                    "logs/*.md",
                    "logs/*.json",
                ],
                "cannot_modify": [
                    "README.md",
                    "status.yaml",
                    "docs/HUMAN_ONLY.md",
                ],
            },
            "expected_outputs": {
                "primary": expected_primary,
                "secondary": ["logs/eval_report.md", "logs/claim_evidence_map.md"],
            },
            "validators": validator_specs,
            "scorecard": {
                "pass_threshold": 0.80,
                "dimensions": DEFAULT_SCORECARDS.get(args.task_type, {"completion": 1.0}),
            },
            "human_gate": {
                "required_before_stage_change": True,
                "protected_files": ["status.yaml", "README.md", "docs/HUMAN_ONLY.md"],
            },
            "stop_rules": ["missing_required_input", "validator_failed", "score_below_threshold", "human_gate_required"],
        }
        dump_yaml(harness, data)

    print(f"Forged harness pack at: {node}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
