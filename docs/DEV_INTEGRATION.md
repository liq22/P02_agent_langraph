# dev integration — 2026-09-15

本次收敛对象是三篇原创研究论文。`dev` 是本仓库唯一核心开发分支；正文入口为 [main.md](../paper/draft/main.md)。按内容和证据择优 PATCH，没有机械合并分支树。

审查基线为刷新后的 `origin/dev`。三仓开放 PR 均为空；已合并的 Benchmark PR #18、Skills PR #2 与 Graph PR #2 的有效内容保留。用户提供的 Benchmark PR #19 当前返回 404，未推断其状态。branch-only commit 数可能包含 squash 前历史，不代表待合入工作量。

| Branch/ref | Branch-only commits | Decision | Reason |
|---|---:|---|---|
| `refs/heads/codex/p2-pr2-rebase-20260903` | 8 | MERGE/PATCH | 吸收核实的直接相关文献；联合调度草稿、未执行结果声明与重复流程不进入新研究条件。 |
| `refs/heads/feat/paper2-active-formal-20260903` | 1 | KEEP (dev baseline) | 成熟正文、冻结协议和结果已在 dev；不重复 merge。冻结工作树保留原条件。 |
| `refs/remotes/origin/agent/graphdecision-benchmark-adapter-v0-20260812` | 3 | DROP | 旧迁移、模板、路线图或已取代实现；未优于 dev 的论文状态，保存分支标签供追溯。 |
| `refs/remotes/origin/docs/core-authority-convergence` | 4 | DROP | 旧迁移、模板、路线图或已取代实现；未优于 dev 的论文状态，保存分支标签供追溯。 |
| `refs/remotes/origin/feat/paper2-active-formal-20260903` | 5 | KEEP (dev baseline) | 成熟正文、冻结协议和结果已在 dev；不重复 merge。冻结工作树保留原条件。 |

## Content decisions

工具集合损失／集合内选择损失连接独立 cue/filter 四格；补入 StateAct 状态提示先例。保留 base-v6 与 dynamic-v3 的不同可达状态、注册比较与原始结果口径。新增组件实验独立于原 Graph 策略。

排除：未执行的联合调度草稿不能替换已有冻结结果；未验证的新引用、过时正文、重复 Goal、应用面板和模板工程不因日期更新而合入。原始研究材料、冻结协议、结果和复现脚本保留。冲突以当前 dev 的结果与协议为准，理论和相关工作做语义补入。

## Branch lifecycle

`archive/2026-09-15/pre-convergence` 保存原 dev。被清理的分支尖端分别保存为 `archive/2026-09-15/remote/<branch>` 和 `archive/2026-09-15/local/<branch>`；云端标签核对成功后才删除分支。main/master 保留稳定快照。Benchmark 未完成 B3 使用的冻结分支、本地有结果或未提交内容的工作树继续保留；它们不作为新论文开发入口。

新任务从最新 dev 建短分支，经相关检查后 PR 回 dev。
