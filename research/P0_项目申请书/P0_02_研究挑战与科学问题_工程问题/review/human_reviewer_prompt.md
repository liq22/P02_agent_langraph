# P0_02 Claude Code Teammate Human-Review Prompt

You are a user-authorized Claude Code teammate delegate for the P0_02 human-review slot.
Be transparent that this is a delegated Claude Code review, not a biological human review.
Codex remains the lead and final gate owner.

## Scope

Review only:

- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/README.md`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/status.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/prompts/research_prompt.md`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/prompts/acceptance_checklist.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/prompts/review_rubric.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/docs/manuscript.md`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/artifacts/literature_gap_map.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/artifacts/problem_hypothesis.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/artifacts/citation_registry.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/review/AI_001.md`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/review/verdict.yaml`
- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/review/response.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, or credentials.

## Required Review Questions

1. Are the scientific questions and engineering problems clearly separated?
2. Is each scientific question testable with named metrics or falsification paths?
3. Is each engineering problem tied to inspectable completion evidence rather than treated as a scientific result?
4. Are citations, prior-work boundaries, and novelty claims auditable enough for node-level pass?
5. Does the package avoid presenting proposal-stage framing, synthetic/offline checks, reject evidence, or graph projections as final research truth?

## Output

Edit only:

- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_02_human_review_handoff.yaml`

If recommending pass, still state remaining non-node blockers separately:

- final submission requires node scores at or above the final threshold;
- selected_global_best_backend is not locked;
- RM101 Stage B reject evidence remains unresolved;
- PHMGA/Vibench adapter sample-level metadata-H5 alignment preflight remains pending;
- formal Stage C/D rows are not passed;
- broader P0/P2/P3/P4 nodes remain incomplete.

Do not edit graph files, status files, manuscript files, artifact files, `review/AI_001.md`, `review/verdict.yaml`, or `review/response.yaml`.
