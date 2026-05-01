# Full Pipeline Test Plan: 0 -> Paper Submission

This document defines the acceptance path from an empty or seed research OS state to a submission-ready paper package.

It is a test plan, not a second workflow engine.

## Principles

- Repo files remain source of truth.
- `backend/graph/*.json` and Canvas files are derived projections.
- Each test checks one bounded gate.
- Human and scientific judgment is evidence, not mocked truth.
- Missing upstream artifacts must be reported as `partial` or `blocked`, never silently passed.

## Baseline Commands

Run these from the repository root:
```bash
python test/run_fixture_acceptance.py
python test/run_gateway_acceptance.py
python test/run_nature_rubric_presence.py
python test/run_nature_capability_acceptance.py
python test/run_live_repo_smoke.py
python test/run_all_acceptance.py
```

Expected:
- `run_all_acceptance.py` exits `0`.
- Nature-level rubric coverage exists for every `research/**/status.yaml` node.
- Nature capability acceptance proves complete synthetic submissions pass and incomplete submissions fail.
- Live smoke exits `0` only when backend, frontend, and skill verdicts are all `pass`.
- Any `partial` output is blocking and must make the runner exit `1`.
- Backend checks must keep `ready_nodes`, `blocked_nodes`, and `next_node` leaf-only.
- `python scripts/validate_research_truth.py --require-submission` is the live-paper readiness gate and must not be treated as pass until real evidence, review closure, manuscript, and bundle files exist.

## Gate 0 - Fresh Repository / Bootstrap

Purpose: prove the repo can derive scheduler and projection state without hidden setup.

Inputs:
- root `README.md`
- `research/**/README.md`
- `research/**/status.yaml`
- `backend/relations/edge_registry.json`
- `.agent/skills/*/SKILL.md`

Checks:
- `python scripts/refresh_views.py --mode graph_only` succeeds.
- `backend/graph/graph.json` contains only `nodes` and `edges`.
- each graph node contains only `path` and `status`.
- each edge contains only `src`, `rel`, and `dst`.
- `backend/graph/graph_status.json` has `refresh_ok`, `current_phase`, `ready_nodes`, `blocked_nodes`, `next_node`, `unfinished_count`.

Failure means:
- graph truth or status contracts are malformed before any research work can run.

## Gate 1 - P0 Project Proposal Readiness

Purpose: validate the proposal/front-matter phase can be scheduled and completed before experiment design.

Nodes:
- `research/P0_项目申请书/P0_01_研究背景与调研`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题`
- `research/P0_项目申请书/P0_03_研究内容与创新点`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界`

Checks:
- all P0 leaf nodes have `README.md`, `status.yaml`, and `skills/local_entry.md`.
- each P0 leaf can become `ready` without reading unrelated repository content.
- parent P0 node does not enter scheduler frontier.
- after P0 leaf nodes are terminal, scheduler can move to P1 leaf frontier.

Evidence:
- `backend/graph/graph_status.json`
- node-local `docs/` or declared output artifacts
- local review/response files when present

Failure means:
- the scheduler is blocked by parent state or P0 local entries are incomplete.

## Gate 2 - P1 Experiment Design And Execution Readiness

Purpose: validate experiment design can progress to a bounded executable campaign without guessing.

Critical chain:
- `P1_01_数据层_集中数据与子模块引用`
- `P1_02_伪代码`
- `P1_03_仓库蓝图`
- `P1_04_核心想法轻量验证`
- `P1_05_初步验证结果整理`

Checks:
- explicit `depends_on` edges connect only leaf nodes.
- `P1_04` uses `local_entry -> local_wrapper -> auto_experiment_worker`.
- `P1_04/artifacts/execution_contract.yaml` must exist before executable experiment work.
- the execution contract must provide repo path, editable paths, run command, metric parser, and budget.
- `P1_05` must not pass until `P1_04/artifacts/auto_experiment/results.tsv` exists.

