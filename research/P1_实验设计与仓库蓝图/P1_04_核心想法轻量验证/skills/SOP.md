---
name: P1_04_核心想法轻量验证_node_sop
description: Ordered operating procedure for `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`.
  Use only when this node declares `skills/SOP.md`.
---

# P1_04_核心想法轻量验证 SOP

This SOP applies to `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`.

## Read Order
1. README.md
2. status.yaml
3. skills/local_entry.md
4. prompts/research_prompt.md
5. prompts/acceptance_checklist.yaml
6. skills/SKILL.md
7. prompts/review_rubric.yaml
8. artifacts/execution_contract.yaml
9. skills/SOP.md
10. skills/local_wrapper.md

## Preflight
- 确认 `skills/local_entry.md` 已经选择了当前有序本地流程。
- 确认 `prompts/acceptance_checklist.yaml` 可用，并且将作为唯一完成定义门槛。
- 确认默认必需的本地工作输入已存在：`artifacts/execution_contract.yaml`。
- 确认 `skills/local_wrapper.md` 与其 IO contract 已可用。
- 确认 `artifacts/execution_contract.yaml` 已存在且 `contract_mode == executable`。
- 确认本轮输出路径固定在 `artifacts/auto_experiment/results.tsv` 与 `logs/auto_experiment/latest_run.log`。
- 仅当需要校对 claim / context 时，再读取这些补充材料：`docs/manuscript.md`。

## Operating Procedure
1. 把本轮限制为一个 bounded experiment round，不扩大到第二个 node 或第二套 worker。
2. 先过 execution contract gate；只要 contract 缺失、字段不完整或 mode 不是 `executable`，立即停在 handoff / repair。
3. 若路径进入 `skills/local_wrapper.md`，只绑定本地 IO，然后委托一次 `auto_experiment_worker` bounded round。
4. 记录 baseline、变更点、metric 结果与 keep/discard 决策；失败也要留 stop reason。
5. 只更新当前节点工件和状态，不替其他节点代工。

## Stop Rules
- 缺关键输入或关键证据
- execution contract 缺失、字段不完整或 mode 仍为 `review_only` 时，只允许转交 contract-prep
- 本节点范围不清或越出节点职责
- 必须依赖的上游节点尚未就绪
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- hard gate 缺 citation/figure/venue/coverage/revision evidence 中的适用工件。
- blocking issue 没有 claim_id/evidence_id/location/actionable_fix。

## Delegate Notes
- Default path: delegate to local wrapper `local_wrapper`.
- When `artifacts/execution_contract.yaml 缺失`, delegate to canonical worker `experiment_design_or_execution`.
- When `contract_mode != executable 或 contract 不完整`, delegate to canonical worker `experiment_design_or_execution`.
- When `contract_mode == executable 且 contract 完整`, keep_default_delegate.
- This node binds a local wrapper; enter `skills/local_wrapper.md` only after the tier-required local stack has been loaded.
