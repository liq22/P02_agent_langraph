---
bibliography: ../refs/phmgraph_review_2026.bib
link-citations: true
---

# PHMGraph: Separating Instruction Indexing from Workflow Gating in Tool-Using PHM Agents

## Abstract

A prognostics and health management (PHM) agent must turn available numerical capabilities into a delivered diagnosis. Explicit workflows can direct this process, but a controller that prevents premature submission may also close useful analytical opportunities. We introduce PHMGraph, a training-free control formulation that separates active-instruction indexing from progress-gated tool exposure under a common procedural catalog, released data scope, fitted expert pool, language model and evaluator. A four-condition design distinguishes the effect of an active-block pointer with global tools from the additional effect of gating after indexing. We use standard finite-horizon value accounting to interpret two task-supported execution boundaries: numerical prediction precedes submission, and successful prediction closes ordinary subsequent analysis in the error-free, event-free diagnosis path. The primary comparison uses pooled diagnosis Macro-F1 over assigned first attempts, retaining canonical non-submissions and provider interruptions; replay performance is secondary. Paired PHM outcomes remain to be collected, so the present analysis establishes the method, its executable boundaries and the comparisons needed to determine its diagnostic effect.

## 1. Introduction

Reliable equipment diagnosis requires both a useful numerical method and a procedure that applies it to the available measurement. Bearing-diagnostic benchmarks expose substantial variation in the difficulty of extracting fault evidence, while transfer learning improves the representations used for classification [@smith2015; @shao2019]. The Paderborn benchmark further distinguishes experimentally generated bearing damage and measurement conditions [@lessmeier2016]. These developments primarily strengthen the mapping from measurements to predictions. A tool-using PHM agent introduces an additional decision layer: it chooses which computation to invoke, interprets the returned evidence and decides when to deliver a diagnosis. A capable predictor that is never called cannot contribute to that delivered result.

Language-model agents offer a way to coordinate these decisions without replacing every numerical component. Coscientist and ChemCrow couple language reasoning with scientific tools [@boiko2023; @bran2024], while ReAct interleaves reasoning with environmental actions and Toolformer learns tool use from API-augmented examples [@yao2023react; @schick2023toolformer]. For PHM, this suggests an architecture in which signal analysis and prediction remain executable numerical operations, while the agent organizes their use. The resulting scientific question concerns the relation between available capability, its actual execution and the final diagnosis—not merely whether an agent can produce an intelligible report.

Explicit workflows are an established response to this coordination problem. StateFlow uses state-dependent instructions and transitions, and evaluates refined reactive prompting and state-removal variants [@wu2024stateflow]. PHMForge studies industrial tool orchestration, including verification, distractor-tool and discovery controls [@li2026phmforge]. TimeSage-MT compares code-enabled, skill-guided and orchestrated time-series systems and reports a grounding–flexibility trade-off [@kong2026timesagemt]. These results motivate a more specific question: **with the same PHM procedures and numerical capabilities available, what changes when an agent is told which instruction is active, and what changes when the workflow additionally restricts executable actions?**

These are different interventions. An active-instruction pointer locates an existing procedure within a shared catalog. A progress gate changes when computations and submission are available. The latter can suppress an early answer that has no numerical prediction behind it, yet also prevent further analysis once a prediction exists. Procedural progress and diagnostic sufficiency are different: executing a predictor does not establish that its label is correct or that every useful computation has been exhausted. Conversely, a removed action matters to the observed task only when the unrestricted agent would select it and its consequences affect the delivered result.

Three challenges follow. First, instruction content and instruction selection must be separated: adding a better procedure only to the graph agent would mix control with domain knowledge. Second, restrictions must be described through the actions they remove, rather than through state names or tool counts. A prediction-ready state need not verify a prediction, and fewer visible tools can encode progress as well as reduce choice. Third, the comparison must retain failures to deliver an answer. Evaluating only successful submissions selects a treatment-dependent subset and can conceal an operationally important effect.

