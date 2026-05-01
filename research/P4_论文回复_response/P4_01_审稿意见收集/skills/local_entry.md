---
skill_id: P4_01_审稿意见收集_local_entry
purpose: 收集并压缩当前 node 的审稿意见，形成后续映射输入。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: aggregate_reviews
outputs:
- artifacts/review_comment_register.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P4_论文回复_response/P4_01_审稿意见收集`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
