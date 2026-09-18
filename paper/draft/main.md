---
bibliography: ../refs/phmgraph_review_2026.bib
link-citations: true
---

# PHMGraph: Contract-Grounded Decision Control for Tool-Using Fault Diagnosis

## Abstract

A tool-using fault-diagnosis agent can complete many computations without assembling the inputs required by its numerical predictor. Native input validation rejects an incompatible request, but does not determine how the agent should use the remaining budget. PHMGraph studies this distinction through contract-grounded decision control. A deterministic execution state tracks distinct feature roles, their signal-transformation ancestry and task-supported predictions. This state conditions workflow progress and tool admission while leaving numerical computation and validation unchanged. A supported prediction permits submission without forcing the end of further analysis. The formulation separates the availability of a computation, its numerical support and its diagnostic consequence. A matched outer-organization-by-evidence-feedback design compares first-attempt diagnosis, supported delivery and resource use; a lossless table control tests feedback presentation. Numerical support is evaluated by fresh execution under declared replay conditions, separately from label correctness. The present study specifies and implements these mechanisms; their diagnostic benefit and net cost on real PHM data remain to be established.

## 1. Introduction

Vibration-based fault diagnosis depends on how a measurement is transformed before it reaches a decision rule. The CWRU benchmark analysis shows that different records can require different processing routes to expose bearing-fault signatures, whereas the Paderborn benchmark distinguishes artificial damage from damage produced in accelerated lifetime tests [@smith2015; @lessmeier2016]. Learned representations and transfer learning address a complementary problem: extracting discriminative information across measurement settings [@asutkar2023; @goswami2024]. These numerical capabilities do not by themselves specify which computation an interactive agent will execute, whether its inputs are compatible, or whether the resulting prediction will support the delivered diagnosis.

Language-model agents provide a decision layer around scientific tools. Coscientist coordinates chemical research operations, and ChemCrow couples language reasoning with domain-specific calculations and laboratory tasks [@boiko2023; @bran2024]. Industrial systems extend this approach to data access, asset-management analytics and prognostic tools [@rayfield2025reactiot; @zhou2026codereact; @li2026phmforge]. The resulting opportunity for PHM is not to replace signal processing with prose, but to coordinate executable numerical methods through a public history of observations and actions.

Much of the required execution machinery is already established. ReAct uses environmental feedback, StateFlow organizes state-dependent execution, and LLMCompiler schedules dependent tool calls and supports replanning from intermediate results [@yao2023react; @wu2024stateflow; @kim2024llmcompiler]. Scientific workflow systems go further in provenance: AiiDA distinguishes data dependencies from workflow logic, including the different cycle properties of their graphs, while the Common Workflow Language specifies typed interfaces and portable execution requirements [@pizzi2016aiida; @huber2020aiida; @crusoe2022cwl]. TimeSage-MT combines typed task dependencies with comparisons of code-enabled, skill-guided and orchestrated time-series agents [@kong2026timesagemt]. Thus, two graph objects or a dependency-aware scheduler alone do not define the scientific advance sought here.

The unresolved comparison concerns **the incremental value of anticipatory numerical-evidence feedback when the numerical tools already enforce their input contract**. Consider a fitted vibration classifier requiring six time-domain roles and four band-energy roles derived from a common window through an approved spectral transform. Several completed calls to the same feature do not satisfy those distinct roles. A valid feature from another window is not interchangeable with one from the current measurement. The native predictor can reject such inputs; the separate question is whether an explicit readiness state helps the agent avoid unproductive requests, complete a supported diagnosis, or retain a useful continuation under the same budget. The roles and permitted transformations are properties of the declared numerical model, not universal requirements of all PHM models.

