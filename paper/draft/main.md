---
bibliography: ../refs/phmgraph_review_2026.bib
link-citations: true
---

# PHMGraph: Separating Instruction Indexing from Workflow Gating in Tool-Using PHM Agents

## Abstract

A prognostics and health management (PHM) agent must turn available numerical capabilities into a delivered diagnosis. PHMGraph studies two control interventions under a common procedural catalog, released data scope, fitted expert pool, language model and evaluator: appending a correct active-block pointer, and jointly gating tool-schema exposure and executable tool names by public progress. Four conditions support two prespecified sequential simple effects: the pointer with global tools, and the additional gate with the pointer present. We distinguish correct label delivery from delivery supported by a task-matched numerical prediction and its required feature references. Pooled first-attempt diagnosis Macro-F1 remains primary; a prospectively specified grounded counterpart measures the latter outcome on the same cohort. The method also exposes a testable boundary: after successful prediction, the ordinary gated path permits submission but no further analysis. A diagnostic-opportunity interpretation requires a budget-feasible continuation that can change the supported prediction, rather than merely produce another artifact. Paired PHM effects remain unestimated; the present contribution is the executable comparison and its task-specific measurement design.

## 1. Introduction

Reliable equipment diagnosis requires both a useful numerical method and a procedure that applies it to the available measurement. Bearing-diagnostic benchmarks expose substantial variation in the difficulty of extracting fault evidence, while transfer learning improves the representations used for classification [@smith2015; @shao2019]. The Paderborn benchmark further distinguishes experimentally generated bearing damage and measurement conditions [@lessmeier2016]. These developments primarily strengthen the mapping from measurements to predictions. A tool-using PHM agent introduces an additional decision layer: it chooses which computation to invoke, interprets the returned evidence and decides when to deliver a diagnosis. A capable predictor that is never called cannot contribute to that delivered result.

Language-model agents offer a way to coordinate these decisions without replacing every numerical component. Coscientist and ChemCrow couple language reasoning with scientific tools [@boiko2023; @bran2024], while ReAct interleaves reasoning with environmental actions and Toolformer learns tool use from API-augmented examples [@yao2023react; @schick2023toolformer]. For PHM, this suggests an architecture in which signal analysis and prediction remain executable numerical operations, while the agent organizes their use. The resulting scientific question concerns the relation between available capability, its actual execution and the final diagnosis—not merely whether an agent can produce an intelligible report.

Explicit workflows are an established response to this coordination problem. StateFlow uses state-dependent instructions and transitions, and evaluates refined reactive prompting and state-removal variants [@wu2024stateflow]. PHMForge studies industrial tool orchestration, including verification, distractor-tool and discovery controls [@li2026phmforge]. TimeSage-MT compares code-enabled, skill-guided and orchestrated time-series systems and reports a grounding–flexibility trade-off [@kong2026timesagemt]. These results motivate a more specific question: **with the same PHM procedures and numerical capabilities available, what changes when an agent is told which instruction is active, and what changes when the workflow additionally gates tool exposure and admission?**

These are different interventions. An active-instruction pointer locates an existing procedure within a shared catalog. A progress gate jointly changes which tool schemas are shown and which tool names are admitted. The latter can suppress an early answer that has no numerical prediction behind it, yet also prevent further analysis once a prediction exists. Procedural progress and diagnostic sufficiency are different: executing a predictor does not establish that its label is correct or that every useful computation has been exhausted. Conversely, a removed action matters to the observed task only when the unrestricted agent would select it and its consequences affect the delivered result.


Three challenges follow. First, instruction content and instruction selection must be separated: adding a better procedure only to the graph agent would mix control with domain knowledge. Second, restrictions must be described through the actions they remove, rather than through state names or tool counts. A prediction-ready state need not verify a prediction, and fewer visible tools can encode progress as well as reduce choice. Third, the comparison must retain failures to deliver an answer. Evaluating only successful submissions selects a treatment-dependent subset and can conceal an operationally important effect.

We address these challenges with PHMGraph. A public-history controller computes analysis progress and independently exposes an opaque instruction-block index and a progress-dependent tool menu. Every condition receives the same complete procedural catalog. A paired four-condition design measures two sequential simple effects: appending the correct pointer under global tools, then adding the exposure-and-admission gate with the pointer present. The analysis connects these comparisons to the opportunities that the implemented controller permits or excludes.

