---
skill_id: P2_02_05_实验与讨论_local_entry
purpose: 推进实验与讨论写作，并在必要时先做 claim-result 对齐。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: manuscript_worker
decision_rule:
- when: 结果与 claim 尚未对齐
  then:
    canonical_global_skill: result_to_claim
- when: 已有清晰 claim-result 对齐
  then: keep_default_delegate
required_local_reads:
- ../artifacts/outline_map.yaml
- docs/manuscript.md
- artifacts/claim_map.yaml
- ../../../P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/artifacts/claim_evidence_registry.yaml
outputs:
- docs/manuscript.md
- artifacts/claim_map.yaml
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../artifacts/outline_map.yaml`
5. `docs/manuscript.md`
6. `artifacts/claim_map.yaml`
7. `../../../P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/artifacts/claim_evidence_registry.yaml`
8. `skills/SKILL.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