![**Motivation: computation progress is not numerical readiness.** A fixed PHM contract $X_k$ connects one vibration window to distinct time-domain and spectral feature roles. Nominal call progress cannot resolve repeated roles or incompatible ancestry. Both comparison paths retain native input validation; $Z=(o,e)$ changes whether deterministic evidence state $\eta_t$ also conditions the decision interface before a request. The observed trajectory $\tau_k^Z$ produces process measurements $T_k^Z$ and evaluated outcomes $Y_k^Z$, with the true class $c_k$ available only to the evaluator. The comparison can reveal improved delivery, redundant control or additional cost; the diagram contains no empirical improvement claim.](../assets/figures/phmgraph_problem_formulation.svg)

Figure 1 locates the ambiguity between an available numerical capability and its productive execution. It does not imply that a graph can correct spectral leakage, recover missing fault information or improve an unchanged expert prediction. A lossless JSON record or relational table can preserve the same dependencies. The intervention of interest is how their deterministic consequences enter a bounded agent's decisions, rather than the necessity of a particular storage representation.

Three challenges follow. **First, distinguish compatible evidence from nominal progress.** Call counts and names do not bind the model's distinct inputs to their actual signal sources; the controller needs role-specific, sample-bound state without duplicating the numerical validator. **Second, isolate useful control from extra information and computation.** A feedback summary, a smaller menu and an altered stopping opportunity can all change behavior and cost. Their treatment definition and presentation control must therefore be explicit. **Third, distinguish better execution from better diagnosis.** A valid and reproducible path can deliver a wrong label, and additional analysis is only a diagnostic opportunity when a legal alternative can change the prediction. Each claim needs its own endpoint and denominator.

PHMGraph addresses these challenges by deriving a deterministic prerequisite state from executed numerical dependencies and using it to condition an outer decision controller. The same procedural catalog, fitted experts and native validation are available in every condition. The studied feedback can delay an unready prediction or unsupported submission while allowing further computation after a supported prediction. Its utility is tested through matched interventions on diagnosis, numerical support and resource use, rather than inferred from the existence of a provenance graph.

The study makes three methodological contributions:

1. **A contract-grounded PHM control formulation.** It separates distinct transformation-compatible inputs, supported predictions and diagnostic correctness under fixed numerical capability, making divergence between call progress and evidence readiness an explicit experimental object.
2. **Deterministic prerequisite feedback with non-closing submission eligibility.** Role-bound execution ancestry supplies the state used for phase selection and tool admission; a supported prediction permits, but does not force, submission. The mechanism is testable through missing-role, incompatible-source and continuation contrasts.
3. **A matched diagnosis–support–cost evaluation design.** Outer organization and active feedback are crossed with common evidence processing. Lossless feedback presentation, native support checks and isolated numerical replay distinguish interface effects, computational support and real diagnostic benefit.

### 1.1 Related work

#### Numerical evidence and diagnostic capability

Smith and Randall compare diagnostic processing routes on CWRU vibration records rather than treating all signals as equally informative. Lessmeier et al. evaluate the transfer from artificially damaged bearings to real damage and compare measurement modalities [@smith2015; @lessmeier2016]. These studies motivate checking the usable information and legal numerical paths in the actual dataset. Asutkar and Tallur adapt a scalogram-based classifier by retraining selected layers on target-domain data, while MOMENT studies pretrained time-series representations across several task families [@asutkar2023; @goswami2024]. Both change learned numerical capability. The present comparison instead fixes fitted predictors, their input contract and the released measurement; improvements from representation learning cannot be attributed to its decision controller.

#### Tool competence, planning and corrective feedback

Toolformer learns API use by filtering executed calls and training on augmented text; PAL delegates generated computational programs to an interpreter [@schick2023toolformer; @gao2023pal]. Coscientist and ChemCrow demonstrate scientific tool coordination, including cases where domain assessment matters more than a fluent answer [@boiko2023; @bran2024]. These works establish the value of executable assistance, not the sufficiency of a valid numerical path for a correct diagnosis.