Blocking partial:
- `P1_04_execution_contract: partial` is an honest missing-contract diagnostic and must not count as pass.

Failure means:
- the system is guessing experiment execution details or allowing result synthesis before experimental evidence exists.

## Gate 3 - P2 Manuscript Draft To Formal Draft

Purpose: validate the manuscript can be assembled from research artifacts without graph becoming a content store.

Nodes:
- `P2_01_风格选择_IEEE_Elsevier_Nature`
- `P2_02_初稿_md/*`
- `P2_03_定稿_tex`
- `P2_04_形式检查`
- `P2_05_去AI味道`

Checks:
- P2 draft leaf nodes are blocked by P1 result synthesis where required.
- manuscript content stays in node-local `docs/` or artifacts, not graph JSON.
- figure/table/claim dependencies are explicit local inputs.
- `P2_04` produces or checks `artifacts/formal_check_report.md`.
- `P2_03` can generate a TeX submission draft from declared manuscript input.

Failure means:
- manuscript generation is running before experiment evidence or claim mapping exists.

## Gate 4 - P3 Simulated Review And Revision Planning

Purpose: validate review loops are bounded and produce actionable revision evidence.

Nodes:
- `P3_01_评审轮次`
- `P3_02_评价者档案`
- `P3_03_批评摘要`
- `P3_04_修订动作`

Checks:
- review input points to the current manuscript artifact.
- critique aggregation produces a structured summary.
- revision actions map back to concrete manuscript or experiment nodes.
- no global endless review loop is started.

Failure means:
- review feedback is untraceable or the review loop is not bounded.

## Gate 5 - P4 Response And Submission Package

Purpose: validate response preparation can produce a submission-ready bundle.

Nodes:
- `P4_01_审稿意见收集`
- `P4_02_问题映射矩阵`
- `P4_03_逐点回复草稿_md`
- `P4_04_正式回复_tex_或_doc`
- `P4_05_覆盖检查`
- `P4_06_修改证据`
- `P4_07_再投稿打包`

Checks:
- `P4_02` waits for `artifacts/review_comment_register.yaml`.
- `P4_03`, `P4_05`, and `P4_06` wait for `artifacts/question_mapping_matrix.yaml`.
- `P4_07` waits for `artifacts/response_letter.tex`.
- final bundle manifest lists manuscript, response letter, revision evidence, figures/tables, and submission metadata.

Failure means:
- response or submission packaging is running before review mapping and evidence are complete.

## End-To-End Acceptance Matrix

| Layer | Command / Evidence | Pass Condition |
| --- | --- | --- |
| Fixture | `python test/run_fixture_acceptance.py` | deterministic stack passes |
| Gateway | `python test/run_gateway_acceptance.py` | bounded agent run and UI contract pass |
| Nature rubric | `python test/run_nature_rubric_presence.py` | every research node has one scoring rubric row |
| Nature capability | `python test/run_nature_capability_acceptance.py` | validator accepts complete package and rejects missing evidence |
| Live smoke | `python test/run_live_repo_smoke.py` | backend/frontend/skill all pass; no partial verdicts remain |
| Combined | `python test/run_all_acceptance.py` | exits `0` |
| Live submission truth | `python scripts/validate_research_truth.py --require-submission` | exits `0` only when the real paper package is complete |
| Graph | `backend/graph/graph_status.json` | next node is leaf or all work is terminal |
| Submission | `P4_07/artifacts/resubmission_bundle_manifest.yaml` | all listed assets exist |

## Non-Goals

- Do not validate scientific truth by file presence.
- Do not auto-generate missing experiment contracts.
- Do not treat Canvas, dashboard, or graph JSON as source of truth.
- Do not collapse P0-P4 into one unbounded autonomous loop.

## Minimal Future Runner

Only add a runner later if this document starts being manually checked repeatedly.

The first runner should be:

```text
test/run_full_pipeline_readiness.py
```

It should only inspect file presence, graph frontier, known gate artifacts, and command exit codes.
It must not write research content or advance node statuses.
