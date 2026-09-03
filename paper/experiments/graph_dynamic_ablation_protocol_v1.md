# Graph dynamic/ablation protocol v1

**Status:** preregistered; provider-free Mock gate accepted; formal not run

**Frozen:** 2026-08-13

**Implementation status updated:** 2026-08-20

**Machine-readable authority:** `graph_dynamic_ablation_protocol_v1.yaml`

> Historical boundary (2026-08-20): this v1 file records the retired
> PHMskills-base mechanics profile. It is not eligible for new formal runs or
> resume. The CORE-authorized Generic-base design is registered separately as
> `graph_dynamic_ablation_protocol_v2.yaml`; v1 and v2 outputs never pool.

This protocol freezes the separate Paderborn dynamic and Graph-ablation study
for P2-E2 through P2-E7. It does not change the active Paderborn v6 dataset,
formal shell, or current primary result profile. Existing runs cannot be
relabelled as evidence for this protocol. At freeze time the event emitter,
isolated runtime profile, conversation ablations, single-unit runner, and
formal results did not exist. As of the implementation update, the Benchmark's
generic public-condition event delivery, the P02 runtime and five Graph
profiles, and an isolated single-unit runner are implemented and provider-free
tested. The exact-six provider-free acceptance bundle set is now materialized
and accepted. A provider-free, fail-closed formal cohort acceptor/analyzer is
also implemented in `scripts/analyze_graph_dynamic_formal.py`; the
provider-bound formal cohort and formal results remain absent.

## Scientific object

The study asks whether the current eight-state Graph policy changes observable
agent behavior or completion as a bounded replay becomes longer and its public
operating-condition identifier changes. The task is only
`online_replay_monitoring`. Cold-start diagnosis, anomaly episodes, RUL,
maintenance decisions, live streaming, and cross-dataset transfer are outside
this profile.

Paderborn provides no verified event-onset timestamps. Accordingly, this study
does **not** introduce `fault_onset`, `anomaly_onset`, event-F1, detection delay,
or time-to-fault claims. A `domain_id` change is reported only as a public
operating-condition-identifier change in an offline, metadata-ordered replay.
It is not a failure onset or a causal physical transition.

## Frozen sequence and public event

For each of the eight held-out bearings in `rotation_0`, task construction sorts
records by the current DataPort metadata order and freezes a 12-window master
sequence. For a bearing with (N) records, master index (k) is

\[
\left\lfloor\frac{k(N-1)}{11}\right\rfloor,
\qquad k=0,\ldots,11.
\]

The three horizons are exact prefixes of that one sequence:

| Horizon | Construction | Expected condition-change releases |
|---:|---|---:|
| 3 | `master[0:3]` | none |
| 6 | `master[0:6]` | index 3 |
| 12 | `master[0:12]` | indices 3, 6, 9 |

No horizon is independently resampled. The frozen public `domain_id` schedule
is `[1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0]`; a mismatch or missing/non-integral
value fails the profile before inference.

At release index zero there is no event. At an index (i>0), the environment
compares only the normalized public `domain_id` of the newly released sample
with that of the previously released sample. It emits exactly one
`operating_condition_change` pulse iff they differ. It cannot inspect signal
values, features, labels, private targets, bearing identity, or evaluator
output, and it cannot expose a future sample or event.

Each logical event receives a sequential opaque ID such as `occ-00000001`.
IDs are assigned before inference from the sorted public key `(seed, rotation,
public_sequence_id, release_index)`; no hash is used. Horizon, arm, Graph
profile, provider, model, target, and bearing identity are excluded. The same
logical ID is deliberately referenced by nested horizons and matched arms,
while distinct logical events cannot collide. The formal catalog contains 72
logical events (3 seeds × 8 sequences × 3 changes).

The complete `public_condition_event` payload and release index must be
identical in Reactive, full Graph, and every ablation. The Benchmark owns only
generic event release under `phase1_public_condition_event_v1`; it does not own
Graph semantics. Reactive sees the same public event information, while P02
alone translates it into a Graph state and state-specific tool subset.

## Graph profiles

The shared states remain `Inspect`, `Hypothesize`, `Analyze`, `Check`,
`Monitor`, `Revise`, `Recover`, and `Submit`. State tool surfaces and the exact
legal adjacency list for every profile are frozen in the YAML.

Routing precedence for the full profile is:

1. an immediately preceding action error enters `Recover`;
2. a new public condition-change pulse enters `Monitor`;
3. the next non-error, non-event observation after `Monitor` enters `Revise`;
4. otherwise the state is recomputed from public rollout progress.

The ablations have the following operational meanings:

| Profile | Exact removal |
|---|---|
| `no_recovery_revision_edge` | Errors do not force `Recover`; `Monitor` does not lead to `Revise`. Both states are unreachable. |
| `no_observation_conditioned_branching` | The public event remains in model input but cannot change the router state. `Monitor` and `Revise` are unreachable. |
| `no_persistent_graph_state` | No previous router state is consumed and no earlier Graph state or state-guidance message may remain in the model conversation. |
| `no_replanning` | Events still enter `Monitor`, but the following decision resumes the rollout-derived base state without `Revise`. |