The contributions are threefold:

1. **A content-matched PHM control comparison.** Two independently configurable interventions act on the same procedural catalog: an appended active-block pointer and progress-gated tool exposure and admission. Their specified comparisons distinguish interface changes without attributing them to new diagnostic knowledge or pure graph topology.
2. **A task-specific characterization of execution opportunities.** We derive prediction-before-submission and post-prediction closure on the supported ordinary path, and connect them to legal numerical continuations. This separates nominally available analyses from continuations capable of changing a contract-grounded diagnosis.
3. **A first-attempt evaluation design separating delivery from numerical support.** The original operational endpoint is retained alongside a prospective grounded endpoint, with paired bearing-level comparisons and trajectory measurements of mechanism activation. Neither procedural compliance nor unmeasured headroom is treated as evidence of diagnostic improvement.

### 1.1 Related work and positioning

**Numerical PHM capability.** Bearing-diagnostic benchmarks and deep transfer learning establish signal-processing, dataset and representation foundations [@smith2015; @lessmeier2016; @shao2019]. MOMENT extends pretrained numerical representations to multiple time-series tasks [@goswami2024]. These approaches change or evaluate numerical capability. The present study holds the available fitted experts fixed and instead examines their actual use by the agent.

**Tools and reusable experience.** Toolformer learns API use, ToolLLM combines training, tool retrieval and tool-use paths, and Gorilla studies API generation with retrieved documentation [@schick2023toolformer; @qin2023toolllm; @patil2023gorilla]. Scientific systems such as Coscientist and ChemCrow coordinate domain-specific computations [@boiko2023; @bran2024]. ReAct organizes actions through interaction history; Reflexion adds feedback across attempts; Agent Workflow Memory induces reusable routines from experience [@yao2023react; @shinn2023reflexion; @wang2024awm]. The PHM comparison here adds neither tool training nor treatment-only knowledge or experience.

**Structured reasoning and workflows.** Finite controllers and reward machines provide established representations of policy or task structure [@hansen1997; @icarte2018]. StateFlow implements state-dependent instructions, execution and transitions, while StateAct combines goal prompting and state tracking [@wu2024stateflow; @rozanov2025stateact]. Tree of Thoughts and Graph of Thoughts organize alternative reasoning continuations and their dependencies [@yao2023tot; @besta2024got]. Language Agent Tree Search uses search and environment feedback, AFlow optimizes code-represented workflows, and AutoGen supports configurable multi-agent conversations [@zhou2024lats; @zhang2025aflow; @wu2023autogen]. PHMGraph instead studies two interface interventions around one fixed public-history controller and one underlying agent.

**Industrial and time-series agents.** ReActXen adds review and reflection for industrial data access, CodeReAct embeds executable-code reasoning in asset-management workflows, and SPIRAL combines planning, simulation and criticism within tree search [@rayfield2025reactiot; @zhou2026codereact; @zhang2026spiral]. TimeART trains tool-augmented time-series reasoning [@wu2026timeart]. PHMForge's industrial tool controls and TimeSage-MT's paired system comparisons are especially relevant: they already examine orchestration and the trade-off between structured grounding and flexibility [@li2026phmforge; @kong2026timesagemt]. The present question concerns the two specified PHM interfaces under a common catalog and numerical contract, not the first use of workflow control.

**Outcome evaluation.** AgentBench, GAIA and WebArena assess interactive or functional task completion, while tau-bench additionally emphasizes consistency in tool–agent–user interaction [@liu2023agentbench; @mialon2023gaia; @zhou2024webarena; @yao2024tau]. Statistical comparison requires explicit experimental units and uncertainty rather than isolated point estimates [@demsar2006; @agarwal2021]. These foundations support a paired, bearing-level diagnostic comparison; neither a valid tool call nor a valid transition substitutes for the final diagnosis.

## 2. Basic Theory and Problem Formulation

### 2.1 Problem setting

We consider an agent that diagnoses a bearing from a released vibration measurement. An episode begins with a task description and public data handles. Available actions provide bounded signal access, numerical-method inspection, feature computation, fitted prediction and diagnosis submission. The output is a submitted label from three declared fault classes or a terminal outcome without an accepted diagnosis. Replay over an ordered sequence of released windows is secondary.

