# P1_04 核心想法轻量验证

## 1. 当前轮次定位

本轮从 execution-contract gate round 升级为 bounded offline synthetic execution round。原始 contract 指向缺失的 `./idea_validation_repo`，经 workspace filename scan 和 PHMGA preflight 后，改为绑定现有 PHMGA 子模块的离线 synthetic lane。所有输出限制在本节点：

- `artifacts/auto_experiment/runs/baseline_simple`
- `artifacts/auto_experiment/runs/attempt_supervisor_proving`
- `artifacts/auto_experiment/results.tsv`
- `logs/auto_experiment/latest_run.log`

## 2. 轻量验证问题

- baseline: `P1_04_BASELINE_001`，PHMGA `ottawa_synth_ml_simple` simple_fullchain baseline，`data=ottawa_synth`，`llm.mode=offline_stub`。
- primary metric: `test.accuracy`，方向为 `higher_is_better`，从每个 run 的 `metrics.json` 解析。
- single changed factor: 将 simple_fullchain baseline 替换为 supervisor_proving plan-execute-compile-verify path；synthetic Ottawa data、`graph_path=ml`、offline_stub 与 metric parser 保持一致。
- keep: baseline 与 controlled attempt 都完成且 metric 可解析，controlled attempt test accuracy 大于 baseline test accuracy。
- discard: controlled attempt accuracy 小于等于 baseline，或者任一 row 不能运行/解析。
- unclear: 只有单 row 运行、metric 缺失/非有限，或 variance 无法和单一变化因素区分。

## 3. 当前结果

| row_id | run preset | mode | test accuracy | test macro_f1 | decision |
| --- | --- | --- | ---: | ---: | --- |
| baseline_simple | `ottawa_synth_ml_simple` | simple_fullchain | 0.8333333333333334 | 0.8285714285714285 | baseline |
| attempt_supervisor_proving | `ottawa_ml_codex_proving data=ottawa_synth llm.mode=offline_stub` | supervisor_proving | 1.0 | 1.0 | keep_limited_synthetic_signal |

Observed delta accuracy is `+0.16666666666666663`, so the bounded synthetic/offline signal is keep.

## 4. 结论边界

本节点只支持 lightweight synthetic/offline keep signal。它不能作为 Stage C/D formal result，不能解锁 `selected_global_best_backend`，不能解决 RM101 Stage B reject rows，也不能写成 submission-ready performance claim。

## 5. Final-threshold handoff contract

`artifacts/lightweight_validation_final_threshold_contract.yaml` 定义 P1_04 的最终分数阈值边界：本节点只因 bounded offline synthetic validation 可复现、baseline-first、单因素变化、metric parser 一致、keep/discard 决策可审计而可进入 90+ 分，不因正式实验证据已经完成而加分。

该合同锁定的 P1_04-scope 事实包括：baseline 与 controlled attempt 均 exit 0；`results.tsv` 与两个 `metrics.json` 的 test accuracy / macro-F1 一致；`logs/auto_experiment/latest_run.log` 记录 cwd、python、exact replay commands、exit codes 和 synthetic/offline determinism boundary；controlled attempt 在相同 synthetic Ottawa、`graph_path=ml`、offline_stub 与 metric parser 下只改变 supervisor_proving 路径，并得到 `+0.16666666666666663` 的 test accuracy delta。

该合同同时保留所有下游 blocker：`selected_global_best_backend`、RM101 positive evidence、adapter sample-level metadata-H5 preflight、real-data Stage C rows、Stage D ablation rows、P1 checklist/status closure、P3 action closure 和 final validator pass 均不属于 P1_04 score review 的可声称结果。
