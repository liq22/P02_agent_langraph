# Results, figures and merge

Scope: recompute retained real metrics and draw only real CSV; separately retain exact-model results. Output: Benchmark figure/source data and P02 result interpretation. Acceptance: matching cohort/denominators, explicit undefined metrics, actual units, editable SVG/PDF and PNG, no expected curves.

```bash
# Real completed study, using existing shared aggregation and plotting:
bash experiments/graph_control/run.sh statistics "$RESULT_ROOT"
# Exact-model figures use only their own CSV:
bash experiments/graph_control/run.sh plot --csv "$TOY_ROOT/toy.csv" --output "$TOY_ROOT/figures"
```

Check figures at their final physical size; exact DP means there is no Monte Carlo confidence interval to draw. Real sampling uncertainty uses the chosen independent unit. Fit parameters/checkpoints must not be selected from test plots. Record which artifact supports each result paragraph.

The original manuscript's old 214-test, finalizer/topology and source-path sections were removed from scientific prose in this revision; original Git content and SOURCE_HISTORY retain the audit history. They do not prove the pending migration is validated. Do not delete the scientific references or raw historical results to make the new prose look complete.

Merge order is Benchmark implementation then P02 paper-only cleanup. Merge into dev normally only after actual shared-method/runtime integration, real PHM entry and document references pass. Current leaf/theory success is insufficient for merging either entire migration. If data or API blocks the gate, leave both Draft and report the exact commit and unmet gate. No master update, force push or deletion of another branch.
