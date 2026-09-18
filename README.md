# Graph-guided PHM Agent — scientific paper

This repository contains the scientific formulation and manuscript for the graph-guided PHM Agent paper.
Executable implementation is maintained in phm-agent-benchmark.

本仓维护 [GOAL](GOAL.md)、`paper/draft/main.md`、理论、文献、评审与[实验映射](experiment_spec/MAPPING.md)。Graph/state/runtime、配置、执行、评价、结果解析和绘图只在 `liq22/phm-agent-benchmark` 维护。

在 Benchmark checkout 中：
```bash
python main.py --config configs/paper02_graph/components.yaml
python main.py --config configs/paper02_graph/components.yaml --override command=run output=local_outputs/p2-dev
python main.py --config configs/paper02_graph/components.yaml --override command=finish output=local_outputs/p2-dev
```
默认只输出计划。实际运行使用相同数据、模型、工具和预算。本文先形成 G 的机制与边界结论，Benchmark 随后综合，不要求先完成 Skills。

本仓不再提供 src、experiments、scripts 或 tests。历史代码与结果见 [SOURCE_HISTORY](experiment_spec/SOURCE_HISTORY.md)，不作为本仓执行入口。出版图表保留来源映射，不是第二套原始结果。
