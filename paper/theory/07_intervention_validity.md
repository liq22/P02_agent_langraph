# Instruction indexing, menu exposure and reachable behavior

## Scope and notation

The primary prospective comparison uses one fixed ordered catalog $B=((b_j,d_j))_{j=1}^6$. IDs B01–B06 correspond to the existing Inspect, Hypothesize, Analyze, Check, Recover and Submit instructions. All four arms receive every instruction once; only the active-block pointer and schema exposure vary. Semantic `organization-*` and earlier `factorial-*` treatments retain their definitions and are not controls for this new profile.

Let $\widetilde h_t$ contain the public task, usage and ordered action-argument/result/error history after common removal of top-level historical decision-state metadata. In the event-free base, the stage function reads only: whether a successful read/catalog/model-schema/prediction exists, the latest call error, and, for replay, public replay sample IDs and source IDs/counts of successful operators. It does not read the removed state labels, private diagnosis targets, interface token counts or a learned fault posterior.

The required history-sufficiency premise is

$$\widetilde h_t=\widetilde h'_t\Longrightarrow z_t=z'_t.$$

For this base source, each used field is retained and previous state can only activate event-dependent Monitor/Revise branches. Those branches are unreachable from Inspect without events. The consumed-event cache remains empty. This supplies a source argument for sufficiency under fixed initialization and flags; finitely many fixtures alone would not prove it. The premise is not extended to dynamic event caches, truncated histories, private metadata or an alternative controller without a new argument.

The prospective interface is

$$
I^B_{im}(\widetilde h_t)=\big(\rho(\widetilde h_t,B)\mathbin\Vert iL(z_t),\operatorname{Schema}(\Gamma_m(z_t))\big).
$$

Indexing adds the text `Active instruction block: B03.` in the relevant case. B03 is an index into the common bank, not the word Analyze or another imperative stage name. Equal-width characters do not prove equal tokenization, and ordered identifiers may still carry positional cues. The treatment does not independently identify pointer correctness versus line salience.

## Task-value equivalence, not cost equivalence

Assume complete retained history, $Z_t=f(\widetilde H_t)$, a fixed finite-horizon world, and identical feasible actions and task-relevant stopping rules. Then

$$\sigma(\widetilde H_t,Z_t)=\sigma(\widetilde H_t).$$

For all history-conditioned stochastic policies $\Pi$ and policies $\Pi_{\rm ann}$ that also receive $f(\widetilde h)$,

$$\sup_{\pi\in\Pi_{\rm ann}}J_{\rm task}(\pi)=\sup_{\pi\in\Pi}J_{\rm task}(\pi).$$

**Proof.** Compose any annotated rule with $f$: $\bar\pi_t(a\mid\widetilde h)=\pi_t(a\mid\widetilde h,f(\widetilde h))$. Action kernels and hence rollout laws agree by induction through the same environmental kernel. Conversely, an annotated rule may ignore its index. $\square$

This is standard deterministic-feature/policy-class reasoning, not an original control-optimality theorem. $J_{\rm task}=\mathbb E[R_{\rm task}]$ excludes interface computation/serialization cost. The empirical cost vector records input tokens, output tokens, elapsed time and tool usage in their own units. A priced scalar cost may be introduced only with its conversion stated. For example, identical task reward 1 but an additional interface charge $c>0$ changes $J_\lambda=J_{\rm task}-\lambda C$ by $-\lambda c$. Thus the task-only equivalence does not imply cost-adjusted equivalence. Token-budget truncation that changes feasible continuations also invalidates the common-world premise.

A fixed language model is not assumed closed under arbitrary policy composition. The empirical index effect can be nonzero even when the annotation adds no evidence to complete history.

## Oracle action support versus implemented menu exposure

For supported policies $\Pi_\Gamma\subseteq\Pi$, ordinary inclusion gives

$$\sup_{\pi\in\Pi_\Gamma}J_{\rm task}(\pi)\leq\sup_{\pi\in\Pi}J_{\rm task}(\pi).$$

This oracle-level comparison does not model all changes induced by deleting tool schemas. Actual schema exposure changes the model input and implicit stage cues as well as its allowed-name list. The measured contrast is the total effect of that defined interface. The mask/select identity in theory04 assumes supported actions; rejected off-menu calls must remain failures in the empirical denominator, not be evaluated as if they were valid within-set selections.

