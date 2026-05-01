---
name: auto_review_loop
description: Advance one selected P3 node with one bounded review, critique, or revision-planning step. Use for P3 nodes after routing, without becoming a repo-wide review engine.
---

# Auto Review Loop

## 使用时机
- 目标 node 属于 P3
- 需要局部 review、critique、revision planning
- 本轮工作能在单一 review node 内闭合

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时本地 review / critique 文件
- 若存在 `prompts/research_prompt.md` 或最近上级 `prompts/standards.md`，读取其中的 P3 review 标准
- 对 P3 论文迭代节点，必须应用最近上级 `prompts/standards.md` 中的 paper iteration gate。

## Workflow
1. 确认 review 只针对当前 node。
2. 读取最小必要的 critique 或 response 证据。
3. 将 critique 原子化为 issue、severity、evidence location、affected claim、proposed action。
4. 只有同时具备 claim/evidence/location/actionable_fix 的问题才可标 hard fail；否则标为 advisory 或 major issue。
5. 记录 reviewer role、source isolation、conflict flag 和 same-author/same-worker 禁止条件。
6. 对 paper iteration gate，补充 manuscript snapshot、reviewer lens、checklist dimension、unresolved blocker 和下一轮 trigger。
7. 产出一份本地 digest、问题列表或修订建议。
8. 不把 review 扩成全 repo 循环，不直接改写 P2 正文或 P4 回复。
9. 更新本地状态并返回。

## 产出
- node-local critique / revision artifact
- 本地状态更新

## 边界
- 不选 node
- 不刷新 graph
- 不复制 review 正文到 graph
- 不把作者辩护当作独立评审

## stop_with
- review 输入不存在
- 评论来源混乱且无法在当前 node 内厘清
- 需要跨 node 聚合但本节点没有对应聚合契约
- hard fail 无法绑定 claim/evidence/location/actionable_fix
- paper iteration gate 缺 manuscript snapshot、reviewer lens 或 unresolved blocker 判定
