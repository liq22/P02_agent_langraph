# Graph-Guided PHM Agents for Long-Horizon Diagnostic Rollouts

## Abstract

Reactive tool-use agents can repeat analyses, lose track of unresolved hypotheses, or submit prematurely during long PHM workflows. This paper studies a graph-guided PHM agent whose implementation defines eight explicit decision states—Inspect, Hypothesize, Analyze, Check, Monitor, Revise, Recover, and Submit—over the same Benchmark Generic LLM base and computational tools as the control. The control is Benchmark Generic (Reactive-equivalent), implemented by `ReactiveSequentialAgent` with zero behavior overrides. The active v6 primary registers no `public_condition_event`, so Monitor and Revise are unreachable there and only the six base-route states can be observed. A separate Generic-base dynamic-v3 profile makes observation-conditioned Monitor/Revise routing executable and registers target-adverse assigned-window Average Precision as its primary endpoint. Its unchanged 10-cell v2 Mock mechanics gate is accepted, while formal coverage is 0/240. The evaluation holds the base prompt, model, runtime, data, tools, numerical experts, budget, evaluator, and episode order fixed. The registered core endpoints are diagnosis Macro-F1 and completion-adjusted anomaly Average Precision; replay monitoring uses target-adverse assigned-window Average Precision as its primary endpoint and treats completion, recovery, stability, latency, and cost as explanatory outcomes. Current accepted evidence establishes matched execution mechanics and a provider-free Scripted reference, while the Generic-versus-Graph treatment cohorts remain unexecuted.

## 1. Introduction

Long diagnostic rollouts require more than choosing individually valid tools. An agent must retain its current hypothesis, decide whether a result supports or contradicts that hypothesis, avoid repeating an unproductive operation, recover from errors, and recognize when evidence is sufficient for submission. A purely reactive policy may encode these decisions implicitly in conversation history, leaving state transitions implicit and harder to audit.

This paper isolates the effect of explicit decision structure. The control is the Benchmark Generic policy; `ReactiveSequentialAgent` is its zero-behavior-override wrapper and is therefore Reactive-equivalent rather than a separate learned or prompted agent. `GraphDecisionAgent` is derived directly from the same Generic base and adds the eight-state decision control. Neither production arm imports P1 runtime code. No additional data, operator, model expert, prompt budget, or evaluator capability is introduced. Graph states are recorded in the shared trajectory and must affect actual next-action selection.

GraphDecisionAgent is deliberately a finite-state control policy; state-machine workflow structure is not the claimed novelty. The research object is a registered matched PHM intervention: deterministic state derived only from public Benchmark trajectory fields, state-specific visibility over the unchanged tool catalog, a zero-override Generic control, condition-event and topology ablations, and task scoring by an independent evaluator. The graph constrains high-level state and legal actions while the shared LLM policy still chooses the within-state tool trajectory.

The primary hypothesis is that graph guidance improves replay-monitoring task performance under the shared fixed action budget. The primary estimand is $\Delta^{\mathrm{replay}}_{AP}=AP^{\mathrm{Graph}}-AP^{\mathrm{Generic}}$ over 24 exact episode pairs (eight rotation-0 bearings crossed with three seeds), stored as `estimate.online_replay_monitoring.task.average_precision` in the paired result. The frozen target-adverse missing-score policy keeps all 72 assigned replay windows per arm in the AP population: an omitted positive is a miss and an omitted negative receives an adverse false-alarm rank. The 95% interval uses 2,000 bearing-clustered paired bootstrap resamples. The accepted analysis will report the estimate and interval without a significance threshold or non-inferiority margin. Grounded completion, recovery, repeated actions, budget exhaustion, latency, and cost are prespecified explanatory outcomes. Diagnosis Macro-F1 and anomaly completion-adjusted AP are registered task-primary core outcomes reported separately from the replay primary.

### 1.1 Contributions

This paper contributes five elements: a compact, library-independent eight-state PHM decision policy aligned with canonical Benchmark actions; a matched intervention that couples a current-state policy suffix with state-specific filtering of an otherwise unchanged tool catalog; a separately registered observation-conditioned operating-change profile with mechanism ablations; a task-primary comparison design against the unchanged Benchmark Generic control under shared data, tools, budgets, and evaluators; and a prespecified secondary analysis of completion, state transitions, recovery, repetition, stability, latency, and cost. Together, these elements make graph guidance an observable and falsifiable intervention rather than a workflow-framework choice.

