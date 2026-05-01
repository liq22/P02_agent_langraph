#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

LEGACY_MINIMAL_ENTRY_BODY = "Use implicit local-entry conventions from the registry. Keep this node-local and bounded."
PROMPT_ASSETS = (
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


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def print_section(title: str) -> None:
    print(f"\n== {title} ==")


def run(cmd: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def path_to_node_id(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix().replace("/", "::")


def ensure_minimal_acceptance_checklists(root: Path) -> None:
    research_root = root / "research"
    for readme in research_root.glob("**/README.md"):
        node = readme.parent
        if not (node / "status.yaml").is_file():
            continue
        checklist = node / "prompts" / "acceptance_checklist.yaml"
        if checklist.exists():
            continue
        checklist.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "node_id": path_to_node_id(node, root),
            "node_path": node.relative_to(root).as_posix(),
            "phase": node.parts[-2].split("_", 1)[0] if len(node.parts) >= 2 else "P9",
            "node_kind": "parent" if any((child / "README.md").is_file() and (child / "status.yaml").is_file() for child in node.iterdir() if child.is_dir()) else "leaf",
            "prompt_assets": [
                {"path": "prompts/research_prompt.md", "status": "required"},
                {"path": "prompts/acceptance_checklist.yaml", "status": "required"},
            ],
            "stop_if": [{"item": "fixture_missing_inputs", "status": "pending"}],
        }
        checklist.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def entry_matches_execution_mode(entry_text: str) -> bool:
    return (
        LEGACY_MINIMAL_ENTRY_BODY not in entry_text
        and all(asset in entry_text for asset in PROMPT_ASSETS)
        and "skills/SKILL.md" in entry_text
        and "skills/SOP.md" in entry_text
        and "skills/local_wrapper.md" in entry_text
    )


def has_heading_contract(text: str, required: tuple[str, ...], banned: tuple[str, ...]) -> bool:
    return all(item in text for item in required) and all(item not in text for item in banned)


def check_equal(name: str, actual: dict, expected: dict) -> tuple[bool, str]:
    if actual == expected:
        return True, f"{name}: pass"
    return False, f"{name}: fail\nexpected={json.dumps(expected, ensure_ascii=False, indent=2)}\nactual={json.dumps(actual, ensure_ascii=False, indent=2)}"


def main() -> int:
    root = repo_root()
    fixture_src = root / "test" / "fixtures" / "min_experiment_stack_repo"
    regenerate_local_skills = root / "scripts" / "regenerate_local_skills.py"
    validate_local_skills = root / "scripts" / "validate_local_skills.py"
    refresh_script = root / "scripts" / "refresh_hypergraph.py"
    refresh_views_script = root / "scripts" / "refresh_views.py"
    canvas_script = root / "scripts" / "build_canvas_from_graph.py"
    orchestrator = root / ".agent" / "skills" / "graph_driven_research_orchestrator" / "SKILL.md"
    auto_campaign = root / ".agent" / "skills" / "auto_research_campaign" / "SKILL.md"
    auto_worker = root / ".agent" / "skills" / "auto_experiment_worker" / "SKILL.md"
    external_reviewer = root / ".agent" / "skills" / "external_node_reviewer" / "SKILL.md"
    entry_matrix = root / "docs" / "architecture" / "entry_matrix.md"
    refresh_modes = root / "docs" / "architecture" / "refresh_modes.md"
    contract_template = root / "templates" / "execution_contract.template.yaml"
    node_tier_policy = fixture_src / "backend" / "registry" / "skill_registry" / "node_tier_policy.yaml"
    local_skill_overrides = fixture_src / "backend" / "registry" / "skill_registry" / "local_skill_overrides.yaml"

    required = [
        fixture_src,
        node_tier_policy,
        local_skill_overrides,
        regenerate_local_skills,
        validate_local_skills,
        refresh_script,
        refresh_views_script,
        canvas_script,
        orchestrator,
        auto_campaign,
        auto_worker,
        external_reviewer,
        entry_matrix,
        refresh_modes,
        contract_template,
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("fixture acceptance: fail")
        print("missing paths:")
        for path in missing:
            print(f"- {path}")
        return 1

    all_ok = True
    with tempfile.TemporaryDirectory(prefix="experiment_stack_fixture_") as tmpdir:
        fixture_root = Path(tmpdir) / "repo"
        shutil.copytree(fixture_src, fixture_root)
        ensure_minimal_acceptance_checklists(fixture_root)

        print_section("local skill generation")
        proc = run([sys.executable, str(regenerate_local_skills), "--root", str(fixture_root)], root)
        print(proc.stdout.strip() or proc.stderr.strip())
        if proc.returncode != 0:
            return 1
        proc = run([sys.executable, str(validate_local_skills), "--root", str(fixture_root)], root)
        print(proc.stdout.strip() or proc.stderr.strip())
        if proc.returncode != 0:
            return 1

        print_section("backend refresh")
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        print(proc.stdout.strip())
        if proc.returncode != 0:
            print(proc.stderr.strip())
            return 1

        graph_actual = load_json(fixture_root / "backend" / "graph" / "graph.json")
        graph_expected = load_json(fixture_root / "backend" / "graph" / "graph.expected.json")
        ok, msg = check_equal("graph.json", graph_actual, graph_expected)
        print(msg)
        all_ok &= ok

        status_actual = load_json(fixture_root / "backend" / "graph" / "graph_status.json")
        status_expected = load_json(fixture_root / "backend" / "graph" / "graph_status.expected.json")
        ok, msg = check_equal("graph_status.json", status_actual, status_expected)
        print(msg)
        all_ok &= ok
        leaf_only_frontier = (
            status_actual.get("current_phase") == "P1"
            and status_actual.get("unfinished_count") == 3
            and all(not str(node_id).startswith("research::P0_parent") for node_id in status_actual.get("ready_nodes", []))
            and all(not str(node_id).startswith("research::P0_parent") for node_id in status_actual.get("blocked_nodes", []))
        )
        print(f"leaf_only_frontier_ignores_seed_parent: {'pass' if leaf_only_frontier else 'fail'}")
        all_ok &= leaf_only_frontier

        print_section("cycle-safe failure")
        good_graph = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8")
        good_status = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8")
        edge_registry = load_json(fixture_root / "backend" / "relations" / "edge_registry.json")
        edge_registry["edges"].append(
            {
                "src": "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证",
                "rel": "depends_on",
                "dst": "research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理",
            }
        )
        (fixture_root / "backend" / "relations" / "edge_registry.json").write_text(
            json.dumps(edge_registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        cycle_ok = proc.returncode != 0
        graph_preserved = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8") == good_graph
        status_preserved = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8") == good_status
        print(f"cycle_detected_failure: {'pass' if cycle_ok else 'fail'}")
        print(f"graph_preserved: {'pass' if graph_preserved else 'fail'}")
        print(f"graph_status_preserved: {'pass' if status_preserved else 'fail'}")
        all_ok &= cycle_ok and graph_preserved and status_preserved

        fixture_root = Path(tmpdir) / "repo"
        shutil.rmtree(fixture_root)
        shutil.copytree(fixture_src, fixture_root)
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        if proc.returncode != 0:
            print("refresh restore failed")
            print(proc.stderr.strip())
            return 1

        print_section("bad edge guard")
        good_graph = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8")
        good_status = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8")
        edge_registry = load_json(fixture_root / "backend" / "relations" / "edge_registry.json")
        edge_registry["edges"].append(
            {
                "src": "research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理",
                "rel": "soft_depends_on",
                "dst": "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证",
            }
        )
        (fixture_root / "backend" / "relations" / "edge_registry.json").write_text(
            json.dumps(edge_registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        bad_edge_ok = proc.returncode != 0 and "invalid relation" in proc.stderr
        graph_preserved = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8") == good_graph
        status_preserved = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8") == good_status
        print(f"bad_edge_rejected: {'pass' if bad_edge_ok else 'fail'}")
        print(f"graph_preserved: {'pass' if graph_preserved else 'fail'}")
        print(f"graph_status_preserved: {'pass' if status_preserved else 'fail'}")
        all_ok &= bad_edge_ok and graph_preserved and status_preserved

        fixture_root = Path(tmpdir) / "repo"
        shutil.rmtree(fixture_root)
        shutil.copytree(fixture_src, fixture_root)
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        if proc.returncode != 0:
            print("refresh restore failed")
            print(proc.stderr.strip())
            return 1

        print_section("parent dependency guard")
        good_graph = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8")
        good_status = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8")
        edge_registry = load_json(fixture_root / "backend" / "relations" / "edge_registry.json")
        edge_registry["edges"].append(
            {
                "src": "research/P0_parent",
                "rel": "depends_on",
                "dst": "research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证",
            }
        )
        (fixture_root / "backend" / "relations" / "edge_registry.json").write_text(
            json.dumps(edge_registry, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        parent_guard_ok = proc.returncode != 0 and "depends_on edges must connect leaf nodes" in proc.stderr
        graph_preserved = (fixture_root / "backend" / "graph" / "graph.json").read_text(encoding="utf-8") == good_graph
        status_preserved = (fixture_root / "backend" / "graph" / "graph_status.json").read_text(encoding="utf-8") == good_status
        print(f"parent_depends_on_rejected: {'pass' if parent_guard_ok else 'fail'}")
        print(f"graph_preserved: {'pass' if graph_preserved else 'fail'}")
        print(f"graph_status_preserved: {'pass' if status_preserved else 'fail'}")
        all_ok &= parent_guard_ok and graph_preserved and status_preserved

        fixture_root = Path(tmpdir) / "repo"
        shutil.rmtree(fixture_root)
        shutil.copytree(fixture_src, fixture_root)

        print_section("paper gate route override")
        write_text(fixture_root / "research" / "P0_parent" / "P0_02_seed" / "README.md", "# P0_02_seed\n")
        write_yaml(
            fixture_root / "research" / "P0_parent" / "P0_02_seed" / "status.yaml",
            {"lifecycle": {"stage": "seed"}},
        )
        write_text(fixture_root / "research" / "P3_论文模拟评审与修改_多轮" / "README.md", "# P3_论文模拟评审与修改_多轮\n")
        write_yaml(
            fixture_root / "research" / "P3_论文模拟评审与修改_多轮" / "status.yaml",
            {
                "lifecycle": {"stage": "active"},
                "paper_iteration_gate": {
                    "readiness": "blocked",
                    "next_route": [
                        "research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理",
                    ],
                },
            },
        )
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        override_status = load_json(fixture_root / "backend" / "graph" / "graph_status.json") if proc.returncode == 0 else {}
        override_ok = (
            proc.returncode == 0
            and override_status.get("current_phase") == "P1"
            and override_status.get("ready_nodes") == ["research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证"]
            and override_status.get("next_node") == "research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证"
        )
        print(f"paper_gate_route_override: {'pass' if override_ok else 'fail'}")
        all_ok &= override_ok

        fixture_root = Path(tmpdir) / "repo"
        shutil.rmtree(fixture_root)
        shutil.copytree(fixture_src, fixture_root)

        print_section("paper gate invalid fallback")
        write_text(fixture_root / "research" / "P0_parent" / "P0_02_seed" / "README.md", "# P0_02_seed\n")
        write_yaml(
            fixture_root / "research" / "P0_parent" / "P0_02_seed" / "status.yaml",
            {"lifecycle": {"stage": "seed"}},
        )
        write_text(fixture_root / "research" / "P3_论文模拟评审与修改_多轮" / "README.md", "# P3_论文模拟评审与修改_多轮\n")
        write_yaml(
            fixture_root / "research" / "P3_论文模拟评审与修改_多轮" / "status.yaml",
            {
                "lifecycle": {"stage": "active"},
                "paper_iteration_gate": {
                    "readiness": "blocked",
                    "next_route": [
                        "research/P9_missing_phase/P9_missing_node",
                    ],
                },
            },
        )
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        fallback_status = load_json(fixture_root / "backend" / "graph" / "graph_status.json") if proc.returncode == 0 else {}
        fallback_ok = (
            proc.returncode == 0
            and fallback_status.get("current_phase") == "P0"
            and fallback_status.get("ready_nodes") == ["research::P0_parent::P0_02_seed"]
            and fallback_status.get("next_node") == "research::P0_parent::P0_02_seed"
        )
        print(f"paper_gate_invalid_fallback: {'pass' if fallback_ok else 'fail'}")
        all_ok &= fallback_ok

        fixture_root = Path(tmpdir) / "repo"
        shutil.rmtree(fixture_root)
        shutil.copytree(fixture_src, fixture_root)
        proc = run([sys.executable, str(refresh_script), "--root", str(fixture_root)], root)
        if proc.returncode != 0:
            print("refresh restore failed")
            print(proc.stderr.strip())
            return 1
        proc = run([sys.executable, str(regenerate_local_skills), "--root", str(fixture_root)], root)
        if proc.returncode != 0:
            print("local skill regeneration restore failed")
            print(proc.stdout.strip() or proc.stderr.strip())
            return 1
        proc = run([sys.executable, str(validate_local_skills), "--root", str(fixture_root)], root)
        if proc.returncode != 0:
            print("local skill validation restore failed")
            print(proc.stdout.strip() or proc.stderr.strip())
            return 1

        print_section("refresh_views entry")
        proc = run(
            [sys.executable, str(refresh_views_script), "--root", str(fixture_root), "--mode", "graph_only"],
            root,
        )
        refresh_graph_only_ok = proc.returncode == 0
        print(proc.stdout.strip() or proc.stderr.strip())
        all_ok &= refresh_graph_only_ok
        graph_only_canvas_absent = not (fixture_root / "obsidian" / "canvases" / "research_overview.canvas").exists()
        print(f"refresh_views_graph_only_skips_canvas: {'pass' if graph_only_canvas_absent else 'fail'}")
        all_ok &= graph_only_canvas_absent

        proc = run([sys.executable, str(refresh_views_script), "--root", str(fixture_root), "--mode", "full"], root)
        refresh_views_ok = proc.returncode == 0
        print(proc.stdout.strip() or proc.stderr.strip())
        all_ok &= refresh_views_ok

        if refresh_views_ok:
            node_details_payload = load_json(fixture_root / "backend" / "graph" / "node_details.json")
            scope_rollup_payload = load_json(fixture_root / "backend" / "graph" / "scope_rollup.json")
            board_state_payload = load_json(fixture_root / "backend" / "graph" / "board_state.json")
            details = node_details_payload.get("nodes", {}) if isinstance(node_details_payload.get("nodes", {}), dict) else {}
            rollups = scope_rollup_payload.get("scopes", {}) if isinstance(scope_rollup_payload.get("scopes", {}), dict) else {}
            lanes = board_state_payload.get("lanes", {}) if isinstance(board_state_payload.get("lanes", {}), dict) else {}
            truth_fields_ok = bool(details) and all(
                isinstance(detail, dict)
                and detail.get("kind") in {"parent", "leaf"}
                and isinstance(detail.get("scheduler_ready"), bool)
                and isinstance(detail.get("truth_ready"), bool)
                and detail.get("review_gate_state") in {"not_required", "missing_verdict", "incomplete", "failed", "passed"}
                and detail.get("execution_gate_state") in {"not_applicable", "missing_contract", "review_only", "contract_incomplete", "missing_outputs", "failed", "ready"}
                and detail.get("handoff_readiness") in {"ready", "blocked_truth", "blocked_review", "blocked_execution", "blocked_parent_rollup", "blocked_unknown"}
                and isinstance(detail.get("blocking_reasons"), list)
                and detail.get("placeholder_risk") in {"none", "suspected", "confirmed"}
                for detail in details.values()
            )
            rollup_truth_ok = bool(rollups) and all(
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
                for payload in rollups.values()
                if isinstance(payload, dict)
            )
            board_truth_ok = set(lanes.keys()) == {
                "scheduler_now",
                "truth_ready",
                "review_blocked",
                "execution_blocked",
                "truth_blocked",
                "active_work",
                "parked",
            }
            print(f"node_details_truth_fields: {'pass' if truth_fields_ok else 'fail'}")
            print(f"scope_rollup_truth_counts: {'pass' if rollup_truth_ok else 'fail'}")
            print(f"board_state_truth_lanes: {'pass' if board_truth_ok else 'fail'}")
            all_ok &= truth_fields_ok and rollup_truth_ok and board_truth_ok

        print_section("canvas projection")
        proc = run([sys.executable, str(canvas_script), "--root", str(fixture_root), "--dry-run"], root)
        dry_run_ok = proc.returncode == 0
        print(proc.stdout.strip() or proc.stderr.strip())
        all_ok &= dry_run_ok

        proc = run([sys.executable, str(canvas_script), "--root", str(fixture_root)], root)
        full_run_ok = proc.returncode == 0
        print(proc.stdout.strip() or proc.stderr.strip())
        all_ok &= full_run_ok

        overview = fixture_root / "obsidian" / "canvases" / "research_overview.canvas"
        focus = fixture_root / "obsidian" / "canvases" / "current_focus.canvas"
        workbench = fixture_root / "obsidian" / "canvases" / "framework_workbench.canvas"
        for path in (overview, focus, workbench):
            print(f"{path.relative_to(fixture_root)}: {'pass' if path.exists() else 'fail'}")
            all_ok &= path.exists()

        if overview.exists():
            overview_payload = load_json(overview)
            file_nodes = [node for node in overview_payload.get("nodes", []) if node.get("type") == "file"]
            has_readme = any(str(node.get("file", "")).endswith("/README.md") for node in file_nodes)
            print(f"overview_file_first_navigation: {'pass' if has_readme else 'fail'}")
            all_ok &= has_readme

        print_section("skill handoff signals")
        local_entry = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "skills" / "local_entry.md"
        node_skill = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "skills" / "SKILL.md"
        node_sop = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "skills" / "SOP.md"
        local_wrapper = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "skills" / "local_wrapper.md"
        local_execution = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "skills" / "local_execution.md"
        contract = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "artifacts" / "execution_contract.yaml"
        research_prompt = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "prompts" / "research_prompt.md"
        acceptance = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "prompts" / "acceptance_checklist.yaml"
        review_rubric = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "prompts" / "review_rubric.yaml"
        review_verdict = fixture_root / "research" / "P1_实验设计与仓库蓝图" / "P1_04_核心想法轻量验证" / "review" / "verdict.yaml"
        local_entry_text = local_entry.read_text(encoding="utf-8") if local_entry.exists() else ""
        node_skill_text = node_skill.read_text(encoding="utf-8") if node_skill.exists() else ""
        node_sop_text = node_sop.read_text(encoding="utf-8") if node_sop.exists() else ""
        research_prompt_text = research_prompt.read_text(encoding="utf-8") if research_prompt.exists() else ""
        local_wrapper_text = local_wrapper.read_text(encoding="utf-8") if local_wrapper.exists() else ""
        contract_payload = load_yaml(contract) if contract.exists() else {}
        acceptance_payload = load_yaml(acceptance) if acceptance.exists() else {}
        review_rubric_payload = load_yaml(review_rubric) if review_rubric.exists() else {}
        review_verdict_payload = load_yaml(review_verdict) if review_verdict.exists() else {}
        research_prompt_heading_ok = has_heading_contract(
            research_prompt_text,
            RESEARCH_PROMPT_REQUIRED_HEADINGS,
            RESEARCH_PROMPT_BANNED_HEADINGS,
        )
        research_prompt_compact_ok = (
            research_prompt.exists()
            and research_prompt_heading_ok
            and RESEARCH_PROMPT_DONE_LINE in research_prompt_text
        )
        if research_prompt.exists() and not research_prompt_compact_ok:
            missing_headings = [item for item in RESEARCH_PROMPT_REQUIRED_HEADINGS if item not in research_prompt_text]
            banned_headings = [item for item in RESEARCH_PROMPT_BANNED_HEADINGS if item in research_prompt_text]
            done_line_present = RESEARCH_PROMPT_DONE_LINE in research_prompt_text
            print(
                "research_prompt_compact_debug: "
                f"missing={missing_headings} banned={banned_headings} done_line={done_line_present}"
            )
        contract_shape_ok = (
            contract_payload.get("contract_mode") == "executable"
            and isinstance(contract_payload.get("editable_paths"), list)
            and isinstance(contract_payload.get("metric"), dict)
            and isinstance(contract_payload.get("budget"), dict)
            and contract_payload.get("metric", {}).get("direction") is not None
            and contract_payload.get("metric", {}).get("pattern") is not None
            and contract_payload.get("budget", {}).get("max_minutes_per_run") is not None
        )

        checks = {
            "fixture_node_tier_policy_exists": node_tier_policy.exists(),
            "fixture_local_skill_overrides_exist": local_skill_overrides.exists(),
            "local_entry_exists": local_entry.exists(),
            "node_skill_exists": node_skill.exists(),
            "node_sop_exists": node_sop.exists(),
            "research_prompt_exists": research_prompt.exists(),
            "research_prompt_compact": research_prompt_compact_ok,
            "acceptance_checklist_exists": acceptance.exists(),
            "review_rubric_exists": review_rubric.exists(),
            "review_verdict_exists": review_verdict.exists(),
            "review_rubric_targets_external_reviewer": review_rubric_payload.get("reviewer_role") == "external_node_reviewer",
            "acceptance_declares_external_review_gate": acceptance_payload.get("external_review_gate", {}).get("required") is True
            and acceptance_payload.get("external_review_gate", {}).get("reviewer_role") == "external_node_reviewer",
            "review_verdict_template_targets_external_reviewer": review_verdict_payload.get("reviewer_skill") == "external_node_reviewer",
            "review_verdict_template_incomplete_by_default": review_verdict_payload.get("review_complete") is False
            and review_verdict_payload.get("independence_confirmed") is False,
            "local_wrapper_exists": local_wrapper.exists(),
            "stale_local_execution_removed": not local_execution.exists(),
            "execution_contract_exists": contract.exists(),
            "execution_contract_mode_executable": contract_payload.get("contract_mode") == "executable",
            "execution_contract_shape_canonical": contract_shape_ok,
            "local_entry_is_execution_tier_shim": entry_matches_execution_mode(local_entry_text),
            "local_entry_declares_local_wrapper": "local_wrapper_skill: local_wrapper" in local_entry_text,
            "local_entry_fallbacks_to_contract_prep": "canonical_global_skill: experiment_design_or_execution" in local_entry_text,
            "local_entry_blocks_non_executable_contract": "contract_mode != executable" in local_entry_text,
            "local_entry_allows_executable_contract": "contract_mode == executable" in local_entry_text,
            "node_skill_declares_execution_mode": "- node_mode: `execution`" in node_skill_text,
            "node_skill_has_tier_aware_structure": has_heading_contract(
                node_skill_text,
                NODE_SKILL_REQUIRED_HEADINGS,
                NODE_SKILL_BANNED_HEADINGS,
            ),
            "node_sop_has_compact_structure": has_heading_contract(
                node_sop_text,
                NODE_SOP_REQUIRED_HEADINGS,
                NODE_SOP_BANNED_HEADINGS,
            ),
            "local_wrapper_targets_auto_worker": "canonical_target: auto_experiment_worker" in local_wrapper_text,
            "local_wrapper_binds_contract": "artifacts/execution_contract.yaml" in local_wrapper_text,
            "orchestrator_exists": orchestrator.exists(),
            "auto_campaign_exists": auto_campaign.exists(),
            "auto_worker_exists": auto_worker.exists(),
            "fixture_next_node_is_experiment_node": status_expected["next_node"] == "research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证",
        }
        for name, ok in checks.items():
            print(f"{name}: {'pass' if ok else 'fail'}")
            all_ok &= ok

    print_section("fixture acceptance verdict")
    if all_ok:
        print("PASS")
        return 0
    print("FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
