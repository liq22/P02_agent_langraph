# P1_02 Human Reviewer Prompt

You are the human-review-slot reviewer for:

`research::P1_实验设计与仓库蓝图::P1_02_伪代码`

This review can be performed by a human or, if the user explicitly authorizes external Claude Code data sharing for P1_02, by a transparent Claude Code teammate delegate. Do not claim to be a biological human if you are a teammate delegate.

## Read Scope

Read only:

- `README.md`
- `status.yaml`
- `skills/local_entry.md`
- `prompts/research_prompt.md`
- `prompts/acceptance_checklist.yaml`
- `prompts/review_rubric.yaml`
- `docs/manuscript.md`
- `artifacts/interface_contract.yaml`
- `review/AI_001.md`
- `review/verdict.yaml`

Do not read `docs/HUMAN_ONLY.md` unless the user explicitly authorizes it for this review.

## Review Questions

1. Are P1_02 inputs, outputs, and state transitions clear enough for downstream implementation?
2. Does the pseudocode separate necessary protocol steps from implementation details?
3. Does `artifacts/interface_contract.yaml` preserve the P1_01 data/provenance boundary and prevent duplicate result truth?
4. Are at least two failure modes or exception branches explicit and actionable?
5. Does the pseudocode avoid promoting Stage B partial evidence into Stage C/D positive paper claims?
6. Is the independent AI review, once completed, credible and responsive to `prompts/review_rubric.yaml`?

## Required Output

Update:

- `review/人类_001.md`

If this is a Claude Code teammate delegate review, also write:

- `docs/submission_ready_goal/runtime_logs/claude_code/p1_02_human_review_handoff.yaml`

Do not edit `review/verdict.yaml`, `review/AI_001.md`, `review/response.yaml`, `docs/manuscript.md`, `artifacts/interface_contract.yaml`, graph files, or PHMGA files.

## Minimum Review Content

`review/人类_001.md` must include:

- reviewer identity or delegate identity
- review date
- final recommendation: `pass`, `revise`, or `block`
- comments mapped to concrete files or interface names
- required fixes before node closure, if any
- explicit note on whether positive result claims remain blocked

No placeholder markers such as `TODO`, `TBD`, `<pending>`, `待补充`, or `占位` may remain.
