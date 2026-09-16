# Decision Structure and Action Restrictions in Graph-Guided PHM Agents

## Abstract

Long-running PHM assistants must decide what to inspect, which numerical analyses to execute, and when to revise or submit a diagnosis. We study explicit decision structure with the language model, PHM knowledge source, observation access, numerical tools, budgets and evaluation held fixed. The structure maintains analysis progress and public-event memory, presents a current-state cue, and restricts tool visibility. A finite-horizon analysis separates value lost through action exclusion from loss caused by selection within the retained set. Conditional value bounds and exact counterexamples show why fewer visible tools, valid transitions and lower exclusion bounds do not guarantee better decisions. A cue-by-filter design isolates the two interface interventions under a common history representation. We further establish that the event-free base persistence and replanning switches are inactive, whereas public events can activate distinct state updates. A cardinality-matched control tests analysis-stage tool identity without changing termination permissions. The resulting PHM evaluation separates task effects, active recurrence, sampling/resource sensitivity and cost; the analytical findings specify what these comparisons can establish without treating process compliance as diagnostic accuracy.

## 1. Introduction

Long-running PHM involves a succession of decisions rather than a single tool call. An assistant must acquire relevant signal windows, choose numerical analyses, examine their outputs and decide whether to continue, revise or submit. Scientific assistants such as Coscientist and ChemCrow demonstrate how language models can coordinate external computation [@boiko2023; @bran2024]. In mechanical diagnosis, the corresponding question is whether that coordination makes useful decisions within limited observation and computation budgets. A completed sequence of valid calls can still omit a necessary analysis.

Reactive agents already retain information in their interaction history. ReAct interleaves reasoning with actions and observations, while Reflexion uses feedback and memory across attempts [@yao2023react; @shinn2023reflexion]. An explicit controller does not create memory where none existed. It makes a particular state update and its consequences for the next decision inspectable. Its effect must therefore be distinguished from differences in model capability, supplied knowledge and available numerical experts.

State-based control is established. Finite-state controllers represent policies under partial observability [@hansen1997], and StateFlow defines context-dependent transitions, state instructions and output functions for language-model workflows [@wu2024stateflow]. StateFlow also evaluates refined prompts and state removals. PHMForge studies domain-tool orchestration with verification, distractor and data-discovery ablations [@li2026phmforge]. These precedents rule out identifying the novelty with a state machine, additional workflow stages or the use of PHM tools.

The unresolved question in the present PHM setting is the task effect of two specific consequences of explicit control: the current-state cue and the restriction of otherwise available actions. A joint comparison changes both. An improvement cannot then be assigned to the cue, tool filtering, persistent memory or graph topology individually. Conversely, restricting choices may simplify selection while excluding a useful analysis. The study must admit both helpful and harmful control.

We define $G$ as a persistent decision structure. It maintains an analysis-progress state and the identity of the last consumed public condition event. Its outputs are a state-conditioned instruction and a tool-visibility mask. The common knowledge source $K_0$, model and evaluation remain fixed; state-conditioned presentation is part of the declared control intervention. A four-cell experiment varies cue and mask independently while treating historical state metadata identically.

The theoretical analysis separates exclusion loss from selection loss [@schulman2015; @geist2019]. Confidence-based action elimination motivates a conditional bound on omitted value [@evendar2006], but neither this bound nor workflow compliance supplies an observed PHM regret. Unsupported logged actions introduce an additional identification limit [@jiang2016; @khan2024]. The useful design objective is to reduce selection loss without an excessive increase in exclusion loss, rather than to minimize tool count.

The study contributes a precise PHM control intervention, an analysis of its value and identification boundaries, and component comparisons that distinguish active from inactive manipulations. The experimental order is joint Graph control, cue/filter attribution, persistence activation, sequence/resource sensitivity, dynamic revision and repeated reliability. Exact-model calculations establish analytical counterexamples; real matched task outcomes are the test of industrial benefit.

## 2. Related work

