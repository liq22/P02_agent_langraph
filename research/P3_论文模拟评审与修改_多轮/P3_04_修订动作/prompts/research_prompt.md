# P3_04_修订动作 research prompt

## 节点定位
- phase: `P3`
- node_kind: `leaf`
- node_path: `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作`
- node_mode: `standard`
- node_profile: `hard_gate`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 把批评摘要转成可执行修订动作图，而不是泛化成任意 revision 任务。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 每条批评的最小修订动作是什么？
- 修改后如何验证问题真的被解决？
- revision_action_map 是否为每个 blocking issue 指定 target_phase、target_node、action_type、expected_evidence、validation_gate 与 next_iteration_trigger？

### 本轮最小交付
- revision action map (需由本节点形成或更新)
- artifacts/review_issue_register.yaml (profile-required local artifact)
- artifacts/critique_digest.yaml (profile-required local artifact)
- artifacts/revision_action_map.yaml (可路由、可验证的修订动作图)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`../prompts/standards.md`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 critique 压成可执行 action，而不是继续堆评论。
- severity、evidence location 与 next action 要能对账。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。
- revision action 指向的是优先修订目标；若该目标当前被 prerequisite 挡住，调度器可回退到最早未完成前置节点。

## 研究者视角
- role: adversarial external reviewer
- node_profile: hard_gate
- 像严苛审稿人一样主动寻找 overclaiming、missing controls、citation mismatch 和替代解释。
- Review 的价值不在语气，而在能否定位缺口、严重度和可执行修订。
- 作者辩护不能替代独立评审判断。
- 像独立审稿人一样用 source isolation、severity、evidence location、affected claim 和 actionable fix 约束批评。

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
- comment -> action -> evidence -> file location 一一对应
- revision_action_map 中每个 action 都绑定 target_phase、target_node、action_type、expected_evidence、validation_gate 与 next_iteration_trigger。
- 若 target_node 当前有 unmet prerequisite，action 的验证说明允许 dependency closure 回退，而不是把 blocked target 伪装成 ready leaf
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- critique 独立、具体、可执行，且 severity 与证据一致。
- hard fail 未关闭不得给 pass。
- review verdict 能映射到后续 revision action。

### 可交接条件
- 主要批评都有修订动作
- 动作可追踪到具体文件与证据
- 每个 blocking issue 都有 action 或 unresolved blocker，不允许静默消失
- target_node 若当前不可直达，其 prerequisite gap 已被显式记录
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
- 不把作者辩护当成独立评审结论。
- 不把当前 review 节点扩成多节点总 review engine。

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
- revision action 缺 target node、expected evidence 或 validation gate。
- revision action 把 blocked target 写成 ready leaf，却没有允许 scheduler 回退到 prerequisite。
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：把 P3_03 的 6 个 issue 转成 P3_04 可验证 revision_action_map。
- 本轮不做什么：不直接改写 P2 TeX、不修复 P1/P4 证据、不宣称最终投稿就绪。
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：P4 response/coverage 节点与后续证据修复节点，承接 action-p3-001 到 action-p3-006。
