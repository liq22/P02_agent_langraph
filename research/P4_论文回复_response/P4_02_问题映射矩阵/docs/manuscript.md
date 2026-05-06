# P4_02 问题映射矩阵

## 目标
本节点把 P4_01 收集的标准化 comments 映射成下游可执行的问题矩阵。输入范围限定为当前可用的 simulated-review comments；official journal comments 仍缺失，不能伪造成已映射的 official response items。

## 输入
本节点本地输入为 `artifacts/review_comment_register.yaml`，它是 P4_01 `artifacts/review_comment_register.yaml` 的投影，保留 6 条 comment records、exact source_comment_ids、official-comment gap 和 split decision。

## 当前结论
`artifacts/question_mapping_matrix.yaml` 映射了全部 6 条 current-scope comments：

- `map-p4-001`: formal evidence eligibility, requires evidence generation or retained blocker.
- `map-p4-002`: reproducibility artifact state, requires reproducibility blocker resolution or retained limitation.
- `map-p4-003`: global validator/response coverage, requires coverage and validator closure or retained blocker.
- `map-p4-004`: claim-language density, requires manuscript wording revision with no claim upgrade.
- `map-p4-005`: figure/table reader path, requires figure/caption boundary check.
- `map-p4-006`: style repetition, optional cosmetic compression with no claim upgrade.

## Final-Threshold Score Boundary
本节点的 final-threshold re-review 只评价 P4_02 是否把 6 条 current-scope comments 准确映射成 response items、evidence items、coverage gates、problem classes、affected artifacts 和 downstream nodes。AI_002 若通过，只能清除 P4_02 的节点内 mapping score blocker；不得声称 official comments 已映射、P3_04 actions 已关闭、P1 checklist 已关闭、response package 已完成或全局 submission-ready validator 已通过。

AI_002 前的全局 gate 仍保留三类 validator blockers：109 个 P1_01-P1_05 checklist pending fields、6 个 P4 score blockers（P4_02-P4_07）和 6 个 P3_04 blocked/planned action statuses。`map-p4-003` 的 blocker 语义已同步为这些当前 gate classes；旧的 registry/failure-truth schema gaps 只属于历史已修复问题，不再作为当前 P4_02 evidence gap。

## 必答问题
每条意见真正指向什么问题：前三条指向 submission-blocking evidence/metadata/coverage blockers；后三条指向 manuscript wording, figure/caption boundary, and style polish follow-ups. Matrix rows preserve comment id, action id, issue id, problem class, evidence gap, affected artifact, target node, response item, evidence item, coverage gate, and status.

需要修改正文、图表还是只需解释：`map-p4-001` and `map-p4-002` require evidence generation or explicit retained limitation; `map-p4-003` requires response coverage and validator closure; `map-p4-004` requires P2 TeX wording change; `map-p4-005` requires figure/caption boundary verification; `map-p4-006` is optional style compression. None can be treated as explanation-only final closure until P4_05/P4_06 and final validation confirm coverage.

## 下一步
- P4_03 uses `response_item_id` to draft point-by-point responses.
- P4_05 uses `coverage_gate_id` and `comment_id` to verify complete coverage.
- P4_06 uses `evidence_item_id`, `target_node`, and `affected_location` to record actual revision evidence or retained blockers.
