---
bibliography: ../refs/phmgraph_review_2026.bib
link-citations: true
---

# PHMGraph: Separating Instruction Indexing from Workflow Gating in Tool-Using PHM Agents

## Abstract

A prognostics and health management (PHM) agent must turn available numerical capabilities into a delivered diagnosis. Explicit workflows can direct this process, but a controller that prevents premature submission may also close useful analytical opportunities. We introduce PHMGraph, a training-free control formulation that separates active-instruction indexing from progress-gated tool exposure under a common procedural catalog, released data scope, fitted expert pool, language model and evaluator. A four-condition design distinguishes the effect of an active-block pointer with global tools from the additional effect of gating after indexing. We connect these interventions to a finite-horizon opportunity–selection decomposition and to two task-supported execution boundaries: numerical prediction precedes submission, and successful prediction closes ordinary subsequent analysis in the error-free, event-free diagnosis path. The primary comparison uses pooled diagnosis Macro-F1 over assigned first attempts, retaining canonical non-submissions and provider interruptions; replay performance is secondary. Paired PHM outcomes remain to be collected, so the present analysis establishes the method, its executable boundaries and the comparisons needed to determine its diagnostic effect.

## 1. Introduction

Reliable equipment diagnosis requires both a useful numerical method and a procedure that applies it to the available measurement. Bearing-diagnostic benchmarks expose substantial variation in the difficulty of extracting fault evidence, while transfer learning improves the representations used for classification [@smith2015; @shao2019]. The Paderborn benchmark further distinguishes experimentally generated bearing damage and measurement conditions [@lessmeier2016]. These developments primarily strengthen the mapping from measurements to predictions. A tool-using PHM agent introduces an additional decision layer: it chooses which computation to invoke, interprets the returned evidence and decides when to deliver a diagnosis. A capable predictor that is never called cannot contribute to that delivered result.

Language-model agents offer a way to coordinate these decisions without replacing every numerical component. Coscientist and ChemCrow couple language reasoning with scientific tools [@boiko2023; @bran2024], while ReAct interleaves reasoning with environmental actions and Toolformer learns tool use from API-augmented examples [@yao2023react; @schick2023toolformer]. For PHM, this suggests an architecture in which signal analysis and prediction remain executable numerical operations, while the agent organizes their use. The resulting scientific question concerns the relation between available capability, its actual execution and the final diagnosis—not merely whether an agent can produce an intelligible report.

Explicit workflows are an established response to this coordination problem. StateFlow uses state-dependent instructions and transitions, and evaluates refined reactive prompting and state-removal variants [@wu2024stateflow]. PHMForge studies industrial tool orchestration, including verification, distractor-tool and discovery controls [@li2026phmforge]. TimeSage-MT compares code-enabled, skill-guided and orchestrated time-series systems and reports a grounding–flexibility trade-off [@kong2026timesagemt]. These results motivate a more specific question: **with the same PHM procedures and numerical capabilities available, what changes when an agent is told which instruction is active, and what changes when the workflow additionally restricts executable actions?**

Figure 1 illustrates why these are different interventions. An active-instruction pointer locates an existing procedure within a shared catalog. A progress gate changes when computations and submission are available. The latter can suppress an early answer that has no numerical prediction behind it, yet also prevent further analysis once a prediction exists. Procedural progress and diagnostic sufficiency are different: executing a predictor does not establish that its label is correct or that every useful computation has been exhausted. Conversely, a removed action matters to the observed task only when the unrestricted agent would select it and its consequences affect the delivered result.

![Motivation and intervention design. **a**, All conditions share the released data scope, numerical expert pool, procedural catalog, model and declared budgets. **b**, Indexing highlights an existing instruction; gating suppresses premature submission and closes post-prediction analysis. Crossed dashed arrows denote opportunities available with global tools but excluded in the illustrated gated path. The diagram simplifies the error-free, event-free, non-replay route; catalog discovery, error recovery and replay progression follow their own rules. **c**, The four conditions separate an explicit pointer from progress-gated tool exposure. **d**, Both primary contrasts use the same first-attempt diagnosis endpoint. This is a conceptual schematic, not a performance result.](../assets/figures/phmgraph_motivation.svg)

