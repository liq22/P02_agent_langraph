# PHMGraph paper

The sole active manuscript is [draft/main.md](draft/main.md). [paper.yaml](paper.yaml) records the current title, bibliography, first-attempt diagnosis contrasts and exact implementation binding. The active bibliography [refs/phmgraph_review_2026.bib](refs/phmgraph_review_2026.bib) contains 38 cited works; the [literature map](refs/phmgraph_literature_review.md) records their contribution and reading depth.

Chapter 2 defines prior foundations, task, variables, gap and objective. Chapter 3 specifies indexing, gating, actual public-history precedence and Algorithm 1. [FORMULATION_METHOD_MAP.md](FORMULATION_METHOD_MAP.md) connects symbols, two figures, algorithm steps, implementation and experiments. [EXPERIMENT_MATRIX.md](experiments/EXPERIMENT_MATRIX.md) retains the scientific protocol: diagnosis Macro-F1 is primary; replay AP is secondary; actual paired effects remain unestimated.

## Reproducible method and figures

The inspected method is `liq22/phm-agent-benchmark@8206cfef540d5f602adba482e9dcc0ebd6b0f437`. Its configuration is `configs/paper02_graph/indexing_first_attempt.yaml`, and its operational goal is `paper/goals/P02_MATCHED_CONTROL.md`. This is an explicit source binding, not acceptance of migration PR #20 or of real-data execution. Do not substitute a changing branch head without checking the method and protocol together.

The two publication SVGs are in `assets/figures/`. Their only drawing source is Benchmark `scripts/figures/plot_phmgraph_formulation_method.py`. From a Benchmark checkout containing that source:

```bash
python scripts/figures/plot_phmgraph_formulation_method.py --output-dir /path/to/P02_agent_langraph/paper/assets/figures
```

SVG export uses the Python standard library with `--svg-only`; PDF/PNG additionally use CairoSVG. No agent runtime, data or provider connection is required. The previous motivation source/asset remains historical; the current manuscript displays the problem and method figures instead.

For a PDF proof, first generate those PDFs. From `paper/draft/`, convert image references to their same-source PDF exports for LaTeX:

```bash
sed 's/\.svg)/.pdf)/g' main.md | pandoc --from=markdown --citeproc --pdf-engine=xelatex -V documentclass=article -V fontsize=10pt -V geometry:margin=20mm -o PHMGraph.pdf
```

## Historical compatibility

The old manifest is preserved exactly at [legacy/graph_v6_manifest.yaml](legacy/graph_v6_manifest.yaml). Its experiments and old result files retain their original definitions, not the current factorial interpretation. Six legacy result-marker pairs are restored in the manuscript; a renderer must remain bound to its own legacy protocol. Schema-version-2 `paper.yaml` must not be silently used as a legacy execution configuration.

Use `dev` for paper integration. Runtime, experiments, evaluation and all drawing code are owned by Benchmark. Older Goal/Research documents and historical protocols do not override the active manuscript, experiment matrix or pinned method binding.
