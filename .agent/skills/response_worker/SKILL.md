---
name: response_worker
description: Advance one selected P4 node with one bounded point-to-point response step. Use for response drafting, evidence binding, or revision explanation inside one response node.
---

# Response Worker

## 使用时机
- 目标 node 属于 P4
- 需要逐点回复、证据绑定或 response letter 局部推进
- 任务可以在单个 response node 内闭合

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时本地 critique / response / evidence 文件
- 若存在 `prompts/research_prompt.md` 或最近上级 `prompts/standards.md`，读取其中的 P4 response 标准

## Workflow
1. 确认本轮只处理一个 response 子目标。
2. 读取最小必要的 critique / evidence。
3. 先应用 coverage、provenance、commitment 三个 gate。
4. 生成或修正本 node 的 point-to-point response 增量。
5. 每条回复按 direct answer -> evidence refs -> manuscript location -> commitment status -> implication 组织，必要时窄化让步。
6. 不承诺未批准实验、数字、引用或改动；无法绑定 evidence/location 时写成 unresolved blocker。
7. 把修改限制在当前 node-local response 工件中。
8. 更新状态并返回。

## 产出
- response 草稿或证据说明增量
- 本地状态更新

## 边界
- 不聚合整个 rebuttal 包
- 不刷新 graph
- 不扩成 manuscript worker

## stop_with
- 缺 critique 输入
- 缺 revision evidence
- 需要承诺未批准实验、数字、引用或修改
- 需要跨多个 response node 统一改动
- 回复缺 direct_answer、evidence_refs、manuscript_location 或 commitment_status
