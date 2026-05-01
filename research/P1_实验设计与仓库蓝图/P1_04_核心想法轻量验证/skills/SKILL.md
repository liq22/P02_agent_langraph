---
name: P1_04_核心想法轻量验证_node_skill
description: Node-local strategy skill for `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P1_04_核心想法轻量验证 Node Skill

This node-local skill applies to `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证`.

## Node Context
- phase: `P1`
- node_kind: `leaf`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `experiment_execution`
- purpose: 在本节点内推进一轮有界轻量验证；若 contract 未就绪则先补齐 handoff。

## Use When
- 当前节点负责基于显式 execution contract 执行一轮有界轻量验证。
- 需要把 baseline、单变量尝试、keep/discard 结论写回本地实验账本。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 把 `artifacts/execution_contract.yaml` 当作唯一 execution gate；若缺失或 `contract_mode != executable`，只允许转交 contract-prep。
- `skills/local_wrapper.md` 只绑定本地 IO，然后委托给 `auto_experiment_worker`。
- `auto_experiment_worker` 仍是唯一 active runtime experiment worker；不要在 node-local 层重新发明实验循环。
- 本地实验工件路径固定为 `artifacts/auto_experiment/results.tsv` 与 `logs/auto_experiment/latest_run.log`。
- Researcher lens: experiment lead.
- Node profile: hard_gate.
- 像实验负责人一样先问“这个实验能支持或推翻哪个 claim”。
- baseline、ablation、metric 和 failure mode 必须在执行前定义，不能结果出来后补故事。
- 实验协议要能让另一个 agent 或 reviewer 复现关键路径。
- 当前 protocol 是否足以区分方法有效、数据偶然、实现偏差和 metric 偏差？
- baseline 是否是 reviewer 会认可的强基线，而不是方便基线？
- 失败结果应如何解释，哪些失败会要求收缩 claim？
- 当前 artifact 是否足以让下游写作引用或复查？
- 只在 review/submission/venue/response gate 阶段 hard block；authoring 阶段只能报告缺口。
- hard fail 必须带 claim_id/evidence_id/location/actionable_fix，否则降级为 advisory critique。
- Use `skills/SOP.md` as the only ordered procedure; do not restate checklist gates in this layer.
- If a wrapper path is selected, treat `skills/local_wrapper.md` as an IO binder rather than a second semantic layer.

## Local Routing / Delegate Contract
- Default path: delegate to local wrapper `local_wrapper`.
- When `artifacts/execution_contract.yaml 缺失`, delegate to canonical worker `experiment_design_or_execution`.
- When `contract_mode != executable 或 contract 不完整`, delegate to canonical worker `experiment_design_or_execution`.
- When `contract_mode == executable 且 contract 完整`, keep_default_delegate.
- This node binds a local wrapper; enter `skills/local_wrapper.md` only after the tier-required local stack has been loaded.

## Boundaries
- 不在无 executable contract 时直接进入实验执行。
- 不把本节点扩成 repo-global experiment orchestrator。
- 不更改实验主工件路径，也不引入第二个 runtime experiment worker。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