A request is $a_t=(u_t,v_t)$, comprising a tool name and arguments. Public history $h_t$ contains task context, previous requests, returned artifacts, errors and remaining resources. The shared setting fixes the language model, procedures, numerical tools, fitted parameters and budgets. Ground-truth class $c_k$ for episode $k$ is evaluator-only. Submission acceptance, agreement with a numerical prediction and correctness against $c_k$ are distinct properties.

The primary task exposes one distinct raw array under fixed sample, window and channel specifications. Rereading can create another reference to that array, not an independent measurement. Alternative computations must satisfy the existing numerical input contract and fit the remaining budget. A longer trajectory therefore need not contain another admissible prediction. Resource exhaustion without an accepted diagnosis remains an operational outcome.

### 2.2 Relevant theoretical foundations

**History-conditioned decisions.** ReAct conditions successive actions on reasoning and observations [@yao2023react]. Finite controllers under partial observability and state-driven language-agent workflows provide established ways to organize such decisions [@hansen1997; @wu2024stateflow]. A progress summary is an execution abstraction, not necessarily a sufficient belief state or a fault posterior.

**Restricted action selection.** Invalid-action masking removes actions that an environment disallows; a workflow gate can instead remove a valid computation because a phase has ended [@huang2022masking]. Confidence-based elimination requires evidence for discarding alternatives, which a progress label alone does not supply [@evendar2006]. For standard finite-horizon optimal values $V_t^*,Q_t^*$, a nonempty retained subset $A_R(\xi)$ of valid actions, attained maxima and $a\in A_R(\xi)$,

$$
\begin{aligned}
V_t^*(\xi)-Q_t^*(\xi,a)
&=\underbrace{V_t^*(\xi)-\max_{u\in A_R(\xi)}Q_t^*(\xi,u)}_{\text{excluded opportunity}}\\
&+\underbrace{\max_{u\in A_R(\xi)}Q_t^*(\xi,u)-Q_t^*(\xi,a)}_{\text{selection within retained actions}}.
\end{aligned}
$$

Here $\xi$ includes history, time and remaining budget. This algebraic separation uses standard policy-value quantities [@schulman2015]; it distinguishes excluding a valuable action from choosing poorly among retained actions. It neither decomposes pooled Macro-F1 nor makes unobserved optimal values identifiable from tool counts [@jiang2016; @khan2024]. Its empirical role is to motivate checking whether an excluded, feasible continuation actually changes numerical output and delivered diagnosis.

**Information and bounded computation.** A deterministic annotation of a fully available history supplies no new information to an unrestricted decision maker that can compute it. Restricting feasible actions cannot improve that decision maker's optimal task utility under identical resources and no annotation-specific processing cost. A finite language model may nevertheless respond differently to an explicit annotation or a shorter menu. Prompt length, salience and execution cost are then part of the implemented interface, not evidence that control creates new diagnostic information.

### 2.3 Mathematical formulation

Let $X_k$ collect the fixed task, released data scope, procedural content, global tool surface, numerical input contract, fitted experts, language-model settings, budgets and evaluator. Matching $X_k$ across conditions fixes potential capability, not realized computation. Let $Z=(i,g)$ indicate the presence of an active-block pointer and a progress-dependent tool-exposure-and-admission gate. Section 3 supplies their executable definitions.

$$
\tau_k^Z\sim P_Z(\cdot\mid X_k),
\qquad T_k^Z=t(\tau_k^Z),
\qquad Y_k^Z=y(\tau_k^Z,c_k).
$$

The public trajectory $\tau$ determines process measurements $T$, including prediction use, continuation, submission timing and resource use. Outcome record $Y$ contains the delivered label, termination status and numerical-support assessment. Let $\hat c_k^Z\in\{1,2,3,\varnothing\}$ be its accepted label, with $\varnothing$ denoting a resolved terminal non-submission. An indeterminate attempt is unresolved, not a fourth outcome that can be assigned a fabricated score.

![**Problem formulation and observation boundaries.** Fixed $X_k$ and assigned interface $Z$ generate public trajectory $\tau_k^Z$ and process measurements $T_k^Z$. The evaluator alone uses private class $c_k$ to assess outcome $Y_k^Z$. The cohort functional $M(D_Z)$ measures accepted-label delivery; the grounded counterpart applies the additional numerical-support criterion defined in Section 2.3 to the same outcome records. Arrows show execution and measurement dependencies, not identified causal mediation.](../assets/figures/phmgraph_problem_formulation.svg)