**Persistent control and state-driven agents.** Hansen represents POMDP policies through controller states, associated actions and observation-conditioned successors, and evaluates them under a specified model [@hansen1997]. StateFlow uses cumulative context in its transition and output functions [@wu2024stateflow]. The present controller retains full public history alongside explicit state, so it is neither a sufficient diagnosis-belief state nor an optimal finite-memory controller. No model-based policy-improvement guarantee is imported from these precedents.

**State ablations and masking.** StateFlow's refined ReAct and state-removal comparisons directly concern instruction and control. Its removal of Observe still permits table exploration through the Solve prompt [@wu2024stateflow]. Thus a removed state need not remove the corresponding action. Invalid-action masking has a policy-gradient analysis [@huang2022masking]; our visibility rule additionally restricts tool interfaces that the shared environment otherwise provides. The cue/filter design estimates the implemented interface effects, not topology in isolation.

**PHM and scientific agents.** Coscientist and ChemCrow couple language decisions to external computation [@boiko2023; @bran2024]. PHMForge includes verification, distractor and data-discovery controls [@li2026phmforge]. Here both arms share the same numerical capabilities, and a secondary cardinality-matched control changes tool identities only in designated analysis states. Removing distractors or adding PHM tools is not itself a new contribution.

**Action values and identification.** Even-Dar, Mannor and Mansour establish value-confidence comparisons for action elimination and stopping [@evendar2006]. Jiang and Li study sequential off-policy evaluation, and Khan, Saveski and Ugander derive partial-identification bounds without overlap [@jiang2016; @khan2024]. Our interval diagnostic and bounded one-step identification region specialize this reasoning; logged execution does not identify all omitted continuation values.

**Numerical capability.** Fixed features, learned representations and foundation models such as MOMENT can change numerical prediction independently of control [@goswami2024]. A frozen reference, validation-selected single representation, static fusion and numerical routing therefore form a separate capability axis. Each admitted expert pool must be exposed equally to compared agents.

## 3. Problem formulation

The fixed world is $\mathcal W=(\mathcal D,\mathcal T,\mathcal A,\mathcal B,P,\mathcal E)$: data access, tasks, actions, resource limits, environment responses and independent evaluation. At step $t$, public history, budget and time form $s_t=(h_t,b_t,t)$. Equal observation access and release rules do not force different policies to realize identical histories.

Define

$$
G=(\mathcal M,m_{\mathrm{init}},\delta,c,\Gamma),\qquad
m_t=(z_t,\nu_t)=\delta(m_{t-1},s_t,e_t).
$$

Here $z_t$ is the phase, $\nu_t$ the last consumed public-event token, $c(z_t)$ the current label-plus-instruction cue, and $\Gamma(z_t,s_t)$ the visible tool set. The explicit edges are induced by $\delta$. The model also receives public history. Private targets enter only the evaluator.

The base profile uses Inspect, Hypothesize, Analyze, Check, Recover and Submit. These are analysis-progress states, not posterior fault hypotheses. Hypothesize follows catalog discovery. In replay, Check follows eleven successful operator calls associated with the current sample after its read; repeated operators can meet this count, so it does not certify distinct-feature completeness. Recovery responds to an observed call error. Submission remains a model-chosen action whose admissibility and result are handled by the shared environment.

Monitor and Revise belong to the dynamic profile. The public event is an operating-condition change at a released replay index, not an onset inferred from vibration. Base inputs carrying these events are rejected rather than silently routed dynamically. Dynamic event identity and release-index checks remain explicit.

The finite-action value analysis concerns fully specified actions and a policy supported on its declared action set. For parameterized tools, family-value intervals must cover the best permitted continuation over the full parameter family. The operational implementation masks tool names; it has no fitted, calibrated PHM continuation-value estimator. Diagnosis Macro-F1 and registered anomaly/replay metrics remain primary and are not replaced by the additive utility used in the theory.

## 4. Control-loss and intervention analysis

### 4.1 Exclusion and selection

