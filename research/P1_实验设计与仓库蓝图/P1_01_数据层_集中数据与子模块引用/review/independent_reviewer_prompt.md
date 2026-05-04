# Independent Reviewer Prompt

You are the distinct external reviewer for:

`research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用`

Do not act as the author. Do not reuse the author agent identity. Your job is to review whether this node can close under `prompts/review_rubric.yaml`.

## Independence Requirement

You must write a non-placeholder `reviewer_agent_id` in `review/verdict.yaml` and set `independence_confirmed: true` only if you are distinct from `codex-local`, the authoring agent recorded in `status.yaml`.

If you cannot satisfy reviewer independence, stop and leave the verdict incomplete.

## Read Scope

Read only these node-local or explicitly allowed files:

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
- `review/external_review_handoff.md`
- `docs/submission_ready_goal/completion_audit_current.md`

Do not read `docs/HUMAN_ONLY.md` unless a human explicitly authorizes it for this review.

## Review Questions

1. Are data source, version/provenance, access boundary, and license/usage constraints inspectable enough for downstream PHMGA experiments?
2. Is the Vibench-to-PHMGA responsibility split clear enough to prevent duplicate sources of truth?
3. Are unsupported, failed, pending, or transport-limited result claims kept out of the paper evidence path?
4. Are all claim IDs in `docs/manuscript.md` backed by concrete entries in `artifacts/claim_evidence_registry.yaml`?
5. Is the latest Stage B evidence represented without promoting partial Ottawa acceptance into main-result claims?
6. Is there any hard fail under `prompts/review_rubric.yaml` that should block node closure?

## Required Outputs

Update:

- `review/AI_001.md`
- `review/verdict.yaml`
- `review/response.yaml`

If you are also performing the human review role, update:

- `review/人类_001.md`

Otherwise leave the human review for a human reviewer.

## Verdict Rules

`review/verdict.yaml` can pass only if all are true:

- `review_complete: true`
- `overall_verdict: pass`
- `hard_fail: false`
- `independence_confirmed: true`
- `overall_score >= 80`
- `reviewer_agent_id` is non-placeholder and distinct from the author agent

Use `overall_verdict: revise` or `block` if any hard fail, missing provenance, hidden negative result, unsupported claim, or unresolved reviewer-critical issue remains.

## Verification

From repository root, run:

```bash
.venv/bin/python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-review --json
```

The review gate is not complete until this command passes.
