# P1_03 仓库蓝图

## 1. 节点范围

本节点把 P1_02 的伪代码和接口契约压缩成最小仓库蓝图。它只回答三个问题：

1. 哪些模块现在必须存在，哪些可以后置。
2. 目录与职责边界是否足够小、清楚、可复现。
3. 生成正式结果所需脚本、配置、日志和 artifact 应放在哪里。

本节点不执行正式实验，不选择 `selected_global_best_backend`，不把 Stage B 局部结果写成主结果，也不把 graph、Canvas、dashboard 或 review 文档变成结果真值。

## 2. 必须模块

仓库最小可执行路径只保留 7 类职责：

| module_id | 最小路径 | 必须性 | 职责 | 不得承担 |
| --- | --- | --- | --- | --- |
| data_read_boundary | `src/data/readers.py` | now | 从 Vibench read bundle 读入只读数据、metadata、H5/sample index | 不定义 split/window/metric/table truth |
| protocol_builder | `src/protocol/dataset_protocol.py` | now | 生成 PHMGA-owned DatasetProtocol、split/window、seed/repeat 配置 | 不读取 reviewer-only 文件，不改数据源 |
| planner_bridge | `src/planning/llm_bridge.py` | now | 调用免费模型 provider、规范化 planner 输出、记录 planner trace | 不直接写 paper claims |
| dag_compiler | `src/dag/compiler.py` | now | 把规范化 plan 编译成 validated DAG 与 feature pipeline | 不训练模型，不决定最终表格 |
| runner | `src/run/workflow.py` | now | 串联 preflight、planner、compile、train/eval、reject bundle | 不隐藏 failure mode |
| metrics_parser | `src/eval/metrics.py` | now | 解析 `metrics.json`，输出 train/val/test accuracy 与 macro_f1 | 不从 narrative report 反推指标 |
| ledger_writer | `src/reporting/ledger.py` | now | 写入 result ledger、artifact index、claim/evidence refs | 不允许 reject row 进入正结果表 |

这些模块覆盖了从 read-only 数据到 ledger row 的最短路径。任何 UI、dashboard、Canvas projection、batch orchestration、notebook 展示、论文排版导出都只能后置。

## 3. 可后置模块

| deferred_id | 后置内容 | 后置理由 | 进入条件 |
| --- | --- | --- | --- |
| web_dashboard | dashboard 或 cockpit 投影 | 不是实验真值，也不影响 artifact contract | Stage C/D rows 已经由 ledger 锁定后再做 |
| notebook_gallery | notebook/demo | 容易复制结果真值 | 只作为 artifact-derived 展示 |
| multi_provider_sweeper | 大规模 provider sweep | 当前限制为免费模型和最小正式路径 | 单一后端选择规则稳定后再扩展 |
| paper_exporter | LaTeX/figure export 自动化 | P1 阶段只需要仓库蓝图 | P2/P3 写作节点需要时再接入 |

## 4. 最小目录方案

```text
phmga/
  configs/
    datasets/*.yaml
    runs/*.yaml
    providers/*.yaml
    operators/*.yaml
    workflow_graphs/*.yaml
  scripts/
    preflight_dataset.py
    run_case.py
    validate_artifacts.py
    build_ledger.py
  src/
    data/readers.py
    protocol/dataset_protocol.py
    planning/llm_bridge.py
    dag/compiler.py
    run/workflow.py
    eval/metrics.py
    reporting/ledger.py
  artifacts/
    runs/<experiment_id>/
    ledgers/result_ledger.md
  tests/
    test_data_boundary.py
    test_dataset_protocol.py
    test_metric_parser.py
    test_artifact_contract.py
```

`configs/` 是可复现实验输入；`scripts/` 是人工/agent 调用入口；`src/` 是实现模块；`artifacts/runs/<experiment_id>/` 是单次 run 的证据包；`artifacts/ledgers/` 是 paper table eligibility 的唯一结果账本。

## 5. 生成正式结果的最小路径

```text
configs/datasets/<dataset>.yaml
  -> scripts/preflight_dataset.py
  -> configs/operators/<operator_registry>.yaml
  -> configs/workflow_graphs/<workflow_graph>.yaml
  -> src/protocol/dataset_protocol.py
  -> scripts/run_case.py
  -> src/planning/llm_bridge.py
  -> src/dag/compiler.py
  -> src/run/workflow.py
  -> src/eval/metrics.py
  -> artifacts/runs/<experiment_id>/
  -> scripts/validate_artifacts.py
  -> scripts/build_ledger.py
  -> artifacts/ledgers/result_ledger.md
```

每个正式 row 必须携带 `experiment_id`、dataset、split/window、seed/repeat、provider/model、operator registry id、workflow graph id、artifact directory、artifact contract result、feature separability result、test macro_f1、workflow exit 和 keep/reject 决策。

## 6. 脚本与资产放置规则

