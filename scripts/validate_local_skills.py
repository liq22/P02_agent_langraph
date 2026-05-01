#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

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
REQUIRED_ROUTING_RE = re.compile(r"(?m)^(default_delegate|routes|stop_with):")
LEGACY_MINIMAL_ENTRY_BODY = "Use implicit local-entry conventions from the registry. Keep this node-local and bounded."
PROMPT_ENTRY_REFERENCES = (
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
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
OPTIONAL_READ_LINE_RE = re.compile(r"(?m)^\d+\.\s+`([^`]+)`")


def fail(msg: str) -> None:
    print(f"[error] {msg}", file=sys.stderr)
    raise SystemExit(1)


def read_yaml(path: Path) -> dict:
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def frontmatter_block(text: str, entry: Path) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        fail(f"missing YAML frontmatter: {entry}")
    return match.group(1)


def ensure_heading_contract(
    text: str,
    path: Path,
    required_headings: tuple[str, ...],
    banned_headings: tuple[str, ...],
) -> None:
    for heading in required_headings:
        if heading not in text:
            fail(f"{path}: missing required heading `{heading}`")
    for heading in banned_headings:
        if heading in text:
            fail(f"{path}: contains banned heading `{heading}`")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate generated node-local skills.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to the current working directory.")
    return parser.parse_args()


def ensure_no_legacy_extra_reads(root: Path) -> None:
    overrides = root / "backend" / "registry" / "skill_registry" / "local_skill_overrides.yaml"
    if "extra_local_reads:" in overrides.read_text(encoding="utf-8"):
        fail("local_skill_overrides.yaml still contains legacy `extra_local_reads`")
    for skill in sorted((root / "research").glob("**/skills/*.md")):
        if "extra_local_reads:" in skill.read_text(encoding="utf-8"):
            fail(f"{skill.relative_to(root)} still contains legacy `extra_local_reads`")


def ensure_optional_reads_not_numbered(entry_text: str, node_path: str, optional_reads: list[str]) -> None:
    numbered_reads = set(OPTIONAL_READ_LINE_RE.findall(entry_text))
    for rel_path in optional_reads:
        if rel_path in numbered_reads:
            fail(f"{node_path}: optional local read `{rel_path}` must not appear in the default numbered read order")


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


def ensure_prompt_mentions(prompt_text: str, node_path: str, label: str, items: list[str]) -> None:
    missing = [item for item in items if item and item not in prompt_text]
    if missing:
        fail(f"{node_path}: research_prompt is missing {label}: {missing}")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    research = root / "research"
    if not research.exists():
        fail("research/ not found")

    overrides = load_local_skill_overrides(root)
    policy = load_node_tier_policy(root)
    ensure_no_legacy_extra_reads(root)

    for readme in research.glob("**/README.md"):
        node = readme.parent
        if not (node / "status.yaml").exists():
            continue

        node_path = node.relative_to(root).as_posix()
        mode = node_mode_for(node_path, overrides)
        research_profile = node_profile_for(node_path, overrides)
        profile = execution_profile_for(node_path, overrides)
        node_cfg = (overrides.get("nodes") or {}).get(node_path) or {}
        optional_reads = [str(item) for item in (node_cfg.get("optional_local_reads") or [])]
        required_files = required_files_for(mode, policy)
        for rel_path in required_files:
            if not (node / rel_path).is_file():
                fail(f"{node_path}: missing required `{rel_path}` for node_mode={mode}")
        if research_profile == "routing_parent" and mode != "parent":
            fail(f"{node_path}: node_profile=routing_parent requires node_mode=parent")
        if profile and mode != "execution":
            fail(f"{node_path}: execution_profile={profile} requires node_mode=execution")

        checklist_path = node / "prompts/acceptance_checklist.yaml"
        checklist = read_yaml(checklist_path)
        requires_external_review = external_review_required(checklist)
        entry = node / "skills/local_entry.md"
        text = entry.read_text(encoding="utf-8")
        frontmatter = frontmatter_block(text, entry)
        if not REQUIRED_ROUTING_RE.search(frontmatter):
            fail(f"local_entry must declare default_delegate or stop_with: {entry}")
        if LEGACY_MINIMAL_ENTRY_BODY in text:
            fail(f"local_entry still uses legacy minimal body: {entry}")

        required_entry_refs = (
            PROMPT_ENTRY_REFERENCES
            if requires_external_review
            else tuple(ref for ref in PROMPT_ENTRY_REFERENCES if ref != "prompts/review_rubric.yaml")
        )
        for ref in required_entry_refs:
            if ref not in text:
                fail(f"{node_path}: local_entry must reference `{ref}`")
        ensure_optional_reads_not_numbered(text, node_path, optional_reads)

        research_prompt = node / "prompts/research_prompt.md"
        review_rubric = node / "prompts/review_rubric.yaml"
        review_verdict = node / "review/verdict.yaml"
        research_prompt_text = research_prompt.read_text(encoding="utf-8")
        ensure_heading_contract(
            research_prompt_text,
            research_prompt,
            RESEARCH_PROMPT_REQUIRED_HEADINGS,
            RESEARCH_PROMPT_BANNED_HEADINGS,
        )
        if RESEARCH_PROMPT_DONE_LINE not in research_prompt_text:
            fail(f"{node_path}: research_prompt must declare acceptance checklist as the done-state truth")

        ensure_prompt_mentions(research_prompt_text, node_path, "node purpose", [str(node_cfg.get("purpose", "")).strip()])
        ensure_prompt_mentions(research_prompt_text, node_path, "required research questions", checklist_items(checklist, "required_questions_answered"))
        ensure_prompt_mentions(research_prompt_text, node_path, "author exit", checklist_items(checklist, "author_exit"))
        ensure_prompt_mentions(
            research_prompt_text,
            node_path,
            "minimum deliverables",
            checklist_output_tokens(checklist) + [str(item) for item in (node_cfg.get("outputs") or [])],
        )
        ensure_prompt_mentions(research_prompt_text, node_path, "quality checks", checklist_items(checklist, "quality_checks"))
        ensure_prompt_mentions(research_prompt_text, node_path, "handoff readiness", checklist_items(checklist, "handoff_ready_if"))
        ensure_prompt_mentions(research_prompt_text, node_path, "node close", checklist_items(checklist, "node_close"))
        ensure_prompt_mentions(research_prompt_text, node_path, "stop conditions", routing_stop_items(node_cfg, checklist))
        rubric_status = prompt_asset_status(checklist, "prompts/review_rubric.yaml")
        rubric_in_assets = rubric_status in {"required", "reviewer_required"}
        if requires_external_review and not rubric_in_assets:
            fail(f"{node_path}: acceptance_checklist must declare `prompts/review_rubric.yaml` as a required or reviewer_required prompt asset")

        external_review_gate = (
            checklist.get("external_review_gate") if isinstance(checklist.get("external_review_gate"), dict) else {}
        )
        if requires_external_review:
            if external_review_gate.get("reviewer_role") != "external_node_reviewer":
                fail(f"{node_path}: acceptance_checklist must route external review to `external_node_reviewer`")
            if external_review_gate.get("rubric_path") != "prompts/review_rubric.yaml":
                fail(f"{node_path}: acceptance_checklist must point external review gate at `prompts/review_rubric.yaml`")
            if external_review_gate.get("verdict_path") != "review/verdict.yaml":
                fail(f"{node_path}: acceptance_checklist must point external review gate at `review/verdict.yaml`")

            close_items = list(checklist.get("node_close") or []) + list(checklist.get("handoff_ready_if") or [])
            close_text = "\n".join(str(item) for item in close_items)
            stop_text = "\n".join(str(item) for item in (checklist.get("stop_if") or []))
            if "review/verdict.yaml" not in close_text:
                fail(f"{node_path}: node_close or handoff_ready_if must mention `review/verdict.yaml`")
            if "review/verdict.yaml" not in stop_text and "node_close" not in checklist:
                fail(f"{node_path}: stop_if must mention `review/verdict.yaml` unless node_close is declared")

            rubric_payload = read_yaml(review_rubric)
            if rubric_payload.get("reviewer_role") != "external_node_reviewer":
                fail(f"{node_path}: review_rubric must set `reviewer_role: external_node_reviewer`")
            independence = (
                rubric_payload.get("independence_requirement")
                if isinstance(rubric_payload.get("independence_requirement"), dict)
                else {}
            )
            if independence.get("reviewer_agent_must_be_distinct") is not True:
                fail(f"{node_path}: review_rubric must require a distinct reviewer agent")
            if independence.get("same_author_agent_forbidden") is not True:
                fail(f"{node_path}: review_rubric must forbid same-agent author/reviewer reuse")

            verdict_payload = read_yaml(review_verdict)
            required_verdict_fields = {
                "review_id",
                "review_complete",
                "reviewer_agent_id",
                "reviewer_skill",
                "reviewed_node_path",
                "rubric_path",
                "rubric_version",
                "overall_score",
                "overall_verdict",
                "hard_fail",
                "dimension_scores",
                "blocking_issues",
                "required_actions",
                "downstream_ready",
                "independence_confirmed",
            }
            missing_verdict_fields = sorted(required_verdict_fields - set(verdict_payload))
            if missing_verdict_fields:
                fail(f"{node_path}: review/verdict.yaml missing fields {missing_verdict_fields}")
            if verdict_payload.get("reviewer_skill") != "external_node_reviewer":
                fail(f"{node_path}: review/verdict.yaml must declare `reviewer_skill: external_node_reviewer`")

        skill_path = node / "skills/SKILL.md"
        sop_path = node / "skills/SOP.md"
        wrapper_path = node / "skills/local_wrapper.md"
        execution_path = node / "skills/local_execution.md"

        if requires_node_skill(mode):
            if "skills/SKILL.md" not in text:
                fail(f"{node_path}: local_entry must reference `skills/SKILL.md` for node_mode={mode}")
            ensure_heading_contract(
                skill_path.read_text(encoding="utf-8"),
                skill_path,
                NODE_SKILL_REQUIRED_HEADINGS,
                NODE_SKILL_BANNED_HEADINGS,
            )
        elif skill_path.exists():
            fail(f"{node_path}: unexpected skills/SKILL.md for node_mode={mode}")
        elif "skills/SKILL.md" in text:
            fail(f"{node_path}: local_entry must not reference `skills/SKILL.md` for node_mode={mode}")

        if requires_sop(mode, node_cfg):
            if "skills/SOP.md" not in text:
                fail(f"{node_path}: local_entry must reference `skills/SOP.md` for node_mode={mode}")
            ensure_heading_contract(
                sop_path.read_text(encoding="utf-8"),
                sop_path,
                NODE_SOP_REQUIRED_HEADINGS,
                NODE_SOP_BANNED_HEADINGS,
            )
        elif sop_path.exists():
            fail(f"{node_path}: unexpected skills/SOP.md for node_mode={mode}")
        elif "skills/SOP.md" in text:
            fail(f"{node_path}: local_entry must not reference `skills/SOP.md` for node_mode={mode}")

        binder_any_of = binder_any_of_for(mode, policy)
        if binder_any_of:
            if not any((node / rel_path).is_file() for rel_path in binder_any_of):
                fail(f"{node_path}: execution node is missing a binder {binder_any_of}")
            if wrapper_path.exists() and "skills/local_wrapper.md" not in text:
                fail(f"{node_path}: local_entry must reference `skills/local_wrapper.md` when wrapper exists")
            if execution_path.exists() and "skills/local_execution.md" not in text:
                fail(f"{node_path}: local_entry must reference `skills/local_execution.md` when local execution exists")
        else:
            if execution_path.exists():
                fail(f"{node_path}: unexpected skills/local_execution.md for node_mode={mode}")

        if profile == "result_synthesis":
            if not execution_path.exists():
                fail(f"{node_path}: result_synthesis nodes must bind `skills/local_execution.md`")
            execution_text = execution_path.read_text(encoding="utf-8")
            if "execution contract" in execution_text.lower():
                fail(f"{node_path}: result_synthesis local_execution must not mention execution contract")
        if profile == "experiment_execution" and not (wrapper_path.exists() or execution_path.exists()):
            fail(f"{node_path}: experiment_execution nodes must bind a local wrapper or local execution file")

        for line in frontmatter.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or ":" not in stripped:
                continue
            field = stripped.split(":", 1)[0]
            if field in BANNED_LOCAL_ENTRY_FIELDS:
                fail(f"banned repeated field `{field}:` found in {entry}")

    print("[ok] local skills validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
