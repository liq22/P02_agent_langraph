# GraphDecisionAgent — Paper 2

> **Authority:** read [`CORE.md`](CORE.md) first. It defines the graph object, primary task, comparison, and data-condition recovery semantics.

Paper 2 asks whether a compact PHM decision graph improves streaming fault/anomaly diagnosis relative to a matched sequential or reactive agent.

```text
same PHM task, data, tools, model, budget, and evaluator
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
Sequential/Reactive Agent   GraphDecisionAgent
```

## Scientific object

The graph is a library-independent policy scaffold:

```text
ORIENT
→ QUERY
→ ANALYZE
→ DECIDE
→ SUBMISSION_CHECK
→ SUBMIT
```

Observation-conditioned edges may return to `QUERY`, `ANALYZE`, or `DECIDE` when new data contradict the current hypothesis. LangGraph may be used as an implementation, but “using LangGraph” is not the contribution.

## Repository role

This repository owns both Paper 2 authority and the active GraphDecisionAgent runtime. The historical `PHMbench/PHMGA` submodule may be inspected for reusable code but is not the active authority. No additional runtime repository is required for Phase 1.

Paper 2 imports the shared benchmark's:

```text
TaskSpec
Observation
CanonicalAction
Budget
RolloutEvent
Submission
operator/model contracts
Evaluator interface and task metrics
```

The benchmark does not import GraphDecisionAgent.

## Task priority

```text
Primary: online/replay monitoring and streaming fault/anomaly diagnosis
Auxiliary: cold-start fault diagnosis
Auxiliary: unsupervised anomaly detection
```

Task performance—accuracy, macro-F1, AUPRC, event-F1, false alarms, and delay—is primary. Graph-state, branch, completion, and cost measures explain the mechanism.

## Meaning of recovery

The main “fault” is an equipment or data condition exposed by data-factory, not an injected invalid LLM action.

Graph decision revision may respond to:

```text
fault/anomaly onset
operating-condition shift
noisy or uninformative windows
missing/delayed windows declared by the data protocol
new observations that contradict the current diagnosis branch
```

Natural tool errors remain in rollouts, but exhaustive software-failure injection is not the Paper 2 center.

## Primary comparison

```text
B2 ScriptedHeuristicAgent
B3 Sequential/Reactive Generic LLM Agent
M2 GraphDecisionAgent
```

The main causal comparison is `B3` versus `M2`, with matched model, prompt information content, data, tools, budget, run policy, and evaluator.

## Execution order

```text
1. make one real-data, one-seed replay episode run sequentially
2. run the matched GraphDecisionAgent episode
3. verify temporal order and no future-window access
4. inspect task outcome and graph-state transitions
5. add a small repeated pilot
6. run ablations and formal comparisons selected by the statistical plan
```

Optional agent-emitted reasoning traces may be stored when permitted. Hidden provider chain-of-thought is not a required field or official score.

## Historical workspace

The current generic AutoResearch/Canvas/project-management material is historical scaffolding rather than the active Paper 2 identity. See [`SUPERSEDED.md`](SUPERSEDED.md).
