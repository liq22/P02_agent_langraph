---
bibliography: ../refs/phmgraph_review_2026.bib
link-citations: true
---

# PHMGraph: Coupling Agent Decisions with Executed Diagnostic Evidence

## Abstract

A tool-using prognostics and health management (PHM) agent must connect decisions about computation to the numerical evidence supporting its diagnosis. Workflow progress alone does not identify complete model inputs, and a provenance record used only after execution cannot affect those decisions. PHMGraph couples an outer decision controller to an inner typed graph of executed numerical dependencies. The graph derives sample-bound feature readiness and supported-prediction availability, which condition phase selection and tool admission while preserving native numerical validation. An eligible prediction permits submission without forcing post-prediction closure. A new outer-organization-by-evidence-feedback design holds potential numerical capability fixed; a lossless flat-feedback control separates presentation from relation information. Selected-path replay and edge-corruption checks assess computational support alongside operational and grounded diagnosis. The mechanism is implemented and tested on the shared native numerical fixture. Its real-data diagnostic effects, prediction-changing headroom and provider costs remain unestimated.

## 1. Introduction

Reliable equipment diagnosis requires both a useful numerical method and a procedure that applies it to the available measurement. Bearing-diagnostic benchmarks expose substantial variation in the difficulty of extracting fault evidence, while transfer learning improves the representations used for classification [@smith2015; @shao2019]. The Paderborn benchmark further distinguishes experimentally generated bearing damage and measurement conditions [@lessmeier2016]. These developments primarily strengthen the mapping from measurements to predictions. A tool-using PHM agent introduces an additional decision layer: it chooses which computation to invoke, interprets the returned evidence and decides when to deliver a diagnosis. A capable predictor that is never called cannot contribute to that delivered result.

Language-model agents offer a way to coordinate these decisions without replacing every numerical component. Coscientist and ChemCrow couple language reasoning with scientific tools [@boiko2023; @bran2024], while ReAct interleaves reasoning with environmental actions and Toolformer learns tool use from API-augmented examples [@yao2023react; @schick2023toolformer]. For PHM, this suggests an architecture in which signal analysis and prediction remain executable numerical operations, while the agent organizes their use. The resulting scientific question concerns the relation between available capability, its actual execution and the final diagnosis—not merely whether an agent can produce an intelligible report.

Explicit workflows are an established response to this coordination problem. StateFlow uses state-dependent instructions and transitions, and evaluates refined reactive prompting and state-removal variants [@wu2024stateflow]. PHMForge studies industrial tool orchestration, including verification, distractor-tool and discovery controls [@li2026phmforge]. TimeSage-MT compares code-enabled, skill-guided and orchestrated time-series systems and reports a grounding–flexibility trade-off [@kong2026timesagemt]. These results motivate a more specific question: **with the same PHM procedures and numerical capabilities available, how should execution evidence condition an agent’s next computation and submission, and when does that coupling change the delivered diagnosis?**

A workflow and a numerical evidence path answer different questions. The workflow specifies which computation to request next; the evidence path records how the released measurement was transformed into a prediction. A successful-call flag cannot determine whether distinct model input roles have been filled, and a prediction flag does not establish the numerical support of a later submission. A provenance graph that is produced only after the episode cannot change those decisions.

We study an explicit coupling of these two objects. The inner graph records typed, role-bound dependencies from actual numerical executions. Its current-task frontier informs outer progress and prediction/submission eligibility. The same fitted experts, procedural catalog and numerical validators are shared across conditions. A supported prediction permits submission without necessarily closing further analysis; this separates evidence readiness from an assumption of diagnostic sufficiency.

Three contributions define the study:

1. **A coupled decision–evidence formulation for PHM.** It distinguishes procedural organization from the numerical path that supports a delivered label, with matched potential capability and evaluator-only targets.
2. **A sample-bound prerequisite-feedback mechanism.** Executed input-role dependencies determine structural feature readiness and supported-prediction availability. These conditions affect the outer phase and tool menu rather than serving only as a retrospective visualization.
3. **A falsifiable computational-support evaluation.** Native support replay, edge corruption and lossless flat feedback complement first-attempt diagnosis outcomes. They separate execution reproducibility from correctness and physical explanation; real-data effects remain to be measured.

