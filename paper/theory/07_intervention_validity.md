# Indexing, workflow gates and task-supported opportunities

This supplement specializes existing policy-value reasoning to the implemented base controller. It does not assert a new general state-machine theorem. Algorithmic execution, artifacts and tests remain in Benchmark.

## 1. Fixed catalog and public history

Let $B=((b_j,d_j))_{j=1}^6$ be the common B01–B06 catalog. Each arm receives all six unchanged instructions in the same order. Indexing adds only the active block ID; gating changes tool schemas and the accepted action-name set. The four conditions remain catalog-global, indexed-global, catalog-masked and indexed-masked.

The rendered public history retains task scope, ordered action arguments/results/errors and resource information, removing historical top-level stage labels identically. In the event-free base, the phase map uses successful read/catalog/schema/prediction history and the last error; replay also uses released sample identifiers and successful operator counts. It neither reads private labels nor computes a fault posterior. Under fixed initialization and full history, equal rendered histories imply equal phases. Event-dependent memory, truncation or additional private inputs require a different argument.

## 2. Deterministic annotation and action support

For $Z_t=f(\widetilde H_t)$, measurability and projection give

$$\sigma(\widetilde H_t,Z_t)=\sigma(\widetilde H_t).$$

Any annotated policy $\pi(a\mid\widetilde h,z)$ induces the history-only kernel $\bar\pi(a\mid\widetilde h)=\pi(a\mid\widetilde h,f(\widetilde h))$. With common environment, decoding and stopping, induction gives identical rollout laws. Conversely the annotation may be ignored. Thus unrestricted optimal task utility is unchanged; restricting action support can only reduce its supremum. These are ordinary policy-class facts, not guarantees for a fixed finite language model.

The objective is $J_{\mathrm{task}}=\mathbb E[R_{\mathrm{task}}]$, not priced interface cost. Added tokens, computation, latency or context truncation can change $J_\lambda=J_{\mathrm{task}}-\lambda C$. Rejected off-menu calls remain recorded empirical outcomes; the mask/select identity in theory04 assumes supported actions and cannot simply absorb these errors as zero regret.

The six base menus are distinct when the declared catalog is present, so the menu abstractly identifies the base phase. It need not be decoded correctly by the model. Monitor, Revise and Recover share a dynamic menu. The index effect in a masked condition is therefore incremental presentation, not the introduction of all phase information.

## 3. The raw-observation opportunity is a singleton in diagnosis

The current diagnosis task permits one sample handle and one exact window/channel specification. Repeated reads return the same fixed raw array $X$ under different artifact references. Alternate windows, channels and handles are not admissible. This premise is checked through the native data scope and runtime, not inferred from the Graph diagram.

Consequently $|\mathcal O_{\mathrm{raw,legal}}^D|=1$. For a repeated raw array $X_2=X_1$, its conditional law given $X_1$ is a point mass, so

$$I(Y;X_2\mid X_1)=0.$$

This does not imply that all deterministic processing of $X$ is useless to a computationally limited model, or that rereading has no artifact-handling or cost effect. It rules out interpreting the diagnosis comparison as loss of a second distinct raw observation. The earlier multi-observation acquisition explanation is withdrawn; the data protocol is not expanded to preserve it.

## 4. Conditional trace restrictions

**Single acquisition.** In an event-free, non-replay, error-free supported base trajectory from Inspect, there is at most one successful read. After the first read, that fact remains in history and prevents return to Inspect. Without a call error, Recover is unavailable; the remaining base menus omit reading. This proves the trace property but not a diagnosis loss, by Section 3.

**Post-prediction closure.** In that same domain, a successful prediction on a reachable masked trajectory selects Submit, whose only exposed action is submission. Before successful termination, an error-free supported continuation cannot reopen analysis. A submission error can activate Recover and is an explicit exception. Replay's progression to a new sample is outside the claim.

Accordingly, Check denotes prediction readiness/execution, not a post-prediction verification stage. The controller neither estimates evidence sufficiency nor proves that further analysis is valueless. An observable constraint becomes an empirical mechanism only after distinguishing available actions, actual use and changes in the final diagnosis or numerical support.

