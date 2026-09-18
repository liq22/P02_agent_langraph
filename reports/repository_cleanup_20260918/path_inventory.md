# Path-by-path cleanup inventory

Scope: 219 user-listed paths. Every line below is an explicit disposition; no unlisted file is implicitly deleted.

## ARCHIVE_OUTSIDE_ACTIVE_REPO (10)

- `_reference`
- `obsidian`
- `obsidian/canvases`
- `obsidian/inbox`
- `obsidian/README.md`
- `research`
- `research/P0_项目申请书`
- `research/P1_实验设计与仓库蓝图`
- `research/P3_论文模拟评审与修改_多轮`
- `research/P4_论文回复_response`

## ARCHIVE_THEN_REMOVE (86)

- `.agent`
- `.agents`
- `.claude`
- `.claude/agents`
- `.claude/skills`
- `.codex`
- `config/agent_gateway.yaml.example`
- `config/jargon_rules.yaml`
- `docs/analysis`
- `docs/architecture`
- `docs/desktop`
- `docs/plan`
- `docs/progress`
- `docs/submission_ready_goal`
- `goal`
- `goal/p02_submission_ready_goal_package`
- `goal/p02_submission_ready_goal_package/claude_code_assets`
- `goal/p02_submission_ready_goal_package/docs`
- `goal/p02_submission_ready_goal_package/tools`
- `goal/p02_submission_ready_goal_package/AGENTS.md`
- `goal/p02_submission_ready_goal_package/INSTALL.md`
- `goal/p02_submission_ready_goal_package/PACKAGE_MANIFEST.md`
- `goal/p02_submission_ready_goal_package/README.md`
- `scripts/bootstrap_agent_app.sh`
- `scripts/build_board_state.py`
- `scripts/build_canvas_from_graph.py`
- `scripts/build_hierarchy_projection.py`
- `scripts/build_node_details.py`
- `scripts/build_nodebench.py`
- `scripts/build_scope_rollup.py`
- `scripts/dev_start_agent_app.sh`
- `scripts/evaluate_node.py`
- `scripts/forge_research_pack.py`
- `scripts/generate_agent_skill_wrappers.py`
- `scripts/intake_research_materials.py`
- `scripts/inventory_repo.py`
- `scripts/lint_jargon.py`
- `scripts/node_tier.py`
- `scripts/refresh_hypergraph.py`
- `scripts/refresh_views.py`
- `scripts/regenerate_local_skills.py`
- `scripts/run_node_harness.py`
- `scripts/S_01_moctree.py`
- `scripts/scan_duplicate_semantics.py`
- `scripts/setup_venv.py`
- `scripts/sync_agent_skill_wrappers.sh`
- `scripts/validate_context_hygiene.py`
- `scripts/validate_graph.py`
- `scripts/validate_local_skills.py`
- `scripts/validate_node_contracts.py`
- `scripts/validate_research_truth.py`
- `scripts/validate_schema_use.py`
- `scripts/validate_skill_fit.py`
- `scripts/validate_skill_refs.py`
- `scripts/validate_template_first_run.py`
- `test`
- `test/cases`
- `test/fixtures`
- `test/skills`
- `test/FULL_PIPELINE_TEST_PLAN.md`
- `test/gateway_fixture.py`
- `test/NATURE_LEVEL_NODE_RUBRIC.md`
- `test/README.md`
- `test/requirements-browser.txt`
- `test/run_all_acceptance.py`
- `test/run_browser_smoke.py`
- `test/run_context_hygiene_acceptance.py`
- `test/run_fixture_acceptance.py`
- `test/run_gateway_acceptance.py`
- `test/run_live_repo_smoke.py`
- `test/run_nature_capability_acceptance.py`
- `test/run_nature_rubric_presence.py`
- `test/TESTING_QUICKSTART.md`
- `tests/nodebench`
- `tools`
- `tools/submission_ready_goal`
- `tools/submission_ready_goal/audit_data_resource_pack.py`
- `tools/submission_ready_goal/README.md`
- `tools/submission_ready_goal/validate_claude_handoff.py`
- `tools/submission_ready_goal/validate_goal_fsm_state.py`
- `tools/submission_ready_goal/validate_p1_01_node_outputs.py`
- `tools/submission_ready_goal/validate_p1_01_node_package.py`
- `tools/submission_ready_goal/validate_submission_gate.py`
- `tools/submission_ready_goal/validate_traceability_lock.py`
- `tools/submission_ready_goal/verify_llm_keys.py`
- `web`

## AUDIT_AND_SPLIT (4)

- `config` → `Benchmark configs/ or remove`
- `docs` → `P02 paper docs / archive`
- `scripts` → `Benchmark execution scripts / P02 render scripts`
- `tests` → `Benchmark tests/ or P02 paper checks`

## AUDIT_THEN_REMOVE (15)

- `backend`
- `backend/agent_gateway`
- `backend/evaluators`
- `backend/graph`
- `backend/harness`
- `backend/indexes`
- `backend/registry`
- `backend/relations`
- `backend/views`
- `templates`
- `templates/nodes`
- `templates/scoring`
- `templates/shared`
- `templates/execution_contract.template.yaml`
- `templates/README.md`

## DELETE_LOCAL_GENERATED (11)

- `.claude/settings.local.json`
- `.venv`
- `.venv/bin`
- `.venv/include`
- `.venv/include/python3.11`
- `.venv/lib`
- `.venv/lib64`
- `.venv/pyvenv.cfg`
- `scripts/__pycache__`
- `tests/__pycache__`
- `.env`

## DISTILL_THEN_ARCHIVE (5)