We address these challenges with PHMGraph. A public-history controller computes analysis progress and independently exposes an opaque instruction-block index and a progress-dependent tool menu. Every condition receives the same complete procedural catalog. A paired four-condition design measures indexing under global tools and the incremental gate effect after indexing, using diagnosis as the primary task. The analysis connects these comparisons to the opportunities that the implemented controller permits or excludes.

The contributions are threefold:

1. **A content-matched PHM control formulation.** PHMGraph separates active-instruction indexing from progress-gated tool exposure while keeping procedural content and potential numerical capabilities common. This formulation makes instruction localization and executable workflow restriction independently manipulable components of a PHM agent.
2. **A task-supported analysis of the control trade-off.** Using established value accounting to separate excluded opportunities from retained-action selection, we characterize prediction-before-submission and post-prediction closure in the supported diagnosis path. The analysis distinguishes workflow progress from diagnostic sufficiency and specifies the behavior needed to connect a restriction to task outcomes.
3. **A paired, first-attempt evaluation design for delivered diagnosis.** Two prespecified Macro-F1 contrasts separate indexing from the additional gate effect, retain canonical failed deliveries, and use bearing-clustered uncertainty. Trajectory observations then distinguish numerical execution, premature submission and post-prediction continuation without replacing the task endpoint with procedural compliance.

### 1.1 Related work and positioning

**Numerical PHM capability.** Bearing-diagnostic benchmarks and deep transfer learning establish signal-processing, dataset and representation foundations [@smith2015; @lessmeier2016; @shao2019]. MOMENT extends pretrained numerical representations to multiple time-series tasks [@goswami2024]. These approaches change or evaluate numerical capability. The present study holds the available fitted experts fixed and instead examines their actual use by the agent.

**Tools and reusable experience.** Toolformer learns API use, ToolLLM combines training, tool retrieval and tool-use paths, and Gorilla studies API generation with retrieved documentation [@schick2023toolformer; @qin2023toolllm; @patil2023gorilla]. Scientific systems such as Coscientist and ChemCrow coordinate domain-specific computations [@boiko2023; @bran2024]. ReAct organizes actions through interaction history; Reflexion adds feedback across attempts; Agent Workflow Memory induces reusable routines from experience [@yao2023react; @shinn2023reflexion; @wang2024awm]. The PHM comparison here adds neither tool training nor treatment-only knowledge or experience.

**Structured reasoning and workflows.** Finite controllers and reward machines provide established representations of policy or task structure [@hansen1997; @icarte2018]. StateFlow implements state-dependent instructions, execution and transitions, while StateAct combines goal prompting and state tracking [@wu2024stateflow; @rozanov2025stateact]. Tree of Thoughts and Graph of Thoughts organize alternative reasoning continuations and their dependencies [@yao2023tot; @besta2024got]. Language Agent Tree Search uses search and environment feedback, AFlow optimizes code-represented workflows, and AutoGen supports configurable multi-agent conversations [@zhou2024lats; @zhang2025aflow; @wu2023autogen]. PHMGraph instead studies two interface interventions around one fixed public-history controller and one underlying agent.

**Industrial and time-series agents.** ReActXen adds review and reflection for industrial data access, CodeReAct embeds executable-code reasoning in asset-management workflows, and SPIRAL combines planning, simulation and criticism within tree search [@rayfield2025reactiot; @zhou2026codereact; @zhang2026spiral]. TimeART trains tool-augmented time-series reasoning [@wu2026timeart]. PHMForge's industrial tool controls and TimeSage-MT's paired system comparisons are especially relevant: they already examine orchestration and the trade-off between structured grounding and flexibility [@li2026phmforge; @kong2026timesagemt]. The current question is narrower: instruction localization and incremental progress gating under one common PHM catalog.

