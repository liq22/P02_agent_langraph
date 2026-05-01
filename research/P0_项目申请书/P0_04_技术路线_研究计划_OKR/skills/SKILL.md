---
name: P0_04_技术路线_研究计划_OKR_node_skill
description: Node-local strategy skill for `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P0_04_技术路线_研究计划_OKR Node Skill

This node-local skill applies to `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR`.

## Node Context
- phase: `P0`
- node_kind: `leaf`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`
- purpose: 把技术路线、研究计划与 OKR 对齐成可执行的局部蓝图。

## Use When
- 当前节点负责问题定义、gap 收敛、innovation 边界或约束澄清。
- 需要把背景、问题、aim、impact 或 feasibility 压成当前节点可交付、可反驳的研究判断。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 先判断问题是否真实、重要、可研究，而不是先寻找可包装的技术点。
- 把 strong prior work、未解决瓶颈、目标读者和资源约束压成可反驳的 gap。
- 只输出当前节点需要的背景、问题、aim、impact 或 feasibility 判断。
- Researcher lens: problem-formulation PI.
- Node profile: evidence_leaf.
- 像 PI 一样先问“这个问题为什么现在必须做”，再问“我们能做什么”。
- 综述不是文献堆叠；必须综合方法簇、共同假设、失败边界和未被解决的约束。
- novelty 必须相对强基线成立，不能靠换名词、换场景或扩大叙事制造。
- 当前领域的主要未解瓶颈是什么？
- 现有强方法已经解决了什么，明确没有解决什么？
- 本项目的 gap 是否足够具体，是否能被后续实验或论证反驳？
- 预期贡献是否值得一个 skeptical reviewer 继续读？
- 直接产出证据、图表、claim map 或协议的节点必须保留 claim/evidence 身份层。
- 负结果、失败解释和 keep/discard 决策是一等工件，不得被正结果叙事覆盖。
- Keep the round in planning / mapping / writing space; do not invent execution-only procedure here.

## Local Routing / Delegate Contract
- Default path: delegate to canonical worker `structured_map_builder`.

## Boundaries
- 不把想法筛选扩成无界文献检索或全局 proposal 总控。
- 不在当前节点里替代 P1/P2/P3/P4 的执行逻辑。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