- `docs/architecture.md` → `README/DEV if unique`
- `docs/CODEX_ONLY_WORKFLOW.md` → `README/DEV if unique`
- `docs/framework_outline_and_innovations.md` → `paper/RESEARCH.md`
- `docs/USER_GUIDEBOOK.md` → `README/DEV if unique`
- `research/P2_论文撰写` → `paper/review or paper/draft`

## KEEP_MINIMAL (8)

- `docs/dev.md` → `P02 docs/`
- `docs/UPDATE_GUIDE_CN.md` → `P02 docs/`
- `scripts/README.md` → `P02 scripts/README.md`
- `AGENTS.md` → `P02 root`
- `CLAUDE.md` → `P02 root`
- `CORE.md` → `P02 root`
- `README_CN.md` → `P02 root`
- `README.md` → `P02 root`

## KEEP_P02 (14)

- `paper` → `P02 paper/`
- `paper/draft` → `P02 paper/draft`
- `paper/refs` → `P02 paper/refs`
- `paper/theory` → `P02 paper/theory`
- `paper/GOAL.md` → `P02 paper/`
- `paper/literature_matrix.md` → `P02 paper/`
- `paper/paper.yaml` → `P02 paper/`
- `paper/RESEARCH.md` → `P02 paper/`
- `tests/test_graph_manuscript_table.py` → `P02 tests/`
- `tests/test_render_graph_cross_dataset_manuscript.py` → `P02 tests/`
- `tests/test_render_graph_dynamic_manuscript.py` → `P02 tests/`
- `tests/test_render_graph_reliability_manuscript.py` → `P02 tests/`
- `.gitignore` → `P02 root`
- `LICENSE` → `P02 root`

## KEEP_P02_THIN (6)

- `scripts/make_graph_figure.py` → `P02 scripts/`
- `scripts/render_current_mechanics_evidence.py` → `P02 scripts/`
- `scripts/render_graph_cross_dataset_manuscript.py` → `P02 scripts/`
- `scripts/render_graph_dynamic_manuscript.py` → `P02 scripts/`
- `scripts/render_graph_manuscript_table.py` → `P02 scripts/`
- `scripts/render_graph_reliability_manuscript.py` → `P02 scripts/`

## KEEP_SELECTIVE (2)

- `paper/assets` → `P02 paper/assets`
- `changelog.md` → `P02 root`

## KEEP_TEMPORARILY (11)

- `reports` → `P02 reports/`
- `reports/occam_prune` → `P02 reports/`
- `reports/occam_prune/after_phase1_inventory.json` → `P02 reports/`
- `reports/occam_prune/baseline_duplicate_semantics.json` → `P02 reports/`
- `reports/occam_prune/baseline_inventory.json` → `P02 reports/`
- `reports/occam_prune/baseline_node_contracts.json` → `P02 reports/`
- `reports/occam_prune/baseline_schema_use.json` → `P02 reports/`
- `reports/occam_prune/baseline_skill_refs.json` → `P02 reports/`
- `reports/occam_prune/baseline_summary.md` → `P02 reports/`
- `reports/occam_prune/baseline_template_first_run.json` → `P02 reports/`
- `SUPERSEDED.md` → `P02 root`

## MOVE_THEN_REMOVE_DUPLICATE (44)

- `scripts/analyze_graph_cross_dataset_replay.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/analyze_graph_dynamic_formal.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/analyze_graph_reliability.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/analyze_p2_e0_adapter_equivalence.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/analyze_p2_e0_generic_base_adapter_equivalence_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/audit_p2_e1_primary_readiness_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/audit_p2_e1_primary_readiness.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/finalize_p2_e1_generic_base_formal_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/run_graph_dynamic_formal_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/run_graph_dynamic_mock_acceptance.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/run_graph_experiment.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/run_graph_reliability_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/schedule_graph_cross_dataset_replay.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/schedule_graph_dynamic_formal_v2.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/schedule_graph_horizon_scaling.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/schedule_graph_reliability.py` → `liq22/phm-agent-benchmark/experiments or research`
- `scripts/summarize_graph_states.py` → `liq22/phm-agent-benchmark/experiments or research`
- `src` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `src/phm_graph_agent` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `src/phm_graph_agent/__init__.py` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `src/phm_graph_agent/agent.py` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `src/phm_graph_agent/dynamic_runtime.py` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `src/phm_graph_agent/state.py` → `liq22/phm-agent-benchmark/src/phm_graph_agent`
- `tests/test_graph_cross_dataset_analysis.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_cross_dataset_replay_scheduler.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_cross_dataset_runtime.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_execution.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_formal_analysis.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_formal_runner_v2.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_formal_scheduler_v2.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_mock_acceptance.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_protocol.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_runner_contract.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_dynamic_runtime.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_horizon_scaling_scheduler.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_policy.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_reliability_v1.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_graph_runner_bundles.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_p2_e0_adapter_equivalence.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_p2_e0_generic_base_adapter_equivalence_v2.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_p2_e1_generic_base_formal_v2.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_p2_e1_primary_readiness_v2.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_p2_e1_primary_readiness.py` → `liq22/phm-agent-benchmark/experiments/tests`
- `tests/test_summarize_graph_states.py` → `liq22/phm-agent-benchmark/experiments/tests`

## REMOVE_AFTER_DEPENDENCY_MIGRATION (1)

- `requirement.yaml` → `Benchmark pyproject/config`

## REVIEW_REMOVE_OBSOLETE (1)

- `.gitmodules` → `P02 root`

## SPLIT_OWNERSHIP (1)

- `paper/experiments` → `Specs stay P02; runtime/config/results to Benchmark`
