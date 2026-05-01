---
name: P1_05_初步验证结果整理_node_sop
description: Ordered operating procedure for `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`.
  Use only for execution-tier nodes after `skills/SKILL.md`.
---

# P1_05_初步验证结果整理 SOP

This SOP applies to `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`.

## Read Order
1. README.md
2. status.yaml
3. skills/local_entry.md
4. prompts/research_prompt.md
5. prompts/acceptance_checklist.yaml
6. skills/SKILL.md
7. prompts/review_rubric.yaml
8. artifacts/auto_experiment/results.tsv
9. skills/local_execution.md

## Preflight
- 确认 `skills/local_entry.md` 已经选择了当前 execution-tier 路径。
- 确认 `prompts/acceptance_checklist.yaml` 可用，并且将作为唯一完成定义门槛。
- 确认默认必需的本地工作输入已存在：`artifacts/auto_experiment/results.tsv`。
- 确认 `skills/local_execution.md` 与其 declared required inputs 已可用。
- 确认 `artifacts/auto_experiment/results.tsv` 已存在且本轮可解析。
- 确认当前节点可回写 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`。
- 仅当需要生成最小 paper 摘要或定位 claim 上下文时，再读取这些补充材料：`docs/manuscript.md`。

## Operating Procedure
1. 把本轮限制为一次结果收敛，不重开实验执行。
2. 先读取并压缩 `artifacts/auto_experiment/results.tsv`，提取 baseline / variant / decision / claim impact 证据。
3. 按 supported / unsupported / unclear 更新 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`。
4. 只在证据位置明确时补最小 paper 摘要；否则报告缺口而不是补写强结论。
5. 若路径进入 `skills/local_execution.md`，它只负责这一轮结果收敛，不读取 execution contract。

## Stop Rules
- fixture_missing_inputs
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭

## Delegate Notes
- Default path: delegate to local execution `local_execution`.
- This node binds local execution; enter `skills/local_execution.md` only after the tier-required local stack has been loaded.
