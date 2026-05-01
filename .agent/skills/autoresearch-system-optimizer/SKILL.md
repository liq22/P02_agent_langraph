---
name: autoresearch-system-optimizer
description: Run a limited optimization loop for the AutoResearch system itself. Use when the goal is to harden prompts, skills, validation configs, runners, and node-local prompt/skill files; route through `$graph-driven-research-orchestrator` once when no explicit target is provided; then evaluate, score, triage fixes, apply only low-risk maintenance patches, and re-evaluate.
---

# AutoResearch System Optimizer

## Plain-language role

Use this skill to improve the research system itself.

It checks prompts, skills, validation rules, and helper scripts. It may apply low-risk maintenance fixes, but it does not change research results, manuscript text, graph files, review verdicts, or experiment evidence.

It separates maintenance fixes from research-quality judgments.
It defaults to an advisory-only, single-target cycle unless low-risk apply is explicitly enabled.

## Use When

- The user wants to improve the AutoResearch system itself rather than advance one manuscript or experiment node.
- The task is a limited improvement loop over prompts, skills, validators, runners, or node-local prompt/skill files.
- The likely edit set is prompts, skills, validation configs, helper scripts, or node-local prompt/skill files.
- No explicit target node is given and one graph-aware routing round is needed before validation.

## Source Files

This skill is self-contained.

Load operating instructions from:

1. `references/node_validation.md`
2. `references/system_optimizer_cycle.md`
3. `config/validation_rules.yaml`
4. `config/optimization_loop.yaml`
5. `config/score_matrix.yaml`
6. `config/score_policy.yaml`
7. `config/scorecard.template.yaml`
8. `config/immutable_core_rules.yaml`
9. `config/research_gate_rules.yaml`
10. `config/agents.yaml`
11. `scripts/batch_node_validation.py`
12. `scripts/summarize_validation_results.py`
13. `scripts/score_and_plan_actions.py`
14. `scripts/apply_low_risk_actions.py`
15. `scripts/run_optimization_cycle.py`
16. `scripts/run_node_campaign.py`

`_reference/test/` is a validation fixture area for this skill, not the source for its prompts, configs, or helper scripts.

## Validation Layer Contract

Use the existing validation layers; do not create a second red-team truth source.

- `_reference/test/v2/`
  - optimizer acceptance fixtures, deterministic single-node metric fixtures, and score/action planner checks
  - use this layer to verify scoring, exploratory gates, optimizer cycle outputs, and compact EBR/HIR/CCS/PBC fixtures
- `_reference/test/redteam/`
  - deterministic node-level adversarial validation layer
  - use this layer to test whether selected high-risk nodes stop on missing contracts, contradictory results, fake evidence, unfalsifiable problems, or uncovered review responses
  - write cycle-specific reports under the current cycle directory, not the shared `reports/latest` path

Do not migrate these layers into a new `tests/autoresearch/` tree unless the repo first declares a single replacement truth source.

## Dual-Track Contract

This optimizer keeps automatic scoring, but splits it into two tracks.

- `maintenance_score`
  - drives `score -> plan -> low-risk apply -> recheck`
  - only this track may produce `auto_apply`
- `research_rigor_score`
  - scores research-facing rigor by phase, mode, and node profile
  - may rank urgency and emit human gate tickets
  - never drives auto-apply directly

Do not collapse these tracks into one blended score.

## Node-Aware Scoring Contract

Every evaluated target must be scored against the repo's declared dimensions:

- `phase`: `P0`, `P1`, `P2`, `P3`, `P4`
- `node_mode`: `parent`, `lite`, `standard`, `execution`
- `node_profile`: `routing_parent`, `lite_research_leaf`, `evidence_leaf`, `hard_gate`
- `execution_profile`: `experiment_execution`, `result_synthesis` when applicable

The score matrix must vary by these dimensions. Do not reuse one flat rubric for every node.