## 2. Related Work

ReAct interleaves reasoning and environment actions so an agent can update plans and handle exceptions [@yao2023react], while Reflexion uses linguistic feedback and episodic memory to influence subsequent trials [@shinn2023reflexion]. AgentBench shows that long-horizon reasoning and decision-making remain common failure sources across interactive environments [@liu2023agentbench]. The registered object here retains the Generic ReAct-style base but makes the treatment's current decision state, legal transitions, and state-specific tool visibility explicit in the shared rollout.

TimeART trains a tool-using model on expert time-series tool trajectories [@wu2026timeart], while TimeSage-MT evaluates structured, skill-guided and code-enabled agents over 240 multi-turn tasks across eight domains [@kong2026timesagemt]. PHMForge further motivates execution-trace evaluation in PHM-oriented tool environments [@das2026phmforge]. The present comparison fixes the Generic base prompt and every computational capability and varies only the registered eight-state control.

Industrial agents provide two closer control-structure references. ReActXen augments a ReAct executor with Review, Reflect, and Distillation components plus a Tiny Trajectory Store for structured SCADA queries [@rayfield2025reactiot]. CodeReAct embeds executable Python in a Thought--Action--Observation loop over structured maintenance records and evaluates outer-loop reflection and adaptive temperature [@zhou2026codereact]. P2 introduces none of those treatment-only roles or executable capabilities: `GraphDecisionAgent` remains one Generic-derived policy whose added state is computed from the public Benchmark trajectory.

StateFlow is the direct state-machine precedent. It models LLM task solving as a state machine, separates process grounding through states and transitions from actions within a state, and permits rule- or LLM-selected transitions over context history [@wu2024stateflow]. P2 therefore does not claim state-machine workflow formalism as new. It studies a narrower experimental question in PHM: whether deterministic public-rollout state and state-specific tool visibility change independently evaluated task outcomes when the Generic base, computational world, budget, and episode order are matched.

SPIRAL is the closest verified search-based planning comparison. It formalizes tool-use planning as state-space search and places Planner, Simulator, and Critic roles inside an MCTS loop; its Simulator predicts plausible next observations and its Critic supplies reflective feedback [@zhang2026spiral]. The P2 graph is a different intervention: it never searches predicted outcomes and adds no simulator, critic, or tree search. Its eight states and legal tool subsets are derived deterministically from actions and observations already recorded by the shared Benchmark environment.

Table 1 freezes these source-bounded distinctions. It is a structural comparison, not a numerical ranking, and imports no reported result from another task. The versioned table asset is `paper/assets/tables/graph_closest_work.md`.

| Work | Documented decision structure | Documented state or grounding source | Relation to the registered P2 contrast |
|---|---|---|---|
| ReAct [@yao2023react] | interleaved reasoning and environment actions | model trajectory and returned observations | P2 retains the Generic base and makes treatment state plus legal tool visibility explicit |
| ReActXen [@rayfield2025reactiot] | ReAct executor with Review, Reflect, and Distillation components and a Tiny Trajectory Store | structured SCADA query results plus curated in-context trajectories | P2 uses one Generic-derived treatment and no treatment-only auxiliary agent or trajectory store |
| StateFlow [@wu2024stateflow] | finite-state-machine-derived workflow whose states execute predefined prompt, model, or tool output functions | current state abstracts cumulative context history; rules or an LLM select transitions | direct formalism precedent; P2 does not claim state-machine workflows as novel and instead isolates public-rollout state plus state-specific tool visibility in a matched PHM evaluation |
| CodeReAct [@zhou2026codereact] | executable Python inside a Thought--Action--Observation loop with outer-loop reflection | structured Business Objects, analytic functions, alerts, and work orders | P2 adds an eight-state tool-visibility controller, not executable Python or adaptive model control |
| SPIRAL [@zhang2026spiral] | Planner/Simulator/Critic roles embedded in MCTS | Simulator-predicted observations and Critic feedback guide search | P2 derives state from observed Benchmark rollout events and performs no outcome simulation or tree search |
| PHMForge [@das2026phmforge] | PHM-oriented tool orchestration and execution traces | heterogeneous scenario-specific tools and data | P2 holds the Generic Benchmark world fixed and varies only graph control |
| GraphDecisionAgent (this work) | eight deterministic states with declared legal transitions and state-specific views of the unchanged tool catalog | public actions, execution results, errors, budget, and optional public condition events in the canonical rollout | active v6 exposes six reachable base-route states; dynamic-v3 retains an accepted 10-cell Mock mechanics gate, a runner-ready provider-free schedule, and formal coverage 0/240 |

