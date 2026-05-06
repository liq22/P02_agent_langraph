# P4_05 Human-Review-Slot Prompt

## Scope

Review `research/P4_论文回复_response/P4_05_覆盖检查` for the user-authorized human-review slot. This review may be completed by a Claude Code teammate delegate because the user authorized future similar reviewer handoffs.

Be transparent if delegated: identify as a user-authorized Claude Code teammate delegate, not a biological human.

## Read Only

- `research/P4_论文回复_response/P4_05_覆盖检查/README.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/status.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/prompts/research_prompt.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/prompts/acceptance_checklist.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/prompts/review_rubric.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/skills/local_entry.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/skills/SKILL.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/skills/local_wrapper.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/docs/manuscript.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/artifacts/coverage_check_report.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/artifacts/coverage_check.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/artifacts/question_mapping_matrix.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/artifacts/revision_evidence_map.yaml`
- `research/P4_论文回复_response/P4_05_覆盖检查/review/AI_001.md`
- `research/P4_论文回复_response/P4_05_覆盖检查/review/verdict.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`
- `research/P4_论文回复_response/P4_03_逐点回复草稿_md/artifacts/response_items.yaml`
- `research/P4_论文回复_response/P4_03_逐点回复草稿_md/docs/manuscript.md`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, credentials, unrelated node files, PHMGA source files, graph projections as evidence, Canvas files, or dashboard files.

## Review Questions

1. Does the coverage report represent all six P4_02 mapped comments and issues?
2. Does every row include response_item_id, claim_id, evidence_id, manuscript_location, actionable_fix, severity, coverage_status, and downstream commitment state?
3. Does `coverage_status: covered` mean response-level coverage only, not revision-evidence closure?
4. Are blocked/planned commitments explicit and routed to P4_06?
5. Are official-comment absence and no-final-readiness boundaries explicit?
6. Do the local question-mapping projection and revision-evidence handoff support P4_06 without fabricating completed revisions?

## Allowed Edit

Edit only:

- `research/P4_论文回复_response/P4_05_覆盖检查/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_05_human_review_handoff.yaml`

Do not edit status, graph, manuscript, artifacts, AI review, verdict, response, PHMGA files, Canvas files, dashboard files, or credentials.
