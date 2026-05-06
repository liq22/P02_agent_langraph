# P1_05 Gate Report

- node_id: `research::P1_实验设计与仓库蓝图::P1_05_初步验证结果整理`
- generated_at: 2026-05-04
- actor: codex-local
- input_ledger: `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`
- round_type: result synthesis
- final_threshold_contract: `artifacts/result_synthesis_final_threshold_contract.yaml`

## Input Verification

The P1_04 source ledger exists and contains two rows:

| row_id | role | test_accuracy | test_macro_f1 | decision |
| --- | --- | ---: | ---: | --- |
| baseline_simple | baseline | 0.8333333333333334 | 0.8285714285714285 | baseline |
| attempt_supervisor_proving | controlled_attempt | 1.0 | 1.0 | keep_limited_synthetic_signal |

The controlled attempt improves test accuracy by `0.16666666666666663`.

## Claim-Safety Decision

Supported:

- `P1_05_C01_KEEP_LIMITED_SYNTHETIC_SIGNAL`: supervisor_proving has a bounded offline synthetic keep signal over simple_fullchain.

Unsupported:

- real-data generalization
- RM101 Stage B resolution
- selected backend readiness
- formal Stage C/D paper performance claim

Unclear:

- variance stability
- whether the perfect synthetic accuracy reflects meaningful mechanism improvement or a trivial synthetic fixture

## Handoff

P1_05 can hand off a small preliminary/synthetic sanity-check summary to writing/planning nodes. The summary must include the synthetic/offline boundary and cannot be used as a main result table row.

The final-threshold handoff contract preserves the same boundary: score readiness is based on faithful result-state synthesis only, not on real-data generalization, RM101 resolution, selected-backend readiness, formal Stage C/D evidence, variance stability, checklist closure, P3 action closure, or final validator pass.