## 3. Graph-Guided Policy

The implemented policy uses eight states. Inspect exposes only bounded data tools. Hypothesize exposes catalog-level operator/model discovery. Analyze exposes signal operators and model schemas. Check exposes numerical prediction and verification actions. Monitor represents a registered public equipment- or data-condition observation, and Revise replans after such an observation. Recover follows a recorded error and exposes the tools needed for one corrected call. Submit exposes only the terminal tool. State is derived from the public trajectory before each decision and is written to the resulting `TrajectoryStep`; it therefore changes both the model's policy context and the set of callable tools. The current registered v6 primary supplies no `public_condition_event`, so Monitor/Revise are unreachable, zero visitation is valid, and this cohort supports no dynamic-revision claim. Its declared transition relation is the 50-edge base-v6 relation used for primary treatment-integrity validation. Observation-conditioned behavior is isolated in a separately preregistered dynamic-full profile with its own 33-edge legal relation; that profile's provider-free mechanics gate is accepted but its formal cohort has not run. The Benchmark owns only generic public-condition event delivery; P02 owns the Graph-state interpretation.

Let $h_t$ be the public trajectory before turn $t$, $g(h_t)$ the deterministic state function, and $\mathcal{T}$ the unchanged shared tool set. The treatment action set is

$$
\mathcal{A}_t^{\mathrm{graph}} = \mathcal{T} \cap \mathcal{A}(g(h_t)),
$$

and its decision is sampled from the same Generic-base model policy as the control:

$$
a_t \sim \pi_\theta(a \mid q,h_t,\mathcal{A}_t^{\mathrm{graph}},g(h_t)).
$$

The Benchmark Generic (Reactive-equivalent) control receives $\mathcal{T}$ without $g$ or the state-specific filter. Thus graph guidance consists of two coupled, predeclared policy operations: exposing the current public decision state in the prompt and restricting the callable schemas to that state's subset. It does not add a computation, prediction, memory store, or private observation.

Transitions are a deterministic function of public trajectory fields: successful tool families, the most recent error, the current ordered replay sample, the number of successful feature calls whose public `source_sample_id` matches that sample, and the set of distinct replay samples with a successful sample-bound prediction. Under the v6 runtime contract, every successful `op.run` result inherits this opaque handle from its source artifact, including chained operator outputs. The same contract linearly interpolates the PSD value at each exact requested low- and high-Hz `band_power` endpoint before trapezoidal integration. The public task observation, tool results, and policy history contain no bearing identifier or target; `bearing_id` exists only in evaluator-side experiment records for split alignment and bearing-clustered inference. Repeating a prediction for one sample, or analyzing a different sample, therefore cannot advance the current sample's graph state. The graph does not read a private target, estimate an unrecorded uncertainty, perform numerical signal processing, or change the shared tool surface. A minimal runtime can implement these transitions directly; dependency on a particular graph framework is not part of the method.

![The shared eight-state topology with distinct legal-transition matrices: the 50-edge base-v6 relation, in which Monitor/Revise are unreachable because the active primary registers no public condition event, and the 33-edge dynamic-full relation whose provider-bound formal cohort has not run.](../assets/figures/graph_policy_states.svg)

### 3.1 State semantics and tool visibility

