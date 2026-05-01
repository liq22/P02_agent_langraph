---
name: leaf_node_writer
description: Write or refine one selected leaf node with one bounded local drafting step. Use for lightweight node-local content work when no more specialized worker is needed.
---

# Leaf Node Writer

## 使用时机
- 当前 node 是叶子节点
- 只需要轻量文本增量
- 没有更专门的 canonical worker 更合适

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时 `docs/manuscript.md`

## Workflow
1. 确认这是一个 leaf-node 范围内的轻量写作任务。
2. 读取最小必要的本地文稿，并检查 `research_prompt.md` / checklist 中的 `node_researcher_lens`、`author_exit_if`、`node_close_if`。
3. 写入一次受控增量：只回答当前节点关键研究判断，无法验证的 claim 写成 gap。
4. 保持改动局限在当前 node，并保留 claim/evidence ID 或明确说明本节点暂不产出证据 ID。
5. 更新状态并返回。

## 产出
- node-local 文稿增量
- 本地状态更新

## 边界
- 不扩成整篇论文写作
- 不替代实验或 response worker
- 不刷新 graph

## stop_with
- 任务超出 leaf node scope
- 缺必要本地正文输入
- 作者退出条件无法满足且没有显式 gap 说明
