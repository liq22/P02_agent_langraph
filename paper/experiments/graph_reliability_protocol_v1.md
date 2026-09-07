# Graph P2-E9 repeated-run reliability protocol v1 (superseded)

**Status:** `superseded_phmskills_base`; formal launch forbidden
**Frozen:** 2026-08-20
**Machine-readable authority:** `graph_reliability_protocol_v1.yaml`

This historical shell used a PHMskills-derived Reactive control and is not an
admissible Paper 2 comparison. It is retained only for provenance. The active
Generic-base authority is `graph_reliability_protocol_v2.yaml`; current tools
reject v1 for scheduling, acceptance, or analysis, and v1 outputs cannot be
resumed or pooled with v2.

This protocol registers the separate n=10 repeated-run reliability extension
for Paper 2. It does not execute a provider, change the active Paderborn v6
primary experiment, or alter the separately registered dynamic-ablation study.
The scheduler only materializes and validates assignments; the analyzer accepts
results only after every registered canonical episode has a non-provider
terminal attempt.

## Registered cohort

The cohort contains ten new repeat IDs and ten unique seeds, `20260828` through
`20260906`. They are disjoint from the three primary seeds (`20260808`–
`20260810`). Each repeat covers the eight frozen public replay sequences in
`rotation_0` under both arms:

- Reactive: the PHMskills agent without Graph-state routing;
- Graph: the same PHMskills and public information plus the full eight-state
  Graph policy.

The paired unit is `(repeat_id, seed, rotation, public_sequence_id)`. Thus the
cohort has 80 matched pairs and 160 assigned arm episodes. Arm order alternates
by repeat-plus-sequence parity. This controls ordering; it does not create
additional replication.

The model, provider profile, task, public sequence, tools, numerical experts,
budget, evaluator, temperature, and output-token cap are matched. The sole
treatment difference is full Graph-state routing and its legal tool subset.

## Isolation from primary and dynamic profiles

The reliability cohort has effective runtime identity
`phase1_graph_reliability_n10_v1` and profile ID
`graph_reliability_n10_v1`. It uses the v6 bounded-observation semantics as its
base, but has its own output and result roots. Primary v6 run directories and
the dynamic-ablation profile are forbidden inputs. The n=10 estimates are
reported alongside the three-seed primary comparison; they never replace,
extend, or pool with that primary estimand.

The provider and model fields freeze a possible future execution profile. The
two scripts in this protocol contain no provider client and do not authorize
inference.

## Attempts, failures, and acceptance

Every episode attempt is an immutable exact-six RunBundle containing
`run.json`, `rollout.jsonl`, `submission.json`, `metrics.json`,
`failures.jsonl`, and `artifacts.json`. `rollout.jsonl` remains canonical event
truth.

An episode key may retain provider-error attempts, but acceptance requires
exactly one same-profile non-provider terminal attempt. An unresolved provider
error therefore leaves the cohort incomplete. Agent errors, invalid
submissions, budget exhaustion, timeouts, and other non-provider terminals are
not exclusions: they remain in every assigned-episode denominator with their
canonical outcome.

The acceptance gate fails closed on a missing run directory, manifest drift,
profile drift, unregistered sequence, incomplete exact-six leaf, duplicate
non-provider terminal, unresolved provider failure, unmatched arm, or any
episode-count mismatch.

## Reliability and cost reporting

The pass event is canonical `rollout_metrics.grounded_completion == 1.0`.

- `pass@1` is the passed fraction over all assigned episodes in an arm,
  including non-provider failures.
- `pass-all-10` is the fraction of the eight base public sequences that pass in
  every one of the ten registered repeats for that arm.

For each registered metric, the report includes the equal-weight mean over ten
repeat estimates, sample between-repeat variance, and a 95% crossed
repeat-by-sequence bootstrap interval. Reactive and Graph remain paired within
every bootstrap draw; paired effects are Graph minus Reactive. The bootstrap
uses 2,000 iterations and seed `20260820`. `pass-all-10` keeps the complete ten-
repeat vector fixed and resamples only public sequences.

Token, turn, tool-call, and model-cost outcomes use every assigned episode.
Missing or out-of-domain values are `null` with the defined numerator and full
assigned denominator. They are never coerced to zero. Paderborn replay has no
verified event-onset timestamps, so event-F1 and detection delay remain
forbidden.

## Provider-free usage

The deterministic dry schedule is safe to inspect without credentials:

```bash
python scripts/schedule_graph_reliability.py schedule \
  --output-root /path/to/isolated/reliability/root
```

After a future, separately authorized executor has produced the complete frozen
profile, acceptance and analysis are separate commands:

```bash
python scripts/schedule_graph_reliability.py accept \
  --output-root /path/to/isolated/reliability/root \
  --output /path/to/acceptance.json

python scripts/analyze_graph_reliability.py \
  --output-root /path/to/isolated/reliability/root \
  --acceptance /path/to/acceptance.json \
  --output /path/to/result.json
```

The dry schedule is mechanics evidence only. No reliability or Graph-effect
claim is available until the 160-episode acceptance gate succeeds and the
result is computed from those same canonical bundles.
