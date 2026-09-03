# Graph cross-dataset replay protocol v3

**Status:** Ottawa source, runtime, dry schedule, accepted-only analyzer, and
accepted-result manuscript consumer are provider-free ready; formal inference
has not run and the 2026-09-02 same-day North retry is blocked after HTTP 429.

**Frozen:** 2026-09-02

**Machine-readable authority:** `graph_cross_dataset_replay_protocol_v3.yaml`

Version 3 supersedes the zero-eligible v2 snapshot. It registers the
Benchmark-owned Ottawa ordered bearing-state protocol as the sole P2-E8
external dataset and preserves the corrected Generic-base comparison:

| Role | Runtime class | Profile | Only arm-specific factor |
|---|---|---|---|
| Control | `ReactiveSequentialAgent` | `reactive_sequential_generic_v2` | no graph decision control |
| Treatment | `GraphDecisionAgent` | `graph_dynamic_full_generic_v2` | registered graph state guidance and tool visibility |

Both arms share the Ottawa CSV DataPort, v6 replay runtime, split, ordered
episodes, numerical experts, model/provider profile, budget, and independent
evaluator. PHMskills-derived leaves remain ineligible.

## Registered Ottawa path

Ottawa contributes 12 physical bearings. Each bearing supplies one
source-authored `healthy`, `developing_fault`, and `faulty` window; the private
evaluator mapping is `[0, 1, 1]`. Three asset-disjoint cyclic rotations hold
out four bearings each. Three seeds and two arms yield:

| Quantity | Registered count |
|---|---:|
| Runner commands | 18 |
| Episode bundles | 72 |
| Matched Reactive/Graph episode pairs | 36 |
| Assigned windows across both arms | 216 |

The source states define ordered window targets, not a verified fault-onset
event. Event-F1, detection delay, and Monitor/Revise event-branch transfer are
therefore not P2-E8 estimands.

## Provider-free preflight

```bash
python scripts/schedule_graph_cross_dataset_replay.py \
  --dry-run \
  --run-stamp 20260902T000000Z
```

The scheduler audits source protocols, runner flags/source, analyzer source,
and emits 18 command arrays. It reads no raw signals, private targets,
credentials, or environment values; invokes no runner; performs no provider
call; and writes no output. The current manifest reports
`provider_free_preflight_ready=true` while retaining the same-day HTTP-429
retry blocker.

## Accepted-only analysis

`scripts/analyze_graph_cross_dataset_replay.py` accepts only nine complete
canonical runs per arm and independently rebuilds private assignments through
the registered DataPort. It rejects partial cohorts, unresolved provider
errors, identity/world drift, non-exact episode keys, or any denominator other
than 36 episodes and 108 windows per arm. Only then does it recompute the
target-adverse metrics and the 2,000-resample physical-bearing-clustered
Graph-minus-Reactive bootstrap.

## Accepted-result manuscript consumer

After the analyzer emits the registered accepted result, the provider-free
consumer is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:src:../p01-phm-agent-benchmark/src \
  python scripts/render_graph_cross_dataset_manuscript.py
```

It reads only this protocol, the accepted `formal_result.json`, and the active
manuscript. It does not read raw run bundles, private DataPort inputs, provider
environment, or credentials. Before any write, it rechecks the embedded 9-run
and 36-episode acceptance per arm, 36 exact pairs, 108 assigned windows per
arm, retained failures, target-adverse accounting, all five displayed
Graph-minus-Reactive task deltas, and the 2,000-resample bootstrap metadata. It
then updates `paper/assets/tables/p2_e8_ottawa_results.md`,
`paper/assets/figures/p2_e8_ottawa_primary.svg`, and the unique
`P2_E8_OTTAWA` manuscript marker as one write group. The 9/9 focused checks
include direct analyzer-to-consumer integration and rejected, drifted, marker,
and no-write cases.

No accepted P2-E8 cohort or result exists, so the dedicated table and figure
remain absent and the manuscript marker stays Pending. A dry schedule, runtime
smoke, analyzer test, or consumer test is implementation evidence, not
cross-dataset performance, external validity, or a Graph effect.
