# CORE — GraphDecisionAgent (Paper 2)

**Status:** active authority
**Repository:** `liq22/P02_agent_langraph`
**Shared benchmark:** `liq22/phm-agent-benchmark`
**Updated:** 2026-09-03

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

Paper 2 studies whether an explicit eight-state PHM decision policy improves registered task outcomes and observable long-horizon rollout behavior relative to the same Generic LLM tool agent without graph guidance.

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

Explicit state machines and state-conditioned LLM control are established prior work, including StateFlow. Paper 2 therefore does not claim novelty for representing an agent as a graph. Its testable contribution is the matched PHM intervention that jointly adds a current-state policy suffix and state-specific filtering of the same global Benchmark tool schemas, together with task-primary and mechanism-focused evaluation.

## 6. Registered task scope

```text
P2-E1 core: cold-start fault diagnosis and unsupervised anomaly detection
P2-E1 replay stress: ordered online/replay monitoring
P2-E2--E7 dynamic profile: ordered replay with a public operating-condition-change event
```

The active v6 P2-E1 profile has no `public_condition_event`; Monitor and Revise are therefore unreachable and support no dynamic-revision claim. Observation-conditioned Monitor/Revise execution belongs to the separate dynamic-v3 profile. Its task-primary endpoint remains target-adverse assigned-window Average Precision, not event detection. RUL is excluded from the first paper.

## 7. Minimal decision graph

A compact Phase-1 topology is:

```text
Inspect
Hypothesize
Analyze
Check
Monitor
Revise
Recover
Submit
```

The base-v6 profile uses the registered 50-edge relation while omitting public condition events, so only Inspect, Hypothesize, Analyze, Check, Recover, and Submit are reachable. The separate dynamic-full profile uses its registered 33-edge observation-conditioned relation. Recover follows a recorded action failure; Monitor and Revise respond only to an explicitly released public event, never to a hidden target or an event inferred from signal values. Keep the graph small; do not create one node per function, schema field, or hypothetical exception.

## 8. State and transition contract

A graph decision is derived immediately before each LLM action from the public task and canonical trajectory. Its observable contract minimally contains:

```yaml
decision_state:
public_task_and_observation_context:
canonical_public_trajectory_prefix:
last_recorded_action_status:
remaining_budget:
optional_public_condition_event:
state_specific_visible_tool_schemas:
```

A transition minimally records:

```yaml
from_decision_state:
to_decision_state:
public_trigger:
selected_canonical_action:
transition_validity:
```

The selected state is written to the observable trajectory step. The graph adds a state suffix to the unchanged Generic base policy and filters only which schemas from the unchanged global tool catalog are visible at that step. It does not edit tool outputs or supply an action on behalf of the LLM. Hidden provider chain-of-thought is not required, reconstructed, or used as a benchmark field.

## 9. Meaning of fault, anomaly, and recovery

The primary “fault” in Paper 2 is an equipment or data condition represented through data-factory, not an artificially injected LLM action error.

The registered dynamic-v3 condition is:

```text
one opaque public `operating_condition_change` event released at its registered sequence index
ordered bounded windows whose evaluator-private anomaly targets remain hidden
public action failures that may route to Recover
```

The public condition identifier does not reveal a fault/anomaly onset, label, severity, or evaluator target. Event-F1, detection delay, time-to-fault detection, changing-fault-signature, and missing-window claims are outside this estimand. Decision recovery means making a corrected observable action after a recorded failure or replanning after the registered public event.

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
Generic base prompt and non-graph task information
TaskSpec and data split
tool and operator surface
budget profile
temperature and run policy
evaluator methods
```

The principal varied factor is the joint graph-guidance intervention: an explicit current-state policy suffix plus state-specific visibility over the same global tool schemas. The study does not identify these two components separately unless a future registered factorial experiment does so.

## 11. Primary hypotheses

### H1 — task performance

GraphDecisionAgent improves the registered task-primary metric while respecting the same budget: diagnosis Macro-F1, completion-adjusted anomaly Average Precision, or target-adverse assigned-window replay Average Precision, depending on the cohort.

### H2 — long-horizon completion

The graph increases valid completion and submission rates on long replay episodes.

### H3 — branch selection and decision revision

Observation-conditioned transitions reduce unproductive branch persistence and improve recovery after new data contradict the current hypothesis.

### H4 — stability and cost

The graph reduces repeated work and improves repeated-run stability or the task-performance–cost Pareto frontier.

Graph-state and rollout metrics are secondary explanatory outcomes rather than substitutes for PHM performance. Event-F1 and detection delay are not registered outcomes for the current P2 protocols.

## 12. Metrics

### Primary task metrics

```text
diagnosis: accuracy / balanced accuracy / macro-F1
anomaly primary: completion-adjusted average precision
replay primary: target-adverse assigned-window average precision
secondary task diagnostics: submitted-only AP, AUROC, false-alarm rate, true-positive rate, score coverage
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
full GraphDecisionAgent
no recovery/revision edge
no observation-conditioned branching
no persistent graph state
no replanning
ReactiveSequentialAgent with the unchanged Generic behavior and no graph guidance
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

1. a compact, library-independent eight-state PHM decision policy aligned with canonical Benchmark actions;
2. a matched joint intervention combining a current-state policy suffix with state-specific filtering of an otherwise unchanged tool catalog;
3. a separately registered observation-conditioned operating-change profile and mechanism ablations;
4. matched comparisons against the unchanged Generic sequential/reactive control using registered PHM task performance as the primary outcome;
5. secondary analysis of completion, state transitions, recovery, repetition, stability, latency, and cost.

LangGraph, UI dashboards, graph databases, project schedulers, and review workflows are implementation choices rather than scientific contributions.

## 16. Release gates

Paper 2 results require:

```text
GraphDecisionAgent emits benchmark CanonicalAction values;
graph state cannot access hidden targets or evaluator internals;
sequential and graph conditions use matched model, data, tools, budget, and evaluator;
the replay task preserves temporal order and prevents future-window access;
state transitions are reconstructable from saved rollout events;
formal dynamic claims concern only the registered public operating-condition-change event, and recovery claims use observable recorded failures/actions;
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
