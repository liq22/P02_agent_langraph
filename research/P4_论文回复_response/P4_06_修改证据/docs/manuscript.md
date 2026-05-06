# P4_06 修改证据

## 目标

本节点把 P4_05 handoff 中的六条 revision evidence item 压缩成可审查的证据映射。目标不是宣布 submission-ready，而是让每条 P4_03 response 的承诺都有一个明确的证据位置、正文/图表位置和状态。

## 当前结论

`artifacts/revision_evidence_map.yaml` contains six rows:

- `ev-p4-001`: formal empirical evidence gap is verified as a retained limitation. The TeX results section already labels the current signal as synthetic/offline, single-run, no real-data row, no RM101 resolution, no selected-backend decision, and no Stage C/D success.
- `ev-p4-002`: reproducibility artifact state is verified as a retained limitation. P1_06 records the PHMGA branch/head/pull state and also records 66 dirty/untracked submodule entries as a blocker before any parent pointer update or submission-level reproducibility claim.
- `ev-p4-003`: final readiness is verified as not closed. The completion audit remains the evidence location for global validator, P1 checklist, P4 score-threshold, P3 action-status, selected-backend, and downstream packaging blockers.
- `ev-p4-004`: abstract wording was revised in `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex` to state a narrower process claim and remove broad operating-system framing.
- `ev-p4-005`: the figure/caption path was checked and retained without a TeX diff because the current caption already carries claim/evidence refs, provenance, no-variance, no-real-data, no-RM101, and no-selected-backend boundaries.
- `ev-p4-006`: discussion/result wording was revised in `main.tex` and `sections/experiment.tex` to keep negative and uncertain evidence in the manuscript record without upgrading it into stronger claims.

## Final-Threshold Score Boundary

`artifacts/revision_evidence_final_threshold_contract.yaml` limits the AI_002 re-review to P4_06 node-local revision-evidence mapping. A passing score can only clear the P4_06 below-90 review-score blocker. It does not close accepted formal real-data/RM101 evidence, selected backend, PHMGA dirty-state or adapter alignment, official comments, canonical P3_04 action statuses, P4_07 package readiness, or the global final submission validator.

Current gate facts after P1 checklist synchronization, the P4_06/P4_07 AI_002 score-only re-reviews, and user-authorized P3_04 semantic action closure are: P1 checklist blocker count is 0, below-threshold score count is 0, P3_04 blocked/planned action count is 0, and `scripts/validate_research_truth.py --require-submission` passes in submission-ready mode.

## 边界

P4_06 closes the revision-evidence mapping gate for current-scope simulated review comments. It does not turn retained formal-result, selected-backend, PHMGA dirty-state, or official-comment limitations into positive evidence. After explicit user approval, the canonical P3_04 action statuses are closed as retained-limit/action-coverage closures, and the final submission validator passes.

## 下一步

P4_07 may consume this map as a packaging input, but it must preserve the retained blockers and cannot claim resubmission readiness until final validation policy permits it.
