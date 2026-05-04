# P1_01 数据层、数据血缘与子模块引用

## 1. 节点目标

本节点用于收敛 P02 论文系统的数据对象、数据血缘和代码子模块引用关系。当前节点不执行 PHMGA formal experiments，也不撰写最终论文结果；它只建立后续实验与写作必须遵守的数据/代码/provenance 边界。

## 2. 数据来源边界

P02 的数据资源由用户提供的 `DATA_ROOT` 文件夹承载。该文件夹包含 `metadata.xlsx`、metadata 历史版本，以及多个 `RM_*.h5` 数据文件。

本论文系统采用 PHM-Vibench `data_factory` 体系作为数据读取与数据目录接口，但只使用到读取层：metadata 加载、dataset reader 选择、H5/raw signal/cache 访问、metadata-H5 对齐审计。

读取之后的数据交给 PHMGA。PHMGA 负责 DatasetProtocol、SplitManifest、WindowSpec、SignalRecord、split-before-windowing、DAG workflow、bridge compilation、ML/Torch evaluation、result ledger、main tables 和最终 report。

## 3. Formal P02 最小数据范围

第一轮 submission-ready 的 formal 最小数据范围为：

- `RM_017_Ottawa19.h5`
- `RM_101_THU_GEARBOX.h5`
- `metadata.xlsx`

其余 `RM_*.h5` 文件作为扩展资源登记，不阻塞第一轮 submission-ready。

## 4. Metadata 版本策略

默认策略：

- `metadata.xlsx`：canonical metadata。
- `metadata_25_10_30.xlsx`：metadata lineage/history。
- `metadata_25_11_13.xlsx`：metadata lineage/history。

除非 human 明确指定，否则历史 metadata 不进入 formal experiment。

## 5. PHMGA 子模块关系

PHMGA 是 P02 项目实现仓与正式实验事实源。它作为 submodule 挂载在：

```text
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

目标分支：

```text
journal_thesis
```

所有论文结果必须能回指 PHMGA submodule commit、formal artifact directory、result_md、result ledger 和 main tables。

## 6. 不在本节点完成的事项

本节点不完成：

- PHMGA Stage B/C/D formal runs；
- main table 更新；
- final TeX 写作；
- final submission-ready 声明。

这些必须在后续节点和 PHMGA formal gate 中完成。

## 7. 当前结论

本节点建立三层事实源：

```text
PHM-Vibench data_factory = data reading truth
PHMGA = project and formal experiment truth
P02_agent_langraph = paper, review, and submission truth
```

只有当数据包审计、Vibench read bundle、PHMGA formal artifact、claim-evidence registry 和 final submission check 全部通过后，才能声明 submission-ready。
