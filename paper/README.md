# PHMGraph paper

The sole active manuscript is [draft/main.md](draft/main.md). [paper.yaml](paper.yaml) records the decision–evidence study and exact source binding. The bibliography is [refs/phmgraph_review_2026.bib](refs/phmgraph_review_2026.bib); the older [literature map](refs/phmgraph_literature_review.md) retains its original scope. New provenance references and reading depth are documented in [FORMULATION_METHOD_MAP.md](FORMULATION_METHOD_MAP.md).

Chapter 2 defines foundations, task, variables, gap and estimands. Chapter 3 specifies the outer decision interface, inner typed numerical-evidence graph, online coupling and Algorithm 1. The [experiment matrix](experiments/EXPERIMENT_MATRIX.md) separates software mechanics from real PHM measurement. Operational Macro-F1 remains primary; grounded diagnosis, support-path replay and cost are distinct outcomes. Real dual-v1 effects are unestimated.

## Implementation and figures

The active method is `liq22/phm-agent-benchmark@45704762bd2e3ee7f8d0da4c037e67a575779703`, merged through PR #27. Its plan-only smoke entry is `configs/paper02_graph/dual_v1.yaml`; the operational continuation is `paper/goals/P02_DUAL_GRAPH.md`. The policy and native fixture checks are implemented. Real-waveform acceptance, shared canonical first-attempt cohort integration and grounded cohort scoring remain separate gates. This binding does not accept migration PR #20.

The two publication SVGs are in `assets/figures/`. Their only drawing source is Benchmark `scripts/figures/plot_phmgraph_formulation_method.py`. From a Benchmark checkout containing that source:

```bash
python scripts/figures/plot_phmgraph_formulation_method.py --output-dir /path/to/P02_agent_langraph/paper/assets/figures
```

SVG export uses only the Python standard library with `--svg-only`; PDF/PNG additionally use CairoSVG. No agent runtime, data or provider connection is required. Figure 1 defines the comparison; Figure 2 now shows both graphs and their two-way coupling. The earlier motivation source/asset remains historical.

For a PDF proof, first generate the PDFs. From `paper/draft/`, convert the same-source figure references for LaTeX:

```bash
sed 's/\.svg)/.pdf)/g' main.md | pandoc --from=markdown --citeproc --pdf-engine=xelatex -V documentclass=article -V fontsize=10pt -V geometry:margin=20mm -o PHMGraph.pdf
```

## Historical compatibility and validation

The preceding pointer/gate specification is preserved exactly at [legacy/indexing_v1_manifest.yaml](legacy/indexing_v1_manifest.yaml) and [legacy/indexing_v1_experiment_matrix.md](legacy/indexing_v1_experiment_matrix.md). [legacy/graph_v6_manifest.yaml](legacy/graph_v6_manifest.yaml) remains unchanged. Six legacy result-marker pairs retain their original profile meanings; never populate them with dual-v1 outcomes. Schema-version-3 `paper.yaml` is a scientific manifest, not a legacy renderer or execution configuration.

Final source head `35785d4`: focused installed workflow `35354189769` passes 36 tests. Broader workflow `35354189755` runs 208 tests, with 202 passing and six errors in the unchanged analysis-applicability input-token fixture. Neither that broader failure nor pending real-data evidence is hidden by this paper integration. Details and exact mapping are in `FORMULATION_METHOD_MAP.md` and Benchmark PR #27.

Use `dev` for paper integration. Runtime, experiments, evaluation and all drawing code remain in Benchmark. Older Goal/Research documents do not override this manuscript, experiment matrix or source binding.