Figure 1 separates capability availability, its use along the trajectory and its evaluated consequence. Numerical support is assessed from the submitted prediction and required feature references; the true class has no feedback edge to the agent.

For assigned cohort $\mathcal I$, let $D_Z=\{Y_k^Z:k\in\mathcal I\}$ contain resolved first-attempt outcomes. The unchanged primary functional is

$$
M(D_Z)=\frac{1}{3}\sum_{c=1}^{3}
\frac{2\mathrm{TP}_c(D_Z)}{2\mathrm{TP}_c(D_Z)+\mathrm{FP}_c(D_Z)+\mathrm{FN}_c(D_Z)}.
$$

Counts are pooled across the cohort. A non-submission contributes a false negative to its true class and is not a fourth averaged class. The supported cohort contains all three classes; native undefined-metric handling applies outside it. This operational metric evaluates delivered labels, including accepted labels without numerical support.

For the grounded secondary endpoint, define $G_k^Z=1$ exactly when an accepted diagnosis agrees with a task-matched numerical prediction and contains that prediction's required feature references. Otherwise $G_k^Z=0$ for a resolved failure of this criterion, including a terminal non-submission. Define

$$
\widetilde c_k^Z=
\begin{cases}
\hat c_k^Z,&G_k^Z=1,\\
\varnothing,&G_k^Z=0,
\end{cases}
\qquad M_{\mathrm{grounded}}(D_Z)=M(\widetilde D_Z),
$$

where $\widetilde D_Z$ changes only the scored labels, retaining the same assigned episodes and true classes. Grounding establishes numerical agreement and required-feature support, not correctness or physical sufficiency. An accepted outcome with unresolved support information leaves the secondary endpoint unresolved; missing support fields are not automatically zero. The operational endpoint remains computable when its own outcome records are complete.

The two primary repeated-execution estimands, conditional on fixed assignments $X_{\mathcal I}$, are

$$
\Delta_{\mathrm{index}\mid g=0}
=\mathbb E\!\left[M(D_{10})-M(D_{00})\mid X_{\mathcal I}\right],
$$

$$
\Delta_{\mathrm{gate}\mid i=1}^{\mathrm{bundle}}
=\mathbb E\!\left[M(D_{11})-M(D_{10})\mid X_{\mathcal I}\right].
$$

Their observed statistics are the corresponding whole-cohort differences. These are sequential simple effects, not factor-averaged main effects: the second is conditional on the pointer being present. The same contrasts applied to $M_{\mathrm{grounded}}$ are secondary. Conditioning a trajectory rate on reaching prediction or submission selects a treatment-dependent subset; such summaries describe execution rather than identify mediation.

### 2.4 Existing limitation and research gap

StateFlow already evaluates state-dependent execution and state ablations; PHMForge studies industrial tool-orchestration controls; TimeSage-MT compares progressively structured time-series systems [@wu2024stateflow; @li2026phmforge; @kong2026timesagemt]. These studies establish workflow control as prior art. They do not by themselves determine the two specified effects under a common PHM catalog, numerical contract and first-attempt endpoint.

Three distinctions make this question testable. An appended correct pointer is not an isolated test of pointer correctness without a matched sham pointer. A gate that changes both schemas and execution admission is a compound intervention. Finally, a legal extra computation may yield no different model-admissible prediction, while an unsupported accepted label can still improve operational accuracy. A diagnostic-opportunity account therefore requires evidence of feasible numerical alternatives, their use and their consequences, rather than a shorter menu or more artifacts alone.

### 2.5 Research objective

This work investigates whether appending a correct active-block pointer changes first-attempt PHM diagnosis under global tools, and whether adding progress-gated exposure and admission changes diagnosis with that pointer present. It distinguishes operational delivery from contract-grounded delivery and tests which feasible numerical continuations connect control to the observed outcome.

## 3. Method

### 3.1 Overview

PHMGraph implements $Z=(i,g)$ around one unchanged tool-using language agent. A deterministic function summarizes progress from public history. The pointer switch appends the identifier of the relevant instruction in a catalog visible to every condition. The gate switch supplies a phase-dependent menu both to the model and to execution admission. The model proposes one request; shared tools return a result or error. Nonterminal feedback updates the public history, while accepted submission or a native terminal event closes the episode. Evaluation subsequently distinguishes the delivered label from its numerical support.