### 1.1 Related work and positioning

**Numerical PHM capability.** Bearing-diagnostic benchmarks and deep transfer learning establish signal-processing, dataset and representation foundations [@smith2015; @lessmeier2016; @shao2019]. MOMENT extends pretrained numerical representations to multiple time-series tasks [@goswami2024]. These approaches change or evaluate numerical capability. The present study holds the available fitted experts fixed and instead examines their actual use by the agent.

**Tools and reusable experience.** Toolformer learns API use, ToolLLM combines training, tool retrieval and tool-use paths, and Gorilla studies API generation with retrieved documentation [@schick2023toolformer; @qin2023toolllm; @patil2023gorilla]. Scientific systems such as Coscientist and ChemCrow coordinate domain-specific computations [@boiko2023; @bran2024]. ReAct organizes actions through interaction history; Reflexion adds feedback across attempts; Agent Workflow Memory induces reusable routines from experience [@yao2023react; @shinn2023reflexion; @wang2024awm]. The PHM comparison here adds neither tool training nor treatment-only knowledge or experience.

**Structured reasoning and workflows.** Finite controllers and reward machines provide established representations of policy or task structure [@hansen1997; @icarte2018]. StateFlow implements state-dependent instructions, execution and transitions, while StateAct combines goal prompting and state tracking [@wu2024stateflow; @rozanov2025stateact]. Tree of Thoughts and Graph of Thoughts organize alternative reasoning continuations and their dependencies [@yao2023tot; @besta2024got]. Language Agent Tree Search uses search and environment feedback, AFlow optimizes code-represented workflows, and AutoGen supports configurable multi-agent conversations [@zhou2024lats; @zhang2025aflow; @wu2023autogen]. PHMGraph instead studies evidence-conditioned control around one underlying agent and a fixed numerical tool pool.

**Industrial and time-series agents.** ReActXen adds review and reflection for industrial data access, CodeReAct embeds executable-code reasoning in asset-management workflows, and SPIRAL combines planning, simulation and criticism within tree search [@rayfield2025reactiot; @zhou2026codereact; @zhang2026spiral]. TimeART trains tool-augmented time-series reasoning [@wu2026timeart]. PHMForge's industrial tool controls and TimeSage-MT's paired system comparisons are especially relevant: they already examine orchestration and the trade-off between structured grounding and flexibility [@li2026phmforge; @kong2026timesagemt]. The present question concerns numerical dependency feedback under a common PHM catalog and feature contract, not the first use of workflow control.

**Outcome evaluation.** AgentBench, GAIA and WebArena assess interactive or functional task completion, while tau-bench additionally emphasizes consistency in tool–agent–user interaction [@liu2023agentbench; @mialon2023gaia; @zhou2024webarena; @yao2024tau]. Statistical comparison requires explicit experimental units and uncertainty rather than isolated point estimates [@demsar2006; @agarwal2021]. These foundations support a paired, bearing-level diagnostic comparison; neither a valid tool call nor a valid transition substitutes for the final diagnosis.


**Provenance and action control.** PROV-DM establishes entity/activity provenance relations [@moreau2013prov]. MAP-Graph reports ancestry-aware memory handling and action gating [@wang2026mapgraph]. These precedents rule out treating typed provenance or its use in control as standalone novelty. The distinguishing object here is the implemented PHM numerical prerequisite, its coupling to continuation/submission, and the resulting task-specific evidence.

## 2. Basic Theory and Problem Formulation

### 2.1 Tool-using PHM diagnosis

An episode asks an agent to diagnose a bearing from a released vibration measurement. The agent receives public task information, data handles, numerical-tool interfaces and a computational budget. It can acquire a bounded window, inspect numerical methods, compute features, invoke a fitted expert and submit a class with supporting references. A request $a_t=(u_t,v_t)$ consists of a tool name and its arguments. Public history $h_t$ contains requests, returned observations, errors and resource use; evaluator-only class $c_k$ never enters the policy.

The primary task exposes one distinct raw window with fixed channels and sampling rate. Rereading may generate another identifier for the same array. Numerical experts accept specified feature roles, not arbitrary operator outputs. We hold the data scope, feature contract, fitted parameters, language model, procedural catalog and resource caps fixed across treatments. These conditions fix potential capability, not the operations actually selected.

