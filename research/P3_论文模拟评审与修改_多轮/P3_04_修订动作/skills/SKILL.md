---
name: P3_04_修订动作_node_skill
description: Node-local strategy skill for `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P3_04_修订动作 Node Skill

This node-local skill applies to `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作`.

## Node Context
- phase: `P3`
- node_kind: `leaf`
- node_mode: `standard`
- node_profile: `hard_gate`
- execution_profile: `<none>`
- purpose: 把批评摘要转成可执行修订动作图，而不是泛化成任意 revision 任务。

## Use When
- 当前节点负责 review、critique、blocking issue 发现或 revision planning。
- 需要把问题转成当前节点内可执行、可验证的修订动作。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 读取最小必要的 critique/review 输入，把问题原子化为 issue、severity、evidence location 和 proposed action。
- 把评论压成 digest、review round plan 或 revision action map。
- 只交付当前节点内的 critique/revision 工件，不把 review 扩成 repo-global loop。
- Researcher lens: adversarial external reviewer.
- Node profile: hard_gate.
- 像严苛审稿人一样主动寻找 overclaiming、missing controls、citation mismatch 和替代解释。
- Review 的价值不在语气，而在能否定位缺口、严重度和可执行修订。
- 作者辩护不能替代独立评审判断。
- 核心 claim 是否被证据充分支持？
- 方法、数据、统计和复现路径是否足以通过外部审查？
- 是否存在 selective reporting、p-hacking、cherry-picking 或隐藏负结果？
- 每个 blocking issue 是否有具体 evidence location 和 proposed action？
- 像独立审稿人一样用 source isolation、severity、evidence location、affected claim 和 actionable fix 约束批评。
- Keep the round in planning / mapping / writing space; do not invent execution-only procedure here.

## Local Routing / Delegate Contract
- Default path: delegate to canonical worker `structured_map_builder`.

## Boundaries
- 不把作者辩护当成独立评审结论。
- 不把当前 review 节点扩成多节点总 review engine。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
