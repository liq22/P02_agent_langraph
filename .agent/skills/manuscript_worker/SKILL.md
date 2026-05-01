---
name: manuscript_worker
description: Advance one selected manuscript node with one bounded drafting, revision, or normalization step. Use for P2 nodes after routing, without widening into repo-global writing orchestration.
---

# Manuscript Worker

## 使用时机
- 目标 node 属于 P2
- 需要撰写、改写、压缩、结构化或规范化本 node 文稿
- 任务范围能在单个 node 内闭合

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时 `docs/manuscript.md`
- 若存在 `prompts/research_prompt.md` 或最近上级 `prompts/standards.md`，读取其中的 P2 manuscript 标准

## Workflow
1. 确认本轮只改一个局部写作目标。
2. 读最小需要的本地正文。
3. 先检查本段的 one-sentence contribution、IMRAD role、claim-evidence 对齐和 skim-reader path。
4. 检查 citation gate：支撑 claim 的引用必须可验证；未验证引用应转交 `citation_verifier`、改成占位或阻断 handoff。
5. 检查 figure-callout 逻辑：正文提到的 figure/table 必须有 claim、evidence source、caption obligation 或明确缺口。
6. 完成一个受控写作增量：起草、重写、压缩、对齐结构或术语。
7. 删除或标记 research debt：含糊抽象、无证据 claim、未验证引用、术语漂移、过度 claim、缺失 limitation。
8. 把变化限制在当前 node 及其声明的本地产物。
9. 更新状态并返回。

## 产出
- `docs/manuscript.md` 或 node-local 导出目标的增量
- 本地状态更新

## 边界
- 不接管整个论文
- 不代替 response / review worker
- 不刷新 graph

## stop_with
- 需要外部未准备好的结果或图表
- 本轮需要跨多个 node 同步改写
- 任务超出当前 node scope
- claim 没有证据或引用仍未验证
- Figure callout 没有 provenance、claim_ref 或 evidence_ref
