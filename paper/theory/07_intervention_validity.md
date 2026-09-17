# Persistent structure, interface interventions and inactive ablations

## Object and scope

We study $G=\text{persistent decision structure}$ and keep the shared PHM world, model, knowledge source $K_0$, response decoder, resource accounting and evaluator fixed. The explicit controller is

$$
G=(\mathcal M,m_{\mathrm{init}},\delta,c,\Gamma),\qquad
m_t=(z_t,\nu_t),\qquad
m_t=\delta(m_{t-1},s_t,e_t),
$$

where $s_t=(h_t,b_t,t)$ is public history, remaining budget and time. The phase $z_t$ labels analysis progress, and $\nu_t$ is the last consumed public-event token. In the original package, the cue $c(z_t)$ contains the current phase label and stage instruction; in the fixed-bank profile it contains only the phase annotation; $\Gamma(z_t,s_t)$ returns tool visibility. Transitions are induced by $\delta$, rather than an independently changed topology. Public events $e_t$ are released condition metadata, not hidden targets or fault onsets inferred from the signal.

A definition containing only the phase label omits the event-deduplication memory used by the actual controller. Conversely, the model still receives public history: this implementation is not a memory-limited finite-state policy or a sufficient diagnostic belief state. Classical finite-state control and state-driven LLM workflows are precedents, not new formalisms here (Hansen, NIPS 1997, Section 3.1; StateFlow, Section 3.1).

## Four-cell intervention

For indicators $u,v\in\{0,1\}$, the model-facing interface is

$$
I_{uv}(h_t)=\left(\operatorname{render}(h_t;K_0)+u\,c(z_t),\ \mathcal T_v(z_t,h_t)\right),
$$

where $\mathcal T_0$ is the common tool catalog and $\mathcal T_1$ its Graph subset. The expression denotes structured message assembly, not arithmetic on strings. All four cells use the same renderer with top-level historical decision-state metadata removed from tool messages. Numerical tool payloads, action arguments, errors, order and remaining-budget information are otherwise unchanged at the same public history.

The cue factor is a label-plus-instruction package, not a pure state-name intervention. Tool identity can also convey the stage implicitly; removing the explicit cue does not remove all information about the state. Thus the estimands are direct effects of these implemented interfaces. They do not identify topology-only effects or separate latent semantic pathways. $K_0$ is the common knowledge source; state-conditioned presentation belongs to the declared $G$ intervention. A comparison independent of newly supplied procedural wording uses the fixed-instruction profile below.

## Fixed instruction inventory: organization rather than extra advice

The original four cells change a label-plus-instruction cue. Their common source $K_0$ does not ensure that the same procedural text reaches the model at a given history. To test organization conditional on a fixed text inventory, define the ordered bank

$$
B=\big((z,d_z):z\in\mathcal Z_{\mathrm{base}}\big),
$$

containing the unchanged six base-stage instructions. Let $\widetilde h_t$ be the provider-visible public task, usage and action/result/error history after the common removal of top-level historical state metadata. Define a new, separate interface family

$$
I^B_{uv}(\widetilde h_t)
=\big(\operatorname{render}(\widetilde h_t;K_0,B)\mathbin\Vert u\,\operatorname{name}(z_t),\;\mathcal T_v(z_t,\widetilde h_t)\big).
$$

The notation denotes concatenation of a structured annotation, not arithmetic on text. All six instruction entries occur once and in the same order in every arm, including annotation-off arms. The annotation adds only the current phase name, not its advice again. $u$ controls annotation; $v$ controls the existing tool restriction. The bank is independent of the current state, fitted data, targets and PHMskills retrieval. The treatment is event-free; Monitor/Revise instructions are excluded equally from every bank. The existing base state map and terminal rules are unchanged.

This comparison is a specialization motivated by StateFlow's state-dependent instructions and refined-workflow baseline, not a new general prompting principle [@wu2024stateflow, Sections 3.1 and 4.1]. Its purpose is to remove a concrete content-versus-organization ambiguity in this PHM study.

### Policy-class consequence

Assume the full public history needed by the base phase map is retained, with fixed initialization, and $z_t=f(\widetilde h_t)$ is deterministic. The equality

$$
\sigma(\widetilde H_t,Z_t)=\sigma(\widetilde H_t)
$$

holds because $Z_t$ is measurable with respect to $\widetilde H_t$, while projection recovers $\widetilde H_t$ from the pair. In particular, the annotation provides no additional random information about a hidden target conditional on that history. This is not a claim that a finite language model can compute the annotation without effort.

Let $\Pi$ contain all history-conditioned stochastic action rules in the same finite-horizon world, and let $\Pi_{\mathrm{ann}}$ contain all rules that can additionally read $f(\widetilde h)$. With the same feasible actions, environment, stopping and action-cost rules,

$$
\sup_{\pi\in\Pi_{\mathrm{ann}}}J(\pi)=\sup_{\pi\in\Pi}J(\pi),
\qquad
\sup_{\pi\in\Pi_{\Gamma}}J(\pi)\leq\sup_{\pi\in\Pi}J(\pi),
$$

where $\Pi_\Gamma$ restricts action support to the nonempty Graph sets.

**Proof.** Any annotated rule $\pi_t(a\mid \widetilde h,z)$ defines the history-only rule $\bar\pi_t(a\mid\widetilde h)=\pi_t(a\mid\widetilde h,f(\widetilde h))$. Their action kernels agree at every history, so the common environment gives the same rollout law by induction. Conversely, an annotated rule can ignore the annotation. These inclusions give equality of the optimal values. Masked rules form a subset of $\Pi$, giving the inequality. $\square$

