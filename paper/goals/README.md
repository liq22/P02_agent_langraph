# Graph paper: next executable slice

P02 owns manuscript, theory and experiment/claim mappings. Benchmark owns every method, data consumer, runtime, result and figure. Continue P02 PR #4 and Benchmark PR #20; merge Benchmark first, then P02 only after installed and real-data gates pass. Do not recreate a P02 Python package or a second Factory submodule.

The scientific question remains when state cues and tool visibility improve PHM decisions and when they remove useful actions. Read `paper/draft/main.md` and theory04–06. The new cardinality control tests whether stage-specific tool identities matter beyond how many tools are exposed. The existing Graph and four component conditions remain distinct from this additional intervention.

| Goal | Scope and product | Acceptance / commands |
|---|---|---|
| Sync | Remote ancestry, full installed methods, Factory decision | `01_sync.md`; no pointer update before accepted-descendant and real-data checks |
| Theory | Coverage, selection, support and count/identity separation | `02_theory.md` and `paper/theory/06_cardinality_control.md`; exact identities and retained counterexamples |
| Data / GPU | Actual records, labels/splits, checkpoint and metric reproduction | `03_data_and_gpu.md`; eight RTX4090 devices for GPU work, never a two-card substitute |
| Experiments | Graph/Generic, cue/filter, cardinality control, active persistence | `04_experiments.md`; matched cohorts with explicit failures |
| Results / merge | CSV figures, cohort effects, paper interpretation | `05_results.md`; no merge on source-only tests |

## Completed in this continuation

Benchmark adds a seed-frozen, Analyze/Check-only cardinality control through the existing component factory. Seventeen new dependency-free tests pass. Complete enumeration produces 63 subset rows and six summaries: at three visible actions, best/mean/worst returns are 0.8/0.5/0.2. The new figure is derived from the summary CSV. These are exact finite-model quantities, not PHM or LLM measurements. Main Sections 4.4, 5, 6.3 and 7.3 contain the corresponding argument, method, estimand and result.

Actual commands and limitations are in Benchmark `results/graph_control/cardinality_20260916/README.md`. The native integration test invocation failed at import because the editing environment lacks the full Phase1 installation; its three test functions did not run. Do not count the earlier 20 tests again or call this full migration validation.

## Next gate and failure handling

Run the native integration and existing migration tests in the full Benchmark checkout, then one real development episode using inspected data/provider settings. Stop at the first failed import, protocol, pairing or data check and retain its output. Five external Graph bindings, faithful SOTA reproduction, active dynamic/memory and nested-prefix horizon remain unfinished; this is not a GPU-only handoff.

Factory main was still five commits behind the existing pin at this inspection. No downgrade, core change or parent pointer update is warranted. Preserve all historical results. Graph code stays at Benchmark `experiments/graph_control` and the single Factory remains `src/phm_data_factory`; generic path names in a reused request do not relocate these components.
