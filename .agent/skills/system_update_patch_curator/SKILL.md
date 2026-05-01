---
name: system_update_patch_curator
description: Curate future AutoResearch system update patch queues from completed topic or node retrospectives. Use after a research topic, phase, or selected nodes have produced enough usage evidence and the user wants system-improvement patches proposed, not applied.
---

# System Update Patch Curator

## Role

Use this skill after a research topic, phase, or selected nodes have been used enough to expose improvement opportunities in the AutoResearch system itself.

It reads bounded retrospective evidence and writes a reviewable patch queue. It does not apply patches.

## Inputs

At least one bounded source is required:

- selected node id or `research/` path
- a phase scope such as `P0`, `P1`, `P2`, `P3`, or `P4`
- a completed topic workset declared by the user
- an explicit retrospective note from the user

Preferred node-local evidence:

- `status.yaml`
- `docs/`
- `artifacts/`
- `logs/`
- `review/`
- `prompts/acceptance_checklist.yaml`
- `skills/local_entry.md`

Read only the declared source scope. Do not scan the whole repository unless the user explicitly asks for a repo-wide system update queue.

## Workflow

1. Freeze the source scope and list the exact nodes or files inspected.
2. Extract repeated friction, routing failures, unclear prompts, missing checks, stale docs, unsafe defaults, or validation gaps.
3. Separate research-content issues from system-improvement issues.
4. For each system-improvement issue, create one patch queue item with evidence paths and a bounded target surface.
5. Classify risk:
   - `low`: docs, skill wording, prompt clarification, narrow validation fixture.
   - `medium`: local entry routing, acceptance checklist semantics, gateway or CLI behavior.
   - `high`: scheduler behavior, graph relations, experiment evidence rules, review gates, submission gates.
6. Classify apply mode:
   - `optimizer_candidate`: low-risk maintenance item suitable for later `autoresearch-system-optimizer` review.
   - `manual_only`: any item touching research gates, scheduler relations, generated outputs, manuscripts, results, verdicts, or broad architecture.
7. Write the patch queue artifacts and report the paths.

## Output Contract

Write both files under `artifacts/system_update_queue/`:

- `<timestamp>.yaml`
- `<timestamp>.md`

Each queue item must include:

- `id`
- `source_node`
- `observed_problem`
- `evidence_paths`
- `proposed_change`
- `target_files`
- `risk_level`: `low`, `medium`, or `high`
- `apply_mode`: `manual_only` or `optimizer_candidate`
- `validation_commands`
- `do_not_change`

The Markdown file should group items by risk and briefly explain why the queue is safe to review.

## Boundaries

- Do not apply patches.
- Do not edit system files directly.
- Do not modify manuscripts, experiment results, review verdicts, response evidence, generated graph files, Canvas files, or dashboard output.
- Do not turn a single topic preference into a global rule unless the evidence shows a repeated system-level failure.
- Do not claim that a queue item is safe to apply; only classify it as a candidate for review.
- Do not replace `autoresearch-system-optimizer`. This skill curates candidates; the optimizer validates and may apply low-risk maintenance fixes later.

## Stop With

- missing_source_scope
- source_scope_too_broad
- no_system_update_candidates
- evidence_paths_missing
- output_queue_write_failed