**Outcome evaluation.** AgentBench, GAIA and WebArena assess interactive or functional task completion, while tau-bench additionally emphasizes consistency in tool–agent–user interaction [@liu2023agentbench; @mialon2023gaia; @zhou2024webarena; @yao2024tau]. Statistical comparison requires explicit experimental units and uncertainty rather than isolated point estimates [@demsar2006; @agarwal2021]. These foundations support a paired, bearing-level diagnostic comparison; neither a valid tool call nor a valid transition substitutes for the final diagnosis. The action-restriction and value foundations used in the analysis are developed in Section 2.

## 2. Basic Theory and Problem Formulation

### 2.1 Problem setting

We consider a tool-using agent that diagnoses a bearing from a released vibration measurement. An episode begins with a task description and public data handles. The agent may request bounded signal access, inspect available numerical methods, compute features, invoke a fitted predictor and submit a diagnosis with supporting artifacts. The output is an accepted label from three declared fault classes, or a recorded terminal outcome without an accepted diagnosis. Replay over an ordered sequence of released windows is a secondary task.

The shared computational setting comprises the language model, procedural instructions, numerical tools, fitted expert parameters and execution budgets. A tool request is an action $a_t=(u_t,v_t)$: a tool name and its arguments. Public history $h_t$ contains the task context, previous requests, returned artifacts, errors and remaining resources. A tool result establishes what a computation returned, not that the returned diagnosis is correct. Ground-truth class $c_k$ for episode $k$ is held by the evaluator and never supplied to the controller.

The primary diagnosis scope exposes one distinct raw array under fixed sample, window and channel specifications. Rereading it can create another reference to the same array, not a new independent measurement. This task still permits alternative analyses of that array. Budget limits include tool interactions and model-generation resources; exhausting them without an accepted diagnosis is an operational outcome rather than an excluded case.

### 2.2 Relevant theoretical foundations

**History-conditioned tool use and finite controllers.** ReAct conditions successive decisions on reasoning and environmental observations [@yao2023react]. Finite-state policies under partial observability and state-driven language-agent workflows provide established ways to organize such interactions [@hansen1997; @wu2024stateflow]. A progress summary computed from public history is an abstraction for decision organization; it need not be a sufficient belief state or a fault posterior. The full history, together with time and remaining budget, can instead serve as the state for finite-horizon value accounting.

**Action restriction and selection.** Invalid-action masking excludes actions that an environment does not admit, whereas a workflow restriction may exclude a valid computation because a prescribed phase has ended [@huang2022masking]. Confidence-based action elimination additionally requires evidence for removing alternatives [@evendar2006]. A progress label alone provides no such confidence certificate.

For a finite horizon $H$ with zero terminal continuation, let $V_t^*,Q_t^*$ denote unrestricted optimal expected task values. At a history state $\xi$, let $A_R(\xi)$ be a nonempty retained subset of valid actions. Assuming the maxima are attained, define

$$
\ell_t^{\mathrm{opp}}(\xi)=V_t^*(\xi)-\max_{a\in A_R(\xi)}Q_t^*(\xi,a),
\qquad
\ell_t^{\mathrm{sel}}(\xi,a_t)=\max_{a\in A_R(\xi)}Q_t^*(\xi,a)-Q_t^*(\xi,a_t).
$$

For a policy supported on $A_R$,

$$
V_0^*(\xi_0)-V_0^\pi(\xi_0)
=\mathbb E_\pi\sum_{t=0}^{H-1}
\left[\ell_t^{\mathrm{opp}}(\xi_t)+\ell_t^{\mathrm{sel}}(\xi_t,a_t)\right].
$$

The two terms add to the optimal advantage gap. Bellman substitution and telescoping then give the identity, as in standard policy-value analysis [@schulman2015]. Its purpose here is to distinguish a lost opportunity from poor selection among remaining opportunities. It is not a new control theorem. The identity concerns expected episodic return, not the non-additive pooled Macro-F1 defined below. Real agent errors also need not satisfy the supported-policy assumption. Unobserved optimal action values cannot be recovered from tool counts alone; additional support or identification assumptions are needed [@jiang2016; @khan2024].

