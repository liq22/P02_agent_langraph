---
skill_id: P4_02_问题映射矩阵_local_entry
purpose: 把审稿问题映射成局部矩阵，而不是继续堆叠原始评论。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_wrapper_skill: local_wrapper
outputs:
- artifacts/question_mapping_matrix.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P4_论文回复_response/P4_02_问题映射矩阵`.

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
