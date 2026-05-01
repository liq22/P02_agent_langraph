# P3 review and revision standards

## Purpose

Use these checks when a P3 node performs simulated review, critique aggregation, revision planning, or hard-mode quality control.

## Standards

- Keep reviewer independence: critique the paper as a skeptical reviewer, not as the author defending it.
- Convert critique into atomic issues: issue, severity, evidence location, affected claim, and proposed action.
- Separate fatal flaws, major concerns, minor clarity issues, and taste preferences.
- Look for unsupported claims, missing baselines, unclear novelty, weak causal links, reproducibility gaps, and figure/table ambiguity.
- Preserve negative and contradictory feedback. Do not average it away during aggregation.
- A revision plan must say what changes, where it changes, and what evidence justifies it.
- Do not expand review into rewrite unless the selected node explicitly owns the rewrite action.

## Paper Iteration Gate

Use P3 as a repeatable paper-quality gate for every future manuscript snapshot. P3 may judge, route, and map revision work; it must not become a second manuscript truth source.

- Claim/evidence gate: every central claim must have evidence refs, manuscript location, and a falsifiable boundary.
- Method/reproducibility gate: methods, data, baselines, metrics, configs, and uncertainty must be sufficient for external audit.
- Figure/table gate: every figure and table must have provenance, claim mapping, caption obligation, and text callout.
- Writing/venue gate: the manuscript must have a clear contribution thesis, section roles, venue constraints, and no unsupported overclaiming.
- Review/revision gate: every blocking issue must map to source comment, severity, affected claim, target node, evidence gap, and actionable fix.
- Response/submission gate: unresolved blockers must prevent P4 or submission readiness; P3 can only mark readiness when evidence, revision action, and manuscript location are traceable.

P3 outputs should be reusable across iterations:

- `artifacts/paper_iteration_gate.yaml`: round-level decision about next iteration, P2/P1/P4 routing, or submission-gate readiness.
- `artifacts/reviewer_lens_matrix.yaml`: reviewer perspectives and attack surfaces.
- `artifacts/review_issue_register.yaml`: atomic issue register with source comments and evidence gaps.
- `artifacts/revision_action_map.yaml`: concrete revision actions and validation gates.

Routing semantics are fixed:

- `paper_iteration_gate.next_route` / `recommended_next_route` names the preferred research target, not permission to skip explicit `depends_on` prerequisites.
- Scheduler resolves that target through dependency closure and may route to the earliest unfinished prerequisite leaf instead of the named target.
- If the preferred target is blocked by unmet prerequisites, the gate or revision action must leave that gap explicit rather than silently pretending the target is immediately executable.

## Stop Or Narrow

- Stop if the manuscript or review input is missing.
- Narrow if the critique spans multiple nodes without a declared aggregation contract.
- Flag issues that require new evidence rather than trying to solve them with prose.
- Stop if P3 is being used to directly rewrite P2 manuscript content or P4 response prose instead of routing revision actions.