ReAct interleaves reasoning and environmental observations. ReWOO separates planning, tool execution and answer composition to reduce repeated context, while LLMCompiler combines dependency scheduling with intermediate-result-driven replanning [@yao2023react; @xu2023rewoo; @kim2024llmcompiler]. Reflexion uses evaluation and verbal feedback across attempts; CRITIC performs tool-assisted verification and correction; Agent Workflow Memory induces reusable routines from experience [@shinn2023reflexion; @gou2024critic; @wang2024awm]. These mechanisms change plans, verification budgets or available experience. PHMGraph studies a narrower signal: deterministic readiness of the currently executed numerical inputs, without learning new tools or introducing treatment-only procedural knowledge.

#### Structured control and industrial agents

StateFlow evaluates state-dependent instructions, execution and transitions. StateAct adds explicit goal and state descriptions within agent prompting [@wu2024stateflow; @rozanov2025stateact]. Graph of Thoughts separates prescribed thought operations from the evolving reasoning state and evaluates aggregation-based reasoning; Language Agent Tree Search couples search with environment feedback; AFlow optimizes executable workflows using validation performance [@besta2024got; @zhou2024lats; @zhang2025aflow]. Their structures and feedback are established alternatives, not mechanisms missing from the literature. Their reported quality–cost comparisons also caution against treating additional control as uniformly beneficial.

ReActXen adds review and reflection to industrial data access. CodeReAct combines executable analytics with validated business-object interfaces, and TimeART trains time-series tool reasoning through staged supervision [@rayfield2025reactiot; @zhou2026codereact; @wu2026timeart]. PHMForge directly studies industrial numerical-tool orchestration and includes verification, discovery and distractor controls. TimeSage-MT evaluates multiple time-series agent paradigms under typed dependencies and reports a grounding–flexibility trade-off [@li2026phmforge; @kong2026timesagemt]. These are the closest application-level comparisons. The present experimental object is the incremental feedback of sample-bound input-role readiness under common fitted PHM experts and native rejection rules, rather than an unrestricted comparison of entire agent systems.

#### Provenance, dependency execution and the remaining contrast

PROV-DM formalizes entities, activities, use and generation [@moreau2013prov]. AiiDA records computational dependencies and supports automated workflows; AiiDA 1.0 explicitly separates data and logical provenance. CWL represents typed dataflow and execution requirements in structured descriptions [@pizzi2016aiida; @huber2020aiida; @crusoe2022cwl]. The authors of MAP-Graph additionally describe provenance-aware shared memory and action gating in their abstract [@wang2026mapgraph]. Consequently, neither a dual representation nor provenance-conditioned control is claimed as a general invention here.

These precedents establish representation, execution and feedback capabilities. They do not settle the effect targeted by the present matched PHM comparison: whether explicit numerical readiness improves supported first-attempt delivery beyond an unchanged predictor's input validation, and whether that benefit exceeds the added decision cost. A relational implementation with the same readiness predicates is a valid realization of the mechanism. A node-only record with deleted dependencies is a different information condition, not a lossless representation baseline.

#### Task outcomes, consistency and resource accounting

Tau-bench evaluates tool–agent interaction against task state and repeated-trial consistency, showing why one successful-looking interaction does not establish reliable task completion [@yao2024tau]. Demšar emphasizes the experimental unit and paired comparisons, while Agarwal et al. demonstrate how evaluation protocols and uncertainty estimates affect conclusions from limited stochastic runs [@demsar2006; @agarwal2021]. These lessons motivate matched first-attempt assignments, bearing-level dependence handling and separate diagnosis, support and cost endpoints. They do not supply a ready-made sample size or justify treating correlated windows as independent trials.

## 2. Basic Theory and Problem Formulation

### 2.1 Tool-using PHM diagnosis

An episode asks an agent to diagnose a bearing from a released vibration measurement. The agent receives public task information, data handles, numerical-tool interfaces and a computational budget. It can acquire a bounded window, inspect numerical methods, compute features, invoke a fitted expert and submit a class with supporting references. A request $a_t=(u_t,v_t)$ consists of a tool name and its arguments. Public history $h_t$ contains requests, returned observations, errors and resource use; evaluator-only class $c_k$ never enters the policy.

