---
skill_id: P1_04_核心想法轻量验证_local_entry
purpose: 在本节点内推进一轮有界轻量验证；若 contract 未就绪则先补齐 handoff。
node_profile: experiment_execution
default_delegate:
  local_wrapper_skill: local_wrapper
decision_rule:
- when: artifacts/execution_contract.yaml 缺失
  then:
    canonical_global_skill: experiment_design_or_execution
- when: contract_mode != executable 或 contract 不完整
  then:
    canonical_global_skill: experiment_design_or_execution
- when: contract_mode == executable 且 contract 完整
  then: keep_default_delegate
required_local_reads:
- artifacts/execution_contract.yaml
optional_local_reads:
- docs/manuscript.md
outputs:
- artifacts/auto_experiment/results.tsv
- logs/auto_experiment/latest_run.log
extra_status_updates:
- lifecycle.stage
- progress_pct
stop_with:
- 缺关键输入或关键证据
- execution contract 缺失、字段不完整或 mode 仍为 `review_only` 时，只允许转交 contract-prep
- 本节点范围不清或越出节点职责
---

Runtime entry shim for this node-local research stack.

This shim applies to `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `artifacts/execution_contract.yaml`
5. `skills/SKILL.md`
6. `skills/SOP.md`
7. `skills/local_wrapper.md`

Optional local reads (only when they materially change this bounded round):
- `docs/manuscript.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
