---
skill_id: P3_04_修订动作_local_entry
purpose: 把批评摘要转成可执行修订动作图，而不是泛化成任意 revision 任务。
node_mode: standard
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: structured_map_builder
required_local_reads:
- ../prompts/standards.md
outputs:
- artifacts/revision_action_map.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../prompts/standards.md`
5. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
