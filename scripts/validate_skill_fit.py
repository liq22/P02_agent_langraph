#!/usr/bin/env python3
"""Validate that global and node-local skills fit the current research tree."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

from node_tier import (
    binder_any_of_for,
    execution_profile_for,
    load_local_skill_overrides,
    load_node_tier_policy,
    node_mode_for,
    node_profile_for,
    required_files_for,
    requires_node_skill,
    requires_sop,
)

RESEARCH_PROMPT_REQUIRED_HEADINGS = (
    "## 节点定位",
    "## 本轮目标",
    "### 节点职责",
    "### 必答研究问题",
    "### 本轮最小交付",
    "## 输入优先级",
    "## 阶段标准与局部附加约束",
    "### 研究判断口径",
    "## 研究者视角",
    "## 本节点应该做出的关键判断",
    "## 证据 / 引用 / 图表要求",
    "## 不合格写法",
    "### 质量门槛",
    "### 可交接条件",
    "## 执行边界",
    "### 明确不做",
    "### 停止条件",
    "## 供执行者填写的本轮摘要",
)
BANNED_LOCAL_ENTRY_FIELDS = {
    "type",
    "trigger",
    "graph_reads",
    "local_reads",
    "refresh_policy",
    "prompt_read_surface",
    "mutable_paths",
    "protected_paths",
    "append_only_artifacts",
    "reviewer_independence",
    "stage_routes",
}
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.S)
RESEARCH_PROMPT_BANNED_HEADINGS = (
    "## 本节点必须回答的问题",
    "## 本节点建议产出",
    "## stop_with 建议",
)
NODE_SKILL_REQUIRED_HEADINGS = (
    "## Node Context",
    "## Use When",
    "## Strategy Delta",
    "## Local Routing / Delegate Contract",
    "## Boundaries",
)
NODE_SKILL_BANNED_HEADINGS = (
    "## Required Inputs",
    "## Prompt Assets",
    "## Required Questions",
    "## Expected Outputs",
    "## Workflow",
    "## Quality Gates",
    "## stop_with",
)
NODE_SOP_REQUIRED_HEADINGS = (
    "## Read Order",
    "## Preflight",
    "## Operating Procedure",
    "## Stop Rules",
    "## Delegate Notes",
)
NODE_SOP_BANNED_HEADINGS = (
    "## Acceptance Review",
    "## Quality Gates",
    "## Expected Outputs",
    "## Required Questions",
)
RESEARCH_PROMPT_DONE_LINE = "完成定义以 `prompts/acceptance_checklist.yaml` 为准。"
PROMPT_ENTRY_REFERENCES = (
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
)
EXPECTED_NODE_MODE_COUNTS = {
    "parent": 7,
    "lite": 11,
    "standard": 22,
    "execution": 4,
}
VALID_RESEARCH_PROFILES = {"routing_parent", "lite_research_leaf", "evidence_leaf", "hard_gate"}
MODE_ALLOWED_RESEARCH_PROFILES = {
    "parent": {"routing_parent"},
    "lite": {"lite_research_leaf", "hard_gate"},
    "standard": {"evidence_leaf", "hard_gate"},
    "execution": {"evidence_leaf", "hard_gate"},
}
PROFILE_REQUIRED_KEYS = {
    "lite_research_leaf": ("node_researcher_lens", "required_artifacts", "author_exit_if", "node_close_if", "blocking_failure_modes"),
    "evidence_leaf": ("node_researcher_lens", "required_artifacts", "author_exit_if", "node_close_if", "blocking_failure_modes"),
    "hard_gate": ("node_researcher_lens", "required_artifacts", "author_exit_if", "node_close_if", "blocking_failure_modes"),
}
REQUIRED_RESEARCHER_HEADINGS = (
    "## 研究者视角",
    "## 本节点应该做出的关键判断",
    "## 证据 / 引用 / 图表要求",
    "## 不合格写法",
)
REQUIRED_CANONICAL_SKILLS = {"citation_verifier", "autonomous_research_lane"}
REQUIRED_ALIASES = {
    "citation-verifier": "citation_verifier",
    "citation-check": "citation_verifier",
    "autonomous-research-lane": "autonomous_research_lane",
}
CATALOG_REQUIRED_FIELDS = {
    "name",
    "role",
    "scope",
    "requires_selected_node",
    "requires_execution_contract",
    "can_cross_nodes",
    "default_visibility",
}
VALID_CATALOG_ROLES = {"entry", "lane", "worker", "helper", "profile"}
VALID_CATALOG_VISIBILITY = {"core", "operator_only", "optional"}
EXPECTED_CATALOG_ROLES = {
    "graph_driven_research_orchestrator": "entry",
    "auto_research_campaign": "entry",
    "autonomous_research_lane": "lane",
    "auto_experiment_worker": "worker",
    "idea_discovery_or_problem_formulation": "worker",
    "experiment_design_or_execution": "worker",
    "manuscript_worker": "worker",
    "auto_review_loop": "worker",
    "external_node_reviewer": "helper",
    "response_worker": "worker",
    "aggregate_reviews": "helper",
    "leaf_node_writer": "helper",
    "citation_verifier": "helper",
    "paper_figure": "helper",
    "result_to_claim": "helper",
    "structured_map_builder": "helper",
    "draft_export_sync": "helper",
    "response_coverage_check": "helper",
    "karpathy-skills": "profile",
    "deai_cn_skill": "profile",
}
KEY_NODE_RESEARCHER_TOKENS = {
    "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证": (
        "baseline",
        "metric",
        "variance/statistical validity",
        "failure interpretation",
        "reproducibility",
    ),
    "research/P2_论文撰写/P2_04_形式检查": (
        "citation criticality",
        "core-claim block",
        "figure provenance",
        "first_callout_location",
        "venue_requirements.yaml",
    ),
    "research/P4_论文回复_response/P4_07_再投稿打包": (
        "submission bundle consistency",
        "citation registry",
        "figure manifest",
        "venue requirements",
        "evidence map",
    ),
    "research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案": (
        "EIC",
        "devil's advocate",
        "reviewer_lens_matrix.yaml",
    ),
    "research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要": (
        "review_issue_register.yaml",
        "severity",
        "evidence location",
    ),
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def node_dirs(root: Path) -> list[Path]:
    research_root = root / "research"
    return sorted(
        path.parent
        for path in research_root.rglob("status.yaml")
        if (path.parent / "README.md").is_file()
    )


def global_skill_names(root: Path) -> set[str]:
    return {
        path.parent.name
        for path in (root / ".agent" / "skills").glob("*/SKILL.md")
        if path.is_file()
    }


def catalog_skill_entries(root: Path) -> list[dict]:
    catalog = root / "backend" / "registry" / "skill_registry" / "skill_catalog.yaml"
    payload = load_yaml(catalog)
    skills = payload.get("skills")
    if not isinstance(skills, list):
        return []
    return [item for item in skills if isinstance(item, dict)]


def catalog_skill_names(root: Path) -> set[str]:
    return {str(item.get("name")).strip() for item in catalog_skill_entries(root) if str(item.get("name", "")).strip()}


def check_skill_catalog(root: Path, globals_: set[str], errors: list[str]) -> set[str]:
    catalog_path = root / "backend" / "registry" / "skill_registry" / "skill_catalog.yaml"
    payload = load_yaml(catalog_path)
    raw_skills = payload.get("skills")
    if not isinstance(raw_skills, list):
        errors.append("skill_catalog.yaml must contain a list at `skills`")
        return set()

    names: list[str] = []
    for index, entry in enumerate(raw_skills):
        if not isinstance(entry, dict):
            errors.append(f"skill_catalog.yaml entry {index} must be a mapping, not a flat string")
            continue
        missing = sorted(CATALOG_REQUIRED_FIELDS - set(entry))
        name = str(entry.get("name", "")).strip()
        if not name:
            errors.append(f"skill_catalog.yaml entry {index} missing non-empty name")
            continue
        names.append(name)
        if missing:
            errors.append(f"skill_catalog.yaml `{name}` missing fields: {missing}")
        role = entry.get("role")
        visibility = entry.get("default_visibility")
        if role not in VALID_CATALOG_ROLES:
            errors.append(f"skill_catalog.yaml `{name}` has invalid role={role}")
        if visibility not in VALID_CATALOG_VISIBILITY:
            errors.append(f"skill_catalog.yaml `{name}` has invalid default_visibility={visibility}")
        for field in ("requires_selected_node", "requires_execution_contract", "can_cross_nodes"):
            if not isinstance(entry.get(field), bool):
                errors.append(f"skill_catalog.yaml `{name}` field `{field}` must be boolean")
        expected_role = EXPECTED_CATALOG_ROLES.get(name)
        if expected_role and role != expected_role:
            errors.append(f"skill_catalog.yaml `{name}` role must be {expected_role}, got {role}")

    catalog_names = set(names)
    duplicates = sorted(name for name in catalog_names if names.count(name) > 1)
    if duplicates:
        errors.append(f"skill_catalog.yaml has duplicate names: {duplicates}")
    if "autoresearch" in catalog_names:
        errors.append("skill_catalog.yaml must not list legacy `autoresearch` as an active skill")
    if "autoresearch" in globals_:
        errors.append(".agent/skills/autoresearch must not exist as an active runtime skill")

    experiment_workers = [
        entry.get("name")
        for entry in raw_skills
        if isinstance(entry, dict)
        and entry.get("role") == "worker"
        and entry.get("requires_execution_contract") is True
    ]
    if experiment_workers != ["auto_experiment_worker"]:
        errors.append(f"auto_experiment_worker must be the only execution-contract worker, got {experiment_workers}")
    return catalog_names


def alias_map(root: Path) -> dict[str, str]:
    payload = load_yaml(root / "backend" / "registry" / "skill_registry" / "skill_aliases.yaml")
    aliases = payload.get("aliases")
    if not isinstance(aliases, dict):
        return {}
    return {str(key): str(value) for key, value in aliases.items()}


def delegates_from_skill(skill_path: Path) -> list[str]:
    text = skill_path.read_text(encoding="utf-8")
    return re.findall(r"canonical_global_skill:\s*([A-Za-z0-9_-]+)", text)


def load_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def effective_profile_value(overrides: dict, phase: str, profile: str, cfg: dict, key: str) -> object:
    if key in cfg:
        return cfg[key]
    phase_defaults = ((overrides.get("phase_profile_defaults") or {}).get(phase) or {}).get(profile)
    if isinstance(phase_defaults, dict) and key in phase_defaults:
        return phase_defaults[key]
    profile_defaults = (overrides.get("profile_defaults") or {}).get(profile)
    if isinstance(profile_defaults, dict) and key in profile_defaults:
        return profile_defaults[key]
    return None


def value_present(value: object) -> bool:
    if value is None:
        return False
    if value in ("", [], {}):
        return False
    return True


def check_global_frontmatter(root: Path, errors: list[str]) -> None:
    for skill_path in sorted((root / ".agent" / "skills").glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not match:
            errors.append(f"{skill_path}: missing YAML frontmatter")
            continue
        fields = [
            line.split(":", 1)[0].strip()
            for line in match.group(1).splitlines()
            if line.strip() and ":" in line and not line.startswith(" ")
        ]
        for field in fields:
            if field not in {"name", "description"}:
                errors.append(f"{skill_path}: unsupported global skill frontmatter field {field}")


def ensure_heading_contract(
    text: str,
    rel_path: str,
    required_headings: tuple[str, ...],
    banned_headings: tuple[str, ...],
    errors: list[str],
) -> None:
    for heading in required_headings:
        if heading not in text:
            errors.append(f"{rel_path}: missing required heading `{heading}`")
    for heading in banned_headings:
        if heading in text:
            errors.append(f"{rel_path}: contains banned heading `{heading}`")


def checklist_items(checklist: dict, key: str, field: str = "item") -> list[str]:
    items = checklist.get(key) or []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            value = item.get(field)
            if not value and field != "path":
                value = item.get("path")
            if value:
                out.append(str(value))
        elif isinstance(item, str):
            out.append(item)
    return out


def checklist_output_tokens(checklist: dict) -> list[str]:
    items = checklist.get("required_outputs") or []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            value = str(item.get("path", "")).strip()
            if value:
                out.append(value)
        elif isinstance(item, str):
            out.append(item)
    return out


def prompt_asset_status(checklist: dict, rel_path: str) -> str:
    prompt_assets = checklist.get("prompt_assets") if isinstance(checklist.get("prompt_assets"), list) else []
    for item in prompt_assets:
        if isinstance(item, dict) and str(item.get("path", "")).strip() == rel_path:
            return str(item.get("status", "")).strip()
    return ""


def routing_stop_items(node_cfg: dict, checklist: dict) -> list[str]:
    items = checklist_items(checklist, "stop_if")
    if node_cfg.get("stop_with"):
        items.append(str(node_cfg["stop_with"]))
    for rule in node_cfg.get("decision_rule") or []:
        if "stop_with" in rule:
            items.append(str(rule["stop_with"]))
    return items


def external_review_required(checklist: dict) -> bool:
    gate = checklist.get("external_review_gate")
    return isinstance(gate, dict) and gate.get("required") is True


def ensure_prompt_mentions(prompt_text: str, rel_path: str, label: str, items: list[str], errors: list[str]) -> None:
    missing = [item for item in items if item and item not in prompt_text]
    if missing:
        errors.append(f"{rel_path}: missing {label}: {missing}")


def check_local_entry_frontmatter(entry_text: str, rel_path: str, errors: list[str]) -> None:
    match = FRONTMATTER_RE.match(entry_text)
    if not match:
        errors.append(f"{rel_path}: missing YAML frontmatter")
        return
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        field = stripped.split(":", 1)[0]
        if field in BANNED_LOCAL_ENTRY_FIELDS:
            errors.append(f"{rel_path}: banned local_entry field `{field}:`")


def validate(root: Path) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    nodes = node_dirs(root)
    globals_ = global_skill_names(root)
    catalog = check_skill_catalog(root, globals_, errors)
    overrides = load_local_skill_overrides(root)
    policy = load_node_tier_policy(root)
    overrides_text = (root / "backend" / "registry" / "skill_registry" / "local_skill_overrides.yaml").read_text(encoding="utf-8")
    mode_counts: dict[str, int] = {}
    for cfg in (overrides.get("nodes") or {}).values():
        mode = str(cfg.get("node_mode", "")).strip()
        mode_counts[mode] = mode_counts.get(mode, 0) + 1
    if root == repo_root_from_script() and mode_counts != EXPECTED_NODE_MODE_COUNTS:
        errors.append(f"node_mode distribution changed: expected {EXPECTED_NODE_MODE_COUNTS}, got {mode_counts}")
    if "extra_local_reads:" in overrides_text:
        errors.append("local_skill_overrides.yaml still contains legacy `extra_local_reads`")

    if catalog != globals_:
        missing_dirs = sorted(catalog - globals_)
        missing_catalog = sorted(globals_ - catalog)
        if missing_dirs:
            errors.append(f"catalog entries without .agent skills: {missing_dirs}")
        if missing_catalog:
            errors.append(f".agent skills missing from catalog: {missing_catalog}")
    if root == repo_root_from_script():
        missing_required = sorted(REQUIRED_CANONICAL_SKILLS - globals_)
        if missing_required:
            errors.append(f"missing required canonical skills: {missing_required}")
        aliases = alias_map(root)
        for alias, target in REQUIRED_ALIASES.items():
            if aliases.get(alias) != target:
                errors.append(f"skill_aliases.yaml must map `{alias}` to `{target}`")
        guidance_path = root / "backend" / "registry" / "skill_registry" / "reference_guidance_map.yaml"
        guidance = load_yaml(guidance_path)
        if not guidance:
            errors.append("reference_guidance_map.yaml is missing or empty")
        for phase in ["P0", "P1", "P2", "P3", "P4"]:
            phase_lens = ((guidance.get("phase_lenses") or {}).get(phase) if isinstance(guidance, dict) else None)
            if not isinstance(phase_lens, dict) or not phase_lens.get("researcher_role"):
                errors.append(f"reference_guidance_map.yaml missing researcher_role for {phase}")

    check_global_frontmatter(root, errors)

    local_files = sorted((root / "research").glob("**/skills/*.md"))
    for node in nodes:
        node_rel = node.relative_to(root).as_posix()
        mode = node_mode_for(node_rel, overrides)
        research_profile = node_profile_for(node_rel, overrides)
        profile = execution_profile_for(node_rel, overrides)
        node_cfg = (overrides.get("nodes") or {}).get(node_rel) or {}
        phase = node_rel.split("/", 2)[1].split("_", 1)[0] if "/" in node_rel else "P9"
        if research_profile not in VALID_RESEARCH_PROFILES:
            errors.append(f"{node_rel}: invalid node_profile={research_profile}")
        if research_profile not in MODE_ALLOWED_RESEARCH_PROFILES.get(mode, set()):
            errors.append(f"{node_rel}: node_mode={mode} is incompatible with node_profile={research_profile}")
        for key in PROFILE_REQUIRED_KEYS.get(research_profile, ()):
            if not value_present(effective_profile_value(overrides, phase, research_profile, node_cfg, key)):
                errors.append(f"{node_rel}: node_profile={research_profile} missing effective `{key}`")
        required_files = required_files_for(mode, policy)
        for rel_path in required_files:
            if not (node / rel_path).is_file():
                errors.append(f"{node_rel}: missing required `{rel_path}` for node_mode={mode}")
        if profile and mode != "execution":
            errors.append(f"{node_rel}: execution_profile={profile} requires node_mode=execution")

        prompt_path = node / "prompts" / "research_prompt.md"
        checklist_path = node / "prompts" / "acceptance_checklist.yaml"
        review_rubric = node / "prompts" / "review_rubric.yaml"
        review_verdict = node / "review" / "verdict.yaml"
        entry_path = node / "skills" / "local_entry.md"
        checklist = load_yaml(checklist_path)
        requires_external_review = external_review_required(checklist)
        if prompt_path.is_file():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            ensure_heading_contract(
                prompt_text,
                prompt_path.relative_to(root).as_posix(),
                RESEARCH_PROMPT_REQUIRED_HEADINGS,
                RESEARCH_PROMPT_BANNED_HEADINGS,
                errors,
            )
            if RESEARCH_PROMPT_DONE_LINE not in prompt_text:
                errors.append(f"{prompt_path.relative_to(root).as_posix()}: missing acceptance checklist done-state line")
            for heading in REQUIRED_RESEARCHER_HEADINGS:
                if heading not in prompt_text:
                    errors.append(f"{prompt_path.relative_to(root).as_posix()}: missing researcher heading `{heading}`")
            key_tokens = KEY_NODE_RESEARCHER_TOKENS.get(node_rel) if root == repo_root_from_script() else None
            if key_tokens:
                for token in key_tokens:
                    if token not in prompt_text:
                        errors.append(
                            f"{prompt_path.relative_to(root).as_posix()}: missing key researcher token `{token}`"
                        )
        if entry_path.is_file():
            entry_text = entry_path.read_text(encoding="utf-8")
            check_local_entry_frontmatter(entry_text, entry_path.relative_to(root).as_posix(), errors)
            required_entry_refs = (
                PROMPT_ENTRY_REFERENCES
                if requires_external_review
                else tuple(ref for ref in PROMPT_ENTRY_REFERENCES if ref != "prompts/review_rubric.yaml")
            )
            for ref in required_entry_refs:
                if ref not in entry_text:
                    errors.append(f"{entry_path.relative_to(root).as_posix()}: missing local entry reference `{ref}`")

        if prompt_path.is_file():
            prompt_text = prompt_path.read_text(encoding="utf-8")
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "node purpose", [str(node_cfg.get("purpose", "")).strip()], errors)
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "required research questions", checklist_items(checklist, "required_questions_answered"), errors)
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "author exit", checklist_items(checklist, "author_exit"), errors)
            ensure_prompt_mentions(
                prompt_text,
                prompt_path.relative_to(root).as_posix(),
                "minimum deliverables",
                checklist_output_tokens(checklist) + [str(item) for item in (node_cfg.get("outputs") or [])],
                errors,
            )
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "quality checks", checklist_items(checklist, "quality_checks"), errors)
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "handoff readiness", checklist_items(checklist, "handoff_ready_if"), errors)
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "node close", checklist_items(checklist, "node_close"), errors)
            ensure_prompt_mentions(prompt_text, prompt_path.relative_to(root).as_posix(), "stop conditions", routing_stop_items(node_cfg, checklist), errors)
        if requires_external_review and prompt_asset_status(checklist, "prompts/review_rubric.yaml") not in {"required", "reviewer_required"}:
            errors.append(
                f"{checklist_path.relative_to(root).as_posix()}: missing required or reviewer_required prompt asset `prompts/review_rubric.yaml`"
            )
        external_review_gate = (
            checklist.get("external_review_gate") if isinstance(checklist.get("external_review_gate"), dict) else {}
        )
        if requires_external_review:
            if external_review_gate.get("reviewer_role") != "external_node_reviewer":
                errors.append(
                    f"{checklist_path.relative_to(root).as_posix()}: external_review_gate.reviewer_role must be `external_node_reviewer`"
                )

            rubric_payload = load_yaml(review_rubric)
            if rubric_payload.get("reviewer_role") != "external_node_reviewer":
                errors.append(f"{review_rubric.relative_to(root).as_posix()}: reviewer_role must be `external_node_reviewer`")

            verdict_payload = load_yaml(review_verdict)
            if verdict_payload.get("reviewer_skill") != "external_node_reviewer":
                errors.append(f"{review_verdict.relative_to(root).as_posix()}: reviewer_skill must be `external_node_reviewer`")

        if not requires_node_skill(mode) and (node / "skills" / "SKILL.md").is_file():
            errors.append(f"{node_rel}: unexpected skills/SKILL.md for node_mode={mode}")
        elif requires_node_skill(mode):
            skill_path = node / "skills" / "SKILL.md"
            if skill_path.is_file():
                ensure_heading_contract(
                    skill_path.read_text(encoding="utf-8"),
                    skill_path.relative_to(root).as_posix(),
                    NODE_SKILL_REQUIRED_HEADINGS,
                    NODE_SKILL_BANNED_HEADINGS,
                    errors,
                )
        if not requires_sop(mode, node_cfg) and (node / "skills" / "SOP.md").is_file():
            errors.append(f"{node_rel}: unexpected skills/SOP.md for node_mode={mode}")
        elif requires_sop(mode, node_cfg):
            sop_path = node / "skills" / "SOP.md"
            if sop_path.is_file():
                ensure_heading_contract(
                    sop_path.read_text(encoding="utf-8"),
                    sop_path.relative_to(root).as_posix(),
                    NODE_SOP_REQUIRED_HEADINGS,
                    NODE_SOP_BANNED_HEADINGS,
                    errors,
                )
        if not any((node / rel_path).is_file() for rel_path in binder_any_of_for(mode, policy)) and binder_any_of_for(mode, policy):
            errors.append(f"{node_rel}: missing execution binder for node_mode={mode}")
        if mode != "execution" and (node / "skills" / "local_execution.md").is_file():
            errors.append(f"{node_rel}: unexpected skills/local_execution.md for node_mode={mode}")

        skill_text = (node / "skills" / "SKILL.md").read_text(encoding="utf-8") if (node / "skills" / "SKILL.md").is_file() else ""
        sop_text = (node / "skills" / "SOP.md").read_text(encoding="utf-8") if (node / "skills" / "SOP.md").is_file() else ""
        wrapper_text = (node / "skills" / "local_wrapper.md").read_text(encoding="utf-8") if (node / "skills" / "local_wrapper.md").is_file() else ""
        execution_text = (node / "skills" / "local_execution.md").read_text(encoding="utf-8") if (node / "skills" / "local_execution.md").is_file() else ""

        if profile == "experiment_execution":
            if "artifacts/execution_contract.yaml" not in (skill_text + sop_text + wrapper_text + execution_text):
                errors.append(f"{node_rel}: experiment_execution stack must mention `artifacts/execution_contract.yaml`")
            if "auto_experiment_worker" not in (wrapper_text + execution_text):
                errors.append(f"{node_rel}: experiment_execution stack must route to `auto_experiment_worker`")
        if profile == "result_synthesis":
            if not (node / "skills" / "local_execution.md").is_file():
                errors.append(f"{node_rel}: result_synthesis nodes must bind `skills/local_execution.md`")
            if "execution contract" in execution_text.lower():
                errors.append(f"{node_rel}: result_synthesis local_execution must not mention execution contract")
            if "artifacts/auto_experiment/results.tsv" not in (skill_text + sop_text + execution_text):
                errors.append(f"{node_rel}: result_synthesis stack must mention `artifacts/auto_experiment/results.tsv`")
            if "artifacts/result_registry.yaml" not in (skill_text + sop_text + execution_text):
                errors.append(f"{node_rel}: result_synthesis stack must mention `artifacts/result_registry.yaml`")
        if "paper_figure" in (
            str(node_cfg.get("default_delegate", ""))
            + str(node_cfg.get("decision_rule", ""))
            + str(node_cfg.get("outputs", ""))
        ):
            prompt_text = prompt_path.read_text(encoding="utf-8") if prompt_path.is_file() else ""
            if "artifacts/figure_manifest.yaml" not in prompt_text + skill_text + wrapper_text:
                errors.append(f"{node_rel}: paper_figure nodes must mention `artifacts/figure_manifest.yaml`")

    for skill_path in local_files:
        try:
            node = skill_path.parent.parent
            node_rel = node.relative_to(root).as_posix()
        except ValueError:
            errors.append(f"{skill_path}: not under repository root")
            continue
        if not (node / "README.md").is_file() or not (node / "status.yaml").is_file():
            errors.append(f"{skill_path.relative_to(root)}: parent directory is not a research node")
            continue
        text = skill_path.read_text(encoding="utf-8")
        if "extra_local_reads:" in text:
            errors.append(f"{skill_path.relative_to(root)}: still contains legacy `extra_local_reads`")
        if skill_path.name not in {"local_entry.md", "local_wrapper.md", "local_execution.md"} and node_rel not in text:
            warnings.append(f"{skill_path.relative_to(root)}: does not explicitly mention its node path")
        for delegate in delegates_from_skill(skill_path):
            if delegate not in globals_:
                errors.append(f"{skill_path.relative_to(root)}: missing global delegate {delegate}")

    print(
        f"[skill_fit] nodes={len(nodes)} global_skills={len(globals_)} "
        f"local_skill_files={len(local_files)} node_modes={mode_counts}"
    )
    if warnings:
        for warning in warnings:
            print(f"[warn] {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1
    print("[skill_fit_ok]")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate global and node-local skill fit.")
    parser.add_argument("--root", default=str(repo_root_from_script()), help="Repository root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return validate(Path(args.root).resolve())


if __name__ == "__main__":
    sys.exit(main())
