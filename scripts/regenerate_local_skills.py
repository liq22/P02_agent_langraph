#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import re

import yaml

from node_tier import (
    allows_execution,
    allows_wrapper,
    binder_any_of_for,
    declared_execution,
    declared_wrapper,
    execution_profile_for,
    load_local_skill_overrides,
    load_node_tier_policy,
    node_mode_for,
    node_profile_for,
    requires_node_skill,
    requires_sop,
)


PHASE_USE_WHEN = {
    "P0": [
        "当前节点负责问题定义、gap 收敛、innovation 边界或约束澄清。",
        "需要把背景、问题、aim、impact 或 feasibility 压成当前节点可交付、可反驳的研究判断。",
    ],
    "P1": [
        "当前节点负责实验设计、协议、仓库蓝图、可复现约束或执行准备。",
        "需要把方法、接口、工件或 contract 组织成后续执行可用的局部资产。",
    ],
    "P2": [
        "当前节点负责论文写作、章节起草、结构化改写、形式检查或导出同步。",
        "需要把 claim、evidence、术语与版式要求压到当前节点的正文或导出目标里。",
    ],
    "P3": [
        "当前节点负责 review、critique、blocking issue 发现或 revision planning。",
        "需要把问题转成当前节点内可执行、可验证的修订动作。",
    ],
    "P4": [
        "当前节点负责审稿意见收集、问题映射、逐点回复、证据绑定或再投稿打包。",
        "需要把 comment、evidence、change location 和 response package 对齐到当前节点。",
    ],
}

PHASE_WORKFLOW = {
    "P0": [
        "先压缩问题背景、已有方法簇和核心 gap，不把材料堆砌当结论。",
        "把目标、预期结果、impact、risk/feasibility 明确成 reviewer 可检查的表述。",
        "输出当前节点需要的 manuscript/map 资产，并为下游问题或计划节点准备 handoff。",
    ],
    "P1": [
        "先确认协议、接口、artifact、metric、baseline 与 reproducibility 约束。",
        "把当前节点要产出的 contract、map、registry 或 execution input 压缩到本地工件。",
        "只在 contract/inputs 完整时进入 wrapper/execution；否则停在 contract-prep 或 protocol-prep。",
    ],
    "P2": [
        "先确认本段 one-sentence contribution、claim-evidence 对齐和术语一致性。",
        "完成一次受控写作增量：起草、重写、压缩、格式检查或导出同步。",
        "把结果限制在当前章节、图表、导出资产或形式检查报告，不扩成整篇论文总控。",
    ],
    "P3": [
        "读取最小必要的 critique/review 输入，把问题原子化为 issue、severity、evidence location 和 proposed action。",
        "把评论压成 digest、review round plan 或 revision action map。",
        "只交付当前节点内的 critique/revision 工件，不把 review 扩成 repo-global loop。",
    ],
    "P4": [
        "读取 comment、mapping、evidence 与 manuscript change location，先过 coverage/provenance gate。",
        "逐点生成 response、evidence map、coverage report 或 resubmission asset。",
        "确保每条回复都能落到具体 comment、具体 evidence 和具体改动位置。",
    ],
}

PHASE_BOUNDARIES = {
    "P0": [
        "不把想法筛选扩成无界文献检索或全局 proposal 总控。",
        "不在当前节点里替代 P1/P2/P3/P4 的执行逻辑。",
    ],
    "P1": [
        "不在 contract 未齐时直接猜 execution 行为。",
        "不把当前节点扩成 repo-global experiment orchestrator。",
    ],
    "P2": [
        "不把当前节点扩成整篇论文统一重写器。",
        "不在无证据时维持核心 claim。",
    ],
    "P3": [
        "不把作者辩护当成独立评审结论。",
        "不把当前 review 节点扩成多节点总 review engine。",
    ],
    "P4": [
        "不承诺未批准的实验、数字、引用或改动。",
        "不把局部回复节点扩成整套 submission manager。",
    ],
}

PHASE_PROMPT_STANDARDS = {
    "P0": [
        "优先把 significance、gap、aims、expected outcomes 与 impact 压成 reviewer 可快速判断的表达。",
        "避免空泛承诺，目标、阶段与风险分支都要可检验。",
    ],
    "P1": [
        "优先把 protocol、metric、baseline、artifact 边界与 reproducibility 约束说清。",
        "只有 contract / inputs ready 时才进入执行层，否则停在 prep / handoff。",
    ],
    "P2": [
        "优先保证 claim-evidence 对齐、术语一致与章节边界清晰。",
        "把本轮约束压在当前章节、图表或导出资产，不扩成整篇论文总控。",
    ],
    "P3": [
        "优先把 critique 压成可执行 action，而不是继续堆评论。",
        "severity、evidence location 与 next action 要能对账。",
    ],
    "P4": [
        "优先保证 point-by-point coverage、evidence 绑定与 change location 可追踪。",
        "不承诺正文里不存在的改动，也不把回复写成泛泛解释。",
    ],
}

