# GraphDecisionAgent — dev research

`dev` 是本仓库正文、文献、理论、图表、实验支撑及 PR 集成的唯一核心开发分支，也是 GitHub 默认入口。`main`/`master` 保留稳定快照。

入口：[Goal](paper/GOAL.md) · [正文](paper/draft/main.md) · [研究规格](paper/RESEARCH.md) · [实验](experiments/README.md) · [当前状态](obsidian/log/LOCAL_AGENT_STATE.md)。

方法仓库只依赖 Benchmark，不要求安装另一方法仓库。通过 `PHM_BENCHMARK_ROOT` 显式指定兼容的 Benchmark checkout。

从最新 `dev` 创建 `feature/*`、`review/*`、`figure/*`、`experiment/*` 或 `agent/*`，每次围绕一个可审阅改动，检查通过后 PR 回 `dev`。按科学逻辑和证据吸收增量，不按分支日期覆盖正文。

冻结协议、结果与工作树保留原条件。旧材料可从 `archive/2026-09-15/pre-convergence` 标签恢复。论文主入口保持 Markdown；Git 整合不代表完成尚缺的处理效应实验。

下一步：在相同历史上核对 cue/filter 四格的实际消息与工具集合，再选择保留开发资产的配对单元。