![**PHMGraph overview and execution loop.** Shared history $h_t$, catalog $B$, model $\pi_\theta$, numerical tools and evaluator are inherited components. Public-progress abstraction $f$ adapts state-driven control. The pointer $iL(s_t)$ and gate $\Gamma_g(s_t)$ are separately configurable interventions. The gate jointly changes tool-schema exposure and name admission; both branches receive the same menu. Nonterminal results and errors return to history. Final outcome assessment remains evaluator-side, including both label accuracy and the grounded endpoint. Numbered blocks correspond to Algorithm 1.](../assets/figures/phmgraph_method_overview.svg)

Figure 2 separates the shared numerical capability from its decision interface. Section 3.2 defines pointer presentation; Section 3.3 defines the combined gate; Section 3.4 connects progress to numerical admissibility and closure. Algorithm 1 assembles these mechanisms without introducing another model, a search tree or a learned diagnostic representation.

### 3.2 Mechanism I: appending the active-block pointer

The ordered catalog $B=((b_j,d_j))_{j=1}^{6}$ pairs opaque identifiers B01–B06 with fixed instructions for acquisition, analysis-family selection, typed-feature construction, numerical prediction, error correction and supported submission. Every condition receives the entire catalog in the same order on each request.

Let $s_t=f(h_t)$ and let $L(s_t)$ identify its instruction block. For common history renderer $\rho$,

$$
x_t^{ig}=\rho(h_t,B)\oplus iL(s_t)
\oplus\operatorname{Schema}\bigl(\Gamma_g(s_t)\bigr),
\qquad a_t\sim\pi_\theta(\cdot\mid x_t^{ig}).
$$

Here $iL(s_t)$ denotes an appended active-block sentence when $i=1$ and its omission when $i=0$. It does not duplicate the block's instruction. Historical state annotations are removed equally from model-visible tool messages, preserving numerical payloads and errors. This comparison measures the addition of a correct pointer sentence to the common catalog, including its token and salience changes. It does not separately identify the benefit of a correct versus incorrect pointer or an attention mechanism.

The four interfaces are catalog-global (00), indexed-global (10), catalog-masked (01) and indexed-masked (11). The 01 condition supports the other simple effects and interaction; it is not used to reinterpret the two primary comparisons as averaged main effects.

### 3.3 Mechanism II: progress-gated tool exposure and admission

Let $\mathcal U$ be the common Phase-1 surface of eleven tool names: four data-access tools, three operator tools, three model tools and submission. The additional artifact-description and explicit-stop actions in the broader canonical adapter are outside this declared comparison. The unmasked interface uses $\Gamma_0(s)=\mathcal U$; the masked interface uses the phase subset $\Gamma_1(s)$.

The same selected menu is presented to the model and used for name admission. For request $a_t=(u_t,v_t)$,

$$
o_{t+1}=\begin{cases}
\mathcal E_{\mathrm{tool}}(u_t,v_t;h_t),&u_t\in\Gamma_g(s_t),\\
\operatorname{error}(u_t),&u_t\notin\Gamma_g(s_t).
\end{cases}
$$

The shared environment still validates arguments, data scope and artifact types. Admitted names need not yield successful computations or correct diagnoses. Rejected requests remain errors rather than being projected onto another action.

| Phase / block | Exposed and admitted tools in the gated diagnosis interface |
|---|---|
| Inspect / B01 | Data search, description, bounded reading and summary |
| Hypothesize / B02 | Operator catalog, model catalog and data summary |
| Analyze / B03 | Data summary; operator catalog, schema and execution; model catalog and schema |
| Check / B04 | Data summary; operator schema and execution; model catalog, schema and prediction |
| Recover / B05 | Data description, reading and summary; operator and model catalogs/schemas; operator execution and model prediction |
| Submit / B06 | Submission only |

These menus communicate progress, change schema length and choice, constrain executable requests and alter subsequent resource use. Accordingly, $\Delta_{\mathrm{gate}\mid i=1}^{\mathrm{bundle}}$ is the total effect of this exposure-and-admission interface, not an isolated executor, topology or action-count effect. Check permits prediction and feature computation before submission becomes available; its name does not designate a separate post-prediction verification mechanism.

### 3.4 Public-progress update and numerical execution boundaries

For diagnosis, let $r(h),d(h),p(h),m(h)$ indicate successful bounded reading, inspection of either catalog, numerical prediction and a model-schema request. Let $e(h)$ indicate failure of the latest recorded action. For a nonterminal episode,

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