BASE_PROMPT_ASSET_PATHS = {"prompts/research_prompt.md", "prompts/acceptance_checklist.yaml"}
RESEARCH_PROMPT_DONE_LINE = "完成定义以 `prompts/acceptance_checklist.yaml` 为准。"
CANONICAL_ARTIFACT_PATH_ALIASES = {
    "coverage_check_report.md": "artifacts/coverage_check_report.yaml",
    "artifacts/coverage_check_report.md": "artifacts/coverage_check_report.yaml",
}
REVIEW_RUBRIC_PATH = "prompts/review_rubric.yaml"
REVIEW_VERDICT_PATH = "review/verdict.yaml"
REVIEW_RESPONSE_PATH = "review/response.yaml"
REVIEW_RUBRIC_VERSION = "nature_node_review_v1"
REVIEWER_SKILL_ID = "external_node_reviewer"
REVIEWER_ROLE = "external_node_reviewer"
NATURE_RUBRIC_PATH = Path("test") / "NATURE_LEVEL_NODE_RUBRIC.md"
REFERENCE_GUIDANCE_PATH = Path("backend") / "registry" / "skill_registry" / "reference_guidance_map.yaml"
NATURE_NODE_ROW_RE = re.compile(r"^\| `(?P<path>research/[^`]+)` \| (?P<criterion>.+?) \| (?P<blocking>.+?) \|$", re.MULTILINE)
NATURE_SCORING_DIMENSIONS = [
    {
        "name": "originality_novelty",
        "weight": 20,
        "reviewer_standard": "Clear advance over strong prior work, not incremental repackaging.",
    },
    {
        "name": "scientific_importance",
        "weight": 20,
        "reviewer_standard": "Addresses a field-level scientific or engineering bottleneck.",
    },
    {
        "name": "evidence_technical_soundness",
        "weight": 25,
        "reviewer_standard": "Claims are supported by robust data, baselines, uncertainty, and controls.",
    },
    {
        "name": "reproducibility_transparency",
        "weight": 15,
        "reviewer_standard": "Data, code, protocol, config, and limitations are inspectable.",
    },
    {
        "name": "broad_interest_story_clarity",
        "weight": 10,
        "reviewer_standard": "A scientist outside the narrow subfield can understand why it matters.",
    },
    {
        "name": "review_robustness",
        "weight": 10,
        "reviewer_standard": "Anticipates alternative explanations, negative results, and reviewer attacks.",
    },
]
NATURE_VERDICT_THRESHOLDS = {
    "nature_ready_candidate_min_score": 90,
    "strong_specialist_min_score": 80,
    "revise_min_score": 60,
    "block_below_score": 60,
    "downstream_pass_min_score": 80,
}
NATURE_HARD_FAILS = [
    "Unsupported central claim.",
    "Material citation is missing, unverified, or mismatched with the claim it supports.",
    "Figure lacks provenance, claim mapping, or evidence mapping.",
    "Missing reproducibility path for data, code, protocol, or configuration.",
    "Hidden negative result or omitted limitation.",
    "Graph, Canvas, or dashboard treated as research truth.",
    "Unbounded autonomous loop or undeclared handoff.",
    "Reviewer-critical concern not mapped to evidence or revision action.",
]
PHASE_REVIEWER_LENSES = {
    "P0": [
        "重点检查问题是否真实存在、gap 是否具体、novelty 是否相对强基线而成立。",
        "重点检查目标、预期结果、impact、risk、resource 假设是否可检验。",
    ],
    "P1": [
        "重点检查证据链是否可执行、可复现、可审计，而不是只有方法叙述。",
        "重点检查 protocol、metric、baseline、artifact、failure interpretation 是否闭环。",
    ],
    "P2": [
        "重点检查 claim-evidence 对齐、术语一致、方法复现性和讨论中的限制承认。",
        "重点检查写作是否压着证据走，而不是靠修辞放大结论。",
    ],
    "P3": [
        "重点检查 critique 是否独立、具体、可执行，并且不把作者辩护当评审结论。",
        "重点检查 severity、evidence gap、next action 是否可对账。",
    ],
    "P4": [
        "重点检查逐点回复是否直接、可核对、能定位正文改动和证据位置。",
        "重点检查 coverage 是否完整，是否存在 evasive response 或无证据承诺。",
    ],
}
PROFILE_REVIEW_LENSES = {
    "experiment_execution": [
        "这是 execution-tier 实验节点：必须重点检查 execution contract、metric parser、budget 与 editable scope。",
        "任何 `contract_mode != executable` 或 contract 字段残缺都应视为 reviewer-blocking issue。",
    ],
    "result_synthesis": [
        "这是 result-synthesis 节点：必须重点检查结果归类是否忠实于 ledger，而不是替实验补写结论。",
        "任何把 unclear evidence 写成 supported claim 的行为都应视为 reviewer-blocking issue。",
    ],
}
DEFAULT_REVIEW_VERDICT_DIMENSIONS = {
    "originality_novelty": None,
    "scientific_importance": None,
    "evidence_technical_soundness": None,
    "reproducibility_transparency": None,
    "broad_interest_story_clarity": None,
    "review_robustness": None,
}
_REFERENCE_GUIDANCE_CACHE: dict[str, dict] = {}
_LOCAL_OVERRIDES_CACHE: dict[str, dict] = {}
EXTERNAL_REVIEW_HANDOFF_ITEMS = [
    "独立 reviewer agent 已生成 `review/verdict.yaml`",
    "`review/verdict.yaml` 中 `review_complete == true`",
    "`review/verdict.yaml` 中 `overall_verdict == pass`",
    "`review/verdict.yaml` 中 `hard_fail == false`",
    "`review/verdict.yaml` 中 `independence_confirmed == true`",
]
EXTERNAL_REVIEW_STOP_ITEMS = [
    "缺少独立 reviewer verdict (`review/verdict.yaml`)",
    "独立 reviewer verdict 尚未完成 (`review_complete != true`)",
    "独立 reviewer 判定为 `revise` 或 `block`",
    "独立 reviewer 提出 hard fail 且未关闭",
]
_NATURE_NODE_ROW_CACHE: dict[str, dict[str, dict[str, str]]] = {}

SCOPE_WORKFLOW = [
    "先判断子节点 readiness、blocking edge 和当前 scope 节点是否只需要协调状态更新。",
    "只维护当前 scope 节点自己的协调类资产与 handoff，不替子节点越权产出正文或实验结论。",
    "当子节点已有明确 ready frontier 时，优先 route child first，而不是在 scope 壳层消耗预算。",
]

SCOPE_BOUNDARIES = [
    "不把父节点当成第二个正文仓库。",
    "不跳过子节点 contract 直接在父节点内做深层执行。",
]


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def remove_if_exists(path: Path) -> None:
    if path.exists():
        path.unlink()


def read_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def reference_guidance(root: Path) -> dict:
    cache_key = str(root)
    if cache_key not in _REFERENCE_GUIDANCE_CACHE:
        _REFERENCE_GUIDANCE_CACHE[cache_key] = read_yaml(root / REFERENCE_GUIDANCE_PATH)
    return _REFERENCE_GUIDANCE_CACHE[cache_key]


def local_overrides(root: Path) -> dict:
    cache_key = str(root)
    if cache_key not in _LOCAL_OVERRIDES_CACHE:
        _LOCAL_OVERRIDES_CACHE[cache_key] = load_local_skill_overrides(root)
    return _LOCAL_OVERRIDES_CACHE[cache_key]


def guidance_section(root: Path, key: str) -> dict:
    section = reference_guidance(root).get(key)
    return section if isinstance(section, dict) else {}


def phase_lens(root: Path, phase: str) -> dict:
    lenses = guidance_section(root, "phase_lenses")
    lens = lenses.get(phase)
    return lens if isinstance(lens, dict) else {}


def phase_guidance_items(root: Path, phase: str, key: str, fallback: list[str] | None = None) -> list[str]:
    value = phase_lens(root, phase).get(key)
    if isinstance(value, list):
        return uniq([str(item).strip() for item in value])
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return list(fallback or [])


def phase_researcher_role(root: Path, phase: str) -> str:
    role = phase_lens(root, phase).get("researcher_role")
    if isinstance(role, str) and role.strip():
        return role.strip()
    return {
        "P0": "problem-formulation PI",
        "P1": "experiment lead",
        "P2": "top-conference paper author",
        "P3": "adversarial external reviewer",
        "P4": "responsible rebuttal author",
    }.get(phase, "node-local researcher")


def canonical_skill_lens(root: Path, skill_id: str) -> list[str]:
    lenses = guidance_section(root, "canonical_skill_lenses")
    value = lenses.get(skill_id)
    if isinstance(value, list):
        return uniq([str(item).strip() for item in value])
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def delegate_skill_ids(cfg: dict) -> list[str]:
    out: list[str] = []

    def collect(value: object) -> None:
        if isinstance(value, dict) and value.get("canonical_global_skill"):
            out.append(str(value["canonical_global_skill"]))

    collect(cfg.get("default_delegate"))
    for rule in cfg.get("decision_rule") or []:
        if isinstance(rule, dict):
            collect(rule.get("then"))
    return uniq(out)


def figure_manifest_path(root: Path) -> str:
    policies = guidance_section(root, "policies")
    figure = policies.get("figure") if isinstance(policies.get("figure"), dict) else {}
    manifest = figure.get("manifest_path")
    return str(manifest) if manifest else "artifacts/figure_manifest.yaml"


def node_profile_defaults(root: Path, profile: str) -> dict:
    defaults = local_overrides(root).get("profile_defaults") or {}
    value = defaults.get(profile)
    return value if isinstance(value, dict) else {}


def phase_profile_defaults(root: Path, phase: str, profile: str) -> dict:
    defaults = local_overrides(root).get("phase_profile_defaults") or {}
    phase_defaults = defaults.get(phase)
    if not isinstance(phase_defaults, dict):
        return {}
    value = phase_defaults.get(profile)
    return value if isinstance(value, dict) else {}


def effective_cfg_value(root: Path, cfg: dict, phase: str, profile: str, key: str, fallback: object | None = None) -> object:
    if key in cfg:
        return cfg[key]
    phase_value = phase_profile_defaults(root, phase, profile).get(key)
    if phase_value is not None:
        return phase_value
    profile_value = node_profile_defaults(root, profile).get(key)
    if profile_value is not None:
        return profile_value
    return fallback


def effective_list(root: Path, cfg: dict, phase: str, profile: str, key: str) -> list[str]:
    value = effective_cfg_value(root, cfg, phase, profile, key, [])
    if isinstance(value, list):
        return uniq([str(item).strip() for item in value])
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def effective_dict(root: Path, cfg: dict, phase: str, profile: str, key: str) -> dict:
    value = effective_cfg_value(root, cfg, phase, profile, key, {})
    return value if isinstance(value, dict) else {}


