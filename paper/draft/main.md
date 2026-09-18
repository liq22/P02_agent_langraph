# Active-Instruction Indexing and Progress-Gated Tool Exposure in PHM Agents

## Abstract

A PHM agent can receive the right numerical tools yet fail to invoke them, submit prematurely, or continue analysis without improving its diagnosis. We study how explicit instruction indexing and workflow gating change these decisions under a fixed procedural catalog, released data scope, potential expert pool and evaluator. Four conditions separate adding an active-block pointer with global tools from imposing progress-dependent menus after the pointer is explicit. The gate changes both presented schemas and executable action sequences: it suppresses submission before numerical prediction and closes ordinary analysis after prediction. These restrictions do not establish diagnostic benefit. In particular, the diagnosis task provides one distinct legal raw window, so preventing repeated reads cannot be interpreted as removing a second raw observation. A finite-horizon value decomposition distinguishes excluded opportunities from selection among retained actions. The primary empirical endpoint is pooled diagnosis Macro-F1 over first attempts, including recorded non-submissions and provider interruptions; replay is secondary. Paired task outcomes and observed use of post-prediction actions are required to distinguish improved execution from an unhelpful restriction.

## 1. Introduction

A tool-using diagnostic agent must decide which available computations to execute and when to submit their result. Correctly executing a numerical method does not guarantee a correct diagnosis, and simply making a predictor available does not ensure that the agent uses it. Scientific assistants demonstrate how language models coordinate external computation [@boiko2023; @bran2024]. For PHM, the practical question is whether organizing those decisions improves the delivered diagnosis under finite resources.

Explicit control differs from adding diagnostic knowledge. ReAct conditions decisions on interaction history, while Reflexion uses feedback across attempts [@yao2023react; @shinn2023reflexion]. A controller can point to a procedure and constrain its execution without changing the underlying experts or their fitted parameters. The realized numerical path may nevertheless change. A shared expert pool therefore does not imply identical computations across agents.

State-driven workflows are established. Finite-state controllers represent policies under partial observability [@hansen1997], and StateFlow supplies state-dependent instructions, transitions and verification [@wu2024stateflow]. PHMForge studies industrial tool orchestration and associated controls [@li2026phmforge]. These precedents motivate a narrower comparison: with the same PHM procedural catalog supplied to every arm, what is the effect of an active-instruction pointer, and what is the additional effect of progress gating?

The gate is more than a shorter menu. It can require numerical progress before submission and remove opportunities after a prediction. The distinction between a permissible action, an action actually selected and an action that changes the submitted diagnosis is central. A restriction cannot explain a task effect merely because its implementation is visible. In the present diagnosis task, repeated reading retrieves the same fixed array; a loss of distinct raw observations is therefore not the mechanism being tested.

Our contribution is a controlled PHM study of indexing and executable workflow restrictions under common procedural content. It links the implemented action boundaries to two prespecified task contrasts and observable execution patterns. Standard value and information arguments delimit their interpretation; they are not new general control theorems. The substantive empirical question is whether gating improves execution, changes label quality, or closes useful subsequent analysis. None of these outcomes follows from successful implementation alone.

## 2. Related work

**State-driven control.** StateFlow includes refined ReAct and state-removal comparisons. Its Verify state can inspect a generated solution; removing Observe does not remove every exploration capability because another state retains it [@wu2024stateflow]. A state's name or removal consequently does not specify the intervention. We instead examine the schemas and action sequences exposed by the PHM controller. Its prediction-ready state is not a separate post-prediction verification procedure.

**Industrial tools and numerical capability.** PHMForge includes verification, distractor and data-discovery controls [@li2026phmforge]. Representation learning, including foundation models such as MOMENT, changes a different part of the system [@goswami2024]. Our control comparisons hold potential experts and fitted parameters fixed. A learned representation, static fusion or numerical router belongs to a separately justified capability study and must be available equally across its compared control arms.

**Value and incomplete outcomes.** Standard policy-value analysis and confidence-based elimination distinguish retained opportunities from suboptimal selection [@schulman2015; @evendar2006]. Off-policy evaluation additionally requires support or assumptions for unobserved alternatives [@jiang2016; @khan2024]. These results prevent tool counts and logged compliance from being interpreted as observed regret. Repeated-trial reliability is also an established evaluation concern [@yao2024tau]. First-attempt reporting here specifies which outcomes enter the comparison rather than proposing a new reliability metric.

## 3. Common content, different decision interfaces