Three challenges follow. First, instruction content and instruction selection must be separated: adding a better procedure only to the graph agent would mix control with domain knowledge. Second, restrictions must be described through the actions they remove, rather than through state names or tool counts. A prediction-ready state need not verify a prediction, and fewer visible tools can encode progress as well as reduce choice. Third, the comparison must retain failures to deliver an answer. Evaluating only successful submissions selects a treatment-dependent subset and can conceal an operationally important effect.

We address these challenges with PHMGraph. A public-history controller computes analysis progress and independently exposes an opaque instruction-block index and a progress-dependent tool menu. Every condition receives the same complete procedural catalog. A paired four-condition design measures indexing under global tools and the incremental gate effect after indexing, using diagnosis as the primary task. The analysis connects these comparisons to the opportunities that the implemented controller permits or excludes.

The contributions are threefold:

1. **A content-matched PHM control formulation.** PHMGraph separates active-instruction indexing from progress-gated tool exposure while keeping procedural content and potential numerical capabilities common. This formulation makes instruction localization and executable workflow restriction independently manipulable components of a PHM agent.
2. **A task-supported analysis of the control trade-off.** We specialize a finite-horizon value decomposition to distinguish excluded analytical opportunities from selection within retained actions, and characterize prediction-before-submission and post-prediction closure in the supported diagnosis path. The analysis distinguishes workflow progress from diagnostic sufficiency and specifies the behavior needed to connect a restriction to task outcomes.
3. **A paired, first-attempt evaluation design for delivered diagnosis.** Two prespecified Macro-F1 contrasts separate indexing from the additional gate effect, retain canonical failed deliveries, and use bearing-clustered uncertainty. Trajectory observations then distinguish numerical execution, premature submission and post-prediction continuation without replacing the task endpoint with procedural compliance.

## 2. Related work

### 2.1 Numerical PHM capability and agent control

Vibration-based bearing diagnosis has a substantial signal-processing and benchmarking foundation. Smith and Randall evaluate diagnostic analyses on the CWRU data, making the quality of extracted fault evidence central to assessing a method [@smith2015]. Lessmeier et al. provide systematically generated measurements and damage descriptions, including distinctions between artificial and real damage [@lessmeier2016]. Shao et al. combine time-frequency transformation with pretrained deep representations for machine-fault diagnosis [@shao2019]. More generally, MOMENT develops pretrained representations for multiple time-series tasks [@goswami2024]. These works establish or improve numerical capabilities and the data on which they are evaluated.

PHMGraph examines a different component: the control interface through which a fixed agent invokes such capabilities. Equal access to an expert pool does not imply that two agents execute the same numerical path. One may fail to call a predictor, choose different features or submit a different supported label. Accordingly, the controlled quantity is the available pool and its fitted parameters, while realized computations are part of the treatment response. This distinction also separates PHMGraph from studies that add reusable diagnostic knowledge or train a stronger representation.

### 2.2 Tool acquisition, feedback and reusable experience

Toolformer learns when and how to use APIs, ToolLLM combines tool-use data construction, training and API retrieval, and Gorilla studies API generation with retrieved documentation [@schick2023toolformer; @qin2023toolllm; @patil2023gorilla]. Coscientist coordinates computation, documentation and experimental modules, while ChemCrow integrates chemistry-specific tools into language-model reasoning [@boiko2023; @bran2024]. These contributions demonstrate complementary ways to make computational capabilities usable by language models.

ReAct conditions actions on an evolving reasoning-and-observation history [@yao2023react]. Reflexion uses feedback and episodic verbal memory across attempts [@shinn2023reflexion], whereas Agent Workflow Memory induces reusable routines from previous experience and supplies them to guide later actions [@wang2024awm]. PHMGraph instead holds model weights and procedural content fixed within the comparison. Its pointer identifies one of the instructions already visible to every arm; it neither retrieves a new skill nor adds experience from another attempt. Consequently, an observed indexing effect concerns the use of common content, rather than acquisition of additional knowledge.

