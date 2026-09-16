# Closest original work — 16 September 2026

These notes record the primary passages relevant to the current claim. They are author-facing material, separate from the manuscript and bibliography.

| Original work / inspected passage | What the source actually studies | Consequence for this paper |
|---|---|---|
| StateFlow, COLM 2024; full v5 Sections 3–4, state ablation paragraph and Figure 4 | Context-dependent states, prompts and transitions; refined ReAct and removal of Observe/Error/Verify. Removing Observe still leaves table exploration in the Solve prompt. | State control and state-removal experiments are prior art. Reproduce the mechanisms and match prompt information; do not claim that the source lacks these controls. |
| PHMForge v3, 24 August 2026; Sections 2.3, 3.4 and Appendix H | PHM tool orchestration and retrieval; verification, distractor and data-discovery ablations. The paper distinguishes automated subset evaluation from manual frontier-model evaluation. | Treat it as a direct PHM precedent and a 2026 preprint, not a peer-reviewed SOTA win. The current controlled raw-window question must be compared explicitly. |
| Even-Dar, Mannor and Mansour, JMLR 2006; Sections 3–4 | Value-confidence comparisons, action elimination and stopping in bandit/RL problems. | The interval elimination principle is established. The present mask-bound application cannot claim a new general elimination theory. |
| Jiang and Li, ICML 2016; Sections 3.2–3.3 | Target/behavior action ratios, model-based extrapolation issues and independence requirements for off-policy evaluation. | A masked log is not evidence for every omitted action's continuation value. |
| Khan, Saveski and Ugander, ICML 2024; Sections 3–4, boundedness case and Theorem 4.1 | Sharp partial identification without overlap; bounded-response and Lipschitz restrictions distinguish population identification from estimation. | The one-step $[0,1-v]$ mask-loss region is a specialization of established reasoning, not a new general result or a sampled confidence interval. |

Primary sources:

- https://arxiv.org/html/2403.11322v5 ; acceptance: https://github.com/yiranwu0/StateFlow
- https://arxiv.org/html/2604.01532v3
- https://jmlr.org/papers/volume7/evendar06a/evendar06a.pdf
- https://proceedings.mlr.press/v48/jiang16.pdf
- https://proceedings.mlr.press/v235/khan24b.html ; full text: https://faculty.washington.edu/msaveski/assets/publications/2024_ope_lipschitz/paper.pdf

The live PHMForge reference was corrected from the previous unversioned/v2 note to v3. The StateFlow venue was corrected to COLM, and internal “checked” notes were removed from bibliographic entries. No literature omission is inferred merely from an abstract or search snippet. Novelty still requires real PHM component effects and their failure boundaries; exact counterexamples alone do not establish industrial superiority.
