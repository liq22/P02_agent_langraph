# P1_01 数据层、Vibench 读取边界与 PHMGA 子模块引用

## 1. 节点目标

本节点固定 P02 submission-ready 工作流的数据来源、数据读取边界、PHMGA 子模块引用关系与最小 provenance。当前节点不运行正式实验、不生成论文主表、不写最终实验结果；它只建立后续实验与论文写作必须遵守的输入事实链。

## 2. 当前事实源划分

- 数据读取事实源：PHM-Vibench `data_factory` 只用于 metadata、H5、raw signal、cache 的读取与审计。
- 项目实现事实源：PHMGA submodule 负责 DatasetProtocol、split/window、DAG workflow、bridge、ML/Torch、evaluation、report、ledger 与 main tables。
- 论文事实源：P02_agent_langraph 的 selected nodes、claim-evidence registry、review、final TeX 与 final submission check。

因此，本节点只记录数据和代码边界，不把 graph、Canvas、dashboard 或 Vibench DataLoader/sampler/trainer/evaluator 输出当作论文结果事实源。

## 3. 数据资源包边界

用户提供的外部 `DATA_ROOT` 为：

```text
/mnt/k/D01_vibench
```

该目录不进入论文仓库；论文仓只记录 manifest、checksum、metadata-H5 audit、read bundle 和 provenance。已审计的 first-round formal 数据范围为：

- `metadata.xlsx`
- `RM_017_Ottawa19.h5`
- `RM_101_THU_GEARBOX.h5`

审计输出位于：

```text
docs/submission_ready_goal/runtime_logs/data_audit/
```

审计结论为 `data_ready: pass`，score 为 `100`。审计记录了 `metadata.xlsx` 共 `49855` 行，`RM_017_Ottawa19.h5` 有 `36` 个顶层 H5 key，`RM_101_THU_GEARBOX.h5` 有 `240` 个顶层 H5 key。预览级 metadata-H5 alignment 没有 hard fail；完整样本级 alignment 仍应由 Vibench/PHMGA adapter 在正式 preflight 中复核。

扩展 H5 文件仅登记为扩展资源，不阻塞第一轮 submission-ready。

## 4. PHMGA 子模块绑定

PHMGA 是 P02 项目实现仓与正式实验事实源。它作为 submodule 挂载在：

```text
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

分支为 `journal_thesis`，当前记录 commit：

```text
914bc5925d5230917a5de95d88784075fb2b041e
```

后续任何论文 claim、table、figure 都必须能回指 PHMGA commit、formal artifact directory、result markdown、result ledger 和 main tables。

## 5. 模型与 API 边界

本轮 submission-ready 只允许使用免费模型路径：

- OpenRouter：仅允许模型名以 `:free` 结尾的免费模型，当前默认 `z-ai/glm-4.5-air:free`。
- BigModel：仅允许 `glm-4.7-flash`，通过 `BIGMODEL_API_KEY` 从环境变量读取。

API key 不写入仓库文件。live key check 只允许使用 `tools/submission_ready_goal/verify_llm_keys.py`，并且该工具只记录 provider、model、env var 名和 pass/fail，不记录 key 或完整响应。

## 6. 当前不允许声称的内容

- 不声称 PHMGA formal results 已完成，除非 PHMGA main tables 中已有 passed rows。
- 不把 proving lane 或 simple qualification 写成 formal paper result。
- 不把 Vibench DataLoader/sampler/trainer/evaluator 的输出写成 PHMGA formal result。
- 不把 pending、fail、no_evidence、transport-failure 或 planner-timeout 行写入论文主表。

## 7. 本节点交付物

本节点已经建立数据与代码边界的本地工件：

- `artifacts/data_lineage.yaml`
- `artifacts/submodule_ref.yaml`
- `artifacts/vibench_data_factory_binding.yaml`
- `artifacts/data_reading_boundary.yaml`
- `artifacts/phmga_data_protocol_handoff.yaml`
- `artifacts/result_source_map.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/failure_register.yaml`
- `artifacts/negative_result_note.md`
- `artifacts/keep_discard_ledger.yaml`

## 8. Handoff 条件

本节点只有在数据来源、版本/许可、子模块引用、最小复现路径、claim-evidence registry、negative result 记录和 external reviewer verdict 都满足后，才能交给 P1_02。当前数据审计和子模块记录已完成；正式进入下游实验前仍需要独立 reviewer gate 和 PHMGA preflight gate。