Three outcomes must remain distinct: a submitted label can be accepted, supported by a task-matched numerical computation, and correct against the private class. These checks have different meanings; acceptance alone guarantees neither numerical support nor correctness. A complete computational path explains how an executed numerical result was produced; it does not establish why that fault is physically present or which feature is causally important.

### 2.2 Prior foundations: decision control and execution provenance

**Decision organization.** History-conditioned tool use and finite-state control are established foundations [@yao2023react; @hansen1997]. StateFlow explicitly uses states, transitions and state-dependent execution [@wu2024stateflow]. A decision graph $G^{\mathrm{out}}=(S,E^{\mathrm{out}})$ represents procedural states and permitted transitions, including recovery cycles. A state label is an execution abstraction rather than a diagnostic posterior.

**Execution provenance.** PROV-DM separates entities from activities and distinguishes use, generation and derivation [@moreau2013prov]. For numerical analysis, a feature is an entity, while the operator invocation that produced it is an activity. A model's input role must identify the actual feature entity consumed. Merely listing an artifact beside a prediction does not establish this dependency. A submitted citation is likewise different from a numerical input.

**Provenance-conditioned decisions.** Provenance need not be confined to retrospective inspection. MAP-Graph reports typed execution ancestry and risk-sensitive action gating in multi-agent memory workflows [@wang2026mapgraph]. Thus, using provenance as a control signal is prior art. The present problem concerns sample-bound numerical prerequisites, selection among fitted diagnostic computations and reproduction of the resulting prediction under a shared PHM contract.

A deterministic summary of a complete public trace adds no external observation: an unrestricted policy could compute it from the trace. Its value to a bounded language model can arise from explicit organization and enforcement. Any such value must be measured against the corresponding prompt, control and resource changes, rather than attributed to new information or graph notation itself.

### 2.3 Mathematical formulation and observation boundaries

Let $X_k$ collect the fixed episode setting. Let $Z=(o,e)$ switch outer decision organization and inner evidence feedback. The resulting public trajectory, process measurements and evaluated outcome are

$$
\tau_k^Z\sim P_Z(\cdot\mid X_k),\qquad
T_k^Z=t(\tau_k^Z),\qquad
Y_k^Z=y(\tau_k^Z,c_k).
$$

Every condition retains the same kinds of execution records. The intervention is whether evidence-derived prerequisites are exposed to the policy and used in control, not whether only the treatment produces an auditable record. Process measurements include completed numerical input roles, prediction use, recovery, analytical continuation, submission and resource use. The specific graph construction and feedback rule are defined in Section 3.

![**Problem formulation and observation boundaries.** The matched setting $X_k$ and assigned interface $Z=(o,e)$ generate a public trajectory. Process measurements $T_k^Z$ and evaluated outcome $Y_k^Z$ have different roles; only the evaluator accesses the true class $c_k$. Diagnosis is scored over a cohort, not by averaging episode-level F1. These arrows show execution and measurement dependencies, not an identified causal mediation model.](../assets/figures/phmgraph_problem_formulation.svg)

Figure 1 separates available capability, its execution and its evaluated consequence. A graph can faithfully record an incorrect computation, and an accepted correct guess may lack a numerical support path. Both cases remain in the assigned cohort.

Let $\hat c_k^Z\in\{1,2,3,\varnothing\}$ denote an accepted diagnosis or a resolved terminal non-submission. For resolved first-attempt records $D_Z$, the operational endpoint is

$$
M(D_Z)=\frac{1}{3}\sum_{c=1}^{3}
\frac{2\mathrm{TP}_c(D_Z)}{2\mathrm{TP}_c(D_Z)+\mathrm{FP}_c(D_Z)+\mathrm{FN}_c(D_Z)}.
$$

A non-submission contributes a false negative to its true class; it is not a fourth averaged class. The cohort contains all three declared classes. An indeterminate attempt remains unresolved rather than being fabricated, discarded or automatically repeated.

