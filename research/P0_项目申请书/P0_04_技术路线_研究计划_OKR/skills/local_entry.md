---
skill_id: P0_04_技术路线_研究计划_OKR_local_entry
purpose: 把技术路线、研究计划与 OKR 对齐成可执行的局部蓝图。
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
- artifacts/okr_map.yaml
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
