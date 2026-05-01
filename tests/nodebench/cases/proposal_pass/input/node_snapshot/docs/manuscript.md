# Research Content and Innovation

## Problem Boundary

本节点的问题边界是：现有研究流程可以生成长文本，但缺少把研究内容、工程问题、证据链和失败条件绑定到同一节点任务的机制。该问题直接影响 proposal 写作，因为评审需要快速判断每个研究内容是否有清晰假设、可执行技术路线、可复核证据和可接受风险。已有自动化工具通常关注生成速度，本 fixture 只验证节点级验收结构，不声称覆盖真实科学质量。

## Hypothesis and Route

核心假设是：如果每个研究内容都绑定技术路线、验证指标和失败风险，那么 proposal 节点会更容易被审计 [@nodebenchProposal]。技术路线分三步：先列出研究内容，再把每条内容映射到问题和证据，最后记录失败条件与下一步动作。实验型证据可来自最小 benchmark、审稿清单覆盖率和人类 gate 记录 [@nodebenchProposal]。

## Evidence and Risk

本节点表明，结构化 proposal 产物可以减少遗漏，因为问题、假设、证据和风险在同一节中显式出现 [@nodebenchProposal]；该判断只由 NodeBench fixture 检查，不代表真实论文结论。风险边界是：如果没有人工确认、没有引用或没有真实实验数据，该节点只能进入 review，不能进入 done。下一步是把该结构应用到真实 P0 节点，并让 reviewer 依据清单检查缺口。

## Reference

[@nodebenchProposal] NodeBench proposal fixture.
