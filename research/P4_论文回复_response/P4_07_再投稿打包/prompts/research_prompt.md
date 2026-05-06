# P4_07_再投稿打包 research prompt

## 节点定位
- phase: `P4`
- node_kind: `leaf`
- node_path: `research/P4_论文回复_response/P4_07_再投稿打包`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 执行一次有界再投稿打包检查，核对 submission bundle consistency、citation registry、figure manifest、venue requirements 并生成 bundle manifest。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 哪些文件是必须的？
- clean / marked / response / source / supplementary 是否一致？

### 本轮最小交付
- artifacts/resubmission_bundle_manifest.yaml (需由本节点形成或更新)
- artifacts/question_mapping_matrix.yaml (profile-required local artifact)
- artifacts/coverage_check_report.yaml (profile-required local artifact)
- artifacts/revision_evidence_map.yaml (profile-required local artifact)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex`, `../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex`, `../P4_06_修改证据/artifacts/revision_evidence_map.yaml`, `artifacts/evidence_registry.yaml`, `artifacts/submission_metadata.yaml`, `../../P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml`, `../../P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml`, `../../P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`, `artifacts/figures/`, `artifacts/tables/`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先保证 point-by-point coverage、evidence 绑定与 change location 可追踪。
- 不承诺正文里不存在的改动，也不把回复写成泛泛解释。
- 只有 contract / required inputs ready 时才进入 binder；否则只做 preparation 或 handoff。
- `skills/local_execution.md` 只负责一轮本地执行，不承担路由职责。

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
- 文件齐全、命名一致、版本一致、可提交
- manifest 需覆盖 manuscript、response、evidence、figures、tables、metadata、citation_registry、figure_manifest、venue_requirements 九类资产
- submission bundle consistency 必须覆盖 citation registry、figure manifest、venue requirements 与 evidence map
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- hard-gate block 必须绑定 claim_id/evidence_id/location/actionable_fix；否则只能作为 advisory critique。
- comment coverage、evidence traceability、change location 和 package integrity 都可核对。
- 未关闭 review block 不得进入 resubmission ready。
- 所有 citation/figure/evidence 改动都能追到本地 artifact。

### 可交接条件
- 形成 manifest
- 必需文件和版本一致性检查通过
- manifest 中六类资产都能定位到实际文件
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
- 本轮最小目标：生成 P4_07 bundle manifest，核对 manuscript、response、evidence、figures、tables、metadata、citation registry、figure manifest、venue requirements、question mapping、coverage check 和 revision evidence map 是否都有可定位文件。
- 本轮不做什么：不伪造 official journal comments、manuscript id、editor metadata、accepted formal result evidence 或最终 submission-ready 状态。
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：交给最终 submission audit；若保留 blockers 未解决，manifest 只能作为 internal review handoff。
