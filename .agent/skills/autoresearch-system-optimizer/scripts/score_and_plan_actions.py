#!/usr/bin/env python3
"""Convert structured validation payloads into dual-lane scorecards and ranked actions."""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from summarize_validation_results import collect_all_results


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
CONFIG_DIR = SKILL_DIR / "config"
DEFAULT_MATRIX = CONFIG_DIR / "score_matrix.yaml"
DEFAULT_POLICY = CONFIG_DIR / "score_policy.yaml"
DEFAULT_TEMPLATE = CONFIG_DIR / "scorecard.template.yaml"
DEFAULT_RESEARCH_GATE = CONFIG_DIR / "research_gate_rules.yaml"
DEFAULT_IMMUTABLE = CONFIG_DIR / "immutable_core_rules.yaml"
PATH_RE = re.compile(r"(\.agent/[\w./-]+|_reference/[\w./-]+|backend/[\w./-]+|research/[\w./\u4e00-\u9fff-]+|test/[\w./-]+)")


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def matches_any(rel_path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_path, pattern) for pattern in patterns)


def first_candidate_path(*surfaces: Any) -> str | None:
    for surface in surfaces:
        if isinstance(surface, str):
            match = PATH_RE.search(surface)
            if match:
                return match.group(1)
        elif isinstance(surface, list):
            for item in surface:
                candidate = first_candidate_path(item)
                if candidate:
                    return candidate
    return None


def ensure_list_of_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    output: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            output.append(item.strip())
    return output


def finding_key(finding: dict[str, Any]) -> tuple[str, str]:
    root = str(finding.get("root_cause_id") or "").strip()
    surface = str(finding.get("fix_surface") or "").strip()
    fallback = str(finding.get("finding_id") or finding.get("summary") or finding.get("claim_or_surface") or "unknown").strip()
    if root:
        return root, ""
    if surface:
        return "", surface
    return fallback or "unknown", ""


def load_teammate_consensus(results_dir: Path) -> dict[str, Any]:
    path = results_dir / "teammate_consensus.yaml"
    return load_yaml(path) if path.exists() else {}


def consensus_index(consensus: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    rows = consensus.get("majority_findings") if isinstance(consensus.get("majority_findings"), list) else []
    output: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        root = str(row.get("root_cause_id") or "").strip()
        surface = str(row.get("fix_surface") or "").strip()
        surfaces = ensure_list_of_strings(row.get("fix_surfaces"))
        if surface:
            surfaces.append(surface)
        if root:
            output[(root, "")] = row
        for item in sorted(set(surfaces)):
            output[("", item)] = row
            if root:
                output[(root, item)] = row
    return output


def consensus_required(consensus: dict[str, Any]) -> bool:
    meta = consensus.get("meta") if isinstance(consensus.get("meta"), dict) else {}
    return bool(meta.get("enabled", False))


def consensus_auto_apply_gate_passed(consensus: dict[str, Any]) -> bool:
    if not consensus_required(consensus):
        return True
    gate = consensus.get("auto_apply_gate") if isinstance(consensus.get("auto_apply_gate"), dict) else {}
    return bool(gate.get("majority_passed", False))


def deep_copy_dict(payload: dict[str, Any]) -> dict[str, Any]:
    return yaml.safe_load(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))


def normalize_phase(result: dict[str, Any]) -> str | None:
    phase = result.get("phase")
    if isinstance(phase, str) and phase:
        return phase
    target = str(result.get("target_node") or "")
    match = re.search(r"/(P[0-4])_", target)
    return match.group(1) if match else None


