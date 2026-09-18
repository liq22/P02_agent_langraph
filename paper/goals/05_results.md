# Results, figures and merge

Scope: map computed CSVs to manuscript claims, keeping exact models separate from PHM cohorts. Products: Benchmark source rows, SVG/PDF/PNG and corresponding P02 prose. Acceptance: declared units/denominators, consistent estimands, no fabricated empirical curves or confidence intervals on exact expectations.

## New executed figure

The complete six-action experiment gives 63 detailed masks and six cardinality summaries. Its figure asks whether count alone determines selector value: best, uniform-subset mean and worst subset returns are shown together. All six summary rows are used; no convenient cardinality or subset is dropped.

From Benchmark, with a new explicit output root:

```bash
bash experiments/graph_control/run.sh cardinality --output local_outputs/cardinality-recheck
bash experiments/graph_control/run.sh plot --experiment cardinality \
  --csv local_outputs/cardinality-recheck/summary.csv \
  --output local_outputs/cardinality-recheck/figures
```

The committed results are at `results/graph_control/cardinality_20260916/`. Do not rerun into that existing directory or delete it to make the command pass. Inspect it, or recompute into a new directory and compare parsed rows. The plot has one panel; no multi-panel alignment claim applies. Text is retained in SVG/PDF. The reference Nature-figure principles used are a single scientific question, actual source data, explicit exact-model semantics and editable export; the complete external audit-script suite was not run.

## Real cohort analysis

```bash
# Only after a genuine completed matched cohort exists:
bash experiments/graph_control/run.sh statistics "$RESULT_ROOT"
```

The cardinality effect is the difference of registered cohort statistics after pooling matched assignments. Do not replace it with an average of per-seed F1/AP. All-attempt cost remains distinct from outcome-conditioned cost. Undefined statistics, provider failures, stops and budget exhaustion are retained under the existing contract. Do not use test plots to choose models, checkpoints or the primary metric.

The previous finite-horizon and support/expansion examples remain in Results as historical calculations; this continuation did not rerun their tests or reinterpret them as PHM effects. The new 63 masks are one exhaustive finite model, not 63 independent datasets or Agent trials.

## Failure handling and merge

Stop on a mismatched CSV type, wrong count, failed pairing, undefined required statistic or clipped export; preserve the input and failure. Native integration failed at import in this environment, so neither this figure nor the 17 new source tests satisfies the real-entry gate.

Keep Benchmark PR #20 and P02 PR #4 Draft until installed migration checks, one real matched PHM episode, numerical checkpoint reload/metric reproduction and document consistency pass. Then merge Benchmark normally into dev before P02. No master update, force push, Factory downgrade or deletion of another branch.
