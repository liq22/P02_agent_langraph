# Instruction Indexing and Tool Exposure in Graph-Guided PHM Agents

## Abstract

A PHM agent must choose not only a diagnosis but also the analyses that support it. Explicit control can focus these choices while preventing further inspection when the current evidence is insufficient. We study this trade-off with the language model, procedural instruction catalog, numerical experts, observation access, budgets and evaluator held fixed. A history-conditioned controller supplies an optional active-block index and a stage-dependent tool menu. Four conditions separate indexing from tool-schema exposure without introducing additional stage-specific advice. The two primary contrasts measure indexing with global tools and menu restriction after indexing. A finite-horizon analysis separates excluded action value from selection error within the visible set. The controller also has a concrete acquisition boundary: in event-free, non-replay trajectories without call errors, its masked policies cannot read a second window after the first successful acquisition. This property motivates testing whether lower workflow error comes at the cost of restricted evidence collection. Existing exact calculations illustrate beneficial, null and harmful restrictions. Matched PHM task outcomes, rather than state compliance, are required to determine the diagnostic and cost consequences of the proposed comparisons.

## 1. Introduction

Mechanical diagnosis depends on a sequence of evidence-gathering decisions. An agent acquires a bounded vibration window, selects numerical analyses, examines the resulting artifacts and decides whether to inspect further or submit. Scientific assistants such as Coscientist and ChemCrow demonstrate how language models coordinate external computation [@boiko2023; @bran2024]. In PHM, the relevant question is whether this coordination supports reliable decisions under limited measurement and computational resources. A valid computation can still operate on insufficient evidence.

Reactive agents already use interaction history. ReAct interleaves actions and observations, and Reflexion incorporates feedback into subsequent attempts [@yao2023react; @shinn2023reflexion]. Explicit control provides a particular interpretation of progress and changes how the next decision is presented. Its benefit therefore cannot be attributed merely to the existence of memory, nor separated from supplied procedural advice by comparing a detailed controller prompt with a shorter generic prompt.

State-driven workflows are established. Finite-state controllers represent policies under partial observability [@hansen1997]. StateFlow extends state-dependent instructions and transitions to language-model workflows and includes refined-prompt and state-removal comparisons [@wu2024stateflow]. PHMForge evaluates industrial tool orchestration, including verification, distracting tools and data discovery [@li2026phmforge]. These works motivate a more specific PHM question: what changes when an agent receives an explicit pointer to already available instructions and a stage-dependent menu of tools?

The two interventions require separate interpretation. A semantic stage label such as Analyze also acts as a concise instruction. A tool menu changes prompt content, the choices exposed to the model and the inferred stage. We therefore give all conditions the same numbered instruction catalog and manipulate only its active-block index and tool-schema exposure. The comparison is conditional on that catalog; it does not equate catalog-guided behavior with an unconstrained reactive baseline.

Restricting a menu can reduce distracting choices but also hide a useful action. Standard value analysis separates exclusion loss from selection loss among retained actions [@schulman2015; @geist2019]. Confidence-based elimination supplies a conditional bound on omitted value [@evendar2006], while off-policy analysis explains why executed logs alone may not identify that value [@jiang2016; @khan2024]. These distinctions motivate task-level comparisons rather than interpreting fewer calls or valid transitions as lower diagnostic regret.

The study specifies a controlled intervention on instruction indexing and tool exposure, derives its implementation-specific acquisition boundary, and evaluates the associated hypotheses through paired PHM tasks. The central empirical questions are whether indexing helps under global tools and whether restriction helps once the active instruction is explicit. The original Graph-versus-Generic comparison remains a secondary system comparison; earlier semantic-cue variants explain the development of the design. No effect is obtained by subtracting results from these different prompt families.

## 2. Related work

**State-driven decision control.** Hansen studies finite-state policy evaluation with a specified environmental model [@hansen1997]. StateFlow defines transition and output functions over cumulative context [@wu2024stateflow]. Its refined ReAct baseline follows an intended workflow without the full state controller. Removing its Observe state still allows table exploration through the Solve prompt. Thus removing a state need not remove the associated capability. The present study focuses on the actual interfaces exposed to a fixed PHM agent, rather than the number or names of controller states.

**Scientific and industrial tool use.** Coscientist and ChemCrow couple model decisions to external numerical tools [@boiko2023; @bran2024]. PHMForge provides PHM-oriented tools and mechanism ablations [@li2026phmforge]. Here numerical capability is fixed within each comparison. The question is how an agent selects and executes available computations, including whether a progress-dependent menu prevents further evidence acquisition.