**Information and bounded computation.** A deterministic annotation of a fully rendered history adds no information to an unrestricted history-conditioned decision maker: that decision maker could compute the annotation itself. Likewise, restricting available actions cannot increase its unrestricted optimum. This statement concerns task utility with identical feasible resources and no annotation-specific processing cost, not equality of token use, latency or priced net value. These observations do not imply behavioral equivalence for a finite language model. Explicit organization may change how effectively it uses existing information, and a smaller menu may simplify selection while excluding useful alternatives. These are empirical questions about bounded computation, not claims that control creates new diagnostic evidence.

### 2.3 Mathematical formulation

Let $X_k$ collect the fixed conditions for episode $k$: task and released data scope, procedural content, global tool catalog, language-model settings, fitted numerical experts, budgets and evaluator. These conditions are matched across interventions; they do not require identical realized computations. Let $Z=(i,g)$ specify whether an explicit instruction locator and a temporal tool restriction are enabled. Their realization is deferred to Section 3.

For each assigned episode,

$$
\tau_k^Z\sim P_Z(\cdot\mid X_k),
\qquad T_k^Z=t(\tau_k^Z),
\qquad Y_k^Z=y(\tau_k^Z,c_k).
$$

Here $\tau$ is the public action–observation trajectory, $T$ contains process measurements, and $Y$ is an evaluator-derived outcome record. Process measurements include numerical-prediction use, submission timing, analytical continuation and resource use. The outcome record distinguishes an accepted label from a canonical terminal non-submission. A request whose final record is indeterminate is neither a fabricated non-submission nor a replaceable unattempted case.

![**Problem formulation and observation boundaries.** Fixed conditions $X_k$ determine the common computational setting; intervention $Z$ changes the decision interface. The resulting trajectory $\tau_k^Z$ supplies process measurements $T_k^Z$ and the submitted diagnosis. The evaluator alone accesses the true class $c_k$ to construct $Y_k^Z$. The cohort metric $M(D_Z)$ aggregates matched first outcomes. Arrows indicate execution and measurement dependencies, not an identified causal mediation model. No proposed controller architecture is introduced in this figure.](../assets/figures/phmgraph_problem_formulation.svg)

Figure 1 distinguishes three objects that a workflow comparison can otherwise conflate: a computation being available in $X$, its selection along $\tau$, and its contribution to the delivered outcome $Y$. The process measurements do not replace the outcome, and the private target has no feedback edge to the agent.

For the matched assigned cohort $\mathcal I$, let $D_Z=\{Y_k^Z:k\in\mathcal I\}$ contain canonical first-attempt outcomes. The primary functional is

$$
M(D_Z)=\frac{1}{3}\sum_{c=1}^{3}
\frac{2\mathrm{TP}_c(D_Z)}{2\mathrm{TP}_c(D_Z)+\mathrm{FP}_c(D_Z)+\mathrm{FN}_c(D_Z)}.
$$

Counts are pooled across the cohort. A canonical non-submission contributes a false negative to its true class and is not a fourth averaged class. The cohort contains the three declared classes; native undefined-metric handling is retained outside this supported setting. Macro-F1 is a functional of the joint outcome set, not the mean of episode-level F1 values.

The two prespecified comparisons are

$$
\Delta_{\mathrm{index}}=M(D_{10})-M(D_{00}),
\qquad
\Delta_{\mathrm{gate}}=M(D_{11})-M(D_{10}).
$$

Their repeated-execution targets are expectations of these whole-cohort differences conditional on the fixed assignments, rather than differences of per-episode F1 expectations. An analogous difference of explicitly normalized trajectory summaries can describe $T$. Conditioning a process rate on reaching prediction or submission produces a treatment-dependent subset; such rates are descriptive, not identified mediation effects.

### 2.4 Existing limitation and research gap

