# P4_论文回复_response research prompt

## 节点定位
- phase: `P4`
- node_kind: `scope`
- node_path: `research/P4_论文回复_response`
- node_mode: `parent`
- node_profile: `routing_parent`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 协调 `P4_论文回复_response` 子树推进，并把执行保持在子节点而不是父节点壳层。
- 这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。

### 必答研究问题
- 所有 reviewer/editor comments 是否都能被定位和追踪？
- 回复与 manuscript 修改是否一致？

### 本轮最小交付
- response program 摘要 (需由本节点形成或更新)
- 闭环风险列表 (需由本节点形成或更新)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`, `prompts/standards.md`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 point-by-point coverage、evidence 绑定与 change location 可追踪。
- 不承诺正文里不存在的改动，也不把回复写成泛泛解释。
- 若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。
- 父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。

## 研究者视角
- role: responsible rebuttal author
- node_profile: routing_parent
- 像负责任作者一样逐点回答，不逃避、不扩大承诺、不用语气替代证据。
- 每条 response 必须绑定 reviewer comment、正文改动位置和 evidence。
- 若需要改图或补引用，必须记录 revision provenance。
- 只做 coordination/routing/summary；不得替 leaf 节点产出正文、实验或评审结论。

## 本节点应该做出的关键判断
- 每条 reviewer concern 是否被直接覆盖？
- 回复中的每个承诺是否已反映在正文、图表、实验或 citation registry 中？
- 是否存在 evasive response、无证据承诺或未映射改动？
- submission package 是否保持 manuscript、figures、tables、evidence map 一致？

## 证据 / 引用 / 图表要求
- 回复引用的 citation 必须 verified，无法核验时转交 citation_verifier 或明确标注仍需人类/外部来源。
- 修改 figure 必须说明来源、版本、claim_ref、evidence_ref 和 change reason。
- 不得把未完成实验或未修改正文的内容写成已解决。

## 不合格写法
- 回复泛泛解释但没有正文改动位置。
- 承诺新增实验、图或引用但本地证据不存在。
- submission package 中正文、图表和 evidence map 不一致。

### 质量门槛
- 围绕 point-by-point response、clear description of changes、coverage 和 evidence 链组织内容
- 回复语气冷静专业，能指出具体修改位置
- point-by-point、证据定位清楚、语气冷静专业
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- 父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。
- comment coverage、evidence traceability、change location 和 package integrity 都可核对。
- 未关闭 review block 不得进入 resubmission ready。
- 所有 citation/figure/evidence 改动都能追到本地 artifact。

### 可交接条件
- 回复主流程完整
- 评论-修改-证据闭环清晰
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
