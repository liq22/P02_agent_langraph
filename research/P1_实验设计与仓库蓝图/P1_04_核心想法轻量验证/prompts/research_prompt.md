# P1_04_核心想法轻量验证 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `experiment_execution`

## 本轮目标
### 节点职责
- 在本节点内推进一轮有界轻量验证；若 contract 或 repo binding 未就绪则先补齐 blocker handoff。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- baseline 是什么？
- primary metric 是什么？
- 这一轮只改变哪个概念因素？
- 什么结果算 keep，什么结果算 discard？

### 本轮最小交付
- artifacts/gate_report.md (每轮都要形成或更新；若无法执行，则记录 blocker、claim boundary 与 handoff)
- artifacts/auto_experiment/results.tsv (仅在 contract 可执行且进入真实执行回合时形成或更新)
- logs/auto_experiment/latest_run.log (仅在 contract 可执行且进入真实执行回合时形成或更新)
- 轻量验证结论摘要 (执行回合给 keep/discard；blocker 回合给明确 handoff summary)

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
- 只有 contract_mode 为 `executable`、repo_path 在 workspace 中真实存在且 run target 可绑定时才进入 wrapper / worker；否则停在 prep / blocker handoff。
- 只有 contract / required inputs ready 时才进入 binder；否则只做 preparation 或 handoff。
- 这是 experiment execution node：execution contract 是 gate，baseline/单变量尝试/keep-discard 要留在本地 ledger。
- `skills/local_wrapper.md` 只负责本地 IO 绑定，不重新定义节点语义。

## 研究者视角
- role: experiment lead
- node_profile: hard_gate
- 像实验负责人一样先问“这个实验能支持或推翻哪个 claim”。
- baseline、ablation、metric 和 failure mode 必须在执行前定义，不能结果出来后补故事。
- 实验协议要能让另一个 agent 或 reviewer 复现关键路径。
- 只在 review/submission/venue/response gate 阶段 hard block；authoring 阶段只能报告缺口。
- hard fail 必须带 claim_id/evidence_id/location/actionable_fix，否则降级为 advisory critique。

## 本节点应该做出的关键判断
- 当前 protocol 是否足以区分方法有效、数据偶然、实现偏差和 metric 偏差？
- baseline 是否是 reviewer 会认可的强基线，而不是方便基线？
- 失败结果应如何解释，哪些失败会要求收缩 claim？
- 当前 artifact 是否足以让下游写作引用或复查？

## 证据 / 引用 / 图表要求
- 实验设计要绑定数据来源、配置、随机性、预算和 metric parser。
- 表格/图计划必须提前说明每列或每张图支持哪个 claim。
- 未完成执行的节点不得把预期结果写成 observed evidence。

## 不合格写法
- 没有强基线或只写“后续补充实验”。
- metric 无法解析或无法和 claim 对齐。
- 结果整理时把 unclear evidence 抬高成 supported claim。

### 质量门槛
- 围绕 baseline、metric、protocol、reproducibility、artifact 完整性组织内容
- 明确 documented / consistent / complete / exercisable 的最低要求
- baseline-first、metric-driven、单轮单变化、可回滚
- 记录 variance/statistical validity、failure interpretation 与 reproducibility 风险，不把单次波动写成稳定结论
- 不要猜 execution contract
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- protocol、baseline、metric、预算、artifact path 和 stop condition 都明确。
- repo_path 在 workspace 中可解析到真实验证仓库；否则只能 blocker-handoff
- 结果账本能区分 supported、unsupported 和 unclear。
- 可复现路径缺失时不得进入执行或写作完成态。

### 可交接条件
- contract 完整且 `contract_mode` 明确
- 若未进入执行回合，gate_report 已明确 repo_path/run_command/metric/baseline 缺口与下一交接节点
- 至少形成 1 次 baseline 与 1 次受控尝试的账本
- keep/discard 结论明确
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

### 作者退出条件
- gate_inputs_verified: true
- blocking_gaps_are_explicit: true

### 节点关闭条件
- review/verdict.yaml:review_complete: true
- review/verdict.yaml:overall_verdict: pass
- review/verdict.yaml:hard_fail: false
- review/verdict.yaml:independence_confirmed: true

## 执行边界
### 明确不做
- 不在无 executable contract 时直接进入实验执行。
- 不在 repo_path 缺失或路径不存在时伪造 results.tsv / latest_run.log。
- 不把本节点扩成 repo-global experiment orchestrator。
- 不更改实验主工件路径，也不引入第二个 runtime experiment worker。
- 不要把 `skills/local_wrapper.md` 当作第二个语义层；它只是 IO binder。

### 停止条件
- 缺关键输入或关键证据
- execution contract 缺失、字段不完整或 mode 仍为 `review_only` 时，只允许转交 contract-prep
- repo_path 缺失、路径不存在或 run target 不可绑定时，只允许转交 blocker handoff
- 本节点范围不清或越出节点职责
- 必须依赖的上游节点尚未就绪
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- hard gate 缺 citation/figure/venue/coverage/revision evidence 中的适用工件。
- blocking issue 没有 claim_id/evidence_id/location/actionable_fix。
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
