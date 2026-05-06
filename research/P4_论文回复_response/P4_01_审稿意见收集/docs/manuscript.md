# P4_01 审稿意见收集

## 目标
本节点收集当前可用的 review comments，并把它们标准化为后续 P4_02 问题映射、P4_03 逐点回复、P4_05 覆盖检查和 P4_06 修改证据的输入。当前没有 official journal decision letter 或 official reviewer comments；因此本节点只收集 P3_04/P4_04 已审计的 simulated-review action comments，并把 official-comment 缺口作为 retained blocker。

## 输入边界
已使用的可审计输入：

- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/revision_action_map.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/review_issue_register.yaml`
- `research/P4_论文回复_response/P4_04_正式回复_tex_或_doc/artifacts/Reviewers/R1.tex`
- `research/P4_论文回复_response/P4_04_正式回复_tex_或_doc/artifacts/Reviewers/R2.tex`
- `research/P4_论文回复_response/P4_04_正式回复_tex_或_doc/artifacts/Reviewers/R3.tex`

未使用且仍缺失的输入：

- official manuscript ID
- official decision type
- official editor name
- official editor comment
- official reviewer comment verbatim text
- journal anonymity/export rule

## 当前结论
当前可用评论已完整保留在 `artifacts/review_comment_register.yaml`。该 register 包含 6 条标准化 comment records：

- `p4-01-c001`: formal evidence eligibility blocker, from `action-p3-001` / `issue-p3-001`
- `p4-01-c002`: reproducibility artifact-state blocker, from `action-p3-002` / `issue-p3-002`
- `p4-01-c003`: global validator and response coverage blocker, from `action-p3-003` / `issue-p3-003`
- `p4-01-c004`: claim-language density planned edit, from `action-p3-004` / `issue-p3-004`
- `p4-01-c005`: figure/table reader-path planned edit, from `action-p3-005` / `issue-p3-005`
- `p4-01-c006`: style repetition cosmetic edit, from `action-p3-006` / `issue-p3-006`

## Final-Threshold Score Boundary
本节点的 final-threshold re-review 只评价 P4_01 是否把当前可用审稿意见收集、拆分和边界记录到足以支撑 P4_02 问题映射。AI_002 若给出通过结论，只能清除 P4_01 当前节点的 score blocker；不得声称 official comments 已存在、response package 已完成、P3_04 actions 已关闭、P1 checklist 已关闭，或全局 submission-ready validator 已通过。

AI_002 前的全局 gate 仍保留三类 blocker：109 个 P1_01-P1_05 checklist pending fields、7 个 P4 score blockers、6 个 P3_04 blocked/planned action statuses。P4_01 的通过只能把 P4 score blockers 从 7 个减少到 6 个，前提是独立 reviewer 确认本节点的 official-comment 缺口和 downstream mapping 边界没有被隐藏。

## 必答问题
comments 是否被完整保留：是，在当前可用输入范围内完整保留。每条 record 保留 source action ID、issue ID、exact source_comment_ids、severity、blocking status、affected location、evidence gap、target node、required change 和 downstream mapping target。Official comments 不存在，已单独标记为缺口。

多条评论是否需要拆分：需要按 actionable unit 拆分。P3_04 已把上游多位 reviewer 的意见压缩为 6 个 atomic actions；P4_01 保持这 6 个 action/comment records，不再把同一 action 内的 source_comment_ids 拆成重复 items，以免破坏 action-to-issue traceability。

editor comment 是否单独标识：没有 official editor comment。`P3_02:eic` 是 simulated editor-in-chief lens，不是 official editor decision comment；register 中用 `official_editor_comment: false` 和 `simulated_editor_lens_present: true` 区分。

## 下一步
- P4_02 使用 `artifacts/review_comment_register.yaml` 建立问题映射矩阵。
- P4_03 只对这些标准化 comments 草拟逐点回复，不伪造 official reviewer comments。
- P4_05 覆盖检查必须逐条覆盖 `p4-01-c001` 至 `p4-01-c006`。
- P4_06 修改证据必须为每条 comment 绑定实际 revision evidence 或 retained blocker。
