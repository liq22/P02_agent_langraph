# P0_02_研究挑战与科学问题_工程问题 research prompt

## 节点定位
- phase: `P0`
- node_kind: `leaf`
- node_path: `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题`
- node_mode: `lite`
- node_profile: `lite_research_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 把研究挑战、科学问题与工程问题分层写清，并形成可证伪问题假设。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 哪些问题属于机制/理论层，哪些属于系统/实现层？
- 问题是否可测试、可评价、可完成？
- 是否存在无法证伪或无法量化的表述？

### 本轮最小交付
- docs/manuscript.md 中的问题定义草稿 (需由本节点形成或更新)
- 科学问题/工程问题映射 (需由本节点形成或更新)
- docs/manuscript.md (profile-required local artifact)
- artifacts/literature_gap_map.yaml (profile-required local artifact)
- artifacts/problem_hypothesis.yaml

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

## 研究者视角
- role: problem-formulation PI
- node_profile: lite_research_leaf
- 像 PI 一样先问“这个问题为什么现在必须做”，再问“我们能做什么”。
- 综述不是文献堆叠；必须综合方法簇、共同假设、失败边界和未被解决的约束。
- novelty 必须相对强基线成立，不能靠换名词、换场景或扩大叙事制造。
- 像 PI 一样收敛 nearest prior work、真实 gap、科学/工程边界、可证伪问题和 feasibility。

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
- 问题必须可评估、可证据支撑、边界清晰
- 避免把 solution 直接写成 problem
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- gap、novelty、feasibility 和 risk 都能被 reviewer 独立检查。
- 没有把 proposal 目标写成已经证实的论文结论。
- 关键 citation 缺失或未验证时不得进入下游完成态，应转交 citation_verifier 或报告 citation gate。

### 可交接条件
- 至少形成 1 个科学问题和 1 个工程问题
- 每个问题都能对应后续内容/路线/评价
- 不存在显著不可评估表述
- 独立 reviewer agent 已生成 `review/verdict.yaml`
- `review/verdict.yaml` 中 `review_complete == true`
- `review/verdict.yaml` 中 `overall_verdict == pass`
- `review/verdict.yaml` 中 `hard_fail == false`
- `review/verdict.yaml` 中 `independence_confirmed == true`

### 作者退出条件
- required_artifacts_exist: true
- key_research_judgment_answered_or_gap_reported: true
- citation_status_checked_when_external_sources_are_used: true

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
- 缺少本节点关键研究判断，或把未验证引用/证据写成确定事实。
- 作者退出条件与节点关闭条件混用，导致未评审内容伪装完成。
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
