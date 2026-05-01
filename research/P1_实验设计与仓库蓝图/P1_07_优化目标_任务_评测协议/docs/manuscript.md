# 优化目标、任务与评测协议模板：AutoResearch 系统研究

## Protocol Scope

本节点定义 AutoResearch 作为研究系统时的评价协议，不绑定某个学科数据集或某个算法 benchmark。评测对象是研究流程质量：从问题、协议、正文主张到评审回复，系统是否能产生可复核、可重复计算、可被 reviewer 攻击的 evidence chain。该协议对齐 Nature 的可复现报告要求 [1] 和 IEEE/TPAMI 论文评审对方法、实验、公平比较与同行审查的要求 [2]。

## Primary/Secondary Outcomes 是什么？

Primary outcome：claim-evidence validity rate。定义为在预声明节点集合中，所有 manuscript/proposal/response 级 claim 能够绑定有效 evidence_id、artifact path、citation status、boundary 和 reviewer action 的比例。该 metric 直接对应科学主张是否可审计，而不是文本是否流畅。

Secondary outcomes：protocol completeness、independent reviewer pass rate、reproducibility rerun agreement、unsupported claim count、hard-fail closure rate、human gate escalation rate、time-to-author-exit。Secondary metrics 用来解释 primary metric 的来源，不能替代 primary metric。

最低 success criterion：在相同节点集合、相同预算和相同 reviewer rubric 下，AutoResearch 相对 prompt-only agent workflow 或 manual checklist workflow 具有更高的 claim-evidence validity rate，并同时报告 repeat、uncertainty、negative result 和失败类型 [1][3]。若未完成 baseline、repeat 或 uncertainty，本节点只能进入 protocol-ready，不能进入 result-claim-ready。

## Task 定义和 Success Criterion 是什么？

Task family A：P0 problem formulation。输入是 research prompt、node checklist 和相关资料；输出是 gap map、candidate claim list、innovation boundary 和 evidence gate。成功条件是每个研究内容能映射到具体问题、相邻工作边界、后续证据和降级规则。

Task family B：P1 experiment protocol。输入是 candidate claims 和研究对象；输出是 protocol_map、primary/secondary metrics、baseline/control、repeat/uncertainty plan 和 negative result policy。成功条件是 objective、task、protocol、metrics、baseline 和 artifact path 一一对应。

Task family C：P2 manuscript methods and claim registry。输入是 protocol、evidence artifacts 和 venue standard；输出是 methods draft、claim_evidence_registry、data-code/protocol availability statements 和 limitation boundary。成功条件是别人能理解数据、参数、统计、代码路径和复现实验步骤。

Task family D：P3/P4 review and response. 输入是 manuscript version、review comments 和 evidence registry；输出是 critique severity map、revision actions、point-to-point response 和 coverage check。成功条件是每个 fatal/major concern 有 evidence、location、actionable fix 和 response status。

## 什么 Baseline 与对照是必须的？

Baseline 1：manual checklist workflow。研究者按同一 acceptance checklist 手工推进节点，不使用 agent 自动生成正文；该 baseline 用来估计人类流程的可审计性和遗漏模式。

Baseline 2：prompt-only agent workflow。agent 只接收 research prompt 并产出正文，不使用 claim/evidence/protocol registry、review gate 或 allowed edit scope；该 baseline 用来隔离“文本生成能力”和“研究状态治理能力”。

Baseline 3：agent workflow without independent gate。保留节点结构和 checklist，但取消独立 reviewer/human gate；该对照用于评估 author exit 与 node close 混用带来的风险。

公平比较要求：所有 baseline 使用同一节点集合、同一时间或 token 预算、同一 reviewer rubric、同一 primary metric 和同一 artifact audit procedure。任何 baseline 缺少运行命令、人工操作记录或 reviewer assignment 时，比较结论必须降级 [3]。

## Protocol_Map 与可执行评测协议摘要

protocol_map 将 objective、task、protocol、metrics、baseline、repeat、uncertainty 和 artifact path 绑定在一起。目标/任务/协议一一对应：目标是提高研究流程的 claim-evidence validity；任务是节点级 research production and review；协议是 fixed-node-set controlled comparison；primary metric 是 claim-evidence validity rate；secondary metrics 是 protocol completeness、reviewer pass rate、rerun agreement 和 unsupported claim count。

可执行评测协议摘要：

1. 固定节点集合：至少覆盖 P0 problem, P1 protocol, P2 methods, P3 review, P4 response 五类节点。
2. 固定输入：同一 research prompt、acceptance checklist、review rubric、allowed edit scope 和 evidence artifact policy。
3. 固定 baseline：manual checklist、prompt-only agent、no-independent-gate agent。
4. 固定 repeat：每个 condition 至少多个随机种子或独立 reviewer assignment；若预算不足，必须报告 low-power limitation。
5. 固定 statistics：报告 point estimate、confidence interval 或 bootstrap interval、failure distribution 和 negative result。
6. 固定 artifact：每个 run 输出 result ledger、claim registry、review verdict、coverage matrix 和 run command。

## Documented / Consistent / Complete / Exercisable

本节明确 documented / consistent / complete / exercisable 的最低要求。

Documented：objective、task、protocol、primary metric、secondary metrics、baseline/control、repeat、uncertainty、budget、reviewer rubric 和 artifact path 必须被写入 protocol artifact。

Consistent：正文、protocol_map、gate_report、experiment_rigor_plan 和后续 result ledger 使用同一 claim_id/evidence_id 命名；不允许同一 claim 在不同 phase 中改名后失去追踪。

Complete：除了成功指标，协议必须包含 unsupported claim、failed reviewer gate、missing citation、missing baseline、missing uncertainty、hidden negative result 等 failure case。

Exercisable：下一阶段 worker 应能在不重定义科学问题的情况下运行或模拟比较；若缺少命令、人工记录格式或 reviewer assignment 规则，则本节点必须报告 blocking gap。

## Gate Report Policy

hard-gate block 必须绑定 claim_id、evidence_id、location 和 actionable_fix；否则只能作为 advisory critique。缺失指标或 baseline 会被明确暴露为 blocking gap，不能用“后续完善”替代。Primary metric、公平比较、可重复计算和 artifact 完整性是进入 P2/P3 的最低门槛 [1][2][3]。

## Author Exit

gate_inputs_verified: true。blocking_gaps_are_explicit: true。Baseline、metric、protocol、reproducibility、artifact、primary metric、公平比较和可重复计算均已在本节点显式声明；未执行真实比较实验的证据边界已标出。

## References

[1] Nature Portfolio, Reporting standards: https://www.nature.com/ncomms/editorial-policies/reporting-standards

[2] IEEE Author Center, Submission and peer-review policies: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/

[3] Local evidence gate: `test/NATURE_LEVEL_NODE_RUBRIC.md`, `artifacts/experiment_rigor_plan.yaml`, and downstream result ledgers.
