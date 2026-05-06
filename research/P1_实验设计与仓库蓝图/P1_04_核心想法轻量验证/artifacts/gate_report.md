# P1_04 Gate Report

- node_id: `research::P1_实验设计与仓库蓝图::P1_04_核心想法轻量验证`
- generated_at: 2026-05-04
- actor: codex-local
- round_type: bounded offline synthetic execution
- contract_mode: `executable`
- execution_started: true

## Gate Decision

Execute only as lightweight synthetic/offline evidence. The original missing `./idea_validation_repo` target was replaced by the existing PHMGA submodule after offline synthetic preflight passed:

- `repo_path`: `../P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA`
- source mode: synthetic
- LLM mode: offline_stub
- evidence_id: `P1_04_E03_PHMGA_OFFLINE_SYNTH_BINDING`

This run does not use external providers and does not claim formal Stage C/D readiness.

## Required Questions

| Question | Current Answer |
| --- | --- |
| baseline 是什么？ | `P1_04_BASELINE_001`: PHMGA `ottawa_synth_ml_simple` simple_fullchain baseline with `data=ottawa_synth` and `llm.mode=offline_stub`. |
| primary metric 是什么？ | `test.accuracy`, `higher_is_better`, parsed from each run's `metrics.json`. |
| 这一轮只改变哪个概念因素？ | Replace simple_fullchain with supervisor_proving plan-execute-compile-verify path while synthetic Ottawa data, graph_path=ml, offline_stub, and metric parser remain fixed. |
| 什么结果算 keep/discard？ | keep if controlled attempt test accuracy is greater than baseline test accuracy; discard if it is less than or equal or either row cannot run/parse. |

## Results

| row_id | role | workflow mode | test accuracy | test macro_f1 | artifact dir | decision |
| --- | --- | --- | ---: | ---: | --- | --- |
| baseline_simple | baseline | simple_fullchain | 0.8333333333333334 | 0.8285714285714285 | `artifacts/auto_experiment/runs/baseline_simple` | baseline |
| attempt_supervisor_proving | controlled_attempt | supervisor_proving | 1.0 | 1.0 | `artifacts/auto_experiment/runs/attempt_supervisor_proving` | keep_limited_synthetic_signal |

Observed delta accuracy: `+0.16666666666666663`.

## Resolved Blocking Issues

| blocker_id | resolution |
| --- | --- |
| P1_04_BLOCK_REPO_PATH_MISSING | Replaced missing `idea_validation_repo` with the existing PHMGA submodule for bounded synthetic/offline validation. |
| P1_04_BLOCK_RUN_TARGET_UNBOUND | Baseline and controlled attempt commands both exited 0 and wrote `metrics.json`. |

## Artifact Boundary

This round created:

- `artifacts/auto_experiment/results.tsv`
- `logs/auto_experiment/latest_run.log`
- `artifacts/lightweight_validation_final_threshold_contract.yaml`

These are observed lightweight execution artifacts for synthetic/offline validation only. They do not unlock paper claims.

## Replay Trace

`logs/auto_experiment/latest_run.log` records the bounded replay fields required for P1_04/P1_05 handoff: working directory, python executable, exact baseline command, exact controlled-attempt command, both exit codes, and the deterministic boundary that this was synthetic Ottawa with `offline_stub`, no external provider call, and no formal Stage C/D claim.

The replay trace is sufficient for this lightweight node's score review. It is not sufficient to promote the result into formal paper evidence; real-data protocol rows, selected-backend lock, repeated-run or variance evidence, adapter preflight, and Stage C/D acceptance remain downstream blockers.

## Handoff

Next action for P1_04:

1. Send this P1_04 package to an independent reviewer.
2. Require the reviewer to check that the synthetic/offline boundary is explicit and that no formal Stage C/D claim is made.
3. Only after review pass may the node move toward closure or P1_05 handoff.

Positive formal-result claims remain blocked until real-data formal rows and downstream review gates pass.
