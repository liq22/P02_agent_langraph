# G-T1 — When filtering helps, and when it removes useful actions

## Status and assumptions

This exact conditional-probability calculation is a design lemma, not a guarantee for tool-filtered LLM prompts. At one public history, let $q$ be a baseline action distribution, $U$ the set of useful actions and $A$ the visible/allowed action set. Assume $0<p=q(U)<1$ and $q(A)>0$. Define useful-action retention $g=q(A\mid U)$ and non-useful-action retention $b=q(A\mid U^c)$.

## Proposition

If filtering acts as exact renormalization $q_A(a)=q(a\mid A)$, then

$$
q_A(U)=\frac{pg}{pg+(1-p)b},
$$

and

$$
q_A(U)-p=\frac{p(1-p)(g-b)}{pg+(1-p)b}.
$$

Proof: the intersection has mass $q(U\cap A)=pg$; the total retained mass is $pg+(1-p)b$. Divide and subtract $p$. Hence improvement occurs exactly when $g>b$. A small action set is not sufficient: filtering that disproportionately removes useful actions worsens the policy.

For example, $p=0.2,g=0.9,b=0.1$ gives $q_A(U)=9/13>0.2$. Reversing the retention rates gives $q_A(U)=1/37<0.2$. The direction depends on relevance, not cardinality alone.

## Relation to a real LLM

Changing tool schemas can change the distribution rather than merely renormalize it. If the actual filtered policy $\widetilde q_A$ satisfies

$$
\operatorname{TV}(\widetilde q_A,q_A)\leq\varepsilon,
$$

then $|\widetilde q_A(U)-q_A(U)|\leq\varepsilon$ by the definition of total variation. A guaranteed positive one-step gain requires the calculated gain to exceed $\varepsilon$, which is not known for the current Agent. Do not assert this assumption as measured fact.

## What the experiment must distinguish

The present graph policy adds a state prompt and filters schemas. Run the four new component arms with the same treatment of historical state labels:

```
factorial-reactive: no visible state cue, no filtering
factorial-state:    state cue, all tools
factorial-filter:   no visible state cue, state-specific tools
factorial-both:     state cue, state-specific tools
```

Internal state computation remains available to select the mask. These arms identify the two policy-output mechanisms, not the existence of internal graph computation or topology alone. The original `graph` condition is retained separately and is not silently rewritten into this factorial profile.

## Empirical observations

Report schema visibility, successful calls, completion and primary PHM performance. A handcrafted useful-action label is not automatically ground truth; use a declared local action-compatibility criterion or controlled simulation and disclose it. Main evaluation accepts multiple valid trajectories. For the real benchmark, the factorial effect and action-loss cases are more defensible than an assumed universal reduction in search complexity.
