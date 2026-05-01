---
skill_id: P1_09_结果图与草稿_local_entry
purpose: 推进结果图、图草稿与 claim-figure 对齐，而不是泛化成任意写作任务。
node_mode: standard
node_profile: evidence_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_wrapper_skill: local_wrapper
decision_rule:
- when: artifacts/figure_plan.yaml 缺失
  then: keep_default_delegate
- when: artifacts/figure_plan.yaml 已存在但 artifacts/claim_figure_map.yaml 缺失
  then:
    canonical_global_skill: result_to_claim
- when: 上游 claim_map 缺失
  stop_with: waiting_for_claim_map
required_local_reads:
- docs/manuscript.md
- ../P1_08_预期结果与表格/artifacts/claim_map.yaml
- artifacts/figure_plan.yaml
outputs:
- artifacts/figure_plan.yaml
- artifacts/claim_figure_map.yaml
- artifacts/figure_manifest.yaml
- figures/
extra_status_updates:
- progress_pct
---

Runtime entry shim for this standard node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `docs/manuscript.md`
5. `../P1_08_预期结果与表格/artifacts/claim_map.yaml`
6. `artifacts/figure_plan.yaml`
7. `skills/SKILL.md`
8. `skills/local_wrapper.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
