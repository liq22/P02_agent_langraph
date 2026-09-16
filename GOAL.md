# GOAL — persistent decision structure G

冻结 $G=\text{persistent decision structure}$。在相同模型、PHM 知识源 $K_0$、公开观测访问与释放规则、全局工具、预算和评价下，研究显式结构何时帮助长程 PHM 决策，何时限制必要行动。不同策略可以产生不同实际历史；不把观测权限匹配写成所有轨迹相同。

数学对象为 $G=(\mathcal M,m_{\mathrm{init}},\delta,c,\Gamma)$，其中 $m_t=(z_t,\nu_t)$ 同时包含分析进度和最近已消费事件标识。提示 $c$ 包含当前阶段标签与指令；$\Gamma$ 控制可见工具。它不是完整故障信念状态，也不是单独的 topology treatment。

保留 mask/select 损失及条件性价值分析。真实 PHM 的 $Q^*$ 未知，状态访问、transition validity、invalid-call rate、工具数均不能替代任务表现或真实 regret。本文不研究新的 LangGraph 平台、UI 或更多状态的系统。

执行全部位于 Benchmark `src/phm_graph_agent/` 和 `configs/paper02_graph/`，唯一 Runner、数据协议和指标不变。P02 只维护科学定义、正文、理论、参考文献、评审、出版图和 `experiment_spec`。继续当前 PR，不覆盖已提交的 Analyze/Check 同数量工具对照，也不应用较旧的本地整包。

优先级固定为 G-main → 新的 cue/filter 四格 → persistence 激活检查 → horizon/sampling/resource sensitivity → dynamic revision → repeated reliability。原 Generic 不能代替 factorial-reactive；四格历史 decision_state 处理必须一致。

无事件 base 的 memory 和 replanning 开关是无效机制消融，保留为负控，不作为下一项效果实验。Monitor/Revise 仅属于 dynamic；base 事件输入直接拒绝。未来 dynamic-history-matched 队列对全部动态条件清理历史状态字段；旧 full-dynamic 输入不等价，不能重标或混用。

当前切片在 theory07 和正文中完成递归 G 定义、无效消融证明、输入干预边界。Benchmark 中修复 base 事件越界和动态历史提示不对称，并增加原生输入合同测试。本轮已由 GitHub Actions run 35110539101 完成真实依赖安装、pip check 和 83 项原生研究测试，其中包含全部 11 项新增 Graph 检查。未产生新的 PHM matched result；83 项不是完整仓库测试或迁移行为的穷尽验收。

本地唯一下一入口：Benchmark `paper/goals/P02_MATCHED_CONTROL.md`。复用已通过的原生 CI 证据，确认本地环境后，用真实开发 assignment 和批准的 provider/model 运行 G-main 与四格。任务指标是 primary，过程与成本是 secondary。八卡仅用于实际训练或本地大模型，不把 API rollout 写成 GPU 实验。

正文唯一入口 `paper/draft/main.md`；真实结果进入 7.4，之后再将 G 的任务、可靠性与成本发现反馈给 Paper 0。两个迁移 PR 在真实入口验收前保持 Draft；先 Benchmark 后 P02 正常合入 dev，不修改 master，不强推。