Let $\mathcal W=(\mathcal D,\mathcal T,\mathcal A,\mathcal B,P,\mathcal E)$ denote the released data scope, tasks, global actions, budgets, environment and evaluator. Public history $h_t$ contains task context, actions, returned artifacts, errors and remaining resources. Private targets remain evaluator-side. The underlying scope is common; the gate deliberately changes the temporal opportunity to invoke data and analysis tools.

The controller computes analysis progress $z_t=f(h_t)$. The event-free base phases concern acquisition, catalog inspection, analysis, prediction readiness, error recovery and submission. They are neither fault posteriors nor estimates of evidence sufficiency. The full history remains available, so this experiment does not isolate an indispensable persistent-memory mechanism.

The catalog $B=((b_j,d_j))_{j=1}^{6}$ contains six unchanged instructions under B01–B06, displayed once in the same order in every request. Indexing appends only the designated block identifier. Equal character width does not establish equal tokenization. For index $i$ and gate $g$, the interface is

$$
x_t^{ig}=\rho(h_t,B)\oplus iL(z_t)\oplus\operatorname{Schema}(\Gamma_g(z_t)),
\qquad \Gamma_0(z_t)=\mathcal A.
$$

The conditions are catalog-global, indexed-global, catalog-masked and indexed-masked. Each uses the same removal of historical state annotations from model-visible tool messages, retaining numerical payloads and errors. The catalog itself may impose an instruction-selection burden; effects are conditional on $B$, not comparisons against every reasonable reactive prompt.

In masked base trajectories, submission becomes available after numerical prediction. A successful prediction then exposes only submission, unless a subsequent call error activates recovery. Gating therefore combines schema reduction, implicit progress information, premature-submission suppression, numerical-path enforcement and post-prediction closure. Its measured effect is the total effect of this specified interface, not pure action masking, topology or planning ability. The six base menus are distinct, so they also encode the phase abstractly; a model need not decode them reliably.

## 4. Value and task-supported boundaries

### 4.1 Opportunity and selection

