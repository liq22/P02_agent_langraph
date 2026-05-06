# P0_05 Human-Review-Slot Prompt

## Scope

Review `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界` for the user-authorized human-review slot. This review may be completed by a Claude Code teammate delegate if the user has authorized sending the packet to Claude Code/Anthropic.

Be transparent if delegated: identify as a user-authorized Claude Code teammate delegate, not a biological human.

## Read Only

- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/README.md`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/status.yaml`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/prompts/research_prompt.md`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/prompts/acceptance_checklist.yaml`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/prompts/review_rubric.yaml`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/docs/manuscript.md`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/artifacts/constraint_risk_map.yaml`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/artifacts/gate_report.md`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/review/AI_001.md`
- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/review/verdict.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, credentials, or unrelated node files.

## Review Questions

1. Does the package explicitly answer the largest resource bottleneck, most likely failure path, and reviewer-misunderstanding boundaries?
2. Are at least three major constraints/risks present, each with mitigation or downgrade action?
3. Are provider/model, data/license, PHMGA/Vibench, review-threshold, registry-schema, and preliminary-evidence boundaries explicit?
4. Does the package avoid treating graph projections, Vibench trainers/evaluators, synthetic/offline evidence, single logs, or teammate reviews as final research truth?
5. Are non-node blockers preserved rather than smoothed into a submission-ready claim?

## Allowed Edit

Edit only:

- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_05_human_review_handoff.yaml`

Do not edit status, graph, manuscript, artifacts, AI review, verdict, response, PHMGA files, Canvas files, dashboard files, or credentials.