| State | Public condition | Tool families exposed |
|---|---|---|
| Inspect | current sample has no successful bounded read | `data.*` |
| Hypothesize | signal exists but analysis/model families have not been listed | catalog discovery and summary |
| Analyze | a catalog has been inspected but the core model schema is not yet available, or the current replay sample has fewer than 11 successful feature calls | operator list/schema/run and model schema |
| Check | the core model schema is available without a prediction, or the current replay sample has accumulated 11 successful feature calls | operator/model schema and prediction |
| Monitor | separate dynamic profile only: the current released sample carries a new public `operating_condition_change` pulse | bounded data, operator, and model analysis/prediction tools |
| Revise | separate full dynamic profile only: the next non-error, non-event observation follows Monitor | bounded data, operator, and model analysis/prediction tools |
| Recover | the previous recorded step failed | the tools needed for one corrected data/operator/model call |
| Submit | a core prediction exists, or replay has one successful prediction whose `source_sample_id` matches every ordered sample | terminal `submit` only |

The state is derived from public trajectory fields immediately before an LLM decision. `GraphDecisionAgent.available_tools` then filters the same benchmark schemas using the active state, and the shared runner records an out-of-state tool selection as a recoverable failed action rather than executing it. Either operator-catalog or model-catalog inspection advances Hypothesize to Analyze, so every catalog exposed in that state has a declared successor. For replay, a successful prediction advances to Inspect for the next ordered sample; after the final prediction it advances to Submit. A failed grounded-submission check advances from Submit to Recover so the Agent can correct its supporting artifacts. The graph neither edits a tool result nor supplies an action on behalf of the LLM.

### 3.2 Transition evaluation

Every `TrajectoryStep` stores the decision state used for that action. Transition validity is the fraction of adjacent observed states that belong to the declared transition relation; an episode with no observed state receives 0, while a one-state episode with no illegal transition receives 1. State coverage, per-state step occupancy, per-state episode visitation, Recover visits, repeated actions, grounded completion, and budget exhaustion remain separate measurements; they are not compressed into a graph score. A valid transition does not imply a useful action, which is why task outcomes are primary and rollout diagnostics remain explanatory.

For the non-empty observed state sequence $(s_1,\ldots,s_n)$ and declared edge relation $E$, transition validity is

$$
V_{\mathrm{trans}} =
\begin{cases}
1, & n=1,\\
\frac{1}{n-1}\sum_{t=1}^{n-1}\mathbf{1}[(s_t,s_{t+1})\in E], & n>1.
\end{cases}
$$

An empty sequence receives 0 because it provides no evidence that the treatment entered the runtime. During replay, a successful prediction advances the state to Inspect for the next ordered sample, while the already discovered operator/model catalogs remain public trajectory knowledge. After the final numerical prediction, the state advances to Submit. These rules make cross-window persistence observable without introducing an external graph memory.

For task $q$, episode state sequences $(s_{i1},\ldots,s_{iT_i})$, and declared state $s$, step occupancy and episode visitation are

$$
O_{q,s}=\frac{\sum_i\sum_{t=1}^{T_i}\mathbf{1}[s_{it}=s]}{\sum_i T_i},
\qquad
V_{q,s}=\frac{1}{N_q}\sum_i\mathbf{1}[\exists t:s_{it}=s].
$$

Occupancy is a proportion of recorded decision steps, not wall-clock time. Both diagnostics are reported for all eight executable states, including zero-valued states. Because the registered v6 primary has no `public_condition_event`, zero Monitor/Revise values are expected to remain admissible and must not be interpreted as evidence of dynamic revision.

## 4. Controlled Evaluation

The control and treatment use the identical Benchmark Generic base prompt, model runtime, task instances, tools, numerical experts, budgets, and stochastic seeds. The control is reported as Benchmark Generic (Reactive-equivalent); `ReactiveSequentialAgent` changes no Generic behavior. `GraphDecisionAgent` adds only the registered current-state prompt suffix and state-specific visibility over the same global tool catalog. The only varied factor is whether decision state is implicit/Generic or explicit/graph-guided.