The precedence applies in all four conditions, including global-tool histories that issue actions out of order. State is recomputed from recorded execution, not advanced because the model names a desired phase. After a nonterminal action,

$$
h_{t+1}=h_t\oplus(a_t,o_{t+1},\text{recorded resource use}).
$$

On the supported error-free, event-free gated path, a successful read removes ordinary rereading, submission is unavailable before numerical prediction, and successful prediction leaves submission as the only ordinary next action. These are execution properties. A nonterminal error can select Recover and reopen reading or analysis; it cannot reopen an episode already terminated by the shared runtime. Repeated errors may consume the budget, so corrected-call guidance provides no recovery guarantee.

The numerical contract determines what the excluded continuation could accomplish. Diagnosis requires six specified time-domain features and four band powers from the prescribed Welch spectrum, all associated with the same raw window. A callable preprocessing or envelope operator does not thereby supply a model-admissible input. Another artifact reference may resolve to identical values. Alternative fitted experts can be queried through the same legal feature interface, but whether they return different labels and remain affordable after the first prediction must be measured. Post-prediction closure is therefore not, by itself, evidence that useful diagnostic information was removed.

Replay retains its separate sample-bound progression: eleven successful operator calls for the active sample trigger prediction readiness in the bound profile. This counts calls, not distinct features or evidence sufficiency. Dynamic condition-change events are outside the primary comparison.

### 3.5 Algorithm

**Algorithm 1. PHMGraph under a fixed procedural catalog.**

**Input:** public task and released scope, common catalog $B$, global tool surface $\mathcal U$, model $\pi_\theta$, fitted numerical tools, budgets and switches $(i,g)$.

**Output:** first-attempt submission or terminal non-delivery and its public trajectory. Private labels are not inputs.

1. Initialize public history and resource accounting from the assigned task.
2. While the episode is nonterminal and the budget permits a decision, compute $s_t=f(h_t)$ from successful calls and the latest error.
3. Render the complete shared catalog and sanitized history; append the active-block sentence exactly when $i=1$.
4. Set $\Gamma_g(s_t)$ to the global or gated menu and supply its schemas to the fixed model.
5. Obtain one model decision. Retain any native provider or response-format terminal outcome without model switching or a replacement attempt.
6. Check the proposed name against the same menu. Record a rejection or invoke the shared validating numerical environment.
7. Append the request, result or error, and resource use. Only a nonterminal episode returns to step 2.
8. Retain the accepted submission or native terminal non-submission. Resolve an indeterminate persisted attempt before scoring it; do not automatically resend it. The evaluator assesses the label and numerical-support criterion on the resulting record.

The algorithm changes pointer presentation and the combined tool interface. Numerical fitting, input admissibility, submission acceptance and the primary scoring rule remain shared. The grounded endpoint is an additional outcome mapping, not a stricter execution gate that changes any condition's behavior.

## 4. Testable consequences

The opportunity–selection distinction motivates opposing hypotheses. A pointer may change numerical execution or delivery by making an existing instruction salient. A gate may prevent premature submission, but it can impair a supported diagnosis through closure only where a legal, budget-feasible continuation can produce a different supported label. Failure to improve either endpoint is also possible.

We therefore distinguish six observations: prediction is reached; a legal alternative fits the remaining budget; the unrestricted agent selects a continuation; resolved numerical output changes; the supported submitted label changes; and correctness changes. These are linked measurements, not an estimated causal mediation chain. New references alone do not establish new numerical evidence, and a changed model output need not change the label. Correctness is evaluated only after submission against private labels.

Each stage is reported against all assigned episodes, with explicitly labelled conditional denominators where useful. Feasibility is evaluated separately from selection using declared numerical contracts, not inferred from missing actions. A gate can be behaviorally inactive in observed traces even when its menu is smaller. An imprecise task contrast does not establish equivalence or general inactivity.

## 5. Paired first-attempt evaluation

### 5.1 Endpoints and planned contrasts

The primary endpoint remains pooled three-class operational Macro-F1 over assigned first attempts, with canonical non-submissions contributing false negatives to their true classes. The two primary contrasts are the sequential simple effects in Section 2.3. The grounded counterpart is a prospectively specified secondary diagnostic endpoint on the same cohort; it neither replaces the primary metric nor drops unsupported submissions from its denominator. Native agreement and required-feature-support fields define its mapping in the accompanying experiment specification.

