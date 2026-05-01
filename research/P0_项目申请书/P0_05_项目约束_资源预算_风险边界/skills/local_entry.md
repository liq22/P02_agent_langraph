---
skill_id: P0_05_项目约束_资源预算_风险边界_local_entry
purpose: 明确本项目的资源、计算、数据许可、伦理与失败边界，并压缩成局部决策工件。
node_mode: standard
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: structured_map_builder
outputs:
- docs/manuscript.md
- artifacts/constraint_risk_map.yaml
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
