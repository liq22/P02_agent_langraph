---
name: P1_05_初步验证结果整理_node_skill
description: Node-local strategy skill for `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P1_05_初步验证结果整理 Node Skill

This node-local skill applies to `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理`.

## Node Context
- phase: `P1`
- node_kind: `leaf`
- node_mode: `execution`
- node_profile: `result_synthesis`
- purpose: 收敛轻量验证结果，形成支持/不支持/待澄清的结论边界。

## Use When
- 当前节点负责把实验账本压缩成 result registry、hypothesis status 与 claim-safe 摘要。
- 需要判断哪些 evidence 支持、否定或仍不足以支持当前 claim。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 把 `artifacts/auto_experiment/results.tsv` 当作主输入，而不是继续等待 execution contract。
- 先写 `artifacts/result_registry.yaml` 与 `artifacts/hypothesis_status.yaml`，再决定是否补最小 paper 摘要。
- 显式区分 supported / unsupported / unclear，并把缺证据项留在当前节点内报告。
- `skills/local_execution.md` 在这里是结果收敛 binder，不是实验发射器。
- Use `skills/SOP.md` as the only ordered procedure; do not restate checklist gates in this layer.
- If a local execution path is selected, treat `skills/local_execution.md` as a bounded executor rather than a second router.

## Local Routing / Delegate Contract
- Default path: delegate to local execution `local_execution`.
- This node binds local execution; enter `skills/local_execution.md` only after the tier-required local stack has been loaded.

## Boundaries
- 不重开 baseline / experiment loop。
- 不把 execution contract 当作本节点 gate。
- 不在证据不足时抬高 claim 强度，也不把结果整理扩成全局 figure/table 管理器。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
