# CORE — GraphDecisionAgent (Paper 2)

**Status:** active authority  
**Repository:** `liq22/P02_agent_langraph`  
**Shared benchmark:** `liq22/phm-agent-benchmark`  
**Current method profile:** persistent decision state + state-dependent tool visibility  
**Updated:** 2026-09-07

## 1. Scientific position in the three-paper program

Paper 0 fixes the PHM world and evaluator. Paper 2 changes the decision-control factor used by a matched Generic Agent.

Let

$$
\pi(a_t\mid o_{\le t};M,H,K,G)
$$

be the Agent policy. Paper 2 compares

$$
\pi_{\mathrm{reactive}}(M,H,K=K_0,G=\varnothing)
\quad\text{with}\quad
\pi_{\mathrm{graph}}(M,H,K=K_0,G=\mathcal G),
$$

under the same Benchmark task, data-release sequence, tools, model/provider condition, budget, run policy, and evaluator.

The benchmark must run without GraphDecisionAgent installed. Paper 2 does not redefine `TaskSpec`, DataPort semantics, `CanonicalAction`, Budget, Rollout, or task metrics.

## 2. Research question

> **Does explicit persistent graph control improve long-horizon PHM task performance or rollout stability relative to the same reactive Generic Agent under a matched benchmark condition?**

The paper is not about using LangGraph as a software library. A workflow graph alone is not the contribution.

## 3. Scientific object

The method is library-independent:

$$
\mathcal G=(V,E,s_0,\phi,\psi),
$$

where

- $V$ is a compact PHM decision-state set;
- $E$ is the legal state-transition relation;
- $s_0$ is the initial state;
- $\phi$ maps public observations and current state to the next state;
- $\psi$ maps state and public context to a Benchmark `CanonicalAction`.

The current treatment jointly adds

```text
1. an explicit current-state policy suffix / persistent decision context;
2. state-dependent visibility over the same global Benchmark tool schemas.
```

The main treatment must therefore be described as a **joint graph-control intervention**. It is not a pure topology effect unless a registered mechanism experiment separates state context from tool filtering.

## 4. Base and dynamic profiles

The declared graph contains eight named states:

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

The current base-v6 formal profile reaches six states:

```text
Inspect
Hypothesize
Analyze
Check
Recover
Submit
```

`Monitor` and `Revise` belong to a separate dynamic profile driven by a declared public operating-condition event. A base-v6 result must not be described as dynamic monitoring/replanning when those states are unreachable in that condition.

The dynamic profile does not reveal a hidden fault label, onset, severity, or evaluator target. It tests response to a public condition change and observable action history.

## 5. Primary comparison

```text
Control:   B3 matched Sequential/Reactive Generic Agent
Treatment: M2 same Generic Agent + joint graph control
```

Fix:

```text
backbone model and provider/runtime condition
generic prompt information outside graph state
TaskSpec and dataset split
released data sequence
global tool and numerical-expert catalog
budget
temperature / seed / run policy
evaluator and statistical unit
```

The graph may change current-state context and which existing tool schemas are visible at a step. It must not edit tool outputs, access private targets, add treatment-only numerical experts, or choose an action outside the Benchmark boundary.

## 6. What Paper 2 must establish

### P2-C1 — Persistent decision control

**Claim.** Explicit state preserves useful PHM decision context across a long rollout.

**Evidence.** Matched reactive/graph cohorts and a no-persistent-state condition. Task performance remains primary; state-transition traces explain the mechanism.

### P2-C2 — Observation-conditioned revision

**Claim.** Graph control can redirect an unproductive PHM decision path when a later public observation or declared condition contradicts the current working state.

**Evidence.** Dynamic-profile runs and no-revision/no-replanning ablations. Natural public data/decision conditions are preferred over artificial software-error injection.

### P2-C3 — Mechanism attribution

**Claim.** Any graph-control effect is associated with persistent state, tool visibility, or their combination.

**Evidence.** The full joint intervention is the main treatment. State-only and filtering-only conditions are required before attributing an effect specifically to topology or one component.

### P2-C4 — Horizon-dependent utility

**Claim.** Persistent control should matter more when the rollout is long enough for memory, revision, and repeated work to accumulate.

**Evidence.** Short/medium/long replay analysis or an equivalent registered horizon experiment using the same task condition.

## 7. Registered task scope

```text
primary setting: ordered replay / long-horizon monitoring
auxiliary: cold-start fault diagnosis
auxiliary: unsupervised anomaly detection
```

The current replay task uses the Benchmark's assigned-window metric contract. Event-F1 and detection delay are not claimed without a dataset protocol that supplies the required event-time annotations.

RUL is outside the first paper.

## 8. State and transition record

The method may retain only public decision state:

```text
current state
released sample/window handle
selected public artifact references
working public hypothesis summary
last action/result status
remaining budget
public condition event when registered
```

Each transition should be reconstructable from the canonical rollout through:

```text
from_state
to_state
public trigger
selected CanonicalAction
transition validity / reason code
```

Hidden provider chain-of-thought is not required and is not an official metric.

## 9. Main experiments

```text
P2-E1  reactive Generic vs full graph-control treatment
P2-E2  no persistent state
P2-E3  no observation-conditioned branch/revision
P2-E4  no replanning
P2-E5  state-only / filtering-only mechanism separation when feasible
P2-E6  replay-horizon analysis
P2-E7  independent repeated reliability/cost cohort
```

Do not add new states merely because P2-E1 is incomplete.

## 10. Metrics

Use the Benchmark task-primary metric for each task. Paper-2 secondary diagnostics explain the control effect:

```text
grounded completion
state-transition distribution
branch revisitation
repeated actions / loops
decision revision and recovery
premature submission
data/tool/model/LLM/time cost
repeat-run variation
```

Graph-state metrics cannot replace PHM task performance.

## 11. Current empirical boundary

As of 2026-09-07, the provider-free graph scaffold, base/dynamic profiles, and experiment machinery exist, but there is **no accepted provider-bound Graph-minus-Generic treatment-effect cohort** and no accepted reliability effect.

The next scientific milestone is P2-E1 on the completed Generic baseline. Dynamic `Monitor`/`Revise` language must remain scoped to the dynamic experiment until formal runs actually exercise those states.

## 12. Repository responsibility

`P02_agent_langraph` owns:

```text
GraphDecisionAgent adapter
graph state and transition policy
state-conditioned tool visibility
method-specific ablations
Paper-2 experiments, analysis, figures, and manuscript
```

It does not own the Benchmark Runner, DataPort, task definitions, numerical operators, or official evaluator.

The historical PHMGA/AutoResearch/Canvas/project-management material is reference-only and must not redefine the Paper-2 method.

## 13. Non-goals

```text
general-purpose LangGraph platform
learned graph topology as the first-paper treatment
new Benchmark Runner or Evaluator
multi-agent scheduling
graph database / UI contribution
RUL in the first paper
artificial software-failure injection as the main experiment
large defensive state machines
mandatory hidden reasoning capture
```

This file overrides historical Goal, UI, workflow, and review narratives when they conflict with the current Paper-2 question or treatment definition.
