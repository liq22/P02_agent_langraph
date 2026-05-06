# P4_03 逐点回复草稿

## 目标
本节点把 P4_02 的 six-row `question_mapping_matrix.yaml` 转成可审阅的逐点回复草稿。草稿只覆盖当前可用的 simulated-review comments；official journal decision letter、official editor comment 和 official reviewer comments 仍缺失，不能伪造成正式投稿回复。

## 输入边界
- Primary mapping input: `../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`.
- Manuscript location input: `../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex` and section files.
- Existing formal-response draft used only for consistency: `../P4_04_正式回复_tex_或_doc/artifacts/Reviewers/*.tex`.
- No new experiment, citation, figure, or TeX manuscript edit is claimed by this node.

## 当前结论
`artifacts/response_items.yaml` contains six point-by-point response items, one for each current-scope P4_01 comment:

- `rsp-p4-001`: formal evidence eligibility. Direct answer: agree; commitment remains blocked until accepted formal real-data/RM101/selected-backend/repeat/ablation evidence exists or the limitation is explicitly retained.
- `rsp-p4-002`: reproducibility artifact state. Direct answer: agree; commitment remains blocked until dirty-state disposition, adapter metadata-H5 alignment, selected-backend trace, and formal ledger/config provenance are closed or retained as named blockers.
- `rsp-p4-003`: global validator/response coverage. Direct answer: agree; final readiness is not claimed, and P4_05/P4_06 must prove or retain coverage for all action/comment IDs.
- `rsp-p4-004`: claim-language density. Direct answer: agree; planned wording change must compress the abstract/contribution framing without upgrading process claims into unsupported empirical claims.
- `rsp-p4-005`: figure/table reader path. Direct answer: agree; planned caption/callout check must keep synthetic/offline, single-run, no-real-data, no-RM101, and no-selected-backend boundaries visible.
- `rsp-p4-006`: style repetition. Direct answer: agree; optional cosmetic compression may shorten repeated draft-state phrasing only if limitation and negative-evidence language are preserved.

## Final-Threshold Score Boundary
本节点的 final-threshold re-review 只评价 P4_03 是否把 6 条 P4_02 mappings 转成可审阅、可覆盖检查、可交给 P4_06 的逐点回复草稿。AI_002 若通过，只能清除 P4_03 的节点内 response-draft score blocker；不得声称 official comments 已回复、TeX 修改已由本节点完成、coverage/revision evidence 已关闭、P3_04 actions 已关闭、P1 checklist 已关闭或全局 submission-ready validator 已通过。

AI_002 前的全局 gate 仍保留三类 validator blockers：109 个 P1_01-P1_05 checklist pending fields、5 个 P4 score blockers（P4_03-P4_07）和 6 个 P3_04 blocked/planned action statuses。`rsp-p4-003` 必须把 final-readiness response 写成当前 gate blockers，而不是旧的 registry/failure-truth schema gaps；这些旧 schema/failure-truth blockers 已经修复，只能保留为历史审计背景。

## 必答问题
回复是否逐点、编号、可追踪：是。Each item keeps `comment_id`, `response_item_id`, `mapping_id`, `source_action_id`, `issue_id`, exact `source_comment_ids`, evidence references, manuscript location, commitment status, and downstream gate.

是否在必要时礼貌反驳并给出根据：当前 six items do not require adversarial rebuttal. The draft agrees with the concerns and narrows commitments instead of over-answering. The closest argumentative boundary is that P4_03 can answer and route each concern, but it does not claim that evidence generation, manuscript editing, coverage closure, or final submission readiness has already happened.

## 下一步
- P4_05 should use `coverage_gate_id` and `comment_id` to check whether every response item is covered.
- P4_06 should use `evidence_item_id`, `location`, and `commitment_status` to record actual revision evidence or retained blockers.
- P4_07 must not package a resubmission until official comments, coverage, revision evidence, final validation, and score thresholds are resolved or explicitly retained by policy.
