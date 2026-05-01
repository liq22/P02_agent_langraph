---
name: P4_07_再投稿打包_node_sop
description: Ordered operating procedure for `research/P4_论文回复_response/P4_07_再投稿打包`.
  Use only for execution-tier nodes after `skills/SKILL.md`.
---

# P4_07_再投稿打包 SOP

This SOP applies to `research/P4_论文回复_response/P4_07_再投稿打包`.

## Read Order
1. README.md
2. status.yaml
3. skills/local_entry.md
4. prompts/research_prompt.md
5. prompts/acceptance_checklist.yaml
6. skills/SKILL.md
7. prompts/review_rubric.yaml
8. ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
9. ../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex
10. ../P4_06_修改证据/artifacts/revision_evidence_map.yaml
11. artifacts/evidence_registry.yaml
12. artifacts/submission_metadata.yaml
13. ../../P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml
14. ../../P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml
15. ../../P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml
16. artifacts/figures/
17. artifacts/tables/
18. skills/local_execution.md

## Preflight
- 确认 `skills/local_entry.md` 已经选择了当前 execution-tier 路径。
- 确认 `prompts/acceptance_checklist.yaml` 可用，并且将作为唯一完成定义门槛。
- 确认默认必需的本地工作输入已存在：`../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex`, `../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex`, `../P4_06_修改证据/artifacts/revision_evidence_map.yaml`, `artifacts/evidence_registry.yaml`, `artifacts/submission_metadata.yaml`, `../../P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml`, `../../P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml`, `../../P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`, `artifacts/figures/`, `artifacts/tables/`。
- 确认 `skills/local_execution.md` 与其 declared required inputs 已可用。

## Operating Procedure
1. 只读取 Read Order 中列出的文件，并把本轮限制在一个 bounded round 内。
2. 确认当前状态、阻塞项和 contract / inputs readiness，不在 scope 不清时继续深推。
3. 更新当前 binder 或 local action 路径负责的 node-local artifacts，不扩张到其他节点。
4. 重新对照 `prompts/acceptance_checklist.yaml` 记录 handoff 或 stop reason，不制造假推进。

## Stop Rules
- 缺关键输入或关键证据
- 本节点范围不清或越出节点职责
- 必须依赖的上游节点尚未就绪
- 缺少独立 reviewer verdict (`review/verdict.yaml`)
- 独立 reviewer verdict 尚未完成 (`review_complete != true`)
- 独立 reviewer 判定为 `revise` 或 `block`
- 独立 reviewer 提出 hard fail 且未关闭
- hard gate 缺 citation/figure/venue/coverage/revision evidence 中的适用工件。
- blocking issue 没有 claim_id/evidence_id/location/actionable_fix。

## Delegate Notes
- Default path: delegate to local execution `local_execution`.
- This node binds local execution; enter `skills/local_execution.md` only after the tier-required local stack has been loaded.
