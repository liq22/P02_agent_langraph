# Gate Report

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
