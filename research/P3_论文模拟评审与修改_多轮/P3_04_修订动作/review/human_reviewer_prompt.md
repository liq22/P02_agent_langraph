# P3_04 Human-Review-Slot Prompt

## Scope

Review `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作` for the user-authorized human-review slot. This review may be completed by a Claude Code teammate delegate because the user authorized future similar reviewer handoffs.

Be transparent if delegated: identify as a user-authorized Claude Code teammate delegate, not a biological human.

## Read Only

- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/README.md`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/status.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/prompts/research_prompt.md`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/prompts/acceptance_checklist.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/prompts/review_rubric.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/skills/local_entry.md`
- `research/P3_论文模拟评审与修改_多轮/prompts/standards.md`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/docs/manuscript.md`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/revision_action_map.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/review_issue_register.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/critique_digest.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/logs/session_manifest.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/review/AI_001.md`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/review/verdict.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/artifacts/review_issue_register.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/artifacts/critique_digest.yaml`
- `docs/submission_ready_goal/completion_audit_current.md`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, credentials, unrelated node files, PHMGA source files, graph projections as evidence, Canvas files, or dashboard files.

## Review Questions

1. Does `revision_action_map.yaml` map every P3_03 issue to an action or explicit retained blocker?
2. Does every blocking action include target_phase, target_node, action_type, expected_evidence, validation_gate, and next_iteration_trigger?
3. Do blocked targets record prerequisite gaps and allow scheduler dependency closure rather than pretending a blocked target is ready?
4. Does the map preserve action -> issue -> evidence -> file-location traceability?
5. Are non-blocking/cosmetic actions separated from evidence-blocking actions and guarded against claim upgrades?
6. Does the package avoid applying manuscript rewrites or claiming final submission readiness?

## Allowed Edit

Edit only:

- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p3_04_human_review_handoff.yaml`

Do not edit status, graph, manuscript, artifacts, AI review, verdict, response, PHMGA files, Canvas files, dashboard files, or credentials.

