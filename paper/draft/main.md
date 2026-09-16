# Value Coverage and Decision Control in Graph-Guided PHM Agents

## Abstract

Restricting a diagnostic agent's tools can simplify its choices while excluding an analysis needed for a correct decision. We study this trade-off through graph-guided state cues and tool visibility in a fixed PHM environment. A finite-horizon value decomposition distinguishes losses caused by excluding actions from losses caused by selection within the retained set. Building on confidence-based action elimination, we formulate a value-coverage bound for a heuristic mask. When action-value intervals cover simultaneously, the bound limits exclusion loss and yields a terminating action-exposure procedure. A cue-by-filter design separates two components of the existing graph policy while preserving its observations, numerical tools and budgets. Twenty-four exact finite-model configurations verify the decomposition to numerical precision. A deliberately uncovered interval set yields a bound of zero despite an actual exclusion loss of 0.85, establishing the importance of the coverage assumption. Even with valid intervals, a second exact example reduces exclusion loss to zero while lowering the selector's expected return from 0.8000 to 0.5667. A pair of observationally equivalent worlds further separates what masked logs identify from what requires additional action coverage. The PHM evaluation specifies asset-disjoint diagnosis and released-window replay with all terminal outcomes retained. Current evidence comprises exact-model calculations and historical numerical references; matched language-model cohorts are required to determine diagnostic benefit and reliability.

## 1. Introduction

A vibration diagnosis depends on the measurements and numerical analyses that support it. Language-based scientific assistants can coordinate external computations, as demonstrated by Coscientist and ChemCrow [@boiko2023; @bran2024]. For mechanical equipment, the diagnostic question is whether that coordination selects useful analyses under finite sensing and computational budgets. A successfully executed workflow can still lead to an incorrect diagnosis when its numerical information is insufficient.

ReAct updates decisions through action-observation interaction, and Reflexion introduces feedback-based memory [@yao2023react; @shinn2023reflexion]. Both use history. Explicit graph control adds a more specific intervention: a state-dependent instruction and a restricted view of tools. Comparing these interventions requires keeping the underlying model, history and computational capabilities fixed.

StateFlow provides a direct precedent for state-driven workflows, including state-removal and refined-prompt controls [@wu2024stateflow]. PHMForge evaluates PHM-oriented algorithmic tools, sequencing, verification and distracting tools [@li2026phmforge]. These studies establish the relevance of workflow control and domain tools. The question considered here is the value potentially removed by a heuristic PHM visibility rule and its relation to the independent effects of state cues and filtering.

Feasibility and usefulness are distinct. Invalid-action masking removes actions that violate environmental rules and has an established policy-gradient analysis [@huang2022masking]. A workflow mask may instead hide an action that is valid but appears unnecessary at the current analysis stage. Reducing malformed calls can therefore coexist with excluding a diagnostically useful operation.

Sequential value analysis makes this trade-off explicit [@schulman2015; @geist2019]. Confidence-based action elimination already compares upper and lower value estimates to remove suboptimal actions [@evendar2006]. We apply this principle to assessing an existing heuristic mask: the important quantity is the largest plausible excluded value relative to the best assured retained value. The assessment is conditional on simultaneous coverage of the action-value intervals, rather than on the model's stated confidence in a diagnosis.

Two further distinctions determine the evaluation. Expanding the visible set preserves more valuable actions but may increase selection error. Moreover, the outcomes of actions that the logging policy never takes are not identified by those logs alone [@jiang2016; @khan2024]. Direct component interventions measure policy effects without equating logged execution statistics with optimal continuation values.

The empirical design separates mechanism from total treatment effect. The original GraphDecisionAgent combines a current-state prompt with state-specific tool visibility. A four-cell design varies these components independently within the same task population, numerical expert pool and budget. Repeated trials are grouped by physical asset, with task and resource uncertainty reported separately [@agarwal2021].

