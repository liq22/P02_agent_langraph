# Source-bounded related-work review — 2026-09-16

The closest sources were checked beyond their abstracts. This is a focused comparison, not a systematic review or proof that no earlier interval certificate exists. Old bibliography files remain for historical citations; the revised main uses `refs/graph_tii_mssp.bib`.

| Source and accessed text | Positive documented content | Our actual distinction / unresolved issue |
|---|---|---|
| StateFlow arXiv2403.11322v5, Sec3.1, Sec4.1, appendix A.1 | State representations from context, output functions, rule/LLM transitions; refined ReAct prompt and No_Observe/No_Error/No_Verify controls | Do not claim it lacks state/ablation study. Study feasible-action value coverage and independently exposed cue/filter mechanisms in the same PHM world. No foreign score is used. |
| PHMForge arXiv2604.01532, served HTML says v2 8May2026; Sec2.1--2.2, Sec3.4, Appendix H | Algorithm-grounded PHM tools and scenario verification; explicit domain-tool, distractor and discovery experiments | Do not claim first PHM tools/trajectory evaluation. Our fixed-window same-world policy intervention is narrower. Site metadata and older abstract snapshots can differ; do not mix counts from versions. |
| Huang/Ontanon arXiv2006.14171v3, pp1--3 | Masks invalid game actions; differentiable masked policy and valid policy-gradient argument; compares penalty/mask variants | A workflow mask can exclude feasible valuable analyses. Our conditional bound is about value loss, not a new policy-gradient estimator. |
| Even-Dar/Mannor/Mansour, JMLR2006, Sec3 and Sec4.1 finite-horizon analysis | Upper/lower value confidence bounds, successive action elimination and stopping rules | Direct theoretical precedent. Our certificate is a diagnostic specialization for a heuristic PHM mask, not a new general elimination principle or sample-complexity result. |
| TRPO, ICML2015; regularized MDPs, ICML2019 | Existing sequential value analysis | Bellman telescoping is acknowledged prior mathematics. The new diagnostic's general priority remains unestablished. |
| Coscientist, Nature2023; ChemCrow, NMI2024 | External scientific tools integrated with language decisions | Motivation only; not evidence for mechanical diagnosis performance. |
| ReAct ICLR2023; Reflexion NeurIPS2023 | Interactive histories and feedback/memory | Generic is not memoryless. Faithful reproduction must preserve prompts, feedback boundaries and counted calls. |
| Statistical Precipice NeurIPS2021; Demsar JMLR2006 | Evaluation uncertainty and across-dataset comparisons | Choose asset clusters and paired cells for this task; five data domains are not automatically five i.i.d. replicates. |
| MOMENT ICML2024 | Time-series foundation model | Numerical control; pretrained exposure and train/test fitting must be checked before comparison. |

The eleven distinct Introduction sources include eight from Nature/NMI/JMLR/ICLR/ICML/NeurIPS. Keep the three nearest non-main-track references rather than inflate venue prestige with unrelated citations. Venue status is not used to suppress an inconvenient precedent.

## Journal emphasis

TII: industrial decision integration, bounded latency/cost and reproducible task-level effects. Official IES describes the journal as bridging informatics theory and industrial application (https://iten.ieee-ies.org/announcement/2026/call-for-nominations-for-co-editor-in-chief-positions-for-tie-tii-ojies/).

MSSP: a convincing mechanical signal-analysis decision and its measured effect must accompany the Agent study. This is an editorial positioning judgment, not a verified journal requirement. The official ScienceDirect aims/author pages returned access errors in this session; no current word/page limit, impact factor or acceptance claim was inferred from third-party journal clones. Verify the actual journal submission page when choosing the final venue. Do not submit the same manuscript simultaneously.

## Figure reference

Read `Yuan1z0825/nature-skills/skills/nature-figure/SKILL.md` and its Python fragment. Adopt editable SVG/PDF text, restrained single-question layout, physical sizing and explicit data provenance. Toy plots contain computed CSV values with an exact-model label, not predicted PHM curves. The repository's full automated collision/alignment suite was not installed; only direct render and PDF text inspection is claimed here.
