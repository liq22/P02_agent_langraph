# Paper 2 → Benchmark 映射

所有命令在 liq22/phm-agent-benchmark 执行：`python main.py --config <path>`。默认 plan；--override command=run 执行，command=finish 统计绘图。下列 G-* 是本轮配置映射名，不重新编号或重标历史 P2-E* 实验。

| 映射 | 问题／estimand | 处理与控制 | Benchmark module/config | 证据／claim |
|---|---|---|---|---|
| G-main | 联合 G 效应，逐任务Δ_G | Generic vs 原cue+filter | src/phm_graph_agent/{agent,state}.py；configs/paper02_graph/main.yaml | 同K/M/观测/工具/预算；不是纯topology效果 |
| G-components | cue、filter及交互 | 四格，历史提示处理一致 | components.py；components.yaml | 四格matched结果；不用旧Generic代替组件control |
| G-memory | persistence是否改变行为 | graph vs graph-no-memory | state.py；memory.yaml | 先确认可达状态下消融生效 |
| G-horizon | 长度与资源联合敏感性 | 不同窗口数 | horizon.yaml | 当前选样与预算同时变化，非pure horizon |
| G-dynamic | 显式工况变化后的修正 | 相同公开事件的匹配控制 | 状态规则已迁入；统一assignment/event/config dispatch尚缺 | 不复活旧dynamic_runtime独立Runner |
| G-extension | nested-prefix/跨数据/reliability | 匹配条件与固定控制 | 部分公共统计可复用；正式整合未完成 | Mock状态覆盖不能替代任务结果 |

Required artifacts：Benchmark六文件attempt、公共统计CSV、figure source。本仓只登记路径、实验解释和claim mapping。base六状态与dynamic Monitor/Revise分开；公共工况事件不是从信号推断的故障起始。

迁移没有产生新处理效应。历史来源见SOURCE_HISTORY.md，不将旧结果重新标成新组件实验。
