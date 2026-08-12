# CORE.md — Graph-guided PHM Agent / Paper 2

Status: **Repository authority**  
Effective date: 2026-08-12  
Paper repository: `liq22/P02_agent_langraph`  
Reusable implementation source: `PHMbench/PHMGA`

## Scientific question

Does a compact PHM decision graph improve long-horizon tool use, state transitions, failure recovery, grounded completion, and resource efficiency under a common PHM-Agent Benchmark?

## Central hypothesis

With provider model, tasks, tools, numerical experts, budgets, episodes, and evaluator fixed, a graph-guided policy improves rollout stability by making decision state, branch selection, replanning, and recovery explicit.

## Repository responsibility

This repository owns:

```text
Paper 2 scientific question and manuscript
compact PHM decision graph
GraphDecisionAgent and reactive comparison policy
state-transition and replanning analysis
matched B3-versus-B5 experiments and graph ablations
```

It does not own benchmark tasks, data, tools, budgets, RunBundle, evaluator, numerical PHM operators, a general research scheduler, Canvas/Web/Tauri, or a graph database.

## Shared benchmark dependency

Paper 2 consumes the exact benchmark objects:

```text
TaskSpec
Observation
CanonicalAction
BudgetSpec
RolloutEvent
RunBundle
SevenAxisEvaluator
```

The graph chooses actions over this interface. It cannot change task semantics, hidden targets, tool behavior, budget accounting, or scoring.

## Phase-1 scope

```text
cold-start fault diagnosis
normal-only unsupervised anomaly detection
online/replay monitoring stress task
continuous vibration time series
```

RUL, maintenance decisions, mixed-modal main experiments, and production IoTDB are outside the active paper.

## Compact decision graph

```text
orient → acquire → analyze → model → submit
                     ↘ recover ↗
```

Formal states:

```text
orient
acquire
analyze
model
recover
submit
```

Each Agent turn records exactly one decision state. A failure moves the policy to `recover`; recovery must select a materially changed action or parameter before returning to the main path.

## Primary comparison

```text
B3 GenericLLMToolAgent / reactive sequential policy
vs
B5 GraphDecisionAgent
```

Fix provider model/version, provider route, task/episode order, tool schemas, numerical experts, temperature, seeds, hard budgets, RunBundle, and evaluator. Vary only the decision-graph policy.

## Graph-specific secondary metrics

```text
state-transition validity
distinct-state coverage
branch count
replan count
graph loop ratio
recovery-path length
premature-submit transitions
```

These are secondary. The benchmark seven-axis metrics and task outcomes remain primary.

## Allowed ablations

```text
full graph
remove explicit recover state
remove task-dependent branch selection
remove state-conditioned tool exposure
replace graph with reactive sequential policy
remove replanning after tool failure
```

Typed validation stays enabled in every arm.

## Release gates

Paper 2 becomes result-bearing only when:

1. B3/reactive and B5 use identical benchmark/provider settings;
2. every B5 turn records a valid decision state;
3. all failures and recovery paths remain in the RunBundle;
4. both core tasks have repeated real-data runs;
5. monitoring provides long-horizon and recovery stress cases;
6. graph ablations isolate graph components;
7. no mock result supports a performance claim;
8. repository scheduler, UI, Canvas, Tauri, hash, receipt, or ledger machinery does not enter the scientific method.
