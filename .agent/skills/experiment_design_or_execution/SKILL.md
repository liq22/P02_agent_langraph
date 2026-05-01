---
name: experiment_design_or_execution
description: Advance one selected P1 node with one bounded protocol, setup, or execution-preparation step. Use for P1 design nodes before or around experiments, without becoming a global experiment orchestrator.
---

# Experiment Design Or Execution

## 使用时机
- 目标 node 属于 P1
- 需要设计协议、评测、仓库蓝图、执行准备或局部验证策略
- 尚未进入完整 auto experiment campaign，或只需其前置准备

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时 node-local docs / artifacts
- 若存在 `prompts/research_prompt.md` 或最近上级 `prompts/standards.md`，读取其中的 P1 protocol 标准

## Workflow
1. 确认本轮只做一个 P1 局部动作。
2. 先写清 hypothesis、baseline、metric、success/failure signal 与最低可行 pilot。
3. 补全协议、评测、蓝图、输入输出边界，或准备 execution contract。
4. 如果 node 已明确 campaign-ready，只生成 handoff 所需 contract，不在此 skill 内扩大实验循环。
5. 写回 node-local 产物并返回。

## 产出
- 协议/蓝图/contract 等 node-local 工件
- 本地状态更新

## 边界
- 不选 node
- 不替代 auto_experiment_worker
- 不在缺 baseline、metric parser 或 budget 时启动真实实验
- 不刷新 graph

## stop_with
- 需要真实实验但 execution contract 仍不完整
- node 依赖未满足
- 局部协议无法在当前 node 内界定
