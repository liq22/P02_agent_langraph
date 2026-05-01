---
skill_id: P0_02_研究挑战与科学问题_工程问题_local_entry
purpose: 把研究挑战、科学问题与工程问题分层写清，并形成可证伪问题假设。
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
- artifacts/problem_hypothesis.yaml
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this lite node.

This shim applies to `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