## Score Stability Contract

Each node score must be stable for the same frozen target boundary, repo evidence, score matrix, and structured `score_inputs[]`.

- Score changes must cite an explicit evidence delta.
- If two evaluations of the same node disagree without a concrete evidence delta, downgrade the result to `manual_ticket` or a human gate.
- Unstable node scoring may remove `auto_apply` eligibility; it must never create patch authority.
- Scorecards should record `score_stability.status`, `prior_score_ref`, `evidence_delta`, and `variance_reason` when comparison evidence exists.

Optional `score_inputs[]` fields may be used to explain stability and risk:

- `evidence_strength`
- `recheckability`
- `blast_radius`
- `score_stability_note`
- `delta_reason`

## Cycle Contract

Run one limited cycle with these stages in order.

1. `preflight`
   - load source files used by this skill
   - run declared preflight checks
   - fail fast on missing config, invalid prompt files, or broken helper scripts
2. `target_freeze`
   - freeze exactly one optimization target, success boundary, write surface, and cycle budget before patching
   - if no explicit target exists, do one graph-guided routing round and freeze the result
3. `prompt_hardening`
   - compare `references/node_validation.md` against `config/validation_rules.yaml`
   - allow at most two low-risk tightening passes
4. `evaluate`
   - run hostile validation on the frozen target
   - require concrete evidence, blockers, `UNVERIFIED` handling, and structured score inputs
5. `finding_normalization`
   - deduplicate evaluator findings into root-cause rows
   - preserve evidence path, severity, confidence, and fix surface
6. `score`
   - compute `maintenance_score` and `research_rigor_score` from structured `score_inputs[]`
   - select dimensions from `config/score_matrix.yaml`
7. `rank_actions`
   - rank candidate actions by severity, confidence, blast radius, and recheckability
   - only maintenance-track findings may become `auto_apply` candidates
8. `triage`
   - classify every candidate as exactly one of `auto_apply`, `manual_ticket`, `defer`, or `no_change`
   - freeze the patch set before editing
9. `apply_low_risk_fixes`
   - apply only maintenance-track, low-risk, reversible actions inside the allowed path set
10. `recheck`
   - re-run the narrowest declared checks first
   - compare pre/post deltas
11. `continue_or_stop`
   - continue only if budget remains, no hard gate fired, and a next smallest action is justified

Do not patch before stages 1 through 8 are complete.

## Structured Evaluator Payload

`references/node_validation.md` must still produce the 12 required sections.
Inside `Verdict`, it must also emit one machine-readable `Structured Evaluation Payload` block containing:

- `phase`
- `node_mode`
- `node_profile`
- `execution_profile`
- `boundary_class`
- `exploratory`
- `maintenance_findings[]`
- `research_findings[]`
- `score_inputs[]`

Every `score_inputs[]` row must include at least:

- `dimension_id`
- `observed_status`
- `severity`
- `confidence`
- `evidence_paths`
- `auto_apply_candidate`

If the structured payload is missing, the planner must downgrade to `manual_ticket` and low confidence. Do not fall back to free-text heuristics as the primary scoring path.

## Exploratory Rule

If the target falls outside checklist coverage or current rules cannot evaluate it honestly:

- keep maintenance-track scoring active
- set `boundary_class = exploratory`
- do not emit a numeric `research_rigor_score`
- set `research_rigor_score_status = unscored_exploratory`
- generate a human gate ticket
- do not let research-facing uncertainty justify `auto_apply`

## Immutable Anchors

The optimizer may not auto-apply changes to its own hard research-gate anchors.

Treat these as immutable for auto-apply purposes:

- `config/immutable_core_rules.yaml`
- `config/research_gate_rules.yaml`

If a proposed change hits those anchors, emit a manual ticket instead of patching.

## Agent Roles

