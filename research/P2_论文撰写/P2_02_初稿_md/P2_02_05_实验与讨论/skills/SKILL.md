---
name: P2_02_05_实验与讨论_node_skill
description: Node-local strategy skill for `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论`.
  Use only when this node's tier requires `skills/SKILL.md`.
---

# P2_02_05_实验与讨论 Node Skill

This node-local skill applies to `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论`.

## Node Context
- phase: `P2`
- node_kind: `leaf`
- node_mode: `standard`
- node_profile: `evidence_leaf`
- execution_profile: `<none>`
- purpose: 推进实验与讨论写作，并在必要时先做 claim-result 对齐。

## Use When
- 当前节点负责论文写作、章节起草、结构化改写、形式检查或导出同步。
- 需要把 claim、evidence、术语与版式要求压到当前节点的正文或导出目标里。

## Strategy Delta
- Treat `prompts/acceptance_checklist.yaml` as the only done-state truth; this skill only adds node-local strategy beyond the prompt assets.
- 先确认本段 one-sentence contribution、claim-evidence 对齐和 skim-reader path。
- 完成一次受控写作增量：起草、重写、压缩、格式检查或导出同步。
- 把结果限制在当前章节、图表、导出资产或形式检查报告，不扩成整篇论文总控。
- Researcher lens: top-conference paper author.
- Node profile: evidence_leaf.
- 像顶会论文作者一样先建立一句话贡献，再组织段落、实验和图。
- 论文不是实验集合；每个段落、图和表都必须服务一个明确 claim。
- 写作应使用完整学术段落，不能用 bullet 堆成初稿。
- 本节是否清楚回答 What、Why、So What？
- 每个 claim 是否能追到结果、方法细节、图表或 verified citation？
- Figure 1 或关键图是否能让 skim reader 抓住贡献和证据路径？
- limitations 是否诚实约束了 claim 强度？
- 像顶会作者一样维护 one-sentence contribution、claim/evidence ID、citation/figure/venue linkage 和 limitations。
- Enforce one-sentence contribution before drafting prose.
- Check IMRAD role, skim-reader path, verified citations, figure callouts, and limitations.
- Convert unsupported claims into placeholders or research debt instead of polishing them.
- Check overclaiming, negative results, alternative explanations, statistical validity, and missing evidence.
- Separate supported, unsupported, and unclear claims before writing or figure finalization.
- Keep the round in planning / mapping / writing space; do not invent execution-only procedure here.

## Local Routing / Delegate Contract
- Default path: delegate to canonical worker `manuscript_worker`.
- When `结果与 claim 尚未对齐`, delegate to canonical worker `result_to_claim`.
- When `已有清晰 claim-result 对齐`, keep_default_delegate.

## Boundaries
- 不把当前节点扩成整篇论文统一重写器。
- 不在无证据时维持核心 claim。
- When this file and the prompt assets differ, the prompt assets win on goal and done-state.
- Do not restate checklist inputs, outputs, or stop conditions in this layer.