**Action masking, value and support.** Invalid-action masking has an established policy-gradient analysis [@huang2022masking]. A PHM workflow menu additionally hides actions that the global environment permits. Even-Dar, Mannor and Mansour develop confidence-based action elimination [@evendar2006]; Jiang and Li study off-policy evaluation [@jiang2016]; Khan, Saveski and Ugander study partial identification without overlap [@khan2024]. Our value bounds and equivalence arguments specialize this reasoning. They do not identify an unobserved PHM action value or provide a general improvement theorem for language-model menus.

**Numerical representation.** Fixed features, learned representations and foundation models such as MOMENT can improve prediction independently of agent control [@goswami2024]. Reference models, validation-selected single methods, static fusion and numerical routing belong to a separate capability comparison. Changing that capability in only one controller arm would prevent attribution to decision organization.

## 3. Problem and intervention

The shared world is $\mathcal W=(\mathcal D,\mathcal T,\mathcal A,\mathcal B,P,\mathcal E)$: data access, tasks, global actions, budgets, environmental response and independent evaluation. Public task context, ordered action/result/error history and remaining budget form $h_t$. Private diagnosis targets are available only to $\mathcal E$. Policies share access and release rules but may produce different realized histories.

A controller is $G=(\mathcal M,m_0,\delta,c,\Gamma)$, with memory $m_t=(z_t,\nu_t)$ updated by $\delta$. The phase $z_t$ represents analysis progress; $\nu_t$ records the last consumed public event. The current base profile is event-free. Its phases correspond to acquisition, catalog inspection, numerical analysis, prediction checking, recovery and submission. The model retains public history alongside this explicit controller state. These phases are not a posterior distribution over faults.

Let the fixed instruction catalog be

$$
B=((b_j,d_j))_{j=1}^{6},\qquad b_j\in\{\mathrm{B01},\ldots,\mathrm{B06}\}.
$$

Each $d_j$ is the unchanged base-stage instruction. Every condition receives the complete catalog in the same order, once per request. An index supplies only the corresponding block identifier. It does not repeat the selected instruction. The identifiers remove imperative stage names from the pointer; their common character width does not assert tokenizer equivalence or eliminate order-related cues.

For index indicator $i$ and menu indicator $m$, the model receives

$$
x_t^{im}=\rho(h_t,B)\oplus i\,L(z_t)\oplus\operatorname{Schema}(\Gamma_m(z_t)),
$$

where $\Gamma_0$ is the global catalog, $\Gamma_1$ the existing stage-conditioned subset, and $\rho$ applies the same historical-state rendering in every arm. The term $L$ is the block-index annotation. This defines four conditions: catalog-global, indexed-global, catalog-masked and indexed-masked.

Schema exposure is a composite interface intervention. It changes visible descriptions, menu size, implicit phase information and the allowed-name list used by the common execution path. Its effect is not equivalent to applying a pure support constraint to an otherwise identical model input.

## 4. Value and behavioral boundaries

### 4.1 Exclusion and selection

For a finite-horizon decision model with absorbing termination, let $Q_t^*,V_t^*$ denote unrestricted optimal task values and let $A_G(s)$ be a nonempty retained action set. Define

