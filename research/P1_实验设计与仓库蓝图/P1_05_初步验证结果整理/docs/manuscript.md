# P1_05_初步验证结果整理

## 目的
把轻量验证结果转成结构化判断，决定是否进入正式实现。

## 应回答的问题
- 哪个方案值得继续
- 哪些假设被证伪
- 哪些实验需要复现或加样本

## 当前整理结论

P1_04 的 source ledger 已存在并包含两行 bounded offline synthetic 结果。`attempt_supervisor_proving` 相比 `baseline_simple` 的 test accuracy 从 `0.8333333333333334` 到 `1.0`，delta 为 `+0.16666666666666663`。因此当前只支持一个有限结论：supervisor_proving 值得作为后续机制候选继续检查。

不支持的结论同样明确：这不是 real-data generalization，不解决 RM101 Stage B reject evidence，不锁定 selected backend，也不能进入正式 Stage C/D 主结果表。variance stability 和 perfect synthetic accuracy 的解释仍为 unclear，必须在下游 repeated/real-data run 中处理。

## Final-threshold handoff contract

`artifacts/result_synthesis_final_threshold_contract.yaml` 定义 P1_05 的最终分数阈值边界：本节点只因结果整理足够可审计而可进入 90+ 分，不因正式实验或投稿证据已经完成而加分。

该合同锁定的 P1_05-scope 事实包括：唯一正向结论 `P1_05_C01_KEEP_LIMITED_SYNTHETIC_SIGNAL` 完整回指 P1_04 source ledger 和两个 `metrics.json`；real-data generalization、RM101 resolution、selected-backend readiness、formal Stage C/D evidence 继续是 unsupported；variance stability 与 perfect synthetic accuracy interpretation 继续是 unclear；`paper_ready_result_summary.md` 只能用作 preliminary/synthetic sanity-check wording。

该合同同时保留所有下游 blocker：selected backend、RM101 positive evidence、adapter sample-level metadata-H5 preflight、real-data Stage C rows、Stage D ablations、P1 checklist/status closure、P3 action closure 和 final validator pass 均不属于 P1_05 score review 的可声称结果。
