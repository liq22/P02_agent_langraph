# P3_03_批评摘要 research prompt

## 节点定位
- phase: `P3`
- node_kind: `leaf`
- node_path: `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`

## 本轮目标
### 节点职责
- 把本节点 review / critique 压缩成 digest，而不是继续扩写评论正文。
- 这是 leaf node，重点是完成当前节点最小可验证产出，不扩张到其他节点。

### 必答研究问题
- 哪些批评是同一根因的不同表述？
- 哪些问题最先修？
- review_issue_register 是否保留 source_comment_ids、severity、affected claim、evidence gap、location 与 next action？

### 本轮最小交付
- critique digest (需由本节点形成或更新)
- 问题聚类结果 (需由本节点形成或更新)
- artifacts/claim_evidence_registry.yaml (profile-required local artifact)
- artifacts/failure_register.yaml (profile-required local artifact)
- artifacts/negative_result_note.md (profile-required local artifact)
- artifacts/keep_discard_ledger.yaml (profile-required local artifact)
- artifacts/critique_digest.yaml (压缩后的 critique digest)
- artifacts/review_issue_register.yaml (原子化 review issue register)
- logs/session_manifest.yaml (记录 critique 聚合与外部评审会话)

完成定义以 `prompts/acceptance_checklist.yaml` 为准。

## 输入优先级
1. 先读取 `README.md`、`status.yaml` 与 `skills/local_entry.md`，确认当前节点范围、当前状态与路由前提。
2. 把 `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml` 当作本轮语义层与完成定义层；目标和 DoD 以这两者为准。
3. 若存在附加 prompt 资产，再按 `skills/local_entry.md` 的 read order 继续读取：`prompts/review_rubric.yaml`。
4. 默认必须补齐的 node-local 输入：`../prompts/standards.md`, `review/`。

## 阶段标准与局部附加约束
### 研究判断口径
- 优先把 critique 压成可执行 action，而不是继续堆评论。
- severity、evidence location 与 next action 要能对账。
- 本节点只补局部策略，不把 mapping / figure / digest / export 任务扩成 execution loop。

## 研究者视角
- role: adversarial external reviewer
- node_profile: evidence_leaf
- 像严苛审稿人一样主动寻找 overclaiming、missing controls、citation mismatch 和替代解释。
- Review 的价值不在语气，而在能否定位缺口、严重度和可执行修订。
- 作者辩护不能替代独立评审判断。
- 直接产出证据、图表、claim map 或协议的节点必须保留 claim/evidence 身份层。
- 负结果、失败解释和 keep/discard 决策是一等工件，不得被正结果叙事覆盖。

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
- 聚类后仍保留原 comment 可追溯性
- review_issue_register 按 checklist dimension 聚合，同时保留少数强反对意见和矛盾反馈。
- 节点产物必须能通过独立 reviewer agent 基于 `prompts/review_rubric.yaml` 的外部评审。
- critique 独立、具体、可执行，且 severity 与证据一致。
- hard fail 未关闭不得给 pass。
- review verdict 能映射到后续 revision action。

### 可交接条件
- 至少形成 blocking / non-blocking / cosmetic 三类聚合
- 每个 blocking issue 都能路由到 P3_04 修订动作或显式 blocker
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
- 核心 claim 没有 claim_id/evidence_id，或 evidence registry 与正文不一致。
- 负结果、失败实验、反例或限制被删除、隐藏或改写成正结果。
- 聚合会丢失 source_comment_ids、强反对意见或矛盾反馈。
- 若缺关键输入、关键证据或关键 prompt 资产，应停止并显式报告缺口。

## 供执行者填写的本轮摘要
- 本轮最小目标：把 P3_01/P3_02 reviewer 输入压缩为 P3_04 可消费的 critique digest 与 review_issue_register。
- 本轮不做什么：不改写 P2 TeX、不生成 P4 回复、不宣称最终投稿就绪。
- 完成定义：见 `prompts/acceptance_checklist.yaml`
- 完成后交给谁：P3_04 修订动作节点，承接 issue-p3-001 到 issue-p3-006。
