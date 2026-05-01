---
name: draft_export_sync
description: Synchronize one selected node's draft into a declared export target such as tex, doc, or package manifest. Use for bounded local export preparation, not for full submission orchestration.
---

# Draft Export Sync

## 使用时机
- 当前 node 明确需要 tex/doc/export 形式同步
- 输入和输出边界已经由 local entry 或 wrapper 绑定
- 任务不需要统筹整个 submission pipeline

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 已声明的本地 draft 输入与 export 目标

## Workflow
1. 确认 export 目标只属于当前 node。
2. 读取声明好的输入草稿；若节点处在 export/submission gate，同时读取适用的 citation registry、figure manifest、venue requirements、claim/evidence registry。
3. 执行一次 bounded sync，生成 export 目标或 delta 说明；不得改变科学 claim、证据 ID、citation key 或 figure callout 语义。
4. 在 authoring 阶段把缺失 registry 记为 gap；只有 export/submission stage 才把适用 registry 缺失作为 hard stop。
5. 写回本地导出工件并返回。

## 产出
- tex/doc/export 目标或 sync delta
- 本地状态更新

## 边界
- 不编排整套投稿流程
- 不刷新 graph
- 不改无关 node 的导出状态

## stop_with
- export 输入不完整
- 目标格式未声明
- 需要 repo-wide packaging
- export/submission stage 缺适用 citation/figure/venue/claim registry
