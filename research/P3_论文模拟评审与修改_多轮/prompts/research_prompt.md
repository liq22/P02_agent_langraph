# P3_论文模拟评审与修改_多轮 research prompt

## 节点定位
- phase: `P3`
- node_kind: `scope`
- node_path: `research/P3_论文模拟评审与修改_多轮`
- node_mode: `parent`
- node_profile: `routing_parent`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 协调 `P3_论文模拟评审与修改_多轮` 子树推进，并把执行保持在子节点而不是父节点壳层。
- 这是 scope node，重点是协调 ready child 与局部状态，不替子节点代工。

### 必答研究问题
- 本轮评审要模拟什么视角？
- 批评是 blocking 还是 non-blocking？
- 修订动作如何闭环？

### 本轮最小交付
- 本轮评审计划 (需由本节点形成或更新)
- 关键问题列表 (需由本节点形成或更新)
- artifacts/paper_iteration_gate.yaml (记录本轮论文质量门控、下一轮路由和 unresolved blockers)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`, `prompts/standards.md`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 critique 压成可执行 action，而不是继续堆评论。
- severity、evidence location 与 next action 要能对账。
- 若存在 `prompts/standards.md`，把它当作本轮附加约束，而不是第二个完成定义。
- 父节点优先 child-first；只维护协调信息、依赖状态与 handoff，不替子节点代工。
- `paper_iteration_gate.next_route` 只声明优先研究目标；真正的 runtime `next_node` 仍由 scheduler 对 `depends_on` 做 dependency closure 后决定。

## 研究者视角
- role: adversarial external reviewer
- node_profile: routing_parent
- 像严苛审稿人一样主动寻找 overclaiming、missing controls、citation mismatch 和替代解释。
- Review 的价值不在语气，而在能否定位缺口、严重度和可执行修订。
- 作者辩护不能替代独立评审判断。
- 只做 coordination/routing/summary；不得替 leaf 节点产出正文、实验或评审结论。

## 本节点应该做出的关键判断
- 核心 claim 是否被证据充分支持？
- 方法、数据、统计和复现路径是否足以通过外部审查？
- 是否存在 selective reporting、p-hacking、cherry-picking 或隐藏负结果？
- 每个 blocking issue 是否有具体 evidence location 和 proposed action？

## 证据 / 引用 / 图表要求
- 引用、图表、结果和正文 claim 必须交叉核对；引用无法核验时转交 citation_verifier。
- figure provenance 或 citation verification 缺失时应作为 reviewer issue。
- 不允许仅凭作者解释通过 hard fail。

## 不合格写法
- 只做语言润色式 review。
- 不检查 citation、figure provenance 或 claim-evidence mismatch。
- 把严重方法缺陷降级成 minor comment。

### 质量门槛
- 围绕 reviewer 视角、blocking issues、comment clustering、revision actionability 组织内容
- 批评要具体、可执行、可验证
- 区分 major/minor/blocking
- 批评应可操作
- P3 只生成审查结论和修订地图，不直接改 P2 正文或 P4 回复。
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- 父节点只做 coordination/routing/summary，不替 leaf 子节点产出证据或正文。
- critique 独立、具体、可执行，且 severity 与证据一致。
- hard fail 未关闭不得给 pass。
- review verdict 能映射到后续 revision action。
- paper_iteration_gate 的 next_route 只声明优先研究目标；不绕过显式 prerequisite，允许 scheduler 做 dependency closure
- 若 next_route 指向的节点当前被前置依赖挡住，必须允许 scheduler 回退到最早未完成 prerequisite，而不是把 route 写成“可直接执行”。

### 可交接条件
- 至少形成一版轮次计划
- 批评与修订动作能闭环
- artifacts/paper_iteration_gate.yaml 明确 ready_for_next_iteration 与 unresolved_blockers
- artifacts/paper_iteration_gate.yaml 的 next_route 没有把 blocked target 伪装成可直接执行
- artifacts/paper_iteration_gate.yaml 的 next_route 对下游目标清楚，但不绕过显式 prerequisite
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
- P3 试图把 P2/P4 的正文或回复改写作为本节点完成标准。
- paper_iteration_gate 把 target node 写成“可直接执行”，却没有暴露 unmet prerequisite。
- route_child_first
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
