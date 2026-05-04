# P1_01 数据层_集中数据与子模块引用

## 1. Node objective

This node defines the data layer, data reading boundary, PHMGA submodule binding, and provenance requirements for P02 submission readiness.

## 2. Data source

The user provides a local DATA_ROOT containing canonical metadata, metadata lineage files, and RM-series H5 files. The formal P02 minimum scope uses `RM_017_Ottawa19.h5` and `RM_101_THU_GEARBOX.h5`.

## 3. Reading boundary

PHM-Vibench data_factory is used only to read metadata, select readers, access H5/raw signals, and materialize cache/read bundles.

## 4. PHMGA handoff

After reading, data are handed to PHMGA DatasetProtocol. PHMGA owns split, windowing, signal layout normalization, DAG-agent workflow, bridge, ML/Torch evaluation, reports, ledger, and main tables.

## 5. Submodule

PHMGA is the implementation submodule:

```text
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

## 6. Evidence rules

No formal result can enter the paper unless it traces to DATA_ROOT, vibench_read_bundle, PHMGA submodule commit, experiment_id, artifact_dir, result_md, ledger row, and main table row.
