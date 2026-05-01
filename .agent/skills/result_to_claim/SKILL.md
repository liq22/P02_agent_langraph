---
name: result_to_claim
description: Judge what local results support, what they do not support, and what evidence is still missing. Use when one selected node needs claim-evidence alignment before writing or figure finalization.
---

# Result To Claim

## 使用时机
- 当前 node 需要 claim-evidence 对齐
- 实验结果已有一部分，但结论边界尚未清楚
- 需要决定继续补实验、收缩 claim、还是进入写作

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时本地结果、表格、图表、文稿

## Workflow
1. 确认本轮只处理当前 node 的 claim/result 对齐。
2. 读取最小必要的结果与 claim 文本。
3. 建立 claim-evidence matrix，标出 supported、unsupported、missing-evidence 与 limitation。
4. 对每条 claim 检查 overclaiming、negative result、alternative explanation、统计有效性、baseline 充分性和 citation 状态。
5. 对每条 claim 写清证据来源、最近反证/替代解释、是否需要收缩表述。
6. 输出紧凑的 claim map 或决策建议。
7. 更新状态并返回。

## 产出
- claim-evidence matrix / result decision note
- 本地状态更新

## 边界
- 不扩成新的实验循环
- 不直接改 graph
- 不替代 manuscript worker 做整段成文

## stop_with
- 没有可评估结果
- claim 目标完全不清楚
- 证据链无法追溯到本地结果或可信输入
- claim 依赖未验证 citation 或无 provenance figure 且当前节点不能修复
- 需要跨多个 node 统一裁决
