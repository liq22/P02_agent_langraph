# Graph paper: TII / MSSP continuation

P02 owns scientific formulation and manuscript; `liq22/phm-agent-benchmark` owns all implementations, data consumers, experiments, scoring and plotting. Continue the existing P02 PR #4 and Benchmark PR #20. Both remain Draft until real integration passes; merge Benchmark before the paper-only cleanup. Do not create another Runner or move executable work into P02.

The current scientific question is when state cues and heuristic tool visibility improve PHM decisions, and when masking or selection instead causes harm. Read `paper/draft/main.md`, `paper/theory/04_value_coverage.md` and `paper/theory/05_support_and_policy_value.md`. The original interval bound is conditional, its expansion rule is not a policy-improvement guarantee, and unsupported masked logs cannot identify omitted action values.

| Goal | Scope / deliverable | Acceptance and command location |
|---|---|---|
| Sync | Source branches, installed migration, Factory ancestry | `01_sync.md`; no pointer change before real validation |
| Theory | Decomposition, coverage, selector and support boundaries | `02_theory.md`; supplementary commands in theory05; actual CPU results below |
| Data / GPU | Real reads, labels/split, numerical checkpoint and metric reproduction | `03_data_and_gpu.md`; GPU work only on eight RTX4090 cards, never a two-card substitute |
| Experiments | Graph/Generic, four component cells, active persistence, external/numerical axes | `04_experiments.md`; matched declared conditions and retained failures |
| Results / merge | CSV-derived figures, effect estimates, source-to-claim mapping | `05_results.md`; integration gates before either migration merges |

## Completed continuation

Benchmark fixes the missing direct Graph-minus-no-memory contrast, adds the two conditional cue/filter contrasts, and rejects nonfinite value intervals/tolerances. Twenty dependency-free tests pass. The original 24 exact-model rows are reproduced unchanged. Nine additional rows establish covered expansion with lower return and identical masked logs with different exclusion losses; main Sections 4.3, 6.3, 7.2 and 7.3 report the corresponding argument, estimands and values.

Actual commands, negative prepatch observations and validation scope are in Benchmark `results/graph_control/boundaries_20260916/README.md`. Figures come from those CSVs. No Graph policy, Factory core, provider or evaluator was replaced. No new PHM/SOTA/GPU result was obtained.

## Still required before merge

Full installed imports and original-versus-relocated behavior, a real PHM episode, numerical reload/recomputation, and active-ablation validation are pending. Factory main remains five commits behind the current gitlink at this inspection, not a fast-forward target. Five external bindings and faithful SOTA adapters remain implementation work; this is not yet a handoff with only GPU execution left.

Preserve all existing raw runs and source history. Update the existing goals rather than generating a parallel reviewer/plan pack. In this architecture the generic names `experiments/p19` and `external/phmfactory` do not relocate Graph work: use Benchmark `experiments/graph_control` and its existing `src/phm_data_factory` submodule. Fix failed hypotheses by revising the claim, not by adding models or replacing the test population.
