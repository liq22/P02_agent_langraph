
# P1_01 数据层、Vibench 读取边界与 PHMGA 子模块引用

## 1. 节点目标

本节点用于固定 P02 论文系统的数据来源、数据读取边界、PHMGA 子模块引用关系与最小 provenance。当前节点不运行正式实验、不生成论文主表、不写最终结果；它只建立后续实验与论文写作所需的输入事实链。

## 2. 当前事实源划分

- 数据读取事实源：PHM-Vibench `data_factory`，只用于 metadata / H5 / raw signal / cache 的读取与审计。
- 项目实现事实源：PHMGA submodule，负责 DatasetProtocol、split/window、DAG workflow、bridge、ML/Torch、evaluation、report、ledger 与 main tables。
- 论文事实源：P02_agent_langraph 的 autoresearch selected nodes、claim-evidence registry、review、final TeX 与 final submission check。

## 3. 数据资源包边界

用户会把数据放在一个外部 `DATA_ROOT` 中。H5 文件和 metadata 文件不得直接提交到论文仓。论文仓只记录 manifest、checksum、metadata-H5 alignment、read bundle 与 provenance。

Formal P02 最小数据范围为：

- `RM_017_Ottawa19.h5`
- `RM_101_THU_GEARBOX.h5`
- `metadata.xlsx`

其他 `RM_*.h5` 作为扩展资源登记，不阻塞第一轮 submission-ready。

## 4. PHMGA 子模块绑定

PHMGA submodule 路径：

```text
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

分支：`journal_thesis`。

本节点必须记录 submodule commit。后续任何论文 claim、table、figure 都必须能回指 PHMGA commit、artifact_dir、result_md 和 ledger/main table。

## 5. 当前不允许声称的内容

- 不声称 PHMGA formal results 已完成，除非 PHMGA main tables 中已有 passed rows。
- 不把 proving lane 或 simple qualification 写成 formal paper result。
- 不把 Vibench DataLoader / sampler / trainer 的输出写成 PHMGA formal result。
- 不把 pending/fail/no_evidence 行写入论文主表。

## 6. 本节点交付物

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
- `logs/codex_run_001.md`
- `review/AI_001.md`
- `review/verdict.yaml`
- `review/response.yaml`

## 7. Handoff 条件

本节点只有在数据来源、版本/许可、子模块引用、最小复现路径、claim-evidence registry、negative result 记录和 external reviewer verdict 都满足后，才能交给 P1_02。
