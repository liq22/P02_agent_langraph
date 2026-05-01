# P1_05_初步验证结果整理 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`
- node_mode: `execution`
- node_profile: `result_synthesis`

## 本轮目标
### 节点职责
- 收敛轻量验证结果，形成支持/不支持/待澄清的结论边界。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 无

### 本轮最小交付
- artifacts/result_registry.yaml
- artifacts/hypothesis_status.yaml

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`artifacts/auto_experiment/results.tsv`。
5. 仅当这些补充上下文会改变当前有界轮次时，再按需读取：`docs/manuscript.md`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 results ledger、evidence location、claim boundary 与不确定性说清。
- 先压 registry / hypothesis status，再决定是否补最小正文摘要。
- 这是 result synthesis node：`artifacts/auto_experiment/results.tsv` 是主输入，先压 registry/status，再决定可写入正文的最小摘要。
- `skills/local_execution.md` 只负责一轮本地执行，不承担路由职责。

### 质量门槛
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。

### 可交接条件
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

## 执行边界
### 明确不做
- 不重开 baseline / experiment loop。
- 不把 execution contract 当作本节点 gate。
- 不在证据不足时抬高 claim 强度，也不把结果整理扩成全局 figure/table 管理器。
- 不要把 `skills/local_execution.md` 当作第二个 orchestrator；它只执行一轮 bounded local round。

### 停止条件
- fixture_missing_inputs
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