Core diagnosis and anomaly comparisons use the Paderborn bearing dataset [@lessmeier2016conditionMonitoring] with all four bearing-grouped rotations, the sample at metadata-order index $\lfloor 2(n-1)/3 \rfloor$ from each of the 32 held-out bearings, and three paired seeds. These formal records are distinct from the exact midpoint records used during pre-formal endpoint and feature-contract development. Every bounded read contains all 8,192 samples from channel index 2, the bearing-housing vibration column mapped by the public upstream reader; the shared full-rate window contract prevents the material high-frequency aliasing identified by the benchmark sampling audit. Replay stress uses the eight held-out bearings in rotation 0, three ordered windows per bearing, and the same seeds. Fold-level expert/reference fitting and validation selection occur before the matched episodes and are identical across policies; the reported cost comparison therefore covers inference rollouts only. Core episodes have a 33-call budget; replay episodes allow 72 calls, three reads, 50 operator calls, and three model calls. These limits are shared by the Benchmark Generic and Graph arms.

The extension protocols keep the same task-primary hierarchy and acceptance discipline. Dynamic-v3, horizon-v3, Ottawa P2-E8, and reliability P2-E9 all retain assigned windows and failed or partial episodes, use physical-bearing inference where registered, and admit manuscript estimates only from complete accepted cohorts. Their current execution and validation status is reported once in Section 6 and the claim--evidence matrix.

## 5. Tasks and Metrics

Diagnosis and anomaly tasks use the shared Benchmark metrics, including diagnosis accuracy, Macro-F1, ten-bin expected calibration error and calibration coverage, and anomaly submitted-episode AP, completion-adjusted AP, AUROC, false-alarm rate, true-positive rate, full-cohort prevalence, and submitted-subset prevalence. AP requires a positive target, AUROC both classes, false-alarm rate a negative target, and true-positive rate a positive target; out-of-domain values and completion-adjusted AP when AP is undefined are N/A rather than zero. Replay monitoring composes bounded windows into longer episodes. Its primary metric is Average Precision over every protocol-assigned window under `phase1_replay_target_adverse_missing_score_v1`; each arm also reports assigned, submitted, missing, and covered windows. Grounded completion, valid and failed tool calls, Agent decision errors, reference validity, repeated actions and errors, grounded recovery, budget exhaustion, trajectory length, window/operator/model calls, LLM turns, returned scalar values and float64 bytes, latency, and cost are explanatory outcomes. No separate cycle-ratio endpoint is registered: loop behavior is represented by `repeated_action_ratio` and the Graph-only state occupancy, visitation, and transition diagnostics. Every 2,000-resample bootstrap interval reports its valid-replicate count. State-transition validity and coverage describe Graph treatment integrity only. Event-level detection metrics are excluded unless verified event annotations exist, and provider latency remains descriptive because counterbalancing cannot eliminate backend drift.

## 6. Implementation Validation

The accepted P2-E0-v2 real-data Generic-base adapter/world mechanics gate reads the fixed seed-20260808 rotation-0 Benchmark Generic (Reactive-equivalent) and `GraphDecisionAgent` roots without calling a provider. It accepts 16 matched statistical episode keys per arm, verifies all 32 attempt leaves are exact-six, and counts 352 canonical action rows and 16 submitted terminal paths per arm. TaskSpecs, budgets, full-rate windows, sampling, evaluators, model identity, validation-selected numerical model, validation scores, and the global tool catalog match. The gate verifies zero control behavior overrides, direct Generic inheritance in both arms, registered Graph control only, and no P1 runtime import or bundle provenance. These observations establish one-seed adapter/world mechanics; submission counts are terminal-path mechanics rather than outcome-quality estimates.

The opt-in Generic-base dynamic-v3 implementation uses target-adverse Average Precision over every assigned replay window as its primary endpoint. Failed and partial episodes stay in the population under `phase1_replay_target_adverse_missing_score_v1`; grounded completion is secondary. Seed-level metrics are recomputed over all eight held-out bearing sequences, and the paired bootstrap and exact 256-way swap test recompute the nonlinear endpoint at the matched bearing-cluster level. Per-bearing AP averaging is forbidden because one bearing sequence can contain a single target class.

