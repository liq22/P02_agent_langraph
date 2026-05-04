# P1_02 伪代码与接口契约

## 1. 节点边界

本节点只定义 PHMGA 下游实现应遵守的伪代码、输入输出、状态转移和不变量。它不执行正式实验，不选择最终 backend，不把任何 Stage B 局部结果写成主结果声明。

上游 P1_01 已关闭数据/provenance/submodule 边界：Vibench 只提供只读数据读取包，PHMGA 负责 split/window、DatasetProtocol、DAG workflow、bridge、training/evaluation、ledger 和 paper artifact。P1_02 的伪代码必须保持这个责任划分。

## 2. 输入输出

### 输入

- `DataReadBundle`: 来自 Vibench/data audit 的只读数据包，包含 metadata 路径、H5 路径、dataset name、sample keys、channel/window hints、checksum/provenance 摘要。
- `DatasetProtocol`: PHMGA 内部协议，包含 split strategy、window spec、selected channels、label policy、random seed 和 source-mode。
- `RunConfig`: graph path、LLM provider/model、retry/backoff、max_iterations、min/max DAG depth、output_dir、artifact policy。
- `OperatorRegistry`: 可用 transform、aggregate、ML/Torch bridge、evaluation operator 及其 shape/legal-path 约束。
- `ClaimPolicy`: 当前 paper claim 边界，特别是 pending/reject/no-evidence 行不得进入主结果声明。
- `BaselineSpec`: downstream comparison baseline contract，定义必须出现的 baseline rows、artifact 名称、metric 对齐和 ledger 处理。
- `MetricSchema`: `metrics.json` 与 parser 接受标准，定义 split、seed/repeat、macro-F1/proxy quality 和 parse failure 行为。

### 输出

- `validated_dag.json`: schema、shape、legal-path 均通过的 DAG。
- `compiled_dag_manifest.json`: DAG 到 `ml` 或 `torch` path 的编译 manifest。
- `feature_pipeline.json` 与 `feature_list.json`: terminal features 和可复现特征流水线。
- `metrics.json`、`feature_separability_summary.json`、`predictions.json`、`importance.json`: 评价证据。
- `final_report.md`: artifact-derived 报告，必须区分 supported / unsupported / unclear。
- `result_md` 与 ledger row: 只在 artifact contract 和 gate 满足时进入对应 evidence path。

## 3. Baseline 合同

P1_02 不决定最终方法优劣，但必须定义 downstream formal run 不能省略的 baseline rows。每个 formal dataset/graph path 至少保留以下比较位置：

| baseline_id | artifact_suffix | 作用 | 必须共享的 metric |
| --- | --- | --- | --- |
| `deterministic_feature_lr` | `_deterministic_feature_lr` | 无 LLM planner 的 deterministic feature plan + logistic regression，下界和 sanity check | accuracy、macro_f1、feature_count、artifact_contract_pass |
| `llm_planned_ml` | run preset 原始 suffix | LLM planner 生成或 fallback 修复后的 PHMGA ML path 主比较 | accuracy、macro_f1、feature_separability decision、workflow_exit |
| `reject_evidence_max_iter` | `_qualityfix*` 或 `_reject_evidence` | 记录 max_iterations 后仍未 finish 的负结果 | macro_f1、last_reflection_decision、compiled_for_rejection_evidence |

Baseline 不通过时的处理：

1. 缺 artifact bundle 或 parse 失败：ledger row 必须 `keep=reject`，不能进入 paper table。
2. deterministic baseline 失败：阻断对应 dataset 的 formal claim，因为 sanity check 不成立。
3. LLM row 低于 baseline 或 max-iteration reject：只能写 negative/limitation evidence，不能写 supported positive result。
4. 所有 baseline 和 LLM row 必须引用同一 split/window policy，否则比较无效。

## 4. Metric schema 与 parser 合同

`metrics.json` 的最小 schema：

```yaml
train:
  accuracy: float
  macro_f1: float
val:
  accuracy: float
  macro_f1: float
test:
  accuracy: float
  macro_f1: float
metadata:
  dataset_name: optional string
  graph_path: optional string
  split_seed: optional int
  repeat_id: optional string
```