def normalize_mode(value: Any, default: str | None = None) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def select_dimensions(score_matrix: dict[str, Any], lane: str, *, phase: str | None, node_mode: str | None, node_profile: str | None, execution_profile: str | None) -> list[dict[str, str]]:
    lane_matrix = score_matrix.get(lane) if isinstance(score_matrix.get(lane), dict) else {}
    selected: list[dict[str, str]] = []
    seen: set[str] = set()

    def append(category: str, values: list[str]) -> None:
        for dimension_id in values:
            if dimension_id not in seen:
                selected.append({"category": category, "dimension_id": dimension_id})
                seen.add(dimension_id)

    append("common", ensure_list_of_strings(lane_matrix.get("common")))
    if phase:
        phase_map = lane_matrix.get("phase") if isinstance(lane_matrix.get("phase"), dict) else {}
        append("phase", ensure_list_of_strings(phase_map.get(phase)))
    if node_mode:
        mode_map = lane_matrix.get("node_mode") if isinstance(lane_matrix.get("node_mode"), dict) else {}
        append("node_mode", ensure_list_of_strings(mode_map.get(node_mode)))
    if node_profile:
        profile_map = lane_matrix.get("node_profile") if isinstance(lane_matrix.get("node_profile"), dict) else {}
        append("node_profile", ensure_list_of_strings(profile_map.get(node_profile)))
    if execution_profile:
        exec_map = lane_matrix.get("execution_profile") if isinstance(lane_matrix.get("execution_profile"), dict) else {}
        append("execution_profile", ensure_list_of_strings(exec_map.get(execution_profile)))
    return selected


def score_value(observed_status: str, severity: str, confidence: str, weight: float, policy: dict[str, Any]) -> tuple[float, float]:
    max_dimension = float(policy.get("score_ranges", {}).get("max_dimension_score", 10.0))
    status_weight = float(policy.get("status_weights", {}).get(observed_status, 0.0))
    severity_penalty = float(policy.get("severity_penalties", {}).get(severity, 0.2))
    confidence_multiplier = float(policy.get("confidence_multiplier", {}).get(confidence, 0.6))
    raw_score = max_dimension * weight * status_weight * max(0.0, 1.0 - severity_penalty) * confidence_multiplier
    max_possible = max_dimension * weight
    return raw_score, max_possible


def normalize_input_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {
        "dimension_id": str(row.get("dimension_id") or "").strip(),
        "observed_status": str(row.get("observed_status") or "missing").strip() or "missing",
        "severity": str(row.get("severity") or "medium").strip() or "medium",
        "confidence": str(row.get("confidence") or "unknown").strip() or "unknown",
        "evidence_paths": ensure_list_of_strings(row.get("evidence_paths")),
        "auto_apply_candidate": bool(row.get("auto_apply_candidate", False)),
    }
    for key in ("evidence_strength", "recheckability", "blast_radius", "score_stability_note", "delta_reason"):
        value = row.get(key)
        normalized[key] = str(value).strip() if isinstance(value, str) and value.strip() else None
    return normalized


