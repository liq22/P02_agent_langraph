# P2_04_形式检查 research prompt

## 节点定位
- phase: `P2`
- node_kind: `leaf`
- node_path: `research/P2_论文撰写/P2_04_形式检查`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 执行一次有界形式检查，核对 citation criticality、figure provenance、venue requirements 与高置信格式问题。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 标题、摘要、图表、references、units、availability statements 是否合规？
- 是否存在明显结构/格式缺失？

### 本轮最小交付
- artifacts/formal_check_report.md (需由本节点形成或更新)
- artifacts/gate_report.md (profile-required local artifact)
- artifacts/citation_registry.yaml (profile-required local artifact)
- artifacts/figure_manifest.yaml (profile-required local artifact)
- artifacts/venue_requirements.yaml (profile-required local artifact)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`docs/manuscript.md`, `../P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`, `../P2_03_定稿_tex/artifacts/citation_registry.yaml`, `../P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 claim-evidence 对齐、术语一致与章节边界清晰。
- 把本轮约束压在当前章节、图表或导出资产，不扩成整篇论文总控。
- 只有 contract / required inputs ready 时才进入 binder；否则只做 preparation 或 handoff。
- `skills/local_execution.md` 只负责一轮本地执行，不承担路由职责。

## 研究者视角
- role: top-conference paper author
- node_profile: hard_gate
- 像顶会论文作者一样先建立一句话贡献，再组织段落、实验和图。
- 论文不是实验集合；每个段落、图和表都必须服务一个明确 claim。
- 写作应使用完整学术段落，不能用 bullet 堆成初稿。
- 只在 review/submission/venue/response gate 阶段 hard block；authoring 阶段只能报告缺口。
- hard fail 必须带 claim_id/evidence_id/location/actionable_fix，否则降级为 advisory critique。

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
- 只报告高置信结构/格式问题
- 不在此节点重写科学内容
- 检查 citation criticality、core-claim block、figure provenance/first_callout_location 与 venue_requirements.yaml
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- one-sentence contribution、claim-evidence map、citation status 和 figure callout 都一致。
- 方法可复现，结果客观报告，讨论承认限制。
- 未验证 citation、无来源图、无证据 claim 均阻断完成态。

### 可交接条件
- 形成一版 formal check 报告
- 问题按严重性排序
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
- 不把当前节点扩成整篇论文统一重写器。
- 不在无证据时维持核心 claim。
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