The shared Benchmark Environment releases a generic `public_condition_event` without future samples, targets, bearing identity, or Graph semantics. P02 consumes that event under `phase1_graph_dynamic_generic_ablation_v3` and implements the full and four ablation profiles. The retained v2 mechanics gate accepts 10/10 exact-six Mock cells with zero provider calls. The dedicated formal runner is implemented and ready for all 240 units; its provider-free schedule emits 240/240 dry-run commands and invokes none, while validate-only performs zero environment reads, zero probe reads, zero provider calls, and zero filesystem writes. Formal coverage is 0/240. The analyzer rebuilds private assignments through DataPort and uses canonical successful-submit prefixes as prediction authority. Runner checks pass 17/17, dynamic-focused checks pass 50/50, and accepted-consumer checks pass 20/20.

Horizon-v3 emits 144/144 dry commands with zero executions. Ottawa P2-E8 emits 18/18 unexecuted commands for 72 bundles and 36 matched pairs; analyzer/runtime checks pass 22/22 and consumer checks pass 18/18. Reliability P2-E9 emits 160/160 inert commands for 160 bundles and 80 pairs; runner/analyzer/scheduler checks pass 12/12 and consumer checks pass 20/20. No provider-bound unit or accepted result exists for these extensions.

### 6.1 Current mechanics-only evidence

<!-- P2_CURRENT_MECHANICS_TABLE:BEGIN -->

| Gate | Matched policies | Materialized mechanics | Formal coverage | Claim boundary |
|---|---|---:|---:|---|
| P2-E0-v2 | Benchmark Generic (Reactive-equivalent) / GraphDecisionAgent over the same Generic base | 32 exact-six leaves (16 per arm), 352 actions and 16 submitted terminal mechanics per arm | Not a provider-bound formal cohort | Accepted adapter/world equivalence mechanics only |
| Dynamic-v3 | Benchmark Generic (Reactive-equivalent) plus the full and four Graph profiles | 10/10 exact-six Mock cells, 0 provider calls; dedicated formal runner 17/17 and dynamic-focused 50/50 | runner ready; 240/240 dry-run commands emitted, 0 invoked; 0/240 formal units; formal gate not accepted | Event routing and profile mechanics only |

<!-- P2_CURRENT_MECHANICS_TABLE:END -->

Neither row contains a task-performance estimate or a Graph treatment effect.
Submission counts above are terminal-path mechanics, not outcome quality. The
standalone generated table is
`paper/assets/tables/p2_current_mechanics_status.md`.

![Current provider-free Paper-2 mechanics evidence. P2-E0-v2 accepts matched Generic-base adapter/world execution mechanics; dynamic-v3 retains the unchanged v2 Mock gate, emits 240 dry-run commands without invoking them, and has formal coverage 0/240.](../assets/figures/p2_current_mechanics_status.svg)

The accepted public aggregate `../p01-phm-agent-benchmark/paper/experiments/results/p0_active_v02_provider_free_reference_subset_v1.json` is the shared provider-free reference authority. It binds Benchmark revision `b6cf5796b7e07c20866fd1bfda743f51ee4ea940`, Data Factory revision `58050716383e32ca79fdad0d9a45ad96a19eb838`, and formal stamp `20260903T080515Z`. Within that aggregate, the B2 Scripted reference contains 64 core episodes and eight replay episodes. Core outcomes cover 32 bearings per task, grounded completion 1.0, 22 steps and 11 operator calls per episode, diagnosis Macro-F1 0.3324, and anomaly Average Precision 0.8987. Replay reports grounded completion 1.0, 50 steps and 33 operator calls per episode, and target-adverse Average Precision 0.9355. This B0/B1/B2 reference subset supplies descriptive one-seed calibration and no Generic-versus-Graph treatment estimate.

## 7. Registered Formal Analysis

The primary runtime is frozen to `cohere/north-mini-code:free` through the OpenRouter OpenAI-compatible Chat Completions endpoint at temperature 0.2, seeds 20260808--20260810, and a 2,048-token per-turn output cap. The accepted active-v0.2 public aggregate above supplies the provider-free reference; matched Generic-versus-Graph LLM estimates do not yet exist. The production v6 contract uses opaque public handles, binds predictions and successful operator artifacts to source samples, excludes bearing identity from the public rollout, fixes the mapped vibration column, and interpolates exact requested `band_power` endpoints before integration. Replay task Average Precision is primary, while grounded completion remains explanatory. The paired table will report Graph-minus-Generic task-primary, completion, recovery, repetition, budget, latency, token, and cost outcomes; Graph state metrics will describe treatment integrity.

