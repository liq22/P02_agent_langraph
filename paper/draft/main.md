# Value Coverage and Decision Control in Graph-Guided PHM Agents

## Abstract

Restricting a diagnostic agent's tools can simplify its choices while excluding an analysis needed for a correct decision. We study this trade-off through graph-guided state cues and tool visibility in a fixed PHM environment. A finite-horizon value decomposition distinguishes exclusion loss from selection loss within the retained set. Building on confidence-based action elimination, a conditional value-coverage bound yields a terminating exposure rule. Exact counterexamples show that valid coverage need not improve the selector's return, and that masked logs need not identify omitted-action values. These distinctions motivate a cue-by-filter experiment and a cardinality-matched control that replaces tool identities only during analysis and checking while preserving termination permissions. Complete enumeration of 63 nonempty subsets of six abstract actions gives the same random-subset expected return at every cardinality, although equally sized subsets can perform differently. At cardinality three, the best, random-average and worst subset returns are 0.8, 0.5 and 0.2 under the same uniform selector. The PHM protocol separates numerical capability, control effects and incurred cost on asset-disjoint diagnosis and released-window replay. The finite-model results establish the analytical distinctions; diagnostic benefit remains to be determined by matched language-model cohorts.

## 1. Introduction

A vibration diagnosis depends on the measurements and numerical analyses that support it. Language-based scientific assistants can coordinate external computations, as demonstrated by Coscientist and ChemCrow [@boiko2023; @bran2024]. For mechanical equipment, the diagnostic question is whether that coordination selects useful analyses under finite sensing and computational budgets. Successful execution alone does not establish a correct diagnosis when the numerical information is insufficient.

ReAct updates decisions through action-observation interaction, and Reflexion introduces feedback-based memory [@yao2023react; @shinn2023reflexion]. Both use history. Explicit graph control adds a more specific intervention: a state-dependent instruction and a restricted view of tools. Assessing their effects requires keeping the underlying model, public observation access and computational capabilities fixed.

StateFlow provides a direct precedent for state-driven workflows, including state-removal and refined-prompt controls [@wu2024stateflow]. PHMForge evaluates PHM-oriented algorithmic tools, sequencing, verification and distractors [@li2026phmforge]. These studies establish the relevance of workflow control and domain tools. The question here is how a heuristic visibility rule trades off omitted diagnostic opportunities against selection among the retained tools.

Feasibility and usefulness are distinct. Invalid-action masking removes actions that violate environmental rules and has an established policy-gradient analysis [@huang2022masking]. A workflow mask may instead hide a valid action because it appears unnecessary at the current stage. Fewer malformed calls can therefore coexist with the loss of a useful analysis. Tool-set size does not identify which of these mechanisms is responsible for an observed effect.

Sequential value analysis separates the two losses [@schulman2015; @geist2019]. Confidence-based action elimination already compares upper and lower value estimates [@evendar2006]. Applied to a heuristic mask, this comparison bounds the largest value potentially excluded relative to a retained alternative. The bound requires simultaneous coverage of continuation values; confidence in a final diagnosis is a different quantity. Moreover, a selector can deteriorate when additional tools are exposed, even when the exclusion bound improves.

A second difficulty concerns what can be learned from completed workflows. Outcomes of actions that a logging policy never takes are not identified by those logs without further restrictions [@jiang2016; @khan2024]. Directly assigned control conditions can estimate policy effects without identifying these omitted continuation values. The design therefore separates a latent-value analysis from observable task-statistic contrasts.

We first separate current-state cues from tool visibility in a four-cell experiment. We then compare the state-specific mask with an identity-randomized, cardinality-matched mask during analysis and checking. Acquisition, recovery and termination visibility remain unchanged. This narrower contrast tests tool identity without interpreting arbitrary tool removal as an equivalent workflow. Repeated trials remain grouped by physical asset, and task uncertainty is reported separately from resource expenditure [@agarwal2021].

The work contributes a PHM-specific formulation of exclusion and selection losses, conditional coverage and support boundaries, and a component-separated evaluation design with an explicit tool-count control. Exact positive and negative examples establish the analytical distinctions and the counting behavior of the control. The industrial question is whether these distinctions explain reproducible diagnostic effects with the numerical expert pool held fixed.

## 2. Related work

**State control and action masking.** StateFlow defines context-dependent states, prompts and transitions, and evaluates No_Observe, No_Error and No_Verify variants [@wu2024stateflow]. Its refined ReAct control also changes workflow instructions without adding the full state controller. These are direct precedents for component analysis. Huang and Ontanon study masked policy gradients for invalid actions [@huang2022masking]. Here the environment's feasibility rules are retained, while an additional policy-level mask restricts valid tool interfaces.