The primary task exposes one distinct raw window with fixed channels and sampling rate. Rereading may generate another identifier for the same array. Numerical experts accept specified feature roles, not arbitrary operator outputs. We hold the data scope, feature contract, fitted parameters, language model, procedural catalog and resource caps fixed across treatments. These conditions fix potential capability, not the operations actually selected.

Three outcomes must remain distinct: a submitted label can be accepted, supported by a task-matched numerical computation, and correct against the private class. These checks have different meanings; acceptance alone guarantees neither numerical support nor correctness. A complete computational path explains how an executed numerical result was produced; it does not establish why that fault is physically present or which feature is causally important.

### 2.2 Prior foundations: decision control and execution provenance

History-conditioned tool use and explicit workflow states are established control mechanisms [@yao2023react; @wu2024stateflow]. Let $G^{\mathrm{out}}=(S,E^{\mathrm{out}})$ denote procedural states and their transitions, including recovery cycles. A state is an execution abstraction, not a posterior over fault classes.

Execution provenance distinguishes data entities from the activities that use and generate them [@moreau2013prov]. AiiDA's distinction between logical provenance and data provenance already separates workflow control from acyclic numerical dependencies [@huber2020aiida]. A model input role identifies the feature actually consumed, not merely an artifact listed near a prediction. Submission citations are a further relation: a cited object need not have been a numerical input. These representations and typed workflow interfaces are inherited foundations [@crusoe2022cwl].

A deterministic function of a complete public trace introduces no external observation. Its possible value to a bounded agent lies in explicit organization and control. Both a graph and a lossless relational encoding can support the same computation. The empirical question concerns use of that state under a PHM numerical contract, not a representational necessity theorem.

### 2.3 Mathematical formulation and observation boundaries

Let $X_k$ collect the fixed episode setting. Let $Z=(o,e)$ switch outer decision organization and inner evidence feedback. The resulting public trajectory, process measurements and evaluated outcome are

$$
\tau_k^Z\sim P_Z(\cdot\mid X_k),\qquad
T_k^Z=t(\tau_k^Z),\qquad
Y_k^Z=y(\tau_k^Z,c_k).
$$

Every condition retains the same kinds of execution records. The intervention is whether evidence-derived prerequisites are exposed to the policy and used in control, not whether only the treatment produces an auditable record. Process measurements include completed numerical input roles, prediction use, recovery, analytical continuation, submission and resource use. The specific graph construction and feedback rule are defined in Section 3.

Figure 1 distinguishes available capability, executed numerical support and evaluated diagnosis. A complete path can support an incorrect prediction, whereas an accepted correct guess can lack numerical support. Both remain in the assigned cohort.

Let $\hat c_k^Z\in\{1,2,3,\varnothing\}$ denote an accepted diagnosis or a resolved terminal non-submission. For resolved first-attempt records $D_Z$, the operational endpoint is

$$
M(D_Z)=\frac{1}{3}\sum_{c=1}^{3}
\frac{2\mathrm{TP}_c(D_Z)}{2\mathrm{TP}_c(D_Z)+\mathrm{FP}_c(D_Z)+\mathrm{FN}_c(D_Z)}.
$$

A non-submission contributes a false negative to its true class; it is not a fourth averaged class. The cohort contains all three declared classes. An indeterminate attempt remains unresolved rather than being fabricated, discarded or automatically repeated.

The computational-grounding endpoint retains the same labels and cohort rule. An accepted label is retained only when it agrees with the native task-matched prediction and includes that prediction's required feature references; otherwise a resolved failure maps to $\varnothing$. Missing support fields leave that secondary endpoint unresolved. Support-path replay is evaluated separately from both diagnosis scores: replay agreement neither makes a wrong prediction correct nor establishes feature relevance.

### 2.4 Research gap

Dependency execution, provenance and state-conditioned agent control are established [@huber2020aiida; @kim2024llmcompiler; @wu2024stateflow]. Industrial and time-series agent evaluations additionally demonstrate that structured grounding and flexible computation can trade off [@li2026phmforge; @kong2026timesagemt]. The missing evidence for the present problem is a matched estimate of active numerical-readiness feedback beyond the same native validator and fitted capability.

