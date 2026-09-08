# Graph horizon-scaling scheduler contract v1 (superseded)

**Status:** `superseded_phmskills_base`; formal launch forbidden

**Frozen:** 2026-08-20

**Machine-readable authority:** `graph_horizon_scaling_protocol_v1.yaml`

This historical projection used a PHMskills-derived Reactive control and is no
longer an admissible Paper 2 experiment. It is retained only for provenance.
The Generic-LLM-base authority is
`graph_horizon_scaling_protocol_v2.yaml`. The scheduler rejects v1 even when it
is selected explicitly; no v1 command may be generated, resumed, or pooled
with v2.

This is the executable schedule projection for Paper 2 experiment P2-E2. It
does not create a new experiment profile and does not supersede
`graph_dynamic_ablation_protocol_v1.yaml`. The scheduler only constructs a
deterministic manifest and future command vectors. It never reads provider
credentials, invokes the runner, or writes formal results.

## Frozen comparison

Each of the eight public `rotation_0` sequence IDs names one longest ordered
12-window sequence. Horizons 3 and 6 are exact prefixes of that same sequence;
they are never independently sampled for a seed, arm, or horizon.

| Horizon | Public sequence | Reactive | Graph-full | Per-horizon bundles |
|---:|---|---:|---:|---:|
| 3 | `master[0:3]` | 24 | 24 | 48 |
| 6 | `master[0:6]` | 24 | 24 | 48 |
| 12 | `master[0:12]` | 24 | 24 | 48 |

The 24 units per cell are three registered seeds times eight public sequences.
The complete P2-E2 schedule therefore contains 72 matched pairs and 144 episode
bundles. The four horizon-12 Graph ablations belong to P2-E3 through P2-E6 and
are deliberately absent here. A horizon-12 unit reused by P2-E7 is stored once,
not rerun or duplicated in a denominator.

`domain_id` changes are public operating-condition-identifier changes in an
offline metadata order. Horizon is released-window count, not physical time,
fault onset, time to failure, or a basis for event-F1/detection-delay claims.

## Matched arms and budgets

Reactive and Graph-full share the model, provider profile, public prompt
information, public event payload, tools before Graph filtering, numerical
experts, evaluator, seeds, and episode order. The treatment-only difference is
the full Graph state router and its state-specific legal tool subset.

| Horizon | Tool/LLM turns | Reads | Operators | Models | Points | Bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 72 | 3 | 50 | 3 | 24,576 | 196,608 |
| 6 | 144 | 6 | 100 | 6 | 49,152 | 393,216 |
| 12 | 288 | 12 | 200 | 12 | 98,304 | 786,432 |

The future dynamic runner must load these budgets from
`graph_dynamic_ablation_protocol_v1.yaml` through `--dynamic-protocol`; the
scheduler does not invent parallel budget flags.

## Deterministic and collision-free schedule

Unit order is fixed as seed, rotation, public sequence ID, horizon, then
Reactive/Graph-full. A unit key and output root contain every varying field.
The 144 output roots are therefore unique. A retry creates a new attempt below
the same unit root and uses the same model, route, runtime, sequence, horizon,
and budget.

Each successful or failed attempt retains the benchmark's exact six canonical
files, with `rollout.jsonl` as event truth. Canonical terminal statuses include
`submitted`, `partial`, `stopped`, `failed`, `timeout`,
`invalid_submission`, and `budget_exhausted`; failure kinds such as
`provider_error` and `agent_decision_error` are recorded separately. A retained
provider-error attempt does not become a second denominator row: that unit is
incomplete until one later same-profile non-provider terminal exists. Every
non-provider failure remains the unit's outcome in the 144-unit denominator.

Run the provider-free projection with:

```bash
python scripts/schedule_graph_horizon_scaling.py --dry-run
```

The JSON output contains all unit keys, budgets, unique output roots, argv
vectors, shell-rendered commands, and runtime-readiness diagnostics. It
contains environment-variable names only, never values. `--dry-run` performs
no filesystem writes or provider calls.

The command vectors target three isolated dynamic-runtime flags:
`--dynamic-protocol`, `--public-sequence-id`, and `--horizon`. Until the runner
exposes those flags and the source protocol declares the required runtime
components implemented, readiness is `false`. For a strict integration check:

```bash
python scripts/schedule_graph_horizon_scaling.py \
  --dry-run \
  --require-runtime-ready
```

That command exits nonzero when a prerequisite is missing. Invoking the
scheduler without `--dry-run` is always refused: formal provider execution is
owned by the root orchestrator after the provider-free mechanics gate and the
same-profile two-turn probe pass.

## Reporting boundary

Grounded completion and all task, dynamic-behavior, trajectory, and cost
metrics are reported separately at horizons 3, 6, and 12. There is no pooled
headline Graph effect across horizons. The registered interaction is the
matched `(Graph-full - Reactive)` difference at horizon 12 minus that at
horizon 3. Because horizons are nested observations of the same public
sequence, their rows must never be treated as independent samples. Undefined
metrics remain undefined rather than being replaced with zero.

If and only if the future 240-unit P2-E2--P2-E7 formal cohort becomes complete,
`scripts/analyze_graph_dynamic_formal.py` is the registered provider-free
acceptor/analyzer. Its result schema has no pooled horizon/profile view: P2-E2
selects its registered 144 rows from that cohort, and horizon-12 rows reused by
P2-E7 are referenced rather than duplicated. The current formal root is empty,
so no formal acceptance or performance result exists yet.
