# P0_项目申请书 research prompt

## 节点定位
- phase: `P0`
- node_kind: `scope`
- node_path: `research/P0_项目申请书`
- node_mode: `parent`
- node_profile: `routing_parent`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 协调 `P0_项目申请书` 子树推进，并把执行保持在子节点而不是父节点壳层。
- 这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。

### 必答研究问题
- 五个子节点的主线是否自洽，没有互相冲突的定义或目标？
- 项目的核心问题、预期结果、意义与资源边界是否能被同一评审视角快速理解？
- 是否存在过度承诺、目标过宽或 feasibility 不足的问题？

### 本轮最小交付
- docs/manuscript.md（项目申请书总控摘要或主线草图） (需由本节点形成或更新)
- 对子节点的一致性修正建议 (需由本节点形成或更新)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/standards.md`, `prompts/review_rubric.yaml`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 significance、gap、aims、expected outcomes 与 impact 压成 reviewer 可快速判断的表达。
- 避免空泛承诺；目标、阶段、风险与资源假设都要可检验。
- 若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。
- 父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。

## 研究者视角
- role: problem-formulation PI
- node_profile: routing_parent
- 像 PI 一样先问“这个问题为什么现在必须做”，再问“我们能做什么”。
- 综述不是文献堆叠；必须综合方法簇、共同假设、失败边界和未被解决的约束。
- novelty 必须相对强基线成立，不能靠换名词、换场景或扩大叙事制造。
- 只做 coordination/routing/summary；不得替 leaf 节点产出正文、实验或评审结论。

## 本节点应该做出的关键判断
- 当前领域的主要未解瓶颈是什么？
- 现有强方法已经解决了什么，明确没有解决什么？
- 本项目的 gap 是否足够具体，是否能被后续实验或论证反驳？
- 预期贡献是否值得一个 skeptical reviewer 继续读？

## 证据 / 引用 / 图表要求
- 背景和 related-work 判断必须绑定可核验来源；未验证 citation 只能标为待核验。
- 每个核心 gap 至少要能指向代表性 prior work、失败模式或权威综述。
- 若画概念图，只能表达问题结构和方法簇关系，不能暗示尚未证明的性能优势。

## 不合格写法
- 用泛泛背景替代具体 gap。
- 把未验证的文献印象写成确定事实。
- 把工程可做性误写成科学或方法贡献。

### 质量门槛
- 围绕 significance、gap、hypothesis/aims、expected outcomes、impact、feasibility 组织内容
- 避免空泛承诺，优先 reviewer 可快速判断的清晰目标
- 目标明确、预期结果清楚、影响可解释、范围可完成
- 避免过度 ambition，保持 aims/路线/资源一致
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- 父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。
- gap、novelty、feasibility 和 risk 都能被 reviewer 独立检查。
- 没有把 proposal 目标写成已经证实的论文结论。
- 关键 citation 缺失或未验证时不得进入下游完成态，应转交 citation_verifier 或报告 citation gate。

### 可交接条件
- 五个子节点在术语、目标、方法、预期结果上保持一致
- 至少给出一版总控主线或总览摘要
- 没有明显过宽、不可评估、不可完成的承诺
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
