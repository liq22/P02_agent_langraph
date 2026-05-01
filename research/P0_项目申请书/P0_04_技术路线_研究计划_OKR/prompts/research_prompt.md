# P0_04_技术路线_研究计划_OKR research prompt

## 节点定位
- phase: `P0`
- node_kind: `leaf`
- node_path: `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 把技术路线、研究计划与 OKR 对齐成可执行的局部蓝图。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 研究将按什么阶段推进？
- 阶段成功的可观测指标是什么？
- 若某一步失败，是否存在降级路线？

### 本轮最小交付
- 技术路线草图 (需由本节点形成或更新)
- 阶段性计划与 OKR 草案 (需由本节点形成或更新)
- 风险分支说明 (需由本节点形成或更新)
- docs/manuscript.md (profile-required local artifact)
- artifacts/claim_evidence_registry.yaml (profile-required local artifact)
- artifacts/risk_decision_map.yaml (profile-required local artifact)
- artifacts/okr_map.yaml

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 significance、gap、aims、expected outcomes 与 impact 压成 reviewer 可快速判断的表达。
- 避免空泛承诺；目标、阶段、风险与资源假设都要可检验。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。

## 研究者视角
- role: problem-formulation PI
- node_profile: evidence_leaf
- 像 PI 一样先问“这个问题为什么现在必须做”，再问“我们能做什么”。
- 综述不是文献堆叠；必须综合方法簇、共同假设、失败边界和未被解决的约束。
- novelty 必须相对强基线成立，不能靠换名词、换场景或扩大叙事制造。
- 直接产出证据、图表、claim map 或协议的节点必须保留 claim/evidence 身份层。
- 负结果、失败解释和 keep/discard 决策是一等工件，不得被正结果叙事覆盖。

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
- 每个 aim/阶段都应有 clear endpoint
- 路线与资源/时间相匹配
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- gap、novelty、feasibility 和 risk 都能被 reviewer 独立检查。
- 没有把 proposal 目标写成已经证实的论文结论。
- 关键 citation 缺失或未验证时不得进入下游完成态，应转交 citation_verifier 或报告 citation gate。

### 可交接条件
- 至少形成 1 条主路线与 1 条风险分支
- 里程碑与评价点明确
- 没有明显超出时间/资源边界的路线
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

### 作者退出条件
- claim_evidence_ids_are_explicit_or_gap_is_reported: true
- negative_or_failed_results_recorded: true
- protected_paths_respected: true

### 节点关闭条件
- review/verdict.yaml:review_complete: true
- review/verdict.yaml:overall_verdict: pass
- review/verdict.yaml:hard_fail: false
- review/verdict.yaml:independence_confirmed: true

## 执行边界
### 明确不做
- 不把想法筛选扩成无界文献检索或全局 proposal 总控。
- 不在当前节点里替代 P1/P2/P3/P4 的执行逻辑。

### 停止条件
- 缺关键输入或关键证据
- 本节点范围不清或越出节点职责
- 必须依赖的上游节点尚未就绪
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- 核心 claim 没有 claim_id/evidence_id，或 evidence registry 与正文不一致。
- 负结果、失败实验、反例或限制被删除、隐藏或改写成正结果。
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
