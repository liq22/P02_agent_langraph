---
skill_id: P1_01_数据层_集中数据与子模块引用_local_entry
purpose: 收敛数据对象、数据血缘与子模块引用关系，保持输入边界清晰。
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
- artifacts/data_lineage.yaml
- artifacts/submodule_ref.yaml
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