- `evaluator`: validates one bounded target and does not patch files
- `synthesizer`: normalizes findings, emits scorecards, ranks actions, and emits human gate tickets
- `fixer`: applies only approved low-risk maintenance actions and records exact touched files

Do not merge evaluator and fixer responsibilities inside one step.

## Optional Claude Code Teammates

Claude Code teammates are optional. Do not call them unless the user or cycle configuration explicitly enables teammate evaluation.

When enabled:

- teammates act only as independent `evaluator` agents
- teammates must not patch files
- each teammate must emit the same 12-section validation report and `Structured Evaluation Payload`
- teammate outputs feed only the synthesizer and consensus calculation
- maintenance `auto_apply` eligibility requires majority agreement on the same root cause or fix surface
- any missing structured payload, forbidden surface, immutable anchor, research-lane uncertainty, or score instability downgrades the candidate to `manual_ticket`

Deterministic red-team and single-node metric checks remain the primary validation signal; teammate reviews are an optional advisory layer.

## Full P0-P4 Node Campaign

When the user explicitly asks to optimize P0-P4 or every fine-grained node, use `scripts/run_node_campaign.py`.

- enumerate every `research/P*/**/status.yaml` node as an individual frozen target
- run one bounded optimizer cycle per node
- keep Codex as the patch owner through the local fixer path
- keep Claude Code teammates as optional evaluator-only reviewers; pass `--enable-teammates` when they are explicitly requested
- require teammate majority consensus for maintenance `auto_apply` when teammate evaluation is enabled
- preserve the same forbidden surfaces as a normal single-target cycle
- write campaign outputs under `_reference/test/v2/results/node_campaigns/`

For a large campaign, run a dry-run or a small `--limit` slice first unless the user explicitly accepts the runtime and external-agent cost.

## Validation Backend

- Default backend: `local_command`
- Compatibility backend: `external_agent`
- Default concurrency: one validation invocation per cycle

If the default backend lacks an explicit command template, stop with an explicit error. Do not silently fall back to a different backend.

## Allowed Auto-Apply Surface

- `.agent/skills/**`
- `_reference/test/**`
- `research/**/prompts/*.md`
- `research/**/prompts/*.yaml`
- `research/**/skills/local_entry.md`
- `research/**/skills/SKILL.md`
- test fixtures and local validation config files

## Forbidden Auto-Apply Surface

- `research/**/status.yaml`
- `research/**/review/verdict.yaml`
- `backend/graph/*.json`
- `backend/relations/edge_registry.json`
- `research/**/artifacts/**`
- `research/**/logs/**`
- manuscript body files, experiment ledgers, citation artifacts, figure provenance, and submission packages
- `config/immutable_core_rules.yaml`
- `config/research_gate_rules.yaml`

## Outputs

- One cycle directory under `_reference/test/v2/results/`
- Scope record
- Validation summaries
- `03_maintenance_scorecards/`
- `04_research_rigor_scorecards/`
- `05_optimization_actions.yaml`
- `06_human_gate_tickets.yaml`
- `07_applied_changes.md`
- `08_recheck.md`
- `09_cycle_verdict.yaml`
- optional cycle-local `10_redteam/`
- optional cycle-local `11_single_node_metrics/`
- optional full-node campaign directory under `_reference/test/v2/results/node_campaigns/`

## Boundaries

- Do not replace `graph_driven_research_orchestrator`, `auto_research_campaign`, or `autonomous_research_lane`.
- Do not auto-edit review verdicts, status files, generated graph artifacts, or experiment evidence.
- Do not fabricate evidence to close a hard gate.
- Do not run an unbounded loop.
- Do not turn research-rigor scores into automatic patch authority.

## stop_with

- preflight_failed
- target_not_frozen
- graph_skill_required
- no_actionable_target
- critical_unverified_assumption
- validation_failed
- hard_gate_hit
- no_auto_apply_eligible_fix
- forbidden_change_required
- cycle_budget_reached
- recheck_failed