Our analysis develops a value-coverage bound and a finite exposure rule for heuristic PHM masks. The method specification provides component-separated graph controls and a criterion for determining whether an ablation changes reachable behavior. Exact finite-model experiments establish the conditional analysis, including beneficial filtering, harmful filtering, violated coverage, selection deterioration after expansion and nonidentification under masked logging. The resulting PHM study tests when these distinctions explain task performance; its matched language-model cohorts remain incomplete.

## 2. Related work

**State control and action masking.** StateFlow defines states and transition decisions from context, and evaluates No_Observe, No_Error and No_Verify variants [@wu2024stateflow]. Its state and prompt controls are direct precedents for this work. Huang and Ontanon analyze masked policy gradients and compare invalid-action masks with penalty-based alternatives [@huang2022masking]. Their feasibility setting differs from heuristic visibility over valid PHM analyses. We retain the Benchmark's feasibility rules and vary only the additional policy-level restriction.

**Confidence-based action elimination.** Even-Dar, Mannor and Mansour develop action-value bounds, elimination procedures and stopping rules for bandit and reinforcement-learning problems [@evendar2006]. Our interval inequality specializes this established reasoning to the loss of an existing heuristic mask. It does not provide a new general elimination principle or sample-complexity bound. The application requires identifying the omitted PHM actions, their continuation values and the information available to estimate them.

**Scientific and PHM agents.** Coscientist and ChemCrow separate language decisions from external scientific computations [@boiko2023; @bran2024]. PHMForge provides domain tools, scenario-specific verification and distractor/data-discovery comparisons [@li2026phmforge]. Here the principal contrast fixes the raw-window task and numerical capabilities while changing the control policy. The policy's access to useful computations, rather than the availability of new treatment-only tools, is the variable of interest.

**Logged support and policy evaluation.** Jiang and Li formulate sequential off-policy evaluation through target-to-behavior action probabilities [@jiang2016]. Khan, Saveski and Ugander develop sharp partial-identification bounds when overlap fails, including bounded-response and smoothness cases [@khan2024]. Their results establish that unobserved action outcomes require additional assumptions or data. We use a bounded one-step specialization to delimit claims about a PHM mask; neither a complete rollout log nor a narrow uncalibrated interval establishes the values of omitted analyses.

**Numerical time-series methods.** A stronger representation can improve the numerical expert pool independently of the Agent controller. MOMENT provides a recent foundation-model comparison for time series [@goswami2024]. Fixed-feature, learned-representation, static-fusion and numerical-routing references belong to a separate capability axis. A control comparison must expose the same admitted numerical pool to both arms.

## 3. Problem formulation

Let the shared world be $\mathcal W=(\mathcal D,\mathcal T,\mathcal A,\mathcal B,P,\mathcal E)$: data access, tasks, feasible actions, resource limits, response dynamics and independent evaluation. At time $t$, the public history $h_t$ and remaining budget $b_t$ form $s_t=(h_t,b_t,t)$. A graph state $z_t=f(h_t)$ supplies a cue $c(z_t)$ and a nonempty visible set $M(s_t)\subseteq\mathcal A(s_t)$. The model selects a canonical action from this interface. Targets are available only to $\mathcal E$.

The finite-action analysis concerns fully specified candidate actions. Alternatively, each tool-family value must represent the best continuation over its full admissible parameter set. An interval for one parameter setting does not bound an entire tool schema. The current language-agent interface has not been equipped with such calibrated family-value intervals.

The base controller tracks successful reads, catalog discovery, numerical analysis, prediction, submission and recovery after observable errors. These are workflow-progress states rather than posterior fault hypotheses. The Hypothesize state follows catalog progress. In the current replay profile, the transition to Check counts eleven successful operator calls tied to the current sample after its read. This is an execution-progress rule, not a test of distinct-feature completeness or diagnostic sufficiency. Monitor and Revise belong to a separate public-condition-event profile. An externally supplied change event and a fault onset inferred from vibration are different observations.

PHM outcomes retain the registered task metrics: diagnosis Macro-F1, anomaly scoring and assigned-window replay Average Precision under its declared missing-score rule. Grounding measures numerical-source consistency. Coverage, repetition, valid calls, inference/tool time and cost are explanatory measurements, reported without a combined weighted score.