StateFlow already supplies state-dependent execution and ablations; PHMForge already studies industrial orchestration controls; TimeSage-MT already compares structured and less constrained time-series agents [@wu2024stateflow; @li2026phmforge; @kong2026timesagemt]. The relevant gap is therefore not the absence of graphs or controlled experiments. It is the unresolved decomposition of a specified PHM control interface under common procedural content: whether locating an existing instruction changes delivered diagnosis, and whether an additional executable restriction helps or harms after that locator is present.

A jointly changed prompt and tool set cannot answer these two questions separately. Nor does legal execution establish diagnostic sufficiency. A restriction can be present without changing behavior, and changed behavior can leave the final diagnosis unchanged. The formulation requires a task-supported link from the manipulated interface through observed execution to the same diagnostic endpoint. Zero or adverse task effects, or nonuse of the excluded opportunities, are valid outcomes that can reject a proposed beneficial mechanism.

### 2.5 Research objective

This work investigates the separate effects of explicit instruction localization and temporal tool restriction on first-attempt PHM diagnosis under matched computational conditions. It seeks to determine whether observed differences arise alongside greater numerical execution, suppressed premature submission, altered analytical continuation or changed diagnostic labels. The next section specifies the two interventions and the public-history update that makes them executable.

## 3. Method

### 3.1 Overview

PHMGraph implements $Z=(i,g)$ around one unchanged tool-using language agent. Figure 2 shows the shared components and the intervention points. At each turn, a deterministic progress function summarizes public execution history. One switch exposes the identifier of the relevant instruction in a catalog already visible to every condition. The other switch exposes and enforces a phase-dependent menu drawn from the common numerical tools. The language model proposes one request; the shared environment either executes an admitted request or records an error. Both successful observations and errors update the same history used on the next turn. Accepted submission produces the output, while the true diagnosis remains evaluator-side.

![**PHMGraph overview and execution loop.** The common history $h_t$, catalog $B$, language model $\pi_\theta$, numerical tools and evaluator are inherited components. Public-progress abstraction $f$ adapts established state-driven control. The independently switched locator $iL(s_t)$ and menu $\Gamma_g(s_t)$ constitute the studied control interface. The same menu is supplied to the model and to tool-name admission; argument validation and numerical computation remain shared. Errors are returned to public history rather than silently repaired. An accepted submission is evaluated against private labels. Step numbers refer to Algorithm 1.](../assets/figures/phmgraph_method_overview.svg)

The diagram separates locating instructions from changing executable opportunities. Section 3.2 defines the locator, Section 3.3 defines menu presentation and admission, Section 3.4 specifies progress and its exceptions, and Algorithm 1 assembles the loop. No simulator, search tree, additional model or learned diagnostic representation is introduced.

### 3.2 Mechanism I: active-instruction indexing

The ordered catalog is $B=((b_j,d_j))_{j=1}^{6}$, with opaque identifiers B01–B06 and fixed instruction texts $d_j$. Every condition receives the entire catalog in the same order on every request. The six instructions concern bounded acquisition, analysis-family selection, typed-feature construction, numerical prediction, error correction and supported submission. Their content is common to all arms.

Let $s_t=f(h_t)$ be the current progress phase and $L(s_t)$ its catalog identifier. With $i=1$, the request appends only this identifier; with $i=0$, it appends no locator. For the common history renderer $\rho$,

$$
x_t^{ig}=\rho(h_t,B)\oplus iL(s_t)
\oplus\operatorname{Schema}\bigl(\Gamma_g(s_t)\bigr),
\qquad a_t\sim\pi_\theta(\cdot\mid x_t^{ig}).
$$

The zero term denotes omission, not the numeral zero printed in the prompt. Historical state annotations are removed from model-visible tool messages in all four conditions, while returned numerical payloads and errors are preserved. Thus, the locator points to existing instructions rather than supplying new procedural knowledge. The effect remains conditional on this catalog and its selection burden; equal-width identifiers do not guarantee equal tokenizer cost.

### 3.3 Mechanism II: progress-gated tool exposure

