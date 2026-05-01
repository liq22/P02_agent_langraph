#!/usr/bin/env python3
"""Build a lightweight node detail projection for the hierarchy dashboard."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml  # type: ignore

from validate_research_truth import (
    COMPLETE_ITEM_STATUSES,
    PLACEHOLDER_AGENT_MARKERS,
    PLACEHOLDER_MARKERS,
    agent_id_is_pending,
    artifact_path_exists,
    has_placeholder,
    item_is_complete,
)

from node_tier import (
    archetype_family_for_mode,
    binder_any_of_for,
    execution_profile_for,
    load_local_skill_overrides,
    load_node_tier_policy,
    node_mode_for,
    node_profile_for,
    requires_node_skill,
    requires_sop,
)


LEGACY_MINIMAL_ENTRY_BODY = "Use implicit local-entry conventions from the registry. Keep this node-local and bounded."
PROMPT_ENTRY_REFERENCES = (
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.S)

TRUTH_REVIEW_READY_STATES = {"not_required", "passed"}
EXECUTION_BLOCKING_STATES = {"missing_contract", "review_only", "contract_incomplete", "missing_outputs", "failed"}
TEXTUAL_OUTPUT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".tex", ".tsv", ".csv", ".log"}



def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def is_node_dir(path: Path) -> bool:
    return path.is_dir() and (path / "README.md").is_file() and (path / "status.yaml").is_file()


def path_to_node_id(path_str: str) -> str:
    return path_str.replace("/", "::")


REPO_ROOT_READ_PREFIXES = ("research/", "backend/", ".agent/", "scripts/", "test/")


def declared_read_path(root: Path, node_dir: Path, rel_path: str) -> Path:
    candidate = Path(rel_path)
    if candidate.is_absolute():
        return candidate
    if rel_path.startswith(REPO_ROOT_READ_PREFIXES):
        return root / candidate
    return node_dir / candidate


def infer_phase(path_str: str) -> str:
    parts = path_str.split("/")
    phase_name = parts[1] if len(parts) > 1 else ""
    match = re.match(r"^(P\d+)", phase_name)
    return match.group(1) if match else "P9"


def read_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise RuntimeError(f"{path}: YAML parse failed ({exc})") from exc
    return data if isinstance(data, dict) else {}


def read_frontmatter(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    match = FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise RuntimeError(f"{path}: frontmatter YAML parse failed ({exc})") from exc
    return data if isinstance(data, dict) else {}


def read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{path} must contain a JSON object")
    return payload


def json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value


def count_review_files(review_dir: Path) -> tuple[int, int, bool]:
    if not review_dir.exists():
        return 0, 0, False

    ai_count = 0
    human_count = 0
    response_exists = (review_dir / "response.yaml").exists()

    for item in review_dir.glob("*.md"):
        lower_name = item.name.lower()
        if lower_name.startswith("ai_") or lower_name.startswith("ai-") or "ai" in lower_name:
            ai_count += 1
        elif (
            lower_name.startswith("human_")
            or lower_name.startswith("human-")
            or lower_name.startswith("人类_")
            or "human" in lower_name
            or "人类" in item.name
        ):
            human_count += 1

    return ai_count, human_count, response_exists


def file_entry(root: Path, path: Path, label: str, state: str, exists: bool | None = None) -> dict[str, Any]:
    return {
        "label": label,
        "path": path.relative_to(root).as_posix(),
        "exists": path.exists() if exists is None else exists,
        "state": state,
    }


def linkable_files(root: Path, node_dir: Path, status: str) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = [
        file_entry(root, node_dir / "README.md", "README.md", "entry"),
        file_entry(root, node_dir / "status.yaml", "status.yaml", status),
        file_entry(root, node_dir / "docs" / "manuscript.md", "docs/manuscript.md", "body"),
        file_entry(root, node_dir / "docs" / "HUMAN_ONLY.md", "docs/HUMAN_ONLY.md", "human-only"),
        file_entry(root, node_dir / "review" / "AI_001.md", "review/AI_001.md", "review"),
        file_entry(root, node_dir / "review" / "response.yaml", "review/response.yaml", "response"),
        file_entry(root, node_dir / "review" / "verdict.yaml", "review/verdict.yaml", "review"),
    ]
    seen = {item["path"] for item in files}

    for item in sorted(node_dir.iterdir(), key=lambda path: path.name):
        if item.is_file() and not item.name.startswith("."):
            rel_path = item.relative_to(root).as_posix()
            if rel_path not in seen:
                files.append(file_entry(root, item, item.name, "node-file"))
                seen.add(rel_path)
        elif item.is_dir() and item.name in {"docs", "skills", "prompts"}:
            for nested in sorted(item.rglob("*")):
                if nested.is_file() and not any(part.startswith(".") for part in nested.relative_to(node_dir).parts):
                    rel_path = nested.relative_to(root).as_posix()
                    if rel_path not in seen:
                        files.append(
                            file_entry(
                                root,
                                nested,
                                nested.relative_to(node_dir).as_posix(),
                                item.name,
                            )
                        )
                        seen.add(rel_path)

    return files


def local_skill_files(root: Path, node_dir: Path) -> list[str]:
    skills_dir = node_dir / "skills"
    if not skills_dir.is_dir():
        return []
    return [
        path.relative_to(root).as_posix()
        for path in sorted(skills_dir.rglob("*.md"))
        if path.is_file()
    ]


def local_entry_is_thin(node_dir: Path, mode: str, cfg: dict[str, Any]) -> bool:
    entry = node_dir / "skills" / "local_entry.md"
    if not entry.is_file():
        return False
    text = entry.read_text(encoding="utf-8")
    if LEGACY_MINIMAL_ENTRY_BODY in text:
        return True
    if any(ref not in text for ref in PROMPT_ENTRY_REFERENCES):
        return True
    if requires_node_skill(mode) and "skills/SKILL.md" not in text:
        return True
    if requires_sop(mode, cfg) and "skills/SOP.md" not in text:
        return True
    if (node_dir / "skills" / "local_wrapper.md").is_file() and "skills/local_wrapper.md" not in text:
        return True
    if (node_dir / "skills" / "local_execution.md").is_file() and "skills/local_execution.md" not in text:
        return True
    return False


def local_entry_read_order(node_dir: Path) -> list[str]:
    entry = node_dir / "skills" / "local_entry.md"
    if not entry.is_file():
        return []
    text = entry.read_text(encoding="utf-8")
    return re.findall(r"(?m)^\d+\. `([^`]+)`", text)


def contract_packet(node_dir: Path) -> dict[str, Any]:
    contract_path = node_dir / "artifacts" / "execution_contract.yaml"
    if not contract_path.is_file():
        return {"path": None, "exists": False, "contract_mode": None}
    data = read_yaml(contract_path)
    return {
        "path": contract_path.name if contract_path.parent.name == "artifacts" else contract_path.as_posix(),
        "exists": True,
        "contract_mode": data.get("contract_mode"),
    }


def external_review_packet(root: Path, node_dir: Path, rel_path: str, gate: dict[str, Any]) -> dict[str, Any]:
    rubric_path = node_dir / "prompts" / "review_rubric.yaml"
    verdict_path = node_dir / "review" / "verdict.yaml"
    verdict = read_yaml(verdict_path) if verdict_path.is_file() else {}
    return {
        "required": gate.get("required", rubric_path.is_file()),
        "reviewer_role": gate.get("reviewer_role"),
        "rubric_path": rubric_path.relative_to(root).as_posix() if rubric_path.is_file() else None,
        "rubric_exists": rubric_path.is_file(),
        "verdict_path": verdict_path.relative_to(root).as_posix() if verdict_path.is_file() else None,
        "verdict_exists": verdict_path.is_file(),
        "review_complete": verdict.get("review_complete"),
        "overall_verdict": verdict.get("overall_verdict"),
        "overall_score": verdict.get("overall_score"),
        "hard_fail": verdict.get("hard_fail"),
        "reviewer_agent_id": verdict.get("reviewer_agent_id"),
        "reviewer_skill": verdict.get("reviewer_skill"),
        "downstream_ready": verdict.get("downstream_ready"),
        "independence_confirmed": verdict.get("independence_confirmed"),
        "reviewed_node_path": verdict.get("reviewed_node_path", rel_path),
    }


def node_entry_packet(
    root: Path,
    node_dir: Path,
    rel_path: str,
    status: str,
    mode: str,
    cfg: dict[str, Any],
    policy: dict[str, Any],
    checklist_data: dict[str, Any],
) -> dict[str, Any]:
    entry = node_dir / "skills" / "local_entry.md"
    prompt = node_dir / "prompts" / "research_prompt.md"
    checklist = node_dir / "prompts" / "acceptance_checklist.yaml"
    review_rubric = node_dir / "prompts" / "review_rubric.yaml"
    binder_any_of = binder_any_of_for(mode, policy)
    archetype_family = archetype_family_for_mode(mode)
    present_binders = [rel for rel in binder_any_of if (node_dir / rel).is_file()]
    contract = contract_packet(node_dir)
    external_review_gate = (
        checklist_data.get("external_review_gate")
        if isinstance(checklist_data.get("external_review_gate"), dict)
        else {}
    )
    entry_fm = read_frontmatter(entry)
    required_local_reads = cfg.get("required_local_reads") or entry_fm.get("required_local_reads") or []
    optional_local_reads = cfg.get("optional_local_reads") or entry_fm.get("optional_local_reads") or []
    missing_required_reads = [
        rel
        for rel in required_local_reads
        if not declared_read_path(root, node_dir, str(rel)).is_file()
    ]
    gaps: list[str] = []
    if not entry.is_file():
        gaps.append("missing_local_entry")
    if not prompt.is_file():
        gaps.append("missing_research_prompt")
    if not checklist.is_file():
        gaps.append("missing_acceptance_checklist")
    if external_review_gate.get("required", False) and not review_rubric.is_file():
        gaps.append("missing_review_rubric")
    if binder_any_of and not present_binders:
        gaps.append("missing_execution_binder")
    if mode == "execution" and contract["exists"] and contract.get("contract_mode") != "executable":
        gaps.append("execution_contract_not_executable")
    for rel in missing_required_reads:
        gaps.append(f"missing_required_read:{rel}")

    execution_profile = cfg.get("execution_profile") or (
        cfg.get("node_profile") if cfg.get("node_profile") in {"experiment_execution", "result_synthesis"} else None
    )
    if mode == "execution" and execution_profile == "result_synthesis":
        execution_contract_ready = bool(present_binders) and not missing_required_reads
    else:
        execution_contract_ready = mode == "execution" and bool(present_binders) and contract.get("contract_mode") == "executable" and not missing_required_reads
    return {
        "node_path": rel_path,
        "status": status,
        "node_mode": mode,
        "node_archetype_family": archetype_family,
        "node_profile": cfg.get("node_profile"),
        "execution_profile": execution_profile,
        "purpose": cfg.get("purpose") or entry_fm.get("purpose"),
        "default_delegate": cfg.get("default_delegate") or entry_fm.get("default_delegate"),
        "routes": cfg.get("routes") or entry_fm.get("routes"),
        "read_order": local_entry_read_order(node_dir),
        "required_local_reads": required_local_reads,
        "optional_local_reads": optional_local_reads,
        "prompt_path": f"{rel_path}/prompts/research_prompt.md",
        "checklist_path": f"{rel_path}/prompts/acceptance_checklist.yaml",
        "review_rubric_path": f"{rel_path}/prompts/review_rubric.yaml" if review_rubric.is_file() else None,
        "declared_outputs": cfg.get("outputs") or entry_fm.get("outputs") or [],
        "external_review_gate": {
            "required": external_review_gate.get("required", False),
            "reviewer_role": external_review_gate.get("reviewer_role"),
            "verdict_path": external_review_gate.get("verdict_path"),
        },
        "binder": {
            "required": bool(binder_any_of),
            "any_of": binder_any_of,
            "present": present_binders,
        },
        "contract": {
            "path": f"{rel_path}/artifacts/execution_contract.yaml" if contract["exists"] else None,
            "exists": contract["exists"],
            "contract_mode": contract.get("contract_mode"),
        },
        "execution_contract_ready": execution_contract_ready,
        "next_blocking_gap": gaps,
    }


def output_path_is_mappable(value: Any) -> bool:
    raw = str(value or "").strip()
    if not raw:
        return False
    candidate = Path(raw)
    return "/" in raw or "\\" in raw or bool(candidate.suffix)


def resolve_artifact_path(root: Path, manifest_path: Path, value: str) -> Path | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    candidate = Path(raw)
    candidates: list[Path] = []
    if candidate.is_absolute():
        candidates.append(candidate)
    else:
        candidates.extend([root / candidate, manifest_path.parent / candidate])
    for resolved in candidates:
        if resolved.is_file() or resolved.is_dir():
            return resolved
    return None


def contains_placeholder_agent_marker(value: Any) -> bool:
    text = str(value or "").strip().lower()
    if not text:
        return False
    return any(marker.lower() in text for marker in PLACEHOLDER_AGENT_MARKERS)


def checklist_items(payload: dict[str, Any], section: str) -> list[dict[str, Any]]:
    raw = payload.get(section) or []
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def incomplete_items(payload: dict[str, Any], section: str) -> list[dict[str, Any]]:
    return [item for item in checklist_items(payload, section) if not item_is_complete(item)]


def is_execution_output_path(value: str) -> bool:
    raw = str(value or "").strip().lower()
    return (
        raw.startswith("artifacts/")
        or raw.startswith("logs/")
        or "results" in raw
        or raw.endswith(".log")
        or "gate_report" in raw
    )


def required_output_reasons(root: Path, checklist_path: Path, checklist_data: dict[str, Any]) -> tuple[list[str], list[Path], list[str]]:
    reasons: list[str] = []
    existing_paths: list[Path] = []
    execution_paths: list[str] = []
    for item in checklist_items(checklist_data, "required_outputs"):
        raw = str(item.get("path") or item.get("item") or "").strip()
        if not raw:
            reasons.append("required_output_missing_path")
            continue
        if is_execution_output_path(raw):
            execution_paths.append(raw)
        if not output_path_is_mappable(raw):
            reasons.append(f"unmapped_required_output:{raw}")
            continue
        resolved = resolve_artifact_path(root, checklist_path, raw)
        if resolved is None:
            reasons.append(f"required_output_missing:{raw}")
            continue
        existing_paths.append(resolved)
        if resolved.is_file() and has_placeholder(resolved):
            reasons.append(f"required_output_placeholder:{raw}")
    return reasons, existing_paths, execution_paths


def review_gate_state_for(detail: dict[str, Any]) -> str:
    external_review = detail.get("external_review", {}) if isinstance(detail.get("external_review"), dict) else {}
    required = bool(external_review.get("required"))
    if not required:
        return "not_required"
    if not external_review.get("verdict_exists"):
        return "missing_verdict"
    if external_review.get("review_complete") is not True:
        return "incomplete"
    if agent_id_is_pending(external_review.get("reviewer_agent_id")):
        return "incomplete"
    if external_review.get("independence_confirmed") is not True:
        return "incomplete"
    if external_review.get("overall_verdict") != "pass" or external_review.get("hard_fail") is not False:
        return "failed"
    return "passed"


def review_gate_reason(review_gate_state: str, required: bool) -> str | None:
    if not required or review_gate_state == "passed":
        return None
    return {
        "missing_verdict": "review_gate_missing_verdict",
        "incomplete": "review_gate_incomplete",
        "failed": "review_gate_failed",
    }.get(review_gate_state)


def execution_overlay_required(node_dir: Path, detail: dict[str, Any]) -> bool:
    if detail.get("node_mode") == "execution":
        return True
    return (node_dir / "artifacts" / "execution_contract.yaml").is_file()


def contract_field_missing(contract_data: dict[str, Any], dotted_field: str) -> bool:
    current: Any = contract_data
    for key in dotted_field.split("."):
        if not isinstance(current, dict) or key not in current:
            return True
        current = current.get(key)
    return not (isinstance(current, str) and current.strip())


def execution_gate_state_for(root: Path, node_dir: Path, detail: dict[str, Any], checklist_data: dict[str, Any]) -> str:
    if not execution_overlay_required(node_dir, detail):
        return "not_applicable"
    contract_path = node_dir / "artifacts" / "execution_contract.yaml"
    if not contract_path.is_file():
        return "missing_contract"
    contract_data = read_yaml(contract_path)
    contract_mode = str(contract_data.get("contract_mode") or "").strip().lower()
    if contract_mode == "review_only":
        return "review_only"
    required_fields = ("repo_path", "run_command", "metric.name", "metric.direction", "metric.pattern")
    if contract_mode != "executable" or any(contract_field_missing(contract_data, field) for field in required_fields):
        return "contract_incomplete"
    checklist_path = node_dir / "prompts" / "acceptance_checklist.yaml"
    for raw in [path for path in checklist_items(checklist_data, "required_outputs") if isinstance(path, dict)]:
        output_path = str(raw.get("path") or raw.get("item") or "").strip()
        if not output_path or not is_execution_output_path(output_path):
            continue
        if not output_path_is_mappable(output_path):
            return "missing_outputs"
        resolved = resolve_artifact_path(root, checklist_path, output_path)
        if resolved is None:
            return "missing_outputs"
        if resolved.is_file() and has_placeholder(resolved):
            return "missing_outputs"
    return "ready"


def execution_gate_reason(state: str) -> str | None:
    return {
        "missing_contract": "execution_missing_contract",
        "review_only": "execution_review_only",
        "contract_incomplete": "execution_contract_incomplete",
        "missing_outputs": "execution_missing_outputs",
        "failed": "execution_failed",
    }.get(state)


def placeholder_risk_for(
    root: Path,
    node_dir: Path,
    detail: dict[str, Any],
    existing_required_outputs: list[Path],
) -> str:
    confirmed = False
    suspected = False

    if contains_placeholder_agent_marker(detail.get("author_agent_id")):
        confirmed = True
    external_review = detail.get("external_review", {}) if isinstance(detail.get("external_review"), dict) else {}
    if contains_placeholder_agent_marker(external_review.get("reviewer_agent_id")):
        confirmed = True

    key_paths = [node_dir / "review" / "verdict.yaml", node_dir / "artifacts" / "execution_contract.yaml", *existing_required_outputs]
    for candidate in key_paths:
        if candidate.is_file() and has_placeholder(candidate):
            confirmed = True

    for file_info in detail.get("files", []):
        if not isinstance(file_info, dict):
            continue
        rel_path = file_info.get("path")
        if not isinstance(rel_path, str):
            continue
        candidate = root / rel_path
        if not candidate.is_file():
            continue
        if candidate in key_paths:
            continue
        if file_info.get("state") in {"body", "review", "response", "prompts", "node-file"} and has_placeholder(candidate):
            suspected = True
            break

    if confirmed:
        return "confirmed"
    if suspected:
        return "suspected"
    return "none"


def handoff_items_complete(checklist_data: dict[str, Any]) -> bool:
    return all(item_is_complete(item) for item in checklist_items(checklist_data, "handoff_ready_if"))


def dedupe_reasons(reasons: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for reason in reasons:
        if reason and reason not in seen:
            seen.add(reason)
            ordered.append(reason)
    return ordered


def direct_parent_map(nodes: dict[str, Any]) -> dict[str, str | None]:
    by_path = {detail.get("path"): node_id for node_id, detail in nodes.items() if isinstance(detail.get("path"), str)}
    parent_map: dict[str, str | None] = {}
    for node_id, detail in nodes.items():
        path = Path(str(detail.get("path", "")))
        parent_id: str | None = None
        for ancestor in path.parents:
            ancestor_key = ancestor.as_posix()
            if ancestor_key in by_path:
                parent_id = by_path[ancestor_key]
                break
        parent_map[node_id] = parent_id
    return parent_map


def depth_for_path(path_value: str) -> int:
    return len(Path(path_value).parts)


def derive_flags(root: Path, detail: dict[str, Any], overrides: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    status = detail.get("status")
    progress = detail.get("progress_pct")
    review_gate = detail.get("review_gate", {}) or {}
    external_review = detail.get("external_review", {}) or {}
    local_skill_files = detail.get("local_skill_files", []) or []
    node_path = str(detail.get("path", ""))
    path = Path(node_path)
    mode = node_mode_for(node_path, overrides)
    cfg = (overrides.get("nodes") or {}).get(node_path, {})

    if status == "active" and progress in (0, None):
        flags.append("zero-progress-active")
    if review_gate.get("ai_review_count", 0) == 0 and review_gate.get("human_review_count", 0) == 0:
        flags.append("review-not-started")
    if review_gate.get("external_ai_review_required") and not external_review.get("rubric_exists"):
        flags.append("missing-review-rubric")
    if review_gate.get("external_ai_review_required") and not external_review.get("verdict_exists"):
        flags.append("missing-external-review-verdict")
    if external_review.get("review_complete") and external_review.get("hard_fail"):
        flags.append("external-review-hard-fail")
    if external_review.get("review_complete") and external_review.get("overall_verdict") not in {None, "pass"}:
        flags.append("external-review-not-passed")
    if external_review.get("review_complete") and not external_review.get("independence_confirmed"):
        flags.append("external-review-independence-unconfirmed")
    if not any(path.endswith("/skills/local_entry.md") for path in local_skill_files):
        flags.append("missing-local-entry")
    has_node_skill = any(path_str.endswith("/skills/SKILL.md") for path_str in local_skill_files)
    has_sop = any(path_str.endswith("/skills/SOP.md") for path_str in local_skill_files)
    has_local_execution = any(path_str.endswith("/skills/local_execution.md") for path_str in local_skill_files)

    if requires_node_skill(mode):
        if not has_node_skill:
            flags.append("missing-node-skill")
    elif has_node_skill:
        flags.append("unexpected-node-skill")

    if requires_sop(mode, cfg):
        if not has_sop:
            flags.append("missing-sop")
    elif has_sop:
        flags.append("unexpected-sop")

    if mode != "execution" and has_local_execution:
        flags.append("unexpected-local-execution")

    binder_any_of = binder_any_of_for(mode, policy)
    if binder_any_of and not any((root / node_path / rel_path).is_file() for rel_path in binder_any_of):
        flags.append("missing-execution-binder")

    if path and local_entry_is_thin(root / path, mode, cfg):
        flags.append("thin-local-entry")
    return flags


def local_truth_snapshot(root: Path, node_dir: Path, detail: dict[str, Any], checklist_data: dict[str, Any]) -> dict[str, Any]:
    checklist_path = node_dir / "prompts" / "acceptance_checklist.yaml"
    reasons: list[str] = []
    if not checklist_path.is_file():
        reasons.append("missing_acceptance_checklist")

    questions_incomplete = incomplete_items(checklist_data, "required_questions_answered")
    if questions_incomplete:
        reasons.append("required_questions_incomplete")

    output_reasons, existing_required_outputs, _ = required_output_reasons(root, checklist_path, checklist_data)
    reasons.extend(output_reasons)

    quality_incomplete = incomplete_items(checklist_data, "quality_checks")
    if quality_incomplete:
        reasons.append("quality_checks_incomplete")

    execution_state = execution_gate_state_for(root, node_dir, detail, checklist_data)
    execution_reason = execution_gate_reason(execution_state)
    if execution_reason:
        reasons.append(execution_reason)

    review_state = review_gate_state_for(detail)
    placeholder_risk = placeholder_risk_for(root, node_dir, detail, existing_required_outputs)

    return {
        "_local_truth_ready": not reasons,
        "_local_blocking_reasons": dedupe_reasons(reasons),
        "_review_ready": review_state in TRUTH_REVIEW_READY_STATES,
        "_handoff_complete": handoff_items_complete(checklist_data),
        "review_gate_state": review_state,
        "execution_gate_state": execution_state,
        "placeholder_risk": placeholder_risk,
    }


def build_detail(root: Path, node_dir: Path, overrides: dict[str, Any], policy: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    rel_path = node_dir.relative_to(root).as_posix()
    node_id = path_to_node_id(rel_path)
    status_data = read_yaml(node_dir / "status.yaml")
    checklist_path = node_dir / "prompts" / "acceptance_checklist.yaml"
    checklist_data = read_yaml(checklist_path) if checklist_path.is_file() else {}
    lifecycle = status_data.get("lifecycle") if isinstance(status_data.get("lifecycle"), dict) else {}
    review_gate = status_data.get("review_gate") if isinstance(status_data.get("review_gate"), dict) else {}
    external_review_gate = (
        checklist_data.get("external_review_gate") if isinstance(checklist_data.get("external_review_gate"), dict) else {}
    )
    ai_count_fs, human_count_fs, response_exists = count_review_files(node_dir / "review")
    status = status_data.get("status") or lifecycle.get("stage") or "seed"
    child_node_count = sum(1 for child in node_dir.iterdir() if child.is_dir() and is_node_dir(child))
    mode = node_mode_for(rel_path, overrides)
    profile = node_profile_for(rel_path, overrides)
    execution_profile = execution_profile_for(rel_path, overrides)
    archetype_family = archetype_family_for_mode(mode)

    cfg = (overrides.get("nodes") or {}).get(rel_path, {})
    external_review = external_review_packet(root, node_dir, rel_path, external_review_gate)
    detail: dict[str, Any] = {
        "path": rel_path,
        "title": node_dir.name,
        "phase": infer_phase(rel_path),
        "status": status,
        "kind": "parent" if child_node_count else "leaf",
        "node_mode": mode,
        "node_archetype_family": archetype_family,
        "node_profile": profile,
        "execution_profile": execution_profile,
        "required_local_reads": cfg.get("required_local_reads") or [],
        "optional_local_reads": cfg.get("optional_local_reads") or [],
        "lifecycle_stage": lifecycle.get("stage"),
        "progress_pct": status_data.get("progress_pct"),
        "review_gate": {
            "ai_review_count": review_gate.get("ai_review_count", ai_count_fs),
            "human_review_count": review_gate.get("human_review_count", human_count_fs),
            "all_comments_responded": review_gate.get("all_comments_responded", response_exists),
            "response_exists": response_exists,
            "external_ai_review_required": external_review.get("required", False),
            "external_ai_review_complete": external_review.get("review_complete"),
            "external_ai_review_verdict": external_review.get("overall_verdict"),
            "external_ai_review_score": external_review.get("overall_score"),
            "external_ai_review_hard_fail": external_review.get("hard_fail"),
            "external_ai_reviewer_id": external_review.get("reviewer_agent_id"),
        },
        "can_enter_fix": status_data.get("can_enter_fix"),
        "heartbeat_at": status_data.get("heartbeat_at"),
        "author_agent_id": status_data.get("author_agent_id"),
        "last_actor": status_data.get("last_actor"),
        "readme_path": f"{rel_path}/README.md",
        "status_path": f"{rel_path}/status.yaml",
        "files": linkable_files(root, node_dir, status),
        "local_skill_files": local_skill_files(root, node_dir),
        "external_review": external_review,
    }
    detail["node_entry_packet"] = node_entry_packet(root, node_dir, rel_path, status, mode, cfg, policy, checklist_data)
    detail["flags"] = derive_flags(root, detail, overrides, policy)
    detail.update(local_truth_snapshot(root, node_dir, detail, checklist_data))
    return node_id, json_safe(detail)


def annotate_truth_fields(nodes: dict[str, Any], graph_status: dict[str, Any]) -> None:
    ready = set(graph_status.get("ready_nodes", []) or [])
    parent_map = direct_parent_map(nodes)
    children_by_parent: dict[str, list[str]] = {}
    for node_id, parent_id in parent_map.items():
        if parent_id is None:
            continue
        children_by_parent.setdefault(parent_id, []).append(node_id)
    for child_ids in children_by_parent.values():
        child_ids.sort(key=lambda item: str(nodes[item].get("path", item)))

    for node_id, detail in nodes.items():
        detail["scheduler_ready"] = node_id in ready

    for node_id, detail in sorted(nodes.items(), key=lambda item: depth_for_path(str(item[1].get("path", ""))), reverse=True):
        kind = detail.get("kind")
        local_truth_ready = bool(detail.pop("_local_truth_ready", False))
        local_blocking_reasons = list(detail.pop("_local_blocking_reasons", []))
        review_ready = bool(detail.pop("_review_ready", False))
        handoff_complete = bool(detail.pop("_handoff_complete", False))
        review_state = str(detail.get("review_gate_state") or "not_required")
        execution_state = str(detail.get("execution_gate_state") or "not_applicable")

        final_reasons = list(local_blocking_reasons)
        truth_ready = local_truth_ready

        if kind == "parent" and truth_ready:
            child_blockers = [child_id for child_id in children_by_parent.get(node_id, []) if not nodes[child_id].get("truth_ready")]
            if child_blockers:
                final_reasons.extend(f"parent_child_truth_missing:{child_id}" for child_id in child_blockers)

        review_required = review_state != "not_required"
        review_reason = review_gate_reason(review_state, review_required)
        if review_reason:
            final_reasons.append(review_reason)

        if kind == "parent" and truth_ready and any(reason.startswith("parent_child_truth_missing:") for reason in final_reasons):
            handoff_readiness = "blocked_parent_rollup"
        elif truth_ready and not review_ready:
            handoff_readiness = "blocked_review"
        elif truth_ready and review_ready and not handoff_complete:
            final_reasons.append("handoff_requirements_incomplete")
            handoff_readiness = "blocked_unknown"
        elif truth_ready:
            handoff_readiness = "ready"
        elif execution_state in EXECUTION_BLOCKING_STATES:
            handoff_readiness = "blocked_execution"
        elif final_reasons:
            handoff_readiness = "blocked_truth"
        else:
            handoff_readiness = "blocked_unknown"

        detail["truth_ready"] = truth_ready
        detail["handoff_readiness"] = handoff_readiness
        detail["blocking_reasons"] = dedupe_reasons(final_reasons)


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dashboard node details projection.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    research_root = root / "research"
    out_path = root / "backend" / "graph" / "node_details.json"
    overrides = load_local_skill_overrides(root)
    policy = load_node_tier_policy(root)
    graph_status_path = root / "backend" / "graph" / "graph_status.json"
    graph_status = read_json(graph_status_path) if graph_status_path.is_file() else {}

    nodes: dict[str, Any] = {}
    for directory in sorted(research_root.rglob("*")):
        if is_node_dir(directory):
            node_id, detail = build_detail(root, directory, overrides, policy)
            nodes[node_id] = detail

    annotate_truth_fields(nodes, graph_status)
    atomic_write_json(out_path, {"nodes": nodes})
    print(f"[node_details_ok] nodes={len(nodes)} output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
