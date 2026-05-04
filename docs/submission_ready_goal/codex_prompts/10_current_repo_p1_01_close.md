
# 10 Current Repo P1_01 Closure Prompt

Use this after `00_master_goal.md` when the current graph still points to P1_01.

```text
/goal
Execute one bounded selected-node step for:
research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用

Read in order:
1. README.md
2. backend/graph/graph_status.json
3. .gitmodules
4. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/README.md
5. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/status.yaml
6. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/skills/local_entry.md
7. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/prompts/research_prompt.md
8. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/prompts/acceptance_checklist.yaml
9. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/prompts/review_rubric.yaml
10. research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/skills/SKILL.md
11. PHMGA README.md through the submodule if available
12. PHMGA doc/structure/00_problem_and_protocol.md through the submodule if available
13. PHMGA doc/experiments/02_main_tables.md through the submodule if available

Write only inside the selected node:
- docs/manuscript.md
- artifacts/data_lineage.yaml
- artifacts/submodule_ref.yaml
- artifacts/vibench_data_factory_binding.yaml
- artifacts/data_reading_boundary.yaml
- artifacts/phmga_data_protocol_handoff.yaml
- artifacts/result_source_map.yaml
- artifacts/claim_evidence_registry.yaml
- artifacts/failure_register.yaml
- artifacts/negative_result_note.md
- artifacts/keep_discard_ledger.yaml
- logs/codex_run_001.md
- review/AI_001.md
- review/verdict.yaml
- review/response.yaml

Use templates from:
docs/submission_ready_goal/node_templates/P1_01_actual/

Do not run formal PHMGA experiments.
Do not claim main results if PHMGA main tables have no passed rows.
After writing, run:
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs
```
```
