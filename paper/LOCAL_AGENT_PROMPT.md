# GraphDecisionAgent 执行 Prompt

读 [DEV](../DEV.md)、[CORE](../CORE.md)、[本论文 Goal](GOAL.md) 与[滚动状态](../obsidian/log/LOCAL_AGENT_STATE.md)。从最新 `dev` 开短分支，按实质学术增量修改现有正文、实验或图表，完成后 PR 回 `dev`。

当前下一步：在相同历史上核对 cue/filter 四格的实际消息与工具集合，再选择保留开发资产的配对单元。

使用本仓库 `experiments/run.sh`，复用 Benchmark 的 DataPort、Runner、evaluator 和规范 rollout writer。先检查已有结果和最近验证，不重装环境，不重建参考 cohort。保持冻结条件与全部失败／弃答；新 provider、模型、工具、预算或策略使用新 study。在线请求须有当前任务授权与明确限额，凭据仅用环境变量。

理论与有限例子给出假设和机制边界；实际贡献由受控结果判断。保留负效应。正文逐段形成问题、方法变量、对照、观察和结论的连接。仅运行受影响检查，结束时更新滚动状态，不生成重复 Goal 或核验包。
