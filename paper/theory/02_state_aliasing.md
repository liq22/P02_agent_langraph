# G-T2 — State sufficiency, history aliasing and horizon

## Scientific object

Let $H_t$ be public history, $Z_t=f(H_t)$ the graph state, $B_t$ remaining budget, and $a_t$ the next action. A compact state is useful only if it retains distinctions needed for future actions. The current GraphDecisionAgent also retains its public history; the state-only counterexample below motivates ablations and must not be misrepresented as a theorem about that implementation.

## Proposition 1: aliasing can make a state-only policy worse

Consider two equally likely histories $h_0,h_1$ mapped to the same $z$. There are two actions $a_0,a_1$, with utility one exactly when $a_i$ follows $h_i$, and zero otherwise. A policy observing only $z$ chooses $a_0$ with probability $p$ and has expected utility

$$
\tfrac12p+\tfrac12(1-p)=\tfrac12.
$$

A history-aware policy chooses the matching action and attains one. Thus persistent state alone does not guarantee useful memory. Adding more nodes also offers no guarantee unless they separate decision-relevant histories.

## Proposition 2: sufficient state permits an optimal state policy

For a finite-horizon task, assume the conditional distribution of immediate utility, next state, and next budget, given $H_t$ and $a_t$, depends only on $(Z_t,B_t,a_t,t)$, and feasible actions are a function of $(Z_t,B_t,t)$. Then backward induction gives an optimal policy depending only on $(Z_t,B_t,t)$.

At the final step, maximize expected terminal utility given that tuple. If the optimal future value is $V_{t+1}(z,b)$, the assumed sufficiency makes

$$
V_t(z,b)=\max_{a\in\mathcal A(z,b,t)}
\mathbb E[u_t+V_{t+1}(Z_{t+1},B_{t+1})\mid z,b,a]
$$

well defined independently of the original history. Induction proves the claim. An LLM's manually selected graph states have not been shown to satisfy this assumption; it is a condition to investigate, not an established property.

## Horizon-dependent trade-off

Suppose two policies can be coupled so that, while their histories agree, their next-action distributions differ by at most $\epsilon_t$ in total variation. The probability that the full histories ever diverge is at most $\sum_{t<T}\epsilon_t$ by a union bound. For terminal utility in $[0,1]$, their utility difference is at most $\min(1,\sum_t\epsilon_t)$. This bound explains why small local changes may accumulate over a long horizon; it does not say whether graph control improves or worsens utility.

A valid horizon study must specify the resource regime. The supplied script scales replay call/read budgets with horizon, so it tests length at roughly fixed per-window capacity. It does not isolate horizon under a fixed total budget. A fixed-total-budget experiment is a different registered condition.

## Base versus dynamic profile

The current base graph only reaches six states. Monitor/Revise require the separately registered public-condition profile. Its released operating-condition event is public metadata, not a fault label inferred from vibration. Do not infer event-F1, detection delay or autonomous contradiction detection from that profile. The new one-key entry does not yet dispatch the downstream dynamic event runner.

## Experiment exit

`graph-components` tests cue/filter mechanisms; `graph-memory` tests the existing no-memory profile; `horizon` tests length under proportional budgets. State reachability and transition counts explain task outcomes but cannot substitute for them. A null task gain with lower cost may support an efficiency claim; better reasoning remains too broad.

### Horizon interpretation

The current evenly spaced sample selector changes selected windows when the requested count changes. Therefore 2/3/5-window runs measure length, sample-selection and proportional-resource sensitivity together, not an isolated causal horizon effect. A nested-prefix horizon study requires a separately fixed longest sequence and prefix binding; it is not implemented by the current run_rotation interface. Report the selected sample IDs and do not claim horizon-only causality.
