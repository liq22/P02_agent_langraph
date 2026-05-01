---
skill_id: P2_05_去AI味道_local_entry
purpose: 做学术表达与主张校准，提升 clarity、precision、claim restraint 与跨领域可读性，保持证据边界不变。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: deai_cn_skill
required_local_reads:
- docs/manuscript.md
outputs:
- docs/manuscript.md
- artifacts/academic_expression_claim_calibration.md
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P2_论文撰写/P2_05_去AI味道`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `docs/manuscript.md`
5. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
