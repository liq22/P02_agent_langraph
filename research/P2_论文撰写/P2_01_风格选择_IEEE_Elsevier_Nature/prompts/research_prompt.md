# P2_01_风格选择_IEEE_Elsevier_Nature research prompt

## 节点定位
- phase: `P2`
- node_kind: `leaf`
- node_path: `research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature`
- node_mode: `lite`
- node_profile: `lite_research_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 收敛目标 venue fit、contradiction list、证据缺口与局部写作规范。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 目标 venue 对 title/abstract/figures/methods 的要求差异是什么？
- 当前工作更适合哪种叙事粒度和格式？

### 本轮最小交付
- venue-fit 比较 (需由本节点形成或更新)
- 推荐风格与理由 (需由本节点形成或更新)
- artifacts/venue_requirements.yaml (记录 selected_profiles、venue-fit contradiction list、evidence gaps、scope fit 与 summary paragraph requirements)
- docs/manuscript.md (profile-required local artifact)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 claim-evidence 对齐、术语一致与章节边界清晰。
- 把本轮约束压在当前章节、图表或导出资产，不扩成整篇论文总控。

## 研究者视角
- role: top-conference paper author
- node_profile: lite_research_leaf
- 像顶会论文作者一样先建立一句话贡献，再组织段落、实验和图。
- 论文不是实验集合；每个段落、图和表都必须服务一个明确 claim。
- 写作应使用完整学术段落，不能用 bullet 堆成初稿。
- 用最小证据回答本节点关键研究判断；不靠增加 skill 数量冒充质量。
- 明确 claim/evidence 缺口，无法验证时写 gap，不写确定事实。

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
- 遵循目标 venue 的标题、摘要、方法、图表、数据/代码声明要求
- 不把目标 venue 选择写成 acceptance-ready；必须列出 contradiction list、evidence gaps 和 scope-fit 判断
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- one-sentence contribution、claim-evidence map、citation status 和 figure callout 都一致。
- 方法可复现，结果客观报告，讨论承认限制。
- 未验证 citation、无来源图、无证据 claim 均阻断完成态。

### 可交接条件
- 至少比较两种风格
- 形成一个明确推荐与备选
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
- 不把当前节点扩成整篇论文统一重写器。
- 不在无证据时维持核心 claim。

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
