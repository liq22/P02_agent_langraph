#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

LEGACY_MINIMAL_ENTRY_BODY = "Use implicit local-entry conventions from the registry. Keep this node-local and bounded."
VALID_NODE_MODES = {"parent", "lite", "standard", "execution"}
VALID_NODE_PROFILES = {"experiment_execution", "result_synthesis"}
NODE_ARCHETYPE_FAMILIES = {
    "parent": "parent_coordination_family",
    "lite": "lite_research_leaf_family",
    "standard": "standard_research_leaf_family",
    "execution": "execution_leaf_family",
}
PROMPT_ASSETS = (
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
)
EXPECTED_NODE_MODE_COUNTS = {"parent": 7, "lite": 11, "standard": 22, "execution": 4}
RESEARCH_PROMPT_REQUIRED_HEADINGS = (
    "## 节点定位",
    "## 本轮目标",
    "### 节点职责",
    "### 必答研究问题",
    "### 本轮最小交付",
    "## 输入优先级",
    "## 阶段标准与局部附加约束",
    "### 研究判断口径",
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


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def node_mode_for(node_path: str, overrides: dict) -> str:
    nodes = overrides.get("nodes") or {}
    cfg = nodes.get(node_path) if isinstance(nodes, dict) else None
    mode = str((cfg or {}).get("node_mode", "")).strip()
    return mode


def node_cfg_for(node_path: str, overrides: dict) -> dict:
    nodes = overrides.get("nodes") or {}
    cfg = nodes.get(node_path) if isinstance(nodes, dict) else None
    return cfg if isinstance(cfg, dict) else {}


def node_profile_for(node_path: str, overrides: dict) -> str | None:
    nodes = overrides.get("nodes") or {}
    cfg = nodes.get(node_path) if isinstance(nodes, dict) else None
    profile = str((cfg or {}).get("node_profile", "")).strip()
    return profile or None


def execution_profile_for(node_path: str, overrides: dict) -> str | None:
    nodes = overrides.get("nodes") or {}
    cfg = nodes.get(node_path) if isinstance(nodes, dict) else None
    profile = str((cfg or {}).get("execution_profile", "")).strip()
    if not profile:
        legacy = str((cfg or {}).get("node_profile", "")).strip()
        profile = legacy if legacy in {"experiment_execution", "result_synthesis"} else ""
    return profile or None


def requires_node_skill(mode: str) -> bool:
    return mode in {"standard", "execution"}


def requires_sop(mode: str, cfg: dict | None = None) -> bool:
    if mode == "execution":
        return True
    return bool((cfg or {}).get("generate_sop"))


def entry_matches_mode(entry_text: str, mode: str, cfg: dict, wrapper_exists: bool, execution_exists: bool) -> bool:
    if LEGACY_MINIMAL_ENTRY_BODY in entry_text:
        return False
    if not all(asset in entry_text for asset in PROMPT_ASSETS):
        return False
    if requires_node_skill(mode) and "skills/SKILL.md" not in entry_text:
        return False
    if not requires_node_skill(mode) and "skills/SKILL.md" in entry_text:
        return False
    if requires_sop(mode, cfg) and "skills/SOP.md" not in entry_text:
        return False
    if not requires_sop(mode, cfg) and "skills/SOP.md" in entry_text:
        return False
    if wrapper_exists and "skills/local_wrapper.md" not in entry_text:
        return False
    if execution_exists and "skills/local_execution.md" not in entry_text:
        return False
    return True


def has_heading_contract(text: str, required: tuple[str, ...], banned: tuple[str, ...]) -> bool:
    return all(item in text for item in required) and all(item not in text for item in banned)


def print_header(title: str) -> None:
    print(f"\n== {title} ==")


def main() -> int:
    root = repo_root()
    refresh_script = root / "scripts" / "refresh_hypergraph.py"
    refresh_views_script = root / "scripts" / "refresh_views.py"
    canvas_script = root / "scripts" / "build_canvas_from_graph.py"
    validate_local_skills_script = root / "scripts" / "validate_local_skills.py"
    validate_skill_fit_script = root / "scripts" / "validate_skill_fit.py"
    jargon_lint_script = root / "scripts" / "lint_jargon.py"
    readme = root / "README.md"
    entry_matrix = root / "docs" / "architecture" / "entry_matrix.md"
    refresh_modes = root / "docs" / "architecture" / "refresh_modes.md"
    architecture = root / "docs" / "architecture.md"
    contract_template = root / "templates" / "execution_contract.template.yaml"
    skill_catalog = root / "backend" / "registry" / "skill_registry" / "skill_catalog.yaml"
    local_skill_overrides = root / "backend" / "registry" / "skill_registry" / "local_skill_overrides.yaml"
    node_tier_policy = root / "backend" / "registry" / "skill_registry" / "node_tier_policy.yaml"
    scoring_policy = root / "backend" / "registry" / "scoring_registry" / "node_scoring_system_v0_2.yaml"
    scorecard_template = root / "templates" / "scoring" / "node_scorecard.template.yaml"
    edge_registry = root / "backend" / "relations" / "edge_registry.json"
    graph_path = root / "backend" / "graph" / "graph.json"
    graph_status_path = root / "backend" / "graph" / "graph_status.json"
    node_details_path = root / "backend" / "graph" / "node_details.json"
    scope_rollup_path = root / "backend" / "graph" / "scope_rollup.json"
    board_state_path = root / "backend" / "graph" / "board_state.json"
    orchestrator = root / ".agent" / "skills" / "graph_driven_research_orchestrator" / "SKILL.md"
    auto_campaign = root / ".agent" / "skills" / "auto_research_campaign" / "SKILL.md"
    auto_worker = root / ".agent" / "skills" / "auto_experiment_worker" / "SKILL.md"
    external_reviewer = root / ".agent" / "skills" / "external_node_reviewer" / "SKILL.md"
    legacy_autoresearch = root / ".agent" / "skills" / "autoresearch" / "SKILL.md"

    missing = [
        p
        for p in [
            readme,
            entry_matrix,
            refresh_modes,
            architecture,
            contract_template,
            skill_catalog,
            local_skill_overrides,
            node_tier_policy,
            scoring_policy,
            scorecard_template,
            refresh_script,
            refresh_views_script,
            canvas_script,
            validate_local_skills_script,
            validate_skill_fit_script,
            jargon_lint_script,
            edge_registry,
            orchestrator,
            auto_campaign,
            auto_worker,
            external_reviewer,
        ]
        if not p.exists()
    ]
    if missing:
        print("live repo smoke: fail")
        for path in missing:
            print(f"- missing: {path.relative_to(root) if path.is_absolute() else path}")
        return 1

    status = {"backend": "pass", "frontend": "pass", "skill": "pass"}
    readme_text = readme.read_text(encoding="utf-8")
    architecture_text = architecture.read_text(encoding="utf-8")
    entry_matrix_text = entry_matrix.read_text(encoding="utf-8")
    refresh_modes_text = refresh_modes.read_text(encoding="utf-8")
    skill_catalog_payload = load_yaml(skill_catalog)
    local_skill_overrides_payload = load_yaml(local_skill_overrides)
    node_tier_policy_payload = load_yaml(node_tier_policy)
    scoring_policy_payload = load_yaml(scoring_policy)
    scorecard_template_payload = load_yaml(scorecard_template)
    raw_skill_entries = skill_catalog_payload.get("skills", []) if isinstance(skill_catalog_payload.get("skills", []), list) else []
    skill_entries = [entry for entry in raw_skill_entries if isinstance(entry, dict)]
    skill_list = [str(entry.get("name", "")).strip() for entry in skill_entries if str(entry.get("name", "")).strip()]
    skill_roles = {str(entry.get("name", "")).strip(): str(entry.get("role", "")).strip() for entry in skill_entries}
    skill_visibility = {str(entry.get("name", "")).strip(): str(entry.get("default_visibility", "")).strip() for entry in skill_entries}
    node_mode_counts: dict[str, int] = {}
    for cfg in (local_skill_overrides_payload.get("nodes") or {}).values():
        if isinstance(cfg, dict):
            mode = str(cfg.get("node_mode", "")).strip()
            node_mode_counts[mode] = node_mode_counts.get(mode, 0) + 1

    print_header("backend")
    proc = run([sys.executable, str(refresh_script)], root)
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0 or not graph_path.exists() or not graph_status_path.exists():
        print("backend: fail")
        return 1

    graph = load_json(graph_path)
    graph_status = load_json(graph_status_path)
    nodes = graph.get("nodes", {})
    next_node = graph_status.get("next_node")
    current_phase = graph_status.get("current_phase")
    parent_node_ids = {
        node_id
        for node_id, payload in nodes.items()
        if any(
            other_id != node_id and str(other_payload.get("path", "")).startswith(str(payload.get("path", "")) + "/")
            for other_id, other_payload in nodes.items()
        )
    }
    print(f"current_phase={current_phase}")
    print(f"next_node={next_node}")

    backend_ok = isinstance(nodes, dict) and isinstance(next_node, str) and next_node in nodes
    print(f"minimal_graph_and_next_node: {'pass' if backend_ok else 'fail'}")
    if not backend_ok:
        status["backend"] = "fail"

    next_path = None
    if backend_ok:
        next_path = root / nodes[next_node]["path"]
        node_files_ok = (next_path / "README.md").exists() and (next_path / "status.yaml").exists()
        print(f"next_node_files_exist: {'pass' if node_files_ok else 'fail'}")
        if not node_files_ok:
            status["backend"] = "fail"

    frontier_leaf_only = all(
        node_id not in parent_node_ids
        for node_id in graph_status.get("ready_nodes", []) + graph_status.get("blocked_nodes", [])
    )
    print(f"scheduler_frontier_leaf_only: {'pass' if frontier_leaf_only else 'fail'}")
    if not frontier_leaf_only:
        status["backend"] = "fail"

    parent_depends_on_edges = [
        edge
        for edge in graph.get("edges", [])
        if edge.get("rel") == "depends_on"
        and (edge.get("src") in parent_node_ids or edge.get("dst") in parent_node_ids)
    ]
    print(f"depends_on_edges_leaf_only: {'pass' if not parent_depends_on_edges else 'fail'}")
    if parent_depends_on_edges:
        status["backend"] = "fail"

    print_header("frontend")
    proc = run([sys.executable, str(refresh_views_script), "--mode", "graph_only"], root)
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0:
        status["frontend"] = "fail"

    proc = run([sys.executable, str(refresh_views_script), "--mode", "full"], root)
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0:
        status["frontend"] = "fail"

    proc = run([sys.executable, str(canvas_script), "--dry-run"], root)
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0:
        status["frontend"] = "fail"

    workbench = root / "obsidian" / "canvases" / "framework_workbench.canvas"
    proposals = root / "obsidian" / "inbox" / "canvas_proposals.md"
    if proposals.exists():
        print("canvas_proposal_inbox: pass")
    else:
        print("canvas_proposal_inbox: partial")
        if status["frontend"] == "pass":
            status["frontend"] = "partial"
    print(f"framework_workbench_present: {'pass' if workbench.exists() else 'partial'}")
    if not workbench.exists() and status["frontend"] == "pass":
        status["frontend"] = "partial"

    node_details = load_json(node_details_path) if node_details_path.exists() else {}
    scope_rollup = load_json(scope_rollup_path) if scope_rollup_path.exists() else {}
    board_state = load_json(board_state_path) if board_state_path.exists() else {}

    print_header("skill layer")
    print(f"orchestrator_exists: {'pass' if orchestrator.exists() else 'fail'}")
    print(f"auto_campaign_exists: {'pass' if auto_campaign.exists() else 'fail'}")
    print(f"auto_worker_exists: {'pass' if auto_worker.exists() else 'fail'}")
    print(f"external_reviewer_exists: {'pass' if external_reviewer.exists() else 'fail'}")
    print(f"legacy_autoresearch_runtime_absent: {'pass' if not legacy_autoresearch.exists() else 'fail'}")
    entry_matrix_ok = all(
        marker in entry_matrix_text
        for marker in (
            "graph_driven_research_orchestrator",
            "auto_research_campaign",
            "auto_experiment_worker",
            "parent_coordination_family",
            "lite_research_leaf_family",
            "standard_research_leaf_family",
            "execution_leaf_family",
        )
    )
    docs_entry_consistent = all(
        marker in readme_text and marker in architecture_text
        for marker in ("graph_driven_research_orchestrator", "auto_research_campaign", "auto_experiment_worker")
    )
    refresh_modes_ok = "--mode graph_only" in readme_text and "--mode full" in readme_text and "graph_only" in refresh_modes_text and "full" in refresh_modes_text
    skill_catalog_ok = (
        "auto_research_campaign" in skill_list
        and "auto_experiment_worker" in skill_list
        and "external_node_reviewer" in skill_list
        and "autoresearch" not in skill_list
        and skill_roles.get("graph_driven_research_orchestrator") == "entry"
        and skill_roles.get("auto_research_campaign") == "entry"
        and skill_roles.get("autonomous_research_lane") == "lane"
        and skill_roles.get("auto_experiment_worker") == "worker"
        and skill_roles.get("aggregate_reviews") == "helper"
        and skill_roles.get("external_node_reviewer") == "helper"
        and skill_roles.get("karpathy-skills") == "profile"
        and skill_visibility.get("external_node_reviewer") == "operator_only"
    )
    node_tier_policy_ok = isinstance(node_tier_policy_payload.get("node_modes"), dict) and all(
        mode in node_tier_policy_payload.get("node_modes", {}) for mode in VALID_NODE_MODES
    )
    local_skill_overrides_ok = isinstance(local_skill_overrides_payload.get("nodes"), dict)
    node_mode_counts_ok = node_mode_counts == EXPECTED_NODE_MODE_COUNTS
    node_details_nodes = node_details.get("nodes", {}) if isinstance(node_details.get("nodes", {}), dict) else {}
    node_archetype_family_ok = bool(node_details_nodes) and all(
        isinstance(detail, dict)
        and detail.get("node_mode") in VALID_NODE_MODES
        and detail.get("node_archetype_family") == NODE_ARCHETYPE_FAMILIES.get(detail.get("node_mode"))
        and isinstance(detail.get("node_entry_packet"), dict)
        and detail.get("node_entry_packet", {}).get("node_archetype_family") == NODE_ARCHETYPE_FAMILIES.get(detail.get("node_mode"))
        and isinstance(detail.get("external_review"), dict)
        and detail.get("external_review", {}).get("reviewer_role") == "external_node_reviewer"
        for detail in node_details_nodes.values()
    )
    truth_field_kinds = {"parent", "leaf"}
    review_gate_states = {"not_required", "missing_verdict", "incomplete", "failed", "passed"}
    execution_gate_states = {"not_applicable", "missing_contract", "review_only", "contract_incomplete", "missing_outputs", "failed", "ready"}
    handoff_states = {"ready", "blocked_truth", "blocked_review", "blocked_execution", "blocked_parent_rollup", "blocked_unknown"}
    placeholder_states = {"none", "suspected", "confirmed"}
    truth_projection_ok = bool(node_details_nodes) and all(
        isinstance(detail, dict)
        and detail.get("kind") in truth_field_kinds
        and isinstance(detail.get("scheduler_ready"), bool)
        and isinstance(detail.get("truth_ready"), bool)
        and detail.get("review_gate_state") in review_gate_states
        and detail.get("execution_gate_state") in execution_gate_states
        and detail.get("handoff_readiness") in handoff_states
        and isinstance(detail.get("blocking_reasons"), list)
        and detail.get("placeholder_risk") in placeholder_states
        for detail in node_details_nodes.values()
    )
    rollup_payload = scope_rollup.get("scopes", {}) if isinstance(scope_rollup.get("scopes", {}), dict) else {}
    board_lanes = board_state.get("lanes", {}) if isinstance(board_state.get("lanes", {}), dict) else {}
    rollup_truth_counts_ok = bool(rollup_payload) and all(
        all(
            key in payload
            for key in (
                "scheduler_ready_count",
                "scheduler_blocked_count",
                "truth_ready_count",
                "truth_blocked_count",
                "review_blocked_count",
                "execution_blocked_count",
                "handoff_ready_count",
                "placeholder_confirmed_count",
                "scheduler_next_descendants",
            )
        )
        for payload in rollup_payload.values()
        if isinstance(payload, dict)
    )
    board_truth_lanes_ok = set(board_lanes.keys()) == {
        "scheduler_now",
        "truth_ready",
        "review_blocked",
        "execution_blocked",
        "truth_blocked",
        "active_work",
        "parked",
    }
    hotspot_ids = [
        "research::P0_项目申请书::P0_01_研究背景与调研",
        "research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证",
        "research::P2_论文撰写::P2_03_定稿_tex",
        "research::P3_论文模拟评审与修改_多轮::P3_02_评价者档案",
        "research::P3_论文模拟评审与修改_多轮::P3_03_批评摘要",
        "research::P4_论文回复_response::P4_07_再投稿打包",
    ]
    hotspot_truth_blocked_ok = all(
        node_details_nodes.get(node_id, {}).get("handoff_readiness") != "ready"
        for node_id in hotspot_ids
        if node_id in node_details_nodes
    )
    contract_template_ok = contract_template.exists() and "contract_mode: review_only" in contract_template.read_text(encoding="utf-8")
    scoring_policy_ok = (
        scoring_policy_payload.get("version") == "0.2"
        and isinstance(scoring_policy_payload.get("layers"), dict)
        and isinstance(scoring_policy_payload.get("layers", {}).get("research_quality"), dict)
        and isinstance(scoring_policy_payload.get("layers", {}).get("smoothness"), dict)
        and isinstance(scoring_policy_payload.get("complexity_penalty"), dict)
        and "final_formula" in scoring_policy_payload
    )
    scorecard_template_ok = all(
        field in scorecard_template_payload
        for field in (
            "policy_version",
            "node_path",
            "node_mode",
            "node_profile",
            "phase",
            "scores",
            "complexity_penalty",
            "final_score",
            "hard_caps",
            "evidence",
            "review_notes",
            "next_action",
        )
    )
    print(f"entry_matrix_exists_and_complete: {'pass' if entry_matrix_ok else 'fail'}")
    print(f"docs_entry_consistent: {'pass' if docs_entry_consistent else 'fail'}")
    print(f"refresh_modes_documented: {'pass' if refresh_modes_ok else 'fail'}")
    print(f"skill_catalog_runtime_truth: {'pass' if skill_catalog_ok else 'fail'}")
    print(f"node_tier_policy_exists_and_complete: {'pass' if node_tier_policy_ok else 'fail'}")
    print(f"local_skill_overrides_exist: {'pass' if local_skill_overrides_ok else 'fail'}")
    print(f"node_mode_counts_stable: {'pass' if node_mode_counts_ok else 'fail'} ({node_mode_counts})")
    print(f"node_archetype_families_projected: {'pass' if node_archetype_family_ok else 'fail'}")
    print(f"truth_fields_projected: {'pass' if truth_projection_ok else 'fail'}")
    print(f"scope_rollup_truth_counts: {'pass' if rollup_truth_counts_ok else 'fail'}")
    print(f"board_truth_lanes: {'pass' if board_truth_lanes_ok else 'fail'}")
    print(f"hotspot_nodes_not_handoff_ready: {'pass' if hotspot_truth_blocked_ok else 'fail'}")
    print(f"execution_contract_template_exists: {'pass' if contract_template_ok else 'fail'}")
    print(f"node_scoring_policy_v0_2: {'pass' if scoring_policy_ok else 'fail'}")
    print(f"node_scorecard_template: {'pass' if scorecard_template_ok else 'fail'}")
    proc = run([sys.executable, str(validate_local_skills_script)], root)
    validate_local_skills_ok = proc.returncode == 0
    print(f"validate_local_skills: {'pass' if validate_local_skills_ok else 'fail'}")
    if not validate_local_skills_ok:
        print(proc.stdout.strip() or proc.stderr.strip())
    proc = run([sys.executable, str(validate_skill_fit_script), "--root", str(root)], root)
    validate_skill_fit_ok = proc.returncode == 0
    print(f"validate_skill_fit: {'pass' if validate_skill_fit_ok else 'fail'}")
    if not validate_skill_fit_ok:
        print(proc.stdout.strip() or proc.stderr.strip())
    proc = run(
        [
            sys.executable,
            str(jargon_lint_script),
            "--strict",
            "README.md",
            "docs/USER_GUIDEBOOK.md",
            "docs/CODEX_ONLY_WORKFLOW.md",
            "docs/architecture/entry_matrix.md",
        ],
        root,
    )
    jargon_lint_ok = proc.returncode == 0
    print(f"entry_doc_jargon_lint: {'pass' if jargon_lint_ok else 'fail'}")
    if not jargon_lint_ok:
        print(proc.stdout.strip() or proc.stderr.strip())
    if (
        not orchestrator.exists()
        or not auto_campaign.exists()
        or not auto_worker.exists()
        or not external_reviewer.exists()
        or legacy_autoresearch.exists()
        or not entry_matrix_ok
        or not docs_entry_consistent
        or not refresh_modes_ok
        or not skill_catalog_ok
        or not node_tier_policy_ok
        or not local_skill_overrides_ok
        or not node_mode_counts_ok
        or not node_archetype_family_ok
        or not truth_projection_ok
        or not rollup_truth_counts_ok
        or not board_truth_lanes_ok
        or not hotspot_truth_blocked_ok
        or not contract_template_ok
        or not scoring_policy_ok
        or not scorecard_template_ok
        or not validate_local_skills_ok
        or not validate_skill_fit_ok
        or not jargon_lint_ok
    ):
        status["skill"] = "fail"

    if next_path is not None:
        next_node_path = nodes[next_node]["path"]
        next_mode = node_mode_for(next_node_path, local_skill_overrides_payload)
        next_cfg = node_cfg_for(next_node_path, local_skill_overrides_payload)
        local_entry = next_path / "skills" / "local_entry.md"
        research_prompt = next_path / "prompts" / "research_prompt.md"
        acceptance = next_path / "prompts" / "acceptance_checklist.yaml"
        review_rubric = next_path / "prompts" / "review_rubric.yaml"
        review_verdict = next_path / "review" / "verdict.yaml"
        node_skill = next_path / "skills" / "SKILL.md"
        node_sop = next_path / "skills" / "SOP.md"
        local_wrapper = next_path / "skills" / "local_wrapper.md"
        local_execution = next_path / "skills" / "local_execution.md"
        acceptance_payload = load_yaml(acceptance) if acceptance.exists() else {}
        review_verdict_payload = load_yaml(review_verdict) if review_verdict.exists() else {}
        next_detail = node_details_nodes.get(next_node, {}) if isinstance(node_details_nodes.get(next_node, {}), dict) else {}
        local_entry_text = local_entry.read_text(encoding="utf-8") if local_entry.exists() else ""
        research_prompt_text = research_prompt.read_text(encoding="utf-8") if research_prompt.exists() else ""
        node_skill_text = node_skill.read_text(encoding="utf-8") if node_skill.exists() else ""
        node_sop_text = node_sop.read_text(encoding="utf-8") if node_sop.exists() else ""
        mode_ok = next_mode in VALID_NODE_MODES
        entry_is_shim = (
            local_entry.exists()
            and mode_ok
            and entry_matches_mode(
                local_entry_text,
                next_mode,
                next_cfg,
                wrapper_exists=local_wrapper.exists(),
                execution_exists=local_execution.exists(),
            )
        )
        unexpected_stack = (
            (not requires_node_skill(next_mode) and node_skill.exists())
            or (not requires_sop(next_mode, next_cfg) and node_sop.exists())
            or (next_mode != "execution" and local_execution.exists())
        ) if mode_ok else True
        print(f"next_node_mode_valid: {'pass' if mode_ok else 'fail'}")
        print(f"next_node_local_entry: {'pass' if local_entry.exists() else 'fail'}")
        print(f"next_node_research_prompt: {'pass' if research_prompt.exists() else 'fail'}")
        print(f"next_node_research_prompt_compact: {'pass' if (research_prompt.exists() and has_heading_contract(research_prompt_text, RESEARCH_PROMPT_REQUIRED_HEADINGS, RESEARCH_PROMPT_BANNED_HEADINGS) and RESEARCH_PROMPT_DONE_LINE in research_prompt_text) else 'fail'}")
        print(f"next_node_acceptance_checklist: {'pass' if acceptance.exists() else 'fail'}")
        print(f"next_node_review_rubric: {'pass' if review_rubric.exists() else 'fail'}")
        print(f"next_node_review_verdict_template: {'pass' if review_verdict.exists() else 'fail'}")
        print(f"next_node_external_review_gate: {'pass' if (acceptance_payload.get('external_review_gate', {}).get('required') is True and acceptance_payload.get('external_review_gate', {}).get('reviewer_role') == 'external_node_reviewer') else 'fail'}")
        print(f"next_node_verdict_targets_external_reviewer: {'pass' if review_verdict_payload.get('reviewer_skill') == 'external_node_reviewer' else 'fail'}")
        print(f"next_node_node_details_external_review: {'pass' if (next_detail.get('external_review', {}).get('reviewer_role') == 'external_node_reviewer') else 'fail'}")
        print(f"next_node_node_skill_required: {'pass' if (node_skill.exists() if mode_ok and requires_node_skill(next_mode) else True) else 'fail'}")
        print(f"next_node_node_skill_compact: {'pass' if ((not requires_node_skill(next_mode)) or has_heading_contract(node_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS)) else 'fail'}")
        print(f"next_node_node_sop_required: {'pass' if (node_sop.exists() if mode_ok and requires_sop(next_mode, next_cfg) else True) else 'fail'}")
        print(f"next_node_node_sop_compact: {'pass' if ((not requires_sop(next_mode, next_cfg)) or has_heading_contract(node_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS)) else 'fail'}")
        print(f"next_node_unexpected_stack_absent: {'pass' if not unexpected_stack else 'fail'}")
        print(f"next_node_entry_is_shim: {'pass' if entry_is_shim else 'fail'}")
        if (
            not mode_ok
            or not local_entry.exists()
            or not research_prompt.exists()
            or not has_heading_contract(research_prompt_text, RESEARCH_PROMPT_REQUIRED_HEADINGS, RESEARCH_PROMPT_BANNED_HEADINGS)
            or RESEARCH_PROMPT_DONE_LINE not in research_prompt_text
            or not acceptance.exists()
            or not review_rubric.exists()
            or not review_verdict.exists()
            or acceptance_payload.get("external_review_gate", {}).get("required") is not True
            or acceptance_payload.get("external_review_gate", {}).get("reviewer_role") != "external_node_reviewer"
            or review_verdict_payload.get("reviewer_skill") != "external_node_reviewer"
            or next_detail.get("external_review", {}).get("reviewer_role") != "external_node_reviewer"
            or (requires_node_skill(next_mode) and not node_skill.exists())
            or (requires_node_skill(next_mode) and not has_heading_contract(node_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS))
            or (requires_sop(next_mode, next_cfg) and not node_sop.exists())
            or (requires_sop(next_mode, next_cfg) and not has_heading_contract(node_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS))
            or unexpected_stack
            or not entry_is_shim
        ):
            status["skill"] = "fail"

    p104 = root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证"
    p104_cfg = node_cfg_for("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证", local_skill_overrides_payload)
    local_entry = p104 / "skills" / "local_entry.md"
    node_skill = p104 / "skills" / "SKILL.md"
    node_sop = p104 / "skills" / "SOP.md"
    local_wrapper = p104 / "skills" / "local_wrapper.md"
    local_execution = p104 / "skills" / "local_execution.md"
    execution_contract = p104 / "artifacts" / "execution_contract.yaml"

    if p104.exists():
        p104_mode = node_mode_for("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证", local_skill_overrides_payload)
        p104_profile = execution_profile_for("research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证", local_skill_overrides_payload)
        research_prompt = p104 / "prompts" / "research_prompt.md"
        print(f"P1_04_local_entry: {'pass' if local_entry.exists() else 'partial'}")
        print(f"P1_04_node_mode_execution: {'pass' if p104_mode == 'execution' else 'fail'}")
        print(f"P1_04_node_profile_experiment_execution: {'pass' if p104_profile == 'experiment_execution' else 'fail'}")
        print(f"P1_04_node_skill: {'pass' if node_skill.exists() else 'fail'}")
        print(f"P1_04_node_sop: {'pass' if node_sop.exists() else 'fail'}")
        print(f"P1_04_local_wrapper: {'pass' if local_wrapper.exists() else 'fail'}")
        print(f"P1_04_stale_local_execution_removed: {'pass' if not local_execution.exists() else 'fail'}")
        print(f"P1_04_execution_contract: {'pass' if execution_contract.exists() else 'partial'}")
        if p104_mode != "execution" or p104_profile != "experiment_execution" or not node_skill.exists() or not node_sop.exists() or not local_wrapper.exists() or local_execution.exists():
            status["skill"] = "fail"
        local_entry_text = local_entry.read_text(encoding="utf-8") if local_entry.exists() else ""
        research_prompt_text = research_prompt.read_text(encoding="utf-8") if research_prompt.exists() else ""
        node_skill_text = node_skill.read_text(encoding="utf-8") if node_skill.exists() else ""
        node_sop_text = node_sop.read_text(encoding="utf-8") if node_sop.exists() else ""
        local_wrapper_text = local_wrapper.read_text(encoding="utf-8") if local_wrapper.exists() else ""
        contract_payload = load_yaml(execution_contract) if execution_contract.exists() else {}
        contract_mode = contract_payload.get("contract_mode")
        contract_shape_ok = (
            isinstance(contract_payload.get("editable_paths"), list)
            and isinstance(contract_payload.get("metric"), dict)
            and isinstance(contract_payload.get("budget"), dict)
            and contract_mode in {"review_only", "executable"}
            and contract_payload.get("metric", {}).get("direction") is not None
            and contract_payload.get("metric", {}).get("pattern") is not None
            and contract_payload.get("budget", {}).get("max_minutes_per_run") is not None
        )
        p104_entry_ok = entry_matches_mode(local_entry_text, "execution", p104_cfg, wrapper_exists=True, execution_exists=False)
        p104_optional_reads_ok = "optional_local_reads:" in local_entry_text and "required_local_reads:" in local_entry_text
        print(f"P1_04_entry_reads_tier_stack: {'pass' if p104_entry_ok else 'fail'}")
        print(f"P1_04_entry_declares_required_and_optional_reads: {'pass' if p104_optional_reads_ok else 'fail'}")
        print(f"P1_04_entry_targets_local_wrapper: {'pass' if 'local_wrapper_skill: local_wrapper' in local_entry_text else 'fail'}")
        print(f"P1_04_entry_has_contract_prep_fallback: {'pass' if 'canonical_global_skill: experiment_design_or_execution' in local_entry_text else 'fail'}")
        print(f"P1_04_entry_blocks_non_executable_contract: {'pass' if 'contract_mode != executable' in local_entry_text else 'fail'}")
        print(f"P1_04_entry_blocks_missing_repo_path: {'pass' if ('repo_path' in local_entry_text and '路径不存在' in local_entry_text) else 'fail'}")
        print(f"P1_04_entry_allows_executable_contract: {'pass' if 'contract_mode == executable' in local_entry_text else 'fail'}")
        print(f"P1_04_research_prompt_compact: {'pass' if (research_prompt.exists() and has_heading_contract(research_prompt_text, RESEARCH_PROMPT_REQUIRED_HEADINGS, RESEARCH_PROMPT_BANNED_HEADINGS) and RESEARCH_PROMPT_DONE_LINE in research_prompt_text) else 'fail'}")
        print(f"P1_04_node_skill_structure: {'pass' if has_heading_contract(node_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS) else 'fail'}")
        print(f"P1_04_node_sop_structure: {'pass' if has_heading_contract(node_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS) else 'fail'}")
        print(f"P1_04_wrapper_targets_auto_worker: {'pass' if 'canonical_target: auto_experiment_worker' in local_wrapper_text else 'fail'}")
        print(f"P1_04_wrapper_mentions_execution_contract: {'pass' if 'artifacts/execution_contract.yaml' in local_wrapper_text else 'fail'}")
        print(f"P1_04_wrapper_requires_existing_repo_binding: {'pass' if ('repo_path' in local_wrapper_text and 'exists in the workspace' in local_wrapper_text) else 'fail'}")
        print(f"P1_04_execution_contract_shape: {'pass' if contract_shape_ok else 'fail'}")
        print(f"P1_04_execution_contract_mode: {'pass' if contract_mode in {'review_only', 'executable'} else 'fail'}")
        if (
            not p104_entry_ok
            or not p104_optional_reads_ok
            or
            "local_wrapper_skill: local_wrapper" not in local_entry_text
            or "canonical_global_skill: experiment_design_or_execution" not in local_entry_text
            or "contract_mode != executable" not in local_entry_text
            or "路径不存在" not in local_entry_text
            or "contract_mode == executable" not in local_entry_text
            or not research_prompt.exists()
            or not has_heading_contract(research_prompt_text, RESEARCH_PROMPT_REQUIRED_HEADINGS, RESEARCH_PROMPT_BANNED_HEADINGS)
            or RESEARCH_PROMPT_DONE_LINE not in research_prompt_text
            or not has_heading_contract(node_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS)
            or not has_heading_contract(node_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS)
            or "canonical_target: auto_experiment_worker" not in local_wrapper_text
            or "artifacts/execution_contract.yaml" not in local_wrapper_text
            or "repo_path" not in local_wrapper_text
            or "exists in the workspace" not in local_wrapper_text
        ):
            status["skill"] = "fail"
        if execution_contract.exists() and not contract_shape_ok:
            status["skill"] = "fail"
        if not execution_contract.exists() and status["skill"] == "pass":
            status["skill"] = "partial"
        if execution_contract.exists() and contract_mode == "review_only" and status["skill"] == "pass":
            status["skill"] = "pass"
        if execution_contract.exists() and contract_mode == "executable" and status["skill"] == "pass":
            status["skill"] = "pass"
    else:
        print("P1_04_experiment_node: partial")
        if status["skill"] == "pass":
            status["skill"] = "partial"

    p105 = root / "research" / "P1_实验设计与仓库蓝图" / "P1_05_初步验证结果整理"
    p105_entry = p105 / "skills" / "local_entry.md"
    p105_skill = p105 / "skills" / "SKILL.md"
    p105_sop = p105 / "skills" / "SOP.md"
    p105_execution = p105 / "skills" / "local_execution.md"
    if p105.exists():
        p105_mode = node_mode_for("research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理", local_skill_overrides_payload)
        p105_profile = execution_profile_for("research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理", local_skill_overrides_payload)
        p105_entry_text = p105_entry.read_text(encoding="utf-8") if p105_entry.exists() else ""
        p105_skill_text = p105_skill.read_text(encoding="utf-8") if p105_skill.exists() else ""
        p105_sop_text = p105_sop.read_text(encoding="utf-8") if p105_sop.exists() else ""
        p105_execution_text = p105_execution.read_text(encoding="utf-8") if p105_execution.exists() else ""
        print(f"P1_05_node_mode_execution: {'pass' if p105_mode == 'execution' else 'fail'}")
        print(f"P1_05_node_profile_result_synthesis: {'pass' if p105_profile == 'result_synthesis' else 'fail'}")
        print(f"P1_05_local_execution_present: {'pass' if p105_execution.exists() else 'fail'}")
        print(f"P1_05_entry_declares_required_and_optional_reads: {'pass' if ('required_local_reads:' in p105_entry_text and 'optional_local_reads:' in p105_entry_text) else 'fail'}")
        p105_upstream_ledger = "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv"
        print(f"P1_05_upstream_result_ledger_required: {'pass' if p105_upstream_ledger in p105_entry_text and p105_upstream_ledger in p105_execution_text else 'fail'}")
        print(f"P1_05_execution_contract_removed: {'pass' if 'execution contract' not in p105_execution_text.lower() else 'fail'}")
        print(f"P1_05_node_skill_structure: {'pass' if has_heading_contract(p105_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS) else 'fail'}")
        print(f"P1_05_node_sop_structure: {'pass' if has_heading_contract(p105_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS) else 'fail'}")
        if (
            p105_mode != "execution"
            or p105_profile != "result_synthesis"
            or not p105_execution.exists()
            or "required_local_reads:" not in p105_entry_text
            or "optional_local_reads:" not in p105_entry_text
            or p105_upstream_ledger not in p105_entry_text
            or p105_upstream_ledger not in p105_execution_text
            or "execution contract" in p105_execution_text.lower()
            or not has_heading_contract(p105_skill_text, NODE_SKILL_REQUIRED_HEADINGS, NODE_SKILL_BANNED_HEADINGS)
            or not has_heading_contract(p105_sop_text, NODE_SOP_REQUIRED_HEADINGS, NODE_SOP_BANNED_HEADINGS)
        ):
            status["skill"] = "fail"

    print_header("verdict")
    print(f"backend={status['backend']}")
    print(f"frontend={status['frontend']}")
    print(f"skill={status['skill']}")

    if any(value != "pass" for value in status.values()):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