This distinction is falsifiable. Repeated calls can leave required roles unfilled; a feature can have the wrong source; and an eligible prediction can leave a useful alternative affordable. Conversely, complete inputs, agreeing experts and no effective continuation can make feedback redundant. The comparison must measure these opportunities rather than assume them from the tool catalog. It must also separate supported execution from correct labels and total recording cost from the marginal cost of exposing and enforcing feedback.

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

The evidence state is computed deterministically; it is neither an LLM-generated summary nor a subgraph-isomorphism search. For each inspected model $m$, current-task window $w$ and required role $j\in\mathcal R(m)$, let $\mathcal F_{m,w,j}(G_t^{\mathrm{in}})$ be the set of available feature entities with the required operator, source path and role-specific attributes. Its binary readiness vector is

$$
r_{m,w,j,t}=\mathbf1\{\mathcal F_{m,w,j}(G_t^{\mathrm{in}})\ne\varnothing\},
\qquad
\mathbf r_{m,w,t}\in\{0,1\}^{|\mathcal R(m)|},
\qquad
R_t=\max_{(m,w)}\prod_{j\in\mathcal R(m)}r_{m,w,j,t}.
$$

The maximum over no candidate bundles is defined as zero. Let $\mathcal P_t$ be the set of task-supported native predictions, $P_t=\mathbf1\{\mathcal P_t\ne\varnothing\}$ and $D_t$ indicate whether their predicted labels disagree. The feedback object is

$$
\eta_t=\Phi(G_t^{\mathrm{in}})
=\left(\{\mathcal F_{m,w,j},\mathbf r_{m,w,t}\}_{m,w,j},
R_t,\mathcal P_t,P_t,D_t\right).
$$

In the studied PHM contract, six roles are direct time-domain features; four are band powers from the prescribed Welch-PSD path. Features must trace to the same current-task window. Repeating RMS cannot fill kurtosis or a spectral role. The band checks use frequency bounds expressed relative to the window's effective Nyquist frequency. This makes the intervention specific to the numerical feature contract without claiming that every bearing diagnosis requires this particular feature set.

The readiness check is deliberately narrower than the native numerical validator. It checks structural role availability and declared source attributes, not every operator convention, admissible parameter or numerical value. Full model validation is unchanged. In particular, reaching $R_t=1$ does not guarantee that an arbitrary feature bundle proposed by the agent will be accepted. After successful native prediction, $\mathcal P_t$ additionally requires complete role-bound ancestry, current-task agreement and the native required supporting references. A successful prediction can retain this support even when no separate schema-discovery call preceded it. $D_t$ reports disagreement but does not choose an expert or infer the true label.

With feedback off, $s_t=f(h_t)$ is the inherited call-history phase. With feedback on, the latest nonterminal error selects Recover; otherwise absence of a current-task window selects Inspect; $R_t=1$ or $P_t=1$ selects Check; the remaining case selects Analyze. Let the starting menu be the phase subset for $o=1$ and the common global set for $o=0$. Active feedback removes prediction when $R_t=0$, removes submission when $P_t=0$, and admits submission when $P_t=1$. The resulting menu $\Gamma_t$ is used both for visible tool schemas and name admission.

The coupled path therefore remains able to analyze after a supported prediction. It neither forces another call nor assumes that the existing prediction is diagnostically sufficient. Native submission validation still checks the actual proposed label and references, and a terminal episode cannot be reopened. The resulting decision loop is

$$
G_t^{\mathrm{in}}\rightarrow\eta_t\rightarrow
(s_t,\Gamma_t)\rightarrow a_t\rightarrow o_{t+1}\rightarrow G_{t+1}^{\mathrm{in}}.
$$