This is ordinary policy-class inclusion, not an original policy-improvement theorem. It concerns an unrestricted decision rule under fixed world/action accounting, not equal computational cost of implementing different prompts. The frozen language model is not assumed closed under arbitrary deterministic preprocessing. Token usage, context truncation and response latency remain empirical measurements. Hidden-target access, external event information absent from the retained history, a learned estimator trained with additional knowledge, or truncated history would invalidate the stated measurability premise; the result cannot be extended to those cases by renaming them annotations.

### Estimand and falsification

For matched assigned assets/trials $\mathcal I$, retain the existing cohort statistic $\Theta$ and define $\theta^B_{uv}=\Theta(D^B_{uv}(\mathcal I))$. Apply simple effects, equal-weight marginal effects and interaction only within the new profile. In particular,

$$
\Delta^B_c(v)=\theta^B_{1v}-\theta^B_{0v},\qquad
\Delta^B_{cf}=\theta^B_{11}-\theta^B_{10}-\theta^B_{01}+\theta^B_{00}.
$$

Identical assigned assets and paired asset-block resampling are required; neighboring windows and repeated seeds are not independent equipment. AP/Macro-F1 are recomputed on pooled records, not averaged per episode. An original cue-package gain does not identify an annotation gain under $B$. Negative annotation or filtering effects remain admissible. This design does not separate annotation correctness from the added line's salience/token cost, and masks can reveal stage information even when annotation is off. Those are limits on interpretation, not reasons to relabel the old controls or create unobserved PHM regret.

Implementation uses the existing component factory and `configs/paper02_graph/organization.yaml` in Benchmark. The four condition names are `organization-reactive/state/filter/both`; original `factorial-*` and K conditions are preserved. Eight native tests check actual request construction, legacy prompt compatibility, contrast algebra and the real YAML plan. Input fixtures do not establish task effects.

## Lemma: equal reachable interfaces imply an inactive intervention

Assume two policies have the same initial world distribution. At every history reachable under either policy, they use the same model conditional response distribution, identical model-facing messages and schemas, and identical response-to-action decoding, stopping and resource rules. Then they induce the same action and rollout distributions.

**Proof.** Their first model-response laws agree because the initial interfaces agree. The common decoder gives the same action law. Applying the common environment kernel and resource update gives the same next-history law. Repeating this argument up to the bounded horizon or absorbing termination proves equality of the complete rollout laws. Identical strings alone would not suffice if decoding, termination or charging differed. $\square$

This is an elementary coupling argument, not a policy-improvement theorem. Equality on finitely many fixtures is not a proof over all reachable histories. A changed input is a useful activation witness but does not by itself imply a changed model action distribution or task outcome.

## Corollary: the event-free base memory and replanning ablations are inactive

Assume the current base profile, initial phase Inspect, no public events in the task or observations, and no change to the history supplied to the model. In the existing state function, the phase is determined by public read/catalog/operator/prediction progress or the latest error. Previous state and the replanning flag can affect phase selection only through Monitor/Revise, which are unreachable under these assumptions. The event token is never populated. Full, no-persistent-state and no-replanning therefore produce the same phase, cue and visible tools at every reachable history. Their historical metadata also agree by induction. The lemma yields equal rollout laws under the common decoder and environment.

A measured zero difference is consequently a null-manipulation check for this base profile, not evidence that persistent control or replanning is generally useless. Noise between independently sampled finite cohorts does not turn the inactive switch into an active mechanism test. The base memory configuration remains available as a negative control, not as the next efficacy experiment.

## Dynamic profiles and matched history

The prospective dynamic-history-matched cohort removes historical decision-state metadata in every dynamic arm, including full, no-memory and no-replanning. Previously only no-memory did so, mixing persistent-memory removal with a history-disclosure change. The correction changes future full-dynamic inputs; old dynamic-full runs are not equivalent controls and cannot be relabelled or pooled with this cohort.

A repeated valid operating-condition event provides an input-level witness. From an Analyze-compatible public history, the first event selects Monitor. On the next presentation of the same event, full consumes the token only once and selects Revise; no-memory sees the event anew and remains Monitor; no-replanning consumes the token but returns to Analyze. Monitor and Revise currently expose the same tool set, so this witness can distinguish cues while leaving visibility equal. It does not establish that the model replans, nor that this sequence is realized by the shared Runner. Those require actual released-event episodes.

Base inputs containing public events are rejected before event-cache mutation. Direct attempts to seed base with Monitor or Revise are also rejected. Dynamic fault-onset names and unreleased event indices remain invalid. Legacy transition tables remain unchanged for interpreting historical records; no task metric or data protocol is redefined.

## Connection to mask and selection losses

For the bounded finite-action model in theory04, the standard Bellman identity remains

$$
V_0^*-V_0^\pi=\mathbb E_\pi\sum_{t<T}
(\ell_t^{\mathrm{mask}}+\ell_t^{\mathrm{select}}).
$$

Changing a cue can change selection and future visitation; changing a mask can change both losses and future visitation. The four-cell task contrasts do not directly observe these latent terms. Transition validity, tool count and invalid calls therefore remain explanatory measurements, not numerical substitutes for regret. The interval bound, its support requirements and the retained counterexamples in theory04–06 are unchanged.

## Verification and falsification

The shared implementation owns `experiments/tests/test_graph_intervention_contract.py`. Native command:

```bash
python -m unittest discover -v -s experiments/tests \
  -p 'test_graph_intervention_contract.py'
```

The tests stop deliberately at the provider boundary without producing a model response. They inspect the four cells on six progress fixtures, unchanged base requests, rejection of event/profile misuse and equal dynamic history disclosure. They also retain the repeated-event witness and the eleven-call replay rule, including the fact that repeated operators can meet that count. These are input-contract checks, not PHM performance experiments. A native-import failure blocks integration acceptance; isolated source checks cannot replace it.
