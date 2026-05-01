---
name: research_material_intake
description: Record user research materials into the right P0-P4 phase or explicit node, then return one bounded next action and recommended worker without forcing a fixed starting phase.
---

# Research Material Intake

## Role

Use this skill when the user wants to start or resume research from whatever material maturity they already have: a raw idea, data/code, experiment results, manuscript draft, review comments, or response materials.

This skill converts that material into node-local intake artifacts and a single next action.

## Inputs

- `entry_phase`: optional, one of `P0`, `P1`, `P2`, `P3`, `P4`.
- `target_node`: optional `research::` id or `research/` path. If present, route to that node.
- `material_summary`
- `available_assets`
- `desired_output`
- `constraints`
- `known_gaps`

At least one of `entry_phase` or `target_node` is required.

## Workflow

1. Resolve routing:
   - If `target_node` is present, infer phase from that node path and check any supplied `entry_phase` matches.
   - If only `entry_phase` is present, use that phase's default intake node.
2. Write node-local artifacts:
   - `artifacts/intake/material_<timestamp>.yaml`
   - `docs/intake_<timestamp>.md`
3. Record unmet explicit dependencies from the generated graph as advisory prerequisites.
4. Return:
   - selected `entry_phase`
   - selected `target_node`
   - artifact paths
   - recommended worker
   - one next action
   - unmet prerequisites

## Phase Defaults

- `P0`: formulate falsifiable problem, gap, boundary, and failure definition.
- `P1`: bind assets to experiment protocol, metrics, baselines, and minimum validation.
- `P2`: bind assets to manuscript claim-evidence structure and local writing task.
- `P3`: bind critique to review issues, revision map, and next review loop.
- `P4`: bind reviewer comments to response coverage, evidence, and point-to-point drafting.

## Boundaries

- Do not create a dedicated start UI.
- Do not force every user through P0.
- Do not generate a global project brief as a prerequisite.
- Do not mark upstream phases complete.
- Do not edit generated graph files directly.
- Do not bypass local acceptance checklists.
- Do not claim novelty, experiment validity, review pass, or submission readiness.
- Do not run experiments, write a full paper, or enter a multi-node orchestration loop.

## Stop With

- missing_entry_phase_or_target_node
- invalid_target_node
- phase_target_mismatch
- missing_required_intake_field
- material_intake_write_failed
- material_intake_refresh_failed
