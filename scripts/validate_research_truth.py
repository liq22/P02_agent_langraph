#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


DONE_STATUSES = {"done", "archive"}
COMPLETE_ITEM_STATUSES = {"done", "pass", "passed", "complete", "completed", "ok", "true", "yes"}
PLACEHOLDER_MARKERS = ("<待填写>", "<pending", "待补充", "TODO", "TBD", "placeholder")
PLACEHOLDER_AGENT_MARKERS = ("<pending", "<authoring_agent_id>", "待补充", "TODO", "TBD", "placeholder")
REQUIRED_REVIEW_DIMENSIONS = (
    "originality_novelty",
    "scientific_importance",
    "evidence_technical_soundness",
    "reproducibility_transparency",
    "broad_interest_story_clarity",
    "review_robustness",
)
CHECKLIST_SECTIONS = (
    "required_questions_answered",
    "required_outputs",
    "quality_checks",
    "handoff_ready_if",
)
P0_01 = Path("research/P0_项目申请书/P0_01_研究背景与调研")
P1_04 = Path("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证")
P1_05 = Path("research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理")
P1_09 = Path("research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿")
P2_01 = Path("research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature")
P2_02_03 = Path("research/P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿")
P2_03 = Path("research/P2_论文撰写/P2_03_定稿_tex")
P2_04 = Path("research/P2_论文撰写/P2_04_形式检查")
P4_07 = Path("research/P4_论文回复_response/P4_07_再投稿打包")
P1_08 = Path("research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格")
P3_04 = Path("research/P3_论文模拟评审与修改_多轮/P3_04_修订动作")
P4_02 = Path("research/P4_论文回复_response/P4_02_问题映射矩阵")
P4_05 = Path("research/P4_论文回复_response/P4_05_覆盖检查")
P4_06 = Path("research/P4_论文回复_response/P4_06_修改证据")
P1_04_RESULTS = P1_04 / "artifacts" / "auto_experiment" / "results.tsv"
RESULT_STATUSES = {"supported", "unsupported", "unclear"}
CITATION_CRITICALITIES = {
    "core_claim",
    "background_context",
    "method_reference",
    "comparison_baseline",
    "format_supporting",
}
CORE_CITATION_CRITICALITIES = {"core_claim", "comparison_baseline"}
CITATION_SUPPORT_STATUSES = {
    "verified",
    "minor_distortion",
    "major_distortion",
    "unverifiable",
    "unverifiable_access",
    "contradiction",
}
BLOCKING_CITATION_SUPPORT_STATUSES = {
    "major_distortion",
    "unverifiable",
    "unverifiable_access",
    "contradiction",
}
CITATION_ACTIONS = {"keep", "revise_claim", "replace_source", "block_handoff"}
FIGURE_SOURCE_KINDS = {"tex", "python", "pdf"}
FIGURE_NECESSITIES = {"essential", "supporting", "supplemental"}
FIGURE_STATUSES = {"draft", "accepted", "locked"}
FIGURE_MANIFEST_NODES = (P1_09, P2_02_03)
FIGURE_QUALITY_CHECKS = {
    "vector_or_dpi_checked",
    "caption_self_contained",
    "colorblind_or_grayscale_checked",
    "source_permission_checked",
}
VENUE_PROFILES = {
    "nature_article",
    "ieee_tpami",
    "elsevier_specialist_engineering_imrad",
    "ieee_transactions_technical",
    "nature_broad_interest",
}
VENUE_GATE_STAGES = {"draft", "review", "submission"}
VENUE_FIT_DECISIONS = {"venue_gate_passed", "revise", "block", "not_fit"}
GAP_EVIDENCE_STATUSES = {"supported", "weak", "pending", "contradicted"}
CLAIM_TYPES = {"core_claim", "background", "method", "result", "limitation", "response_commitment"}
EVIDENCE_TYPES = {"citation", "experiment", "figure", "table", "code", "review_comment", "revision_diff"}
CLAIM_SUPPORT_STATUSES = {"supported", "weak", "contradicted", "pending", "not_applicable"}
BLOCKING_CLAIM_TYPES = {"core_claim", "result", "response_commitment"}
BLOCKING_CLAIM_SUPPORT_STATUSES = {"contradicted", "pending"}
CLAIM_ACTIONS = {"keep", "revise_claim", "replace_source", "document_limitation", "block_handoff"}
FAILURE_SEVERITIES = {"low", "medium", "high"}
FAILURE_STATUSES = {"open", "explained", "resolved", "accepted_limitation"}
FAILURE_ACTIONS = {"revise_claim", "add_experiment", "document_limitation", "discard_claim", "no_action"}
KEEP_DISCARD_DECISIONS = {"keep", "discard", "defer"}
MAPPING_STATUSES = {"mapped", "covered", "uncovered", "pending"}
COVERAGE_STATUSES = {"covered", "partial", "uncovered", "pending"}
REVISION_STATUSES = {"applied", "verified", "pending", "missing"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate research truth gates without writing repo state.")
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument(
        "--require-submission",
        action="store_true",
        help="Require the discovered research tree to be submission-ready, not merely internally consistent.",
    )
    parser.add_argument(
        "--min-review-score",
        type=float,
        default=90.0,
        help="Minimum accepted per-node Nature-level review score. Defaults to 90.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def load_yaml_if_present(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return load_yaml(path)


def collect_values(payload: Any, keys: set[str]) -> set[str]:
    values: set[str] = set()
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key) in keys and value not in (None, ""):
                values.add(str(value))
            values.update(collect_values(value, keys))
    elif isinstance(payload, list):
        for item in payload:
            values.update(collect_values(item, keys))
    return values


def entries_for(payload: dict[str, Any], keys: tuple[str, ...]) -> list[Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def has_list_field(payload: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return any(isinstance(payload.get(key), list) for key in keys)


def required_one_of_text(entry: dict[str, Any], fields: tuple[str, ...], rel: str, label: str, errors: list[str]) -> str:
    for field in fields:
        value = norm(entry.get(field))
        if value:
            return value
    errors.append(f"{rel}: {label} missing one of {', '.join(fields)}")
    return ""


def node_dirs(root: Path) -> list[Path]:
    research = root / "research"
    if not research.is_dir():
        return []
    return sorted(
        path.parent
        for path in research.glob("**/status.yaml")
        if (path.parent / "README.md").is_file()
        and not node_is_parent(path.parent)
    )


def node_is_parent(node: Path) -> bool:
    checklist = node / "prompts" / "acceptance_checklist.yaml"
    if not checklist.is_file():
        return False
    payload = load_yaml(checklist)
    return str(payload.get("node_kind", "")).strip().lower() == "parent"


def node_stage(status_payload: dict[str, Any]) -> str | None:
    if "status" in status_payload:
        return str(status_payload.get("status", "")).strip().lower()
    lifecycle = status_payload.get("lifecycle")
    if isinstance(lifecycle, dict):
        return str(lifecycle.get("stage", "")).strip().lower()
    return None


def item_is_complete(item: Any) -> bool:
    if not isinstance(item, dict):
        return False
    return str(item.get("status", "")).strip().lower() in COMPLETE_ITEM_STATUSES


def has_placeholder(path: Path) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    return any(marker.lower() in text.lower() for marker in PLACEHOLDER_MARKERS)


def payload_text(payload: Any) -> str:
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def has_upstream_ledger_ref(payload: Any) -> bool:
    text = payload_text(payload)
    return P1_04_RESULTS.as_posix() in text or (
        "P1_04" in text and "artifacts/auto_experiment/results.tsv" in text
    )


def value_is_present(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (int, float)):
        return True
    if isinstance(value, list):
        return any(value_is_present(item) for item in value)
    if isinstance(value, dict):
        return any(value_is_present(item) for item in value.values())
    return value is not None


def has_ledger_row_ref(payload: Any) -> bool:
    row_keys = {"ledger_row", "ledger_rows", "row_id", "row_ids", "run_id", "run_ids"}
    if isinstance(payload, dict):
        for key, value in payload.items():
            if str(key).strip().lower() in row_keys and value_is_present(value):
                return True
            if has_ledger_row_ref(value):
                return True
    if isinstance(payload, list):
        return any(has_ledger_row_ref(item) for item in payload)
    return False


def norm(value: Any) -> str:
    return str(value or "").strip()


def norm_lower(value: Any) -> str:
    return norm(value).lower()


def list_payload(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def required_text(entry: dict[str, Any], field: str, rel: str, label: str, errors: list[str]) -> str:
    value = norm(entry.get(field))
    if not value:
        errors.append(f"{rel}: {label} missing {field}")
    return value


def required_mapping(entry: dict[str, Any], field: str, rel: str, label: str, errors: list[str]) -> dict[str, Any]:
    value = entry.get(field)
    if not isinstance(value, dict):
        errors.append(f"{rel}: {label} missing mapping {field}")
        return {}
    return value


def artifact_path_exists(root: Path, manifest_path: Path, value: str) -> bool:
    if not value:
        return False
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate.is_file() or candidate.is_dir()
    return (root / candidate).is_file() or (root / candidate).is_dir() or (manifest_path.parent / candidate).is_file() or (manifest_path.parent / candidate).is_dir()


def normalized_agent_id(value: Any) -> str:
    return str(value or "").strip()


def agent_id_is_pending(value: Any) -> bool:
    text = normalized_agent_id(value)
    if not text:
        return True
    lower = text.lower()
    return any(marker.lower() in lower for marker in PLACEHOLDER_AGENT_MARKERS)


def validate_checklist(node: Path, rel: str, errors: list[str]) -> None:
    checklist = node / "prompts" / "acceptance_checklist.yaml"
    if not checklist.is_file():
        errors.append(f"{rel}: missing prompts/acceptance_checklist.yaml")
        return
    payload = load_yaml(checklist)
    for section in CHECKLIST_SECTIONS:
        for index, item in enumerate(payload.get(section) or [], start=1):
            if not item_is_complete(item):
                errors.append(f"{rel}: {section}[{index}] is not complete")
    gate = payload.get("external_review_gate")
    if isinstance(gate, dict) and gate.get("required") is True:
        pass_condition = gate.get("pass_condition") if isinstance(gate.get("pass_condition"), dict) else {}
        if pass_condition.get("review_complete") is not True:
            errors.append(f"{rel}: external review gate does not require review_complete=true")
        if pass_condition.get("overall_verdict") != "pass":
            errors.append(f"{rel}: external review gate does not require overall_verdict=pass")
        if pass_condition.get("hard_fail") is not False:
            errors.append(f"{rel}: external review gate does not require hard_fail=false")
        if pass_condition.get("independence_confirmed") is not True:
            errors.append(f"{rel}: external review gate does not require independence_confirmed=true")


def validate_review(node: Path, rel: str, min_score: float, author_agent_id: str, errors: list[str]) -> None:
    verdict = node / "review" / "verdict.yaml"
    if not verdict.is_file():
        errors.append(f"{rel}: missing review/verdict.yaml")
        return
    payload = load_yaml(verdict)
    reviewer_agent_id = normalized_agent_id(payload.get("reviewer_agent_id"))
    if payload.get("review_complete") is not True:
        errors.append(f"{rel}: review_complete is not true")
    if payload.get("overall_verdict") != "pass":
        errors.append(f"{rel}: overall_verdict is not pass")
    if payload.get("hard_fail") is not False:
        errors.append(f"{rel}: hard_fail is not false")
    if payload.get("independence_confirmed") is not True:
        errors.append(f"{rel}: reviewer independence is not confirmed")
    if agent_id_is_pending(reviewer_agent_id):
        errors.append(f"{rel}: reviewer_agent_id is missing or placeholder")
    if author_agent_id and reviewer_agent_id == author_agent_id:
        errors.append(f"{rel}: reviewer_agent_id matches author_agent_id")
    score = payload.get("overall_score")
    if not isinstance(score, (int, float)) or float(score) < min_score:
        errors.append(f"{rel}: overall_score is below {min_score:g}")
    dimension_scores = payload.get("dimension_scores")
    if not isinstance(dimension_scores, dict):
        errors.append(f"{rel}: missing dimension_scores")
        return
    for name in REQUIRED_REVIEW_DIMENSIONS:
        value = dimension_scores.get(name)
        if not isinstance(value, (int, float)):
            errors.append(f"{rel}: dimension_scores.{name} is not numeric")


def validate_no_placeholders(node: Path, rel: str, errors: list[str]) -> None:
    for candidate in (
        node / "docs" / "manuscript.md",
        node / "review" / "AI_001.md",
        node / "review" / "response.yaml",
        node / "review" / "verdict.yaml",
        node / "tex" / "main.tex",
    ):
        if has_placeholder(candidate):
            errors.append(f"{rel}: placeholder marker remains in {candidate.relative_to(node).as_posix()}")


def validate_author_identity(rel: str, status_payload: dict[str, Any], errors: list[str]) -> str:
    author_agent_id = normalized_agent_id(status_payload.get("author_agent_id"))
    if agent_id_is_pending(author_agent_id):
        errors.append(f"{rel}: author_agent_id is missing or placeholder")
    return author_agent_id


def validate_execution_node(root: Path, errors: list[str]) -> None:
    node = root / P1_04
    rel = P1_04.as_posix()
    contract = node / "artifacts" / "execution_contract.yaml"
    if not contract.is_file():
        errors.append(f"{rel}: missing artifacts/execution_contract.yaml")
        return
    payload = load_yaml(contract)
    if payload.get("contract_mode") != "executable":
        errors.append(f"{rel}: execution_contract.yaml contract_mode is not executable")
    if not payload.get("repo_path"):
        errors.append(f"{rel}: execution contract missing repo_path")
    if not isinstance(payload.get("editable_paths"), list) or not payload.get("editable_paths"):
        errors.append(f"{rel}: execution contract missing editable_paths")
    if not payload.get("run_command"):
        errors.append(f"{rel}: execution contract missing run_command")
    metric = payload.get("metric")
    if not isinstance(metric, dict) or not all(metric.get(key) for key in ("name", "direction", "pattern")):
        errors.append(f"{rel}: execution contract metric is incomplete")
    budget = payload.get("budget")
    if not isinstance(budget, dict) or budget.get("max_minutes_per_run") is None:
        errors.append(f"{rel}: execution contract budget is incomplete")
    if not (node / "artifacts" / "auto_experiment" / "results.tsv").is_file():
        errors.append(f"{rel}: missing artifacts/auto_experiment/results.tsv")
    if not (node / "logs" / "auto_experiment" / "latest_run.log").is_file():
        errors.append(f"{rel}: missing logs/auto_experiment/latest_run.log")


def validate_result_registry(payload: dict[str, Any], rel: str, errors: list[str]) -> None:
    entries: list[Any] = []
    for key in ("claims", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            entries.extend(value)
    if not entries:
        errors.append(f"{rel}: result_registry.yaml has no claims/results entries")
        return
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, dict):
            errors.append(f"{rel}: result_registry entry[{index}] is not a mapping")
            continue
        status = str(entry.get("status", "")).strip().lower()
        if status not in RESULT_STATUSES:
            errors.append(f"{rel}: result_registry entry[{index}] missing supported/unsupported/unclear status")
        if not has_upstream_ledger_ref(entry):
            errors.append(f"{rel}: result_registry entry[{index}] evidence is not anchored to P1_04 results.tsv")
        if not has_ledger_row_ref(entry):
            errors.append(f"{rel}: result_registry entry[{index}] evidence lacks concrete ledger row/run reference")


def validate_hypothesis_status(payload: dict[str, Any], rel: str, errors: list[str]) -> None:
    hypotheses = payload.get("hypotheses")
    if not isinstance(hypotheses, list) or not hypotheses:
        errors.append(f"{rel}: hypothesis_status.yaml has no hypotheses")
        return
    for index, item in enumerate(hypotheses, start=1):
        if not isinstance(item, dict):
            errors.append(f"{rel}: hypothesis_status hypothesis[{index}] is not a mapping")
            continue
        status = str(item.get("status", "")).strip().lower()
        if status not in RESULT_STATUSES:
            errors.append(f"{rel}: hypothesis_status hypothesis[{index}] missing supported/unsupported/unclear status")


def validate_result_synthesis(root: Path, errors: list[str]) -> None:
    node = root / P1_05
    rel = P1_05.as_posix()
    registry = node / "artifacts" / "result_registry.yaml"
    hypothesis = node / "artifacts" / "hypothesis_status.yaml"
    paper_summary = node / "artifacts" / "paper_ready_result_summary.md"
    upstream_results = root / P1_04_RESULTS
    if not registry.is_file():
        errors.append(f"{rel}: missing artifacts/result_registry.yaml")
    else:
        if has_placeholder(registry):
            errors.append(f"{rel}: placeholder marker remains in artifacts/result_registry.yaml")
        validate_result_registry(load_yaml(registry), rel, errors)
    if not hypothesis.is_file():
        errors.append(f"{rel}: missing artifacts/hypothesis_status.yaml")
    else:
        if has_placeholder(hypothesis):
            errors.append(f"{rel}: placeholder marker remains in artifacts/hypothesis_status.yaml")
        validate_hypothesis_status(load_yaml(hypothesis), rel, errors)
    if not paper_summary.is_file():
        errors.append(f"{rel}: missing artifacts/paper_ready_result_summary.md")
    elif has_placeholder(paper_summary):
        errors.append(f"{rel}: placeholder marker remains in artifacts/paper_ready_result_summary.md")
    if not upstream_results.is_file():
        errors.append(f"{rel}: upstream P1_04 results.tsv is missing")


def validate_tex_submission(root: Path, errors: list[str]) -> None:
    rel = P2_03.as_posix()
    section_map = root / P2_03 / "section_map.yaml"
    sync_map = root / P2_03 / "sync_map.yaml"
    tex = root / P2_03 / "tex" / "main.tex"
    if not tex.is_file():
        errors.append(f"{rel}: missing tex/main.tex")
        return
    if not section_map.is_file():
        errors.append(f"{rel}: missing section_map.yaml")
    if not sync_map.is_file():
        errors.append(f"{rel}: missing sync_map.yaml")
    else:
        sync_payload = load_yaml(sync_map)
        if str(sync_payload.get("sync_mode", "")).strip() == "manual_gate":
            errors.append(f"{rel}: sync_map.yaml still uses manual_gate")
        for index, item in enumerate(sync_payload.get("sync_items") or [], start=1):
            if not isinstance(item, dict):
                errors.append(f"{rel}: sync_map.yaml sync_items[{index}] is invalid")
                continue
            tex_file = str(item.get("tex_file", "")).strip()
            if not tex_file:
                errors.append(f"{rel}: sync_map.yaml sync_items[{index}] missing tex_file")
                continue
            target = root / P2_03 / tex_file
            if not target.is_file():
                errors.append(f"{rel}: sync target missing: {tex_file}")
            elif has_placeholder(target):
                errors.append(f"{rel}: sync target contains placeholder text: {tex_file}")
            if str(item.get("status", "")).strip().lower() != "done":
                errors.append(f"{rel}: sync_map.yaml sync_items[{index}] is not done")
    text = tex.read_text(encoding="utf-8", errors="ignore").lower()
    if any(marker.lower() in text for marker in PLACEHOLDER_MARKERS):
        errors.append(f"{rel}: tex/main.tex contains placeholder text")
    for token in ("abstract", "introduction", "methods", "results", "discussion", "data availability", "code availability"):
        if token not in text:
            errors.append(f"{rel}: tex/main.tex missing {token}")


def validate_citation_registry_file(root: Path, registry: Path, errors: list[str]) -> None:
    rel = registry.relative_to(root).as_posix()
    payload = load_yaml(registry)
    citations = payload.get("citations")
    if not isinstance(citations, list) or not citations:
        errors.append(f"{rel}: citations must be a non-empty list")
        return
    for index, entry in enumerate(citations, start=1):
        label = f"citation[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in (
            "citation_key",
            "claim_id",
            "claim_context",
            "source_ref",
            "source_locator",
            "support_strength",
        ):
            required_text(entry, field, rel, label, errors)
        criticality = norm_lower(entry.get("claim_criticality"))
        support_status = norm_lower(entry.get("support_status"))
        action = norm_lower(entry.get("action"))
        if criticality not in CITATION_CRITICALITIES:
            errors.append(f"{rel}: {label} has invalid claim_criticality `{criticality}`")
        if support_status not in CITATION_SUPPORT_STATUSES:
            errors.append(f"{rel}: {label} has invalid support_status `{support_status}`")
        if action not in CITATION_ACTIONS:
            errors.append(f"{rel}: {label} has invalid action `{action}`")
        checked = required_mapping(entry, "bibliographic_facts_checked", rel, label, errors)
        for fact in ("title", "authors", "year", "venue"):
            if not isinstance(checked.get(fact), bool):
                errors.append(f"{rel}: {label}.bibliographic_facts_checked.{fact} must be boolean")
        if action == "block_handoff":
            errors.append(f"{rel}: {label} action=block_handoff")
        if criticality in CORE_CITATION_CRITICALITIES and support_status in BLOCKING_CITATION_SUPPORT_STATUSES:
            errors.append(
                f"{rel}: {label} blocks submission because {criticality} citation support_status={support_status}"
            )


def validate_citation_truth(root: Path, errors: list[str]) -> None:
    registries = sorted((root / "research").glob("**/artifacts/citation_registry.yaml"))
    if not registries:
        errors.append("submission gate missing artifacts/citation_registry.yaml")
        return
    for registry in registries:
        validate_citation_registry_file(root, registry, errors)


def validate_figure_manifest_file(root: Path, manifest: Path, errors: list[str]) -> None:
    rel = manifest.relative_to(root).as_posix()
    payload = load_yaml(manifest)
    figures = payload.get("figures")
    if not isinstance(figures, list) or not figures:
        errors.append(f"{rel}: figures must be a non-empty list")
        return
    for index, entry in enumerate(figures, start=1):
        label = f"figure[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in ("figure_id", "claim_ref", "evidence_ref", "first_callout_location"):
            required_text(entry, field, rel, label, errors)
        source_kind = norm_lower(entry.get("source_kind"))
        necessity = norm_lower(entry.get("necessity"))
        status = norm_lower(entry.get("status"))
        if source_kind not in FIGURE_SOURCE_KINDS:
            errors.append(f"{rel}: {label} has invalid source_kind `{source_kind}`")
        if necessity not in FIGURE_NECESSITIES:
            errors.append(f"{rel}: {label} has invalid necessity `{necessity}`")
        if status not in FIGURE_STATUSES:
            errors.append(f"{rel}: {label} has invalid status `{status}`")
        if status == "draft":
            errors.append(f"{rel}: {label} is still draft")
        if norm_lower(entry.get("locked_by_node_status")) != "done":
            errors.append(f"{rel}: {label}.locked_by_node_status must be done")
        source_path = required_text(entry, "source_path", rel, label, errors)
        output_path = required_text(entry, "output_path", rel, label, errors)
        if source_path and not artifact_path_exists(root, manifest, source_path):
            errors.append(f"{rel}: {label} source_path missing: {source_path}")
        if output_path and not artifact_path_exists(root, manifest, output_path):
            errors.append(f"{rel}: {label} output_path missing: {output_path}")
        checks = required_mapping(entry, "quality_checks", rel, label, errors)
        for check in FIGURE_QUALITY_CHECKS:
            if checks.get(check) is not True:
                errors.append(f"{rel}: {label}.quality_checks.{check} must be true")


def submission_bundle_role_paths(root: Path, role: str) -> list[Path]:
    manifest = root / P4_07 / "artifacts" / "resubmission_bundle_manifest.yaml"
    if not manifest.is_file():
        return []
    payload = load_yaml(manifest)
    assets = payload.get("assets")
    if not isinstance(assets, list):
        return []
    out: list[Path] = []
    for item in assets:
        if isinstance(item, dict) and norm_lower(item.get("role")) == role and item.get("path"):
            out.append(root / str(item["path"]))
    return out


def validate_figure_truth(root: Path, errors: list[str]) -> None:
    manifests: set[Path] = set()
    for node in FIGURE_MANIFEST_NODES:
        manifest = root / node / "artifacts" / "figure_manifest.yaml"
        if (root / node / "status.yaml").is_file() and not manifest.is_file():
            errors.append(f"{node.as_posix()}: missing artifacts/figure_manifest.yaml")
        elif manifest.is_file():
            manifests.add(manifest)
    for manifest in submission_bundle_role_paths(root, "figure_manifest"):
        if manifest.is_file():
            manifests.add(manifest)
    if not manifests:
        errors.append("submission gate missing artifacts/figure_manifest.yaml")
        return
    for manifest in sorted(manifests):
        validate_figure_manifest_file(root, manifest, errors)


def validate_venue_requirements_file(root: Path, venue: Path, errors: list[str]) -> None:
    rel = venue.relative_to(root).as_posix()
    payload = load_yaml(venue)
    selected = {norm_lower(item) for item in list_payload(payload.get("selected_profiles"))}
    if not selected:
        errors.append(f"{rel}: selected_profiles must be non-empty")
    invalid_profiles = selected - VENUE_PROFILES
    if invalid_profiles:
        errors.append(f"{rel}: invalid selected_profiles {sorted(invalid_profiles)}")
    gate_stage = norm_lower(payload.get("active_gate_stage"))
    if gate_stage not in VENUE_GATE_STAGES:
        errors.append(f"{rel}: active_gate_stage must be one of {sorted(VENUE_GATE_STAGES)}")
    decision = norm_lower(payload.get("venue_fit_decision"))
    if decision not in VENUE_FIT_DECISIONS:
        errors.append(f"{rel}: venue_fit_decision must be one of {sorted(VENUE_FIT_DECISIONS)}")
    elif decision != "venue_gate_passed":
        errors.append(f"{rel}: venue_fit_decision must be venue_gate_passed for submission")
    if "ready" in decision and decision != "venue_gate_passed":
        errors.append(f"{rel}: venue_fit_decision must not claim venue acceptance readiness")
    contradictions = payload.get("contradiction_list")
    if not isinstance(contradictions, list):
        errors.append(f"{rel}: contradiction_list must be a list")
    evidence_gaps = payload.get("evidence_gaps")
    if not isinstance(evidence_gaps, list):
        errors.append(f"{rel}: evidence_gaps must be a list")
    blockers = payload.get("submission_blockers")
    if not isinstance(blockers, list):
        errors.append(f"{rel}: submission_blockers must be a list")
    elif blockers:
        errors.append(f"{rel}: submission_blockers must be empty for submission_gate_passed")
    scope_fit = payload.get("scope_fit")
    if not isinstance(scope_fit, dict):
        errors.append(f"{rel}: scope_fit must be a mapping")
        scope_fit = {}
    nature = scope_fit.get("nature_article") if isinstance(scope_fit.get("nature_article"), dict) else {}
    if "nature_article" in selected:
        for field in ("originality", "outstanding_importance", "interdisciplinary_interest", "broad_readership", "broader_context"):
            if nature.get(field) is not True:
                errors.append(f"{rel}: scope_fit.nature_article.{field} must be true")
    tpami = scope_fit.get("ieee_tpami") if isinstance(scope_fit.get("ieee_tpami"), dict) else {}
    if "ieee_tpami" in selected:
        for field in (
            "computer_vision",
            "pattern_analysis_or_recognition",
            "selected_machine_intelligence",
            "machine_learning_for_pattern_analysis",
        ):
            if tpami.get(field) is not True:
                errors.append(f"{rel}: scope_fit.ieee_tpami.{field} must be true")
    if "nature_article" in selected:
        summary = payload.get("summary_paragraph_requirements")
        if not isinstance(summary, dict):
            errors.append(f"{rel}: summary_paragraph_requirements must be a mapping")
        else:
            if not isinstance(summary.get("max_words"), int) or int(summary.get("max_words")) > 200:
                errors.append(f"{rel}: summary_paragraph_requirements.max_words must be an integer <= 200")
            for field in ("background", "rationale", "main_conclusion", "broader_context", "broad_reader_language"):
                if summary.get(field) is not True:
                    errors.append(f"{rel}: summary_paragraph_requirements.{field} must be true")


def validate_venue_truth(root: Path, errors: list[str]) -> None:
    venue = root / P2_01 / "artifacts" / "venue_requirements.yaml"
    if not venue.is_file():
        errors.append(f"{P2_01.as_posix()}: missing artifacts/venue_requirements.yaml")
        return
    validate_venue_requirements_file(root, venue, errors)

    report = root / P2_04 / "artifacts" / "formal_check_report.md"
    if (root / P2_04 / "status.yaml").is_file():
        if not report.is_file():
            errors.append(f"{P2_04.as_posix()}: missing artifacts/formal_check_report.md")
        else:
            text = report.read_text(encoding="utf-8", errors="ignore").lower()
            for token in ("venue_requirements.yaml", "contradiction", "evidence gap"):
                if token not in text:
                    errors.append(f"{P2_04.as_posix()}: formal_check_report.md missing {token}")


def manifest_asset_paths(payload: dict[str, Any]) -> list[str]:
    assets = payload.get("assets")
    if not isinstance(assets, list):
        return []
    paths: list[str] = []
    for item in assets:
        if isinstance(item, str):
            paths.append(item)
        elif isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.append(item["path"])
    return paths


def validate_submission_bundle(root: Path, errors: list[str]) -> None:
    rel = P4_07.as_posix()
    manifest = root / P4_07 / "artifacts" / "resubmission_bundle_manifest.yaml"
    if not manifest.is_file():
        errors.append(f"{rel}: missing artifacts/resubmission_bundle_manifest.yaml")
        return
    payload = load_yaml(manifest)
    paths = manifest_asset_paths(payload)
    if not paths:
        errors.append(f"{rel}: resubmission bundle manifest has no assets")
        return
    roles = set()
    role_counts: dict[str, int] = {}
    assets = payload.get("assets")
    if isinstance(assets, list):
        for item in assets:
            if isinstance(item, dict) and isinstance(item.get("role"), str):
                role = item["role"].strip().lower()
                roles.add(role)
                role_counts[role] = role_counts.get(role, 0) + 1
    text = manifest.read_text(encoding="utf-8", errors="ignore").lower()
    for marker in (
        "manuscript",
        "response",
        "evidence",
        "figures",
        "tables",
        "metadata",
        "citation_registry",
        "figure_manifest",
        "venue_requirements",
        "question_mapping_matrix",
        "coverage_check_report",
        "revision_evidence_map",
    ):
        if marker not in text:
            errors.append(f"{rel}: manifest missing {marker} asset marker")
        if marker not in roles:
            errors.append(f"{rel}: manifest missing asset role `{marker}`")
        elif role_counts.get(marker, 0) > 1:
            errors.append(f"{rel}: manifest has duplicate asset role `{marker}`")
    for asset_path in paths:
        if not (root / asset_path).is_file():
            errors.append(f"{rel}: manifest asset missing: {asset_path}")


def validate_literature_gap_map_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    gaps = entries_for(payload, ("gaps", "literature_gaps"))
    if not gaps:
        errors.append(f"{rel}: gaps must be a non-empty list")
        return
    for index, entry in enumerate(gaps, start=1):
        label = f"gap[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in ("gap_id", "gap_statement", "novelty_boundary", "falsifiable_question", "action"):
            required_text(entry, field, rel, label, errors)
        if not list_payload(entry.get("nearest_prior_work")):
            errors.append(f"{rel}: {label}.nearest_prior_work must be a non-empty list")
        if not list_payload(entry.get("citation_refs")):
            errors.append(f"{rel}: {label}.citation_refs must be a non-empty list")
        evidence_status = norm_lower(entry.get("evidence_status"))
        if evidence_status not in GAP_EVIDENCE_STATUSES:
            errors.append(f"{rel}: {label} has invalid evidence_status `{evidence_status}`")
        elif evidence_status in {"pending", "contradicted"}:
            errors.append(f"{rel}: {label} blocks submission because evidence_status={evidence_status}")
        if norm_lower(entry.get("action")) == "block_handoff":
            errors.append(f"{rel}: {label} action=block_handoff")


def validate_literature_gap_truth(root: Path, errors: list[str]) -> None:
    path = root / P0_01 / "artifacts" / "literature_gap_map.yaml"
    if not path.is_file():
        errors.append(f"{P0_01.as_posix()}: missing artifacts/literature_gap_map.yaml")
        return
    validate_literature_gap_map_file(root, path, errors)


def validate_claim_evidence_registry_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    claims = entries_for(payload, ("claims", "claim_evidence", "claim_evidence_registry"))
    if not claims:
        errors.append(f"{rel}: claims must be a non-empty list")
        return
    for index, entry in enumerate(claims, start=1):
        label = f"claim[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in ("claim_id", "claim_type", "claim_text", "support_status", "manuscript_location", "action"):
            required_text(entry, field, rel, label, errors)
        claim_type = norm_lower(entry.get("claim_type"))
        support_status = norm_lower(entry.get("support_status"))
        action = norm_lower(entry.get("action"))
        if claim_type not in CLAIM_TYPES:
            errors.append(f"{rel}: {label} has invalid claim_type `{claim_type}`")
        if support_status not in CLAIM_SUPPORT_STATUSES:
            errors.append(f"{rel}: {label} has invalid support_status `{support_status}`")
        if action not in CLAIM_ACTIONS:
            errors.append(f"{rel}: {label} has invalid action `{action}`")
        evidence_refs = list_payload(entry.get("evidence_refs"))
        if claim_type in BLOCKING_CLAIM_TYPES and not evidence_refs:
            errors.append(f"{rel}: {label} blocks submission because critical claim has no evidence_refs")
        for ref_index, ref in enumerate(evidence_refs, start=1):
            ref_label = f"{label}.evidence_refs[{ref_index}]"
            if not isinstance(ref, dict):
                errors.append(f"{rel}: {ref_label} is not a mapping")
                continue
            for field in ("evidence_id", "evidence_type", "source_ref"):
                required_text(ref, field, rel, ref_label, errors)
            evidence_type = norm_lower(ref.get("evidence_type"))
            if evidence_type not in EVIDENCE_TYPES:
                errors.append(f"{rel}: {ref_label} has invalid evidence_type `{evidence_type}`")
        if action == "block_handoff":
            errors.append(f"{rel}: {label} action=block_handoff")
        if claim_type in BLOCKING_CLAIM_TYPES and support_status in BLOCKING_CLAIM_SUPPORT_STATUSES:
            errors.append(
                f"{rel}: {label} blocks submission because {claim_type} support_status={support_status}"
            )
        if claim_type in BLOCKING_CLAIM_TYPES and support_status == "not_applicable":
            errors.append(f"{rel}: {label} critical claim cannot use support_status=not_applicable")


def validate_claim_evidence_truth(root: Path, errors: list[str]) -> None:
    required = root / P2_03 / "artifacts" / "claim_evidence_registry.yaml"
    if not required.is_file():
        errors.append(f"{P2_03.as_posix()}: missing artifacts/claim_evidence_registry.yaml")
    registries = set((root / "research").glob("**/artifacts/claim_evidence_registry.yaml"))
    if required.is_file():
        registries.add(required)
    for registry in sorted(registries):
        validate_claim_evidence_registry_file(root, registry, errors)


def validate_failure_register_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    if not has_list_field(payload, ("failures", "failure_register")):
        errors.append(f"{rel}: failures must be a list")
        return
    failures = entries_for(payload, ("failures", "failure_register"))
    for index, entry in enumerate(failures, start=1):
        label = f"failure[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in ("failure_id", "context", "affected_claim_id", "severity", "interpretation", "action", "status"):
            required_text(entry, field, rel, label, errors)
        severity = norm_lower(entry.get("severity"))
        status = norm_lower(entry.get("status"))
        action = norm_lower(entry.get("action"))
        if severity not in FAILURE_SEVERITIES:
            errors.append(f"{rel}: {label} has invalid severity `{severity}`")
        if status not in FAILURE_STATUSES:
            errors.append(f"{rel}: {label} has invalid status `{status}`")
        if action not in FAILURE_ACTIONS:
            errors.append(f"{rel}: {label} has invalid action `{action}`")
        if severity in {"medium", "high"} and status == "open":
            errors.append(f"{rel}: {label} blocks submission because {severity} failure is open")


def validate_keep_discard_ledger_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    if not has_list_field(payload, ("decisions", "items", "keep_discard")):
        errors.append(f"{rel}: decisions must be a list")
        return
    decisions = entries_for(payload, ("decisions", "items", "keep_discard"))
    for index, entry in enumerate(decisions, start=1):
        label = f"decision[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in ("item_id", "item_type", "decision", "rationale", "evidence_ref"):
            required_text(entry, field, rel, label, errors)
        decision = norm_lower(entry.get("decision"))
        if decision not in KEEP_DISCARD_DECISIONS:
            errors.append(f"{rel}: {label} has invalid decision `{decision}`")
        if decision == "defer":
            errors.append(f"{rel}: {label} blocks submission because decision=defer")


def validate_negative_result_note(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    if not path.is_file():
        errors.append(f"{P1_05.as_posix()}: missing artifacts/negative_result_note.md")
        return
    if has_placeholder(path):
        errors.append(f"{rel}: placeholder marker remains")
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    if not any(token in text for token in ("negative", "负结果", "失败")):
        errors.append(f"{rel}: missing negative-result or failure discussion")
    if not any(token in text for token in ("interpret", "解释", "limitation", "局限", "alternative")):
        errors.append(f"{rel}: missing interpretation, limitation, or alternative explanation")


def validate_failure_truth(root: Path, errors: list[str]) -> None:
    failure = root / P1_05 / "artifacts" / "failure_register.yaml"
    if not failure.is_file():
        errors.append(f"{P1_05.as_posix()}: missing artifacts/failure_register.yaml")
    else:
        validate_failure_register_file(root, failure, errors)
    validate_negative_result_note(root, root / P1_05 / "artifacts" / "negative_result_note.md", errors)
    ledger = root / P1_05 / "artifacts" / "keep_discard_ledger.yaml"
    if not ledger.is_file():
        errors.append(f"{P1_05.as_posix()}: missing artifacts/keep_discard_ledger.yaml")
    else:
        validate_keep_discard_ledger_file(root, ledger, errors)


def validate_question_mapping_matrix_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    mappings = entries_for(payload, ("mappings", "matrix"))
    if not mappings:
        errors.append(f"{rel}: mappings must be a non-empty list")
        return
    for index, entry in enumerate(mappings, start=1):
        label = f"mapping[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        required_one_of_text(entry, ("critique_id", "comment_id", "issue_id"), rel, label, errors)
        for field in ("response_item_id", "claim_id", "evidence_id", "location", "response_strategy", "status"):
            required_text(entry, field, rel, label, errors)
        status = norm_lower(entry.get("status"))
        if status not in MAPPING_STATUSES:
            errors.append(f"{rel}: {label} has invalid status `{status}`")
        elif status in {"uncovered", "pending"}:
            errors.append(f"{rel}: {label} blocks submission because status={status}")


def validate_coverage_check_report_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    coverage = entries_for(payload, ("coverage", "items"))
    if not coverage:
        errors.append(f"{rel}: coverage must be a non-empty list")
        return
    for index, entry in enumerate(coverage, start=1):
        label = f"coverage[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        required_one_of_text(entry, ("critique_id", "comment_id", "issue_id"), rel, label, errors)
        for field in (
            "response_item_id",
            "claim_id",
            "evidence_id",
            "manuscript_location",
            "actionable_fix",
            "severity",
            "coverage_status",
        ):
            required_text(entry, field, rel, label, errors)
        severity = norm_lower(entry.get("severity"))
        if severity not in FAILURE_SEVERITIES:
            errors.append(f"{rel}: {label} has invalid severity `{severity}`")
        coverage_status = norm_lower(entry.get("coverage_status"))
        if coverage_status not in COVERAGE_STATUSES:
            errors.append(f"{rel}: {label} has invalid coverage_status `{coverage_status}`")
        elif coverage_status != "covered":
            errors.append(f"{rel}: {label} blocks submission because coverage_status={coverage_status}")


def validate_revision_evidence_map_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    revisions = entries_for(payload, ("revisions", "evidences"))
    if not revisions:
        errors.append(f"{rel}: revisions must be a non-empty list")
        return
    for index, entry in enumerate(revisions, start=1):
        label = f"revision[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        required_one_of_text(entry, ("critique_id", "comment_id", "issue_id"), rel, label, errors)
        for field in ("evidence_id", "response_item_id", "claim_id", "evidence_kind", "manuscript_location", "status"):
            required_text(entry, field, rel, label, errors)
        if not list_payload(entry.get("modified_nodes")):
            errors.append(f"{rel}: {label}.modified_nodes must be a non-empty list")
        has_diff = bool(norm(entry.get("revision_diff_ref"))) or bool(list_payload(entry.get("artifact_refs")))
        if not has_diff:
            errors.append(f"{rel}: {label} missing revision_diff_ref or artifact_refs")
        status = norm_lower(entry.get("status"))
        if status not in REVISION_STATUSES:
            errors.append(f"{rel}: {label} has invalid status `{status}`")
        elif status not in {"applied", "verified"}:
            errors.append(f"{rel}: {label} blocks submission because status={status}")


def validate_response_artifact_truth(root: Path, errors: list[str]) -> None:
    artifacts = (
        (P4_02, "question_mapping_matrix.yaml", validate_question_mapping_matrix_file),
        (P4_05, "coverage_check_report.yaml", validate_coverage_check_report_file),
        (P4_06, "revision_evidence_map.yaml", validate_revision_evidence_map_file),
    )
    for node, filename, validator in artifacts:
        path = root / node / "artifacts" / filename
        if not path.is_file():
            errors.append(f"{node.as_posix()}: missing artifacts/{filename}")
            continue
        validator(root, path, errors)


def validate_revision_action_map_file(root: Path, path: Path, errors: list[str]) -> None:
    rel = path.relative_to(root).as_posix()
    payload = load_yaml(path)
    actions = entries_for(payload, ("actions", "revision_actions"))
    if not actions:
        errors.append(f"{rel}: actions must be a non-empty list")
        return
    for index, entry in enumerate(actions, start=1):
        label = f"action[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{rel}: {label} is not a mapping")
            continue
        for field in (
            "action_id",
            "issue_id",
            "claim_id",
            "evidence_id",
            "target_path",
            "target_location",
            "actionable_fix",
            "verification",
            "status",
        ):
            required_text(entry, field, rel, label, errors)
        status = norm_lower(entry.get("status"))
        if status not in {"planned", "done", "blocked"}:
            errors.append(f"{rel}: {label} has invalid status `{status}`")
        elif status != "done":
            errors.append(f"{rel}: {label} blocks submission because status={status}")


def validate_review_action_truth(root: Path, errors: list[str]) -> None:
    path = root / P3_04 / "artifacts" / "revision_action_map.yaml"
    if not path.is_file():
        errors.append(f"{P3_04.as_posix()}: missing artifacts/revision_action_map.yaml")
        return
    validate_revision_action_map_file(root, path, errors)


def validate_cross_node_consistency(root: Path, errors: list[str]) -> None:
    p1_claim_map = load_yaml_if_present(root / P1_08 / "artifacts" / "claim_map.yaml")
    p1_figure_manifest = load_yaml_if_present(root / P1_09 / "artifacts" / "figure_manifest.yaml")
    if p1_claim_map and p1_figure_manifest:
        claim_ids = collect_values(p1_claim_map, {"claim_id", "claim_ref"})
        figure_claim_refs = collect_values(p1_figure_manifest, {"claim_ref"})
        missing = sorted(ref for ref in figure_claim_refs if ref and ref not in claim_ids)
        for ref in missing:
            errors.append(f"{P1_09.as_posix()}: figure_manifest claim_ref `{ref}` is absent from P1_08 claim_map")

    p4_mapping = load_yaml_if_present(root / P4_02 / "artifacts" / "question_mapping_matrix.yaml")
    p4_coverage = load_yaml_if_present(root / P4_05 / "artifacts" / "coverage_check_report.yaml")
    if p4_mapping and p4_coverage:
        mapped_ids = collect_values(p4_mapping, {"critique_id", "comment_id", "issue_id"})
        covered_ids = collect_values(p4_coverage, {"critique_id", "comment_id", "issue_id"})
        missing = sorted(item for item in mapped_ids if item and item not in covered_ids)
        for item in missing:
            errors.append(f"{P4_05.as_posix()}: coverage report missing mapped critique/comment `{item}`")

    p3_actions = load_yaml_if_present(root / P3_04 / "artifacts" / "revision_action_map.yaml")
    p4_evidence = load_yaml_if_present(root / P4_06 / "artifacts" / "revision_evidence_map.yaml")
    if p3_actions and p4_evidence:
        action_ids = collect_values(p3_actions, {"comment_id", "issue_id", "critique_id"})
        evidence_ids = collect_values(p4_evidence, {"comment_id", "issue_id", "critique_id"})
        missing = sorted(item for item in action_ids if item and item not in evidence_ids)
        for item in missing:
            errors.append(f"{P4_06.as_posix()}: revision evidence map missing P3 action `{item}`")


def validate_node(root: Path, node: Path, require_submission: bool, min_score: float, errors: list[str]) -> None:
    rel = node.relative_to(root).as_posix()
    status_payload = load_yaml(node / "status.yaml")
    stage = node_stage(status_payload)
    if not stage:
        errors.append(f"{rel}: missing status/lifecycle.stage")
        return
    needs_done = require_submission or stage in DONE_STATUSES
    if require_submission and stage not in DONE_STATUSES:
        errors.append(f"{rel}: stage is not done/archive for submission readiness")
    if not needs_done:
        return
    author_agent_id = validate_author_identity(rel, status_payload, errors)
    validate_checklist(node, rel, errors)
    validate_review(node, rel, min_score, author_agent_id, errors)
    validate_no_placeholders(node, rel, errors)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    errors: list[str] = []
    nodes = node_dirs(root)
    if not nodes:
        errors.append("research tree has no schedulable nodes")

    for node in nodes:
        validate_node(root, node, args.require_submission, args.min_review_score, errors)

    if args.require_submission:
        for critical in (P0_01, P1_04, P1_05, P1_09, P2_01, P2_02_03, P2_03, P2_04, P3_04, P4_02, P4_05, P4_06, P4_07):
            if not (root / critical / "status.yaml").is_file():
                errors.append(f"{critical.as_posix()}: critical submission node is missing")
        validate_literature_gap_truth(root, errors)
        validate_execution_node(root, errors)
        validate_result_synthesis(root, errors)
        validate_failure_truth(root, errors)
        validate_claim_evidence_truth(root, errors)
        validate_citation_truth(root, errors)
        validate_figure_truth(root, errors)
        validate_venue_truth(root, errors)
        validate_review_action_truth(root, errors)
        validate_response_artifact_truth(root, errors)
        validate_tex_submission(root, errors)
        validate_submission_bundle(root, errors)
        validate_cross_node_consistency(root, errors)

    if errors:
        print("research truth: fail")
        for error in errors:
            print(f"- {error}")
        return 1

    mode = "submission-ready" if args.require_submission else "consistent"
    print(f"research truth: pass mode={mode} nodes={len(nodes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