def score_stability_block(result: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    policy_cfg = policy.get("score_stability") if isinstance(policy.get("score_stability"), dict) else {}
    structured = result.get("structured_payload") if isinstance(result.get("structured_payload"), dict) else {}
    explicit = structured.get("score_stability") if isinstance(structured.get("score_stability"), dict) else {}

    status = str(explicit.get("status") or policy_cfg.get("default_status") or "not_compared")
    evidence_delta = ensure_list_of_strings(explicit.get("evidence_delta"))
    variance_reason = str(explicit.get("variance_reason") or "").strip() or None
    prior_score_ref = explicit.get("prior_score_ref")
    require_delta = bool(policy_cfg.get("require_evidence_delta_for_score_change", True))

    node_score_stable = explicit.get("node_score_stable")
    if not isinstance(node_score_stable, bool):
        node_score_stable = status not in {"unstable", "unstable_missing_evidence_delta"}
    if status == "changed" and require_delta and not evidence_delta:
        status = "unstable_missing_evidence_delta"
        node_score_stable = False

    return {
        "status": status,
        "node_score_stable": node_score_stable,
        "prior_score_ref": prior_score_ref,
        "evidence_delta": evidence_delta,
        "variance_reason": variance_reason,
    }


def result_score_stable(result: dict[str, Any], policy: dict[str, Any] | None = None) -> bool:
    structured = result.get("structured_payload") if isinstance(result.get("structured_payload"), dict) else {}
    explicit = structured.get("score_stability") if isinstance(structured.get("score_stability"), dict) else {}
    if explicit.get("node_score_stable") is False:
        return False
    status = str(explicit.get("status") or "")
    if status in {"unstable", "unstable_missing_evidence_delta"}:
        return False
    if status == "changed" and policy is not None:
        policy_cfg = policy.get("score_stability") if isinstance(policy.get("score_stability"), dict) else {}
        if bool(policy_cfg.get("require_evidence_delta_for_score_change", True)) and not ensure_list_of_strings(explicit.get("evidence_delta")):
            return False
    return True


def build_scorecard(
    template: dict[str, Any],
    result: dict[str, Any],
    *,
    lane: str,
    selected_dimensions: list[dict[str, str]],
    input_map: dict[str, dict[str, Any]],
    policy: dict[str, Any],
    exploratory: bool,
) -> dict[str, Any]:
    scorecard = deep_copy_dict(template)
    scorecard["node_path"] = result.get("target_node")
    scorecard["phase"] = normalize_phase(result)
    scorecard["node_mode"] = normalize_mode(result.get("node_mode"))
    scorecard["node_profile"] = normalize_mode(result.get("node_profile"))
    scorecard["execution_profile"] = normalize_mode(result.get("execution_profile"))
    scorecard["lane"] = lane
    scorecard["boundary_class"] = result.get("boundary_class", "maintenance_only")
    scorecard["exploratory"] = exploratory
    scorecard["selected_dimensions"] = [item["dimension_id"] for item in selected_dimensions]
    scorecard["score_stability"] = score_stability_block(result, policy)

    if not input_map:
        scorecard["score_status"] = "missing_structured_input"
        scorecard["summary"] = {
            "counted_dimensions": 0,
            "missing_dimensions": [item["dimension_id"] for item in selected_dimensions],
            "evidence_files": [],
            "advisory_only": lane == "research_rigor",
        }
        scorecard["review_notes"] = ["Structured score_inputs were missing; planner downgraded to manual handling."]
        scorecard["next_action"] = "Emit a manual ticket and require the evaluator to provide structured score_inputs."
        return scorecard

    if lane == "research_rigor" and exploratory:
        scorecard["score_status"] = "unscored_exploratory"
        scorecard["summary"] = {
            "counted_dimensions": 0,
            "missing_dimensions": [item["dimension_id"] for item in selected_dimensions],
            "evidence_files": sorted({path for row in input_map.values() for path in row.get("evidence_paths", [])}),
            "advisory_only": True,
        }
        scorecard["review_notes"] = ["Exploratory boundary: maintenance lane is scored, research-rigor lane is advisory only."]
        scorecard["next_action"] = "Open a human gate ticket instead of forcing a numeric research-rigor score."
        return scorecard

    weight_policy = policy.get("category_weights", {}).get(lane, {})
    total_score = 0.0
    total_possible = 0.0
    dimension_scores: list[dict[str, Any]] = []
    evidence_files: set[str] = set()
    missing_dimensions: list[str] = []
    min_percent = 100.0

    for item in selected_dimensions:
        dimension_id = item["dimension_id"]
        category = item["category"]
        row = input_map.get(dimension_id)
        if row is None:
            row = {
                "dimension_id": dimension_id,
                "observed_status": "missing",
                "severity": "high",
                "confidence": "unknown",
                "evidence_paths": [],
                "auto_apply_candidate": False,
            }
            missing_dimensions.append(dimension_id)
        weight = float(weight_policy.get(category, 1.0))
        raw_score, max_possible = score_value(row["observed_status"], row["severity"], row["confidence"], weight, policy)
        total_score += raw_score
        total_possible += max_possible
        percent = 100.0 * raw_score / max_possible if max_possible else 0.0
        min_percent = min(min_percent, percent)
        evidence_files.update(row.get("evidence_paths", []))
        dimension_scores.append(
            {
                "dimension_id": dimension_id,
                "category": category,
                "observed_status": row["observed_status"],
                "severity": row["severity"],
                "confidence": row["confidence"],
                "evidence_paths": row.get("evidence_paths", []),
                "auto_apply_candidate": bool(row.get("auto_apply_candidate", False)),
                "evidence_strength": row.get("evidence_strength"),
                "recheckability": row.get("recheckability"),
                "blast_radius": row.get("blast_radius"),
                "score_stability_note": row.get("score_stability_note"),
                "delta_reason": row.get("delta_reason"),
                "raw_score": round(raw_score, 3),
                "max_score": round(max_possible, 3),
                "score_percent": round(percent, 2),
            }
        )

    normalized_total = round((100.0 * total_score / total_possible) if total_possible else 0.0, 2)
    scorecard["score_status"] = "scored"
    scorecard["total_score"] = normalized_total
    scorecard["dimension_scores"] = dimension_scores
    scorecard["summary"] = {
        "counted_dimensions": len(selected_dimensions),
        "missing_dimensions": missing_dimensions,
        "evidence_files": sorted(evidence_files),
        "advisory_only": lane == "research_rigor",
        "min_dimension_percent": round(min_percent if dimension_scores else 0.0, 2),
        "score_stability_status": scorecard["score_stability"]["status"],
    }
    scorecard["review_notes"] = [
        f"Boundary class: {scorecard['boundary_class']}",
        f"Exploratory: {exploratory}",
    ]
    scorecard["next_action"] = "Rank maintenance actions and human gate tickets from the structured findings."
    return scorecard


def summarize_scores(scorecards: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [card for card in scorecards if card.get("score_status") == "scored" and isinstance(card.get("total_score"), (int, float))]
    status_counts = Counter(str(card.get("score_status") or "unknown") for card in scorecards)
    if not scored:
        return {
            "count": len(scorecards),
            "scored_count": 0,
            "status_counts": dict(status_counts),
            "average": None,
            "min": None,
            "max": None,
        }
    totals = [float(card["total_score"]) for card in scored]
    return {
        "count": len(scorecards),
        "scored_count": len(scored),
        "status_counts": dict(status_counts),
        "average": round(sum(totals) / len(totals), 2),
        "min": round(min(totals), 2),
        "max": round(max(totals), 2),
    }


def research_gate_status(result: dict[str, Any], research_card: dict[str, Any], gate_rules: dict[str, Any]) -> str:
    boundary_class = str(result.get("boundary_class") or "maintenance_only")
    if boundary_class == "exploratory" or result.get("exploratory"):
        return "exploratory"
    force = gate_rules.get("force_human_gate", {}) if isinstance(gate_rules.get("force_human_gate"), dict) else {}
    phase = normalize_phase(result)
    if phase and phase in ensure_list_of_strings(force.get("phases")):
        return "requires_human_review"
    node_profile = normalize_mode(result.get("node_profile"))
    if node_profile and node_profile in ensure_list_of_strings(force.get("node_profiles")):
        return "requires_human_review"
    if boundary_class in ensure_list_of_strings(force.get("boundary_classes")):
        return "requires_human_review"
    threshold = float(gate_rules.get("research_lane_thresholds", {}).get("low_score_requires_human_gate", 70.0))
    critical_dimension_threshold = float(gate_rules.get("research_lane_thresholds", {}).get("critical_dimension_threshold", 45.0))
    score = research_card.get("total_score")
    if isinstance(score, (int, float)) and float(score) < threshold:
        return "requires_human_review"
    minimum = research_card.get("summary", {}).get("min_dimension_percent")
    if isinstance(minimum, (int, float)) and float(minimum) < critical_dimension_threshold:
        return "requires_human_review"
    return "not_applicable"


def action_priority(severity: str) -> str:
    mapping = {"critical": "critical", "high": "high", "medium": "medium", "low": "low"}
    return mapping.get(severity, "medium")


def priority_rank(severity: str) -> int:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return order.get(severity, 0)


def confidence_rank_value(confidence: str) -> int:
    order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    return order.get(confidence, 0)


def maintenance_reason_code(
    *,
    target_path: str | None,
    immutable_hit: bool,
    auto_apply_candidate: bool,
    score_stable: bool,
    teammate_consensus_passed: bool,
    low_risk_eligible: bool,
    operation: str | None,
    payload: dict[str, Any],
    allowed: list[str],
    forbidden: list[str],
) -> str:
    if immutable_hit:
        return "immutable_path"
    if not score_stable:
        return "score_unstable"
    if not teammate_consensus_passed:
        return "teammate_no_majority"
    if target_path and matches_any(target_path, forbidden):
        return "forbidden_surface"
    if not target_path:
        return "evidence_missing"
    if not low_risk_eligible:
        return "not_low_risk"
    if auto_apply_candidate and (not operation or not payload):
        return "validator_failure"
    if target_path.startswith(".agent/skills/") or target_path.startswith("research/") or target_path.startswith("_reference/test/"):
        return "prompt_only"
    if auto_apply_candidate and not matches_any(target_path, allowed):
        return "forbidden_surface"
    return "runtime_drift"


def sort_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def disposition_rank(value: str) -> int:
        order = {"auto_apply": 4, "manual_ticket": 3, "defer": 2, "no_change": 1}
        return order.get(value, 0)

    def confidence_rank(value: str) -> int:
        order = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
        return order.get(value, 0)

    return sorted(
        actions,
        key=lambda action: (
            -disposition_rank(str(action.get("disposition") or "")),
            -priority_rank(str(action.get("severity") or "")),
            -confidence_rank(str(action.get("confidence") or "")),
            str(action.get("id") or ""),
        ),
    )


def build_maintenance_action(
    action_id: str,
    result: dict[str, Any],
    finding: dict[str, Any],
    *,
    allowed: list[str],
    forbidden: list[str],
    immutable_paths: list[str],
    policy: dict[str, Any],
    teammate_consensus: dict[str, Any],
    teammate_index: dict[tuple[str, str], dict[str, Any]],
) -> dict[str, Any]:
    fix_surface = str(finding.get("fix_surface") or "")
    evidence_files = ensure_list_of_strings(finding.get("evidence_paths"))
    target_path = first_candidate_path(fix_surface, evidence_files, result.get("target_node"))
    immutable_hit = bool(target_path and matches_any(target_path, immutable_paths))
    auto_apply_candidate = bool(finding.get("auto_apply_candidate", False))
    operation = finding.get("operation") if isinstance(finding.get("operation"), str) else None
    payload = finding.get("payload") if isinstance(finding.get("payload"), dict) else {}
    severity = str(finding.get("severity") or "medium")
    confidence = str(finding.get("confidence") or "unknown")
    score_stable = result_score_stable(result, policy)
    consensus_is_required = consensus_required(teammate_consensus)
    consensus_row = teammate_index.get(finding_key(finding))
    teammate_global_passed = consensus_auto_apply_gate_passed(teammate_consensus)
    teammate_consensus_passed = (not consensus_is_required) or (teammate_global_passed and consensus_row is not None)
    consensus_meta = teammate_consensus.get("meta") if isinstance(teammate_consensus.get("meta"), dict) else {}
    auto_policy = policy.get("auto_apply") if isinstance(policy.get("auto_apply"), dict) else {}
    minimum_confidence = str(auto_policy.get("minimum_confidence") or "medium")
    low_risk_eligible = severity == "low" and confidence_rank_value(confidence) >= confidence_rank_value(minimum_confidence)
    disposition = "manual_ticket"
    auto_apply = False

    if severity == "low" and not auto_apply_candidate:
        disposition = "no_change"
    elif low_risk_eligible and teammate_consensus_passed and score_stable and auto_apply_candidate and operation and payload and target_path and not immutable_hit and matches_any(target_path, allowed) and not matches_any(target_path, forbidden):
        disposition = "auto_apply"
        auto_apply = True

    reason_code = maintenance_reason_code(
        target_path=target_path,
        immutable_hit=immutable_hit,
        auto_apply_candidate=auto_apply_candidate,
        score_stable=score_stable,
        teammate_consensus_passed=teammate_consensus_passed,
        low_risk_eligible=low_risk_eligible,
        operation=operation,
        payload=payload,
        allowed=allowed,
        forbidden=forbidden,
    )

    return {
        "id": action_id,
        "target_label": result.get("target_node"),
        "target_path": target_path,
        "lane": "maintenance",
        "boundary_class": result.get("boundary_class", "maintenance_only"),
        "research_gate_status": "not_applicable",
        "human_gate_required": False,
        "immutable_anchor_hit": immutable_hit,
        "verdict": result.get("verdict"),
        "root_cause_id": finding.get("root_cause_id"),
        "finding_id": finding.get("finding_id"),
        "finding_summary": finding.get("summary") or finding.get("claim_or_surface"),
        "priority_class": action_priority(severity),
        "severity": severity,
        "confidence": confidence,
        "risk_level": "low" if auto_apply_candidate and low_risk_eligible else "medium",
        "disposition": disposition,
        "reason_code": reason_code,
        "score_stability_status": (result.get("structured_payload") or {}).get("score_stability", {}).get("status") if isinstance(result.get("structured_payload"), dict) else None,
        "teammate_consensus_status": "not_required" if not consensus_is_required else "majority" if consensus_row else "no_majority",
        "teammate_auto_apply_gate_passed": teammate_global_passed,
        "teammate_support_count": consensus_row.get("support_count") if consensus_row else 0,
        "teammate_majority_required": consensus_row.get("majority_required") if consensus_row else consensus_meta.get("majority_threshold"),
        "teammate_support_agents": consensus_row.get("support_agents") if consensus_row else [],
        "auto_apply": auto_apply,
        "operation": operation,
        "payload": payload,
        "expected_recheck": "derive_from_touched_paths",
        "evidence_files": evidence_files,
        "evidence_refs": evidence_files,
        "rationale": str(finding.get("manual_only_reason") or finding.get("summary") or finding.get("claim_or_surface") or "maintenance follow-up"),
    }


def build_research_action(action_id: str, result: dict[str, Any], finding: dict[str, Any], research_gate: str) -> dict[str, Any]:
    severity = str(finding.get("severity") or "medium")
    disposition = "manual_ticket" if severity in {"critical", "high", "medium"} else "defer"
    evidence_refs = ensure_list_of_strings(finding.get("evidence_paths"))
    return {
        "id": action_id,
        "target_label": result.get("target_node"),
        "target_path": first_candidate_path(finding.get("fix_surface"), finding.get("evidence_paths"), result.get("target_node")),
        "lane": "research_rigor",
        "boundary_class": result.get("boundary_class", "maintenance_only"),
        "research_gate_status": research_gate,
        "human_gate_required": research_gate != "not_applicable",
        "immutable_anchor_hit": False,
        "verdict": result.get("verdict"),
        "finding_id": finding.get("finding_id"),
        "finding_summary": finding.get("summary") or finding.get("claim_or_surface"),
        "priority_class": action_priority(severity),
        "severity": severity,
        "confidence": str(finding.get("confidence") or "unknown"),
        "risk_level": "high",
        "disposition": disposition,
        "reason_code": "manual_review" if research_gate != "not_applicable" else "evidence_missing",
        "auto_apply": False,
        "operation": None,
        "payload": {},
        "expected_recheck": "human_gate_followup",
        "evidence_files": evidence_refs,
        "evidence_refs": evidence_refs,
        "rationale": str(finding.get("manual_only_reason") or finding.get("summary") or finding.get("claim_or_surface") or "research rigor follow-up"),
    }


def build_human_gate_ticket(ticket_id: str, result: dict[str, Any], *, research_gate: str, trigger: str, evidence_files: list[str]) -> dict[str, Any]:
    return {
        "id": ticket_id,
        "target_label": result.get("target_node"),
        "boundary_class": result.get("boundary_class", "maintenance_only"),
        "research_gate_status": research_gate,
        "reason_code": "manual_review" if research_gate != "not_applicable" else "runtime_drift",
        "trigger": trigger,
        "evidence_files": evidence_files,
        "evidence_refs": evidence_files,
        "required_human_decision": "Decide whether the research-facing issue changes node truth, handoff claims, or the evaluation rubric itself.",
        "recommended_next_action": "Review the evidence bundle and either approve a manual fix path or freeze further automation on this target.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate dual-lane scorecards and optimization actions from validation results.")
    parser.add_argument("--results-dir", type=Path, required=True, help="Validation results directory.")
    parser.add_argument("--output", type=Path, required=True, help="YAML action plan output path.")
    parser.add_argument("--maintenance-scorecards-dir", type=Path, default=None, help="Directory for maintenance scorecards.")
    parser.add_argument("--research-scorecards-dir", type=Path, default=None, help="Directory for research-rigor scorecards.")
    parser.add_argument("--scorecards-dir", type=Path, default=None, help="Legacy parent directory; maintenance/ and research_rigor/ will be created under it when explicit dirs are omitted.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.results_dir.exists():
        print(f"错误: 结果目录不存在: {args.results_dir}", file=sys.stderr)
        return 1

    if args.scorecards_dir and (args.maintenance_scorecards_dir or args.research_scorecards_dir):
        print("错误: 不要同时传入 --scorecards-dir 与显式 lane 目录", file=sys.stderr)
        return 1

    if args.scorecards_dir:
        maintenance_dir = args.scorecards_dir / "maintenance"
        research_dir = args.scorecards_dir / "research_rigor"
    else:
        if args.maintenance_scorecards_dir is None or args.research_scorecards_dir is None:
            print("错误: 需要显式传入 maintenance 和 research_rigor scorecard 目录", file=sys.stderr)
            return 1
        maintenance_dir = args.maintenance_scorecards_dir
        research_dir = args.research_scorecards_dir

    maintenance_dir.mkdir(parents=True, exist_ok=True)
    research_dir.mkdir(parents=True, exist_ok=True)

    score_matrix = load_yaml(DEFAULT_MATRIX)
    score_policy = load_yaml(DEFAULT_POLICY)
    scorecard_template = load_yaml(DEFAULT_TEMPLATE)
    research_gate_rules = load_yaml(DEFAULT_RESEARCH_GATE)
    immutable_rules = load_yaml(DEFAULT_IMMUTABLE)
    optimization_policy = load_yaml(CONFIG_DIR / "optimization_loop.yaml")
    teammate_consensus = load_teammate_consensus(args.results_dir)
    teammate_majority_index = consensus_index(teammate_consensus)
    allowed = ensure_list_of_strings(optimization_policy.get("allowed_auto_apply_paths"))
    forbidden = ensure_list_of_strings(optimization_policy.get("forbidden_auto_apply_paths"))
    immutable_paths = ensure_list_of_strings(immutable_rules.get("immutable_paths"))

    all_results, _batch = collect_all_results(args.results_dir)
    actions: list[dict[str, Any]] = []
    human_gate_tickets: list[dict[str, Any]] = []
    maintenance_cards: list[dict[str, Any]] = []
    research_cards: list[dict[str, Any]] = []
    exploratory_nodes: list[str] = []
    action_counter = 1
    ticket_counter = 1

    for index, result in enumerate(all_results, start=1):
        exploratory = bool(result.get("exploratory")) or str(result.get("boundary_class") or "") == "exploratory"
        if exploratory and result.get("target_node"):
            exploratory_nodes.append(str(result["target_node"]))

        phase = normalize_phase(result)
        node_mode = normalize_mode(result.get("node_mode"), None)
        node_profile = normalize_mode(result.get("node_profile"), None)
        execution_profile = normalize_mode(result.get("execution_profile"), None)
        input_map = {}
        for raw_row in result.get("score_inputs", []):
            row = normalize_input_row(raw_row)
            if row["dimension_id"]:
                input_map[row["dimension_id"]] = row

        maintenance_dims = select_dimensions(score_matrix, "maintenance", phase=phase, node_mode=node_mode, node_profile=node_profile, execution_profile=execution_profile)
        research_dims = select_dimensions(score_matrix, "research_rigor", phase=phase, node_mode=node_mode, node_profile=node_profile, execution_profile=execution_profile)

        maintenance_card = build_scorecard(
            scorecard_template,
            result,
            lane="maintenance",
            selected_dimensions=maintenance_dims,
            input_map=input_map,
            policy=score_policy,
            exploratory=exploratory,
        )
        research_card = build_scorecard(
            scorecard_template,
            result,
            lane="research_rigor",
            selected_dimensions=research_dims,
            input_map=input_map,
            policy=score_policy,
            exploratory=exploratory,
        )
        maintenance_cards.append(maintenance_card)
        research_cards.append(research_card)

        maintenance_path = maintenance_dir / f"{index:03d}_{result['agent_name']}_maintenance.yaml"
        research_path = research_dir / f"{index:03d}_{result['agent_name']}_research.yaml"
        maintenance_path.write_text(yaml.safe_dump(maintenance_card, allow_unicode=True, sort_keys=False), encoding="utf-8")
        research_path.write_text(yaml.safe_dump(research_card, allow_unicode=True, sort_keys=False), encoding="utf-8")

        research_gate = research_gate_status(result, research_card, research_gate_rules)

        for finding in result.get("maintenance_findings", []):
            action = build_maintenance_action(
                f"action_{action_counter:03d}",
                result,
                finding,
                allowed=allowed,
                forbidden=forbidden,
                immutable_paths=immutable_paths,
                policy=score_policy,
                teammate_consensus=teammate_consensus,
                teammate_index=teammate_majority_index,
            )
            actions.append(action)
            action_counter += 1

        for finding in result.get("research_findings", []):
            action = build_research_action(f"action_{action_counter:03d}", result, finding, research_gate)
            actions.append(action)
            action_counter += 1
            human_gate_tickets.append(
                build_human_gate_ticket(
                    f"ticket_{ticket_counter:03d}",
                    result,
                    research_gate=research_gate,
                    trigger=str(finding.get("summary") or finding.get("claim_or_surface") or finding.get("finding_id") or "research gate"),
                    evidence_files=ensure_list_of_strings(finding.get("evidence_paths")),
                )
            )
            ticket_counter += 1

        if not result.get("score_inputs"):
            actions.append(
                {
                    "id": f"action_{action_counter:03d}",
                    "target_label": result.get("target_node"),
                    "target_path": None,
                    "lane": "maintenance",
                    "boundary_class": result.get("boundary_class", "maintenance_only"),
                    "research_gate_status": "not_applicable",
                    "human_gate_required": False,
                    "immutable_anchor_hit": False,
                    "verdict": result.get("verdict"),
                    "finding_id": "missing_structured_score_inputs",
                    "finding_summary": "Structured score_inputs were missing; planner cannot perform reliable automatic scoring.",
                    "priority_class": "high",
                    "severity": "high",
                    "confidence": "low",
                    "risk_level": "medium",
                    "disposition": "manual_ticket",
                    "reason_code": "validator_failure",
                    "auto_apply": False,
                    "operation": None,
                    "payload": {},
                    "expected_recheck": "re-run hostile validation with structured payload",
                    "evidence_files": [],
                    "evidence_refs": [],
                    "rationale": "Require the evaluator to emit structured score_inputs before any automatic patch planning.",
                }
            )
            action_counter += 1

        if research_gate != "not_applicable" and not result.get("research_findings"):
            human_gate_tickets.append(
                build_human_gate_ticket(
                    f"ticket_{ticket_counter:03d}",
                    result,
                    research_gate=research_gate,
                    trigger="research gate policy requires human review even without explicit research finding rows",
                    evidence_files=maintenance_card.get("summary", {}).get("evidence_files", []),
                )
            )
            ticket_counter += 1

    actions = sort_actions(actions)
    payload = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "results_dir": str(args.results_dir),
            "maintenance_scorecards_dir": str(maintenance_dir),
            "research_rigor_scorecards_dir": str(research_dir),
            "score_matrix": str(DEFAULT_MATRIX),
            "score_policy": str(DEFAULT_POLICY),
            "teammate_consensus": str(args.results_dir / "teammate_consensus.yaml") if teammate_consensus else None,
        },
        "summary": {
            "maintenance_score_summary": summarize_scores(maintenance_cards),
            "research_rigor_score_summary": summarize_scores(research_cards),
            "exploratory_nodes": sorted(set(exploratory_nodes)),
            "human_gate_required": bool(human_gate_tickets),
            "immutable_anchor_hit": any(bool(action.get("immutable_anchor_hit")) for action in actions),
            "no_change_recommended": any(action.get("disposition") == "no_change" for action in actions),
            "teammate_consensus": {
                "enabled": consensus_required(teammate_consensus),
                "majority_findings": len(teammate_consensus.get("majority_findings", [])) if teammate_consensus else 0,
                "missing_structured_payload_agents": teammate_consensus.get("missing_structured_payload_agents", []) if teammate_consensus else [],
            },
        },
        "actions": actions,
        "human_gate_tickets": human_gate_tickets,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"行动计划已保存: {args.output}")
    print(f"maintenance_scorecards: {len(maintenance_cards)}")
    print(f"research_rigor_scorecards: {len(research_cards)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
