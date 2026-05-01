---
skill_id: P1_05_初步验证结果整理_local_entry
purpose: 收敛初步验证结果、证据状态与结论边界。
node_mode: execution
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
execution_profile: result_synthesis
default_delegate:
  local_execution_skill: local_execution
required_local_reads:
- research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
optional_local_reads:
- docs/manuscript.md
outputs:
- artifacts/result_registry.yaml
- artifacts/hypothesis_status.yaml
- artifacts/claim_evidence_registry.yaml
- artifacts/paper_ready_result_summary.md
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this execution node.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`
5. `skills/SKILL.md`
6. `skills/SOP.md`
7. `skills/local_execution.md`

Optional local reads (only when they materially change this bounded round):
- `docs/manuscript.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