| asset_type | 路径 | 最小内容 | 审计规则 |
| --- | --- | --- | --- |
| dataset config | `configs/datasets/*.yaml` | dataset id、read bundle path、sample/metadata/H5 mapping、split/window policy | 修改后必须跑 preflight |
| run config | `configs/runs/*.yaml` | dataset、`workflow_graph_path`、operator registry、provider/model、budget、seed/repeat、max_iterations | 不得在运行中隐式改配置 |
| provider config | `configs/providers/*.yaml` | free model id、endpoint family、retry/schema policy | 不写 API key |
| operator registry | `configs/operators/*.yaml` | operator id、version、allowed args、schema、implementation reference | 只定义可用 operator，不记录 planner decision 或结果 |
| workflow graph config | `configs/workflow_graphs/*.yaml` | experiment/DAG input graph id、operator sequence constraints、dataset compatibility | 不得指向 `backend/graph/*`、Canvas 或 dashboard |
| run bundle | `artifacts/runs/<experiment_id>/` | DAG、planner trace、feature list、metrics、predictions、importance、workflow state、final report | 缺任一 required artifact 则 reject |
| ledger | `artifacts/ledgers/result_ledger.md` | keep/reject row 和 evidence refs | paper table 只引用 keep=accept row |

API key 只来自 `.env` 或进程环境，不能进入 config、artifact、ledger、review 或 manuscript。

`workflow_graph_path` 只允许指向 PHMGA workflow/DAG 输入，例如 `configs/workflow_graphs/rm101_ml.yaml`。它不是 `backend/graph/graph.json`，不是 Obsidian Canvas，也不是 web/dashboard 投影；这些派生产物不能作为实验 DAG 输入或结果真值。`OperatorRegistry` 被折叠为 `configs/operators/*.yaml`，由 `planner_bridge` 读取并由 `dag_compiler` 校验，因此不是额外全局模块。

## 7. 不变量

1. Vibench 只提供 read-only 数据边界；PHMGA 拥有 split/window、metric、ledger 和 paper table truth。
2. `metrics.json` 是 metric truth；`final_report.md` 只允许引用 artifact-derived narrative。
3. `result_ledger.md` 是 table eligibility truth；graph、dashboard、Canvas、review 文档都不是结果真值。
4. reject bundle 是有效负结果证据，但不能被写成正结果 claim。
5. 未锁定 `selected_global_best_backend` 前，Stage C/D 不得写主结果声明。
6. 所有正式入口必须先过 adapter/sample-level metadata-H5 preflight。
7. `planner_normalization_trace.json` 必须进入 run bundle 并被 `artifact_index.json` 引用；没有 planner trace 的 row 不能进入 ledger keep=accept。

## 8. 失败模式

| failure_id | 触发条件 | 必须响应 |
| --- | --- | --- |
| duplicate_truth_source | 同一 metric/table eligibility 被 ledger 外文件重新定义 | 阻止 paper claim，改为引用 ledger |
| architecture_ceremony | 新增 UI/agent/global registry 但不缩短正式结果路径 | 丢弃或后置该模块 |
| missing_preflight | 未完成 metadata-H5 sample-level alignment 就执行正式 run | 阻止 Stage C/D |
| metric_parser_gap | `metrics.json` 缺 train/val/test accuracy 或 macro_f1 | reject row，记录缺键 |
| reject_row_promoted | reject bundle 被写成 positive paper row | hard block，改入 limitation/negative evidence |
| secret_leak | provider key 出现在 config/artifact/review/manuscript | 立即移除并重跑 secret scan |
| operator_registry_gap | run config 引用的 operator registry 缺失、未版本化或未被 DAG compiler 校验 | reject row，补齐 `configs/operators/*.yaml` |
| scheduler_graph_confusion | `workflow_graph_path` 指向 `backend/graph/*`、Canvas 或 dashboard | hard block，改为 PHMGA workflow graph config |

## 9. 可审阅结论

P1_03 的最小仓库蓝图已经把必须模块、可后置模块、目录边界、入口脚本、artifact 路径和失败模式绑定到同一条正式结果路径。它提供的是工程边界和复现路径，不提供新的实验结果；下游仍必须完成 selected backend、adapter preflight、Stage C/D rows 和最终投稿 validator。

## 10. Final-threshold handoff contract

`artifacts/repo_blueprint_final_threshold_contract.yaml` 定义 P1_03 的最终分数阈值边界：本节点只因仓库蓝图交接足够完整而可进入 90+ 分，不因正式实验结果已经完成而加分。该合同把 P1_01 的数据/结果准入边界、P1_02 的接口/ledger truth 边界、P0_02 的 baseline budget 协议和 P0_04 的阶段 stop/fallback 合同统一到 P1_03 的仓库责任图。

P1_03 的 final-threshold pass 条件是：7 个 required modules 覆盖 read-only data 到 result ledger 的最短路径；`configs/datasets`、`configs/runs`、`configs/providers`、`configs/operators`、`configs/workflow_graphs` 只作为声明输入；`planner_normalization_trace.json`、`artifact_index.json`、`metrics.json` 与 ledger row 构成正式 row 的最小证据链；dashboard、Canvas、scheduler graph、review 文档、narrative report、notebook 和 partial/reject rows 均不得成为 metric 或 table truth。

该合同同时保留所有下游 blocker：P1 checklist/status closure、`selected_global_best_backend`、RM101 positive evidence、adapter sample-level metadata-H5 preflight、Stage C/D rows、P3 action closure 和最终 validator pass 均不属于 P1_03 score review 的可声称结果。