The computational-grounding endpoint retains the same labels and cohort rule. An accepted label is retained only when it agrees with the native task-matched prediction and includes that prediction's required feature references; otherwise a resolved failure maps to $\varnothing$. Missing support fields leave that secondary endpoint unresolved. Support-path replay is evaluated separately from both diagnosis scores: replay agreement neither makes a wrong prediction correct nor establishes feature relevance.

### 2.4 Research gap

StateFlow supplies decision organization, PHMForge investigates industrial numerical-tool orchestration, and TimeSage-MT compares structured time-series agents [@wu2024stateflow; @li2026phmforge; @kong2026timesagemt]. Provenance standards and provenance-aware agents already supply relational execution representations [@moreau2013prov; @wang2026mapgraph]. The unresolved PHM question is how numerical dependency state should affect a workflow whose nominal progress can diverge from its available evidence.

Counting successful calls cannot distinguish ten repeats of one feature from ten distinct required inputs. Reaching a prediction cannot establish that a later submission cites that prediction, or that all affordable alternatives have become useless. Conversely, when the numerical contract leaves only one effective path and the base agent follows it correctly, additional graph feedback may be redundant or costly. These alternatives make the proposed control empirically falsifiable.

The required comparison therefore distinguishes passive recording from active feedback, numerical support from label correctness, and evidence availability from a feasible prediction-changing continuation. A positive effect of one compound interface does not isolate graph topology or establish a general benefit of dual-graph architectures.

### 2.5 Research questions and estimands

We investigate whether numerical-evidence feedback improves first-attempt diagnosis when outer organization is present, what it changes without that organization, and which effects coexist with replayable support. Conditional on fixed cohort assignments, the principal contrast is

$$
\Delta_{e\mid o=1}=\mathbb E\!\left[M(D_{11})-M(D_{10})\mid X_{\mathcal I}\right].
$$

The other simple effects compare $10-00$ and $01-00$. The factorial interaction is

$$
\Delta_{oe}=\mathbb E\!\left[M(D_{11})-M(D_{10})-M(D_{01})+M(D_{00})\mid X_{\mathcal I}\right].
$$

An interaction is defined on the chosen outcome scale; it does not by itself prove mechanistic synergy. The grounded endpoint uses the same contrasts. Conditional process rates describe treatment-dependent subsets rather than identify causal mediation. These new treatment definitions do not relabel the earlier pointer-by-gate comparisons.

## 3. Method

### 3.1 Dual-graph overview

PHMGraph couples an outer decision controller to an inner graph of executed numerical dependencies. After each tool result, the inner graph records what was used and generated. A graph-derived frontier identifies missing feature roles and task-supported predictions. Feedback conditions the next phase and tool menu; the fixed language model still chooses the request and its arguments. Native tools remain responsible for numerical computation and full input validation. A submitted diagnosis yields a control path and a selected numerical support subgraph, which can be replayed separately by the evaluator.

![**Coupled decision and numerical-evidence graphs.** The upper layer organizes decisions; the lower layer records the actual window-to-feature-to-prediction computation. The middle feedback path derives evidence state $\eta_t$ from the inner graph and conditions the outer phase and menu. Executed actions update the graph in the opposite direction. Time and band features are grouped for display; the implementation retains individual activities, artifacts and input roles. The coupled path is shown: an eligible prediction permits submission without forcing all further analysis to stop. Recovery paths are illustrative; the exact rule is in Section 3.4. Offline support replay and private labels never feed back into the episode. Numbers refer to Algorithm 1.](../assets/figures/phmgraph_method_overview.svg)

Figure 2 makes the two directions explicit: decisions select evidence-generating operations, while executed evidence constrains subsequent decisions. Section 3.2 specifies the reused outer interface, Section 3.3 constructs numerical support, Section 3.4 defines online coupling, and Section 3.5 assembles execution and explanation output.

### 3.2 Outer decision organization

All conditions receive the same ordered catalog $B=((b_j,d_j))_{j=1}^{6}$, with opaque identifiers B01–B06. The fixed instructions concern acquisition, analysis-family selection, feature construction, prediction, recovery and supported submission. Enabling $o$ appends the active block pointer and applies its phase menu. Disabling $o$ omits the pointer and starts from the common eleven-tool surface. Historical state annotations are removed equally from model-visible tool messages; public numerical results and errors remain available.