### 2.3 State-driven workflows, thought graphs and search

Finite-state controllers predate language-model agents: Hansen represents partially observable policies as finite controllers, and reward machines expose structured task objectives to reinforcement-learning algorithms [@hansen1997; @icarte2018]. StateFlow brings explicit states, transitions and state-dependent execution to LLM task solving. Its verification and error-handling states, together with its ablations, make it a direct methodological precedent [@wu2024stateflow]. StateAct reinforces goals and tracks state through self-prompting and a chain of states [@rozanov2025stateact]. These approaches establish that explicit state organization itself is not the distinguishing object of the present study.

Other graph structures act on different objects. Tree of Thoughts explores alternative reasoning continuations, and Graph of Thoughts represents dependencies and combinations among generated thoughts [@yao2023tot; @besta2024got]. Language Agent Tree Search combines search, value assessment, reflection and environmental feedback [@zhou2024lats]. AFlow searches over code-represented agentic workflows [@zhang2025aflow], while AutoGen supports configurable multi-agent conversation patterns [@wu2023autogen]. Such methods can change candidate generation, auxiliary computation or the workflow itself. PHMGraph uses a fixed public-history controller and one underlying agent; its primary intervention is the presentation and execution boundary of an existing procedure, rather than thought-graph search or automatic workflow optimization.

### 2.4 Industrial and time-series agents

ReActXen adds review, reflection and distillation components to industrial SCADA data access [@rayfield2025reactiot]. CodeReAct embeds executable Python in a reasoning–action–observation loop for asset-management events and work orders [@zhou2026codereact]. SPIRAL integrates Planner, Simulator and Critic roles with Monte Carlo tree search, including predicted outcomes and reflective feedback [@zhang2026spiral]. TimeART trains time-series reasoning models using tool-use trajectories [@wu2026timeart]. Each changes capabilities, feedback or decision computation beyond an active pointer over fixed instructions.

Two recent studies are particularly close. PHMForge evaluates algorithm-grounded industrial tools and distinguishes orchestration failures, including sequencing and premature termination; its control experiments already address several tool-level mechanisms [@li2026phmforge]. TimeSage-MT includes paired system comparisons and a structured pipeline whose additional stages can improve grounding while reducing other dimensions of performance [@kong2026timesagemt]. The present study builds on these findings through a narrower controlled object: an instruction pointer and a progress gate acting on a common PHM catalog. The two primary contrasts concern that specified interface, not a general comparison of all structured and unstructured agents.

| Closest approach | Documented intervention | PHMGraph comparison object |
|---|---|---|
| StateFlow | State-dependent instructions, execution and transitions | Same full catalog; pointer and gate independently switched |
| StateAct | Repeated goal prompting and state tracking | Opaque active-block identifier derived from public history |
| ReActXen / CodeReAct | Additional reflection roles or executable-code reasoning | One base agent and a common numerical tool pool |
| TimeART | Tool-trajectory training of time-series reasoning models | Fixed model weights and fixed fitted experts |
| PHMForge | Industrial tool orchestration and tool-level controls | Within-catalog indexing and incremental progress gating |
| TimeSage-MT | Code, skill and multi-stage orchestration comparisons | Four interfaces with task-primary first-attempt diagnosis |

The comparisons above describe intervention content; they do not transfer performance numbers across tasks or assert that earlier papers lack controlled experiments.

### 2.5 Task-grounded agent evaluation

AgentBench evaluates interactive agents across environments, GAIA tests general assistant tasks requiring multiple capabilities, and WebArena evaluates functional completion in realistic web environments [@liu2023agentbench; @mialon2023gaia; @zhou2024webarena]. The distinction between producing an action and accomplishing a task is also central to tool–agent–user interaction in tau-bench [@yao2024tau]. These precedents motivate outcome evaluation that extends beyond a valid tool call or a legal transition.

Statistical evaluation also requires the unit of comparison to match the source of dependence. Demšar studies classifier comparisons across datasets, while Agarwal et al. show how limited runs and aggregate point estimates can produce unstable conclusions [@demsar2006; @agarwal2021]. PHMGraph uses paired bearing-level resampling because windows and model repeats from the same bearing are not independent experimental assets. The use of confidence intervals follows established evaluation practice; it does not create a new reliability metric or confer deployment guarantees.

