# Paper 2 Literature Map — verified roles

引言必须承认 state/workflow 与多步 Agent 先例；创新不能建立在“以前没有 graph Agent”上。

| Work | Venue/source | 在本文中的作用 |
|---|---|---|
| Boiko et al., *Autonomous chemical research with large language models* | Nature, 2023 | 多步科学 Agent 与外部工具背景 |
| Bran et al., *Augmenting large language models with chemistry tools* | Nature Machine Intelligence, 2024 | 科学工具增强背景 |
| ReAct | ICLR, 2023 | reactive action-observation control；Generic Agent 有历史，不能写成“无记忆” |
| Reflexion | NeurIPS, 2023 | feedback/memory comparator；需要真实实现和预算核算 |
| AgentBench | ICLR, 2024 | 多环境 Agent 评价已存在 |
| StateFlow | arXiv:2403.11322v5 | 最直接的 state-driven workflow prior；未核验正式主会时不虚构 venue |
| TRPO | ICML, 2015 | performance-difference / value-analysis 的已有理论工具 |
| Geist et al., *A Theory of Regularized MDPs* | ICML, 2019 | Bellman/value analysis 背景；hard mask 是本文特定控制选择 |
| Agarwal et al., *Deep RL at the Edge of the Statistical Precipice* | NeurIPS, 2021 | 多次运行与统计不确定性 |
| PHMForge | arXiv:2604.01532v2 | PHM tool orchestration prior；禁止把“PHM 工具 Agent”当新颖点 |

## Introduction citation strategy

I1–I2 用 Nature/NMI/ICLR/NeurIPS 建立科学 Agent 与 action/history；I3 必须引用 StateFlow；I4 必须引用 PHMForge；I5–I6 用 ICML policy-value theory 与统计工作限定理论和实验。不要把 graph topology 或节点图本身称为 novel architecture。

## 投稿前仍需核验

- StateFlow 的最终发表状态；
- 如果 StateFlow/Reflexion 进入数值结果表，必须按原机制真实复现，不可只改 system prompt；
- base no-memory 是否在可达 histories 上实际改变 intervention；
- dynamic event 是否只有外部 condition signal；没有真实 onset annotation 就删除 detection-delay/event-F1 相关措辞。
