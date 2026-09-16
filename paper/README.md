# Graph paper sources

`draft/main.md` is the sole full manuscript. The September-16 revision contains the TII/MSSP-oriented argument and the actual finite-model Results. It removes the former standalone runtime/finalizer instructions from scientific prose. Historical experiments remain indexed in `../experiment_spec/SOURCE_HISTORY.md`; they are not new Graph treatment estimates.

Start at [goals/README.md](goals/README.md), then read [the value-coverage theory](theory/04_value_coverage.md), [the literature matrix](literature_matrix.md), [the experimental contract](experiments/EXPERIMENT_MATRIX.md) and [data admission SOP](experiments/DATA_DOWNLOAD_SOP.md). The root GOAL remains the scientific authority. Source and config mappings remain in `../experiment_spec/MAPPING.md`.

All executable code, CSV results and generated figures belong to Benchmark. The new slice is `experiments/graph_control/`; the same PR also contains a separately developed P01 numerical slice under `experiments/p19/`. Do not duplicate either implementation here. The nine-test finite-model verification is complete; full migration integration and a real PHM episode are not. Continue from the first uncompleted gate in `goals/EXECUTION_20260916.md`, not from the retired local-runner migration instructions.