def condition_items(mapping: dict) -> list[str]:
    items: list[str] = []
    for key, value in mapping.items():
        if isinstance(value, bool):
            items.append(f"{key}: {str(value).lower()}")
        else:
            items.append(f"{key}: {value}")
    return items


def ensure_checklist_output(checklist: dict, path_text: str) -> None:
    items = checklist.get("required_outputs")
    if not isinstance(items, list):
        items = []
        checklist["required_outputs"] = items
    for item in items:
        if isinstance(item, dict) and str(item.get("path", "")).strip() == path_text:
            return
        if isinstance(item, str) and item.strip() == path_text:
            return
    items.append({"path": path_text, "description": "profile-required local artifact"})


def canonical_artifact_path(path_text: str) -> str:
    return CANONICAL_ARTIFACT_PATH_ALIASES.get(str(path_text).strip(), str(path_text).strip())


def normalize_checklist_artifact_paths(checklist: dict) -> None:
    items = checklist.get("required_outputs")
    if not isinstance(items, list):
        return
    deduped: list[object] = []
    seen_paths: set[str] = set()
    for item in items:
        if isinstance(item, dict) and item.get("path"):
            item["path"] = canonical_artifact_path(str(item["path"]))
            path = str(item["path"])
            if path in seen_paths:
                continue
            seen_paths.add(path)
            deduped.append(item)
        elif isinstance(item, str):
            path = canonical_artifact_path(item)
            if path in seen_paths:
                continue
            seen_paths.add(path)
            deduped.append(path)
        else:
            deduped.append(item)
    checklist["required_outputs"] = deduped


def fm_block(data: dict) -> str:
    return "---\n" + yaml.safe_dump(data, allow_unicode=True, sort_keys=False).strip() + "\n---\n"


def infer_phase(path: str) -> str:
    match = re.search(r"/(P\d+)_", path)
    return match.group(1) if match else "P9"


def infer_kind(root: Path, path: str) -> str:
    node_dir = root / path
    for child in node_dir.iterdir():
        if child.is_dir() and (child / "README.md").is_file() and (child / "status.yaml").is_file():
            return "scope"
    return "leaf"


def checklist_for(root: Path, path: str) -> dict:
    return read_yaml(root / path / "prompts" / "acceptance_checklist.yaml")


def has_standards(root: Path, path: str) -> bool:
    return (root / path / "prompts" / "standards.md").exists()


def uniq(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def checklist_items(checklist: dict, key: str, field: str = "item") -> list[str]:
    items = checklist.get(key) or []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            value = item.get(field)
            if not value and field != "path":
                value = item.get("path")
            if not value and field != "note":
                value = item.get("note")
            if value:
                out.append(str(value))
        elif isinstance(item, str):
            out.append(item)
    return uniq(out)


def checklist_output_items(checklist: dict) -> list[str]:
    items = checklist.get("required_outputs") or []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict):
            path = str(item.get("path", "")).strip()
            desc = str(item.get("description", "")).strip()
            if path and desc and desc != "<待填写>":
                out.append(f"{path} ({desc})")
            elif path:
                out.append(path)
        elif isinstance(item, str):
            out.append(item)
    return uniq(out)


def output_item_key(value: str) -> str:
    text = str(value).strip()
    for marker in (" (", "（"):
        if marker in text:
            return text.split(marker, 1)[0].strip()
    return text


def prompt_assets(checklist: dict) -> list[str]:
    items = checklist.get("prompt_assets") or []
    out: list[str] = []
    for item in items:
        if isinstance(item, dict) and item.get("path"):
            status = item.get("status")
            label = f"{item['path']} [{status}]" if status else str(item["path"])
            out.append(label)
    return uniq(out)


def checklist_prompt_asset_paths(root: Path, path: str, checklist: dict) -> list[str]:
    out: list[str] = []
    for item in checklist.get("prompt_assets") or []:
        if not isinstance(item, dict) or not item.get("path"):
            continue
        rel_path = str(item["path"])
        if rel_path in BASE_PROMPT_ASSET_PATHS:
            continue
        if (root / path / rel_path).is_file():
            out.append(rel_path)
    return uniq(out)


def nature_node_rows(root: Path) -> dict[str, dict[str, str]]:
    cache_key = str(root)
    if cache_key in _NATURE_NODE_ROW_CACHE:
        return _NATURE_NODE_ROW_CACHE[cache_key]
    rubric = root / NATURE_RUBRIC_PATH
    rows: dict[str, dict[str, str]] = {}
    if rubric.is_file():
        text = rubric.read_text(encoding="utf-8")
        for match in NATURE_NODE_ROW_RE.finditer(text):
            rows[match.group("path")] = {
                "criterion": match.group("criterion").strip(),
                "blocking_failure": match.group("blocking").strip(),
            }
    _NATURE_NODE_ROW_CACHE[cache_key] = rows
    return rows


def fallback_nature_node_criterion(phase: str, kind: str, mode: str, profile: str | None) -> str:
    if kind == "scope":
        return "Child leaves form a coherent bounded subtree with explicit handoff, review gate, and no shell-layer overreach."
    if profile == "experiment_execution":
        return "Executable evidence path is explicit: contract, metric, budget, failure signal, and editable scope are all reviewer-inspectable."
    if profile == "result_synthesis":
        return "Result registry distinguishes supported, unsupported, and unclear claims without inflating conclusions beyond the ledger."
    if phase == "P0":
        return "Problem, gap, novelty, route, and feasibility are explicit enough for a skeptical reviewer to test."
    if phase == "P1":
        return "Protocol, artifact, and reproducibility path are explicit enough for a reviewer to rerun or audit the evidence chain."
    if phase == "P2":
        return "Claims, methods, and discussion are evidence-linked and reproducible under reviewer scrutiny."
    if phase == "P3":
        return "Critique is independent, severity-ranked, and translated into evidence-backed revision actions."
    if phase == "P4":
        return "Every response is point-by-point, evidence-backed, and mapped to an exact manuscript change."
    return "Node output is reviewer-auditable, bounded, and evidence-led."


def fallback_nature_blocking_failure(phase: str, kind: str, profile: str | None) -> str:
    if kind == "scope":
        return "Parent shell advances without routing to ready children or without preserving bounded review gates."
    if profile == "experiment_execution":
        return "Execution path is claimed ready without a valid executable contract."
    if profile == "result_synthesis":
        return "Result synthesis writes conclusions not anchored in the experiment ledger."
    if phase == "P0":
        return "Gap, novelty, or feasibility is asserted without concrete support."
    if phase == "P1":
        return "Reproducibility path or evidence contract is missing."
    if phase == "P2":
        return "Central manuscript claim is not traceable to data, figure, table, or method detail."
    if phase == "P3":
        return "Critique lacks severity, evidence mapping, or actionable revision target."
    if phase == "P4":
        return "A reviewer concern is answered evasively or without change/evidence location."
    return "Reviewer cannot verify what claim is made, what evidence exists, or what blocks handoff."


def node_rubric_row(root: Path, path: str, phase: str, kind: str, mode: str, profile: str | None) -> dict[str, str]:
    rows = nature_node_rows(root)
    row = rows.get(path)
    if row:
        return row
    return {
        "criterion": fallback_nature_node_criterion(phase, kind, mode, profile),
        "blocking_failure": fallback_nature_blocking_failure(phase, kind, profile),
    }


def ensure_prompt_asset(checklist: dict, rel_path: str, status: str) -> None:
    items = checklist.get("prompt_assets")
    if not isinstance(items, list):
        items = []
        checklist["prompt_assets"] = items
    for item in items:
        if isinstance(item, dict) and str(item.get("path", "")).strip() == rel_path:
            item["status"] = status
            return
    items.append({"path": rel_path, "status": status})


def ensure_checklist_item(checklist: dict, key: str, item_text: str) -> None:
    items = checklist.get(key)
    if not isinstance(items, list):
        items = []
        checklist[key] = items
    for item in items:
        if isinstance(item, dict) and str(item.get("item", "")).strip() == item_text:
            if "status" not in item:
                item["status"] = "pending"
            return
        if isinstance(item, str) and item.strip() == item_text:
            return
    items.append({"item": item_text, "status": "pending"})


