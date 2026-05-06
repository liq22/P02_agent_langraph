# P4_02 Human-Review-Slot Prompt

## Scope

Review `research/P4_论文回复_response/P4_02_问题映射矩阵` for the user-authorized human-review slot. This review may be completed by a Claude Code teammate delegate because the user authorized future similar reviewer handoffs.

Be transparent if delegated: identify as a user-authorized Claude Code teammate delegate, not a biological human.

## Read Only

- `research/P4_论文回复_response/P4_02_问题映射矩阵/README.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/status.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/prompts/research_prompt.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/prompts/acceptance_checklist.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/prompts/review_rubric.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/skills/local_entry.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/skills/SKILL.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/docs/manuscript.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/review_comment_register.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/问题映射矩阵.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/claim_evidence_registry.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/failure_register.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/negative_result_note.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/artifacts/keep_discard_ledger.yaml`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/review/AI_001.md`
- `research/P4_论文回复_response/P4_02_问题映射矩阵/review/verdict.yaml`
- `research/P4_论文回复_response/P4_01_审稿意见收集/artifacts/review_comment_register.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/revision_action_map.yaml`
- `docs/submission_ready_goal/completion_audit_current.md`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, credentials, unrelated node files, PHMGA source files, graph projections as evidence, Canvas files, or dashboard files.

## Review Questions

1. Are all current-scope P4_01 comments mapped exactly once?
2. Does every mapping preserve comment_id, source_action_id, issue_id, source_comment_ids, problem_class, severity, affected artifact/location, and status?
3. Does every mapping have response_item_id, evidence_item_id, coverage_gate_id, target_node, and downstream nodes for P4_03/P4_05/P4_06?
4. Are the three submission-blocking mappings still explicit rather than silently closed?
5. Are official journal comments and official editor comments still marked absent rather than fabricated?
6. Do claim/evidence, failure, negative-result, and keep/discard artifacts preserve limitations and no-final-readiness boundaries?

## Allowed Edit

Edit only:

- `research/P4_论文回复_response/P4_02_问题映射矩阵/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_02_human_review_handoff.yaml`

Do not edit status, graph, manuscript, artifacts, AI review, verdict, response, PHMGA files, Canvas files, dashboard files, or credentials.
