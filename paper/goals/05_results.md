# Results, figures and merge

Scope: derive figures and claims from their actual CSVs; keep exact-model calculations separate from PHM cohorts. Output: Benchmark source CSV/figures and P02 result paragraphs. Acceptance: declared units/denominators, paired resampling, SVG/PDF/PNG exports, no expected empirical curves or Monte Carlo intervals on exact expectations.

From Benchmark:

```bash
# Existing real completed study only; not executed in this continuation:
bash experiments/graph_control/run.sh statistics "$RESULT_ROOT"
# Recompute the original exact example without overwriting historical results:
bash experiments/graph_control/run.sh toy --output local_outputs/toy_recheck
bash experiments/graph_control/run.sh plot \
  --csv local_outputs/toy_recheck/toy.csv --output local_outputs/toy_recheck/figures
# New counterexamples; the output root must not already exist:
bash experiments/graph_control/run.sh counterexamples \
  --output results/graph_control/boundaries_20260916
bash experiments/graph_control/run.sh plot --experiment expansion \
  --csv results/graph_control/boundaries_20260916/expansion.csv \
  --output results/graph_control/boundaries_20260916/figures/expansion
bash experiments/graph_control/run.sh plot --experiment support \
  --csv results/graph_control/boundaries_20260916/support.csv \
  --output results/graph_control/boundaries_20260916/figures/support
```

On a checkout containing the committed counterexample CSVs, inspect them rather than rerunning into the same root. For an independent recomputation, choose a new explicit output directory and compare parsed numerical rows. Do not delete the first results to make the command pass.

Actual continuation: 20 dependency-free analytical/contrast tests passed. The original 24-row calculation reproduces maximum identity residual $1.6653345369377348\times10^{-16}$. Nine new rows give covered expansion returns 0.8, 0.4, 0.5666667 and identical logging distributions with mask losses 0/0.45. Nine single-panel figures (27 SVG/PDF/PNG exports) were rendered locally and inspected; the CSVs and plotting source reproduce them. No PHM or LLM effect was estimated.

The figure design follows the requested Nature-figure reference's data-to-claim and editable-export principles. This is not a claim of Nature acceptance, full external-skill automated QA, or multi-panel alignment validation. Figures contain exact expectations and clear source captions.

Failure handling: stop on a mismatched CSV type, failed statistical pairing, undefined required metric or clipped figure; preserve the offending input. Do not select models or checkpoints using test plots. Historical mechanics/Mock counts and unrerun numerical references remain in source history, not as Graph effect estimates in the main Results.

Merge Benchmark before P02, into dev normally. Installed migration equivalence, one real shared PHM episode, numerical checkpoint/metric recomputation and document references must pass first. The current partial-source tests do not satisfy these gates. Keep both migration PRs Draft while they remain unmet. Do not update master, force-push or delete another branch.
