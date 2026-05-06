# Methods

## Scope and Unit of Analysis

This study evaluates AutoResearch as an evidence-governed human-agent research workflow rather than as a single model, dashboard, or repository utility. The unit of analysis is a research node. A node is eligible for evaluation only when it has a path-backed identity, a local research prompt, an acceptance checklist, an edit-scope contract, expected outputs, claim/evidence artifacts, and an independent review or human-gate record. This choice keeps the method tied to inspectable research state: fluent text is not sufficient evidence unless the claim, artifact path, boundary, and review response can be reconstructed.

The intervention is the full AutoResearch contract. Each node starts from node-local framing, records its manuscript or protocol contribution, binds claims to evidence and protocol identifiers, preserves negative or blocked evidence, passes through independent review, and closes reviewer comments in a response record before downstream claims are upgraded. The comparison conditions defined by the protocol are a manual checklist workflow, a prompt-only agent workflow, and an agent workflow without the independent gate. These baselines receive the same fixed node set, source prompts, acceptance checklists, review rubrics, budgets, artifact audit rule, and primary metric definition.

For review, the method variables are summarized in `artifacts/method_reviewer_trace.yaml`. That trace maps the unit of analysis, intervention, baselines, primary metric, secondary metrics, eligibility gates, statistics requirements, and retained blockers to the local method contract, claim/evidence registry, upstream protocol map, table plan, submodule reference, and completion audit. It is a reviewer aid for checking the Methods logic, not a substitute for the protocol or a claim that formal rows have passed.

## Node Lifecycle and Local Contract

The lifecycle separates author exit from node close. Author exit means the local manuscript section and required artifacts are present, internally coherent, and bounded by explicit claim and evidence identifiers. Node close requires the review gate: a completed verdict, no hard fail, confirmed reviewer independence, and response coverage for all comments. This separation is a method variable because premature phase transition is one of the failure modes under study.

For a replicating researcher, the minimum node record is the node path, `README.md`, `status.yaml`, `prompts/research_prompt.md`, `prompts/acceptance_checklist.yaml`, `prompts/review_rubric.yaml`, `docs/manuscript.md`, node-local `artifacts/*.yaml` or `artifacts/*.md`, review verdicts, response records, and any script or manual ledger used to compute metrics. Graph files, Canvas views, dashboards, generated wrapper skills, and cockpit pages are treated as projections or operation surfaces. They may help operate the workflow, but they are not evidence sources for manuscript claims.

## Claim, Evidence, and Protocol Registry

Every central method claim is assigned a stable `claim_id` and linked to concrete evidence through `evidence_id`, `evidence_type`, `source_ref`, `support_status`, `boundary_label`, and an action. A claim may be kept only when the registry points to a local artifact, protocol map, figure manifest, review comment, or revision record that a reviewer can inspect. Claims with missing evidence, contradicted support, hidden boundaries, or unresolved reviewer actions are downgraded, revised, or blocked instead of being polished into manuscript prose.

Protocol identifiers connect the manuscript method to the preregistered evaluation design. The fixed-node governance comparison measures claim-evidence validity, independent-review pass rate, response coverage, hard-fail closure, and negative-result retention under matched budgets. The formal evidence eligibility gate controls PHMGA/Vibench result claims and blocks any performance upgrade until provider policy, data alignment, artifact contract, selected backend, Stage C rows, Stage D ablations, result ledger, and table mapping pass.

## Review and Response Closure

Independent review is part of the method, not a post-hoc editing step. The review gate checks whether the node's claims are supported, whether negative or failed evidence remains visible, whether Graph or UI projections are being treated as research truth, and whether the response record closes each actionable comment. Claude Code teammate reviews are recorded as user-authorized review-agent handoffs, not as biological human reviews. Their handoff files must state the agent identity, scope, changed files, verdict, and any residual concerns.

Reviewer comments are mapped to `comment_id`, evidence or manuscript location, response status, and closure evidence. A node can proceed only when the response file shows that all AI and human-review lane comments have been answered. If a reviewer identifies a hard fail, the node remains blocked until the claim is fixed, downgraded, or explicitly carried as a limitation with visible evidence.

## Negative Evidence and Result Denominators

Negative, rejected, unclear, rate-limited, and blocked rows are retained in the result denominator. The table plan requires these rows to remain visible with source artifacts, affected claims, support status, boundary labels, retained locations, and downgrade actions. A favorable synthetic or offline row cannot replace a preregistered formal row, and a missing RM101, Stage C, Stage D, or selected-backend record is reported as blocker, reject evidence, or limitation rather than being omitted from the denominator.

This policy applies to manuscript wording as well as tables. Limited synthetic/offline sanity checks may support planning or sanity-check language, but they cannot support formal performance improvement, real-data generalization, RM101 resolution, selected-backend success, Stage C success, Stage D success, or submission-readiness claims.

## PHMGA, Vibench, and Provider Boundary

Vibench is used as a read boundary: it supplies catalog and read-bundle context only. PHMGA owns the protocol split, windowing, DAG evaluation, result ledger, and table-producing implementation path. The current PHMGA submodule boundary is explicit: the `journal_thesis` branch and recorded commit are the implementation reference, while dirty or untracked local entries prevent any future parent pointer update until they are protected or explicitly resolved.

Formal PHMGA rows must satisfy the eligibility gate before entering the manuscript as result evidence. The provider policy is part of this gate: OpenRouter calls are restricted to free models, and BigModel calls are restricted to the free GLM-4.7-flash lane. Provider credentials are not research artifacts and are not recorded in manuscript, registry, review, or log outputs. A formal row that violates provider policy, lacks metadata-H5 alignment, fails the artifact contract, lacks selected-backend lock, lacks repeat units, or lacks result-ledger and table mapping evidence is non-selection-eligible.

## Metrics and Statistics Plan

The primary outcome for the workflow-governance comparison is `claim_evidence_validity_rate`: the proportion of eligible central claims that have claim identity, evidence identity, artifact path, support status, boundary, reviewer action, and response status. Secondary outcomes include unsupported claim count, independent-review pass rate, response coverage rate, hard-fail closure rate, negative-result retention rate, reproducibility rerun agreement, and time or budget to author exit.

For comparative claims, each workflow condition requires the repeat count defined in the protocol before improvement language is allowed. The report must include numerator, denominator, point estimate, interval method or bootstrap interval, repeat count, missing-data policy, failure distribution, and negative-result handling. If the repeat budget is below protocol, the row is labeled as a low-power pilot or blocker and cannot support a strong result claim.

## Methods Versus Appendix and Protocol

The main Methods section contains the unit of analysis, intervention and baseline definitions, node lifecycle, registry semantics, review-response gate, negative-evidence policy, PHMGA/Vibench boundary, provider boundary, primary and secondary metrics, and statistics plan. Appendix or protocol material should hold long node lists, raw reviewer forms, exact run commands, model/provider metadata, budget logs, result ledgers, bootstrap scripts, failure taxonomies, and full response matrices. This split keeps the manuscript readable while preserving enough protocol detail for a reviewer to reconstruct the study.

## Local Evidence Boundary

This node describes the method and eligibility gates; it does not report final PHMGA performance, selected backend success, RM101 resolution, Stage C completion, Stage D completion, or final submission readiness. Its claims are method/protocol claims supported by the local method contract, method reviewer trace, outline map, protocol map, table plan, submodule reference, and current completion audit. Result interpretation belongs to the experiments and discussion node after the required rows pass their gates.
