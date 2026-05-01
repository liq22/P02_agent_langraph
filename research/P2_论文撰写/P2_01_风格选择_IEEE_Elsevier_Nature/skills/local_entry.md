---
skill_id: P2_01_风格选择_IEEE_Elsevier_Nature_local_entry
purpose: 收敛目标 venue fit、contradiction list、证据缺口与局部写作规范。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: manuscript_worker
outputs:
- docs/manuscript.md
- artifacts/venue_requirements.yaml
---

Runtime entry shim for this lite node.

This shim applies to `research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