def ensure_quality_check(checklist: dict, item_text: str) -> None:
    ensure_checklist_item(checklist, "quality_checks", item_text)


def update_checklist_with_profile_contract(root: Path, cfg: dict, checklist: dict, mode: str, node_profile: str) -> dict:
    checklist = dict(checklist)
    normalize_checklist_artifact_paths(checklist)
    phase = str(checklist.get("phase") or "P9")
    for artifact in effective_list(root, cfg, phase, node_profile, "required_artifacts"):
        ensure_checklist_output(checklist, artifact)
    for item in condition_items(effective_dict(root, cfg, phase, node_profile, "author_exit_if")):
        ensure_checklist_item(checklist, "author_exit", item)
    for item in condition_items(effective_dict(root, cfg, phase, node_profile, "node_close_if")):
        ensure_checklist_item(checklist, "node_close", item)
    for item in effective_list(root, cfg, phase, node_profile, "blocking_failure_modes"):
        ensure_checklist_item(checklist, "stop_if", item)
    if node_profile == "hard_gate":
        ensure_quality_check(
            checklist,
            "hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。",
        )
    if mode == "parent":
        ensure_quality_check(checklist, "父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。")
    return checklist


def review_required_inputs(root: Path, path: str, cfg: dict, checklist: dict, mode: str) -> list[str]:
    inputs = [
        "README.md",
        "status.yaml",
        "prompts/research_prompt.md",
        "prompts/acceptance_checklist.yaml",
        REVIEW_RUBRIC_PATH,
    ]
    if has_standards(root, path):
        inputs.append("prompts/standards.md")
    inputs.extend(required_local_reads(cfg))
    inputs.extend(optional_local_reads(cfg))
    inputs.extend(checklist_items(checklist, "required_outputs", "path"))
    return uniq(inputs)


def update_checklist_with_external_review_gate(root: Path, path: str, cfg: dict, checklist: dict, mode: str) -> dict:
    checklist = dict(checklist)
    ensure_prompt_asset(checklist, REVIEW_RUBRIC_PATH, "required")
    for item in EXTERNAL_REVIEW_HANDOFF_ITEMS:
        ensure_checklist_item(checklist, "handoff_ready_if", item)
    for item in EXTERNAL_REVIEW_STOP_ITEMS:
        ensure_checklist_item(checklist, "stop_if", item)
    ensure_quality_check(checklist, "节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。")
    checklist["external_review_gate"] = {
        "required": True,
        "reviewer_role": REVIEWER_ROLE,
        "reviewer_agent_must_be_distinct": True,
        "rubric_path": REVIEW_RUBRIC_PATH,
        "verdict_path": REVIEW_VERDICT_PATH,
        "pass_condition": {
            "review_complete": True,
            "overall_verdict": "pass",
            "hard_fail": False,
            "independence_confirmed": True,
        },
        "required_reviewer_inputs": review_required_inputs(root, path, cfg, checklist, mode),
    }
    return checklist


def external_review_required(cfg: dict, checklist: dict) -> bool:
    gate = checklist.get("external_review_gate")
    if isinstance(gate, dict):
        return gate.get("required") is True
    return cfg.get("external_review_gate_required") is True


def review_rubric_phase_lenses(root: Path, phase: str, profile: str | None) -> list[str]:
    items = phase_guidance_items(root, phase, "review_lenses", PHASE_REVIEWER_LENSES.get(phase, []))
    items.extend(phase_guidance_items(root, phase, "quality_gates"))
    if profile:
        items.extend(PROFILE_REVIEW_LENSES.get(profile, []))
    return uniq(items)


def generate_review_rubric(root: Path, path: str, cfg: dict, checklist: dict, mode: str, profile: str | None) -> str:
    phase = str(checklist.get("phase") or infer_phase(path))
    kind = "scope" if mode == "parent" else str(checklist.get("node_kind") or infer_kind(root, path))
    node_profile = node_profile_for(path, local_overrides(root))
    row = node_rubric_row(root, path, phase, kind, mode, profile)
    payload = {
        "rubric_version": REVIEW_RUBRIC_VERSION,
        "node_id": str(checklist.get("node_id") or path.replace("/", "::")),
        "node_path": path,
        "phase": phase,
        "node_kind": kind,
        "node_mode": mode,
        "node_profile": node_profile,
        "execution_profile": profile or "<none>",
        "reviewer_role": REVIEWER_ROLE,
        "independence_requirement": {
            "reviewer_agent_must_be_distinct": True,
            "same_author_agent_forbidden": True,
            "required_artifact": REVIEW_VERDICT_PATH,
        },
        "scoring_dimensions": NATURE_SCORING_DIMENSIONS,
        "verdict_thresholds": NATURE_VERDICT_THRESHOLDS,
        "hard_fail_conditions": NATURE_HARD_FAILS,
        "phase_review_lenses": review_rubric_phase_lenses(root, phase, profile),
        "node_level_5_criterion": row["criterion"],
        "node_blocking_failure": row["blocking_failure"],
        "required_reviewer_inputs": review_required_inputs(root, path, cfg, checklist, mode),
        "required_review_outputs": [
            "review/AI_001.md",
            REVIEW_VERDICT_PATH,
            REVIEW_RESPONSE_PATH,
        ],
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).rstrip() + "\n"


def default_review_response_template() -> str:
    payload = {
        "responses": [
            {"comment_id": "AI-001", "responded": False, "note": ""},
            {"comment_id": "H-001", "responded": False, "note": ""},
        ]
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False).rstrip() + "\n"


def default_review_verdict_payload(path: str) -> dict:
    return {
        "review_id": "EXTERNAL-AI-001",
        "review_complete": False,
        "reviewer_agent_id": "<pending-distinct-agent>",
        "reviewer_skill": REVIEWER_SKILL_ID,
        "reviewed_node_path": path,
        "rubric_path": REVIEW_RUBRIC_PATH,
        "rubric_version": REVIEW_RUBRIC_VERSION,
        "overall_score": None,
        "overall_verdict": "revise",
        "hard_fail": False,
        "dimension_scores": dict(DEFAULT_REVIEW_VERDICT_DIMENSIONS),
        "blocking_issues": [],
        "required_actions": [],
        "downstream_ready": False,
        "independence_confirmed": False,
    }


def ensure_review_assets(root: Path, path: str) -> None:
    review_dir = root / path / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    ai_review = review_dir / "AI_001.md"
    if not ai_review.exists():
        ai_review.write_text("# AI_001\n\n- comment_id: AI-001\n- status: unresolved\n- comment: 待补充\n", encoding="utf-8")
    response = review_dir / "response.yaml"
    if not response.exists():
        response.write_text(default_review_response_template(), encoding="utf-8")
    verdict = review_dir / "verdict.yaml"
    if not verdict.exists():
        verdict.write_text(
            yaml.safe_dump(default_review_verdict_payload(path), allow_unicode=True, sort_keys=False).rstrip() + "\n",
            encoding="utf-8",
        )


def prompt_read_paths(root: Path, path: str, checklist: dict) -> list[str]:
    reads = ["prompts/research_prompt.md", "prompts/acceptance_checklist.yaml"]
    reads.extend(checklist_prompt_asset_paths(root, path, checklist))
    if has_standards(root, path):
        reads.append("prompts/standards.md")
    return uniq(reads)


def format_delegate(delegate: dict | str | None) -> str:
    if delegate is None:
        return "stop without a deeper worker"
    if isinstance(delegate, str):
        return delegate
    if delegate.get("canonical_global_skill"):
        return f"delegate to canonical worker `{delegate['canonical_global_skill']}`"
    if delegate.get("local_wrapper_skill"):
        return f"delegate to local wrapper `{delegate['local_wrapper_skill']}`"
    if delegate.get("local_execution_skill"):
        return f"delegate to local execution `{delegate['local_execution_skill']}`"
    if delegate.get("local_action_only"):
        return "stay in local action only mode"
    return yaml.safe_dump(delegate, allow_unicode=True, sort_keys=False).strip()