Let $\mathcal U$ be the global set of tool names. The unmasked interface uses $\Gamma_0(s)=\mathcal U$; the masked interface uses the phase-specific subset $\Gamma_1(s)$. The selected menu is presented to the model and passed unchanged to the executor's name-admission check. For a proposed request $a_t=(u_t,v_t)$,

$$
o_{t+1}=\begin{cases}
\mathcal E_{\mathrm{tool}}(u_t,v_t;h_t),&u_t\in\Gamma_g(s_t),\\
\operatorname{error}(u_t),&u_t\notin\Gamma_g(s_t).
\end{cases}
$$

The shared tool environment $\mathcal E_{\mathrm{tool}}$ still validates arguments, data scope and artifact types, and may itself return an error. Tool-name admission is not proof of valid arguments, numerical success or diagnostic correctness. Unavailable requests are recorded; they are not projected onto another action. Malformed model responses and provider failures retain the shared runtime's terminal handling rather than being converted to successful tool steps.

| Phase / block | Exposed tools in the gated diagnosis interface |
|---|---|
| Inspect / B01 | Data search, description, bounded reading and summary |
| Hypothesize / B02 | Operator catalog, model catalog and data summary |
| Analyze / B03 | Data summary; operator catalog, schema and execution; model catalog and schema |
| Check / B04 | Data summary; operator schema and execution; model catalog, schema and prediction |
| Recover / B05 | Data description, reading and summary; operator and model catalogs/schemas; operator execution and model prediction |
| Submit / B06 | Submission only |

These menus encode distinct phases as well as removing choices. The gate effect therefore includes implicit progress information, changed schema exposure, suppression of early submission and altered execution sequences. It is not a pure topology or action-count effect. In particular, Check permits prediction and further feature computation before submission becomes available; its name does not imply a separate post-prediction verification mechanism.

### 3.4 Public-progress update and execution boundaries

For primary diagnosis, define four indicators from successful public calls: $r(h)$ for a bounded read, $d(h)$ for inspection of either the operator or model catalog, $p(h)$ for numerical prediction, and $m(h)$ for a model-schema request. Let $e(h)$ indicate that the most recent recorded action failed. The controller applies the following precedence:

$$
f(h)=\begin{cases}
\mathrm{Recover},&e(h)=1,\\
\mathrm{Inspect},&e(h)=0,\ r(h)=0,\\
\mathrm{Hypothesize},&e(h)=0,\ r(h)=1,\ d(h)=0,\\
\mathrm{Submit},&e(h)=0,\ r(h)=d(h)=p(h)=1,\\
\mathrm{Check},&e(h)=0,\ r(h)=d(h)=m(h)=1,\ p(h)=0,\\
\mathrm{Analyze},&\text{otherwise}.
\end{cases}
$$

This precedence also applies to global-tool conditions, which can issue requests out of the prescribed order. A successful prediction before catalog inspection does not bypass the earlier catalog condition. State is recomputed from history rather than advanced merely because a model names a desired phase. Following execution, the shared history update is

$$
h_{t+1}=h_t\oplus(a_t,o_{t+1},\text{recorded resource use}).
$$

On a supported, error-free, event-free gated diagnosis trajectory, three execution properties follow directly. A successful read removes reading from the ordinary subsequent menus. Submission is unavailable before successful prediction. Once the ordinary path reaches a successful prediction, only submission remains exposed. These properties characterize the mechanism; they do not establish a diagnostic gain. The one-window scope means that suppressing rereads does not remove a second distinct raw observation, whereas post-prediction closure can remove alternative processing of the same observation.

Errors qualify these boundaries. A failed submission or unavailable request can activate Recover and reopen analysis or reading. Continued errors can keep the controller in recovery until the budget is exhausted. The instruction to make a corrected call is guidance, not a proof of one-step recovery or nonrepetition.

