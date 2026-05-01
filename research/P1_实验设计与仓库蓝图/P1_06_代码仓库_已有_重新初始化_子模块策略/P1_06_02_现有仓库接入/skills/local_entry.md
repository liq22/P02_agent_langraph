---
skill_id: P1_06_02_现有仓库接入_local_entry
purpose: 明确现有仓库接入路径与最小改造边界。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: leaf_node_writer
outputs:
- docs/manuscript.md
---

Runtime entry shim for this lite node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_02_现有仓库接入`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