def cfg_reads(cfg: dict, key: str) -> list[str]:
    return uniq([str(item) for item in (cfg.get(key) or [])])


def required_local_reads(cfg: dict) -> list[str]:
    return cfg_reads(cfg, "required_local_reads")


def optional_local_reads(cfg: dict) -> list[str]:
    return cfg_reads(cfg, "optional_local_reads")


def ensure_no_legacy_extra_reads(label: str, cfg: dict) -> None:
    if "extra_local_reads" in cfg:
        raise RuntimeError(f"{label}: legacy `extra_local_reads` is no longer supported")


def delegate_lines(cfg: dict, wrapper_present: bool, execution_present: bool) -> list[str]:
    lines: list[str] = []
    default_delegate = cfg.get("default_delegate")
    if default_delegate:
        lines.append(f"Default path: {format_delegate(default_delegate)}.")
    for rule in cfg.get("decision_rule") or []:
        when = rule.get("when", "condition")
        if "then" in rule:
            lines.append(f"When `{when}`, {format_delegate(rule.get('then'))}.")
        elif "stop_with" in rule:
            lines.append(f"When `{when}`, stop with `{rule['stop_with']}`.")
    if wrapper_present:
        lines.append("This node binds a local wrapper; enter `skills/local_wrapper.md` only after the tier-required local stack has been loaded.")
    if execution_present:
        lines.append("This node binds local execution; enter `skills/local_execution.md` only after the tier-required local stack has been loaded.")
    return lines


def routing_stop_items(cfg: dict, checklist: dict) -> list[str]:
    items = checklist_items(checklist, "stop_if")
    if cfg.get("stop_with"):
        items.append(str(cfg["stop_with"]))
    for rule in cfg.get("decision_rule") or []:
        if "stop_with" in rule:
            items.append(str(rule["stop_with"]))
    return uniq(items)


def extra_prompt_assets(root: Path, path: str, checklist: dict) -> list[str]:
    return [item for item in prompt_read_paths(root, path, checklist) if item not in BASE_PROMPT_ASSET_PATHS]


def prompt_input_priority(root: Path, path: str, cfg: dict, checklist: dict) -> list[str]:
    items = [
        "先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。",
        "把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。",
    ]
    adjunct_prompts = extra_prompt_assets(root, path, checklist)
    if adjunct_prompts:
        items.append(
            "若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取："
            + ", ".join(f"`{item}`" for item in adjunct_prompts)
            + "。"
        )
    must_reads = required_local_reads(cfg)
    if must_reads:
        items.append(
            "默认必须补齐的 node-local 输入："
            + ", ".join(f"`{item}`" for item in must_reads)
            + "。"
        )
    maybe_reads = optional_local_reads(cfg)
    if maybe_reads:
        items.append(
            "仅当这些补充上下文会改变当前有界轮次时，再按需读取："
            + ", ".join(f"`{item}`" for item in maybe_reads)
            + "。"
        )
    if not must_reads and not maybe_reads:
        items.append("没有额外输入时，不主动扩张读取范围。")
    return items


def prompt_phase_constraints(
    root: Path,
    path: str,
    cfg: dict,
    phase: str,
    kind: str,
    mode: str,
    profile: str | None,
    wrapper_present: bool,
    execution_present: bool,
) -> list[str]:
    if profile == "experiment_execution":
        items = [
            "优先把 execution contract、metric、budget、artifact 边界与 baseline-first 纪律说清。",
            "只有 contract_mode 为 `executable` 时才进入 wrapper / worker；否则停在 prep / handoff。",
        ]
    elif profile == "result_synthesis":
        items = [
            "优先把 results ledger、evidence location、claim boundary 与不确定性说清。",
            "先压 registry / hypothesis status，再决定是否补最小正文摘要。",
        ]
    else:
        items = phase_guidance_items(
            root,
            phase,
            "prompt_standards",
            PHASE_PROMPT_STANDARDS.get(phase, ["优先把本轮约束压到当前节点，而不是扩成 repo-global task。"]),
        )
    if has_standards(root, path):
        items.append("若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。")
    if kind == "scope":
        items.append("父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。")
    if mode == "standard":
        items.append("本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。")
    if mode == "execution" and profile != "result_synthesis":
        items.append("只有 contract / required inputs ready 时才进入 binder；否则只做 preparation 或 handoff。")
    if profile == "experiment_execution":
        items.append("这是 experiment execution node：execution contract 是 gate，baseline/单变量尝试/keep-discard 要留在本地 ledger。")
    if profile == "result_synthesis":
        items.append("这是 result synthesis node：declared results ledger 是主输入，先压 registry/status，再决定可写入正文的最小摘要。")
    if wrapper_present:
        items.append("`skills/local_wrapper.md` 只负责本地 IO 绑定，不重新定义节点语义。")
    if execution_present:
        items.append("`skills/local_execution.md` 只负责一轮本地执行，不承担路由职责。")
    items.extend(str(item) for item in (cfg.get("coordination_notes") or []))
    return uniq(items)


def node_role_items(cfg: dict, kind: str) -> list[str]:
    items = [str(cfg["purpose"]).strip()]
    if kind == "scope":
        items.append("这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。")
    else:
        items.append("这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。")
    return uniq(items)


def prompt_boundaries(
    phase: str,
    kind: str,
    profile: str | None,
    wrapper_present: bool,
    execution_present: bool,
) -> list[str]:
    items = list(profile_boundaries(profile) or node_boundaries(phase, kind))
    if wrapper_present:
        items.append("不要把 `skills/local_wrapper.md` 当作第二个语义层；它只是 IO binder。")
    if execution_present:
        items.append("不要把 `skills/local_execution.md` 当作第二个 orchestrator；它只执行一轮 bounded local round。")
    return uniq(items)


def generate_research_prompt(
    root: Path,
    path: str,
    cfg: dict,
    checklist: dict,
    mode: str,
    profile: str | None,
    wrapper_present: bool,
    execution_present: bool,
) -> str:
    phase = str(checklist.get("phase") or infer_phase(path))
    kind = "scope" if mode == "parent" else str(checklist.get("node_kind") or infer_kind(root, path))
    node_profile = node_profile_for(path, local_overrides(root))
    researcher_lens = effective_list(root, cfg, phase, node_profile, "node_researcher_lens")
    boundary_items = prompt_boundaries(phase, kind, profile, wrapper_present, execution_present)
    sections = [
        f"# {Path(path).name} research prompt",
        "",
        "## 节点定位",
        bullet_list(
            [
                f"phase: `{phase}`",
                f"node_kind: `{kind}`",
                f"node_path: `{path}`",
                f"node_mode: `{mode}`",
                f"node_profile: `{node_profile}`",
                f"execution_profile: `{profile}`" if profile else "execution_profile: `<none>`",
            ]
        ),
        "",
        "## 本轮目标",
        "### 节点职责",
        bullet_list(node_role_items(cfg, kind)),
        "",
        "### 必答研究问题",
        bullet_list(checklist_items(checklist, "required_questions_answered")),
        "",
        "### 本轮最小交付",
        bullet_list(output_items(cfg, checklist)),
        "",
        RESEARCH_PROMPT_DONE_LINE,
        "",
        "## 输入优先级",
        numbered_list(prompt_input_priority(root, path, cfg, checklist)),
        "",
        "## 阶段标准与局部附加约束",
        "### 研究判断口径",
        bullet_list(prompt_phase_constraints(root, path, cfg, phase, kind, mode, profile, wrapper_present, execution_present)),
        "",
        "## 研究者视角",
        bullet_list([f"role: {phase_researcher_role(root, phase)}", f"node_profile: {node_profile}"] + phase_guidance_items(root, phase, "guidance") + researcher_lens),
        "",
        "## 本节点应该做出的关键判断",
        bullet_list(phase_guidance_items(root, phase, "key_judgments")),
        "",
        "## 证据 / 引用 / 图表要求",
        bullet_list(phase_guidance_items(root, phase, "evidence_citation_figure_requirements")),
        "",
        "## 不合格写法",
        bullet_list(phase_guidance_items(root, phase, "failure_modes")),
        "",
        "### 质量门槛",
        bullet_list(uniq(checklist_items(checklist, "quality_checks") + phase_guidance_items(root, phase, "quality_gates"))),
        "",
        "### 可交接条件",
        bullet_list(checklist_items(checklist, "handoff_ready_if")),
        "",
        "### 作者退出条件",
        bullet_list(checklist_items(checklist, "author_exit")),
        "",
        "### 节点关闭条件",
        bullet_list(checklist_items(checklist, "node_close")),
        "",
        "## 执行边界",
        "### 明确不做",
        bullet_list(boundary_items),
        "",
        "### 停止条件",
        bullet_list(uniq(routing_stop_items(cfg, checklist) + ["若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。"])),
        "",
        "## 供执行者填写的本轮摘要",
        bullet_list(
            [
                "本轮最小目标：<待填写>",
                "本轮不做什么：<待填写>",
                "完成定义：见 `prompts/acceptance_checklist.yaml`",
                "完成后交给谁：<待填写>",
            ]
        ),
    ]
    return "\n".join(sections).rstrip() + "\n"


