# P1_01_数据层_集中数据与子模块引用

## 目标
统一管理 centralized_data / submodule_ref_data / hybrid_data 三种模式。

## 数据模式
- centralized_data：数据集中保存，本仓维护切分与索引。
- submodule_ref_data：数据处理逻辑、协议或 baseline 来自子模块，本仓只记录引用与边界。
- hybrid_data：部分数据集中保存，部分通过子模块引用。

## 关键判断
- 原始大数据不重复复制。
- 元数据、切分、lineage 与使用边界必须被结构化记录。
- 处理逻辑优先引用，不复制实现。