Replay retains its separate sample-bound progression. The next unpredicted released sample is analyzed; feature-call progress counts successful operator calls associated with that sample, and eleven such calls trigger prediction readiness in the inspected profile. This is an execution-count threshold, not eleven distinct features or an estimated evidence-sufficiency threshold. After all released samples have predictions, submission is exposed. The primary formulation contains no condition-change event; Monitor/Revise and dynamic adaptation are outside this intervention.

### 3.5 Algorithm

**Algorithm 1. PHMGraph under a fixed procedural catalog.**

**Input:** public task and released scope, common catalog $B$, global tools $\mathcal U$, fixed model $\pi_\theta$, fitted numerical tools, budgets, switches $(i,g)$.

**Output:** canonical first-attempt outcome and public trajectory; evaluator labels are not algorithm inputs.

1. Initialize public history and resource accounting from the assigned task.
2. While the episode is nonterminal and its declared budget permits a decision, compute $s_t=f(h_t)$ from recorded successful calls and the latest error.
3. Render the same complete catalog and sanitized public history; append $L(s_t)$ exactly when $i=1$.
4. Set $\Gamma_g(s_t)$ to the global or gated menu, and provide its schemas to the fixed language model.
5. Request one model decision. On a native provider or response-format terminal failure, retain that first outcome and stop; do not switch models or retry to replace it.
6. Check the proposed tool name against the same $\Gamma_g(s_t)$. Record an unavailable-action error when rejected; otherwise invoke the shared validating tool environment.
7. Append the request, returned numerical result or error, and recorded usage to history. Recompute progress only at the next iteration; do not insert an unobserved successful action.
8. Stop on an accepted submission. If the budget or another native terminal condition ends the episode first, retain its canonical terminal non-submission. An indeterminate persisted attempt requires resolution rather than automatic resend or an invented score.

The four settings of the switches instantiate the conditions in Section 2.3. Algorithm 1 changes only instruction localization and executable tool exposure, while leaving numerical fitting, task admission and scoring to the shared system. Exact source bindings and symbol-to-experiment correspondence are supplied with the reproducibility materials.

## 4. Testable consequences

The opportunity–selection accounting in Section 2 motivates opposing, rather than uniformly beneficial, predictions. Indexing can change task performance when the bounded model uses the designated instruction differently from the same catalog without a pointer. Gating can improve delivery when it prevents unsupported early submission, or impair diagnosis when it removes a continuation that would have improved the final label. The gate can also be inactive because unrestricted agents never select the excluded actions.

These possibilities lead to three observable checks alongside the task contrasts: whether numerical prediction and submission occur, whether analysis continues after prediction when permitted, and whether the first predicted label and final supported label differ in correctness. Additional artifact references count as changed evidence only when their resolved numerical contents differ. Greater compliance alone supports a procedural claim; a diagnostic claim requires the common evaluator's task outcome. Conditional trajectory rates remain descriptive, and neither changed labels nor extra computation imply improvement without their corresponding evaluated outcomes.

## 5. Paired first-attempt evaluation

### 5.1 Primary endpoint and contrasts

Diagnosis is primary. The endpoint is pooled Macro-F1 over the three declared diagnosis classes and all assigned canonical first-attempt outcomes. An attempt with no accepted diagnosis is retained as `no_submission`: it contributes a false negative to its true class and is not averaged as a fourth diagnosis class. This operational endpoint therefore reflects both delivery and label quality.

The two primary contrasts are defined in Section 2.3: indexing under global tools and gating after indexing. The four-condition implementation is given in Section 3. Replay Average Precision, with its unchanged assigned-window and missing-score rules, is secondary. The remaining simple effects and factorial interaction are exploratory. Earlier Graph-versus-Generic or semantic-cue profiles remain separate comparisons and are not substituted for these controls.

### 5.2 Assignment, resources and uncertainty

