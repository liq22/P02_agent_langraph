# Methods Template：AutoResearch 系统研究

## Methods Scope

This Methods node specifies how to study AutoResearch as a human-agent research operating system. The method is not a domain-model training recipe and not a description of a local dashboard. It defines the study design, task set, comparison conditions, artifacts, statistics, data-code statements, protocol statements, and phase-gate policy needed for a reviewer to reproduce the research-process evaluation [1][2].

## 研究设计与实现的关键决定是什么？

Key decision 1: the unit of analysis is a research node. A node is eligible only if it has a node path, research prompt, acceptance checklist, allowed edit scope, expected outputs, evidence artifacts, and a reviewer or human gate. This prevents the study from scoring generic prose without a verifiable research state [3].

Key decision 2: the intervention is the AutoResearch contract, not the language model alone. The intervention includes node-local problem framing, claim/evidence/protocol registry, pre-execution protocol gates, independent review, and response coverage. The comparison conditions are manual checklist workflow, prompt-only agent workflow, and agent workflow without independent gate [3].

Key decision 3: author exit and node close are separated. Author exit means the local artifacts are present and internally coherent; node close requires reviewer verdict or human gate evidence. This distinction is a method variable, because premature phase transition is one of the risks under study [3].

## Study Design

The study uses a fixed-node-set controlled comparison. The node set should cover at least P0 problem formulation, P1 protocol design, P2 methods/claim registry, P3 review, and P4 response coverage. Each condition receives the same source prompt, same acceptance checklist, same review rubric, same time or token budget, same artifact audit procedure, and same output contract.

The primary outcome is claim_evidence_validity_rate: the proportion of eligible claims that have claim_id, evidence_id, artifact path, citation status, boundary, and reviewer or human-gate status. Secondary outcomes are protocol_completeness, independent_reviewer_pass_rate, reproducibility_rerun_agreement, unsupported_claim_count, hard_fail_closure_rate, human_gate_escalation_rate, and time_to_author_exit.

## Procedure

Step 1: select and freeze the node set, prompts, checklists, rubrics, budget, reviewer assignment rule, and artifact paths. The frozen protocol is recorded in P1 `artifacts/experiment_rigor_plan.yaml`.

Step 2: run each condition on the same node set. Manual checklist workflow records human actions and elapsed time. Prompt-only agent workflow records prompt, output, budget, and artifacts. AutoResearch records node-local artifacts, claim/evidence/protocol links, gate outcomes, and reviewer/human decisions.

Step 3: audit every eligible claim. A claim is valid for the primary metric only if it links to evidence, has a boundary, carries citation status when external sources are used, and has a reviewer or human-gate status.

Step 4: compute primary and secondary metrics. Report point estimate, confidence interval or bootstrap interval, repeat count, failure distribution, and negative result. If repeat budget is too low, the limitation is reported and result-level claims are blocked.

Step 5: perform external review. Fatal and major concerns are mapped to claim_id, evidence_id, manuscript location, actionable fix, response status, and closure evidence.

## 别人需要哪些细节才能理解与复现？

A reproducing researcher needs the repository version, node paths, fixed node set, prompts, acceptance checklists, review rubrics, allowed edit scope, budgets, random seeds or reviewer assignments, exact run commands or manual operation ledger, model/provider metadata if agents are used, artifact collection rule, evaluator versions, and result ledger schema.

For each node, the minimum reproducibility record is: `docs/manuscript.md`, relevant `artifacts/*.yaml` or `artifacts/*.md`, `logs/claim_evidence_map.md`, reviewer verdict when available, and any script or manual form used to compute metrics. For each claim, the record must preserve claim_id, evidence_id, evidence location, boundary, citation status, and reviewer action.

Methods 足以支持解释和 replication only when these records let another reviewer reconstruct the study design, metric computation, artifact path, and phase-gate decision without changing the research question [1][2][3].

## 哪些细节该放 Methods，哪些放 Appendix/Protocol？

Methods should contain the study design, unit of analysis, intervention and baseline definitions, task families, primary and secondary metrics, inclusion/exclusion rules, statistics plan, data-code/protocol availability statements, review gate policy, and limitation boundary.

Appendix/protocol should contain long node lists, raw reviewer forms, full run commands, model/provider metadata, budget logs, result ledgers, bootstrap scripts, full failure taxonomy, and complete response coverage matrix. Keeping these details outside the main Methods avoids hiding key logic in prose while preserving full reproducibility [1][2].

## Statistics, Data-Code, and Protocol Statements

Statistics statement: report the numerator and denominator for claim_evidence_validity_rate, repeat count, interval method, missing-data policy, and negative result handling. For small repeat counts, report descriptive statistics and label the study as low-power.

Data statement: the data are node-local research artifacts, prompts, checklists, reviewer verdicts, response matrices, and result ledgers. External literature or policy documents used for claims must retain URL or citation status.

Code statement: metric computation, registry parsing, and validation commands must be versioned with the repository. Graph, Canvas, and dashboards are projections or operation surfaces; they are not sources of research truth.

Protocol statement: the protocol is fixed before result interpretation. A run cannot promote unsupported claims by rewriting the outcome after seeing reviewer comments or metrics.

## IMRAD Role, Results Order, Figure/Table Logic, and Venue Format

IMRAD role: this node supplies Methods. It describes how evidence is generated and audited; it does not report final performance or claim acceptance.

Results order: report task coverage, claim-evidence validity, baseline comparison, uncertainty, failure cases, reviewer findings, and limitations before narrative interpretation.

Figure/table logic: a main table should list condition, node family, primary metric, interval, unsupported claims, reviewer verdict, and phase-gate result. A figure should show the path from research claim to protocol, evidence, reviewer objection, response action, and human gate.

Venue format: Nature-style versions should emphasize field significance, reproducible reporting, data/code availability, and limitations [1][2]. IEEE/TPAMI-style versions should emphasize method definition, algorithmic procedure, experimental protocol, fair baselines, statistics, and reviewer-reproducible artifacts [2].

## Limitations and Negative Results

The method cannot by itself establish paper acceptance, scientific creativity, or downstream venue success [3]. It can evaluate process-level auditability, traceability, reproducibility, and phase-transition discipline. Negative or failed results must remain in the result ledger and claim registry; they cannot be rewritten into positive evidence. Missing reviewer independence, missing baseline records, missing uncertainty, or hidden negative results block result-level claims [3].

## Author Exit

claim_evidence_ids_are_explicit_or_gap_is_reported: true。negative_or_failed_results_recorded: true。protected_paths_respected: true。方法逻辑完整，关键变量、设置和实现假设可追踪；正文服务主张，不重复图表，不夸大结论。

## References

[1] Nature Portfolio, Reporting standards: https://www.nature.com/ncomms/editorial-policies/reporting-standards

[2] IEEE Author Center, Submission and peer-review policies: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/

[3] Local evidence gate: `test/NATURE_LEVEL_NODE_RUBRIC.md`, P1 `artifacts/experiment_rigor_plan.yaml`, and this node `artifacts/claim_evidence_registry.yaml`.