**Confidence-based elimination and policy value.** Even-Dar, Mannor and Mansour develop value-confidence comparisons, elimination procedures and stopping rules for bandit and reinforcement-learning problems [@evendar2006]. The coverage inequality below specializes that reasoning to an existing heuristic mask. Its terminating exposure rule is not an optimal mask-search procedure. The loss decomposition additionally distinguishes retaining a valuable action from a selector actually choosing it.

**Scientific and PHM agents.** Coscientist and ChemCrow couple language decisions to external scientific computations [@boiko2023; @bran2024]. PHMForge studies PHM tools and provides verification, distractor and data-discovery ablations [@li2026phmforge]. Removing distractors is thus already an established PHM comparison. Our specified contrast holds visible-tool count and terminal-tool membership fixed at the same history, while changing tool identities only in designated analysis states. It tests a narrower question than the presence of domain tools or distractors in general.

**Logged support and evaluation.** Jiang and Li formulate sequential off-policy evaluation through target-to-behavior action probabilities [@jiang2016]. Khan, Saveski and Ugander give sharp partial-identification bounds without overlap, with bounded-response and smoothness assumptions [@khan2024]. Our one-step identification region is a bounded-response specialization. Complete recording of executed actions does not by itself identify unrestricted continuation values.

**Numerical time-series capability.** Representations and numerical predictors can improve independently of the controller. MOMENT provides a time-series foundation-model comparison [@goswami2024]. Fixed-feature models, validation-selected single representations, static fusion and numerical routing form a separate capability axis. Each admitted expert pool must be available equally to the compared agents.

## 3. Problem formulation

Let the shared world be $\mathcal W=(\mathcal D,\mathcal T,\mathcal A,\mathcal B,P,\mathcal E)$: data access, tasks, feasible actions, resource limits, response dynamics and independent evaluation. At time $t$, public history $h_t$, remaining budget $b_t$ and time form $s_t=(h_t,b_t,t)$. A graph state $z_t=f(h_t)$ provides a cue $c(z_t)$ and a nonempty visible set $M(s_t)\subseteq\mathcal A(s_t)$. Targets are available to the evaluator, not the agent.

The finite-action analysis concerns fully specified actions. For a parameterized tool family, an interval must instead cover its best permitted continuation over the full parameter family. Covering one selected parameter setting is insufficient. The operational control studied here changes tool-name visibility; a calibrated tool-family continuation-value estimator has not been fitted.

The base controller tracks reads, catalog discovery, numerical analysis, prediction, submission and recovery after observed errors. These are workflow-progress states, not posterior fault hypotheses. Hypothesize follows catalog progress. In replay, Check follows eleven successful operator calls associated with the current sample after its read. This count does not test distinct-feature completeness. Monitor and Revise belong to a separate public-condition-event profile; externally supplied operating-condition changes are not fault onsets inferred from vibration.

For the value analysis, a single bounded utility is declared before comparison, with termination represented by absorption. The empirical PHM metrics retain diagnosis Macro-F1 and the registered anomaly/replay scores, including the assigned-window missing-score rule. These cohort statistics are not replaced by the illustrative additive utility. Numerical-source consistency, completion, repetition, latency and cost are reported separately.

## 4. Control-loss analysis

### 4.1 Exclusion and selection

