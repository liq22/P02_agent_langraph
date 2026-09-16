# Closest primary work — continuation checked 16 September 2026

Author-facing reading notes; source claims and proposed experimental distinctions are separated. The existing bibliography is retained. No absence claim is inferred from an abstract.

| Work / reading location | Supported source content | Consequence for the Graph paper |
|---|---|---|
| StateFlow v5, Sections 3–4, especially 4.1 state ablations | Defines state/output/transition workflows, a refined ReAct control and removal of Observe/Error/Verify. Removing Observe still permits DESC in the Solve prompt. | State workflows and state-removal controls are prior art. Match prompt information and distinguish state cues from tool visibility. |
| PHMForge v3, 24 August 2026; Sections 2.3/3.4 and Appendix H | Algorithm-grounded PHM tools, provided/unknown-tool settings and verification/distractor/data-discovery ablations. Automated subset and manual frontier-model evaluations are separate. | Distracting-tool comparisons are already present. The added intervention fixes conditional tool count and terminal permissions while replacing Analyze/Check identities; it is not claimed to be the first distractor study. |
| Even-Dar, Mannor and Mansour, JMLR 2006, Sections 3–4 | Action-confidence bounds, elimination and stopping conditions in bandit/RL settings. | Coverage/exposure is a PHM-mask specialization, not a new general elimination principle. |
| Jiang and Li, ICML 2016; prior reading retained | Sequential off-policy evaluation and behavior/target action support. | Omitted continuation values are not established by recorded chosen actions alone. |
| Khan, Saveski and Ugander, ICML 2024; prior full-reading record and primary publication metadata | Sharp partial identification without overlap; boundedness and smoothness restrictions. | Retain the bounded one-step specialization with attribution; it is not a sample confidence interval or a new general theory. |

Primary locations:

- StateFlow: https://arxiv.org/html/2403.11322v5
- PHMForge: https://arxiv.org/html/2604.01532v3
- Action elimination: https://jmlr.org/papers/volume7/evendar06a/evendar06a.pdf
- Off-policy evaluation: https://proceedings.mlr.press/v48/jiang16.html
- Partial identification: https://proceedings.mlr.press/v235/khan24b.html

The new finite-set counting formulas are elementary identities and are presented as such. The falsifiable industrial question is whether the predeclared stage-specific tool identities improve matched PHM outcomes beyond their cardinality and terminal permissions. The exact 63-subset calculation motivates that comparison but does not answer it. PHMForge is a 2026 preprint; no peer-reviewed SOTA status or industrial superiority is inferred.