### 2.6 Action restriction and opportunity cost

Invalid-action masking has theoretical and empirical support in policy-gradient settings [@huang2022masking], and confidence-based action elimination studies when alternatives can be discarded using reward evidence [@evendar2006]. A PHM workflow gate is different from an environment-validity mask: it may remove an otherwise legal analysis because a prescribed phase has ended. Its diagnostic effect therefore depends on both easier selection and excluded opportunities.

Policy-value analysis supplies the relevant accounting framework [@schulman2015]. Off-policy evaluation further shows why observed trajectories alone do not reveal the values of unsupported alternatives without additional assumptions [@jiang2016; @khan2024]. We use these foundations to delimit the interpretation of PHMGraph, rather than equating invalid-call counts with regret or deriving an efficacy claim from the size of a tool menu.

## 3. PHMGraph: common content, different decision interfaces

### 3.1 Public progress and shared capabilities

Let

$$
\mathcal W=(\mathcal D,\mathcal Q,\mathcal A,\mathcal B,P,\mathcal E)
$$

denote the released data scope, tasks, global actions, budgets, environment and evaluator. Public history $h_t$ contains task context, actions, returned numerical artifacts, errors and remaining resources. Private targets are available only to the evaluator. PHMGraph computes an analysis-progress phase

$$
z_t=f(h_t).
$$

The event-free base phases represent acquisition, catalog inspection, analysis, prediction readiness, recovery and submission. They describe execution progress rather than fault probabilities or evidence sufficiency. Full public history remains available to the agent, so the experiment concerns an explicit interface to that history rather than indispensable persistent memory.

The procedural catalog is

$$
B=((b_j,d_j))_{j=1}^{6},
$$

where the opaque identifiers B01–B06 name six fixed instruction blocks. Every condition receives the complete catalog once, in the same order, on each request. Indexing appends the designated block identifier without replacing or expanding its instruction. The resulting comparison is conditional on this catalog, including any burden of finding the relevant block.

### 3.2 Independently controlled interfaces

For pointer indicator $i\in\{0,1\}$ and gate indicator $g\in\{0,1\}$, the model input is

$$
x_t^{ig}=\rho(h_t,B)\oplus iL(z_t)
\oplus\operatorname{Schema}(\Gamma_g(z_t)),
\qquad \Gamma_0(z_t)=\mathcal A.
$$

Here $\rho$ renders the common history and catalog, $L$ returns the active-block identifier, and $\Gamma_1$ provides the progress-dependent menu. Actions are selected by the same base model,

$$
a_t\sim\pi_\theta(\cdot\mid x_t^{ig}).
$$

The four conditions are catalog-global (00), indexed-global (10), catalog-masked (01) and indexed-masked (11). Historical state annotations are removed from model-visible tool messages in every condition, while numerical payloads and errors are retained. The gating operation changes both presented schemas and which actions can execute; an unavailable request remains an observed failure rather than a silently corrected action.

The six distinct base menus also convey progress information. Thus, the gate effect includes menu reduction, implicit phase information and changes in permissible action sequences. It is the total effect of this specified gate, not a pure action-count or topology effect. Equal-width block identifiers likewise do not imply equal tokenizer cost.

### 3.3 Execution boundaries

In the supported base diagnosis path, submission becomes available only after numerical prediction. After a successful prediction, the menu contains submission alone, closing ordinary subsequent analysis. A recorded submission error can reopen recovery; replay follows its released-window progression. These rules make two boundaries observable: whether an answer can precede prediction, and whether an agent can continue numerical analysis after prediction.

The diagnosis task exposes one distinct legal raw window with fixed channel and window specifications. Successful rereads return the same array under potentially different artifact references. Gating repeated access in this task therefore changes access behavior and cost, not the number of distinct raw observations. Different processing of the same array can still matter to a bounded agent.

## 4. Opportunity–selection analysis

### 4.1 Finite-horizon decomposition

