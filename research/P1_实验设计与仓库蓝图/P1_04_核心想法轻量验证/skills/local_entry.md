---
skill_id: P1_04_核心想法轻量验证_local_entry
purpose: 在本节点内推进一轮有界轻量验证；若 contract 或 repo binding 未就绪则先补齐 blocker handoff。
node_mode: execution
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
execution_profile: experiment_execution
default_delegate:
  local_wrapper_skill: local_wrapper
decision_rule:
- when: artifacts/execution_contract.yaml 缺失
  then:
    canonical_global_skill: experiment_design_or_execution
- when: contract_mode != executable、contract 不完整、repo_path 缺失、repo_path 路径不存在或 run target 不可绑定
  then:
    canonical_global_skill: experiment_design_or_execution
- when: contract_mode == executable、contract 完整、repo_path 在 workspace 中存在且 run target 可绑定
  then: keep_default_delegate
required_local_reads:
- artifacts/execution_contract.yaml
optional_local_reads:
- docs/manuscript.md
outputs:
- artifacts/gate_report.md
- artifacts/auto_experiment/results.tsv
- logs/auto_experiment/latest_run.log
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Runtime entry shim for this execution node.

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
