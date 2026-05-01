---
skill_id: P0_03_研究内容与创新点_local_entry
purpose: 收敛研究内容拆分、贡献 claim 身份与创新点边界，避免 claim 膨胀。
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
- artifacts/contribution_claims.yaml
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this lite node.

This shim applies to `research/P0_项目申请书/P0_03_研究内容与创新点`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
