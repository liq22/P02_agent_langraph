---
skill_id: P0_01_研究背景与调研_local_entry
purpose: 收敛本节点的研究背景综述、问题引入、nearest prior work 与相关工作定位边界。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: idea_discovery_or_problem_formulation
outputs:
- docs/manuscript.md
- artifacts/positioning_matrix.yaml
- artifacts/literature_gap_map.yaml
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this lite node.

This shim applies to `research/P0_项目申请书/P0_01_研究背景与调研`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
