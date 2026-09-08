# Graph cross-dataset replay protocol v1 — superseded

**Status:** `superseded_phmskills_base`; launch forbidden

**Frozen:** 2026-08-20

**Machine-readable authority:** `graph_cross_dataset_replay_protocol_v1.yaml`

**Current authority:** `graph_cross_dataset_replay_protocol_v3.yaml`

This file is retained only as an inspectable record of the superseded
PHMskills-base contract. It does not bind the corrected Generic-base P2 agent
identities, is not an executable protocol, and must not be used for a new
schedule, run, result, or claim. The scheduler defaults to v2 and rejects an
explicit v1 protocol path.

The candidate audit below remains useful historical context. It is not current
P2-E8 agent-comparison authority.

## Current outcome

The current schedule contains **zero episode bundles**. This is an intended
fail-closed result, not a missing-data value and not an empty experiment:

| Candidate | Ordered mechanics | Legal replay outcome target | Executable P2-E8 status |
|---|---:|---:|---:|
| XJTU-SY | yes | no | blocked |
| CWRU | no | no | blocked |
| HUST24 | no | no | blocked |

XJTU-SY has the strongest current mechanics evidence. Its real-data targetless
smoke accepted three exact-six bundles, twelve ordered reads, and the known
two-minute Bearing3_1 acquisition gap without imputation. The authoritative
dataset protocol nevertheless declares `formal_evidence_eligible: false`,
`task_outcome_target_protocol_complete: false`, and all task-outcome metrics
unavailable. Its `RUL_label`, terminal record, or a fixed lifecycle fraction
must not be converted into a degradation onset. The accepted targetless smoke
therefore cannot be counted as cross-dataset performance or a Graph effect.

CWRU is currently a blocked diagnosis-only candidate: its physical asset unit,
inventory, license, split, and DataPort gates are not accepted, and it has no
ordered replay task. HUST24 has a time-varying operating-speed record, but an
operating-condition change is not a fault onset; asset identity, target,
channel, split, license, monotonic replay, and DataPort gates remain blocked.

## Activation rule

The provider-free scheduler reads all three Benchmark dataset protocols and
checks their exact source fields. A dataset is eligible only if every
execution/readiness assertion passes and at least one legitimate
evaluator-private target is registered:

- a verified degradation/fault/anomaly event or interval; or
- a verified window-level anomaly target suitable for window AP/AUROC/FAR/TPR.

Outcome-target eligibility is separate from mechanics completion. At least one
eligible external dataset is necessary but not sufficient: the external
DataPort runtime, sequence builder, evaluator binding, and a candidate-specific
horizon/budget schedule must also be implemented and frozen in a new protocol
version. The current Graph runner is Paderborn-specific, so it is not reused by
changing only a file path.

## Historical provider-free audit

Do not invoke the scheduler with this protocol. The following historical
command shape is intentionally no longer accepted:

```bash
python scripts/schedule_graph_cross_dataset_replay.py \
  --dry-run \
  --protocol paper/experiments/graph_cross_dataset_replay_protocol_v1.yaml
```

It fails at protocol validation because v1 is superseded. Use the v2 default
for the current provider-free eligibility audit:

```bash
python scripts/schedule_graph_cross_dataset_replay.py \
  --dry-run \
  --require-eligible
```

The v2 strict form exits 3 while no legal external outcome target exists.

## Reporting boundary

P2-E8 effects are reported per external dataset and are never pooled across
datasets. All scheduled failures remain in their assigned arm denominators.
Until a complete matched cohort is accepted, no cross-dataset validity,
external validity, Graph transfer, event-F1, detection-delay, or task-
performance claim is supported.
