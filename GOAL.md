# GOAL — 决策结构 G 的作用与失效边界

## Scientific problem
在相同 PHM 知识、模型、观测序列、全局工具、预算和评价下，显式控制何时改善长程任务，何时排除必要行动？本论文先于 Benchmark 综合论文收敛；使用共享环境，但不依赖 Skills 处理组。

## Research object
研究公开历史导出的状态、当前状态提示和工具可见性约束如何改变轨迹与任务结果。当前状态主要表示分析进度，不等于故障信念推理。base 只有六个可达状态；Monitor/Revise 需要单独公开工况事件，不能表述为从信号自主检测故障起始。

## Mathematical object
$G=(V,E,s_0,\phi,\psi)$；比较 $\pi_{M,H,K_0,G_0}$ 与 $\pi_{M,H,K_0,G}$。当前联合干预包含 state cue 和 action visibility。四格实验分离二者的输出机制，不自动识别纯 topology 效果。

在有限时域、包含历史／时间／预算的状态下，令 $A_G(s)$ 为保留动作，
$$
\ell_t^{mask}(s)=V_t^*(s)-\max_{a\in A_G(s)}Q_t^*(s,a),\quad
\ell_t^{select}(s,a)=\max_{u\in A_G(s)}Q_t^*(s,u)-Q_t^*(s,a).
$$
沿轨迹两项损失和刻画相对不受限最优策略的价值差。真实 PHM 的 $Q^*$ 未知，invalid-call rate 不能冒充 regret。

## Hypothesis
有用控制应减少集合内错误选择，同时不大量删除必要行动。cue、filter 及其交互可能有益、无效或有害，必须用任务表现检验。若消融在可达历史上不改变动作分布，零差异不能解释为对应机制无用。

## Implementation mapping
唯一代码在 `liq22/phm-agent-benchmark::src/phm_graph_agent/{agent,state,components}.py`，配置在 `configs/paper02_graph/`；共享执行、评价、解析和绘图均由 Benchmark 提供。本仓只维护数学定义、假设、正文、实验规范及 `experiment_spec/MAPPING.md`，不保留独立 graph runtime 或执行脚本。

## Estimand
逐任务主对比 $\Delta_{G,q}=M_q(\{\tau^G_{i,r}\})-M_q(\{\tau^0_{i,r}\})$。组件实验另估计 cue、filter 和 $\mu_{11}-\mu_{10}-\mu_{01}+\mu_{00}$，四格采用相同历史状态字段可见性。资产为聚类单位，多次运行不等于新资产。

## Experiment
先整理控制 Method、原 Generic 对照与 cue/filter 四格，检查 no-memory 是否改变行为，再研究长度、成本和公开工况修正。当前 horizon 同时改变选样与比例预算，只支持联合敏感性；嵌套前缀和 dynamic 正式执行须在 Benchmark 接入同一 Runner，不在本仓恢复旧链。

## Evidence
Benchmark 六文件 attempt 是唯一运行事实来源；状态统计、CSV、图表均为派生结果。本仓登记 experiment ID、config、artifact location、图表与主张。没有可靠事件标注时不报告 event-F1／detection delay；Mock 状态覆盖不支持真实任务收益。

## Claim
贡献是控制的任务后果、cue/filter 区分与适用条件，不是用了 LangGraph、更多状态或更高 transition validity。未有匹配结果时不声明收益；正、零、负结论都限定到实际干预。唯一正文为 `paper/draft/main.md`；Benchmark 随后综合 G 与 K 干预的测量含义。
