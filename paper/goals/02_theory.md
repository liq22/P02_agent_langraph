# Theory and exact decision experiment

Scope: test the value-coverage assumptions and control-loss identity, not PHM accuracy. Artifacts: Benchmark `toy.csv`, `config.json`, `counterexample.json`; P02 theory and Results. Acceptance: exact examples satisfy the identity to floating-point precision and preserve the invalid-coverage counterexample.

From Benchmark:

```bash
bash experiments/graph_control/run.sh theory
bash experiments/graph_control/run.sh toy --output results/graph_control/toy_20260916
bash experiments/graph_control/run.sh plot \
  --csv results/graph_control/toy_20260916/toy.csv \
  --output results/graph_control/toy_20260916/figures
```

Actually executed in the editing runtime: 9 tests passed; 24 rows; maximum identity residual 1.6653345369377348e-16. Keep the harmful mask (return0.5) and coverage-failure case (certificate0, loss0.85). Exact centered intervals explain oracle equality in this toy and are not an estimate available to the PHM Agent. Do not smooth, extrapolate or draw anticipated real-model effects. If a test fails, retain its inputs and fix the proposition or direct implementation, not the test tolerance to hide a conceptual error.
