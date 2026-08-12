# Repository Guidelines

`CORE.md` is the highest authority for Paper 2. The scientific product is a matched comparison between ordinary sequential/reactive policy and `GraphDecisionAgent` under `phm-agent-benchmark`.

Active paths:

```text
src/graph_phm_paper/
scripts/run_graph_experiment.py
tests/test_graph_adapter.py
```

Required invariants:

- The graph chooses among benchmark canonical actions; it does not own data, operators, submissions, budgets, or scoring.
- Hold provider model, tools, experts, data, split, sample order, seeds, temperature, and budgets fixed for B3-versus-B5.
- Record decision state on every Agent turn and retain failures, replans, and terminal loops.
- Graph-specific metrics are secondary to the shared seven-axis evaluator.
- Do not import the full repository scheduler, Canvas, dashboard, Web app, Tauri, or graph database into the PHM Agent method.
- Do not add checksum, digest, receipt, ledger, or generic `evidence_policy` gates.
- Do not expand the active paper to RUL.

Historical research-node and submission workflow artifacts cannot override `CORE.md` or the matched experiment protocol.
