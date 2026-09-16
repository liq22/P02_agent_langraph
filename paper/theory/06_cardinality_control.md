# Cardinality-preserving control of tool identity

The objects in this supplement extend the mask/selection notation of theory04 and theory05. The counting formulas are elementary finite-set identities, not a new general action-elimination theory. Their role is to expose a competing explanation for the existing Graph intervention and define the smallest matched control.

## 1. Mathematical question

At a fixed one-step public state, let $\mathcal A=\{1,\ldots,n\}$ have bounded action values $q_1,\ldots,q_n$. Let $S_k$ be uniform over all size-$k$ subsets, $1\leq k\leq n$, and let the selector be uniform within its visible set. Define

$$
J(S_k)=\frac1k\sum_{a\in S_k}q_a,\quad
m(S_k)=q_{\max}-\max_{a\in S_k}q_a,\quad
e(S_k)=\max_{a\in S_k}q_a-J(S_k).
$$

**Lemma 1 (count matching does not determine selector return).**

$$
\mathbb E[J(S_k)]=\frac1n\sum_{a=1}^nq_a.
$$

If the maximum is unique, its inclusion probability is $k/n$. For the ordered values $q_{(1)}\leq\cdots\leq q_{(n)}$,

$$
\mathbb E\max_{a\in S_k}q_a
=\sum_{j=k}^n q_{(j)}\frac{\binom{j-1}{k-1}}{\binom nk}.
$$

**Proof.** Every action belongs to $\binom{n-1}{k-1}$ of the $\binom nk$ subsets, so its inclusion probability is $k/n$. Linearity of expectation proves the first identity and gives the optimum-inclusion probability. Fix a deterministic ordering of tied values. A subset whose largest rank is $j$ contains that ranked action and $k-1$ of the preceding $j-1$ actions. There are $\binom{j-1}{k-1}$ such subsets. Summing their maximum values proves the last identity. Ties do not invalidate that formula, although the probability of retaining at least one maximizer is not generally $k/n$ when maximizers are nonunique. $\square$

Since $m(S_k)+e(S_k)=q_{\max}-J(S_k)$, increasing $k$ can reduce exclusion loss while increasing selection loss without changing average return. No assumption that an LLM samples uniformly is made: the result refutes an implication that tool count alone determines task value.

## 2. Forced visibility and conditional matching

Let $F$ contain $f$ actions whose visibility is fixed, and $B$ contain $n$ other admissible catalog members. Sample $S_k$ uniformly from $B$ and keep $F\cup S_k$, with $f+k>0$. For a uniform selector,

$$
\mathbb E J(F\cup S_k)
=\frac{\sum_{a\in F}q_a+(k/n)\sum_{a\in B}q_a}{f+k}.
$$

The proof is the same inclusion-probability calculation. The mean need not be constant in $k$ when $f>0$. For $n=0$, only the fixed nonempty set is available and no randomization occurs. This distinguishes the unconstrained counting example from an operational mask that preserves submit/stop permissions.

For a public history $h$, let $M(h)$ be the original mask, $T$ the set of terminal names, $F(h)=M(h)\cap T$, $B(h)=\mathcal A(h)\setminus T$ and $k(h)=|M(h)\setminus T|$. The operational control is the conditional mask map

$$
\widetilde M_s(h)=
\begin{cases}
F(h)\cup S_s(B(h),k(h)), & z(h)\in\{\mathrm{Analyze},\mathrm{Check}\},\\
M(h), & \text{otherwise},
\end{cases}
$$

where $S_s$ is the declared seeded sampling rule on the sorted nonterminal catalog. Cardinality still depends on workflow state; only identity selection at fixed catalog/cardinality is state-agnostic. The exact counting lemma concerns uniform subsets, not a guarantee that a finite pseudorandom seed schedule spans them uniformly.

The implemented research condition randomizes only Analyze and Check. It preserves the original membership of terminal tools, the number of nonterminal visible names, shared schema contents and catalog order. All other states are unchanged. A local pseudorandom generator uses the declared run seed and sorted catalog; revisits do not redraw, and coincident masks remain valid controls. Equal catalogs and cardinalities produce the same identity set regardless of the state label. The finite three-seed development schedule is not exhaustive uniform integration over all masks.

Matching is conditional on the same public history and catalog. The two policies can induce different visited histories, prompt-token totals and costs. Equal tool count is not equal information content or equal token count. Tool-name schemas also represent parameter families, not necessarily fully specified feasible actions; the exact action-value formulas cannot be applied to the live interface by assigning a value to one arbitrary parameter setting.

## 3. Estimand and falsification

The named pair is `factorial-filter` versus `factorial-cardinality`, both cue-free with the same history sanitation. For the frozen assignment set $\mathcal I$ and registered cohort statistic $\Theta$, the shared scorer estimates

$$
\widehat\Delta_{\mathrm{rel}}^{\mathrm{pool}}
=\Theta(D_{\mathrm{filter}}(\mathcal I))
-\Theta(D_{\mathrm{cardinality}}(\mathcal I)).
$$

The same assets/trials and paired asset-block resampling are required. AP and Macro-F1 are recomputed after pooling, not averaged per episode or per seed. The contrast is a direct policy comparison. It does not identify unrestricted $Q^*$, mask-loss mediation or a population expectation over every possible random mask. A nonpositive result retains the competing explanation that the chosen stage-specific tool identities do not improve outcomes under the declared protocol. Failed, partial and zero-effect outcomes remain in the assigned population.

The independent relevance manipulation is the scientific addition. StateFlow already has state/prompt ablations, PHMForge already has distracting-tool controls, and confidence-based action elimination is established [@wu2024stateflow; @li2026phmforge; @evendar2006]. Industrial benefit requires the matched PHM comparison rather than this finite example.

## 4. Exact experiment and implementation

For values $(0,1/5,2/5,3/5,4/5,1)$, enumerate all $2^6-1=63$ nonempty subsets. There are 20 size-three subsets. At that cardinality the best and worst uniform-selector returns are 0.8 and 0.2, while the uniform-subset mean is 0.5. Mean exclusion and selection losses are 0.15 and 0.35; optimum-inclusion probability is 0.5. Exact rational computation gives zero decomposition and counting residuals before export to CSV.

Executable locations are in Benchmark: `src/phm_graph_agent/cardinality_control.py`, the existing component factory, `configs/paper02_graph/mask_relevance.yaml`, and `experiments/graph_control/cardinality.py`. The calculation writes 63 detailed rows and six cardinality summaries. The figure reads those summaries, with no sampled confidence interval or generated PHM curve.

```bash
bash experiments/graph_control/run.sh cardinality --output local_outputs/cardinality-recheck
bash experiments/graph_control/run.sh plot --experiment cardinality \
  --csv local_outputs/cardinality-recheck/summary.csv \
  --output local_outputs/cardinality-recheck/figures
```

Choose a new output directory: the calculation refuses to overwrite existing results. Acceptance: all 63 masks occur once; both exact identities hold; the size-three returns/losses agree with the values above; source tests preserve count, terminal permissions, state scope and deterministic revisits. A failed check invalidates the corresponding calculation, not the test population. Native component integration and real PHM effects are separate, still-uncompleted gates.
