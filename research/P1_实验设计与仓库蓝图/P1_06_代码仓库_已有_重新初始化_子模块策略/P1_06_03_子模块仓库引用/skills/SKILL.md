---
name: P1_06_03_子模块仓库引用_node_skill
description: Node-local strategy skill for `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_03_子模块仓库引用`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P1_06_03_子模块仓库引用 Node Skill

This node-local skill applies to `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_03_子模块仓库引用`.

## Node Context
- phase: `P1`
- node_kind: `leaf`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`
- purpose: 厘清子模块引用策略及其与主仓库的边界关系。

## Use When
- 当前节点负责实验设计、协议、仓库蓝图、可复现约束或执行准备。
- 需要把方法、接口、工件或 contract 组织成后续执行可用的局部资产。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 先确认 protocol、metric、baseline、artifact、failure interpretation 与 reproducibility 约束。
- 把当前节点产出的 contract、map、registry 或 execution input 压缩到本地工件。
- 只有 contract / inputs ready 时才进入 wrapper/execution；否则停在 prep / handoff。
- Researcher lens: experiment lead.
- Node profile: evidence_leaf.
- 像实验负责人一样先问“这个实验能支持或推翻哪个 claim”。
- baseline、ablation、metric 和 failure mode 必须在执行前定义，不能结果出来后补故事。
- 实验协议要能让另一个 agent 或 reviewer 复现关键路径。
- 当前 protocol 是否足以区分方法有效、数据偶然、实现偏差和 metric 偏差？
- baseline 是否是 reviewer 会认可的强基线，而不是方便基线？
- 失败结果应如何解释，哪些失败会要求收缩 claim？
- 当前 artifact 是否足以让下游写作引用或复查？
- 像实验负责人一样保护 data split、baseline、metric、variance/statistical validity、failure interpretation 和 reproducibility。
- Keep the round in planning / mapping / writing space; do not invent execution-only procedure here.

## Local Routing / Delegate Contract
- Default path: delegate to canonical worker `structured_map_builder`.

## Boundaries
- 不在 contract 未齐时直接猜 execution 行为。
- 不把当前节点扩成 repo-global experiment orchestrator。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
