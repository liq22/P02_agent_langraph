---
skill_id: P2_02_04_方法_local_entry
purpose: 推进方法章节局部草稿，保持术语、流程与符号一致。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: manuscript_worker
required_local_reads:
- ../artifacts/outline_map.yaml
outputs:
- docs/manuscript.md
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P2_论文撰写/P2_02_初稿_md/P2_02_04_方法`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../artifacts/outline_map.yaml`
5. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