The P2-E1 finalizer consumes explicit active-v0.2 timestamped roots and validates each `cohort_index.json` against canonical exact-six leaves. The checked-in readiness artifact records `external_roots_required_no_audit_performed`, carries no retired-root counts, and emits no effect estimate. Every Graph unit must bind a completed Benchmark control unit and the exact clean Benchmark/Data Factory/P2 source topology. Once all four arm gates and both pairing gates accept, the finalizer emits four absolute arm summaries and two paired bearing-bootstrap results in `p2_e1_generic_base_formal_v2_result.json`. The accepted-only renderer independently verifies that identity and every displayed estimate, interval, and valid-replicate count. Finalizer checks pass 13/13 and renderer checks pass 18/18, including a complete 192-core/24-replay-per-arm fixture.

The formal-result insertion contract is fixed before observing those outcomes:

| Result object | Canonical artifact | Manuscript use after acceptance |
|---|---|---|
| Current primary readiness | `paper/experiments/results/p2_e1_primary_readiness_v2.json` | fail closed while matched Generic-base keys are absent; emit no effect estimate |
| Embedded core gates | `paper/experiments/results/p2_e1_primary_readiness_v2.json`; mirrored in `p2_e1_generic_base_formal_v2_result.json` | verify 192 v6 episodes per arm and 192 exact pairs before any diagnosis/anomaly comparison is quoted |
| Core absolute and paired results | `paper/experiments/results/p2_e1_generic_base_formal_v2_result.json` | absolute diagnosis/anomaly task-primary estimates plus Graph-minus-Generic task and rollout deltas, intervals, and valid-replicate counts |
| Core Graph state diagnostics | `paper/experiments/results/p2_e1_graph_state_summary_v2.json`; `paper/assets/tables/p2_e1_graph_state_summary.md` (generated after acceptance; currently absent) | Graph-only state integrity on diagnosis and anomaly episodes |
| Embedded replay gates | `paper/experiments/results/p2_e1_primary_readiness_v2.json`; mirrored in `p2_e1_generic_base_formal_v2_result.json` | verify 24 v6 episodes per arm and 24 exact pairs before the primary estimate is quoted |
| Replay absolute and paired results | `paper/experiments/results/p2_e1_generic_base_formal_v2_result.json` | $\Delta^{\mathrm{replay}}_{AP}$, target-adverse assigned-window accounting, and secondary long-horizon rollout deltas |
| Replay state diagnostics | `paper/experiments/results/p2_e1_graph_state_summary_v2.json`; `paper/assets/tables/p2_e1_graph_state_summary.md` (generated after acceptance; currently absent) | eight-state occupancy, visitation, and transition integrity; zero Monitor/Revise values are valid because v6 registers no `public_condition_event` |
| Replay mechanism case | not admitted by the active publication contract | optional descriptive output remains omitted until its extractor binds the exact accepted combined-result identity and pairing membership |

An accepted combined result will provide absolute estimates, bearing-bootstrap intervals, valid-replicate counts, and eligible Graph-minus-Generic paired estimates. Formal table rows require all four arm gates and both exact pairing gates. Replay summaries preserve assigned, submitted, missing, and covered-window counts under the frozen target-adverse policy; undefined accepted-cohort metrics remain N/A. Graph state summaries are treatment-integrity diagnostics with no Generic analogue. The v6 primary contains no `public_condition_event`, so Monitor/Revise occupancy cannot measure dynamic revision. Dynamic mechanics remain separate from the primary cohort, and completion or recovery cases require matched evaluator gating.

<!-- P2_DYNAMIC_FORMAL:BEGIN -->
<!-- P2_DYNAMIC_FORMAL:END -->

<!-- P2_E8_OTTAWA:BEGIN -->
<!-- P2_E8_OTTAWA:END -->

<!-- P2_E9_RELIABILITY:BEGIN -->
<!-- P2_E9_RELIABILITY:END -->

<!-- GRAPH_MONITOR_PRIMARY_COMPACT:BEGIN -->
<!-- GRAPH_MONITOR_PRIMARY_COMPACT:END -->

