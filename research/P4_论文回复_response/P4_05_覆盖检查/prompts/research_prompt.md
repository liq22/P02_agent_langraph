# P4_05_覆盖检查 research prompt

## 节点定位
- phase: `P4`
- node_kind: `leaf`
- node_path: `research/P4_论文回复_response/P4_05_覆盖检查`
- node_mode: `standard`
- node_profile: `hard_gate`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 检查当前 response node 对评论与证据的覆盖情况。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 有没有 comment 被漏答？
- 有没有承诺修改但正文没改？
- 有没有证据链断裂？

### 本轮最小交付
- artifacts/coverage_check_report.yaml (需由本节点形成或更新)
- artifacts/question_mapping_matrix.yaml (profile-required local artifact)
- artifacts/revision_evidence_map.yaml (profile-required local artifact)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`, `../P4_03_逐点回复草稿_md/docs/manuscript.md`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 point-by-point coverage、evidence 绑定与 change location 可追踪。
- 不承诺正文里不存在的改动，也不把回复写成泛泛解释。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。
- `skills/local_wrapper.md` 只负责本地 IO 绑定，不重新定义节点语义。

## 研究者视角
- role: responsible rebuttal author
- node_profile: hard_gate
- 像负责任作者一样逐点回答，不逃避、不扩大承诺、不用语气替代证据。
- 每条 response 必须绑定 reviewer comment、正文改动位置和 evidence。
- 若需要改图或补引用，必须记录 revision provenance。
- 像负责任作者一样逐点绑定 reviewer comment、direct answer、正文位置、evidence 和 commitment status。

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
- coverage 不只看回复文本，还看正文/图表/证据一致性
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- comment coverage、evidence traceability、change location 和 package integrity 都可核对。
- 未关闭 review block 不得进入 resubmission ready。
- 所有 citation/figure/evidence 改动都能追到本地 artifact。

### 可交接条件
- 形成覆盖检查报告
- 漏项/弱项被显式标出
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
- 不承诺未批准的实验、数字、引用或改动。
- 不把局部回复节点扩成整套 submission manager。
- 不要把 `skills/local_wrapper.md` 当作第二个语义层；它只是 IO binder。

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
- 本轮最小目标：完成 P4_05 response-level 覆盖检查，确认 P4_01 六条评论均已映射到 P4_03 回复草稿、覆盖状态和 P4_06 待证据项。
- 本轮不做什么：不补写正式修订证据、不声称 P4_06/P4_07 已完成、不引入未验证实验、引用、图表或投稿系统状态。
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：交给 P4_06 修改证据节点关闭阻塞/计划中的修订证据项。
