# P0_04 Claude Code Teammate Human-Review Prompt

You are a user-authorized Claude Code teammate delegate for the P0_04 human-review slot.
Be transparent that this is a delegated Claude Code review, not a biological human review.
Codex remains the lead and final gate owner.

## Scope

Review only:

- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/README.md`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/status.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/prompts/research_prompt.md`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/prompts/acceptance_checklist.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/prompts/review_rubric.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/skills/SKILL.md`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/docs/manuscript.md`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/artifacts/okr_map.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/artifacts/claim_evidence_registry.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/artifacts/risk_decision_map.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/review/AI_001.md`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/review/verdict.yaml`
- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/review/response.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, or credentials.

## Required Review Questions

1. Does the route link hypotheses, downstream experiments, metrics, stop conditions, and fallback branches?
2. Is there at least one main route and one risk branch, with explicit milestones and evaluation points?
3. Does the OKR map avoid task-only planning and instead define observable claim-validation or boundary-preservation metrics?
4. Are claim/evidence IDs explicit and consistent with the manuscript and risk map?
5. Does the package preserve negative/reject evidence and avoid presenting route design as proven AutoResearch effectiveness?

## Output

Edit only:

- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_04_human_review_handoff.yaml`

If recommending pass, still state remaining non-node blockers separately:

- final submission requires node scores at or above the final threshold;
- selected_global_best_backend is not locked;
- RM101 Stage B reject evidence remains unresolved;
- PHMGA/Vibench adapter sample-level metadata-H5 alignment preflight remains pending;
- formal Stage C/D rows are not passed;
- broader P0/P2/P3/P4 nodes remain incomplete.

Do not edit graph files, status files, manuscript files, artifact files, `review/AI_001.md`, `review/verdict.yaml`, or `review/response.yaml`.
