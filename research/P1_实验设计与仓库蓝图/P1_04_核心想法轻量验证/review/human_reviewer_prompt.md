# P1_04 Human Reviewer Prompt

You are the human-review-slot reviewer for:

`research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证`

This review can be performed by a human or, if the user explicitly authorizes external Claude Code data sharing for P1_04, by a transparent Claude Code teammate delegate. Do not claim to be a biological human if you are a teammate delegate.

## Read Scope

Read only:

- `README.md`
- `status.yaml`
- `skills/local_entry.md`
- `prompts/research_prompt.md`
- `prompts/acceptance_checklist.yaml`
- `prompts/review_rubric.yaml`
- `artifacts/execution_contract.yaml`
- `artifacts/experiment_matrix.yaml`
- `docs/manuscript.md`
- `artifacts/gate_report.md`
- `artifacts/auto_experiment/results.tsv`
- `logs/auto_experiment/latest_run.log`
- `review/AI_001.md`
- `review/verdict.yaml`

You may also read the two run metrics files if needed:

- `artifacts/auto_experiment/runs/baseline_simple/metrics.json`
- `artifacts/auto_experiment/runs/attempt_supervisor_proving/metrics.json`

Do not read `docs/HUMAN_ONLY.md` unless the user explicitly authorizes it for this review.

## Review Questions

1. Is the execution contract genuinely executable and bounded to PHMGA offline synthetic validation?
2. Are baseline, primary metric, single changed factor, and keep/discard rule clear and applied consistently?
3. Does `results.tsv` match the two run `metrics.json` files?
4. Does `latest_run.log` contain enough replay information for P1_04/P1_05 handoff?
5. Does the package avoid promoting synthetic/offline evidence into Stage C/D, selected-backend, RM101-resolution, or submission-ready claims?
6. Is the independent AI review credible and responsive to `prompts/review_rubric.yaml`?

## Required Output

Update:

- `review/人类_001.md`

If this is a Claude Code teammate delegate review, also write:

- `docs/submission_ready_goal/runtime_logs/claude_code/p1_04_human_review_handoff.yaml`

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