For a finite horizon with absorbing termination and zero terminal continuation value, define unrestricted optimal task values $Q_t^*,V_t^*$. For a nonempty retained set $A_G(s)$ and supported action $a$,

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in A_G(s)}Q_t^*(s,u),
$$
$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in A_G(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

Bellman substitution and telescoping yield

$$
V_0^*(s_0)-V_0^\pi(s_0)=\mathbb E_\pi\sum_{t<T}
\left(\ell_t^{\mathrm{mask}}+\ell_t^{\mathrm{select}}\right).
$$

This specialization explains the trade-off without identifying either loss from PHM logs. Different policies visit different histories; their loss differences are not automatically causal mediation effects. Invalid calls and interruptions remain empirical outcomes, not valid actions silently projected into the retained set.

If the complete rendered history determines the phase, its deterministic index adds no information to an unrestricted history policy. Policy composition gives the same optimal task utility; restricting action support cannot increase that unrestricted optimum. A finite language model need not implement that composition. Moreover, task utility excludes interface costs: equal task value does not imply equal token use, latency or priced net value. Supplementary theory retains the assumptions and conditional coverage counterexamples.

### 4.2 One raw observation is not a lost second observation

The diagnosis scope permits one sample handle with a fixed window and channel specification. Successful rereads return the same array under new artifact references; changing the window, channels or sample is not another legal observation. Hence, for raw arrays $X_2=X_1$,

$$
I(Y;X_2\mid X_1)=0.
$$

The masked non-replay controller permits at most one successful read on an error-free, event-free supported trajectory. That source property does not remove a distinct raw observation in this task. It may affect repeated access, artifact handling and cost. Nor does determinism imply that processing the same array in a different way is useless to a bounded model. The study leaves the data protocol unchanged and does not claim a demonstrated multi-observation acquisition loss.

### 4.3 Post-prediction closure and activation

On the same error-free non-replay domain, the first successful prediction leads to a menu containing submission alone. Consequently, no further analytical action is exposed before termination. A submission error can reopen recovery; replay follows its own released-window progression. These exceptions are retained.

This is an opportunity boundary, not evidence that additional analysis would improve a diagnosis. We distinguish whether global-tool agents continue after prediction, whether their final label changes, and whether supporting numerical artifacts change. New reference strings alone do not establish new numerical evidence. Procedural completion does not establish that further analysis is valueless, but no evidence-sufficiency threshold is estimated by the controller.

## 5. First-attempt PHM comparison

### 5.1 Endpoint and inference

Diagnosis is primary. Its endpoint is the existing pooled Macro-F1 over all assigned first-attempt outcomes and the three declared diagnosis classes. An attempt without an accepted diagnosis submission is retained as `no_submission`: it contributes a false negative to its true class and is not averaged as a fourth diagnosis class. This operational endpoint reflects both delivered label quality and failure to deliver.

For matched records $D_{ig}^{(1)}(\mathcal I;B)$, the two primary contrasts are

$$
\Delta_{\mathrm{index}}^D=\operatorname{F1}_{\mathrm{macro}}(D_{10}^{(1)})-
\operatorname{F1}_{\mathrm{macro}}(D_{00}^{(1)}),
$$
$$
\Delta_{\mathrm{gate}}^D=\operatorname{F1}_{\mathrm{macro}}(D_{11}^{(1)})-
\operatorname{F1}_{\mathrm{macro}}(D_{10}^{(1)}).
$$

Replay Average Precision uses its unchanged assigned-window and missing-score rules as a secondary outcome. Other simple effects and the interaction are exploratory. Original Graph/Generic and earlier semantic-cue profiles remain separate comparisons, never replacement controls.

Uncertainty uses the existing paired, diagnosis-class-stratified bearing bootstrap. Each sampled bearing retains its windows and model repeats, and the same draws apply to every contrast term. Class bearing counts remain fixed, so the intervals condition on the cohort's class composition rather than deployment prevalence shifts. The two prespecified estimates receive nominal 97.5% percentile intervals with Bonferroni allocation. We report estimates and uncertainty, not an exact small-sample coverage or provider-randomness guarantee. One-bearing smoke results have no inferential interpretation.

### 5.2 Assignment and temporal control

Splits, samples, replay order, window specification, fitted-reference scope, model settings and budgets are frozen before evaluation. Provider-free Scripted acceptance must match the resolved diagnosis and replay assignments, not merely call the same task constructor. Metadata readability alone does not establish waveform correspondence.

Four independent agent sessions run within each bearing, task, rotation and repeat block. Randomized cyclic orders balance each condition's positions to within one occurrence per task/rotation/repeat/budget stratum. The saved plan contains actual assignments and position counts. This is position balance, not a guarantee against carryover or provider drift. An interrupted block remains in the analysis and is not described as simultaneous after resumption.

Before starting a block, the existing request reserve covers the remaining members at their declared turn limits. The invocation ceiling is a safety limit, not a treatment budget or a universal total study allowance. Insufficient capacity stops before starting that block. Completed first outcomes are reused without refitting the shared numerical reference.

### 5.3 Failures and explanatory observations

A provider failure that reaches the native terminal outcome is retained on its first attempt; explicit continuation runs unattempted assignments only. A durable local request-intent record without a complete canonical outcome is indeterminate and blocks automatic resend. It is neither a fabricated failed diagnosis nor a replaceable unattempted case. The safeguard does not establish exactly-once provider execution, and simultaneous loss of log and outcome remains outside it. A complete primary table requires all assigned canonical first outcomes.

Report submission rate, provider interruption, malformed response, unavailable action and budget exhaustion alongside the three-class confusion matrix with a `no_submission` column. Macro-F1 conditional on accepted submissions is a descriptive sensitivity analysis, not a substitute for the primary endpoint. Conditioning on completion can change treatment rankings and selects a treatment-dependent subset.

Mechanism analysis distinguishes attempts to submit before numerical prediction, actual post-prediction analysis, final-label changes, supporting-artifact changes and submission-error recovery. Rates conditional on reaching a prediction use an explicit denominator and remain descriptive; transition strata are not causal subgroups. If global agents never exploit the extra actions, a null task effect does not show that those actions are generally useless. Costs retain known usage, unknown interruption billing, timestamps and resumed-block gaps without deleting unfavorable cases.

## 6. Results

Matched PHM first-attempt outcomes remain unavailable. The two diagnosis effects, secondary replay results and operational costs are therefore unestimated. The task-scope and menu properties in Section 4 delimit testable mechanisms; neither establishes a diagnostic improvement or loss. Earlier exact value/support examples remain supplementary analytical checks, not substitutes for these outcomes.

## 7. Discussion

The central distinction is between providing computations, enforcing a procedure and delivering a diagnosis. Fixed-scope diagnosis does not test whether gating removes a second raw observation. It does test whether a designated instruction pointer and numerical workflow restrictions change execution, premature submission and the use of subsequent analysis. The gate may improve completion without improving submitted labels, suppress useful continuation, or have little effect because the task rarely activates its restrictions. These possibilities require paired outcomes and actual behavior, not inference from graph structure or test counts. Broader claims about long horizons, persistent memory and dynamic revision require separate supported interventions.