## 4. Control-loss analysis and value coverage

### 4.1 Exclusion and selection

For unrestricted optimal continuation values $V_t^*,Q_t^*$, define

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in M(s)}Q_t^*(s,u),
$$
$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in M(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

For a finite policy supported on $M$, with absorbing termination and zero terminal value,

$$
V_0^*(s_0)-V_0^\pi(s_0)
=\mathbb E_\pi\sum_{t<T}
\left(\ell_t^{\mathrm{mask}}(s_t)+\ell_t^{\mathrm{select}}(s_t,a_t)\right).
$$

The losses sum to $V_t^*-Q_t^*$. Substituting the Bellman relation and summing cancels consecutive values. This identity separates the value removed by a mask from imperfect choice among retained actions. The terms depend on the policy's visited histories, so their difference between policies is not automatically a causal mediation decomposition. In real PHM, $Q^*$ is unavailable and invalid-call counts cannot substitute for it.

### 4.2 A conditional bound and exposure rule

Suppose finite real intervals $[L_a,U_a]$ contain the action continuation values simultaneously at a state. Define

$$
C(M;s)=\max\left(0,\max_{a\notin M}U_a-\max_{m\in M}L_m\right),
$$

with $C=0$ when the full feasible set is retained. If a global maximizer is retained, mask loss is zero. Otherwise, the best excluded value is bounded by the outside upper maximum and the best retained value by the inside lower maximum. Hence

$$0\leq\ell^{\mathrm{mask}}(s)\leq C(M;s)$$

on the simultaneous coverage event.

Exposing an excluded action with largest upper bound cannot increase $C$: it removes a candidate from the outside maximum and can increase the retained lower maximum. Repeating this operation terminates after finitely many additions at any finite nonnegative tolerance, because the full action set has $C=0$. This rule guarantees termination and a conditional exclusion-loss bound, not minimum-cardinality exposure.

A production interval policy would require training-only estimation, justification of coverage over adaptive histories, and accounting for estimation cost. Marginal intervals do not automatically provide simultaneous coverage. The current exact-model implementation tests the bound with known continuation values; the original PHM graph policy remains unchanged.

### 4.3 What coverage does not guarantee

For a one-step decision, write $J(M)=\mathbb E_{a\sim\pi_M}Q(a)$ and $e(M)=\max_{a\in M}Q(a)-J(M)$. At the same state and for the same action values,

$$
J(M')-J(M)=\ell^{\mathrm{mask}}(M)-\ell^{\mathrm{mask}}(M')-[e(M')-e(M)].
$$

Thus $M\subseteq M'$ improves return only when the reduction in exclusion loss exceeds any increase in selection loss. Monotonicity of the coverage bound alone does not impose this condition. In a multistep comparison, changed history distributions must also be taken into account.

Suppose a one-step logging policy always takes the retained action, whose mean value is $v\in[0,1]$, and never takes one omitted action. With no restriction beyond bounded reward, the omitted mean may take any value in $[0,1]$ without changing the logging distribution. The exclusion loss therefore has the sharp identified set

$$
\mathcal I_{\mathrm{mask}}(v)=[0,1-v].
$$

This is an identification region given the population logging law, not a finite-sample confidence interval [@khan2024]. Finite samples add uncertainty about the retained value; replacing it by a sample mean does not produce a calibrated confidence interval. Development action coverage or an explicitly justified structural model is required before fitting a useful PHM coverage estimator. Direct, matched cue/filter comparisons do not require estimating this unobserved value.

### 4.4 Risk and sampling units

Population risk is $R_{\mathcal D}(\pi)=\mathbb E_{e\sim\mathcal D,\xi}L(e,\pi,\xi)$; empirical risk averages the corresponding observed losses on held-out assets. Condition on fitted numerical models and a frozen policy. Independent asset blocks permit concentration analysis for an additive bounded loss, while repeated trials within one asset remain dependent at the equipment level. Macro-F1 and AP require cohort-level recomputation in paired asset-block resamples. Neither the finite-model identity nor low training risk provides an unconditional guarantee under a shifted deployment distribution. Detailed proofs and the additive-loss concentration statement are in the supplementary theory.

## 5. Minimal method and controlled comparisons

The principal experiment first compares the existing Generic and Graph policies with unchanged numerical tools. The component experiment crosses current-state cue on/off with graph visibility on/off. Historical decision-state labels are removed from provider-visible messages equally across the four component cells. The retained rollout still records them for analysis. Original Generic/Graph outputs and the new factorial outputs are distinct conditions.

An ablation is informative only when it changes the tested intervention. If two policies have identical conditional action distributions at every reachable history, the same initial distribution and the same environment, induction gives identical rollout distributions. Before a no-memory cohort, we therefore compare its selected states and visible tools on reachable development histories. A switch that reconstructs the same state from full history does not test the value of memory in that task.

Interval-guided exposure is evaluated separately from the existing progress-state controller. Its implementation adds actions explicitly according to $C$. It is not an automatic fallback for invalid Agent actions. Without calibrated PHM continuation-value intervals, the original graph cannot be interpreted as implementing this rule.

## 6. Experiment design

### 6.1 Mechanical tasks and numerical capability

The main tasks are asset-disjoint vibration diagnosis and released-window replay through PHMFactory. Compared arms share label ontology, channel, sampling frequency, split, data budget, numerical experts and evaluator. Pure sequence-length comparisons use nested prefixes of the same longest sequence, with fixed-total and fixed-per-window budgets treated separately. The current evenly spaced selector changes the selected records and therefore supports sensitivity analysis rather than an isolated horizon effect.

The numerical axis compares a validation-selected single representation, probability fusion with weights fixed from training/validation, and training-only numerical routing. Time statistics, spectra and envelope features must be meaningful for the measured sampling and operating conditions. These references change numerical capability, not graph control. A learned numerical model is exposed equally to all compared Agent arms. The current training-free graph has no trainable loss to ablate; loss-function experiments belong to the explicitly identified numerical axis.

### 6.2 Policy controls and external tasks

Policy controls include unchanged Generic, a prompt-information-matched control, original Graph and the cue/filter cells. StateFlow and Reflexion require faithful reproductions of their state or feedback mechanisms, including all model calls and permitted observations. A renamed local graph or a reflection suffix is not the same algorithm.

Five external sensor families are specified for supplementary transport tests: physiological ECG, inertial activities, spacecraft telemetry, server telemetry and process instrumentation. Each requires its own target mapping, independent unit and temporal admission rule. These domains are analyzed separately rather than pooled into a mechanical diagnosis headline score. They are not yet integrated into the shared runtime.

### 6.3 Estimands and retained outcomes

Let $\theta_{cf}$ denote the declared task statistic of the component policy, where $c\in\{0,1\}$ enables the state cue and $f\in\{0,1\}$ enables filtering. The simple effects at both levels are

$$
\Delta_c(f)=\theta_{1f}-\theta_{0f},\qquad
\Delta_f(c)=\theta_{c1}-\theta_{c0},
$$

and the interaction is

$$
\Delta_{cf}=\theta_{11}-\theta_{10}-\theta_{01}+\theta_{00}
=\Delta_f(1)-\Delta_f(0)=\Delta_c(1)-\Delta_c(0).
$$

The original Graph-minus-Generic contrast is separate from $\theta_{11}-\theta_{00}$ because the component policies share a distinct history-sanitation rule. The persistence experiment directly estimates $\Delta_{\mathrm{memory}}=\theta_{\mathrm{Graph}}-\theta_{\mathrm{no\ memory}}$ on matched assets and trials. Comparing each condition with an absent Generic arm cannot estimate this difference. An inactive persistence switch remains a null manipulation rather than evidence against memory in general.

Statistical resampling preserves asset blocks and uses identical draw indices across all terms of a contrast. Macro-F1 and AP are recomputed on each resampled cohort. These quantities are direct policy effects, not a causal mediation decomposition of mask and selection losses. Undefined resamples and the complete assigned denominator are reported.

Stopped, invalid, budget-exhausted and provider-failed attempts remain recorded. Cost is presented both per eligible task outcome and across all attempts, so a successful resumption does not erase earlier expenditure. Thresholds and checkpoints are chosen without test outcomes. Complete experiment and data specifications accompany this manuscript; no unfinished comparison contributes an effect estimate.

## 7. Results

### 7.1 Exact finite-model experiment

The executed model contains two equally likely public contexts and three abstract analysis routes. Dynamic programming integrates the process over horizons 2, 4 and 8. At four steps, the best fixed route returns 0.6000 and static uniform route selection returns 0.55833. An aligned two-route mask returns 0.7625. A harmful singleton returns 0.5000, with exclusion loss 0.4250. Interval expansion followed by uniform selection returns 0.7125. Covered greedy choice and the unrestricted oracle both return 0.9250 because the intervals are centered on the known toy values.

Across 24 configurations, the maximum decomposition residual is $1.67\times10^{-16}$. The three even horizons have identical normalized returns by construction, producing a null length effect. The source CSV contains exact-model expectations, not sampled PHM accuracy or LLM success estimates. Static random route selection is not a trained signal-fusion model.

A deliberately incorrect interval set gives $C=0$ while its true exclusion loss is 0.85. This failure isolates the coverage assumption: a narrow interval does not itself make a useful bound. The numerical result and its inputs are retained alongside the successful cases.

### 7.2 Valid coverage with deteriorating selection

In a one-step counterexample, the retained, useful and distracting actions have values 0.8, 0.9 and 0.0. Their respective intervals are [0.8,0.8], [0.9,0.9] and [0,1], so simultaneous coverage holds. Optimistic exposure first adds the distracting action because it has the largest upper endpoint, then the useful action. The selector applies the same uniform-choice rule to each visible set.

The three evaluated tolerances yield coverage bounds of 0.2, 0.1 and 0.0, while expected return changes from 0.8 to 0.4 and then 0.5667. At full exposure, exclusion loss is zero but selection loss is 0.3333. The bound decreases as proved; the return does not improve. This counterexample rules out a policy-improvement interpretation of the exposure rule even when its coverage assumption is satisfied.

### 7.3 Indistinguishable logs with different exclusion losses

Two one-step worlds assign the retained action the same Bernoulli reward with mean 0.5. The omitted action has mean 0.1 in one world and 0.95 in the other, and the logging policy never selects it. Enumerating all 2, 16 and 256 possible reward logs for sample counts 1, 4 and 8 gives total-variation distance zero between the worlds at every count. Their exclusion losses are nevertheless 0 and 0.45. Both lie in the identified interval [0,0.5]. More repetitions of the same unsupported logging policy do not distinguish these worlds.

### 7.4 Existing PHM evidence and incomplete comparisons

The matched PHM and external-domain cohorts remain incomplete. Their results will distinguish total task effect, cue/filter attribution, active revision or memory effects, numerical capability, sequence/resource sensitivity and incurred cost. Until these cohorts are complete, no diagnostic improvement, cross-domain advantage or reliability increase is inferred from the finite-model results.

## 8. Discussion and conclusion

Graph visibility introduces a trade-off between reducing distracting choices and preserving valuable analyses. A value-coverage bound expresses this requirement relative to continuation-value intervals. Its mathematical validity is conditional; its usefulness in PHM depends on estimation quality, adaptive coverage and the capabilities of the admitted numerical tools. The negative examples identify two distinct requirements: the retained-set selector must not deteriorate enough to erase coverage gains, and the data or structural assumptions must support values assigned to omitted actions.

The current controller tracks workflow progress rather than a calibrated fault posterior. Its public-event profile does not infer a physical onset. These boundaries separate a testable industrial decision policy from stronger claims about fault reasoning. Exact positive and negative examples validate the analytical implementation; the component-separated PHM study is required to determine whether the identified mechanisms improve real diagnostic decisions.
