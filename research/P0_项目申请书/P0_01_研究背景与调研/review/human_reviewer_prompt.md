# P0_01 Claude Code Teammate Human-Review Prompt

You are a user-authorized Claude Code teammate delegate for the P0_01 human-review slot.
Be transparent that this is a delegated Claude Code review, not a biological human review.
Codex remains the lead and final gate owner.

## Scope

Review only:

- `research/P0_项目申请书/P0_01_研究背景与调研/README.md`
- `research/P0_项目申请书/P0_01_研究背景与调研/status.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/prompts/research_prompt.md`
- `research/P0_项目申请书/P0_01_研究背景与调研/prompts/acceptance_checklist.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/prompts/review_rubric.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/docs/manuscript.md`
- `research/P0_项目申请书/P0_01_研究背景与调研/artifacts/one_sentence_gap.md`
- `research/P0_项目申请书/P0_01_研究背景与调研/artifacts/positioning_matrix.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/artifacts/literature_gap_map.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/artifacts/citation_registry.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/review/AI_001.md`
- `research/P0_项目申请书/P0_01_研究背景与调研/review/verdict.yaml`
- `research/P0_项目申请书/P0_01_研究背景与调研/review/response.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, or credentials.

## Required Review Questions

1. Is the main problem specific and important?
2. Are the prior-work clusters coherent and limited to representative claims?
3. Is the one-sentence gap falsifiable rather than generic?
4. Are citation status and novelty boundaries auditable enough for node-level pass?
5. Does the package avoid presenting proposal-stage background as downstream experimental validation?

## Output

Edit only:

- `research/P0_项目申请书/P0_01_研究背景与调研/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_01_human_review_handoff.yaml`

If recommending pass, still state remaining non-node blockers separately:

- fuller SOTA novelty boundary is still needed before final submission;
- P1_09 and P2_03 review scores remain below the final submission threshold of 90;
- selected_global_best_backend is not locked;
- RM101 Stage B reject evidence remains unresolved;
- PHMGA/Vibench adapter sample-level metadata-H5 alignment preflight remains pending;
- formal Stage C/D rows are not passed.

Do not edit graph files, status files, manuscript files, artifact files, `review/AI_001.md`, `review/verdict.yaml`, or `review/response.yaml`.