For `no_persistent_graph_state`, each request is rebuilt from the common base
prompt, the shared public action/result history, prior public observations, and
the current state guidance exactly once. Earlier `decision_state` fields and
state-guidance messages are stripped. This preserves public task evidence while
removing Graph-state memory from both router input and model conversation.

## Matched experiment matrix

Seeds are `20260808`, `20260809`, and `20260810`; only `rotation_0` is used.
Each cell contains the same 8 held-out sequences and the same event catalog.

| Horizon | Cells per seed and sequence |
|---:|---|
| 3 | Reactive, Graph full |
| 6 | Reactive, Graph full |
| 12 | Reactive, Graph full, and four Graph ablations |

This is 10 cells per seed/sequence and 240 formal episode bundles in total.
P2-E2 compares full Graph with Reactive across horizons. P2-E3 through P2-E6
compare full Graph with one ablation at horizon 12. P2-E7 uses the already
registered Reactive, full Graph, and no-observation-branching horizon-12 cells;
it does not add or duplicate episodes.

The backbone, provider, protocol, temperature, output-token cap, public prompt
information, events, tools, numerical experts, evaluator, seeds, and episode
order are matched. The frozen formal profile uses
`cohere/north-mini-code:free` through `openrouter-free` and
`openai_chat_completions`, with effective runtime contract
`phase1_graph_dynamic_ablation_v1`. This identity is separate from the active
Paderborn v6 primary profile. Results cannot be pooled across the two profiles
or across any provider, model, protocol, or runtime change.

Budgets scale linearly with horizon:

| Horizon | Tool/LLM turns | Reads | Operators | Models | Points | Bytes |
|---:|---:|---:|---:|---:|---:|---:|
| 3 | 72 | 3 | 50 | 3 | 24,576 | 196,608 |
| 6 | 144 | 6 | 100 | 6 | 49,152 | 393,216 |
| 12 | 288 | 12 | 200 | 12 | 98,304 | 786,432 |

Wall-clock time is measured but not capped. Failed, partial, timed-out,
provider-failed, invalid, and budget-exhausted episodes remain in denominators.
Canonical terminal status and failure kind are recorded separately: a provider
interruption is a `failed` terminal with `provider_error`. Its attempt is
retained, but that scheduled unit remains incomplete until exactly one later
same-profile non-provider terminal exists. Every non-provider failure is the
unit's effective outcome and remains in the 240-unit denominator.

## Outcomes and statistics

The primary outcome is episode-level grounded completion over every scheduled
episode. Task outcomes are window Average Precision, completion-adjusted window
Average Precision, AUROC, false-alarm rate, and true-positive rate. Dynamic
diagnostics include event-to-`Monitor`/`Revise` transitions, steps from an event
to the next successful action and model prediction, post-event repetition, and
post-event budget exhaustion. Undefined metrics are reported as undefined, not
zero.

The paired unit is `(seed, rotation, public_sequence_id, horizon)`. Repeated
seeds are averaged within the evaluator-private bearing cluster before the
exact 256-assignment paired permutation over the eight bearings. Paired cluster
bootstrap intervals use 10,000 resamples, seed `20260813`, and 95% coverage.
Holm correction is applied separately to the ablation and horizon-interaction
families. Every observed direction is reported.

## Gates and evidence boundary

The static protocol and focused implementation tests prove that the
preregistration parses, the generic event emitter is release-bounded, and the
P02 profiles and conversation ablations execute. The provider-free command
`scripts/run_graph_dynamic_mock_acceptance.py` additionally materialized all 10
registered sequence-0001 cells as exact-six canonical bundles under the
registered mechanics root. `gate.json` accepts matched event payloads and
release indices, no-future access, profile-specific legal transitions,
historical-state stripping in actual no-persistent outbound Mock requests, the
mechanics-only evidence class, and zero provider calls. Mock output cannot
support PHM or Graph performance claims.

The provider-bound 240-episode matrix has not started. Formal inference may
start only after the materialized provider-free gate and a same-profile
two-turn tool probe pass. A free-quota/provider failure is retained and stops
the single provider runner; continuation resumes the same frozen profile from
the first incomplete unit. Model or route switching is forbidden.

Formal output is isolated under
`paper/experiments/runs/formal/graph_dynamic_ablation_v1/`; mechanics output,
formal results, and the public event catalog use their separately registered
roots in the YAML. Each episode leaf contains only the benchmark's six
canonical files, with `rollout.jsonl` as event truth.

After execution, `scripts/analyze_graph_dynamic_formal.py accept` requires all
240 registered unit roots, contiguous exact-six attempt histories, one
non-provider terminal per unit, evaluator-private master prefixes that are
identical across seeds/profiles and nested across horizons, deterministic event
IDs, profile-specific transition and state-tool legality, and a manifest that
proves the frozen model/provider/protocol/temperature/output cap and zero-price
profile. The analyzer then reports only horizon-and-profile-specific cells and
registered paired contrasts. It has no pooled-across-horizon or
pooled-across-profile result path; undefined metrics remain null with their
defined numerator.