Parser 接受标准：

- `train`、`val`、`test` 三个 split 必须至少包含 `accuracy` 和 `macro_f1`。
- 所有 metric 必须是 finite number；缺失、非数值或 NaN/Inf 直接使 row `reject`。
- 若后续引入 repeats，`repeat_id` 与 `split_seed` 必须写入 metadata 或 result_md；聚合时报告 mean、std、n，不能只报最好一次。
- `feature_separability_summary.json` 必须提供 `decision`、`feature_count`、`non_empty_feature_count`、`constant_feature_count` 和 split stability 或等价解释。
- `workflow_state.json:path_artifacts.workflow_exit.compiled_for_rejection_evidence=true` 时，metrics 只能作为 reject evidence，不能作为 passed row。

## 5. 主流程伪代码

```text
procedure PHMGA_RUN_CASE(data_bundle, dataset_protocol, run_config, operator_registry, claim_policy):
    assert data_bundle.source_mode in {"real", "synthetic"}
    assert dataset_protocol.dataset_name == data_bundle.dataset_name
    assert run_config.output_dir is relative to the PHMGA artifact root
    assert claim_policy.forbids_pending_rows_as_positive_evidence

    preflight = PREFLIGHT_DATA_AND_PROVIDER(data_bundle, dataset_protocol, run_config)
    if not preflight.ok:
        return EXPORT_REJECT_EVIDENCE(reason=preflight.reason, stage="preflight")

    workflow_state = INIT_WORKFLOW_STATE(data_bundle, dataset_protocol, run_config)
    last_stable_dag = INIT_INPUT_DAG(dataset_protocol.channels)

    for round_index in 1..run_config.max_iterations:
        context = BUILD_PLANNER_CONTEXT(
            workflow_state=workflow_state,
            last_stable_dag=last_stable_dag,
            operator_registry=operator_registry,
            dataset_protocol=dataset_protocol
        )

        raw_plan = CALL_PLANNER_PROVIDER(context, run_config.llm)
        step_plan = PARSE_AND_NORMALIZE_STEP_PLAN(raw_plan, operator_registry)
        if MODEL_PATH_REQUIRES_FEATURES(run_config.graph_path) and HAS_NO_AGGREGATE_FEATURES(step_plan):
            step_plan = DETERMINISTIC_FEATURE_PLAN(dataset_protocol.channels)

        candidate_dag = APPLY_STEP_PLAN(last_stable_dag, step_plan, operator_registry)
        dag_check = VALIDATE_DAG(candidate_dag, run_config, operator_registry)
        if not dag_check.ok:
            workflow_state = RECORD_REJECTION(workflow_state, dag_check)
            continue

        compiled = COMPILE_DAG_FOR_PATH(candidate_dag, run_config.graph_path)
        execution = EXECUTE_COMPILED_PIPELINE(compiled, data_bundle, dataset_protocol, run_config)
        artifact_gate = CHECK_ARTIFACT_CONTRACT(execution.artifacts)
        separability_gate = CHECK_FEATURE_SEPARABILITY(execution.artifacts)

        reflection = REFLECT_ON_QUALITY(
            dag=candidate_dag,
            execution=execution,
            artifact_gate=artifact_gate,
            separability_gate=separability_gate,
            run_config=run_config
        )

        workflow_state = APPEND_ROUND(
            workflow_state,
            step_plan=step_plan,
            dag=candidate_dag,
            execution=execution,
            reflection=reflection
        )

        if reflection.decision == "finish" and artifact_gate.ok:
            return EXPORT_ACCEPT_OR_REJECT_BUNDLE(
                workflow_state=workflow_state,
                dag=candidate_dag,
                execution=execution,
                claim_policy=claim_policy
            )

        if reflection.decision in {"need_patch", "need_replan"}:
            last_stable_dag = SELECT_NEXT_ROUND_DAG(last_stable_dag, candidate_dag, reflection)
            continue

    return EXPORT_MAX_ITERATION_REJECT_BUNDLE(
        workflow_state=workflow_state,
        last_reflection=workflow_state.last_reflection,
        compiled_for_rejection_evidence=true
    )
```