The inherited call-history controller $f(h_t)$ first handles the latest error, then checks successful reading, catalog inspection, prediction and schema inspection. Its ordinary post-prediction state exposes submission alone. This rule is preserved in the outer-only condition and in the historical indexing experiment. It is not sufficient to establish evidence readiness, which motivates the separate feedback intervention.

| Inherited phase | Available tool families |
|---|---|
| Inspect | Data search, description, bounded read and summary |
| Hypothesize | Operator/model catalogs and data summary |
| Analyze | Data summary; operator catalog, schema and execution; model catalog and schema |
| Check | Data summary; operator schema/execution; model catalog, schema and prediction |
| Recover | Data description/read/summary; operator/model catalogs and schemas; operator execution and prediction |
| Submit | Submission |

The outer graph is a procedural controller, not a learned graph or a physical fault model. Its pointer and exposure/admission operations remain distinguishable in the earlier outer-interface ablations.

### 3.3 Inner numerical-evidence graph

For public prefix $h_t$, define

$$
G_t^{\mathrm{in}}=
\left(V_t^{\mathrm{art}}\cup V_t^{\mathrm{act}},
E_t^{\mathrm{use}}\cup E_t^{\mathrm{gen}}\cup E_t^{\mathrm{cite}}\right).
$$

Artifact entities include raw windows, intermediate numerical outputs, feature vectors, predictions and accepted submissions. Activity nodes record executed calls and their arguments. An input-role edge $(v,a,j)\in E^{\mathrm{use}}$ means activity $a$ consumed entity $v$ in role $j$; $(a,v)\in E^{\mathrm{gen}}$ records generation. A citation edge records a submitted reference, not numerical dependence. Operator input roles come from the actual source argument, and predictor roles from the actual feature-reference mapping.

The update is an append operation on the recorded request and observation:

$$
G_{t+1}^{\mathrm{in}}=U(G_t^{\mathrm{in}},a_t,o_{t+1}).
$$

Successful native calls generate fresh entities. Failed calls remain recorded activities but generate no numerical evidence. Discovery and schema results supply public requirements without becoming computed features. Under fresh references and use of previously generated inputs, the successful numerical subgraph is acyclic: each input producer precedes the consuming activity, which precedes its newly generated output. Forward references, overwritten identifiers or missing input-role edges violate this support condition. The assumption concerns trusted native execution records, not protection against an adversary controlling the recorder.

For prediction $p$, its support subgraph contains the actual numerical ancestors reached through use and generation edges. Every use must agree with the recorded input role and refer to an earlier producer. Repeated or aliased artifacts do not fill an unrelated required role. For a submission, the selected prediction is the first known prediction reference under the native submission rule; its label and required feature citations must agree with that submission. Extra citations are not silently promoted to numerical causes, and a favorable alternative prediction is not selected retrospectively.

### 3.4 Evidence-conditioned phase and tool admission

For a publicly inspected model schema $m$, raw-window reference $w$ and required feature role $j\in\mathcal R(m)$, let $\mathcal F_{m,w,j}(G_t^{\mathrm{in}})$ contain the currently available feature entities whose typed source paths match that role and window. Define

$$
R_t=\mathbf1\!\left\{\exists(m,w):
\mathcal F_{m,w,j}(G_t^{\mathrm{in}})\ne\varnothing\ \forall j\in\mathcal R(m)\right\},
\qquad
P_t=\mathbf1\!\left\{\text{a task-supported native prediction exists}\right\}.
$$

The feedback state $\eta_t=\Phi(G_t^{\mathrm{in}})$ contains these per-role candidate sets, missing roles, supported prediction references and observed label disagreement. $R_t$ establishes structural availability, not complete numerical admissibility: parameter conventions and numerical validity remain native predictor checks. $P_t$ additionally requires successful native prediction and a complete, role-correct, same-window support path for the current task. A successful native prediction can retain complete provenance even when the agent did not explicitly query its schema; missing discovery is not scored as missing numerical ancestry. Neither indicator depends on the true fault class. Disagreement is exposed as an observation, not converted into a rule for choosing the correct expert.

