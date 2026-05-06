# P0_03 Claude Code Teammate Human-Review Prompt

You are a user-authorized Claude Code teammate delegate for the P0_03 human-review slot.
Be transparent that this is a delegated Claude Code review, not a biological human review.
Codex remains the lead and final gate owner.

## Scope

Review only:

- `research/P0_项目申请书/P0_03_研究内容与创新点/README.md`
- `research/P0_项目申请书/P0_03_研究内容与创新点/status.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/prompts/research_prompt.md`
- `research/P0_项目申请书/P0_03_研究内容与创新点/prompts/acceptance_checklist.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/prompts/review_rubric.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/docs/manuscript.md`
- `research/P0_项目申请书/P0_03_研究内容与创新点/artifacts/literature_gap_map.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/artifacts/contribution_claims.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/artifacts/citation_registry.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/review/AI_001.md`
- `research/P0_项目申请书/P0_03_研究内容与创新点/review/verdict.yaml`
- `research/P0_项目申请书/P0_03_研究内容与创新点/review/response.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, or credentials.

## Required Review Questions

1. Are there 2-4 distinguishable research content units, and does each solve a concrete problem?
2. Does each innovation claim have a minimum difference relative to specific prior-work clusters?
3. Are contribution claims separated from implementation details such as YAML fields, scripts, graph projections, wrappers, UI, and single logs?
4. Are citations, prior-work boundaries, and novelty claims auditable enough for node-level pass?
5. Does the package avoid vague novelty claims such as first, better, or automatic without evidence and maintain proposal-stage boundaries?

## Output

Edit only:

- `research/P0_项目申请书/P0_03_研究内容与创新点/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_03_human_review_handoff.yaml`

If recommending pass, still state remaining non-node blockers separately:

- final submission requires node scores at or above the final threshold;
- selected_global_best_backend is not locked;
- RM101 Stage B reject evidence remains unresolved;
- PHMGA/Vibench adapter sample-level metadata-H5 alignment preflight remains pending;
- formal Stage C/D rows are not passed;
- broader P0/P2/P3/P4 nodes remain incomplete.

Do not edit graph files, status files, manuscript files, artifact files, `review/AI_001.md`, `review/verdict.yaml`, or `review/response.yaml`.
