# P1_05 Human Reviewer Prompt

You are the human-review-slot reviewer for:

`research::P1_实验设计与仓库蓝图::P1_05_初步验证结果整理`

This review can be performed by a human or, if the user explicitly authorizes external Claude Code data sharing for P1_05, by a transparent Claude Code teammate delegate. Do not claim to be a biological human if you are a teammate delegate.

## Read Scope

Read only:

- `README.md`
- `status.yaml`
- `skills/local_entry.md`
- `prompts/research_prompt.md`
- `prompts/acceptance_checklist.yaml`
- `prompts/review_rubric.yaml`
- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`
- `docs/manuscript.md`
- `artifacts/result_registry.yaml`
- `artifacts/hypothesis_status.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/paper_ready_result_summary.md`
- `artifacts/gate_report.md`
- `review/AI_001.md`
- `review/verdict.yaml`

Do not read `docs/HUMAN_ONLY.md` unless the user explicitly authorizes it for this review.

## Review Questions

1. Does every positive conclusion map to the P1_04 source ledger?
2. Are supported, unsupported, and unclear evidence states separated without overclaiming?
3. Is `paper_ready_result_summary.md` safe for preliminary/synthetic sanity-check wording only?
4. Are real-data generalization, RM101 resolution, selected-backend readiness, and formal Stage C/D claims explicitly unsupported?
5. Are variance stability and perfect synthetic accuracy interpretation left as unclear limitations?
6. Is the independent AI review credible and responsive to `prompts/review_rubric.yaml`?

## Required Output

Update:

- `review/人类_001.md`

If this is a Claude Code teammate delegate review, also write:

- `docs/submission_ready_goal/runtime_logs/claude_code/p1_05_human_review_handoff.yaml`

Do not edit `review/verdict.yaml`, `review/AI_001.md`, `review/response.yaml`, `status.yaml`, `docs/manuscript.md`, artifacts, graph files, PHMGA files, Canvas files, or dashboard files.

## Minimum Review Content

`review/人类_001.md` must include:

- reviewer identity or delegate identity
- review date
- final recommendation: `pass`, `revise`, or `block`
- comments mapped to concrete files or artifact sections
- required fixes before node closure, if any
- explicit note on whether positive result claims remain blocked

No placeholder markers such as `TODO`, `TBD`, `<pending>`, `待补充`, or `占位` may remain.