Bearing splits, class labels, sample/window/channel specifications, replay order, reference-fitting scope, model settings and task budgets are fixed before evaluation. The four conditions run in independent agent sessions within matched bearing, task, rotation and repeat blocks. Randomized cyclic order balances condition positions to within one occurrence per task/rotation/repeat/budget stratum. This balances positions rather than guaranteeing elimination of provider drift or carryover. Interrupted blocks retain their original assignments and any resumed time gaps.

Uncertainty uses a paired, diagnosis-class-stratified bearing bootstrap. Within each true class, bearings are resampled with their windows and model repeats, and the same draws apply to every term in a contrast. Class-specific bearing counts remain fixed, so the intervals condition on the cohort's class composition. The two prespecified effects receive nominal 97.5% percentile intervals through Bonferroni allocation. These are interval estimates, not claims of exact small-sample coverage or control of all provider randomness. A one-bearing smoke run has no inferential interpretation.

A request reserve must cover the remaining members of a block before that block starts. Its invocation ceiling is an operational safeguard, distinct from per-condition task budgets and from the final study size. Existing first outcomes are reused without refitting the common numerical reference. Numerical reference execution and agent execution must use matching resolved task/data/fit assignments; readable metadata alone does not establish waveform correspondence.

### 5.3 Incomplete delivery and mechanism observations

A provider interruption that produces a canonical terminal outcome remains in its assigned first attempt. A durable request record without a complete canonical outcome is indeterminate and blocks automatic resend; it is neither an inferred diagnostic failure nor an unattempted case. A complete primary comparison requires all assigned canonical first outcomes. This distinction prevents outcome-dependent replacement while preserving genuinely unresolved attempts.

Alongside Macro-F1, report submission rate, the three-class confusion matrix with a `no_submission` column, and the composition of provider interruptions, malformed responses, unavailable actions and budget exhaustion. Macro-F1 conditional on accepted submissions is a descriptive sensitivity analysis. Its treatment-dependent denominator is not a replacement for the operational endpoint.

Mechanism observations include attempted submission before numerical prediction, post-prediction analytical actions, changes from the first prediction to the final submitted label, numerical support changes, and submission-error recovery. Every conditional rate identifies its denominator, including attempts that never reach prediction or submission. These are descriptive trajectory analyses rather than causal subgroups. Resource reporting retains known usage, unknown interruption billing, timestamps and resumed-block gaps.

## 6. Results

Matched PHM first-attempt outcomes are not yet available. The two primary diagnosis effects, secondary replay effects and operational costs are therefore unestimated. The execution boundaries and hypotheses in Sections 3–4 specify the intervention and its testable consequences; they are not empirical estimates of diagnostic improvement or harm.

### 6.1 Comparisons under separate protocols

Earlier Graph–Generic, dynamic-revision, cross-dataset and repeated-trial comparisons address different intervention or task definitions. Their results, when available, are reported separately and are not pooled with the current first-attempt indexing–gating contrasts.

<!-- Legacy result insertion slots below retain their original profile definitions.
They are not indexing-by-gating treatment results. Historical renderers must
remain bound to the legacy protocol manifest, not the active experiment. -->
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

PHMGraph distinguishes providing a computation, guiding its use and enforcing its execution order. This separation is important because a fixed expert pool permits different realized numerical paths. A pointer can change which existing instruction receives attention, whereas a gate also changes what remains possible. Their effects should consequently be interpreted at the level of the specified interface and task, rather than attributed to graph structure in general.

The present diagnosis scope contains one distinct raw window. It supports questions about numerical execution, early submission and post-prediction continuation, but not loss of a second independent raw measurement. Full history remains available, and the primary path has no public condition-change event; persistent-memory and dynamic-revision effects require different interventions. The task-primary comparison and its uncertainty also remain conditional on the declared bearing cohort, model, catalog and budgets.

A useful next empirical conclusion must therefore identify which of three outcomes occurs: improved delivery, changed diagnostic label quality, or an inactive restriction. The same design can reveal adverse effects. That symmetry is central to deciding when an explicit PHM workflow is helpful rather than treating additional control as an automatic improvement.

## References
