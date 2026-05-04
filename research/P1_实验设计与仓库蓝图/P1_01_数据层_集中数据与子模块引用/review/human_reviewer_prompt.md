# Human Reviewer Prompt

You are the human reviewer for:

`research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用`

This review is required before the node can close. Review the node as a data/provenance/submodule package, not as a final paper result section.

## Read Scope

Read only these files unless you explicitly decide to inspect additional human-only context:

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
- `review/external_review_handoff.md`
- `review/independent_reviewer_prompt.md`
- `docs/submission_ready_goal/completion_audit_current.md`

`docs/HUMAN_ONLY.md` is protected by default. Read it only if you intentionally authorize it for this review.

## Human Review Questions

1. Is the data/source boundary clear enough for a downstream reader to understand where PHMGA evidence comes from?
2. Are PHM-Vibench and PHMGA responsibilities separated without creating a second source of truth?
3. Are the latest Stage B results represented honestly, especially the RM101 reject evidence and pending backend selection?
4. Are any positive result claims overstated relative to the available ledger and artifacts?
5. Is the independent AI review, once completed, credible and responsive to `prompts/review_rubric.yaml`?
6. Should the node enter fix/close, or must it revise before downstream graph progression?

## Required Output

Update:

- `review/人类_001.md`

If you also decide the final node verdict, ensure `review/verdict.yaml` remains consistent with the human review and independent AI review. Do not set a passing verdict unless the independent AI review is complete and reviewer independence is satisfied.

## Minimum Human Review Content

`review/人类_001.md` should include:

- reviewer identity or initials
- review date
- final human recommendation: `pass`, `revise`, or `block`
- comments mapped to concrete files or claim IDs
- any required fixes before node closure
- explicit note on whether positive result claims remain blocked

The file must not contain placeholder markers such as `TODO`, `TBD`, `<pending>`, or `待补充`.
