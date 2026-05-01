---
skill_id: P3_03_批评摘要_local_entry
purpose: 把本节点 review / critique 压缩成 digest，而不是继续扩写评论正文。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: aggregate_reviews
required_local_reads:
- ../prompts/standards.md
- review/
outputs:
- artifacts/critique_digest.yaml
- artifacts/review_issue_register.yaml
- logs/session_manifest.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../prompts/standards.md`
5. `review/`
6. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