All four conditions construct $G_t^{\mathrm{in}}$ and compute $\Phi$; only $e=1$ exposes the frontier and uses it in control. Thus, $11-10$ measures active feedback on top of common evidence processing, not the total overhead of adding a graph to an uninstrumented system. The intervention includes a derived prompt, prerequisite admission and, with outer organization, phase routing and non-closing submission eligibility. The lossless flat control changes the frontier's serialization into relational rows but preserves every dependency binding, readiness value and control rule. It tests presentation, not graph necessity.

**Cost and failure boundary.** Record common graph/state computation separately from active-feedback prompt tokens, changed tool execution and end-to-end latency. Readiness processing may cost more than the invalid requests it prevents; no positive net value is assumed. With fixed, inexpensive experts, fewer rejected calls need not produce material savings or better diagnosis. Missing schemas can delay readiness, and structurally complete inputs can still fail native validation. These cases are measured alongside opportunities for useful continuation.

### 3.5 Algorithm and computational explanation output

**Algorithm 1. Diagnosis with coupled decision and execution evidence.**

**Input:** public task and scope, shared catalog and tools, fixed model and fitted numerical experts, budgets and switches $(o,e)$. **Output:** canonical first-attempt outcome, public control path and selected numerical support.

1. Initialize history and an empty inner graph. Use the same graph recorder in all four conditions.
2. Read public history $h_t$ and compute the inherited progress state $f(h_t)$.
3. Append newly recorded activities to $G_t^{\mathrm{in}}$ and deterministically compute $\eta_t=\Phi(G_t^{\mathrm{in}})$ in every condition. Expose $\eta_t$ and use its predicates only when $e=1$.
4. Set the phase $s_t$, optional pointer and menu $\Gamma_t$ under $(o,e)$; retain the full common procedural catalog.
5. Request one action from the fixed language model, using the same menu later supplied to admission. Retain native provider and response-format failures without switching models or replacing the attempt.
6. Admit the tool name or record its rejection; native tools validate and execute admitted requests. Append the result and usage. Only nonterminal episodes continue.
7. Retain submission or terminal non-delivery. Include the final event in the derived evidence graph. For an accepted submission, extract its selected numerical support and recorded outer phase/menu path; unresolved support remains unresolved.

The output pair

$$
\mathcal E_k=(\text{recorded outer control path},\ G_{k,\mathrm{sup}}^{\mathrm{in}})
$$

is a computational execution explanation, not a reconstruction of the language model's hidden reasoning. The outer component records procedural context and restrictions; the inner component reconstructs how executed data transformations produced the selected numerical prediction.

Support replay is evaluator-side and does not rerun the language model. Bind the original signal identity, exact slice indices, channels and effective sample rate; load the same fitted assets; and record the numerical software, hardware, floating-point settings and random state required by any stochastic operation. Re-execute the selected ancestor activities in topological order, remapping newly generated references. Recorded feature values are comparison targets, not substitute computed outputs. A checkpointed replay from cached intermediates would validate only the downstream segment and must not be reported as fresh raw-to-prediction reproduction.

Compare public feature values, prediction probabilities, class and sample metadata. Class agreement is exact; the initial numeric tolerance is relative $10^{-9}$ and absolute $10^{-12}$. This declares a test, not a guarantee of bitwise reproducibility across hardware, libraries or stochastic algorithms. Missing source assets and failed execution are unresolved or failed replay cases; numerical disagreement is retained. The checker does not compare every hidden intermediate array or establish physical causality. Offline replay calls and cost are reported separately and never become free online evidence.

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

Condition 00 is a common-catalog reactive control, not an unmodified vanilla agent. The principal diagnosis contrast is $11-10$; other simple effects, the outcome-scale interaction and grounded counterparts complete the prespecified analysis. The coupled grouped-versus-flat comparison uses identical dependency information and control. Token counts and costs are measured, not assumed equal. Common provenance/state computation is timed separately from active feedback; the factorial does not estimate its uninstrumented overhead. Scripted numerical execution remains a reference rather than another treatment factor.

