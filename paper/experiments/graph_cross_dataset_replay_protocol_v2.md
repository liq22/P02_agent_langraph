# Graph cross-dataset replay protocol v2

**Status:** superseded zero-eligible snapshot; launch forbidden

**Frozen:** 2026-08-20

**Machine-readable authority:** `graph_cross_dataset_replay_protocol_v2.yaml`

**Current authority:** `graph_cross_dataset_replay_protocol_v3.yaml`

This historical snapshot superseded the non-executable PHMskills-base v1
record and bound the corrected P2 comparison to two direct
Generic-base identities:

| Role | Runtime class | Profile | Identity |
|---|---|---|---|
| Control | `ReactiveSequentialAgent` | `reactive_sequential_generic_v2` | zero-behavior-override `GenericLLMToolAgent` |
| Treatment | `GraphDecisionAgent` | `graph_dynamic_full_generic_v2` | same Generic base plus registered graph control |

Both bind `p2_experiment_id=p2_graph_vs_generic_llm_v1` and
`matched_control_id=benchmark_generic_llm_tool_agent_v1`. The control uses
`agent_implementation_id=reactive_sequential_agent_v1`; the treatment uses
`agent_control_id=graph_decision_control_v1` and
`agent_implementation_id=graph_decision_agent_v1`. PHMskills-derived leaves are
never eligible for this estimand.

## Current zero-unit result

The current schedule contains **zero episode bundles**:

| Candidate | Ordered mechanics | Legal replay outcome target | Executable P2-E8 status |
|---|---:|---:|---:|
| XJTU-SY | yes | no | blocked |
| CWRU | no | no | blocked |
| HUST24 | no | no | blocked |

XJTU-SY has real ordered replay mechanics, including three accepted exact-six
targetless bundles and the preserved Bearing3_1 acquisition gap. Its source
protocol still declares `formal_evidence_eligible: false`,
`task_outcome_target_protocol_complete: false`, and no verified onset,
interval, or window-level anomaly target. `RUL_label`, the terminal record, or
a fixed lifecycle fraction cannot be converted into a target. The targetless
smoke is not cross-dataset performance and cannot estimate a Graph effect.

CWRU remains a blocked diagnosis-only candidate without an accepted asset
split, license gate, DataPort binding, or replay task. HUST24's time-varying
speed is an operating-condition change rather than a fault onset; its asset,
target, channel, split, license, replay, and DataPort gates remain blocked.

## Activation and matching

The scheduler reads the three Benchmark dataset protocols and requires every
execution/readiness check plus at least one legitimate evaluator-private
target: a verified fault/anomaly event or interval, or a verified window-level
anomaly target. Outcome eligibility is independent of mechanics completion.

An eligible source is necessary but not sufficient. A new v2-derived protocol
must also freeze the external sequence, horizon, budget, evaluator, provider
profile, and resume contract. ReactiveSequential and GraphDecision must share
the Generic scaffold, model, provider/runtime, prompt information before the
registered state suffix, public history, global tools, numerical experts,
dataset, split, episode order, horizon, budget, evaluator, and seeds. The only
treatment difference is registered graph state control over the same Generic
tool surface. Effects are reported per dataset and never pooled across
datasets; every failed assigned episode remains in its arm denominator.

## Historical provider-free audit

The current scheduler defaults to v3. Passing v2 explicitly is refused because
this zero-eligible record is no longer executable:

```bash
python scripts/schedule_graph_cross_dataset_replay.py \
  --dry-run \
  --protocol paper/experiments/graph_cross_dataset_replay_protocol_v2.yaml
```

The frozen v2 audit recorded zero eligible datasets and zero units. Those
counts remain historical and cannot override the accepted Ottawa registration
in v3.

## Claim boundary

Until a complete matched Generic-base cohort is accepted, P2-E8 supports no
cross-dataset validity, external validity, Graph transfer, task-performance,
event-F1, or detection-delay claim. Unavailable metrics remain unavailable,
not zero.
