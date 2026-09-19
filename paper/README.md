# PHMGraph paper

The active manuscript is [draft/main.md](draft/main.md): **PHMGraph: Contract-Grounded Decision Control for Tool-Using Fault Diagnosis**. [paper.yaml](paper.yaml) binds it to the sole implementation. The existing [30-paper literature matrix](refs/phmgraph_literature_review.md) and [32-entry active bibliography](refs/phmgraph_review_2026.bib) are unchanged; PROV-DM is an additional standard and MAP-Graph remains abstract-only.

Chapter 2 defines the problem, prior foundations, variables and estimands. Chapter 3 gives exact evidence-to-phase/menu maps and the continuation-matched outer rule. The original 11−10 package comparison is retained alongside 10⁺−10 and 11−10⁺. The latter is a remaining feedback bundle, not pure readiness or causal mediation. [FORMULATION_METHOD_MAP.md](FORMULATION_METHOD_MAP.md) connects each equation and figure to its code, test and experiment. Replay now explicitly distinguishes valid support from complete numerical observations and from reproduced values.

## Implementation and figures

Active Benchmark source: `eceada18ebe18ef1e3b8210830b326cc4343c6b7`, normally merged PR #35. Core dual control remains PR #27; open10 was introduced in PR #30 and exact control maps in PR #32. The latest change preflights replay observations and prevents incomplete records from being declared reproduced; it does not change online policies or diagnostic scoring. The plan-only entry is `configs/paper02_graph/dual_v1.yaml`; continuation is `paper/goals/P02_DUAL_GRAPH.md`. The model placeholder is not an approved provider route.

The sole drawing source is Benchmark `scripts/figures/plot_phmgraph_formulation_method.py`. From that checkout:

```bash
python scripts/figures/plot_phmgraph_formulation_method.py --output-dir /path/to/P02_agent_langraph/paper/assets/figures
```

`--svg-only` uses the standard library; PDF/PNG also use CairoSVG. Figure 1 remains the motivation/problem illustration. Figure 2 labels the evidence/control predicates and independent 10/10⁺/11 comparison arms, not additional execution stages. All major objects and text remain editable in SVG. Both figure assets and their source are unchanged by the replay correction.

After generating the PDFs, from `paper/draft/`:

```bash
sed 's/\.svg)/.pdf)/g' main.md | pandoc --from=markdown --citeproc --pdf-engine=xelatex -V documentclass=article -V fontsize=10pt -V geometry:margin=20mm -o PHMGraph.pdf
```

## Validation and historical compatibility

Tested Benchmark head `fd17dad2e896e89600ee14069eb22d404265ce4e`: focused installed workflow `35427170354` passes 51 tests; broad workflow `35427170356` passes 262 research and 52 selected portable core tests. One pre-existing real-HDF5 acceptance test remains unrun. The two suites overlap. The six former applicability-fixture errors remain fixed; no production accounting or native validator was weakened.

Real waveform/split/fitted-asset acceptance, the shared canonical first-attempt path, grounded cohort scoring and real diagnostic effects remain pending. Native fixture tests and a manuscript build do not satisfy these gates. Migration PR #20 remains separate. The [experiment matrix](experiments/EXPERIMENT_MATRIX.md) specifies the same-cohort continuation comparisons, replay-observation requirements and remaining execution requirements.

The preceding indexing manifest/matrix under `legacy/`, `legacy/graph_v6_manifest.yaml` and six original result-marker pairs are unchanged. New dual-v1 results must not be written into those historical slots. The scientific manifest is not a legacy renderer or execution configuration. Runtime, numerical computation, evaluation and plotting source remain only in Benchmark; use `dev` for paper integration.