For unrestricted optimal continuation values $V_t^*$ and $Q_t^*$, define

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in M(s)}Q_t^*(s,u),
$$
$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in M(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

For a policy supported on $M$, finite horizon $T$ and zero terminal continuation value,

$$
V_0^*(s_0)-V_0^\pi(s_0)
=\mathbb E_\pi\sum_{t<T}
\left(\ell_t^{\mathrm{mask}}(s_t)+\ell_t^{\mathrm{select}}(s_t,a_t)\right).
$$

The two losses sum to $V_t^*(s_t)-Q_t^*(s_t,a_t)$. Substituting the Bellman relation and summing cancels consecutive continuation values. This standard telescoping argument separates omitted value from imperfect selection. The state distribution is policy-dependent; subtracting these terms between policies is not automatically a causal mediation decomposition.

### 4.2 Conditional coverage

Suppose finite real intervals $[L_a,U_a]$ simultaneously contain the continuation values at a state. Define

$$
C(M;s)=\max\left(0,\max_{a\notin M}U_a-\max_{m\in M}L_m\right),
$$

with $C=0$ for the full feasible set. If a global maximizer is retained, exclusion loss is zero. Otherwise its value is at most the excluded upper maximum, while a retained alternative is at least the retained lower maximum. Hence, on the coverage event,

$$0\leq\ell^{\mathrm{mask}}(s)\leq C(M;s).$$

Exposing the omitted action with the largest upper endpoint cannot increase $C$. Repetition terminates at any finite nonnegative tolerance, because full exposure has $C=0$. This establishes conditional coverage and finite termination, not minimum-cardinality exposure. Adaptive histories require justified simultaneous coverage; marginal intervals do not supply it automatically. The existing graph controller is not changed into an interval-estimation policy.

### 4.3 Selection and support boundaries

For a one-step decision, let $J(M)=\mathbb E_{a\sim\pi_M}Q(a)$ and $e(M)=\max_{a\in M}Q(a)-J(M)$. At the same state and against the same action values,

$$
J(M')-J(M)=\ell^{\mathrm{mask}}(M)-\ell^{\mathrm{mask}}(M')-[e(M')-e(M)].
$$

Expansion improves return only when the reduction in exclusion loss is large enough to offset increased selection loss. In multiple steps, changed history distributions also matter.

If a one-step logging policy always selects a retained action of mean value $v\in[0,1]$ and never selects an omitted action, bounded reward alone gives the sharp region

$$\mathcal I_{\mathrm{mask}}(v)=[0,1-v].$$

The omitted mean can vary over $[0,1]$ without altering the logging law; its exclusion loss is $\max(0,q-v)$, which attains every value in this interval. This is population identification, not a sample confidence interval [@khan2024]. Additional action coverage or justified structural assumptions are needed to estimate omitted PHM continuation values.

### 4.4 Why match tool count

Consider $n$ one-step actions with fixed values $q_a$ and a uniformly chosen size-$k$ subset $S$, with no forced retained action. A uniform selector within $S$ has

$$
\mathbb E_S J(S)
=\frac{1}{k}\sum_{a=1}^nq_a\Pr(a\in S)
=\frac{1}{n}\sum_{a=1}^nq_a,
$$

because each action is included with probability $k/n$. With a unique maximizer, its inclusion probability is also $k/n$. Thus changing the chance of retaining the optimum does not necessarily change the selector's mean return. For ordered values $q_{(1)}\leq\cdots\leq q_{(n)}$,

$$
\mathbb E_S\max_{a\in S}q_a
=\sum_{j=k}^nq_{(j)}\frac{\binom{j-1}{k-1}}{\binom nk}.
$$

The coefficient counts subsets whose largest element has rank $j$. These elementary counting identities motivate a cardinality control; they neither assume that an LLM selects uniformly nor predict its performance. The supplementary theory gives the extension when terminal actions are forced to remain visible.

### 4.5 Risk and sampling units

Population risk is $R_{\mathcal D}(\pi)=\mathbb E_{e\sim\mathcal D,\xi}L(e,\pi,\xi)$; empirical risk averages the observed loss over held-out assets and trials. Conditional on fitted numerical models and frozen policies, independent asset blocks support concentration arguments for additive bounded losses. Macro-F1 and AP require cohort-level recomputation under paired asset-block resampling. Repeated trials do not create additional independent assets, and training risk does not establish performance under a shifted deployment distribution.

## 5. Minimal method and controlled comparisons

The principal comparison uses the existing Generic and Graph policies with unchanged numerical tools. A four-cell experiment crosses current-state cue on/off with graph visibility on/off. Historical decision-state labels are removed from provider-visible tool messages equally across these cells; the original rollout remains available for analysis. Original Generic/Graph conditions and the component conditions are distinct interventions.

The cardinality control compares the cue-free state mask with a cue-free randomized mask. Only Analyze and Check are altered. At the same history, it samples the same number of nonterminal tool names from the sorted shared catalog, preserves the original membership of submit and stop, and retains catalog order and schema contents. Other states are unchanged. A fixed run seed defines a repeatable subset; equal catalogs and cardinalities give the same subset regardless of state label. Revisiting a state does not redraw the control. A coincident subset is retained rather than resampled to force disagreement.

This construction matches counts and termination permissions conditional on the same history. Different policies may visit different histories and incur different prompt tokens, tool calls and costs. Tool schemas have different lengths, so equal cardinality is not token matching. The policy contrast measures the effect of this defined identity replacement, not a pure semantic mediation effect or an estimate of $Q^*$.

Persistence ablations require a changed reachable intervention. Identical action distributions at every reachable history, under the same initial distribution and environment, induce identical rollout distributions by induction. A switch that reconstructs the same state from full history is therefore a null manipulation for that task. Dynamic event control and interval-guided exposure remain separate conditions.

## 6. Experimental design

### 6.1 Mechanical tasks and numerical capability

The main tasks are asset-disjoint vibration diagnosis and released-window replay through PHMFactory. Arms share labels, channels, sampling frequency, split, observation budget, numerical experts and evaluator. Pure length comparisons require nested prefixes of the same longest sequence, separating fixed-total from fixed-per-window budgets. The existing evenly spaced selector changes records with sequence length and therefore measures joint sampling/resource sensitivity.

The numerical axis compares the existing frozen reference, a validation-selected single representation, static probability fusion with validation-fixed weights, and training-only numerical routing over the same representation bank. Learned experts are exposed equally to all agent arms. Representation, objective and model capacity are changed independently where applicable. The present graph is training-free; it has no optimization loss to ablate. Numerical checkpoint selection and normalization use training/development assets only, followed by checkpoint reload and prediction-to-metric recomputation.

### 6.2 Policy references and external tasks

Policy references include unchanged Generic, Scripted, a prompt-information-matched control, original Graph, the cue/filter cells and the cardinality control. StateFlow and Reflexion require faithful state/prompt or feedback/memory mechanisms, accounting for every call and permitted observation. A renamed local controller is not a reproduction of either method.

Five external families are specified separately: PTB-XL ECG, UCI HAR inertial activity, SMAP/MSL spacecraft telemetry, SMD server telemetry and SWaT process instrumentation. Admission must preserve patient/subject/machine identity or temporal blocks, task-appropriate labels and each dataset's published acquisition semantics. PTB-XL is not silently reduced to a single-label task. A single SWaT plant does not provide independent cross-plant replications. These transport studies are not pooled into a mechanical diagnosis headline score; their shared-runtime bindings and model reproductions remain incomplete.

### 6.3 Estimands and falsification

Let $\theta_{cf}$ be the declared cohort statistic for cue $c\in\{0,1\}$ and filter $f\in\{0,1\}$. Report

$$
\Delta_c(f)=\theta_{1f}-\theta_{0f},\qquad
\Delta_f(c)=\theta_{c1}-\theta_{c0},
$$
$$
\Delta_{cf}=\theta_{11}-\theta_{10}-\theta_{01}+\theta_{00}.
$$

Equal-weight marginal effects average the two simple effects for the corresponding factor. Original Graph-minus-Generic differs from $\theta_{11}-\theta_{00}$ because component histories are sanitized identically under a distinct rule. Persistence uses the direct Graph-minus-no-memory contrast on matched assignments.

Let $\mathcal I$ be the frozen set of asset/trial assignments, including the declared seed schedule. For each arm $p$, let $D_p(\mathcal I)$ contain its retained evaluation records and let $\Theta$ be the registered cohort statistic. The planned analysis uses the finite pooled contrast

$$
\widehat\Delta_{\mathrm{rel}}^{\mathrm{pool}}
=\Theta\!\left(D_{01}(\mathcal I)\right)
-\Theta\!\left(D_C(\mathcal I)\right).
$$

The shared scorer pools assigned trials and recomputes the statistic. For nonlinear AP or Macro-F1 this differs from averaging per-seed statistics; the latter is not the registered primary contrast. A finite seed schedule also does not integrate every possible mask. A nonpositive pooled contrast fails to support a benefit of the stage-specific identities under this comparison. It does not imply that all workflow knowledge is ineffective.

Uncertainty is conditional on the frozen mask/seed schedule rather than an interval over all possible randomized masks. Averages and uncertainty preserve matched asset blocks and use the same resample indices across contrast terms. Mechanism checks inspect state activation, actual visible masks, premature submission, repetition, numerical-source consistency and expenditure. All assigned stops, invalid outputs, budget exhaustion and provider failures remain recorded. Undefined metrics and complete denominators are reported, and resumed attempts do not erase earlier costs.

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

Graph-guided visibility must balance preserving useful analyses with selecting among them. A conditional coverage bound describes omitted value, but does not control all selector errors or identify omitted values from unsupported logs. The cardinality control turns the distinction into a concrete PHM experiment: hold tool count, state cues and terminal visibility fixed, and vary analysis-stage tool identities.

The current controller represents workflow progress rather than a calibrated fault posterior. Its public-event profile does not infer physical onset. The analytical and exact-model findings delimit interpretable comparisons of this controller; matched diagnostic and replay outcomes are required to establish its industrial value.