The six base menus are pairwise distinct provided the global catalog contains the declared tool names. Therefore there is an inverse $g$ on these six menus with $z=g(\Gamma(z))$. An index in the masked arm adds no new abstract phase information conditional on that menu, although its explicit presentation may still alter a finite model's behavior. Dynamic Monitor, Revise and Recover share a menu; this collision does not occur among the six base menus. No inference about the model's ability to decode a menu follows from injectivity alone.

## Implementation-specific single-acquisition invariant

**Claim.** In event-free, non-replay base episodes starting at Inspect, any supported trajectory without tool-call errors contains at most one successful `data.read_window`.

**Proof.** Before a successful read, the base phase map returns Inspect. After the first successful read, that success remains in full history, so the map cannot again return Inspect. On a trajectory without call errors, it cannot return Recover; event-free execution excludes Monitor and Revise. Its remaining phases are Hypothesize, Analyze, Check and Submit. None of their declared menus contains `data.read_window`. Hence no second successful read is exposed along such a trajectory. $\square$

This conditional invariant follows from the actual source, not from an assumed diagram. It does not claim global impossibility: a call error activates Recover, whose menu allows another read. A valid but uninformative first read does not itself activate that recovery edge. The globally allowed read budget can therefore exceed error-free acquisition opportunities under the mask. Whether that harms diagnosis requires a task where additional evidence matters. No observed task loss is assigned to this restriction without such data. The result excludes replay, where a completed prediction can move to the next sample's Inspect stage.

## Static instruction/menu compatibility

The current instructions use capability-level wording and contain no literal tool-function references. The bank's common header asks for the block relevant to current progress; it does not instruct simultaneous execution of all blocks.

| Block / internal phase | Instruction capability | Available implementation capability | Boundary |
|---|---|---|---|
| B01 / Inspect | Bounded signal context | Read/describe/summarize | Only error-free acquisition phase in non-replay |
| B02 / Hypothesize | Choose analysis family | Operator/model catalogs | No actual fault posterior is constructed |
| B03 / Analyze | Typed feature artifacts | Operator schema and execution | Further reads absent |
| B04 / Check | Numerical prediction/checking | Model schema and prediction | Further reads absent; name does not certify sufficiency |
| B05 / Recover | Correct an observed error | Data/operator/model actions | Additional acquisition requires an error trigger |
| B06 / Submit | Submit result with references | Submission | No numerical result is manufactured by the controller |

This table rules out an explicit absent-function-name reference in the active instruction; it is not semantic proof that the whole catalog is harmless or that each stage transition is diagnostically justified. The full directory can itself impose an attention burden shared by all four arms.

## Estimands and interpretation

For the existing cohort statistic $\Theta$ and fixed matched assignment $\mathcal I$, define $\theta^B_{im}=\Theta(D^B_{im}(\mathcal I))$. Primary contrasts are

$$\theta^B_{10}-\theta^B_{00},\qquad\theta^B_{11}-\theta^B_{10}.$$

They estimate indexing under global tools and menu exposure after indexing. The other simple effects, joint effect and interaction are secondary; they are not pure topology or regret mediation. AP/Macro-F1 are recomputed from pooled records in identically drawn asset-block resamples. The number of task families, bearings and stochastic repeats are distinct. Post-treatment transition strata are descriptive, not causal subgroup estimates.

The original system comparison is secondary; older semantic-cue designs are diagnostic context. No cross-profile subtraction or relabelling is valid. Base memory/replanning remain inactive under the existing event-free assumptions; dynamic-history-matched experiments retain their distinct event and rendering contracts. Persistent-memory and pure-horizon efficacy are not established by indexing.

## Verification

Benchmark owns `experiments/tests/test_graph_indexing.py`, the existing component factory, `configs/paper02_graph/indexing.yaml` and its six within-profile contrasts. The tests capture actual requests, check six menu classes and the reacquisition boundary, and exercise the real plan entry. `menus.csv` reports static source-derived rules, not PHM performance. The earlier exact value/support/cardinality results remain in theory04–06 and are not rerun by this slice.