## 6. 必要步骤与实现细节边界

必要步骤：

1. 数据和 provider preflight 必须先于 planner 调用。
2. LLM 输出必须经过 structured parser、operator registry 和 shape/legal-path validator。
3. `ml` / `torch` 路径必须存在 terminal feature 或可训练输出；transform-only DAG 不可进入训练。
4. 每轮必须导出 round history、normalization trace、DAG quality 和 artifact contract evidence。
5. max-iteration 结束时必须导出 reject-evidence bundle，而不是静默失败。
6. ledger row 只能引用已存在 artifact_dir、result_md、metrics 和 gate status。

实现细节：

- 具体 provider retry/backoff、HTTP transport、schema repair 和 deterministic fallback 是实现层细节，但必须被 trace 记录。
- 具体模型算法可以是 logistic regression、compiled torch 或后续替代模块；接口只要求 artifact contract 稳定。
- 报告生成可由 provider 或 deterministic fallback 完成，但报告内容必须来自 artifacts。

## 7. 状态转移

```text
preflight_pending
  -> preflight_failed
  -> reject_evidence_exported

preflight_pending
  -> planning
  -> validating_dag
  -> executing_path
  -> reflecting
  -> finish_candidate
  -> artifact_bundle_exported

reflecting
  -> need_patch
  -> planning

reflecting
  -> need_replan
  -> planning

reflecting
  -> max_iterations_reached
  -> reject_evidence_exported
```

## 8. 不变量

- Vibench 只提供 read bundle；任何 split/window/metric/table truth 必须由 PHMGA 生成。
- 所有 output artifact 必须位于 run-specific `output_dir` 下，不覆盖其他 run。
- `validated_dag.json` 只记录可执行 operator，不保存自然语言承诺。
- `metrics.json` 和 `feature_separability_summary.json` 必须来自实际 artifact，而不是 report 文本。
- `predictions.json`、`importance.json`、`final_report.md` 与 ledger row 必须能回指同一个 `artifact_index.json`。
- `final_report.md` 的每个结论段落必须落入 supported / unsupported / unclear / limitation 之一；unsupported 和 unclear 不得提升为 positive claim。
- `selected_global_best_backend` 未锁定时，Stage C/D 不得执行或写入主结果 claims。
- reject-evidence bundle 是有效负结果，但不能被写成 positive result。

## 9. 失败模式与异常分支

- `provider_rate_limit_or_schema_error`: 记录 transport/normalization trace，使用 deterministic fallback 时必须标明来源。
- `zero_feature_matrix`: 阻断训练并导出 reject evidence；不能伪造 metrics。
- `weak_proxy_or_test_macro_f1`: 可继续 patch/replan；max_iterations 后导出 reject evidence。
- `artifact_contract_missing_file`: row 必须 reject，不能进入 paper table。
- `metric_parser_missing_required_key`: row 必须 reject，并在 result_md 中列出缺失 key。
- `baseline_split_mismatch`: 比较无效，阻断 backend selection。
- `metadata_h5_alignment_gap`: preflight 阻断 formal downstream execution，直到样本级对齐验证完成。

## 10. Artifact 与 evidence mapping

每个 formal result row 必须满足：

```text
experiment_id
  -> artifact_dir
  -> artifact_index.json
  -> metrics.json / feature_separability_summary.json / workflow_state.json
  -> result_md
  -> ledger row
  -> optional paper table row
```

`final_report.md` 不作为 metric truth，只作为 artifact-derived narrative。ledger row 是 table eligibility truth；paper table 只能引用 `keep=accept`、artifact contract pass、feature separability pass、且无 reject workflow_exit 的 row。

## 11. 可审阅结论

P1_02 当前伪代码支持后续实现与审阅：输入输出明确、baseline 和 metric parser 合同显式、必要步骤和实现细节分离、状态转移可追踪、不变量保护数据/结果真值边界，并列出异常分支。独立 AI review 和用户授权的 Claude Code teammate human-review lane 均已给出 pass；这只关闭 P1_02 节点，不解锁 selected backend、Stage C/D 正结果或最终投稿声明。