Earlier pointer-by-gate cells retain their original definitions and first-attempt requirements as outer-interface ablations. Their results are never pooled or renamed as dual-graph evidence. The new protocol must obtain its own approved cohort, provider settings, resource limits and inferential specification before confirmatory execution.

### 5.2 Task, provenance and replay measurements

Report operational and grounded Macro-F1 over the same assigned first-attempt cohort. A resolved non-submission remains an outcome rather than disappearing from the denominator. Report the fraction of resolved assignments yielding a native-supported final submission, and, separately, the conditional support fraction among accepted submissions. Missing support fields remain unresolved; they are not silently counted as false or excluded without disclosure.

For graph support, count submitted predictions with complete, role-bound raw-to-prediction ancestry. For replay, report eligible, attempted, matched, mismatched, failed and unresolved counts, including the eligibility and attempted denominators. A useful summary is the fraction of final submitted diagnoses having both valid recorded support and successful fresh replay; report its coverage over all assigned episodes as well. This joint rate does not replace the separate native grounding, path validity and replay rates, and neither implies a correct fault label.

Measure input/output tokens, tool calls, sequential tool depth, end-to-end latency and redundant numerical executions. A repeated execution has the same operator or model, normalized arguments, resolved source window/feature roles and fitted assets; repeated identifiers alone do not define redundancy. Count it as numerically redundant only when the public result is unchanged and no new required role or evidence is supplied. An alternative fitted expert, changed valid input or intended verification is not automatically redundant. Separate common graph/ready-state time, active-feedback costs and offline replay costs. Missing provider usage is not zero.

Delete or exchange a required use edge in a copied graph, preserving the original trace and node attributes, to test support rejection and online-predicate sensitivity. Reference-renaming replay checks that identity spelling is not treated as numerical content. These interventions test implementation dependence on provenance, not feature importance. Feature relevance requires a separately justified numerical intervention within the admitted data/model contract; an invalid feature edit is not evidence of physical causality.

### 5.3 Real-data and statistical requirements

Before provider experiments, verify metadata-to-waveform alignment, declared sample rate and windows, disjoint fitting/development/evaluation bearings, and reload consistency of fitted experts. On reserved development bearings, measure expert disagreement and resource-feasible second-prediction paths using the native feature contract. Distinguish new artifacts from new numerical values and from changed labels. A best-expert calculation is evaluator-only descriptive headroom, not a test-time selector.

Use independent treatment sessions and matched first-attempt assignments. Keep canonical non-submissions and provider interruptions; resolve indeterminate attempts without automatic resends. Freeze model route and settings, condition order, budgets, timeouts, cohort, repeats and bootstrap specification before confirmatory execution. Paired bearing-level resampling respects dependent windows. The new primary/secondary family needs its own multiplicity rule; the earlier indexing study's two-contrast allocation does not transfer automatically. Pilot variation and event frequency guide a stated precision target, not selection of favorable outcomes.

## 6. Results

Current validation concerns software mechanics on a deterministic numerical fixture: role-bound support, menu sensitivity to a broken dependency and fresh numerical replay. It is not an estimate of fault-diagnosis performance. The real-data four-condition comparison, supported-delivery rates, prediction-changing opportunities and provider costs have not yet been measured.

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

PHMGraph studies how a declared numerical contract becomes usable decision state for a bounded agent. Its graph objects inherit established workflow and provenance ideas; its empirical object is the effect of deterministic, current-task prerequisite feedback beyond unchanged native validation. A supported prediction may remain wrong, and a valid continuation may add cost without changing the delivered label.

The four-condition comparison identifies the specified feedback bundle on top of common evidence processing. It does not isolate a pure topology effect or measure total instrumentation overhead. A lossless relational table is an equally valid carrier of the dependency information; its presentation comparison must not be confused with deletion of that information. Numerical replay tests computational reproduction under stated conditions, not feature necessity, physical-fault causality or the language model's hidden reasoning. The decisive remaining evidence is whether real diagnostic tasks contain readiness failures or useful alternatives often enough for the proposed control to improve supported delivery at an acceptable cost.

## References
