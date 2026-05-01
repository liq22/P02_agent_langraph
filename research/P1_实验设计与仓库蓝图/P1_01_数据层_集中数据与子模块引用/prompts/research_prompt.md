# P1_01_数据层_集中数据与子模块引用 research prompt

## 节点定位
- phase: `P1`
- node_kind: `leaf`
- node_path: `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 收敛数据对象、数据血缘与子模块引用关系，保持输入边界清晰。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 数据从哪里来、以什么版本和许可存在？
- 数据与代码/子模块如何绑定？
- 是否满足可发现、可访问、可复用的最小要求？

### 本轮最小交付
- 数据层描述 (需由本节点形成或更新)
- 数据/子模块清单 (需由本节点形成或更新)
- 最小 provenance 说明 (需由本节点形成或更新)
- artifacts/claim_evidence_registry.yaml (profile-required local artifact)
- artifacts/failure_register.yaml (profile-required local artifact)
- artifacts/negative_result_note.md (profile-required local artifact)
- artifacts/keep_discard_ledger.yaml (profile-required local artifact)
- docs/manuscript.md
- artifacts/data_lineage.yaml
- artifacts/submodule_ref.yaml

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 没有额外输入时，不主动扩张读取范围。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 protocol、metric、baseline、artifact 边界与 reproducibility 约束说清。
- 只有 contract / inputs ready 时才进入执行层，否则停在 prep / handoff。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。

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
- 强调 metadata、version、license、access、provenance
- artifact 需 documented/consistent/complete/exercisable
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- protocol、baseline、metric、预算、artifact path 和 stop condition 都明确。
- 结果账本能区分 supported、unsupported 和 unclear。
- 可复现路径缺失时不得进入执行或写作完成态。

### 可交接条件
- 数据来源与版本明确
- 子模块引用关系明确
- 最小复现所需的数据与依赖已说明
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