With feedback disabled, the phase is $F_0(h_t)=f(h_t)$. With feedback enabled, a latest nonterminal error selects Recover; absence of a current-task window selects Inspect; $R_t=1$ or $P_t=1$ selects Check; otherwise the phase is Analyze. The menu begins with the phase subset when $o=1$, or global tools when $o=0$. Feedback removes prediction when $R_t=0$ and submission when $P_t=0$, and permits submission when $P_t=1$. The resulting menu $\Gamma_t$ is used identically for model-visible schemas and name admission.

Consequently, the coupled path remains in Check after a supported prediction and can expose both submission and further computation. It does not force another expert call, automatically resolve disagreement, repair arguments or stop analysis solely because a predictor has run. Submission eligibility is not a guarantee that the model will supply valid supporting arguments; native submission checks and evaluator metrics still determine that outcome. A native terminal episode cannot be reopened by a recovery state.

The full loop is

$$
G_t^{\mathrm{in}}\rightarrow\eta_t\rightarrow
(s_t,\Gamma_t)\rightarrow a_t\rightarrow o_{t+1}\rightarrow G_{t+1}^{\mathrm{in}}.
$$

Feedback changes a derived prompt, prerequisite admission and, with outer organization, phase routing and post-prediction continuation. Its effect is therefore a specified bundle, not a pure topology effect. The flat-evidence control preserves every frontier value and dependency binding in a lossless row representation while leaving the graph predicates and menu unchanged. It tests presentation, not the removal of relation information. Deleted or shuffled edges are separate corruption controls.

### 3.5 Algorithm and computational explanation output

**Algorithm 1. Diagnosis with coupled decision and execution evidence.**

**Input:** public task and scope, shared catalog and tools, fixed model and fitted numerical experts, budgets and switches $(o,e)$. **Output:** canonical first-attempt outcome, public control path and selected numerical support.

1. Initialize history and an empty inner graph. Use the same graph recorder in all four conditions.
2. Read the latest public prefix and compute the inherited progress state.
3. Update the evidence graph from newly recorded activities and derive the current-task frontier. Only when $e=1$ expose the frontier and use its readiness predicates in control.
4. Set the phase, optional pointer and tool menu under $(o,e)$; retain the full common procedural catalog.
5. Request one action from the fixed language model, using the same menu later supplied to admission. Retain native provider and response-format failures without switching models or replacing the attempt.
6. Admit the tool name or record its rejection; native tools validate and execute admitted requests. Append the result and usage. Only nonterminal episodes continue.
7. Retain submission or terminal non-delivery. Include the final event in the derived evidence graph. For an accepted submission, extract its selected numerical support and recorded outer phase/menu path; unresolved support remains unresolved.

The output pair

$$
\mathcal E_k=(\text{recorded outer control path},\ G_{k,\mathrm{sup}}^{\mathrm{in}})
$$

is a computational execution explanation, not a reconstruction of the language model's hidden reasoning. The outer component records procedural context and restrictions; the inner component reconstructs how executed data transformations produced the selected numerical prediction.

Support replay is evaluator-side. In a fresh environment bound to the same data, numerical implementation and fitted models, replay the selected ancestor activities in topological order, remapping generated references rather than reusing cached results. Compare the public feature values, prediction probabilities, class and recorded sample metadata. Classes must match exactly; numeric values use a prespecified tolerance, initially relative $10^{-9}$ and absolute $10^{-12}$. Missing source assets or failed execution are unresolved replay cases, not agreement. The check does not compare every hidden intermediate array or certify physical causality. Its calls and cost are reported separately and never supplied as free evidence to the online agent.

## 4. Testable consequences

Evidence feedback should be behaviorally relevant where call-history progress and numerical readiness differ: incomplete feature roles, wrong-window ancestry, premature submission or a useful remaining expert prediction. Removing a required usage edge while retaining all node values should invalidate support and can alter the next admitted menu. A failed call should not create evidence. A lossless table conversion should preserve structural predicates even when its model-facing tokenization differs.

These are mechanism tests, not predictions of uniformly positive diagnostic effects. A fixed-contract single-window task can leave little prediction-changing headroom. Additional feedback can be redundant, consume tokens or restrict useful behavior. A supported numerical label may remain wrong. Real development data must therefore establish the presence and frequency of legal alternatives before a diagnostic-opportunity claim is evaluated.