<!-- GRAPH_CORE_PRIMARY_COMPACT:BEGIN -->
<!-- GRAPH_CORE_PRIMARY_COMPACT:END -->

<!-- GRAPH_FORMAL_FIGURES:BEGIN -->
<!-- GRAPH_FORMAL_FIGURES:END -->

## 8. Historical Development Records

Earlier PHMskills-derived Mock and provider pilots exposed transition-implementation and action-space defects before the Generic-base correction. They remain archived in the claim--evidence matrix and `paper/assets/tables/` as development records and are excluded from every active treatment estimate.

## 9. State and Recovery Analysis

Formal trajectories require 192 unique episodes in each Generic-base core arm and 24 in each monitoring arm, aligned by seed, fold, bearing, sample, and task. The paired analysis compares first divergence, repeated calls, steps to the next successful non-terminal action, and grounded recovery length with coverage; state occupancy, episode visitation, and transition validity describe Graph treatment integrity. The displayed paired case is descriptive. The v6 primary defines no `public_condition_event`. Observation-conditioned Monitor/Revise behavior and dynamic edge ablations belong to the separate `paderborn_graph_dynamic_ablation_v3` profile, whose retained Mock gate is mechanics-only and whose formal coverage is 0/240.

## 10. Reproducibility

The authoritative task and split configuration is the Benchmark production protocol at `../p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml`; Goal-pack copies are not experiment inputs. `ReactiveSequentialAgent` and `GraphDecisionAgent` derive directly from `GenericLLMToolAgent`; the former is the zero-override Benchmark Generic control, while the latter adds registered graph decision control. `src/phm_graph_agent/state.py` defines the eight-state relation, and `scripts/run_graph_experiment.py` is the single-arm implementation entry point. The active Benchmark Generic P0 launcher is `../p01-phm-agent-benchmark/paper/experiments/run_formal_paper0_v6.sh`. The provider-free downstream projection is `../p01-phm-agent-benchmark/paper/experiments/schedule_downstream_formal_v2.py --dry-run`; it emits 12 P1, 12 P2 Graph core, and three P2 Graph monitoring jobs, binds each P2 command to its completed Benchmark control unit, and reuses the Benchmark Generic P0 roots. Each episode attempt contains the canonical exact-six files, and provider errors remain immutable leaves. The provider-free P02 suite passes 214/214 against the isolated Benchmark PR #15 and P1 PR #2 sibling worktrees, covering implementation, source topology, private-assignment authority, accepted-run provenance, metric denominators, cluster inference, valid-bootstrap reporting, task/mechanism separation, P2-E7 claim boundaries, and protocol-bound atomic rendering. `scripts/render_current_mechanics_evidence.py` regenerates the current mechanics table and figure. The final ten-lens review begins after formal results, final tables and figures, and a result-grounded conclusion are available.

## 11. Discussion and Limitations

The graph is hand-authored, deterministic, and small. The study covers one vibration dataset family, two core tasks, a replay stress protocol, and one primary LLM runtime. The treatment couples state text with state-specific tool-schema filtering, so the estimated intervention is their joint graph-guidance effect. The v6 primary registers no `public_condition_event`; Monitor/Revise values there are integrity diagnostics. Dynamic-v3 has retained provider-free mechanics but no provider-bound cohort. Effects can vary with episode length and Generic-base model quality. The shared experts use a short fixed window and generic time/band features without shaft-speed or bearing-geometry fault-frequency verification, which limits physics-grounded interpretation. Free-endpoint queueing, load, and backend drift make latency descriptive.

## 12. Conclusion

This work defines an executable eight-state PHM decision policy and a matched evaluation that isolates its joint state-prompt and tool-visibility intervention from the underlying Generic agent, data, tools, budgets, and evaluator. Accepted provider-free evidence establishes Generic-base world equivalence, canonical rollout mechanics, public-event routing, and a shared B2 reference over 64 core and eight replay episodes. The Generic-versus-Graph, dynamic, transfer, and reliability cohorts remain unexecuted, so the effect of graph guidance on registered task outcomes is not yet estimated. The accepted-only analysis path fixes how those effects and their explanatory rollout mechanisms will enter the manuscript once the complete cohorts pass their gates.
