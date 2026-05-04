# Negative Result Note

This P1_01 node records the data/provenance and result-source boundary for PHMGA evidence. It must not claim positive main experimental results until the selected backend is locked and the Stage C/D rows pass with ledger and artifact traces.

Current negative or limitation statements to preserve:

- PHMGA Stage B now has partial backend evidence: Ottawa OpenRouter Nemotron and Ottawa BigModel rows accepted, while RM101 OpenRouter Nemotron and RM101 BigModel rows remain complete reject-evidence bundles.
- `selected_global_best_backend` remains pending, so Stage B evidence must not be promoted into Stage C/D main-result or ablation claims.
- PHMGA main-result and selected-backend-dependent table claims remain blocked.
- Vibench is a read-only data interface and must not provide formal paper result truth.
- Pending, failed, no-evidence, transport-failure, or planner-timeout rows cannot enter paper tables.
- Full sample-level metadata-H5 alignment should still be rechecked by the Vibench/PHMGA adapter during preflight.
- Independent external review is still required before closing the node.
