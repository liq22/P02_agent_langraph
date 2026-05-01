---
skill_id: P2_03_定稿_tex_local_entry
purpose: 把当前定稿同步到 tex 导出目标，而不是扩成整套投稿流程。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_wrapper_skill: local_wrapper
required_local_reads:
- docs/manuscript.md
- section_map.yaml
- sync_map.yaml
outputs:
- tex/main.tex
---

Runtime entry shim for this standard node.

This shim applies to `research/P2_论文撰写/P2_03_定稿_tex`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `docs/manuscript.md`
5. `section_map.yaml`
6. `sync_map.yaml`
7. `skills/SKILL.md`
8. `skills/local_wrapper.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
