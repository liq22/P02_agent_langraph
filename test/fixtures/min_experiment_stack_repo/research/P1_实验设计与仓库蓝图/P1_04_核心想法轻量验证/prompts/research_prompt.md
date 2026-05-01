# P1_04_核心想法轻量验证 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`
- node_mode: `execution`
- node_profile: `experiment_execution`

## 本轮目标
### 节点职责
- 在本节点内推进一轮有界轻量验证；若 contract 未就绪则先补齐 handoff。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- baseline 是什么？
- primary metric 是什么？

### 本轮最小交付
- artifacts/auto_experiment/results.tsv
- logs/auto_experiment/latest_run.log

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`artifacts/execution_contract.yaml`。
5. 仅当这些补充上下文会改变当前有界轮次时，再按需读取：`docs/manuscript.md`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 execution contract、metric、budget、artifact 边界与 baseline-first 纪律说清。
- 只有 contract_mode 为 `executable` 时才进入 wrapper / worker；否则停在 prep / handoff。
- 只有 contract / required inputs ready 时才进入 binder；否则只做 preparation 或 handoff。
- 这是 experiment execution node：execution contract 是 gate，baseline/单变量尝试/keep-discard 要留在本地 ledger。
- `skills/local_wrapper.md` 只负责本地 IO 绑定，不重新定义节点语义。

### 质量门槛
- baseline-first
- contract-ready before execution
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。

### 可交接条件
- contract 完整
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

## 执行边界
### 明确不做
- 不在无 executable contract 时直接进入实验执行。
- 不把本节点扩成 repo-global experiment orchestrator。
- 不更改实验主工件路径，也不引入第二个 runtime experiment worker。
- 不要把 `skills/local_wrapper.md` 当作第二个语义层；它只是 IO binder。

### 停止条件
- execution contract 缺失或不完整
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- ['缺关键输入或关键证据', 'execution contract 缺失、字段不完整或 mode 仍为 `review_only` 时，只允许转交 contract-prep', '本节点范围不清或越出节点职责']
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
