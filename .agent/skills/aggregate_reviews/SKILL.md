---
name: aggregate_reviews
description: Aggregate one selected node's review or critique files into a compact digest. Use when a node-local review synthesis artifact is needed without widening scope.
---

# Aggregate Reviews

## 使用时机
- 当前 node 已经有 review / critique 文件
- 需要把多条评论压缩成 digest、cluster 或 action list
- 不需要执行完整 review loop

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 本地 review / critique 文件
- 若目标 node 属于 P3，读取最近上级 `prompts/standards.md` 中的 paper iteration gate 标准。

## Workflow
1. 只读取当前 node 的 review 相关文件。
2. 归并重复评论，按主题或动作聚类，同时保留少数强反对意见和矛盾反馈。
3. 将每个 cluster 标注 source_comment_ids、severity、affected claim、evidence gap、location、next action。
4. hard fail cluster 必须带 claim/evidence/location/actionable_fix；不满足时降级为 advisory/major。
5. 对 P3 paper iteration，按 checklist dimension 形成 `artifacts/review_issue_register.yaml`，并保留 unresolved blockers。
6. 输出一份紧凑 digest 或 action list。
7. 更新本地状态并返回。

## 产出
- 本地 digest / critique cluster 工件
- 本地状态更新

## 边界
- 不跨 node 聚合
- 不修改 graph
- 不替代 response writing

## stop_with
- 没有可聚合评论
- 评论结构太脏且无局部清洗规则
- 聚合会掩盖关键负面证据或冲突意见
- P3 聚合无法保留 source_comment_ids、severity、affected claim 或 evidence gap