Report submission rate, grounding rate, both diagnosis confusion matrices with a non-submission column, and provider, response-format, unavailable-action and budget-exhaustion outcomes. Better operational Macro-F1 alone supports better label delivery, not better grounded delivery. Better grounded Macro-F1 supports that specified endpoint even if the operational metric is unchanged. A higher grounding rate without improved diagnostic endpoints supports a procedural result. Interpret all differences with their uncertainty rather than from their sign alone.

Replay Average Precision retains its assigned-window and missing-score rules and remains secondary. Other simple effects and the factorial interaction are exploratory. Historical Graph–Generic or semantic-cue comparisons remain separate protocols.

### 5.2 Assignment, resources and uncertainty

Bearing splits, class labels, sample/window/channel specifications, replay order, reference-fitting scope, model settings and task budgets are fixed before evaluation. Four conditions run in independent sessions within matched bearing, task, rotation and repeat blocks. Randomized cyclic order balances condition positions within one occurrence per task/rotation/repeat/budget stratum. Position balance does not eliminate provider drift; absolute request times, condition positions and resumed-block gaps are retained. A changed provider route or model identity defines a new study, not a continuation of the old comparison.

Uncertainty uses a paired, true-class-stratified bearing bootstrap. Bearings are resampled within class with their windows and repeats, and the same draws apply to every term of a contrast. Class-specific bearing counts remain fixed. The two primary operational effects receive nominal 97.5% percentile intervals through Bonferroni allocation. These intervals condition on the assigned cohort and do not guarantee exact small-sample coverage. Secondary analyses do not inherit this two-contrast error allocation; any confirmatory secondary claim requires its own prespecified inference rule.

An invocation reserve must cover all remaining conditions in a block before it starts. The request ceiling is an operational safeguard, not a sample-size calculation. Retain canonical interrupted outcomes and do not replace failed first attempts. Indeterminate attempts require resolution rather than a fabricated failure or automatic resend. Existing compatible numerical references are reused without treatment-specific refitting.

### 5.3 Numerical headroom before model-provider experiments

Before the four-condition pilot, the same real-data assignments must support bounded reads, disjoint fitting and evaluation bearings, and a Scripted diagnosis whose persisted outcome reproduces the native metric. On a reserved development split, query the existing diagnosis experts through the native feature contract. Record per-sample predictions, pairwise label disagreement and which second-prediction sequences fit the declared remaining resources. Compare resolved numerical contents, not artifact identifiers.

A best-available-expert calculation using development labels describes oracle headroom within that audited pool; it is not a deployable selector and is never exposed to the agent. Zero disagreement limits an opportunity-preservation interpretation within the audited support, without proving that every possible analysis is useless. Test labels must not select experts, revise gates or determine the cohort.

The pilot tests execution and mechanism occurrence, not stable population effects. Before confirmatory execution, freeze the cohort and class composition, window scope, repeats, condition order, exact provider/model settings, timeout handling, budgets, endpoints, contrast family and bootstrap specification. Use pilot variation and event frequency to plan precision, not whether a favorable contrast happened to be significant.

## 6. Results

Matched PHM first-attempt outcomes are not reported here. The two primary effects, grounded secondary contrasts, numerical headroom and operational costs remain unestimated.

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

PHMGraph distinguishes potential numerical capability, its invocation and the supported diagnosis ultimately delivered. Its two comparisons address an appended correct pointer and an additional exposure-and-admission gate, not pure pointer correctness, graph topology or execution restriction in isolation. The fixed expert pool allows different realized computations, but the feature contract determines which computations can support a changed numerical label.

Operational and grounded outcomes answer different questions. An accepted correct guess can improve label delivery without numerical support; a grounded label can still be wrong. The grounded criterion checks agreement with a task-matched prediction and inclusion of required features, not the adequacy of the physical diagnosis. Reporting both endpoints prevents procedural improvement from being substituted for diagnostic performance, while preserving the original outcome-selection rule.

The single-window task supports analysis of numerical execution, premature submission and feasible post-prediction continuation. It does not test loss of an independent raw observation, dynamic condition revision or indispensable persistent memory. A nontrivial finding must connect the specified interface to delivery, numerical support or label quality with appropriate uncertainty. Missing results and imprecise contrasts remain unresolved, rather than evidence that the intervention helps, harms or has no effect.

## References
