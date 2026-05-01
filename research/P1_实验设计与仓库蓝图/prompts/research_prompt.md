# P1_实验设计与仓库蓝图 research prompt

## 节点定位
- phase: `P1`
- node_kind: `scope`
- node_path: `research/P1_实验设计与仓库蓝图`
- node_mode: `parent`
- node_profile: `routing_parent`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 协调 `P1_实验设计与仓库蓝图` 子树推进，并把执行保持在子节点而不是父节点壳层。
- 这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。

### 必答研究问题
- 实验设计链条是否闭环？
- 哪些子节点是依赖前置，哪些是并行准备？
- 是否存在缺 baseline、缺指标、缺 artifact 的薄弱环节？

### 本轮最小交付
- 实验设计总览摘要 (需由本节点形成或更新)
- 关键依赖/阻塞项列表 (需由本节点形成或更新)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/standards.md`, `prompts/review_rubric.yaml`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 protocol、metric、baseline、artifact 边界与 reproducibility 约束说清。
- 只有 contract / inputs ready 时才进入执行层，否则停在 prep / handoff。
- 若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。
- 父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。

## 研究者视角
- role: experiment lead
- node_profile: routing_parent
- 像实验负责人一样先问“这个实验能支持或推翻哪个 claim”。
- baseline、ablation、metric 和 failure mode 必须在执行前定义，不能结果出来后补故事。
- 实验协议要能让另一个 agent 或 reviewer 复现关键路径。
- 只做 coordination/routing/summary；不得替 leaf 节点产出正文、实验或评审结论。

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
- 强调可复现、可执行、artifact 自洽
- 只保留支撑主张所需的最小复杂度
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- 父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。
- protocol、baseline、metric、预算、artifact path 和 stop condition 都明确。
- 结果账本能区分 supported、unsupported 和 unclear。
- 可复现路径缺失时不得进入执行或写作完成态。

### 可交接条件
- 明确实验设计主链
- 依赖顺序与阻塞项清晰
- 没有明显缺协议/缺 baseline 的空洞
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

### 作者退出条件
- child_frontier_checked: true
- route_child_first_or_frontier_gap_reported: true
- no_leaf_content_authored_in_parent: true

### 节点关闭条件
- all_required_children_closed_or_blocked_with_reason: true
- parent_rollup_consistent_with_child_artifacts: true

## 执行边界
### 明确不做
- 不把父节点当成第二个正文仓库。
- 不跳过子节点 contract 直接在父节点内做深层执行。

### 停止条件
- 缺关键输入或关键证据
- 本节点范围不清或越出节点职责
- 必须依赖的上游节点尚未就绪
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- 父节点替 leaf 节点产出正文、实验、图表或审稿结论。
- 存在 ready child 但父节点继续深写，导致 route_child_first 被忽略。
- route_child_first
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
