---
name: external-node-reviewer
description: Independently review one selected node against its node-local `prompts/review_rubric.yaml` and write `review/AI_001.md` plus `review/verdict.yaml`. Use only from a reviewer agent or thread distinct from the authoring autoresearch agent.
---

# External Node Reviewer

## Use When

- A selected node requires external AI review before downstream handoff.
- The node already has `prompts/review_rubric.yaml`.
- This run is a distinct reviewer agent or thread, not the same agent that authored the node output.

## Required Inputs

1. `README.md`
2. `status.yaml`
3. `prompts/research_prompt.md`
4. `prompts/acceptance_checklist.yaml`
5. `prompts/review_rubric.yaml`
6. The node-local outputs and evidence files named in `required_reviewer_inputs`

## Workflow

1. Confirm reviewer independence before reading or scoring.
2. Read only the selected node's local assets and the evidence named by the rubric.
3. Score every rubric dimension from `0` to `5`, then convert to the weighted overall score.
4. Check citation verification status when claims rely on references; material unverified or mismatched citations are potential hard fails.
5. Check figure provenance when figures are present; missing source_kind/source_path/claim_ref/evidence_ref is a potential hard fail.
6. Check all hard-fail conditions before assigning a passing verdict.
7. Write the review narrative to `review/AI_001.md`.
8. Write the structured gate to `review/verdict.yaml`.
9. Return only the verdict, blocking issues, and required actions.

## Output Contract

- `review/AI_001.md`
- `review/verdict.yaml`

## Boundaries

- Do not edit node outputs, manuscript text, experiment artifacts, graph, or Canvas.
- Do not repair the node in the same review pass.
- Do not set `independence_confirmed: true` unless this run is a distinct reviewer agent or thread.
- Do not pass a node with an unresolved hard fail.
- Do not treat unverified citation-backed claims or provenance-free figures as reviewer-ready.
