# P1_01 External Review Handoff

- node: `research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用`
- prepared_by: `codex-local`
- prepared_at: 2026-05-04
- purpose: provide a bounded input packet for a distinct external reviewer.

This file is not a review verdict. It exists only to make the required independent review lane executable.

## Reviewer Independence Gate

The reviewer must be distinct from the authoring agent and must write the actual verdict to:

- `review/verdict.yaml`

The node cannot close unless that verdict has:

- `review_complete: true`
- `overall_verdict: pass`
- `hard_fail: false`
- `independence_confirmed: true`

Current verdict state is incomplete, so the node is not downstream-ready.

## Required Inputs

Read only the node-local and explicitly allowed files below:

- `README.md`
- `status.yaml`
- `prompts/research_prompt.md`
- `prompts/acceptance_checklist.yaml`
- `prompts/review_rubric.yaml`
- `docs/manuscript.md`
- `artifacts/data_lineage.yaml`
- `artifacts/submodule_ref.yaml`
- `artifacts/vibench_data_factory_binding.yaml`
- `artifacts/data_reading_boundary.yaml`
- `artifacts/phmga_data_protocol_handoff.yaml`
- `artifacts/result_source_map.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/failure_register.yaml`
- `artifacts/negative_result_note.md`
- `artifacts/keep_discard_ledger.yaml`
- `logs/codex_run_001.md`
- `review/independent_reviewer_prompt.md`
- `review/human_reviewer_prompt.md`
- `docs/submission_ready_goal/completion_audit_current.md`

Do not read `docs/HUMAN_ONLY.md` unless the human reviewer explicitly authorizes it for this review.

## Evidence Snapshot

Supported local claims:

- `C-P02-DATA-001`: PHM-Vibench `data_factory` is the read-only data interface.
- `C-P02-DATA-002`: PHMGA owns downstream protocol, splits/windows, DAG workflow, bridge, evaluation, ledger, and reports after reading.
- `C-P02-SUBMODULE-001`: PHMGA is the P02 implementation submodule on branch `journal_thesis`.
- `C-P02-DATA-003`: first-round formal data scope is `metadata.xlsx`, `RM_017_Ottawa19.h5`, and `RM_101_THU_GEARBOX.h5` under external `DATA_ROOT`.
- `C-P02-RESULT-001`: positive PHMGA main-result claims remain blocked until the selected backend is locked and Stage C/D main or ablation rows pass with ledger and artifact traces.

Recent PHMGA Stage B evidence to inspect:

- `ottawa_ml_openrouter_nemotron_v3`: accept evidence at `artifacts/paper/ottawa_ml_openrouter_nemotron_v3_qualityfix1`; artifact contract and feature separability passed; test macro-F1 `0.8774661249538376`.
- `ottawa_ml_bigmodel_glm47_v1`: accept evidence at `artifacts/paper/ottawa_ml_bigmodel_glm47_v1_qualityfix2`; artifact contract and feature separability passed; test macro-F1 `0.7226535613558728`.
- `rm101_ml_openrouter_nemotron_v3`: reject-evidence bundle at `artifacts/paper/rm101_ml_openrouter_nemotron_v3_qualityfix1`; artifact and feature gates passed, but `workflow_exit.compiled_for_rejection_evidence=true` after `need_replan`; test macro-F1 `0.18337824193501234`.
- `rm101_ml_bigmodel_glm47_v1`: reject-evidence bundle at `artifacts/paper/rm101_ml_bigmodel_glm47_v1_qualityfix7`; artifact and feature gates passed, but `workflow_exit.compiled_for_rejection_evidence=true` after `need_patch`; test macro-F1 `0.18934628733653974`.
- `selected_global_best_backend` remains pending in `doc/experiments/01_result_ledger.md`, so these Stage B rows must not be promoted into Stage C/D main-table claims.

Open failures that must remain visible:

- `F-P02-RESULT-001`: PHMGA selected-backend and main/ablation rows are not locked or passed, so positive paper result claims are blocked even though partial Stage B comparison evidence exists.
- `F-P02-RESULT-002`: RM101 Stage B free-model rows currently remain reject evidence and block backend selection.
- `F-P02-REVIEW-001`: independent external reviewer verdict is not yet passed.

## Reviewer Questions

1. Are data source, version/provenance, access boundary, and license/usage constraints inspectable enough for downstream PHMGA experiments?
2. Is the Vibench-to-PHMGA responsibility split clear enough to prevent duplicate sources of truth?
3. Are unsupported, failed, pending, or transport-limited result claims kept out of the paper evidence path?
4. Are all claim IDs in `docs/manuscript.md` backed by concrete entries in `artifacts/claim_evidence_registry.yaml`?
5. Is there any hard fail under `prompts/review_rubric.yaml` that should block node closure?

## Expected Review Outputs

Update these files as the independent reviewer:

- `review/AI_001.md`
- `review/verdict.yaml`
- `review/response.yaml`

If human review is performed separately, update:

- `review/人类_001.md`

Use `review/human_reviewer_prompt.md` for the human-review-specific scope and required content.

## Verification Commands

From the repository root:

```bash
.venv/bin/python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs --json
.venv/bin/python tools/submission_ready_goal/validate_goal_fsm_state.py --state docs/submission_ready_goal/fsm/current_goal_state.yaml
.venv/bin/python scripts/refresh_views.py --mode graph_only
```
