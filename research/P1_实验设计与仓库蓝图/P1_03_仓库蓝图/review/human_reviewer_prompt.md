# P1_03 Human Reviewer Prompt

You are the human-review-slot reviewer for:

`research::P1_实验设计与仓库蓝图::P1_03_仓库蓝图`

This review can be performed by a human or, if the user explicitly authorizes external Claude Code data sharing for P1_03, by a transparent Claude Code teammate delegate. Do not claim to be a biological human if you are a teammate delegate.

## Read Scope

Read only:

- `README.md`
- `status.yaml`
- `skills/local_entry.md`
- `prompts/research_prompt.md`
- `prompts/acceptance_checklist.yaml`
- `prompts/review_rubric.yaml`
- `docs/manuscript.md`
- `artifacts/repo_blueprint.yaml`
- `artifacts/module_map.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/failure_register.yaml`
- `artifacts/negative_result_note.md`
- `artifacts/keep_discard_ledger.yaml`
- `review/AI_001.md`
- `review/verdict.yaml`

Do not read `docs/HUMAN_ONLY.md` unless the user explicitly authorizes it for this review.

## Review Questions

1. Are required modules and deferred modules clearly separated?
2. Is the directory and responsibility boundary minimal, reproducible, and free of duplicate result truth?
3. Are scripts, configs, logs, artifacts, and ledger paths clear enough for downstream implementation?
4. Does the blueprint preserve the P1_01 data boundary and P1_02 pseudocode/interface contract?
5. Are failure modes and negative/reject evidence explicit, including RM101 and selected-backend blockers?
6. Is the independent AI review, once completed, credible and responsive to `prompts/review_rubric.yaml`?

## Required Output

Update:

- `review/人类_001.md`

If this is a Claude Code teammate delegate review, also write:

- `docs/submission_ready_goal/runtime_logs/claude_code/p1_03_human_review_handoff.yaml`

Do not edit `review/verdict.yaml`, `review/AI_001.md`, `review/response.yaml`, `docs/manuscript.md`, artifacts, graph files, PHMGA files, Canvas files, or dashboard files.

## Minimum Review Content

`review/人类_001.md` must include:

- reviewer identity or delegate identity
- review date
- final recommendation: `pass`, `revise`, or `block`
- comments mapped to concrete files or artifact sections
- required fixes before node closure, if any
- explicit note on whether positive result claims remain blocked

No placeholder markers such as `TODO`, `TBD`, `<pending>`, `待补充`, or `占位` may remain.
