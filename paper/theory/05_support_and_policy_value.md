# Coverage, selection and identification boundaries

This supplement uses the notation and finite-horizon assumptions of `04_value_coverage.md`. The examples concern terminal one-step actions; their values are therefore ordinary expected rewards rather than estimated multistep continuation values. They test two stronger interpretations of the coverage bound without changing the original PHM controller.

## 1. Preserving an optimal action is not policy improvement

For a nonempty visible set $M$, let $\pi_M$ be a selector supported on $M$ and define

$$
J(M)=\sum_{a\in M}\pi_M(a)Q(a),\qquad
m(M)=\max_{a\in\mathcal A}Q(a)-\max_{a\in M}Q(a),
$$
$$
e(M)=\max_{a\in M}Q(a)-J(M).
$$

**Proposition 3 (one-step improvement criterion).** For two nonempty masks evaluated at the same state and against the same action values,

$$
J(M')-J(M)=m(M)-m(M')-[e(M')-e(M)].
$$

Consequently, return does not decrease if and only if the increase in selection loss is no greater than the reduction in exclusion loss. Set inclusion $M\subseteq M'$ ensures $m(M')\le m(M)$, but imposes no corresponding constraint on $e(M')$.

**Proof.** For either mask, $J(M)=\max_aQ(a)-m(M)-e(M)$. Subtract the two equalities. Set inclusion increases or preserves the retained maximum. It does not determine the selector's probabilities. $\square$

For a multistep policy, the original telescoping identity still holds, but two policies generally visit different histories. The one-state criterion must not be substituted for a trajectory-level policy-improvement theorem without accounting for those distributions.

### A covered expansion with lower return

Consider actions $r,u,d$ with values $(0.8,0.9,0)$ and intervals $[0.8,0.8]$, $[0.9,0.9]$, $[0,1]$. All intervals contain their values. Starting at $M_0=\{r\}$, the existing largest-upper-endpoint rule exposes $d$ before $u$:

$$
M_0=\{r\},\quad M_1=\{r,d\},\quad M_2=\{r,d,u\}.
$$

Under the same uniform-choice rule on each mask, direct evaluation gives

| Mask | Coverage bound $C$ | Exclusion loss $m$ | Selection loss $e$ | Return $J$ |
|---|---:|---:|---:|---:|
| $M_0$ | 0.2 | 0.1 | 0 | 0.8 |
| $M_1$ | 0.1 | 0.1 | 0.4 | 0.4 |
| $M_2$ | 0 | 0 | $1/3$ | $17/30$ |

The monotone bound and termination claims hold. Policy improvement fails even with valid coverage. The example does not assert that an LLM samples uniformly; it refutes an unconditional improvement claim that would need to hold for every supported selector.

## 2. What masked logs identify

Overlap is a standard requirement in off-policy evaluation [@jiang2016]. Partial identification without overlap, including bounded-response bounds and additional smoothness assumptions, is established by Khan, Saveski and Ugander [@khan2024, Section 4]. The following specialization states the implication for a heuristic mask, not a new general partial-identification method.

**Proposition 4 (bounded one-step identified set).** Let $\mathcal A=\{r,u\}$, $M=\{r\}$ and rewards lie in $[0,1]$. A logging policy always selects $r$. Given its population logging law, let $v=\mathbb E[R\mid r]$. Without restrictions linking the two action outcomes, the sharp identified set of the mask loss is

$$
\mathcal I_{\mathrm{mask}}(v)=[0,1-v].
$$

**Proof.** Write $q=\mathbb E[R\mid u]$. Since $u$ has zero logging probability, changing its reward distribution leaves the complete logging law unchanged. Bounded reward implies $q\in[0,1]$ and the mask loss is $\max(0,q-v)$. Every number $x\in[0,1-v]$ is attained by choosing a Bernoulli omitted-action reward with mean $q=v+x$, while preserving the retained-action distribution. Thus both the endpoints and all intermediate values are feasible. $\square$

This is a population identification region. Finite observations also leave uncertainty about $v$; inserting a sample mean does not provide a confidence interval with a stated coverage probability. Extension to sequential action values requires assumptions or observations about continuations, not just observing a tool once.

### Two observationally equivalent worlds

Let the retained action have Bernoulli mean $0.5$ in both worlds. Set the omitted mean to $0.1$ in the first and $0.95$ in the second. Their mask losses are $0$ and $0.45$, while every length-$n$ logging distribution is identical. For $n=1,4,8$, exhaustive enumeration covers $2,16,256$ possible reward logs in each world. Probability mass sums to one and total variation between the paired distributions is zero. Additional repetitions of the same mask cannot resolve this ambiguity.

The implication for PHM is an experimental distinction: directly assigned cue/filter policies support comparisons of their task outcomes; the same outcome logs do not automatically identify unrestricted $Q^*$ or a mask-loss mediation effect. A future learned coverage estimator needs explicit development action coverage or justified structural restrictions, plus adaptive interval calibration and estimator cost. The present method does not add such an estimator.

## 3. Executable verification and falsification

Implementation remains in Benchmark. The original 24-row experiment is unchanged. The new calculations write three expansion rows and six logging-support rows to separate CSVs.

```bash
bash experiments/graph_control/run.sh theory
bash experiments/graph_control/run.sh counterexamples \
  --output results/graph_control/boundaries_20260916
```

Acceptance: all intervals cover in the expansion example; $C$ decreases to zero while final return is below initial return; each support distribution sums to one; paired total variation is zero despite different mask losses. The tests also preserve zero/negative paired contrasts and reject nonfinite interval endpoints or tolerance. A failed assertion invalidates the corresponding result paragraph; do not change the values or logging policy to recover a desired conclusion.
