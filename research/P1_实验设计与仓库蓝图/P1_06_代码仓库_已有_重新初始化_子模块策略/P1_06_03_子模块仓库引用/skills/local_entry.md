---
skill_id: P1_06_03_子模块仓库引用_local_entry
purpose: 厘清子模块引用策略及其与主仓库的边界关系。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: structured_map_builder
outputs:
- docs/manuscript.md
- artifacts/submodule_ref_map.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_03_子模块仓库引用`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