Base no-memory and no-replanning remain inactive under the event-free assumptions: their relevant branches are unreachable and full history is unchanged. Equality of model interfaces plus common conditional response, decoding and environment laws implies equality of rollout distributions by induction. Null effects under those assumptions cannot refute memory or replanning generally.

## 5. First-attempt endpoint and descriptive mechanism quantities

Use the native three-class diagnosis Macro-F1, including all assigned canonical first outcomes. Missing accepted submissions become `no_submission`, yielding a false negative for the evaluator-side true class without adding a fourth averaged diagnosis class. Provider failure can change this operational endpoint even when label quality conditional on submission is unchanged. For a binary correct-submission indicator only, $\Pr(S=1)=(1-p)q$ separates interruption probability $p$ and conditional success $q$; it is not a decomposition of Macro-F1.

The two primary contrasts are $\theta^D_{10}-\theta^D_{00}$ and $\theta^D_{11}-\theta^D_{10}$. The current native intervals are paired diagnosis-class-stratified bearing resamples. All repeats/windows of one bearing stay together. Nominal 97.5% intervals allocate error across two prespecified estimates; they are not exact finite-sample coverage and do not include uncertainty in deployment class proportions or provider distribution shifts.

For descriptive mechanism analysis define $P_j=1$ when a first attempt has a successful numerical prediction. Among $P_j=1$, record $A_j^{\mathrm{post}}$ for a non-submit analytical action after the first prediction, and $R_j^{\mathrm{label}}$ for a final accepted label different from that prediction. Report the latter among attempts with both prediction and accepted submission, never code missing final labels as unchanged. Supporting-artifact changes are reported separately, resolving numerical outputs/source/model provenance; a new reference string alone is not new evidence. Attempts to submit before a successful prediction and submission-error recovery use all first attempts as denominator. These are treatment-dependent descriptive subsets, not causal mediators or new primary metrics.

Existing canonical rollouts provide the event source. Actual rates and any derived diagnostic CSV are not reported until eligible real outcomes exist. No fabricated process curve or new correctness proxy is introduced here.

## 6. Position balance and interrupted execution

The existing asset/trial first-attempt schedule has a prospective cyclic-order option. Within each seed/rotation/task/horizon/budget stratum, randomly permute the four conditions and use every cyclic shift once for each complete group of four bearings. For a residual group use distinct shifts. If $N=4q+r$, each condition occupies each position $q$ times plus at most one extra occurrence. Hence

$$\max_k n_{c,k}-\min_k n_{c,k}\leq1.$$

This is first-order position balance, not carryover balance or temporal stationarity. The actual counts and sequence are frozen before outcomes. Long interruptions and provider-model changes remain visible; no unfavorable block is deleted to restore balance. Interruption-free subsets are descriptive sensitivity analyses only.

The existing request reserve sums the actual unattempted assignments' turn limits before starting a block. A cap of 420 pertains to the current one-diagnosis/one-three-window-replay smoke configuration, not an arbitrary cohort. It is not redefined as a treatment budget or automatically increased.

A request intent is flushed to the existing provider log before transmission. Resume refuses an unresolved request context lacking complete canonical first outcomes, or a disagreement between canonical bundles and selected records. It runs before fitting or another request. Confirmatory frozen-plan comparison may first resolve the data assignment, without fitting or inference. Indeterminate cases block completion; they are neither silently retried nor filled as failed diagnoses. A persisted intent can precede an unsent request, and loss of both log and bundle is not detectable by this rule. Thus this is conservative refusal under preserved local evidence, not exactly-once remote execution.

## 7. Executable mapping

Benchmark retains `execution_plan.py`, `schedule=asset_trial_first_attempt_v1` and `outcome_selection=first_attempt`. The optional `block_order=cyclic_balanced_v1` is used by the new output identity in `configs/paper02_graph/indexing_first_attempt.yaml`. Older independent-order studies keep their definitions. No `blocking.py`, second planner, new Runner, evaluator or PHMskills intervention is added.

Native tests are `test_first_attempt_blocks.py`, `test_graph_trace_gating.py` and `test_first_attempt_safety.py`. The last verifies balance, legacy order, saved assignment identity, canonical failure retention, orphan-request refusal and a hard process exit. These are runtime/source checks, not real PHM effects. Execution commands and data/API boundaries are maintained only in Benchmark's existing P02 Goal.
