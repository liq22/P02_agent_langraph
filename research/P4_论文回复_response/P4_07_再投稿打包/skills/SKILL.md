---
name: P4_07_再投稿打包_node_skill
description: Node-local strategy skill for `research/P4_论文回复_response/P4_07_再投稿打包`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P4_07_再投稿打包 Node Skill

This node-local skill applies to `research/P4_论文回复_response/P4_07_再投稿打包`.

## Node Context
- phase: `P4`
- node_kind: `leaf`
- node_mode: `execution`
- node_profile: `hard_gate`
- execution_profile: `<none>`
- purpose: 执行一次有界再投稿打包检查，核对 submission bundle consistency、citation registry、figure manifest、venue requirements 并生成 bundle manifest。

## Use When
- 当前节点负责审稿意见收集、问题映射、逐点回复、证据绑定或再投稿打包。
- 需要把 comment、evidence、change location 和 response package 对齐到当前节点。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 读取 comment、mapping、evidence 与 manuscript change location，先过 coverage/provenance gate。
- 逐点生成 response、evidence map、coverage report 或 resubmission asset。
- 确保每条回复都能落到具体 comment、具体 evidence 和具体改动位置。
- Researcher lens: responsible rebuttal author.
- Node profile: hard_gate.
- 像负责任作者一样逐点回答，不逃避、不扩大承诺、不用语气替代证据。
- 每条 response 必须绑定 reviewer comment、正文改动位置和 evidence。
- 若需要改图或补引用，必须记录 revision provenance。
- 每条 reviewer concern 是否被直接覆盖？
- 回复中的每个承诺是否已反映在正文、图表、实验或 citation registry 中？
- 是否存在 evasive response、无证据承诺或未映射改动？
- submission package 是否保持 manuscript、figures、tables、evidence map 一致？
- 像负责任作者一样逐点绑定 reviewer comment、direct answer、正文位置、evidence 和 commitment status。
- Use `skills/SOP.md` as the only ordered procedure; do not restate checklist gates in this layer.
- If a local execution path is selected, treat `skills/local_execution.md` as a bounded executor rather than a second router.

## Local Routing / Delegate Contract
- Default path: delegate to local execution `local_execution`.
- This node binds local execution; enter `skills/local_execution.md` only after the tier-required local stack has been loaded.

## Boundaries
- 不承诺未批准的实验、数字、引用或改动。
- 不把局部回复节点扩成整套 submission manager。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