Consider a finite horizon $T$ with absorbing termination, zero terminal continuation value and a history state $s_t$ that includes time and remaining budget. Let $V_t^*,Q_t^*$ be unrestricted optimal task values, and let $A_G(s)$ be a nonempty retained action set. For a supported action $a\in A_G(s)$, define

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in A_G(s)}Q_t^*(s,u),
$$

$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in A_G(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

For a policy supported on these sets,

$$
V_0^*(s_0)-V_0^\pi(s_0)=
\mathbb E_\pi\sum_{t=0}^{T-1}
\left[\ell_t^{\mathrm{mask}}(s_t)+\ell_t^{\mathrm{select}}(s_t,a_t)\right].
$$

The two terms sum to $V_t^*(s_t)-Q_t^*(s_t,a_t)$. Substituting the Bellman equation and taking conditional expectations cancels successive optimal values; zero terminal continuation yields the identity. This is a finite-horizon specialization of standard value accounting [@schulman2015]. The first term captures exclusion of high-value opportunities; the second captures selection among retained alternatives. The identity concerns expected episodic return; the pooled Macro-F1 in Section 5 is a separate, non-additive operational estimand.

PHM logs do not provide $Q^*$. Accordingly, neither component is estimated by an invalid-call rate. Different policies also induce different history distributions, so differences between these terms are not automatically causal mediation effects. Empirical malformed calls and interruptions remain outcomes in their own right; the supported-policy assumption is explicit in the analytical identity.

### 4.2 Redundant information, nonredundant computation

When the complete rendered history determines $z_t$, appending its deterministic index adds no information to an unrestricted history policy. Such a policy can internally compose $f$ with its decision rule. Restricting its action support cannot increase its optimal task value. A finite language model may nevertheless use the explicit index more effectively than it reconstructs the relevant phase, or select more effectively from a restricted menu. The empirical question concerns this bounded decision maker, not an increase in information-theoretic capability.

The same distinction applies to rereading. For the legal raw arrays $X_2=X_1$,

$$
I(Y;X_2\mid X_1)=0.
$$

This excludes a second independent raw-observation explanation in the present diagnosis task. It does not imply that an alternative numerical analysis of $X_1$ is computationally redundant for the agent. Task utility here also excludes interface costs: equal optimal task values need not imply equal token use, latency or priced net value.

### 4.3 From a permitted opportunity to an observed effect

Post-prediction closure is an execution property of the error-free, event-free, supported diagnosis path. To investigate its consequence, the comparison separates three observations: whether global-tool agents continue analysis after prediction, whether the final label changes, and whether the supporting numerical results change. New reference identifiers alone do not establish new evidence. A changed label can be correct or incorrect, and a longer trajectory can be useful or wasteful.

These distinctions yield falsifiable alternatives. A gate may improve delivered performance chiefly by increasing numerical execution and submission, without improving label quality among submitted cases. It may reduce performance when useful continuation is selected and then removed. It may show little effect because the unrestricted agent rarely uses the excluded opportunities. The primary outcome tests the total effect; trajectory observations indicate which explanation is compatible with the observed execution, without identifying an unobserved optimal alternative.

## 5. Paired first-attempt evaluation

### 5.1 Primary endpoint and contrasts

Diagnosis is primary. The endpoint is pooled Macro-F1 over the three declared diagnosis classes and all assigned canonical first-attempt outcomes. An attempt with no accepted diagnosis is retained as `no_submission`: it contributes a false negative to its true class and is not averaged as a fourth diagnosis class. This operational endpoint therefore reflects both delivery and label quality.

For matched first-outcome records $D_{ig}^{(1)}$ under catalog $B$, the two primary contrasts are

$$
\Delta_{\mathrm{index}}^{D}=
\operatorname{F1}_{\mathrm{macro}}(D_{10}^{(1)})-
\operatorname{F1}_{\mathrm{macro}}(D_{00}^{(1)}),
$$

$$
\Delta_{\mathrm{gate}}^{D}=
\operatorname{F1}_{\mathrm{macro}}(D_{11}^{(1)})-
\operatorname{F1}_{\mathrm{macro}}(D_{10}^{(1)}).
$$

The first measures the active pointer under global tools; the second measures gating after indexing. Replay Average Precision, with its unchanged assigned-window and missing-score rules, is secondary. The remaining simple effects and factorial interaction are exploratory. Earlier Graph-versus-Generic or semantic-cue profiles remain separate comparisons and are not substituted for these controls.

### 5.2 Assignment, resources and uncertainty

Bearing splits, class labels, sample/window/channel specifications, replay order, reference-fitting scope, model settings and task budgets are fixed before evaluation. The four conditions run in independent agent sessions within matched bearing, task, rotation and repeat blocks. Randomized cyclic order balances condition positions to within one occurrence per task/rotation/repeat/budget stratum. This balances positions rather than guaranteeing elimination of provider drift or carryover. Interrupted blocks retain their original assignments and any resumed time gaps.

Uncertainty uses a paired, diagnosis-class-stratified bearing bootstrap. Within each true class, bearings are resampled with their windows and model repeats, and the same draws apply to every term in a contrast. Class-specific bearing counts remain fixed, so the intervals condition on the cohort's class composition. The two prespecified effects receive nominal 97.5% percentile intervals through Bonferroni allocation. These are interval estimates, not claims of exact small-sample coverage or control of all provider randomness. A one-bearing smoke run has no inferential interpretation.

A request reserve must cover the remaining members of a block before that block starts. Its invocation ceiling is an operational safeguard, distinct from per-condition task budgets and from the final study size. Existing first outcomes are reused without refitting the common numerical reference. Numerical reference execution and agent execution must use matching resolved task/data/fit assignments; readable metadata alone does not establish waveform correspondence.

### 5.3 Incomplete delivery and mechanism observations

A provider interruption that produces a canonical terminal outcome remains in its assigned first attempt. A durable request record without a complete canonical outcome is indeterminate and blocks automatic resend; it is neither an inferred diagnostic failure nor an unattempted case. A complete primary comparison requires all assigned canonical first outcomes. This distinction prevents outcome-dependent replacement while preserving genuinely unresolved attempts.

Alongside Macro-F1, report submission rate, the three-class confusion matrix with a `no_submission` column, and the composition of provider interruptions, malformed responses, unavailable actions and budget exhaustion. Macro-F1 conditional on accepted submissions is a descriptive sensitivity analysis. Its treatment-dependent denominator is not a replacement for the operational endpoint.

Mechanism observations include attempted submission before numerical prediction, post-prediction analytical actions, changes from the first prediction to the final submitted label, numerical support changes, and submission-error recovery. Every conditional rate identifies its denominator, including attempts that never reach prediction or submission. These are descriptive trajectory analyses rather than causal subgroups. Resource reporting retains known usage, unknown interruption billing, timestamps and resumed-block gaps.

## 6. Results

Matched PHM first-attempt outcomes are not yet available. The two primary diagnosis effects, secondary replay effects and operational costs are therefore unestimated. The execution boundaries in Sections 3–4 specify the intervention and its testable consequences; they are not empirical estimates of diagnostic improvement or harm.

## 7. Discussion

PHMGraph distinguishes providing a computation, guiding its use and enforcing its execution order. This separation is important because a fixed expert pool permits different realized numerical paths. A pointer can change which existing instruction receives attention, whereas a gate also changes what remains possible. Their effects should consequently be interpreted at the level of the specified interface and task, rather than attributed to graph structure in general.

The present diagnosis scope contains one distinct raw window. It supports questions about numerical execution, early submission and post-prediction continuation, but not loss of a second independent raw measurement. Full history remains available, and the primary path has no public condition-change event; persistent-memory and dynamic-revision effects require different interventions. The task-primary comparison and its uncertainty also remain conditional on the declared bearing cohort, model, catalog and budgets.

A useful next empirical conclusion must therefore identify which of three outcomes occurs: improved delivery, changed diagnostic label quality, or an inactive restriction. The same design can reveal adverse effects. That symmetry is central to deciding when an explicit PHM workflow is helpful rather than treating additional control as an automatic improvement.

## References