## 5. Evaluation design

### 5.1 New treatment family and preserved historical ablations

The new diagnosis protocol crosses outer organization and active evidence feedback:

| Condition | Outer organization | Evidence feedback | Hidden provenance recording |
|---|---:|---:|---:|
| dual-v1-00 | off | off | common |
| dual-v1-10 | on | off | common |
| dual-v1-01 | off | on | common |
| dual-v1-11 | on | on | common |

The principal diagnosis contrast is $11-10$; other simple effects, the outcome-scale interaction and grounded counterparts complete the prespecified analysis. The coupled grouped-versus-flat comparison uses identical dependency information and control. Token counts and costs are measured, not assumed equal. Scripted numerical execution remains a reference rather than another treatment factor.

Earlier pointer-by-gate cells retain their original definitions and first-attempt requirements as outer-interface ablations. Their results are never pooled or renamed as dual-graph evidence. The new protocol must obtain its own approved cohort, provider settings, resource limits and inferential specification before confirmatory execution.

### 5.2 Task, provenance and replay measurements

Report operational and grounded Macro-F1 on the same assigned first-attempt cohort, alongside submission, numerical support and failure rates. For provenance, measure completed distinct required roles, valid raw-to-prediction support paths and correctly selected submission support. Replay reports the number eligible, attempted, reproduced within tolerance, failed and unresolved; do not hide unsupported submissions by reporting only successful replay cases. Private labels are used only for task outcomes.

Delete or exchange a required use edge in a copied graph, preserving the original trace and node attributes, to test support rejection and online-predicate sensitivity. Reference-renaming replay checks that identity spelling is not treated as numerical content. These interventions test implementation dependence on provenance, not feature importance. Feature relevance requires a separately justified numerical intervention within the admitted data/model contract; an invalid feature edit is not evidence of physical causality.

### 5.3 Real-data and statistical requirements

Before provider experiments, verify metadata-to-waveform alignment, declared sample rate and windows, disjoint fitting/development/evaluation bearings, and reload consistency of fitted experts. On reserved development bearings, measure expert disagreement and resource-feasible second-prediction paths using the native feature contract. Distinguish new artifacts from new numerical values and from changed labels. A best-expert calculation is evaluator-only descriptive headroom, not a test-time selector.

Use independent treatment sessions and matched first-attempt assignments. Keep canonical non-submissions and provider interruptions; resolve indeterminate attempts without automatic resends. Freeze model route and settings, condition order, budgets, timeouts, cohort, repeats and bootstrap specification before confirmatory execution. Paired bearing-level resampling respects dependent windows. The new primary/secondary family needs its own multiplicity rule; the earlier indexing study's two-contrast allocation does not transfer automatically. Pilot variation and event frequency guide a stated precision target, not selection of favorable outcomes.

## 6. Results

The implemented mechanism has software-level checks for typed support, online menu dependence and selected-path replay on the existing deterministic numerical fixture. These checks use the shared native tools and runner; they do not constitute real bearing-data performance results. Operational effects, grounded effects, real-data headroom and provider costs for the new treatment family remain unestimated.

### 6.1 Comparisons under separate protocols

Historical Graph–Generic, dynamic-revision, cross-dataset, repeated-trial and pointer-by-gate comparisons retain their own protocols. Their insertion slots below are not dual-graph results.

<!-- Legacy insertion slots retain their original profiles; never populate them with dual-v1 outcomes. -->
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

## 7. Discussion

The outer and inner graphs describe different objects: procedural decisions and executed numerical dependencies. Their coupling is implemented through sample-bound prerequisite feedback, not through new fault knowledge or stronger fitted models. The task-specific distinction is between nominal progress and numerical readiness, including the choice to permit submission without automatically closing legal analysis.

The representation itself is not uniquely privileged. A lossless relational table can encode the same graph; deleting its dependency information is an information ablation, not a content-matched presentation control. Likewise, numerical support and replayability are narrower than explanation of feature relevance or physical fault mechanisms. A useful scientific conclusion must establish what the specified feedback changes in diagnosis, computational support or cost, and where it is redundant. The current software evidence establishes an executable mechanism, while its PHM utility remains an empirical question.

## References
