# PHMGraph paper

The active manuscript is [draft/main.md](draft/main.md): **PHMGraph: Contract-Grounded Decision Control for Tool-Using Fault Diagnosis**. [paper.yaml](paper.yaml) binds the manuscript to its implementation. The [literature matrix](refs/phmgraph_literature_review.md) records methods and experimental evidence from 30 original papers, all used in the manuscript. PROV-DM and the abstract-only MAP-Graph entry are separate from that count. The [bibliography](refs/phmgraph_review_2026.bib) contains only cited entries.

The question is the incremental value of anticipatory numerical readiness when the native tools already validate their inputs. AiiDA, LLMCompiler and TimeSage-MT rule out treating dual graphs or dependency scheduling alone as novelty. Chapter 2 defines the problem; Chapter 3 defines deterministic readiness, control and isolated support replay. [FORMULATION_METHOD_MAP.md](FORMULATION_METHOD_MAP.md) links the challenges, symbols, figures and experiments. The [experiment matrix](experiments/EXPERIMENT_MATRIX.md) keeps real diagnostic effects distinct from software checks.

## Implementation and figures

The active source is `liq22/phm-agent-benchmark@467a16570c55da086f2d67fe79365c7bf006d9ac`. The numerical mechanism remains the one introduced in PR #27; PR #29 corrects a test fixture and updates its publication drawing source and continuation instructions. Runtime and numerical contracts are unchanged. `configs/paper02_graph/dual_v1.yaml` remains plan-only, with an intentional model placeholder. The next executable work is in Benchmark `paper/goals/P02_DUAL_GRAPH.md`.

Only Benchmark maintains drawing code. Generate the two publication figures from its checkout:

```bash
python scripts/figures/plot_phmgraph_formulation_method.py --output-dir /path/to/P02_agent_langraph/paper/assets/figures
```

`--svg-only` requires only the standard library; PDF/PNG export additionally requires CairoSVG. Figure 1 is the introductory motivation and problem-setting figure, using the existing filename. Figure 2 specifies the control loop and labels the same symbols as Algorithm 1. Both SVGs preserve editable text and separate objects; their PDF exports use embedded vector fonts, not a flattened image. No third overview figure is added.

After generating the PDFs, build the manuscript from `paper/draft/`:

```bash
sed 's/\.svg)/.pdf)/g' main.md | pandoc --from=markdown --citeproc --pdf-engine=xelatex -V documentclass=article -V fontsize=10pt -V geometry:margin=20mm -o PHMGraph.pdf
```

## Validation and historical compatibility

PR #29 source `c040d2a` passed installed workflow `35362929546`: 208 research tests and 52 selected portable core tests. The workflow's pre-existing real-HDF5 acceptance test remains deselected and must run with its actual data. The six earlier applicability errors were fixed by declaring known-zero token usage and the intended native contract in the no-Agent fixture; production accounting and the original assertions were preserved. Final-head evidence is recorded in PR #29.

Real-waveform acceptance, canonical first-attempt cohort integration and grounded cohort scoring remain pending; no real dual-v1 diagnostic effect or live-model result is claimed. Migration PR #20 is separate.

The [indexing manifest](legacy/indexing_v1_manifest.yaml), [indexing experiment matrix](legacy/indexing_v1_experiment_matrix.md), older `legacy/graph_v6_manifest.yaml` and six historical result-marker pairs retain their original meanings. Do not populate those slots with dual-v1 results. `paper.yaml` is a scientific manifest, not a runtime configuration. Use `dev` for paper integration; all runtime, experiment, evaluation and drawing implementations remain in Benchmark.
