# P2_论文撰写 research prompt

## 节点定位
- phase: `P2`
- node_kind: `scope`
- node_path: `research/P2_论文撰写`
- node_mode: `parent`
- node_profile: `routing_parent`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 协调 `P2_论文撰写` 子树推进，并把执行保持在子节点而不是父节点壳层。
- 这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。

### 必答研究问题
- 整篇论文的 claim 主线是否一致？
- 章节顺序与信息密度是否合理？
- 投稿目标与写作风格是否匹配？

### 本轮最小交付
- 论文主线摘要 (需由本节点形成或更新)
- 跨章节协调建议 (需由本节点形成或更新)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`, `prompts/standards.md`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 claim-evidence 对齐、术语一致与章节边界清晰。
- 把本轮约束压在当前章节、图表或导出资产，不扩成整篇论文总控。
- 若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。
- 父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。

## 研究者视角
- role: top-conference paper author
- node_profile: routing_parent
- 像顶会论文作者一样先建立一句话贡献，再组织段落、实验和图。
- 论文不是实验集合；每个段落、图和表都必须服务一个明确 claim。
- 写作应使用完整学术段落，不能用 bullet 堆成初稿。
- 只做 coordination/routing/summary；不得替 leaf 节点产出正文、实验或评审结论。

## 本节点应该做出的关键判断
- 本节是否清楚回答 What、Why、So What？
- 每个 claim 是否能追到结果、方法细节、图表或 verified citation？
- Figure 1 或关键图是否能让 skim reader 抓住贡献和证据路径？
- limitations 是否诚实约束了 claim 强度？

## 证据 / 引用 / 图表要求
- citation 必须可验证；无法验证时转交 citation_verifier、改成占位并阻断 handoff。
- figure 初稿可来自 TeX、Python 或人类 PDF，但必须有 provenance、claim_ref 和 evidence_ref。
- node 状态为 done 后，已接受 figure 不得覆盖修改，只能 reopen 或新建 revision version。

## 不合格写法
- 用流畅叙事掩盖无证据 claim。
- 引言泛泛开头，没有具体贡献和 reviewer path。
- 图表好看但没有 provenance、claim_ref 或 evidence_ref。

### 质量门槛
- 围绕 IMRAD、methods 可复现、results 顺序、figure/table 自解释、venue format 组织内容
- 正文服务主张，不重复图表，不夸大结论
- 整体遵循 IMRAD 或目标 venue 的合理结构
- 章节服务主张而不是堆内容
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- 父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。
- one-sentence contribution、claim-evidence map、citation status 和 figure callout 都一致。
- 方法可复现，结果客观报告，讨论承认限制。
- 未验证 citation、无来源图、无证据 claim 均阻断完成态。

### 可交接条件
- 全篇主线明确
- 章节之间不冲突
- 写作目标与 venue 选择一致
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