def required_input_items(cfg: dict, checklist: dict, standards_present: bool, mode: str) -> list[str]:
    items = [
        "README.md",
        "status.yaml",
        "skills/local_entry.md",
        "prompts/research_prompt.md",
        "prompts/acceptance_checklist.yaml",
    ]
    if requires_node_skill(mode):
        items.append("skills/SKILL.md")
    if requires_sop(mode, cfg):
        items.append("skills/SOP.md")
    if standards_present:
        items.append("prompts/standards.md")
    items.extend(checklist_items(checklist, "prompt_assets", "path"))
    items.extend(required_local_reads(cfg))
    items.extend(optional_local_reads(cfg))
    return uniq(items)


def output_items(cfg: dict, checklist: dict) -> list[str]:
    items: list[str] = []
    seen_keys: set[str] = set()
    for value in checklist_output_items(checklist):
        key = output_item_key(value)
        if key and key not in seen_keys:
            seen_keys.add(key)
            items.append(value)
    for value in cfg.get("outputs") or []:
        text = str(value).strip()
        key = output_item_key(text)
        if key and key not in seen_keys:
            seen_keys.add(key)
            items.append(text)
    return items


def bullet_list(items: list[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def numbered_list(items: list[str]) -> str:
    if not items:
        return "1. 无"
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, start=1))


def node_skill_frontmatter(path: str) -> dict:
    name = Path(path).name
    return {
        "name": f"{name}_node_skill",
        "description": f"Node-local strategy skill for `{path}`. Use only when this node's tier requires `skills/SKILL.md`.",
    }


def sop_frontmatter(path: str) -> dict:
    name = Path(path).name
    return {
        "name": f"{name}_node_sop",
        "description": f"Ordered operating procedure for `{path}`. Use only when this node declares `skills/SOP.md`.",
    }


def node_workflow(root: Path, phase: str, kind: str) -> list[str]:
    if kind == "scope":
        return SCOPE_WORKFLOW
    return phase_guidance_items(
        root,
        phase,
        "workflow",
        PHASE_WORKFLOW.get(phase, ["在当前节点内完成一个有界 research round，并把结果压缩到本地工件。"]),
    )


def node_boundaries(phase: str, kind: str) -> list[str]:
    if kind == "scope":
        return SCOPE_BOUNDARIES
    return PHASE_BOUNDARIES.get(phase, ["不把当前节点扩成 repo-global autonomous loop。"])


def profile_use_when(profile: str | None, phase: str) -> list[str]:
    if profile == "experiment_execution":
        return [
            "当前节点负责基于显式 execution contract 执行一轮有界轻量验证。",
            "需要把 baseline、单变量尝试、keep/discard 结论写回本地实验账本。",
        ]
    if profile == "result_synthesis":
        return [
            "当前节点负责把实验账本压缩成 result registry、hypothesis status 与 claim-safe 摘要。",
            "需要判断哪些 evidence 支持、否定或仍不足以支持当前 claim。",
        ]
    return PHASE_USE_WHEN.get(phase, ["当前节点需要完成一个有界 node-local research round。"])


def profile_strategy_delta(profile: str | None) -> list[str]:
    if profile == "experiment_execution":
        return [
            "把 `artifacts/execution_contract.yaml` 当作唯一 execution gate；若缺失或 `contract_mode != executable`，只允许转交 contract-prep。",
            "`skills/local_wrapper.md` 只绑定本地 IO，然后委托给 `auto_experiment_worker`。",
            "`auto_experiment_worker` 仍是唯一 active runtime experiment worker；不要在 node-local 层重新发明实验循环。",
            "本地实验工件路径固定为 `artifacts/auto_experiment/results.tsv` 与 `logs/auto_experiment/latest_run.log`。",
        ]
    if profile == "result_synthesis":
        return [
            "把 declared results ledger 当作主输入，而不是继续等待 execution contract。",
            "先写 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`，再决定是否补最小 paper 摘要。",
            "显式区分 supported / unsupported / unclear，并把缺证据项留在当前节点内报告。",
            "`skills/local_execution.md` 在这里是结果收敛 binder，不是实验发射器。",
        ]
    return []


def profile_boundaries(profile: str | None) -> list[str]:
    if profile == "experiment_execution":
        return [
            "不在无 executable contract 时直接进入实验执行。",
            "不把本节点扩成 repo-global experiment orchestrator。",
            "不更改实验主工件路径，也不引入第二个 runtime experiment worker。",
        ]
    if profile == "result_synthesis":
        return [
            "不重开 baseline / experiment loop。",
            "不把 execution contract 当作本节点 gate。",
            "不在证据不足时抬高 claim 强度，也不把结果整理扩成全局 figure/table 管理器。",
        ]
    return []


def profile_preflight(profile: str | None, cfg: dict) -> list[str]:
    if profile == "experiment_execution":
        items = [
            "确认 `artifacts/execution_contract.yaml` 已存在且 `contract_mode == executable`。",
            "确认本轮输出路径固定在 `artifacts/auto_experiment/results.tsv` 与 `logs/auto_experiment/latest_run.log`。",
        ]
        maybe_reads = optional_local_reads(cfg)
        if maybe_reads:
            items.append("仅当需要校对 claim / context 时，再读取这些补充材料：" + ", ".join(f"`{item}`" for item in maybe_reads) + "。")
        return items
    if profile == "result_synthesis":
        items = [
            "确认 declared results ledger 已存在且本轮可解析。",
            "确认当前节点可回写 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`。",
        ]
        maybe_reads = optional_local_reads(cfg)
        if maybe_reads:
            items.append("仅当需要生成最小 paper 摘要或定位 claim 上下文时，再读取这些补充材料：" + ", ".join(f"`{item}`" for item in maybe_reads) + "。")
        return items
    return []


def profile_procedure(profile: str | None, wrapper_present: bool, execution_present: bool) -> list[str]:
    if profile == "experiment_execution":
        steps = [
            "把本轮限制为一个 bounded experiment round，不扩大到第二个 node 或第二套 worker。",
            "先过 execution contract gate；只要 contract 缺失、字段不完整或 mode 不是 `executable`，立即停在 handoff / repair。",
        ]
        if wrapper_present:
            steps.append("若路径进入 `skills/local_wrapper.md`，只绑定本地 IO，然后委托一次 `auto_experiment_worker` bounded round。")
        if execution_present:
            steps.append("若路径进入 `skills/local_execution.md`，只执行一轮本地实验，不刷新 graph。")
        steps.extend(
            [
                "记录 baseline、变更点、metric 结果与 keep/discard 决策；失败也要留 stop reason。",
                "只更新当前节点工件和状态，不替其他节点代工。",
            ]
        )
        return steps
    if profile == "result_synthesis":
        steps = [
            "把本轮限制为一次结果收敛，不重开实验执行。",
            "先读取并压缩 declared results ledger，提取 baseline / variant / decision / claim impact 证据。",
            "按 supported / unsupported / unclear 更新 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`。",
            "只在证据位置明确时补最小 paper 摘要；否则报告缺口而不是补写强结论。",
        ]
        if execution_present:
            steps.append("若路径进入 `skills/local_execution.md`，它只负责这一轮结果收敛，不读取 execution contract。")
        return steps
    return []


