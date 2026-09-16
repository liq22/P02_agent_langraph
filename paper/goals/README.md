# Graph paper: TII / MSSP continuation

Scope: one Graph paper, P02 scientific source and Benchmark executable source. Start from current PR #4 and Benchmark PR #20; both were Draft during the 2026-09-16 audit. Do not merge the paper-only deletions before centralized methods pass real integration. Work toward dev; no master changes, force push or branch deletion.

Read the revised `paper/draft/main.md`, `paper/theory/04_value_coverage.md`, and the experiment/data documents. Existing manuscript result counts remain historical. The new complete slice is exact finite-model analysis: code and tests in Benchmark, 24 computed CSV rows, and the corresponding Results section. The interval diagnostic is not installed as a calibrated PHM policy.

| Goal | Artifact and acceptance | Actual command location |
|---|---|---|
| Sync | Confirm branch ancestry, method imports and factory state; preserve local edits | `01_sync.md` |
| Theory/toy | Propositions, counterexample, exact CSV and deterministic regression | `02_theory.md` |
| Data/PHM | Real data read, labels/split, checkpoint and score recomputation | `03_data_and_gpu.md` |
| Model experiments | Matched Generic/Graph and cue/filter effects; no substitute data | `04_experiments.md` |
| Statistics/figures | CSV-derived SVG/PDF/PNG and claim mapping | `05_results.md` |

Every goal ends with the actual command, output path, numerical observation and supported claim recorded in the existing execution log. A blocked dataset binding is not an executed experiment. Negative results complete a scientific test; they do not justify changing the evaluator or test set. Do not restart historical migrations or generate another unchanged reviewer pack.

The generic request's `experiments/p19` and `external/phmfactory` names do not match this repository. Keep executable slices at Benchmark `experiments/graph_control`, shared runtime at `src/phm_agent_benchmark`, and the existing single factory submodule at `src/phm_data_factory`. P02 has no executable submodule. Reference-model/single-representation/fusion comparisons are a secondary numerical axis, not silently substituted for the Graph intervention.
