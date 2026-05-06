# Current Blocker Resolution Plan

- objective: finish the `p02_submission_ready_goal_package` path until the repository can truthfully pass the final submission gate.
- generated_at: 2026-05-06
- source_gate: `python3 scripts/validate_research_truth.py --require-submission`
- current_result: pass
- guardrail: this plan records how blockers were closed; it does not raise scores, read `.env`, run external provider calls, or convert retained limitations into positive empirical evidence.

## Current Gate Facts

`python3 scripts/validate_graph.py` passes.

`backend/graph/graph_status.json` reports:

- `refresh_ok: true`
- `ready_nodes: []`
- `blocked_nodes: []`
- `next_node: null`
- `unfinished_count: 0`

`python3 scripts/validate_research_truth.py --require-submission` passes in submission-ready mode after user-authorized P3_04 action closure:

1. P1_01-P1_05 checklist blocker count: 0.
2. Below-threshold score blocker count: 0.
3. P3_04 blocked/planned action count: 0.

## Cleared Class: P1 Checklist Statuses

The validator no longer reports incomplete P1_01-P1_05 checklist fields after the canonical node acceptance checklist statuses were synchronized to `complete`.

Detailed evidence matrix: `docs/submission_ready_goal/p1_checklist_closure_evidence_matrix_current.md`.

| Node | Former Pending Fields | Current Status |
| --- | ---: | --- |
| P1_01 数据层_集中数据与子模块引用 | 23 | checklist complete |
| P1_02 伪代码 | 18 | checklist complete |
| P1_03 仓库蓝图 | 22 | checklist complete |
| P1_04 核心想法轻量验证 | 25 | checklist complete |
| P1_05 初步验证结果整理 | 21 | checklist complete |

Local audit status from the independent reviewer pass: these items are closed only within their node-local evidence boundaries, with P1_04 limited to synthetic/offline handoff evidence and P1_05 limited to preliminary synthetic-signal evidence. This does not close P3_04 actions, formal evidence, selected-backend, PHMGA adapter, official-comment, or external-submission gates.

Remaining required approval text:

```text
批准关闭 P3_04 revision_action_map.yaml 的 6 个 actions：action-p3-001 至 action-p3-006 均按 P4_05/P4_06 已覆盖或保留限制的证据标为 done，并允许继续冲刺最终 submission-ready validator。
```

## Cleared Class: Review Scores Below 90

There are 0 leaf verdicts below the final threshold after P2_01 through P2_05, P0_01 through P0_05, all current P1 score-remediation nodes, P3_01-P3_04, and P4_01-P4_07 were locally remediated and independently re-reviewed above the final threshold. P0, P1, P2, P3, and P4_01-P4_07 are now above 90. This clears the score class only; it does not close checklist/action/formal-evidence validators.

Detailed remediation matrix: `docs/submission_ready_goal/review_score_remediation_matrix_current.md`.

| Node Group | Low-Score Verdicts |
| --- | ---: |
| P0 | 0 |
| P1 | 0 |
| P2 | 0 |
| P3 | 0 |
| P4 | 0 |

The score gate cannot be truthfully cleared by editing numbers alone. It requires either stronger evidence and re-review, or a deliberate policy change to the final threshold/definition. The current repository policy says final submission requires the configured threshold, default 90.

Future score-regression path:

1. Run or record formal evidence needed to remove retained limitations if a later reviewer lowers a score.
2. Re-run distinct external reviews against the updated evidence.
3. Only then update verdicts if reviewers actually raise scores.

## Cleared Class: P3_04 Revision Actions

`research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/revision_action_map.yaml` formerly had six actions blocking the final validator. After explicit approval, all six are `done` with closure evidence:

| Action | Current Status | Severity | Closure Basis |
| --- | --- | --- | --- |
| action-p3-001 | done | fatal | P4_05/P4_06 retained formal-evidence limitation accepted as action closure |
| action-p3-002 | done | fatal | P4_05/P4_06 retained reproducibility limitation accepted as action closure |
| action-p3-003 | done | major | P1 checklist, score, coverage, and P4 evidence mapping closure |
| action-p3-004 | done | major | wording revision without claim upgrade applied |
| action-p3-005 | done | minor | figure/caption boundary check verified |
| action-p3-006 | done | minor | optional style compression applied |

P4_05/P4_06 cover or preserve these actions as response/revision evidence. The reconciliation note is `docs/submission_ready_goal/p3_p4_action_reconciliation_current.md`.

- action-p3-004 and action-p3-006 are recorded by P4_06 as downstream TeX wording revisions already applied.
- action-p3-005 is recorded by P4_06 as a downstream figure-caption boundary check already verified.
- action-p3-001 through action-p3-003 remain retained formal/reproducibility/final-readiness limitations rather than resolved formal evidence.

The final validator reads the canonical P3_04 statuses. After user-approved semantic closure, it passes in submission-ready mode.

## External Formal Evidence Path

The PHMGA RM101 OpenRouter preflight has passed locally, and the offline execute-agent side-output crash was fixed with unit test coverage in the PHMGA submodule. Real provider formal runs have not been executed because they would send real-data-derived workflow context to OpenRouter/BIGMODEL.

Detailed execution and approval packet: `docs/submission_ready_goal/formal_provider_run_approval_packet_current.md`.

Required approval text:

```text
批准将 RM101/Ottawa formal provider runs 的真实数据派生 workflow context 发送给 OpenRouter/BIGMODEL 服务，仅使用免费模型策略。
```

After approval, the run policy remains:

- OpenRouter: free models only.
- BIGMODEL: GLM-4.7-flash free model only.
- Do not print API keys.
- Do not read `.env` content unless a command must source it without exposing values.

## Current Post-Closure State

1. `python3 scripts/validate_graph.py` passes.
2. `python3 scripts/validate_research_truth.py --require-submission` passes.
3. `git diff --check` passes.
4. Future formal provider rows should run only after exact external-disclosure approval and must not overwrite the retained-limitation boundary unless they produce accepted evidence.