def local_entry_read_order(
    root: Path,
    path: str,
    cfg: dict,
    checklist: dict,
    mode: str,
    wrapper_present: bool,
    execution_present: bool,
) -> list[str]:
    reads = prompt_read_paths(root, path, checklist)
    reads.extend(required_local_reads(cfg))
    reads = uniq(reads)
    if requires_node_skill(mode):
        reads.append("skills/SKILL.md")
    if requires_sop(mode, cfg):
        reads.append("skills/SOP.md")
    if wrapper_present:
        reads.append("skills/local_wrapper.md")
    if execution_present:
        reads.append("skills/local_execution.md")
    return reads


def generate_local_entry(
    root: Path,
    path: str,
    cfg: dict,
    checklist: dict,
    mode: str,
    profile: str | None,
    wrapper_present: bool,
    execution_present: bool,
) -> str:
    fm = {
        "skill_id": f"{Path(path).name}_local_entry",
        "purpose": cfg["purpose"],
        "node_mode": mode,
        "required_prompt_refs": prompt_read_paths(root, path, checklist),
    }
    for key in [
        "default_delegate",
        "decision_rule",
        "required_local_reads",
        "optional_local_reads",
        "outputs",
        "extra_status_updates",
        "stop_with",
    ]:
        value = cfg.get(key)
        if value not in (None, [], {}):
            fm[key] = value
    steps = [
        f"Entry file for this {mode} node.",
        "",
        f"This entry applies to `{path}`.",
        "",
        "Assume `README.md` and `status.yaml` are already loaded by the caller.",
        "",
        "Read in this order:",
    ]
    reads = local_entry_read_order(root, path, cfg, checklist, mode, wrapper_present, execution_present)
    steps.extend(f"{idx}. `{item}`" for idx, item in enumerate(reads, start=1))
    maybe_reads = optional_local_reads(cfg)
    if maybe_reads:
        steps.extend(
            [
                "",
                "Optional local reads (only when they materially change this run):",
                *[f"- `{item}`" for item in maybe_reads],
            ]
        )
    steps.extend(
        [
            "",
            "After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.",
            "Keep all work inside the selected node and auditable against the acceptance checklist.",
            "Do not synthesize deeper local layers than this tier requires.",
        ]
    )
    return fm_block(fm) + "\n" + "\n".join(steps).rstrip() + "\n"


def generate_node_skill(root: Path, path: str, cfg: dict, overrides: dict, mode: str, profile: str | None) -> str:
    checklist = checklist_for(root, path)
    phase = str(checklist.get("phase") or infer_phase(path))
    kind = "scope" if mode == "parent" else str(checklist.get("node_kind") or infer_kind(root, path))
    node_profile = node_profile_for(path, overrides)
    wrapper_present = declared_wrapper(path, overrides)
    execution_present = declared_execution(path, overrides)
    researcher_delta = [
        f"Researcher lens: {phase_researcher_role(root, phase)}.",
        f"Node profile: {node_profile}.",
        *phase_guidance_items(root, phase, "guidance"),
        *phase_guidance_items(root, phase, "key_judgments"),
        *effective_list(root, cfg, phase, node_profile, "node_researcher_lens"),
    ]
    for skill_id in delegate_skill_ids(cfg):
        researcher_delta.extend(canonical_skill_lens(root, skill_id))

    strategy_delta = [
        "Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.",
        *(profile_strategy_delta(profile) or node_workflow(root, phase, kind)),
        *uniq(researcher_delta),
    ]
    if mode == "standard":
        strategy_delta.append("Keep the round in planning / mapping / writing space; do not invent execution-only procedure here.")
    if requires_sop(mode, cfg):
        strategy_delta.append("Use `skills/SOP.md` as the only ordered procedure; do not restate checklist gates in this layer.")
    if wrapper_present:
        strategy_delta.append("If a wrapper path is selected, treat `skills/local_wrapper.md` as an IO binder rather than a second semantic layer.")
    if execution_present:
        strategy_delta.append("If a local execution path is selected, treat `skills/local_execution.md` as a bounded executor rather than a second router.")

    sections = [
        fm_block(node_skill_frontmatter(path)).rstrip(),
        "",
        f"# {Path(path).name} Node Skill",
        "",
        f"This node-local skill applies to `{path}`.",
        "",
        "## Node Context",
        bullet_list(
            [
                f"phase: `{phase}`",
                f"node_kind: `{kind}`",
                f"node_mode: `{mode}`",
                f"node_profile: `{node_profile}`",
                f"execution_profile: `{profile}`" if profile else "execution_profile: `<none>`",
                f"purpose: {cfg['purpose']}",
            ]
        ),
        "",
        "## Use When",
        bullet_list(profile_use_when(profile, phase)),
        "",
        "## Strategy Delta",
        bullet_list(strategy_delta),
        "",
        "## Local Routing / Delegate Contract",
        bullet_list(delegate_lines(cfg, wrapper_present, execution_present)),
        "",
        "## Boundaries",
        bullet_list(
            (profile_boundaries(profile) or node_boundaries(phase, kind))
            + [
                "When this file and the prompt assets differ, the prompt assets win on goal and done-state.",
                "Do not restate checklist inputs, outputs, or stop conditions in this layer.",
            ]
        ),
    ]
    return "\n".join(sections).rstrip() + "\n"


def generate_node_sop(root: Path, path: str, cfg: dict, overrides: dict, mode: str, profile: str | None) -> str:
    checklist = checklist_for(root, path)
    wrapper_present = declared_wrapper(path, overrides)
    execution_present = declared_execution(path, overrides)
    stop_items = routing_stop_items(cfg, checklist)

    read_order = [
        "README.md",
        "status.yaml",
        "skills/local_entry.md",
        "prompts/research_prompt.md",
        "prompts/acceptance_checklist.yaml",
    ]
    if requires_node_skill(mode):
        read_order.append("skills/SKILL.md")
    read_order.extend(extra_prompt_assets(root, path, checklist))
    read_order.extend(required_local_reads(cfg))
    if requires_sop(mode, cfg):
        read_order.append("skills/SOP.md")
    if wrapper_present:
        read_order.append("skills/local_wrapper.md")
    if execution_present:
        read_order.append("skills/local_execution.md")
    read_order = uniq(read_order)

    preflight = [
        "确认 `skills/local_entry.md` 已经选择了当前有序本地流程。",
        "确认 `prompts/acceptance_checklist.yaml` 可用，并且将作为唯一完成定义门槛。",
    ]
    must_reads = required_local_reads(cfg)
    if must_reads:
        preflight.append("确认默认必需的本地工作输入已存在：" + ", ".join(f"`{item}`" for item in must_reads) + "。")
    if wrapper_present:
        preflight.append("确认 `skills/local_wrapper.md` 与其 IO contract 已可用。")
    if execution_present:
        preflight.append("确认 `skills/local_execution.md` 与其 declared required inputs 已可用。")
    preflight.extend(profile_preflight(profile, cfg))
    preflight = uniq(preflight)

    procedure = cfg.get("sop_procedure") or profile_procedure(profile, wrapper_present, execution_present) or [
        "只读取 Read Order 中列出的文件，并把本轮限制在一个 bounded round 内。",
        "确认当前状态、阻塞项和 contract / inputs readiness，不在 scope 不清时继续深推。",
        "更新当前 binder 或 local action 路径负责的 node-local artifacts，不扩张到其他节点。",
        "重新对照 `prompts/acceptance_checklist.yaml` 记录 handoff 或 stop reason，不制造假推进。",
    ]

    sections = [
        fm_block(sop_frontmatter(path)).rstrip(),
        "",
        f"# {Path(path).name} SOP",
        "",
        f"This SOP applies to `{path}`.",
        "",
        "## Read Order",
        numbered_list(read_order),
        "",
        "## Preflight",
        bullet_list(preflight),
        "",
        "## Operating Procedure",
        numbered_list(procedure),
        "",
        "## Stop Rules",
        bullet_list(stop_items),
        "",
        "## Delegate Notes",
        bullet_list(delegate_lines(cfg, wrapper_present, execution_present)),
    ]
    return "\n".join(sections).rstrip() + "\n"


