# P4_05 覆盖检查

## 目标
本节点检查 P4_02 mapping 和 P4_03 point-by-point response draft 是否逐条覆盖当前可用的 simulated-review comments。覆盖检查不等于修订证据闭合，也不等于 final submission readiness。

## 输入边界
- Mapping input: `../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`.
- Response input: `../P4_03_逐点回复草稿_md/artifacts/response_items.yaml` and `../P4_03_逐点回复草稿_md/docs/manuscript.md`.
- Official journal decision letter, official editor comment, and official reviewer comments remain absent.
- No new experiment, citation, figure edit, TeX edit, revision diff, or final submission readiness is claimed by this node.

## Final-Threshold Score Boundary
`artifacts/coverage_final_threshold_contract.yaml` limits the AI_002 re-review to P4_05 node-local response coverage. A passing score can only clear the P4_05 below-90 review-score blocker. It does not close revision evidence, official comments, P1 checklist fields, P3_04 action statuses, P4_06/P4_07 package blockers, or the global final submission validator.

Current gate facts before the P4_05 AI_002 score-only re-review are: 109 P1_01-P1_05 checklist fields remain pending, P4_05/P4_06/P4_07 remain below 90, and P3_04 actions 1-3 are blocked while actions 4-6 are planned.

## 当前结论
`artifacts/coverage_check_report.yaml` verifies that all six mapped comments are covered by corresponding response items:

- `p4-01-c001` / `issue-p3-001` / `rsp-p4-001`: coverage checked and covered at response level; commitment remains blocked for formal empirical evidence.
- `p4-01-c002` / `issue-p3-002` / `rsp-p4-002`: coverage checked and covered at response level; commitment remains blocked for reproducibility artifact state.
- `p4-01-c003` / `issue-p3-003` / `rsp-p4-003`: coverage checked and covered at response level; commitment remains blocked for global validator and coverage closure.
- `p4-01-c004` / `issue-p3-004` / `rsp-p4-004`: coverage checked and covered at response level; commitment remains planned wording revision.
- `p4-01-c005` / `issue-p3-005` / `rsp-p4-005`: coverage checked and covered at response level; commitment remains planned figure/caption boundary check.
- `p4-01-c006` / `issue-p3-006` / `rsp-p4-006`: coverage checked and covered at response level; commitment remains optional style compression.

## 必答问题
有没有 comment 被漏答：没有。All six `comment_id` and `issue_id` entries from P4_02 appear in `artifacts/coverage_check_report.yaml`, and each has a matching `response_item_id`.

有没有承诺修改但正文没改：有三类 downstream commitments are not yet completed: formal evidence/reproducibility/global validation blockers (`rsp-p4-001` through `rsp-p4-003`) and planned manuscript/figure/style work (`rsp-p4-004` through `rsp-p4-006`). The report marks coverage as covered but keeps `commitment_closure_status` as `blocked` or `planned`, so no completed edit is claimed.

有没有证据链断裂：response-level evidence refs exist for all six rows, but revision evidence remains a downstream P4_06 responsibility. `artifacts/revision_evidence_map.yaml` records that each response item still requires P4_06 closure before packaging.

## 下一步
- P4_06 must turn the `revision_evidence_item_id` entries into verified revision evidence or explicit retained blockers.
- P4_07 must not package a resubmission until official comments, coverage, revision evidence, final validation, and score thresholds are resolved or explicitly retained by policy.
