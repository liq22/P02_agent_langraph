---
skill_id: P4_05_覆盖检查_local_entry
purpose: 检查当前 response node 对评论与证据的覆盖情况。
node_mode: standard
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_wrapper_skill: local_wrapper
required_local_reads:
- ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
- ../P4_03_逐点回复草稿_md/docs/manuscript.md
outputs:
- artifacts/coverage_check_report.yaml
---

Runtime entry shim for this standard node.

This shim applies to `research/P4_论文回复_response/P4_05_覆盖检查`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`
5. `../P4_03_逐点回复草稿_md/docs/manuscript.md`
6. `skills/SKILL.md`
7. `skills/local_wrapper.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
