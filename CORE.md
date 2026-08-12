# CORE — GraphDecisionAgent (Paper 2)

**Status:** active authority  
**Repository:** `liq22/P02_agent_langraph`  
**Shared benchmark:** `liq22/phm-agent-benchmark`  
**Updated:** 2026-08-12

## 1. Authority

```text
CORE.md
  > graph / experiment / model protocol files
  > public method and adapter documents
  > README.md
  > AGENTS.md / CLAUDE.md
  > Goal, generated graph, reviewer, handoff, UI, and historical manuscript files
```

This document freezes the Paper 2 scientific object. Model names, dataset splits, graph hyperparameters, seeds, and run paths belong in protocol files.

## 2. One-sentence definition

Paper 2 studies whether a compact, observation-conditioned PHM decision graph improves fault/anomaly decisions in long-horizon rollouts relative to a matched sequential or reactive agent.

## 3. Scientific question

> Under matched PHM tasks, data, tools, model profile, budget, and evaluator, does graph-structured decision control improve task performance and produce more stable and efficient long-horizon PHM rollouts?

The paper is not about AutoResearch node governance, manuscript scheduling, Canvas/UI systems, claim-evidence registries, or a general LangGraph platform.

## 4. Repository responsibility

`P02_agent_langraph` owns both Paper 2 authority and the active GraphDecisionAgent implementation:

```text
GraphDecisionAgent adapter
library-independent decision-graph representation
state variables and transition semantics
observation-conditioned branch policy
decision revision and replanning
method-specific operator or state extensions
ablations
experiments, analysis, figures, tables, and manuscript
```

The historical `PHMbench/PHMGA` submodule may remain as reference material during migration but is not the active Paper 2 authority or required runtime. Do not create a fifth repository merely for the first GraphDecisionAgent implementation.

Paper 2 imports, without redefining:

```text
TaskSpec
DataPort boundary
Observation
CanonicalAction
operator and numerical-expert contracts
Budget
RolloutEvent
Submission
Evaluator interface and task metrics
```

The benchmark must run without GraphDecisionAgent installed.

## 5. Graph object

The scientific object is library-independent:

$$
\mathcal G=(V,E,s_0,\phi,\psi),
$$

where:

- $V$ is a small set of PHM decision states;
- $E$ is the legal transition relation;
- $s_0$ is the initial state;
- $\phi$ maps benchmark observations and current graph state to candidate transitions;
- $\psi$ selects the next canonical action or terminal submission.

LangGraph may implement this object, but the paper contribution is not “using LangGraph.”

## 6. Primary task scope

```text
primary: online/replay monitoring and streaming fault/anomaly diagnosis
auxiliary: cold-start fault diagnosis
auxiliary: unsupervised anomaly detection
```

The graph is expected to be most useful when the agent must retain state, revisit hypotheses, react to new data, and make a time-ordered sequence of decisions. RUL is excluded from the first paper.

## 7. Minimal decision graph

A compact Phase-1 topology is:

```text
ORIENT
→ QUERY
→ ANALYZE
→ DECIDE
→ SUBMISSION_CHECK
→ SUBMIT
```

Observation-conditioned edges may return to:

```text
QUERY
ANALYZE
DECIDE
```

A dedicated `REVISE` or `RECOVER` state may be used when the current hypothesis or branch is contradicted by new data. Keep the graph small; do not create one node per function, schema field, or hypothetical exception.

## 8. State and transition contract

A graph state minimally contains:

```yaml
state_id:
benchmark_observation_ref:
selected_artifact_refs:
working_hypotheses:
last_action_status:
remaining_budget:
data_condition_summary:
```

A transition minimally records:

```yaml
from_state:
to_state:
trigger:
selected_action:
reason_code:
```

The agent may additionally emit a private or shareable `reasoning_trace` when the runtime explicitly provides it and storage is permitted. Hidden provider chain-of-thought is not required, reconstructed, or used as a mandatory benchmark field. Formal scoring relies on task outputs and observable state/action/result events; reasoning traces are optional qualitative material.

## 9. Meaning of fault, anomaly, and recovery

The primary “fault” in Paper 2 is an equipment or data condition represented through data-factory, not an artificially injected LLM action error.

Primary conditions include:

```text
fault or anomaly onset in a replay stream
changing fault signature
operating-condition shift
noisy, low-quality, or temporarily uninformative windows
missing or delayed bounded windows when present in the data protocol
new observations that contradict the current diagnosis hypothesis
```

