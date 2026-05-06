# P4_04 正式回复 TeX 导出说明

## 目标
本节点把可用的 P3_04 修订动作和 current-scope P4 response chain 同步到正式 response-letter TeX 目标，主输出为 `artifacts/response_letter.tex`。P4_01、P4_02、P4_03 现在分别提供 current-scope comment collection、problem mapping 和 point-by-point response draft，且已通过各自 score-only final-threshold re-review；但这些仍不是 official journal decision letter、official editor comment 或 official reviewer comments。当前 response draft 的可核对输入仍以 `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/artifacts/revision_action_map.yaml`、对应 issue register 和 P4_01-P4_03 current-scope artifacts 为边界。

## 正式格式要求
当前导出目标采用 node-local TeX response-letter package：

- `artifacts/response_letter.tex` 是入口文件。
- `artifacts/reviewresponse.sty` 提供 title page、comment box、response block 和 reviewer counter。
- `artifacts/Reviewers/cover_letter.tex` 记录 cover letter、metadata state、scope boundary 和 unresolved gates。
- `artifacts/Reviewers/R1.tex`、`R2.tex`、`R3.tex` 分别承载 formal-evidence、reproducibility、coverage/prose/figure/style 三类 response sections。

该格式可以表达逐点回复、证据引用、修改位置和承诺状态。当前文件是正式 TeX 草案包，不是最终投稿回复。

## 匿名化、编号与导出格式
匿名化要求尚未由投稿系统确认，因此 `response_letter.tex` 使用 `Author block withheld until journal anonymity rule is confirmed`。编号由 `reviewresponse.sty` 自动生成 reviewer/comment counters；每个 response block 同时保留 P3 action id、issue id、evidence id、target node 和 validation gate，避免仅依赖版面编号。导出格式为 TeX；本节点不声称已经生成投稿系统认可的 PDF 或 DOC 包。

## 当前结论
本轮将旧的空模板升级为 P3_04 action-driven formal response draft：

- `action-p3-001` 至 `action-p3-003` 被写入 response letter，并明确为 submission-blocking unresolved actions。
- `action-p3-004` 至 `action-p3-006` 被写入 response letter，并明确为 planned non-blocking/cosmetic actions with no claim upgrade。
- 每条 response 都给出 direct answer、current commitment status、target change location、evidence refs 和 validation gate。
- 未完成实验、未完成 manuscript revision、未锁定 selected backend、未通过 final validator 的内容均不写成已经解决。

## 仍保留的 submission blockers
- P4_01/P4_02/P4_03 已形成 current-scope comment collection、mapping matrix 和 point-by-point response draft，但它们没有也不能替代 official journal comments。
- official manuscript ID、decision type、editor name 和 journal anonymity rule 未锁定。
- P3_04 三个 blocking actions 仍依赖 P1/P4 下游证据与 coverage closure。
- P2 TeX wording、figure/caption 和 style compression actions 仍是 planned，不是已应用 diff。
- full submission validation 仍失败：当前 gate 仍有 109 个 P1 checklist pending fields、4 个 P4 score blockers（P4_04-P4_07）和 6 个 P3_04 blocked/planned action statuses，不能进入 resubmission-ready claim。

## Final-Threshold Score Boundary
本节点的 final-threshold re-review 只评价 P4_04 是否提供可编译、可追踪、边界清楚的 formal response TeX draft。AI_002 若通过，只能清除 P4_04 的节点内 formal-response-draft score blocker；不得声称 official metadata/comments 已获得、P3_04 actions 已关闭、P1 checklist 已关闭、P4_05/P4_06 coverage/evidence 已完成或全局 submission-ready validator 已通过。

## 验收口径
本节点可作为 formal response export draft 关闭：格式、编号、匿名化边界、issue/action coverage、source-comment traceability、evidence traceability、change-location target 和 unsupported-commitment guardrail 都已显式记录。它不满足 final submission readiness，也不关闭 P3_04 保留的 blocked/planned actions。

## 下一步
- P4_05 覆盖检查需逐条核对 `action-p3-001` 至 `action-p3-006`。
- P4_06 修改证据需为实际 manuscript diffs、formal evidence rows 或 retained blocker language 建立 evidence map。
- P4_07 再投稿打包前必须替换 official metadata，并确认 journal anonymity/export requirements。
