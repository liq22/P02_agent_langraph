# AutoResearch System Optimizer Cycle Prompt

You are running one bounded optimization cycle for the AutoResearch system itself.
You are not trying to prove the framework works. You are trying to improve its truthfulness, boundary clarity, and operational reliability without fabricating evidence or silently rewriting research truth.

## Mission

Run one bounded cycle through these stages:

1. preflight
2. target freeze
3. prompt hardening
4. evaluate
5. finding normalization
6. score
7. rank actions
8. triage
9. apply only low-risk maintenance fixes
10. re-run checks
11. decide whether to continue or stop

Do not skip stages. Do not patch before stages 1 through 8 are complete.

## Canonical Inputs

- `.agent/skills/autoresearch-system-optimizer/references/node_validation.md`
- `.agent/skills/autoresearch-system-optimizer/config/validation_rules.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/optimization_loop.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/score_matrix.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/score_policy.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/scorecard.template.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/immutable_core_rules.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/research_gate_rules.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/agents.yaml`

## Validation Layers

Use existing validation layers instead of creating a new test tree:

- `_reference/test/v2/` is the optimizer acceptance and deterministic metric fixture layer.
- `_reference/test/redteam/` is the node-level adversarial red-team layer.

Cycle-local runs must write red-team and single-node metric reports under the current cycle directory. Do not overwrite shared `reports/latest` paths during optimizer cycles.

## Stage Contract

### 1. Preflight

- load the declared config inputs
- run the declared preflight checks
- verify runtime prompt/config/script truth is consistent
- stop immediately on missing runtime truth

### 2. Target Freeze

- if the caller already provided a target node, checklist gap, or file-surface scope, use it directly
- if the caller did not provide a target and the scope is repo-wide or phase-wide, call `$graph-driven-research-orchestrator` once to select the current actionable node
- reading `backend/graph/graph_status.json` alone is not enough; freeze the target through the graph skill contract and normalize the selected node to a repo path
- after that one graph-guided routing round, freeze the target for this cycle
- do not invent a second scheduler

### 3. Prompt Hardening

Before launching evaluators, compare `.agent/skills/autoresearch-system-optimizer/references/node_validation.md` against `.agent/skills/autoresearch-system-optimizer/config/validation_rules.yaml`.

Do exactly two tightening passes when needed:

1. tighten truth-source usage, verdict strictness, `UNVERIFIED` handling, and the structured evaluator payload contract
2. tighten stop conditions, hard gates, exploratory branching, and maintenance-vs-research lane separation

Only patch the evaluator prompt if the change is low-risk, local, and inside the allowed path set.

### 4. Evaluate

Use evaluator agents only.

Evaluator rules:

- validate one smallest meaningful target
- do not patch files
- use the canonical node validation prompt
- produce the 12 required sections
- emit compact `Finding Rows` inside `Adversarial Findings`
- emit the structured YAML payload inside `Verdict`

### 5. Finding Normalization

Use the synthesizer to:

- merge evaluator outputs
- deduplicate findings into root causes
- preserve evidence path, severity, confidence, and affected surface
- separate maintenance findings from research-rigor findings

Do not invent evidence.

### 6. Score

- compute one `maintenance_scorecard` and one `research_rigor_scorecard` per validated target
- drive scoring from structured `score_inputs[]`
- select dimensions from `phase + node_mode + node_profile + execution_profile`
- if `boundary_class = exploratory`, still compute the maintenance lane and emit `research_rigor_score_status = unscored_exploratory`
- keep each node score stable under the same frozen target boundary, repo evidence, score matrix, and structured inputs
- if a score changes, record the evidence delta; if the evaluator cannot explain the delta, downgrade patch planning to manual handling

### 7. Rank Actions

- convert maintenance findings into ranked maintenance actions
- convert research-facing findings into human gate tickets or `defer` / `no_change`
- do not let research-rigor scores directly authorize patching

### 8. Triage

Before patching, classify every candidate as exactly one of:

- `auto_apply`
- `manual_ticket`
- `defer`
- `no_change`

An action may be `auto_apply` only when all of the following hold:

- `lane = maintenance`
- `auto_apply_candidate = true`
- the needed edit is inside the allowed path set
- the fix is local and reversible
- no immutable anchor or research-gate rule is touched
- the expected recheck is narrow and explicit

Freeze the patch list before editing.

### 9. Apply Low-Risk Maintenance Fixes

Use fixer agents only.

Fixer rules:

- only execute actions explicitly marked `lane = maintenance` and `disposition = auto_apply`
- stay inside the allowed path set
- patch the smallest reversible surface
- record exact touched files
- record rejected higher-risk alternatives
- if the cycle runs with `apply_mode = none`, do not patch files; emit the same ranked actions as an advisory-only cycle and stop after verdict emission

### 10. Re-run Checks

Re-run the narrowest declared checks first.

At minimum, report:

- rechecks executed
- pass/fail status
- maintenance score deltas
- research-lane status deltas
- deterministic red-team and single-node metric summaries when configured
- whether any new blocker appeared

If recheck fails after patching, stop this cycle.

### 11. Decide Whether to Continue or Stop

Continue only when all of the following hold:

- budget remains
- no hard gate fired
- the recheck passed
- a next smallest maintenance action is clearly justified by evidence

If the cycle runs with `apply_mode = none`, the correct end state is `advisory_cycle_completed`, not another automatic continuation.

Otherwise stop and state the exact blocker.

## Multi-Agent Contract

Use three roles only:

- `evaluator`
- `synthesizer`
- `fixer`

Do not let the fixer author the evaluation verdict for the same step.

Claude Code teammates are optional. Use them only when explicitly enabled by the caller or cycle configuration. When enabled, they are evaluator-only agents; they may not patch files, and their outputs require majority agreement on the same root cause or fix surface before a maintenance finding can retain `auto_apply` eligibility.

## Full Node Campaign Contract

When the caller asks to optimize all P0-P4 nodes, use `scripts/run_node_campaign.py` instead of widening a single cycle.

- enumerate every `research/P*/**/status.yaml` node and treat each directory as a separate frozen target
- run one normal optimizer cycle per node
- keep all cycle outputs under one campaign directory
- apply only low-risk maintenance actions from the maintenance lane
- do not edit status files, review verdicts, graphs, artifacts, logs, manuscripts, experiment ledgers, citation truth, figure provenance, or submission packages
- if Claude Code teammates are enabled, use them only as evaluator agents and require majority consensus for `auto_apply`

## Auto-Apply Rules

Allowed by default:

- `.agent/skills/**`
- `_reference/test/**`
- `research/**/prompts/*.md`
- `research/**/prompts/*.yaml`
- `research/**/skills/local_entry.md`
- `research/**/skills/SKILL.md`
- test fixtures and validation config files

Forbidden by default:

- `research/**/status.yaml`
- `research/**/review/verdict.yaml`
- `backend/graph/*.json`
- `backend/relations/edge_registry.json`
- `research/**/artifacts/**`
- `research/**/logs/**`
- manuscript bodies, experiment ledgers, citation truth, figure provenance, submission packages
- `.agent/skills/autoresearch-system-optimizer/config/immutable_core_rules.yaml`
- `.agent/skills/autoresearch-system-optimizer/config/research_gate_rules.yaml`

If a fix requires a forbidden path or an immutable anchor, produce a manual optimization ticket instead of patching.

## Required Outputs

Write one cycle directory containing:

- `00_scope.yaml`
- `01_validation/` when a cycle launched validation itself
- `02_summary.md`
- `03_maintenance_scorecards/`
- `04_research_rigor_scorecards/`
- `05_optimization_actions.yaml`
- `06_human_gate_tickets.yaml`
- `07_applied_changes.md`
- `08_recheck.md`
- `09_cycle_verdict.yaml`
- cycle-local `10_redteam/` when deterministic red-team checks are configured
- cycle-local `11_single_node_metrics/` when deterministic single-node metrics are configured

## Stop Gates

Stop this cycle when:

- preflight fails
- the target is not frozen
- a critical assumption is `UNVERIFIED`
- a hard gate fails
- the needed fix is outside the low-risk path set
- no auto-apply eligible maintenance fix remains
- recheck fails after a patch
- the cycle budget is exhausted

When stopping, state the precise blocker and the smallest safe next step.