For unrestricted optimal continuation values $V_t^*$ and $Q_t^*$, let $A_G(s)$ be the retained action set and define

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in A_G(s)}Q_t^*(s,u),
$$
$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in A_G(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

For finite horizon $T$, absorbing termination and zero terminal continuation value,

$$
V_0^*(s_0)-V_0^\pi(s_0)
=\mathbb E_\pi\sum_{t<T}
\left(\ell_t^{\mathrm{mask}}+\ell_t^{\mathrm{select}}\right).
$$

The summands add to $V_t^*-Q_t^*$. Substitution of the Bellman relation telescopes the continuation terms. This standard identity uses the policy's own history distribution; subtracting its terms between policies does not automatically identify causal mediation. In real PHM, $Q^*$ is unknown. Transition validity, invalid-call rate and tool count are not substitutes for either loss.

### 4.2 Conditional coverage and selection

Suppose finite intervals $[L_a,U_a]$ cover all relevant continuation values simultaneously at a state. For a nonempty mask $A_G$, define

$$
C(A_G;s)=\max\left(0,\max_{a\notin A_G}U_a-\max_{u\in A_G}L_u\right),
$$

with $C=0$ under full exposure. On the coverage event,

$$0\leq\ell^{\mathrm{mask}}(s)\leq C(A_G;s).$$

The best omitted value cannot exceed the omitted upper maximum, and a retained alternative reaches at least the retained lower maximum. Adding the omitted action with greatest upper endpoint cannot increase $C$; repetition reaches any finite nonnegative tolerance after finitely many additions. This proves conditional coverage and termination, not optimal mask size or policy improvement. Adaptive histories require justified simultaneous rather than merely marginal coverage.

For a one-step selector, let $J(M)=\mathbb E_{a\sim\pi_M}Q(a)$ and $e(M)=\max_{a\in M}Q(a)-J(M)$. At the same state,

$$
J(M')-J(M)=\ell^{\mathrm{mask}}(M)-\ell^{\mathrm{mask}}(M')-[e(M')-e(M)].
$$

A reduction in exclusion loss can be outweighed by worse selection. Changed visitation also matters in multistep comparisons. The current graph remains a progress controller, not an interval-estimation policy.

### 4.3 Support and tool count

If a one-step logging policy always selects a retained action of mean $v\in[0,1]$ and never an omitted action, bounded reward alone gives the sharp region

$$\mathcal I_{\mathrm{mask}}(v)=[0,1-v].$$

The omitted mean can vary across $[0,1]$ without changing the logging law. This is population identification, not a sampled confidence interval [@khan2024]. Additional action coverage or justified structural assumptions are needed for omitted PHM values.

For $n$ fixed one-step values $q_a$, a uniformly drawn size-$k$ subset $S$ and a uniform selector within it satisfy

$$
\mathbb E_S J(S)=\frac{1}{k}\sum_aq_a\Pr(a\in S)=\frac{1}{n}\sum_aq_a.
$$

For ordered values $q_{(1)}\leq\cdots\leq q_{(n)}$,

$$
\mathbb E_S\max_{a\in S}q_a
=\sum_{j=k}^n q_{(j)}\frac{\binom{j-1}{k-1}}{\binom nk}.
$$

These elementary counting identities motivate a tool-count control. They do not assume that an LLM selects uniformly or predict its task performance. The supplementary theory covers forced terminal membership.

### 4.4 Ablation validity

Two policies with identical model-facing messages and schemas at every reachable history induce the same rollout law when the response distribution, decoding, environment, stopping and resource rules also agree. The proof couples the first response and action, then repeats the argument after the common environment update.

In the event-free base profile initialized at Inspect, previous state and replanning can affect the existing transition function only through unreachable Monitor/Revise branches. The event token remains empty. Full, no-persistent-state and no-replanning therefore produce the same phases, cues and masks on all reachable histories, and the coupling argument applies. A zero result is a null-manipulation check, not evidence against memory or replanning in general.

A changed model input is an activation witness, not evidence of changed action probabilities or task benefit. Finite fixture checks alone also do not prove equality on every reachable history. The supplementary proof separates the source-level equivalence argument from empirical activation tests.

### 4.5 Risk and sampling units

Population risk is $R_{\mathcal D}(\pi)=\mathbb E_{e\sim\mathcal D,\xi}L(e,\pi,\xi)$; empirical risk averages observed losses on held-out assets and trials. Conditional on fitted experts and frozen policies, independent asset blocks support concentration for additive bounded loss. Macro-F1 and AP are instead recomputed inside paired asset-block resamples. Repeated trials do not create independent assets, and training risk does not establish performance under a shifted deployment distribution.

## 5. Minimal method

The primary comparison is original Generic versus Graph, a joint control effect. The component study independently switches the current-state cue and tool filtering. All four cells remove top-level historical decision-state metadata from provider-visible tool messages while preserving action arguments, numerical payloads, errors and order at the same history. Historical Generic is not the new factorial-reactive; original Graph is not the new factorial-both.

The cue contains both a phase label and its stage instruction. Its effect is not a pure label or topology effect. Tool visibility can itself reveal the stage, so disabling the explicit cue does not remove all state information. The common PHM knowledge source is held fixed; a claim independent of additional procedural wording requires the separately specified information-matched prompt control.

The existing secondary cardinality control changes only Analyze/Check tool identities. It samples a fixed-seed subset of the sorted common nonterminal catalog with the original cardinality, preserves submit/stop membership, and preserves tool order and schemas. Other stages are unchanged; revisits do not redraw, and coincident subsets are retained. Conditional count matching does not imply token matching or equal realized trajectory costs.

All prospective dynamic-history-matched profiles remove historical decision-state metadata equally. Removing it only for no-memory would jointly change memory and history disclosure. This prospective rendering differs from legacy full-dynamic rendering, so old full-dynamic outcomes are not reused as matched controls. Persistent memory includes both the previous phase and event-token consumption. A repeated public event can induce full Monitor-to-Revise, no-memory Monitor-to-Monitor and no-replanning Monitor-to-Analyze updates. Actual revision requires an observed change in subsequent decisions, not just a changed label. Dynamic execution uses the sole shared Runner.

## 6. Experimental design

### 6.1 Priority and capability controls

The order is G-main, G-components, persistence activation, sequence/resource sensitivity, dynamic revision and repeated reliability. The first two use the same assigned assets, task ontology, windows, numerical pool, model settings, budgets and evaluator. Base memory remains a negative control rather than an efficacy ablation. A dynamic mechanism claim requires a matched released-event cohort with symmetric history handling.

Generic reactive, full Graph, state-only, filter-only, both and Scripted are the immediate references. StateFlow, Reflexion or planning methods become formal baselines only after faithful mechanism reproduction and accounting for all calls and allowed feedback. The shared numerical axis compares a frozen reference, validation-selected single representation, static fusion and training-only routing. Learned experts are available to every arm. The current graph is training-free and has no optimization loss to ablate.

### 6.2 Sequence and transport

Pure horizon comparisons fix one longest assigned sequence and use nested prefixes. Fixed-total and fixed-per-window budget experiments are separate. The existing horizon configuration changes count, sample selection and proportional resources and therefore supports only horizon/sampling/resource sensitivity. Public operating-condition changes are not inferred fault-onset annotations.

The existing supplementary transport specification covers PTB-XL ECG, UCI HAR inertial activity, SMAP/MSL spacecraft telemetry, SMD servers and SWaT process instrumentation. Each requires its own valid task binding, label mapping and independent-unit or temporal split. These studies follow the core PHM comparison; they do not replace it or support a pooled mechanical headline score. Checkpoints and normalizers are selected without test access, reloaded, and verified against saved predictions using the unchanged scorer.

### 6.3 Estimands, failures and interpretation

Let $\theta_{uv}$ be the declared pooled cohort statistic for cue $u$ and filter $v$. Report

$$
\Delta_c(v)=\theta_{1v}-\theta_{0v},\qquad
\Delta_f(u)=\theta_{u1}-\theta_{u0},\qquad
\Delta_{cf}=\theta_{11}-\theta_{10}-\theta_{01}+\theta_{00}.
$$

Equal-weight marginal effects average the two simple effects. The original Graph-minus-Generic contrast is separate because historical state rendering differs. Persistence compares full and no-memory only after activation is established, with the same history policy and public events.

For the cardinality comparison, let $\mathcal I$ be the frozen asset/trial/seed assignment and $D_p(\mathcal I)$ the retained evaluation records. The registered effect is

$$
\widehat\Delta_{\mathrm{rel}}^{\mathrm{pool}}
=\Theta(D_{01}(\mathcal I))-\Theta(D_C(\mathcal I)).
$$

For nonlinear AP or Macro-F1, this pooled contrast differs from averaging per-seed statistics. Uncertainty is conditional on the frozen seed schedule, with identical asset-block resample indices across arms. It is not uncertainty over all possible masks.

Task performance is primary. Grounded completion, visits, transitions, recovery, revision, repeated actions, premature submission and tool/token/time costs explain observed outcomes without replacing them. All stops, invalid outputs, budget exhaustion and provider failures remain in the assigned population; resumed attempts retain earlier costs. Undefined metrics are reported. Cue benefit with harmful filtering, cost-only benefit, benefit limited to longer sequences and no joint improvement are all admissible findings.

## 7. Results

### 7.1 Finite-horizon reference

The existing exact model has two equally likely public contexts and three abstract analysis routes. At four steps, the best fixed route returns 0.6000, static uniform selection 0.55833, an aligned two-route mask 0.7625, and a harmful singleton 0.5000. Interval expansion with uniform selection returns 0.7125. Covered greedy choice and the unrestricted oracle return 0.9250 because the intervals are centered on known toy values. Across 24 horizon/policy configurations, the recorded maximum decomposition residual is $1.67\times10^{-16}$. Normalized returns are constant over the three even horizons by construction, yielding a null length effect.

### 7.2 Coverage and support counterexamples

Deliberately uncovered intervals give $C=0$ with true exclusion loss 0.85. A separate covered example assigns retained, useful and distracting actions values 0.8, 0.9 and 0, with intervals [0.8,0.8], [0.9,0.9] and [0,1]. Optimistic exposure lowers the bound from 0.2 to 0.1 to zero, while the uniform selector's return changes from 0.8 to 0.4 to 0.5667. Full exposure removes exclusion loss but leaves selection loss 0.3333.

Two logging worlds assign the retained action the same Bernoulli mean 0.5 and the omitted action means 0.1 and 0.95. The logger never chooses the latter. Complete enumeration at sample counts 1, 4 and 8 gives total-variation distance zero between the logging distributions, although their exclusion losses are 0 and 0.45. Both belong to the identified region [0,0.5].

### 7.3 Complete cardinality enumeration

Six one-step actions have values 0, 0.2, 0.4, 0.6, 0.8 and 1. All 63 nonempty subsets are enumerated, yielding 6, 15, 20, 15, 6 and 1 subsets at cardinalities one through six. Within each cardinality the subsets are equally weighted, and selection within a subset is uniform.

Mean return is 0.5 at every cardinality. At cardinality three, the optimal action survives in half of the subsets; mean exclusion and selection losses are 0.15 and 0.35. The best and worst three-action subsets return 0.8 and 0.2. Rational-arithmetic evaluation gives zero residual for both the loss decomposition and the order-statistic identity. These exact results separate tool count, retained opportunity and selector outcome; they are not performance estimates for a fitted PHM controller.

### 7.4 PHM comparisons

Matched PHM and external-domain cohorts have not yet produced the required policy-effect estimates. Their evaluation will distinguish total Graph effect, cue/filter attribution, cardinality-matched identity effects, active persistence, numerical capability, length/resource sensitivity and incurred cost. No diagnostic improvement is inferred from the finite-model calculations.

## 8. Discussion and conclusion

Explicit structure can simplify selection and also restrict necessary action. Its value depends on the resulting PHM decisions, not on the number of states, visible tools or valid transitions. The exclusion/selection analysis specifies this trade-off, while support boundaries prevent logged process statistics from being mistaken for unobserved regret.

The current base is a progress controller with inactive persistence/replanning switches under event-free conditions. Dynamic recurrence is a different, prospectively matched intervention; it requires public-event episodes and observed decision changes. The four-cell study is therefore the immediate empirical test. Only its real task, reliability and cost findings can establish the industrial value of $G$ and support subsequent Benchmark synthesis.
