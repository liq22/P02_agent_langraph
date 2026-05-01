---
name: structured_map_builder
description: Build one compact node-local map, matrix, registry, or digest from local inputs. Use when the selected node needs a structured artifact rather than free-form prose.
---

# Structured Map Builder

## 使用时机
- 当前 node 需要表格化、矩阵化或 registry 化的本地工件
- 输入已经局限在当前 node
- 输出目标比 prose 更像 map / matrix / registry

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 本地 docs / artifacts 中声明的输入
- 若目标 node 属于 P3，读取最近上级 `prompts/standards.md` 中的 paper iteration gate 标准。

## Workflow
1. 确认当前任务目标是结构化工件。
2. 读取最小必要的 node-local 输入。
3. 按节点语义选择最小 map 类型：literature-gap、protocol、claim-evidence、critique、response、coverage、revision-evidence、reviewer-lens、review-issue、paper-iteration-gate 或 bundle manifest。
4. 每行尽量包含稳定 ID、claim/evidence/comment 引用、source/location、status、next action。
5. 对 evidence-bearing 节点，保留 negative/failure/unclear 条目，不用空白或正结果叙事覆盖。
6. 对 P3 revision map，每行必须绑定 issue_id、target_phase、target_node、action_type、expected_evidence、validation_gate 与 next_iteration_trigger。
7. 避免在图或 registry 之外复制正文。
8. 更新状态并返回。

## 产出
- 本地 map / matrix / registry 工件
- 本地状态更新

## 边界
- 不扩成 global registry builder
- 不修改 graph
- 不复制大段正文

## stop_with
- 没有可结构化输入
- 所需输出不是结构化工件
- 需要 hard block 但缺 claim/evidence/location/actionable_fix
- P3 action map 缺 target node、expected evidence 或 validation gate
