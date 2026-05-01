---
skill_id: P3_02_评价者档案_local_entry
purpose: 收敛 EIC、method expert、domain expert、cross-disciplinary reader 与 devil's advocate
  reviewer lenses。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: structured_map_builder
required_local_reads:
- ../prompts/standards.md
outputs:
- artifacts/reviewer_profile_map.yaml
- artifacts/reviewer_lens_matrix.yaml
- logs/session_manifest.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../prompts/standards.md`
5. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