def generate_local_wrapper(path: str, cfg: dict, mode: str, profile: str | None) -> str:
    fm = {
        "skill_id": f"{Path(path).name}_local_wrapper",
        "purpose": cfg["purpose"],
        "canonical_target": cfg["canonical_target"],
        "io_contract": cfg["io_contract"],
    }
    if profile:
        fm["execution_profile"] = profile
    for key in ["required_local_reads", "optional_local_reads", "extra_status_updates", "stop_with"]:
        value = cfg.get(key)
        if value not in (None, [], {}):
            fm[key] = value

    if profile == "experiment_execution":
        body = (
            "Use this wrapper only after `skills/local_entry.md` selected the wrapper path.\n"
            "Bind the declared execution contract and fixed auto-experiment artifact paths, then delegate exactly one bounded `auto_experiment_worker` round.\n"
        )
    elif cfg["canonical_target"] == "paper_figure":
        body = (
            "Use this wrapper only after `skills/local_entry.md` selected the wrapper path.\n"
            "Bind the declared local figure IO, including `artifacts/figure_manifest.yaml` when present, then delegate exactly one bounded `paper_figure` round.\n"
            "Figure drafts may come from TeX/TikZ/PGFPlots, Python, or human-provided PDF; once node status is `done`, do not overwrite accepted figure outputs.\n"
        )
    else:
        body = (
            "Use this wrapper only after `skills/local_entry.md` selected the wrapper path.\n"
            "Bind the declared local IO contract and delegate exactly one bounded canonical worker round.\n"
        )
    return fm_block(fm) + "\n" + body


def generate_local_execution(path: str, cfg: dict, profile: str | None) -> str:
    fm = {
        "skill_id": f"{Path(path).name}_local_execution",
        "purpose": cfg["purpose"],
        "required_inputs": cfg["required_inputs"],
        "outputs": cfg["outputs"],
        "stop_conditions": cfg["stop_conditions"],
    }
    if profile:
        fm["execution_profile"] = profile
    for key in ["required_local_reads", "optional_local_reads", "extra_status_updates"]:
        value = cfg.get(key)
        if value not in (None, [], {}):
            fm[key] = value
    if profile == "result_synthesis":
        body = (
            "Use this execution path only after `skills/local_entry.md` selected it.\n"
            "Verify the declared results ledger, then run exactly one bounded result-synthesis round: classify supported / unsupported / unclear, update the declared registry files, and stop without consulting any experiment gate or refreshing graph.\n"
        )
    elif profile == "experiment_execution":
        body = (
            "Use this execution path only after `skills/local_entry.md` selected it.\n"
            "Verify the declared execution contract inputs, then run exactly one bounded local experiment round without widening scope or refreshing graph.\n"
        )
    else:
        body = (
            "Use this execution path only after `skills/local_entry.md` selected it.\n"
            "Verify the declared required inputs, then run exactly one bounded local execution round without widening scope or refreshing graph.\n"
        )
    return fm_block(fm) + "\n" + body


def cleanup_node_files(root: Path, path: str, cfg: dict, mode: str, wrapper_present: bool, execution_present: bool) -> None:
    node_dir = root / path / "skills"
    node_dir.mkdir(parents=True, exist_ok=True)
    if not requires_node_skill(mode):
        remove_if_exists(node_dir / "SKILL.md")
    if not requires_sop(mode, cfg):
        remove_if_exists(node_dir / "SOP.md")
    if not wrapper_present:
        remove_if_exists(node_dir / "local_wrapper.md")
    if not execution_present:
        remove_if_exists(node_dir / "local_execution.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate node-local skills from registry truth.")
    parser.add_argument("--root", default=str(Path.cwd()), help="Repository root. Defaults to the current working directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    policy = load_node_tier_policy(root)
    overrides = load_local_skill_overrides(root)

    for path, cfg in overrides["nodes"].items():
        ensure_no_legacy_extra_reads(path, cfg)
        mode = node_mode_for(path, overrides)
        node_profile = node_profile_for(path, overrides)
        profile = execution_profile_for(path, overrides)
        wrapper_present = declared_wrapper(path, overrides)
        execution_present = declared_execution(path, overrides)
        if wrapper_present and not allows_wrapper(mode):
            raise RuntimeError(f"{path}: local_wrapper is not allowed for node_mode={mode}")
        if execution_present and not allows_execution(mode):
            raise RuntimeError(f"{path}: local_execution is not allowed for node_mode={mode}")
        if binder_any_of_for(mode, policy) and not (wrapper_present or execution_present):
            raise RuntimeError(f"{path}: node_mode={mode} requires a local wrapper or local execution binder")
        if profile and mode != "execution":
            raise RuntimeError(f"{path}: execution_profile={profile} requires node_mode=execution")

        checklist = checklist_for(root, path)
        checklist = update_checklist_with_profile_contract(root, cfg, checklist, mode, node_profile)
        requires_external_review = external_review_required(cfg, checklist)
        if requires_external_review:
            checklist = update_checklist_with_external_review_gate(root, path, cfg, checklist, mode)
        write(
            root / path / "prompts" / "acceptance_checklist.yaml",
            yaml.safe_dump(checklist, allow_unicode=True, sort_keys=False).rstrip() + "\n",
        )
        if requires_external_review:
            write(
                root / path / "prompts" / REVIEW_RUBRIC_PATH.split("/", 1)[1],
                generate_review_rubric(root, path, cfg, checklist, mode, profile),
            )
            ensure_review_assets(root, path)
        write(
            root / path / "prompts" / "research_prompt.md",
            generate_research_prompt(root, path, cfg, checklist, mode, profile, wrapper_present, execution_present),
        )
        cleanup_node_files(root, path, cfg, mode, wrapper_present, execution_present)
        write(
            root / path / "skills" / "local_entry.md",
            generate_local_entry(root, path, cfg, checklist, mode, profile, wrapper_present, execution_present),
        )
        if requires_node_skill(mode):
            write(root / path / "skills" / "SKILL.md", generate_node_skill(root, path, cfg, overrides, mode, profile))
        if requires_sop(mode, cfg):
            write(root / path / "skills" / "SOP.md", generate_node_sop(root, path, cfg, overrides, mode, profile))

    for path, cfg in overrides.get("wrappers", {}).items():
        ensure_no_legacy_extra_reads(path, cfg)
        mode = node_mode_for(path, overrides)
        profile = execution_profile_for(path, overrides)
        if not allows_wrapper(mode):
            raise RuntimeError(f"{path}: wrapper override conflicts with node_mode={mode}")
        write(root / path / "skills" / "local_wrapper.md", generate_local_wrapper(path, cfg, mode, profile))

    for path, cfg in overrides.get("executions", {}).items():
        ensure_no_legacy_extra_reads(path, cfg)
        mode = node_mode_for(path, overrides)
        profile = execution_profile_for(path, overrides)
        if not allows_execution(mode):
            raise RuntimeError(f"{path}: execution override conflicts with node_mode={mode}")
        write(root / path / "skills" / "local_execution.md", generate_local_execution(path, cfg, profile))

    print("[ok] regenerated local skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
