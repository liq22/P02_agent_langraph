# P4_04 正式回复 TeX 导出说明

## 目标
本节点把正式回复模板同步为 node-local TeX 导出骨架，主输出为 `artifacts/response_letter.tex`。

## 当前结论
当前只完成正式回复文档的可编译骨架，不是可提交的最终 response letter。模板已经给出 Advanced Engineering Informatics 风格的标题页、cover letter、Reviewer 1-3 逐点回复结构和 `reviewresponse.sty` 样式；本轮将这些内容落到 `artifacts/`，作为后续填充官方审稿意见和逐条回复的工作区。

尚未关闭的输入缺口：

- 缺 official manuscript ID。
- 缺 decision type。
- 缺 editor name。
- 缺官方 reviewer comments 原文。
- 缺逐条 direct answer。
- 缺 revised manuscript 的 page/section/figure/table change location。
- 缺每条回复对应的 evidence refs 和 revision provenance。
- 匿名化要求尚未由投稿系统确认。

## 导出目标
`artifacts/response_letter.tex` 是本节点当前正式 TeX 导出入口。该文件依赖同目录下的 `reviewresponse.sty` 和 `Reviewers/*.tex`，不依赖 `templates/` 作为运行时输入。

## 验收口径
本轮只满足“模板骨架已建立、缺口已显式记录、TeX 可编译”。它不满足“正式回复已完成”“所有 comment 已响应”“独立 review pass”或“可以进入 fix”。

## 下一步
- [ ] 填入 manuscript ID、decision type、editor name。
- [ ] 将官方 reviewer comments 原文逐条放入 `revcomment`。
- [ ] 为每条 `revresponse` 补 direct answer、evidence refs、manuscript location、commitment status。
- [ ] 用 revised manuscript 和 revision evidence map 核对每个承诺。
- [ ] 请求独立 reviewer 生成 `review/verdict.yaml`。
