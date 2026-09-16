# Paper 2 — Theory and Contribution Plan

## 1. Gap

ReAct、Reflexion、StateFlow 已经研究 action-observation、feedback/memory 和 state-driven workflow；PHMForge 已研究 PHM tool orchestration。因此“使用 graph / LangGraph / state machine”本身不是创新。真正缺口是：**显式状态提示和动作可见性约束在 PHM 长程任务中分别起什么作用，限制工具时是否会删掉高价值分析。**

## 2. Research question

固定 model、PHM knowledge、released observations、global tools、budget 与 evaluator，研究：

1. current-state cue 是否改善 policy choice？
2. state-dependent tool filter 是否帮助有限模型，还是造成 action loss？
3. graph 控制的收益是否依赖 sequence length、budget 与 public information changes？

## 3. Candidate theoretical contributions

### T1 — Mask loss and within-mask selection loss

设全局可行动作为 \(\mathcal A(s)\)，Graph 保留非空子集 \(\mathcal A_g(s)\)。以 unrestricted optimum \(V_t^*,Q_t^*\) 定义：

\[
\ell_t^{\mathrm{mask}}(s)=V_t^*(s)-\max_{a\in\mathcal A_g(s)}Q_t^*(s,a),
\]
\[
\ell_t^{\mathrm{select}}(s,a)=\max_{u\in\mathcal A_g(s)}Q_t^*(s,u)-Q_t^*(s,a).
\]

有限 horizon 下：

\[
V_0^*(s_0)-V_0^\pi(s_0)=
\mathbb E_\pi\sum_t
[\ell_t^{\mathrm{mask}}(s_t)+\ell_t^{\mathrm{select}}(s_t,a_t)].
\]

证明由两项相加得到 \(V_t^*-Q_t^*\)，再用 Bellman 关系 telescoping。Bellman 分析不是原创；候选贡献在于它如何约束 PHM graph control 的解释和实验。真实 PHM 中 \(Q^*\) 未知，因此不能用 invalid-call rate 冒充 regret。

### T2 — Lossless masking condition

若每个可达状态的 \(\mathcal A_g(s)\) 都保留至少一个 unrestricted optimal action，则最优 masked policy 与 unrestricted optimal value 相同。反之，mask 可能产生不可恢复 value loss。该命题用于设计 harmful-mask counterexample，不保证真实 LLM 最优。

### T3 — Inert ablation condition

若两个条件在所有可达 history 上给出相同 conditional action distribution，且 Environment 相同，则完整 rollout distribution 相同。因而不改变 state cue/tool exposure 的 ablation 不能识别该机制。当前 no-memory 在 base profile 上必须先做 activity check。

### T4 — Exact-renormalization filtering identity（辅助）

若 baseline distribution 对有用 action 的质量为 \(p\)，mask 对 useful/non-useful action 的保留率为 \(g,b\)，且过滤等价于条件化，则：

\[
q(U\mid A)-p=\frac{p(1-p)(g-b)}{pg+(1-p)b}.
\]

真实 LLM schema change 未必是 exact renormalization；该式只解释为何“工具更少”不必然更好。

## 4. Abstract semantic units

1. 长 PHM rollout 需要控制多步工具选择，但动作约束可能删除必要分析。
2. 现有 state/workflow prior 已存在，因此研究 state cue 与 tool visibility 的实际作用。
3. 将 control loss 分成 mask loss 和 within-mask selection loss。
4. 用 cue × filter 四格分离两个 provider-visible 干预。
5. 检查 inactive ablation 与 harmful mask，避免把 workflow 节点当 reasoning 证据。
6. 在 matched replay/task/budget 下测试 task performance、completion 与 cost。
7. 只在真实结果完成后填写收益/失效范围。

## 5. Introduction paragraph plan

- **I1 长程科学决策**：PHM 是持续测量—分析—提交，而非单标签流程图。
- **I2 Agent prior**：ReAct、Reflexion、AgentBench 已有多步 action/history。
- **I3 direct graph prior**：StateFlow 已有 state-driven workflow；Graph 表示不是 gap。
- **I4 PHM prior**：PHMForge 已有 tool orchestration；真正问题是 action restriction 的价值和损失。
- **I5 理论 trade-off**：mask loss vs selection loss；工具更少不等于更优。
- **I6 identification**：cue/filter 四格、same model/data/tools/budget；先确认 ablation active。
- **I7 contributions**：C1 loss analysis、C2 component attribution、C3 applicability boundary，全部映射实验。

## 6. Method plan

### M1 Base graph
准确列出现有 reachable states、state cue 和 tool visibility；不把 node name 当 diagnosis belief。

### M2 Component interventions
四格统一处理历史 `decision_state` 暴露；internal graph computation 可以产生 mask，但 provider-visible state cue 与 filter 分开。

### M3 Control-loss theory
小型 finite decision model 中精确计算 \(Q^*\) 验证 T1/T2；真实任务只用受控 ablation 与可审查 lost-action case。

### M4 Ablation activity
正式大 cohort 前，在开发 histories 上比较 state/tool exposure。若 no-memory 与 full 行为一致，标记 inactive。

### M5 Sequence and dynamic information
现有 `horizon` 同时改变均匀取样和比例预算，只作 sensitivity。纯 horizon 需固定 longest sequence 的 nested prefix，并明确 fixed-total / per-window budget。dynamic public event 是外生工况信息，不是信号推断 onset。

### M6 Statistics
资产配对、所有 terminal outcomes 保留；task metric primary，state transitions/repetition/cost 作为解释性量。

## 7. Experiments / ablations / baselines

- **Main**：original Generic vs original Graph。
- **Factorial**：reactive/state/filter/both。
- **Ablation**：no-memory 仅在 activity check 通过后；dynamic no-revision/no-branch/no-replanning 使用相同 public event。
- **Harmful mask toy**：known finite value model，验证 decomposition，不是 PHM result。
- **Baselines**：Generic、Scripted、原 Graph、四组件条件。
- **Agent comparator**：StateFlow/Reflexion 只有按其实际状态/反馈机制复现并计算额外 calls 后才进入表格；不能简单改 prompt 名称。
- **Numeric controls**：由 Benchmark 统一提供，只用于数值 ceiling，不是 Graph policy competitor。

## 8. Claim gates

- C1：理论假设与 finite toy 检查成立；真实任务不伪造 \(Q^*\)。
- C2：四格 provider-visible intervention 确实不同且 matched。
- C3：长程/revision 结论分别具有 nested-prefix 或真实 public-event 支撑。

未达到 gate 时，摘要只写“we formulate / we decompose / we evaluate”。