Decision recovery means revising the graph state, data query, operator choice, or diagnosis hypothesis after the observed data make the current path unproductive.

Natural tool or backend errors are retained in rollouts, but invalid-action injection, schema-breaking calls, and exhaustive software-failure catalogues are not the main Paper 2 experiment.

## 10. Agent conditions

Primary comparison:

```text
B2 ScriptedHeuristicAgent
B3 Sequential/Reactive Generic LLM Agent
M2 GraphDecisionAgent
```

The strongest causal comparison is `B3` versus `M2`. Fix:

```text
backbone model and provider profile
prompt information content
TaskSpec and data split
tool and operator surface
budget profile
temperature and run policy
evaluator methods
```

The principal varied factor is persistent graph-structured decision control.

## 11. Primary hypotheses

### H1 — task performance

GraphDecisionAgent improves the task-appropriate primary metric, especially event-level streaming diagnosis, while respecting the same budget.

### H2 — long-horizon completion

The graph increases valid completion and submission rates on long replay episodes.

### H3 — branch selection and decision revision

Observation-conditioned transitions reduce unproductive branch persistence and improve recovery after new data contradict the current hypothesis.

### H4 — stability and cost

The graph reduces repeated work and improves repeated-run stability or the task-performance–cost Pareto frontier.

Task accuracy, macro-F1, AUPRC, event-F1, false alarms, and detection delay are primary. Graph-state and rollout metrics are secondary explanatory outcomes rather than substitutes for PHM performance.

## 12. Metrics

### Primary task metrics

```text
diagnosis: accuracy / balanced accuracy / macro-F1
anomaly: AUPRC / AUROC / false-alarm rate
streaming: event-F1 / detection delay / false-alarm rate
```

### Secondary rollout diagnostics

```text
completion and submission
state-transition validity
branch revisitation
repeated-action and loop incidence
premature submission
decision-revision success and steps
budget used before and after revision
trajectory length
data, operator, model, token, latency, and cost use
```

Do not compare against a handcrafted gold path. Multiple graph paths can be valid.

## 13. Ablation Track

Use a small set of mechanism-focused ablations:

```text
A0 full GraphDecisionAgent
A1 no explicit REVISE/RECOVER edge
A2 fixed transitions without observation-conditioned branch selection
A3 no replanning after contradictory or low-quality data
A4 no persistent graph state
A5 reactive agent with matched prompt content but no graph
```

Keep the benchmark task, tool surface, model, budget, typed guard, and evaluator fixed.

## 14. Run ladder

```text
first: one-seed real-data end-to-end run
then: small repeated pilot on the primary replay task
finally: repeated formal comparison selected by the statistical plan
```

A one-seed run establishes the path only. It cannot support stability claims.

## 15. Paper 2 contribution

Paper 2 contributes:

1. a compact, library-independent PHM decision-graph policy aligned with a canonical agent benchmark;
2. observation-conditioned state transitions for long-horizon fault/anomaly diagnosis;
3. explicit decision revision when data contradict the current branch;
4. a matched comparison against sequential/reactive control using task performance as the primary outcome;
5. secondary analysis of completion, branch behavior, stability, and cost.

LangGraph, UI dashboards, graph databases, project schedulers, and review workflows are implementation choices rather than scientific contributions.

## 16. Release gates

Paper 2 results require:

```text
GraphDecisionAgent emits benchmark CanonicalAction values;
graph state cannot access hidden targets or evaluator internals;
sequential and graph conditions use matched model, data, tools, budget, and evaluator;
the replay task preserves temporal order and prevents future-window access;
state transitions are reconstructable from saved rollout events;
formal recovery claims concern declared equipment/data conditions or hypothesis revision;
task-performance claims use registered evaluators;
failed and partial episodes remain in denominators;
```

## 17. Non-goals

```text
general-purpose LangGraph platform
AutoResearch or manuscript-node governance
Canvas, Web, Tauri, or dashboard contribution
multi-agent scheduling
full graph database
RUL in the first paper
invalid-action injection as the main experiment
exhaustive defensive state machines
mandatory chain-of-thought capture
hash/checksum/digest/receipt/ledger machinery
```

## 18. Conflict resolution

This file supersedes P02 narratives centered on AutoResearch workflow governance, reviewer-response closure, PHMGA/Vibench provider gates, paper-node lifecycle, submission packaging, and UI/Canvas projections. Useful implementation may remain after direct review, but Paper 2's active object is the benchmark-facing GraphDecisionAgent and its effect on PHM task performance and observable rollout behavior.
