# P1_09_结果图与草稿 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 推进结果图、图草稿与 claim-figure 对齐，而不是泛化成任意写作任务。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 每张图支持什么结论？
- panel 如何分工？
- legend 里该写什么、不该写什么？

### 本轮最小交付
- figure_plan (需由本节点形成或更新)
- claim_figure_map (需由本节点形成或更新)
- figures/ (需由本节点形成或更新)
- artifacts/claim_evidence_registry.yaml (profile-required local artifact)
- artifacts/failure_register.yaml (profile-required local artifact)
- artifacts/negative_result_note.md (profile-required local artifact)
- artifacts/keep_discard_ledger.yaml (profile-required local artifact)
- artifacts/figure_plan.yaml
- artifacts/claim_figure_map.yaml
- artifacts/figure_manifest.yaml

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`docs/manuscript.md`, `../P1_08_预期结果与表格/artifacts/claim_map.yaml`, `artifacts/figure_plan.yaml`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 protocol、metric、baseline、artifact 边界与 reproducibility 约束说清。
- 只有 contract / inputs ready 时才进入执行层，否则停在 prep / handoff。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。
- `skills/local_wrapper.md` 只负责本地 IO 绑定，不重新定义节点语义。

## 研究者视角
- role: experiment lead
- node_profile: evidence_leaf
- 像实验负责人一样先问“这个实验能支持或推翻哪个 claim”。
- baseline、ablation、metric 和 failure mode 必须在执行前定义，不能结果出来后补故事。
- 实验协议要能让另一个 agent 或 reviewer 复现关键路径。
- 像实验负责人一样保护 data split、baseline、metric、variance/statistical validity、failure interpretation 和 reproducibility。

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
- 图要简洁、自解释、legend 不塞方法细节
- 支持主张而不是炫图
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- protocol、baseline、metric、预算、artifact path 和 stop condition 都明确。
- 结果账本能区分 supported、unsupported 和 unclear。
- 可复现路径缺失时不得进入执行或写作完成态。

### 可交接条件
- 至少形成一版 figure plan
- claim 与 figure 对齐关系明确
- 输出路径明确
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
- 不在 contract 未齐时直接猜 execution 行为。
- 不把当前节点扩成 repo-global experiment orchestrator。
- 不要把 `skills/local_wrapper.md` 当作第二个语义层；它只是 IO binder。

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
- waiting_for_claim_map
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：<待填写>
- 本轮不做什么：<待填写>
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：<待填写>
