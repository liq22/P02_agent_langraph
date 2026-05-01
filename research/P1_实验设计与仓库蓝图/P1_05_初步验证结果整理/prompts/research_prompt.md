# P1_05_初步验证结果整理 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `result_synthesis`

## 本轮目标
### 节点职责
- 收敛初步验证结果、证据状态与结论边界。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 哪些结果支持当前主张？
- 哪些结果必须标为 unsupported 或 unclear？
- 哪些结果可以安全进入正文、表格或图？

### 本轮最小交付
- artifacts/result_registry.yaml (需由本节点形成或更新)
- artifacts/hypothesis_status.yaml (需由本节点形成或更新)
- artifacts/paper_ready_result_summary.md (需由本节点形成或更新)
- artifacts/gate_report.md (profile-required local artifact)
- artifacts/claim_evidence_registry.yaml

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`。
5. 仅当这些补充上下文会改变当前有界轮次时，再按需读取：`docs/manuscript.md`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 results ledger、evidence location、claim boundary 与不确定性说清。
- 先压 registry / hypothesis status，再决定是否补最小正文摘要。
- 这是 result synthesis node：declared results ledger 是主输入，先压 registry/status，再决定可写入正文的最小摘要。
- `skills/local_execution.md` 只负责一轮本地执行，不承担路由职责。

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
- 每条结论都能回指到 results ledger 中的具体证据位置
- 明确 supported / unsupported / unclear，不把缺证据项写成正结论
- 负结果、不确定性与证据缺口需要保留，不能静默吞掉
- 不提高 claim 强度
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- protocol、baseline、metric、预算、artifact path 和 stop condition 都明确。
- 结果账本能区分 supported、unsupported 和 unclear。
- 可复现路径缺失时不得进入执行或写作完成态。

### 可交接条件
- 至少区分 supported/unsupported/unclear
- result registry 与 hypothesis status 已能支撑后续 figure/table/claim
- 证据位置明确
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
- 不重开 baseline / experiment loop。
- 不把 execution contract 当作本节点 gate。
- 不在证据不足时抬高 claim 强度，也不把结果整理扩成全局 figure/table 管理器。
- 不要把 `skills/local_execution.md` 当作第二个 orchestrator；它只执行一轮 bounded local round。

### 停止条件
- 缺关键输入或关键证据
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
