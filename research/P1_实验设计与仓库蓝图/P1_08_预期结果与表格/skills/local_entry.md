---
skill_id: P1_08_预期结果与表格_local_entry
purpose: 把预期结果、表格结构与 claim 对齐成局部计划工件。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_wrapper_skill: local_wrapper
outputs:
- artifacts/table_plan.yaml
- artifacts/claim_map.yaml
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`
5. `skills/local_wrapper.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