$$
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{u\in A_G(s)}Q_t^*(s,u),
$$
$$
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in A_G(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$

For a policy supported on that set,

$$
V_0^*(s_0)-V_0^\pi(s_0)
=\mathbb E_\pi\sum_{t<T}\big(\ell_t^{\mathrm{mask}}+\ell_t^{\mathrm{select}}\big).
$$

The equality follows by substituting the Bellman relation into $V_t^*-Q_t^*$ and telescoping. Different policies visit different states, so differences of these terms are not automatically causal mediation effects. Rejected calls and provider failures remain in empirical outcomes; they are not silently treated as valid within-set choices. In PHM, unknown $Q^*$ prevents transition validity, tool count or invalid-call rate from serving as observed regret.

If simultaneous intervals $[L_a,U_a]$ cover all action continuation values, then

$$
0\leq\ell^{\mathrm{mask}}(s)\leq
\max\left(0,\max_{a\notin A_G}U_a-\max_{u\in A_G}L_u\right).
$$

The bound is zero for full exposure. It specializes confidence-based elimination; the operational controller does not estimate such calibrated PHM intervals. Even valid coverage does not guarantee better selection after expanding the menu. The supplementary analysis preserves the corresponding selection and unsupported-logging counterexamples.

### 4.2 Information equivalence and interface cost

For the event-free base, suppose the complete retained history suffices for the phase map: equal rendered public histories imply equal phases. Then $Z_t=f(\widetilde H_t)$ and

$$
\sigma(\widetilde H_t,Z_t)=\sigma(\widetilde H_t).
$$

An unrestricted annotated policy can be composed with $f$ to obtain a history-only policy with the same action kernel. Conversely, the annotated policy may ignore the index. Therefore their optimal **task utilities** agree; restricting feasible action support cannot increase that unrestricted optimum.

Here $J_{\mathrm{task}}=\mathbb E[R_{\mathrm{task}}]$ excludes the computation and serialization of the interface. Input/output tokens, elapsed time and tool use are reported separately. With a priced cost $C$ and $J_\lambda=J_{\mathrm{task}}-\lambda C$, equal task value need not give equal net value. A fixed language model is also not assumed to implement every history-policy composition. Indexing can alter its computational behavior without adding fault evidence.

### 4.3 Menu information and reacquisition

The six base-stage tool sets are distinct when the shared catalog contains the declared tools. Their identities therefore determine the base phase, even without an explicit index. Indexing under the masked menu measures an incremental presentation effect after this implicit phase signal. It is not an independent introduction of all phase information. The dynamic Monitor, Revise and Recover rules share a menu, but that observation does not describe the event-free experiment.

The non-replay base has a stronger operational boundary. After the first successful read, its public history permanently records that acquisition. Without a call error, subsequent phases belong to catalog inspection, analysis, checking or submission; none exposes another window read. Thus, for supported error-free non-replay trajectories,

$$
N_{\mathrm{successful\ window\ reads}}\leq 1.
$$

Recovery reopens acquisition after an observed error. Consequently, a valid but insufficient first window does not itself open an error-free reacquisition route. The result does not state that every diagnosis needs a second window, nor that recovery makes reacquisition globally impossible. It identifies a falsifiable restriction: a menu may reduce invalid calls while preventing further evidence collection within a larger global read budget. Replay is excluded because successful prediction can advance it to acquisition of the next released window.

### 4.4 Inactive ablations and risk

Under the event-free base and unchanged history handling, persistence and replanning switches affect only unreachable event-dependent branches. Full, no-memory and no-replanning consequently induce identical interfaces on reachable histories. With common response, decoding and environment rules, induction gives the same rollout law. These switches are negative controls for this task, not evidence against memory or replanning generally.

Population risk averages task loss over the intended asset distribution and model randomness; empirical risk is computed on the assigned assets and trials. Repeated runs do not create new independent bearings. Nonlinear cohort statistics such as Macro-F1 and Average Precision are recomputed within paired asset-block resamples rather than averaged across episodes. Neither the task-value identity nor a low observed error establishes a guarantee under an untested deployment shift.

## 5. Experimental design

### 5.1 Primary contrasts and comparison hierarchy

For a fixed catalog $B$ and matched assignment set $\mathcal I$, let

$$
\theta^B_{im}=\Theta(D^B_{im}(\mathcal I))
$$

be the registered pooled task statistic. The two primary contrasts are

$$
\Delta_{\mathrm{index}}^{\mathrm{global}}(B)=\theta^B_{10}-\theta^B_{00},
\qquad
\Delta_{\mathrm{exposure}}^{\mathrm{indexed}}(B)=\theta^B_{11}-\theta^B_{10}.
$$

The first changes the explicit pointer with global tools retained. The second changes schema exposure after the pointer is already explicit. The other simple effects, joint contrast and interaction are secondary:

$$
\Delta_{\mathrm{int}}(B)=\theta^B_{11}-\theta^B_{10}-\theta^B_{01}+\theta^B_{00}.
$$

Interaction can reflect redundant, complementary or conflicting interface signals; it does not by itself identify graph-topology synergy. All effects are conditional on $B$, including the burden of searching its catalog. An index gain is not a comparison against concise ReAct, and an absent gain does not establish that domain knowledge is ineffective.

The original Graph-versus-Generic study is a secondary system comparison. Earlier semantic-cue and fixed-semantic-catalog variants document the design progression and may be reported separately when compatible results exist. They do not provide interchangeable controls or quantities that can be subtracted to isolate the new effect. The existing cardinality-matched menu control addresses a different question about analysis-stage tool identities and remains supplementary.

### 5.2 Tasks, controls and falsification

The core tasks are vibration fault diagnosis and ordered-window replay through the shared PHM environment. Each comparison fixes asset assignment, labels, measurement channels and sampling, numerical experts, model settings, budget and evaluation. Fitting and model selection use the designated training and validation assets. The existing shared fitted reference is reused across matched treatments.

Indexing is tested against improved instruction selection and execution, not against increased information about the fault. Menu exposure is tested against reduced distraction, implicit phase signaling, instruction/menu conflict and prevented reacquisition. Completion, numerical grounding, repeated actions, premature submission and recovery provide supporting observations. A global read budget larger than one does not itself prove that another read is useful; reacquisition effects require task evidence rather than read counts alone.

The current graph is training-free. Representation, training loss, fusion and numerical routing are varied only in a separately justified capability study, with the resulting expert pool supplied equally to all controller arms. StateFlow, Reflexion and planning methods require faithful implementations and matched call accounting before serving as same-protocol baselines; their published scores are not local reproductions.

### 5.3 Sampling, temporal execution and cost

Dataset families, independent assets and stochastic repeats are separate sample counts. Diagnosis and replay are analyzed separately. Repeated reliability requires actual repeated outcomes and a complete assigned denominator, not eight task/condition configuration entries. Paired resampling retains the physical asset as the cluster. Observed-only pilot summaries do not estimate provider uncertainty.

Condition order is randomized within the existing seed/rotation/task schedule, with independent agent histories. This current schedule executes each condition over its assigned cohort; it is not asset-level interleaving. Fine-grained attribution under a changing provider requires an asset/trial-block interleaved schedule or an explicitly narrower temporal interpretation. Timestamps and observed provider/model fields must remain available. A formal temporal-stability claim is not supported by the present plan alone.

All assigned stops, malformed outputs, exhausted budgets and provider failures remain recorded. Resuming a run does not erase prior costs. The two primary task contrasts are specified before evaluation; secondary process comparisons do not replace a failed primary result. Transition-count strata describe observed behavior and are not causal subgroups, because transitions themselves depend on treatment.

### 5.4 Length and dynamic scope

A pure horizon study fixes a longest sequence and uses nested prefixes, with fixed-total and fixed-per-window resource regimes analyzed separately. The current window-count variation also changes selected samples and resource allowances, so it measures joint sensitivity. Long-horizon benefit and persistent-memory efficacy remain separate empirical hypotheses.

Dynamic revision additionally requires the same released public operating-condition events and common history rendering across arms. Such an event is not a fault onset inferred from vibration. Dynamic states must run through the shared execution path; a stage change alone does not demonstrate a revised action. External sensor-domain transport follows the core PHM results only after task-specific admission and preserves its own target and temporal semantics.

## 6. Results and current evidence

Existing exact calculations validate the distinction between restricted opportunity and actual selection. In the four-step reference, the best fixed route, aligned two-route mask and harmful singleton return 0.6000, 0.7625 and 0.5000, respectively. Across the retained 24 horizon/policy settings, the maximum decomposition residual is $1.67\times10^{-16}$. Equal normalized values across the three even horizons are a construction-dependent null result, not evidence about real long sequences.

A failed-coverage example reports a zero bound while true exclusion loss is 0.85. A covered example reduces its bound from 0.2 to zero while uniform-selection return changes from 0.8 through 0.4 to 0.5667. Two observationally identical masked logging worlds have exclusion losses 0 and 0.45. Finally, enumeration of all 63 nonempty subsets of six fixed-value actions gives average return 0.5 at every cardinality, while equally sized three-action sets range from 0.2 to 0.8. These retained calculations support the analytical boundaries; they are not fitted PHM or language-model outcomes.

The base menu distinctions and error-free single-acquisition property follow from the declared controller. Their diagnostic consequences, the two primary index/exposure contrasts and repeated reliability have not yet been established on matched PHM cohorts. No industrial improvement is inferred from implementation tests, metadata readability or the exact examples. The empirical result table remains contingent on the declared four-condition task study.

## 7. Discussion

The useful question is not whether an agent has a graph, but which decision-relevant consequences the graph introduces. A common numbered catalog isolates the effect of an active-block pointer from adding new stage-specific advice. The accompanying tool menu remains a composite intervention whose informational and operational effects should be interpreted together.

The present controller also shows why progress tracking and evidence sufficiency should not be conflated. A successful read advances the non-replay workflow even when another measurement could be useful, and acquisition becomes available again only through error recovery. This is a concrete candidate failure mechanism, not proof that its task performance is worse. Real paired outcomes must establish when indexing helps, when exposure restrictions harm, and whether any benefit is diagnostic, reliability-related or economic. Broader claims about persistent memory, topology or long-horizon reasoning require their corresponding interventions and evidence.
