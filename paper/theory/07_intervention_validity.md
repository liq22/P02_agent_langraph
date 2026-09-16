# Persistent structure, interface interventions and inactive ablations

## Object and scope

Freeze $G=\text{persistent decision structure}$ and keep the shared PHM world, model, knowledge source $K_0$, response decoder, resource accounting and evaluator fixed. The explicit controller is

$$
G=(\mathcal M,m_{\mathrm{init}},\delta,c,\Gamma),\qquad
m_t=(z_t,\nu_t),\qquad
m_t=\delta(m_{t-1},s_t,e_t),
$$

where $s_t=(h_t,b_t,t)$ is public history, remaining budget and time. The phase $z_t$ labels analysis progress, and $\nu_t$ is the last consumed public-event token. The cue $c(z_t)$ contains the current phase label and stage instruction; $\Gamma(z_t,s_t)$ returns tool visibility. Transitions are induced by $\delta$, rather than an independently changed topology. Public events $e_t$ are released condition metadata, not hidden targets or fault onsets inferred from the signal.

A definition containing only the phase label omits the event-deduplication memory used by the actual controller. Conversely, the model still receives public history: this implementation is not a memory-limited finite-state policy or a sufficient diagnostic belief state. Classical finite-state control and state-driven LLM workflows are precedents, not new formalisms here (Hansen, NIPS 1997, Section 3.1; StateFlow, Section 3.1).

## Four-cell intervention

For indicators $u,v\in\{0,1\}$, the model-facing interface is

$$
I_{uv}(h_t)=\left(\operatorname{render}(h_t;K_0)+u\,c(z_t),\ \mathcal T_v(z_t,h_t)\right),
$$

where $\mathcal T_0$ is the common tool catalog and $\mathcal T_1$ its Graph subset. The expression denotes structured message assembly, not arithmetic on strings. All four cells use the same renderer with top-level historical decision-state metadata removed from tool messages. Numerical tool payloads, action arguments, errors, order and remaining-budget information are otherwise unchanged at the same public history.

The cue factor is a label-plus-instruction package, not a pure state-name intervention. Tool identity can also convey the stage implicitly; removing the explicit cue does not remove all information about the state. Thus the estimands are direct effects of these implemented interfaces. They do not identify topology-only effects or separate latent semantic pathways. $K_0$ is the common knowledge source; state-conditioned presentation belongs to the declared $G$ intervention. A stronger claim independent of additional procedural wording needs the separately planned information-matched prompt control.

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
