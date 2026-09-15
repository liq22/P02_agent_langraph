# 本地 Agent 当前续接点

## 2026-09-15 — 三仓 dev 收敛

[Goal](../../paper/GOAL.md) · [正文](../../paper/draft/main.md) · [本次整合](../../docs/DEV_INTEGRATION.md)。本仓库 dev 是写作、实验支撑和 PR 集成入口。

本次在隔离 dev 工作树完成：理论进入已有正文、Goal 与实验归属拆分、共享 Generic 对照显式只读复用、过时模板与重复规划清理。原算法、Data Factory gitlink、注册指标、冻结结果与正文结果块保持原条件。原 checkout 中未提交工作和本地结果没有覆盖。

### 实际检查

现有 Python 环境，无安装、无在线模型请求。执行 `bash experiments/run.sh test`；Benchmark 25 项（22 项迁移测试 + 3 项对照复用），Skills 3 项，Graph 3 项。Benchmark fixtures 实测 finish 的 CSV、SVG/PDF/600-dpi PNG 出口。

`PYTHONPATH=.:tests:src:$PHM_BENCHMARK_ROOT/src python -m unittest -v test_graph_policy test_graph_manuscript_table`：旧冻结图表检查要求协议中 P01/p01 同级 Benchmark 名称，使用原注册路径别名完成检查，25 项通过。

Python 3.10 语法解析、Shell 语法、git diff --check、正文引用键与当前入口链接检查已执行。当前主稿为 Markdown；过时 TeX 模板已退役，没有可编译的现行 LaTeX 全文。新产物是各仓库 paper/ 和 experiments/，共享实现为 Benchmark src/phm_agent_benchmark/research/。未复用或生成真实 cohort；已有结果保持原地，不用本轮源码为旧结果补标签。

### 下一步

四格消息与工具集合已经离线验证；下一步确定开发资产和固定预算，取得对应推理授权后进行 cue/filter 配对实验。

### 2026-09-16 — 集成完成

三个 GitHub 默认分支均已设为 dev。本仓库已清理 3 个过时远端分支和 1 个本地分支，原生云端归档标签已核对。保留原始冻结／未提交工作树。

持久开发工作树为项目旁 `.dev-worktrees-20260915/P02_agent_langraph`；旧根目录仅用于原条件续接。当前实验入口的只读 plan 已从此工作树运行，源码 dirty 标记均为 false，没有模型、数据文件读取或新真实结果。
