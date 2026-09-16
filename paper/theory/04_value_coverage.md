# Value coverage for graph-guided action visibility

Status: analytical extension and exact finite-model validation, 2026-09-16. The original PHM graph policy is unchanged. All executable work is in Benchmark `experiments/graph_control/`.

## 1. Existing theory and the narrower gap

StateFlow already defines state-based workflows and tests state removals; invalid-action masking already has policy-gradient analysis. Bellman telescoping is standard (Schulman et al., 2015; Geist et al., 2019). Our candidate contribution is not the graph formalism or the regret identity. It is **value coverage of a heuristic PHM tool mask**, and a conditional diagnostic for deciding which omitted action warrants exposure. Confidence-based action elimination is also established: Even-Dar, Mannor and Mansour (JMLR 2006, Sections 3 and 4) use upper/lower value bounds for elimination and stopping. The interval diagnostic and exposure rule below are a PHM-mask specialization, not a new general principle of action elimination. Their usefulness still requires a PHM estimator and controlled empirical findings.

Feasibility and helpfulness differ. The Benchmark forbids truly invalid actions through its fixed contract. A graph may additionally hide feasible analyses because a workflow state regards them as unnecessary. Such an action can have high continuation value. A decrease in malformed calls therefore does not prove better diagnosis.

## 2. Notation and assumptions

A finite episode has public history h_t, remaining budget b_t and time t. Set s_t=(h_t,b_t,t), so no Markov property of an arbitrarily compressed graph state is assumed. The globally feasible set A(s) is finite and nonempty before absorption. G provides a nonempty subset M(s). Environment transitions and terminal loss are the same in every arm. Early stop and resource exhaustion enter an absorbing state. V*_t and Q*_t denote unrestricted optimal continuation values for a **single declared bounded utility**; they are not numerical classifier probabilities or LLM confidence scores.

Private evaluation labels never enter the Agent. A future interval estimator must use only training/development information and public histories. Population generalization and simultaneous interval coverage are different requirements. The finite set must contain fully specified candidate actions, or a value interval for each tool must bound the best continuation across its full permitted parameter family. Covering one hand-picked parameter value does not cover a tool schema. This parameter-family calibration is not implemented in the current Agent.

## 3. Standard control-loss decomposition

Define

$$\ell^{mask}_t(s)=V_t^*(s)-\max_{a\in M(s)}Q_t^*(s,a),$$
$$\ell^{select}_t(s,a)=\max_{u\in M(s)}Q_t^*(s,u)-Q_t^*(s,a).$$

For any policy supported on M,

$$V_0^*(s_0)-V_0^\pi(s_0)=E_\pi\sum_{t<T}(\ell^{mask}_t+\ell^{select}_t).$$

**Proof.** The summands add to V*_t(s_t)-Q*_t(s_t,a_t). Substitute Q*=E[u_t+V*_{t+1}|s_t,a_t]; expectation and summation cancel consecutive values. V*_T=0 gives the identity. This is an existing Bellman argument applied to this intervention, not a new policy-improvement theorem. Losses are weighted by the policy's own visited states; between-policy subtraction is not automatically a causal mediation decomposition.

## 4. Interval-valued coverage diagnostic

Suppose intervals [L_t(s,a),U_t(s,a)] cover Q*_t(s,a) simultaneously over the feasible actions under consideration. Define

$$C_t(M;s)=\max\{0,\max_{a\notin M}U_t(s,a)-\max_{m\in M}L_t(s,m)\},$$

with C=0 when no action is excluded.

**Proposition 1.** On that coverage event, 0 <= ell_mask <= C.

**Proof.** If an unrestricted maximizer lies in M, the loss is zero. Otherwise the best excluded value is at most max_outside U, and the best retained value is at least max_inside L. Subtract and take the nonnegative part. No independence between actions is needed. Coverage is the assumption; validity of a per-action point prediction alone is insufficient.

**Proposition 2.** Repeatedly expose the excluded action with largest upper value until C <= delta. For delta >= 0 this process terminates after at most |A\M| additions, and its certificates are nonincreasing.

**Proof.** Each addition removes one candidate from the outside maximum and may increase the retained lower maximum. Hence C cannot increase. The full set has C=0. This is a termination and value-coverage statement, not minimum-cardinality optimality.

This procedure is an explicitly named research intervention. It must not be installed as an invisible automatic repair in the existing Benchmark executor. A production policy needs a validated interval estimator, its overhead charged, and an independently named experimental condition. The current delivery implements the diagnostic and its finite-model experiment only.

**Sequential corollary.** On simultaneous coverage along a realized path, mask regret is bounded by the sum of C_t. If with probability at least 1-alpha a frozen estimator covers every visited (history, action) in a bounded episode, the bound holds on that event. Marginal 95% intervals are not automatically simultaneous under adaptive history selection. A union bound is available only if the constituent conditional error probabilities are actually justified. No such empirical coverage claim has been established for the present PHM Agent.

## 5. Falsification and failure cases

A deliberately uncovered example has Q(time)=0.10 and Q(envelope)=0.95, but claimed intervals time=[0.7,0.8], envelope=[0.1,0.2]. Keeping time yields C=0 while true mask loss is 0.85. The supplied counterexample.json records this calculation. A certificate with unvalidated intervals can be meaningless.

A coarse state can map two equally likely histories to the same label while the optimal action differs. A state-only policy then obtains at most 1/2 in a two-action example, versus 1 for a history-aware policy. The current LLM retains full public history, so this is a caution about state-conditioned masks, not a theorem that its actual return is 1/2.

Two ablation policies with identical conditional actions at all reachable histories induce identical rollout distributions by induction. Before paying for a no-memory cohort, check that the switch alters the tested intervention. The original base profile does not reach Monitor/Revise without public events; an inert switch cannot identify memory utility.

## 6. Empirical and population quantities

Let bounded loss L in [0,1] be declared before test. Population risk is R_D(pi)=E_{e~D,xi}L(e,pi,xi); empirical risk is its average over held-out assets and repeated trials. Condition on fitted models and a frozen policy. If n asset blocks are independent draws from D, then their within-asset average loss differences lie in [-1,1]. Hoeffding gives

$$P(|\widehat\Delta-\Delta|>\epsilon)\leq2\exp(-n\epsilon^2/2).$$

This is an illustrative finite-sample bound for additive loss, not a bound on AP/Macro-F1 or deployment under a shifted D. Cohort AP/Macro-F1 are recomputed inside paired asset-block resamples. Seeds do not increase the number of independent assets. Training risk and toy exact return are never relabelled population test risk.

## 7. Actual numerical verification

Two observed contexts, three abstract routes, horizons 2/4/8 and eight fixed policies produced 24 exact dynamic-programming rows. Maximum decomposition residual: 1.6653345369377348e-16. At horizon 4, best fixed route return is 0.6000, static uniform policy 0.55833, aligned two-route mask 0.7625, harmful singleton 0.5000, interval-expanded uniform 0.7125, and unrestricted oracle/covered greedy 0.9250. The known toy values center the intervals. The last equality is an intentionally transparent finite-model result, not evidence of an estimated PHM controller matching an oracle.

All even horizons have the same normalized return by construction. This is a retained null length effect, not a claimed long-horizon benefit. The original 'fixed_time' and 'harmful_time_mask' coincide behaviorally; their duplicate labels document the reference/control interpretation and are not independent algorithms.

Reproduce from Benchmark: `bash experiments/graph_control/run.sh theory` then `bash experiments/graph_control/run.sh toy --output results/graph_control/toy_20260916`. Source data and plots remain in Benchmark; P02 stores their scientific interpretation.
