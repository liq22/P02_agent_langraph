# P1_07 Gate Report

This report uses the v3 protocol artifacts as the effective gate state.

- node_id: `research::P1_实验设计与仓库蓝图::P1_07_优化目标_任务_评测协议`
- generated_at: 2026-05-05
- actor: codex-local
- decision: ready for distinct final-threshold score re-review, protocol-ready only

## v3 Gate Inputs

| Input | Role | Current Use |
| --- | --- | --- |
| `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/artifacts/problem_hypothesis.yaml` | H1-H3 and falsification paths | Defines claim validity, review-response closure, and formal evidence eligibility tasks; checked anchors include lines 12-29, 35-45, and 126-135. |
| `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/artifacts/okr_map.yaml` | route stages and metrics | Places P1_07 in protocol/data eligibility, evidence-boundary preservation, Stage C/D, and review-response stages; checked anchors include lines 33-62, 63-88, and 124-139. |
| `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/artifacts/constraint_risk_map.yaml` | resource and risk boundaries | Imports provider/model, Vibench/PHMGA, Stage B/C/D, selected backend, registry, and review-threshold blockers; checked anchors include lines 28-44, 72-94, 97-112, and 121-124. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/submodule_ref.yaml` | PHMGA repo state | Records branch `journal_thesis`, commit `914bc5925d5230917a5de95d88784075fb2b041e`, dirty count 66, pull result, and no pointer update; checked anchors include lines 6-17, 21-31, and 45-50. |
| `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/artifacts/hypothesis_status.yaml` | preliminary evidence boundary | Preserves supported_limited, unsupported, and unclear statuses from synthetic/offline evidence; checked anchors include lines 6-14, 17-31, and 35-41. |
| `artifacts/protocol_final_threshold_contract.yaml` | score-only final-threshold boundary | Allows a distinct reviewer to judge node-local protocol-package score readiness while forbidding observed-result, formal-evidence, selected-backend, RM101-resolution, Stage C/D, checklist-status, P3-action, or global-submission-ready upgrades. |

## v3 External Review Fix Register

| review_claim_id | evidence_id | fix_applied | verification_state |
| --- | --- | --- | --- |
| P1_07_C007_UPSTREAM_TRACEABILITY | P1_07_E007_UPSTREAM_EVIDENCE_PATHS | Canonical existing upstream paths, evidence IDs, checked dates, and line anchors are now recorded in `artifacts/protocol_map.yaml:upstream_evidence`. | ready_for_re_review |
| P1_07_C004_UNCERTAINTY_REQUIRED | P1_07_E004_STATISTICS_PLAN | Workflow conditions require 3 repeats each; Stage C/D formal rows require 3 replayable run/seed units; Stage B is limited to 1-row backend-lock preflight; budget constants are fixed. | ready_for_re_review |
| P1_07_C008_METRIC_PARSER_SCHEMA | P1_07_E008_METRIC_LEDGER_CONTRACT | Workflow and formal result ledger fields, enum values, rate numerator/denominator rules, count rules, binary gate rule, exclusion handling, and artifact path validation rules are defined. | ready_for_re_review |
| P1_07_C009_FINAL_THRESHOLD_PROTOCOL_LOCK | P1_07_E009_FINAL_THRESHOLD_CONTRACT | Node-local score boundary is locked in `artifacts/protocol_final_threshold_contract.yaml`; AI-001 and H-001 responses are recorded; legacy sections are non-normative history. | ready_for_score_only_final_threshold_re_review |

## v3 Required Questions

| Question | Answer |
| --- | --- |
| primary/secondary outcomes 是什么？ | Primary: `claim_evidence_validity_rate`. Hard eligibility gate: `formal_result_eligibility_pass`. Secondary outcomes include unsupported claims, reviewer pass, response coverage, hard-fail closure, negative-result retention, protocol completeness, rerun agreement, boundary violations, final-validator blockers, Stage C pass, and Stage D pass. |
| task 定义和 success criterion 是什么？ | Task families cover fixed-node governance comparison, review-response closure, PHMGA formal evidence eligibility, and manuscript integration preflight. Success requires preregistered baselines, identical budgets/rubrics, at least 3 workflow repeats per condition, at least 3 Stage C/D formal repeats per row, uncertainty/failure reporting, and formal-row eligibility before result claims. |
| 什么 baseline 与对照是必须的？ | Required workflow baselines are manual checklist, prompt-only agent, and agent without independent gate. Required formal controls are provider/model free boundary, Vibench read-only boundary, PHMGA protocol ownership, selected backend, artifact contract, Stage C rows, and Stage D ablations. |

## v2 Blocking Gap Register

| claim_id | evidence_id | location | actionable_fix | gate_level |
| --- | --- | --- | --- | --- |
| P1_07_C001_PRIMARY_METRIC_BOUND | P1_07_E001_PROTOCOL_MAP | `artifacts/protocol_map.yaml:P1_07_M001` | Keep numerator, denominator, exclusion rule, and support-status vocabulary fixed before execution. | hard-gate |
| P1_07_C002_BASELINES_REQUIRED | P1_07_E002_BASELINE_CONTRACT | `artifacts/protocol_map.yaml:required_baselines` | Require manual checklist, prompt-only agent, and no-independent-gate records under identical budget/rubric/audit procedure. | hard-gate |
| P1_07_C003_FORMAL_GATE_REQUIRED | P1_07_E003_FORMAL_GATE | `artifacts/protocol_map.yaml:P1_07_PROTO_002` | Require provider policy, metadata-H5 alignment, artifact contract, selected backend, Stage C rows, Stage D rows, result_md, artifact_dir, and table mapping before formal claims. | hard-gate |
| P1_07_C004_UNCERTAINTY_REQUIRED | P1_07_E004_STATISTICS_PLAN | `artifacts/experiment_rigor_plan.yaml:v3_review_fix_register.preregistered_repeat_budget` | Require 3 repeats per workflow condition, 3 repeats per Stage C/D formal row, concrete wall-clock/token/LLM-call budgets, confidence/bootstrap interval, low-power limitation, and failure distribution before result-level claims. | hard-gate |
| P1_07_C005_NO_CHERRY_PICKING | P1_07_E005_STOP_CONDITIONS | `artifacts/experiment_rigor_plan.yaml:P1_07_STOP_001_CHERRY_PICKED_METRIC` | Block any favorable secondary metric if primary outcome or formal eligibility gate fails. | hard-gate |
| P1_07_C006_NEGATIVE_EVIDENCE_VISIBLE | P1_07_E006_FAILURE_RECORDS | `artifacts/experiment_rigor_plan.yaml:required_failure_records` | Keep unsupported, unclear, rejected, failed, rate-limited, and schema-failed cases visible in ledgers. | hard-gate |
| P1_07_C007_UPSTREAM_TRACEABILITY | P1_07_E007_UPSTREAM_EVIDENCE_PATHS | `artifacts/protocol_map.yaml:upstream_evidence` | Use only canonical existing upstream paths with evidence IDs and line anchors; unreachable paths downgrade consistency claims to protocol-draft. | hard-gate |
| P1_07_C008_METRIC_PARSER_SCHEMA | P1_07_E008_METRIC_LEDGER_CONTRACT | `artifacts/protocol_map.yaml:metric_parser_contract` | Require parser-readable common fields, formal row fields, allowed enums, numerator/denominator/count/binary-gate rules, exclusion handling, and artifact path validation. | hard-gate |

## v3 Documented / Consistent / Complete / Exercisable

Documented: objectives, protocols, primary/secondary outcomes, hard gates, baselines, formal controls, fixed budget constants, minimum repeat counts, statistics, artifacts, metric parser contracts, and stop conditions are written in `protocol_map.yaml` and `experiment_rigor_plan.yaml`.

Consistent: H1-H3, support statuses, provider/model policy, Vibench/PHMGA boundary, and PHMGA submodule state match the canonical upstream paths and line anchors listed in this report.

Complete: the protocol covers success, unsupported, unclear, reject evidence, rate limit, missing baseline, missing uncertainty, low-power repeats, adapter failure, parser schema failure, artifact-path failure, and below-threshold review.

Exercisable: downstream workers can execute or record the comparison without redefining the scientific question; missing command, manual operation form, reviewer assignment, result ledger schema, metric parser field, repeat minimum, or formal row denominator blocks result claims.

## v3 Gate Decision

P1_07 is ready for independent node re-review. It is protocol-ready only. It does not claim observed AutoResearch improvement, PHMGA formal eligibility, selected backend, Stage C/D success, RM101 resolution, or final submission readiness.

For the current final-threshold pass, P1_07 asks only whether the protocol package can score at or above 90 after the v3 lock and response coverage. A positive score review must preserve global non-readiness because the remaining final validator blockers are outside P1_07's node-local protocol evidence.

## Legacy Gate Report Context

Legacy context below is non-normative and retained only for history. The v3 gate inputs, fix register, blocking gap register, repeat/budget constants, and parser contracts above override older wording.

## Gate Inputs

- objective: Evaluate whether AutoResearch improves claim-evidence validity and phase-transition discipline for research nodes.
- task: node-level research production, protocol design, manuscript methods, review, and response coverage.
- protocol: `fixed_node_set_controlled_comparison_v1`.
- primary metric: `claim_evidence_validity_rate`.
- secondary metrics: `protocol_completeness`, `independent_reviewer_pass_rate`, `rerun_agreement`, `unsupported_claim_count`, `hard_fail_closure_rate`, `human_gate_escalation_rate`.
- required baselines: `manual_checklist_workflow`, `prompt_only_agent_workflow`, `agent_without_independent_gate`.
- repeat plan: repeated seeds or independent reviewer assignments for each condition; if unavailable, report low-power limitation.
- artifact path: `artifacts/protocol_map.yaml`, `artifacts/experiment_rigor_plan.yaml`, future `artifacts/result_ledger.yaml`, future `review/verdict.yaml`, future `logs/coverage_matrix.md`.

## Blocking Gap Register

| claim_id | evidence_id | location | actionable_fix | gate_level |
|---|---|---|---|---|
| p1_claim_primary_metric_bound | p1_metric_contract | docs/manuscript.md:Primary/Secondary Outcomes 是什么？ | Define numerator, denominator, eligible claims, and exclusion rule for `claim_evidence_validity_rate` before execution | hard-gate |
| p1_claim_baseline_fair | p1_baseline_contract | docs/manuscript.md:什么 Baseline 与对照是必须的？ | Record baseline inputs, budget, reviewer rubric, operator log, and artifact collection procedure | hard-gate |
| p1_claim_reproducible_protocol | p1_protocol_map | docs/manuscript.md:Protocol_Map 与可执行评测协议摘要 | Bind fixed node set, run command or manual operation form, random seed/reviewer assignment, and output ledger schema | hard-gate |
| p1_claim_uncertainty_visible | p1_statistics_plan | docs/manuscript.md:Documented / Consistent / Complete / Exercisable | Add confidence interval or bootstrap interval plan, repeat count, and negative result interpretation | hard-gate |
| p1_claim_no_premature_promotion | p1_phase_gate | docs/manuscript.md:Gate Report Policy | Require reviewer verdict or human gate before node close; author exit alone is insufficient | hard-gate |

## Documented / Consistent / Complete / Exercisable

Documented: objective, task, protocol, baselines, metrics, repeats, uncertainty, artifact paths, and human/reviewer gate are named.

Consistent: protocol_map, experiment_rigor_plan, this gate_report, and future result ledger must use the same claim_id/evidence_id vocabulary.

Complete: the protocol includes success metrics, failure cases, unsupported claim handling, negative result policy, and phase gate rules.

Exercisable: the next worker can execute a controlled comparison or create a manual operation ledger without redefining the research question.

## Author Exit

gate_inputs_verified: true。blocking_gaps_are_explicit: true。Any blocking issue includes claim_id, evidence_id, location, and actionable_fix.
