# P1_07 优化目标、任务与评测协议

## Current Effective Revision

本文件以本节后的 v2 协议为当前有效版本。旧版模板语义已收敛为两个 hard-gate 层次：一层评价 AutoResearch 的 claim/review governance，一层作为 PHMGA/Vibench formal evidence eligibility gate。本节点只定义目标、任务、metric、baseline、repeat/uncertainty、ablation、statistics、budget、artifact path 和 stop condition；不执行 PHMGA formal rows，不选择最终 backend，不把 P1_04/P1_05 synthetic/offline signal、RM101 reject evidence、graph progression 或 review pass 写成最终结果。

## v2 Protocol Scope

P1_07 将 P0_02 的 H1-H3、P0_04 的 evidence-governed route、P0_05 的资源/风险边界和 P1_06 的 PHMGA submodule 边界，压缩成可评审的实验严谨性协议。当前状态是 protocol-ready only：协议可供下游执行或评审，但尚未证明 AutoResearch 有效、PHMGA formal rows selection-eligible、或最终 submission-ready。

## v3 Review-Fix Lock

本节点的当前有效协议以 `artifacts/protocol_map.yaml` 的 `p1_07_protocol_map_v3` 和 `artifacts/experiment_rigor_plan.yaml` 的 `p1_07_experiment_rigor_plan_v3` 为准。上游一致性只引用以下可核验路径：P0_02 `artifacts/problem_hypothesis.yaml` 的 H1/H2/H3 与 falsification lines，P0_04 `artifacts/okr_map.yaml` 的 protocol/data eligibility、Stage C/D 和 review-response closure lines，P0_05 `artifacts/constraint_risk_map.yaml` 的 provider/model、Vibench/PHMGA、Stage B/C/D、review threshold 和 registry blocker lines，P1_05 `artifacts/hypothesis_status.yaml` 的 supported_limited/unsupported/unclear boundary lines，以及 P1_06 `artifacts/submodule_ref.yaml` 的 PHMGA branch/commit/dirty/pointer policy lines。若任一路径不可读，本节点不得声明上游一致性，只能保持 protocol-draft。

预注册 repeat/budget 常量如下：AutoResearch gated workflow、manual checklist workflow、prompt-only agent workflow 和 agent-without-independent-gate workflow 每个 condition 至少 3 个 repeat unit；repeat unit 是独立 seed、独立 operator 或独立 reviewer assignment。每个节点 authoring wall-clock budget 为 45 minutes，reviewer budget 为 20 minutes，artifact audit budget 为 20 minutes。LLM-enabled conditions 每节点 token budget 为 120000；manual condition 记录为 `not_applicable_manual_no_model`，不能把未使用 token 换成额外时间。Stage B backend comparison 每 backend/dataset 至少 1 个完整 row，仅用于 backend-lock preflight，不产生 performance claim；Stage C main rows 和 Stage D ablation rows 每 formal row 至少 3 个 replayable run/seed，否则必须标记为 `low_power_pilot` 或 `non_selection_eligible`。

Metric parser contract 也在 v3 中锁定。Workflow result ledger 必须包含 `protocol_id`, `metric_id`, `row_id`, `claim_id`, `evidence_id`, `condition_id`, `repeat_index`, `artifact_path`, `support_status`, `boundary_label`, `denominator_included`, `numerator_included`, `review_action`, `response_status`, `blocker_id`, and `failure_interpretation`。Formal result ledger 必须包含 `formal_row_id`, `stage`, `dataset_id`, `backend_id`, `provider_name`, `model_name`, `provider_model_policy_pass`, `metadata_h5_alignment_pass`, `artifact_contract_pass`, `selected_global_best_backend_locked`, `result_md`, `artifact_dir`, `ledger_row_path`, `main_table_mapping`, `repeat_count`, and `formal_eligibility_status`。任何 rate metric 缺 numerator/denominator、count metric 缺 count_rule、formal row 缺 gate field、artifact path 缺失且没有 `future_required` 标记，或使用 graph/Canvas/dashboard/wrapper path 作为 research truth，均触发 parser block。

## Final-Threshold Score Boundary

`artifacts/protocol_final_threshold_contract.yaml` 将本节点的 final-threshold 复评边界锁为 node-local protocol score review。可被复评的正向主张只有：P1_07 的 v3 protocol package 已经足够 documented、consistent、complete、exercisable，并且旧 hard-fail 与 AI/H review comments 已在 `review/response.yaml` 中回应。该 contract 不执行 formal rows，不锁定 selected backend，不把 P1_04/P1_05 synthetic/offline signal、RM101 reject evidence、PHMGA provider preflight、graph progression 或 review pass 写成 observed improvement、formal evidence 或 submission-ready proof。

因此，P1_07 可以请求 distinct AI_002 reviewer 判断 node-local protocol score 是否达到 90 以上；即使通过，本节点仍必须保留全局 blocker：P1 checklist、P1_08/P1_09/P3/P4 低分、P3_04 action statuses、selected backend、RM101 positive evidence、adapter preflight、Stage C/D rows 和 final validator。

## v2 Primary/Secondary Outcomes

**Primary outcome: `claim_evidence_validity_rate`.** 它衡量固定节点集合中 central claim 是否同时具备 claim_id、evidence_id、artifact path、support status、boundary label、review action 和 response status。分子是满足完整证据链的 eligible central claims；分母是固定节点集合中所有 proposal、manuscript、review、response 级 central claims。该 metric 对应 H1：gated AutoResearch 是否比 manual checklist、prompt-only agent 和 ungated/no-independent-gate workflow 更少产生 unsupported claims。

**Hard eligibility gate: `formal_result_eligibility_pass`.** 它不是替代 primary outcome 的性能指标，而是 H3 的投稿前门槛。它要求 provider/model policy、metadata-H5 alignment、artifact_contract_pass、selected_global_best_backend、Stage C main rows、Stage D ablation rows、result_md、artifact_dir 和 main table traceability 同时满足。任一失败都将 formal result claim 降级为 blocker、reject evidence 或 limitation。

**Secondary outcomes.** `unsupported_claim_count`, `independent_reviewer_pass_rate`, `response_coverage_rate`, `hard_fail_closure_rate`, `negative_result_retention_rate`, `protocol_completeness_rate`, `reproducibility_rerun_agreement`, `boundary_violation_count`, `final_validator_blocker_count`, `stage_c_main_result_pass`, and `stage_d_ablation_pass`。Secondary outcomes 只能解释 primary outcome 或 hard gate，不得被 cherry-picked 成单独的 positive claim。

## v2 Task Definition And Success Criteria

**Task family A: fixed-node governance comparison.** 输入为同一批 research prompt、acceptance checklist、review rubric、allowed edit scope、node set 和 budget。任务是比较 AutoResearch gated workflow 与三类 baseline：manual checklist workflow、prompt-only agent workflow、agent workflow without independent gate。成功条件是 AutoResearch 在相同节点集合、相同预算、相同 reviewer rubric 和相同 artifact audit procedure 下提高 `claim_evidence_validity_rate`，并且不增加 unresolved unsupported claims。

**Task family B: review-response closure.** 输入为同一 manuscript/review issue set 和 evidence registry。任务是测量 independent review、human-review slot、response coverage 和 negative-result ledger 是否减少未关闭 hard fail。成功条件是 `response_coverage_rate` 和 `hard_fail_closure_rate` 达到预注册阈值，同时 `negative_result_retention_rate` 保持 100 percent 或有显式 keep/discard rationale。

**Task family C: PHMGA formal evidence eligibility.** 输入为 P1_06 记录的 PHMGA submodule、P0_05 约束、Vibench read boundary 和 Stage B/C/D run definitions。任务是验证真实 formal result rows 是否 selection-eligible。成功条件不是单个 macro-F1 好看，而是每个 formal row 有 result_md、artifact_dir、artifact_contract_pass、feature/separability or task-specific gate、ledger row、main-table mapping 和 failure interpretation。RM101 reject rows必须保留，不能转写成 positive evidence。

**Task family D: manuscript integration preflight.** 输入为 protocol_map、experiment_rigor_plan、result ledger、claim_evidence_registry 和 figure/table plan。任务是确认每个 manuscript claim 都能追溯到 protocol/evidence/review/limitation。成功条件是 central claims 的 registry coverage 为 100 percent，unsupported central claim count 为 0，figure/table provenance 可复查。

## v2 Required Baselines And Controls

**Workflow baselines.** 三个必须 baseline 是 `manual_checklist_workflow`、`prompt_only_agent_workflow`、`agent_without_independent_gate`。它们必须使用同一 fixed node set、相同时间或 token budget、同一 acceptance checklist、同一 review rubric、同一 artifact audit procedure 和同一 primary metric。缺任一 baseline 运行记录、人工操作 ledger、prompt/output、review assignment 或 artifact collection procedure 时，H1/H2 只能保持 protocol-ready，不能进入 result-claim-ready。

**Formal evidence controls.** PHMGA formal rows 必须遵守 P0_05 的 Stage B/C/D 范围：Stage B backend comparison 先锁定 `selected_global_best_backend`；Stage C 产生 Ottawa/RM101 ML/Torch main rows；Stage D 产生 minimum ablations。OpenRouter 仅允许 free model，BigModel 仅允许 GLM-4.7-flash free boundary。Vibench 只负责 data reading/catalog/read bundle；PHMGA 负责 DatasetProtocol、split/windowing、DAG、evaluation、ledger 和 tables。

**Negative and failure controls.** Rate limits、missing metadata-H5 alignment、artifact contract failure、RM101 reject evidence、below-threshold reviews、registry schema errors、missing uncertainty 和 missing baseline 都必须作为 blocker 或 reject evidence 留在 ledger 中。它们不能从 denominator 中静默删除。

## v2 Executable Evaluation Protocol Summary

1. Lock the fixed node set and claim universe before running comparisons.
2. Freeze inputs: research prompt, acceptance checklist, review rubric, allowed edit scope, provider/model policy, data root, and artifact schema.
3. Run or record the three workflow baselines under the same budget and audit procedure.
4. For formal PHMGA rows, require adapter preflight, selected backend lock, artifact contract, Stage C rows, Stage D ablations, result_md, artifact_dir, and ledger/table mapping.
5. Repeat each workflow condition at least 3 times by random seed, independent operator, or independent reviewer assignment. Stage C and Stage D formal rows also require at least 3 replayable run/seed units per formal row; Stage B requires at least 1 complete backend/dataset row and remains backend-lock preflight only. If the minimum is not met, mark `low_power_pilot` or `non_selection_eligible` and block strong claims.
6. Report point estimate plus confidence interval or bootstrap interval for rate metrics; report failure distribution for unsupported, rejected, rate-limited, or inconclusive rows.
7. Write every output to a traceable artifact: protocol_map, experiment_rigor_plan, gate_report, future result ledger, future coverage matrix, review verdict, response coverage, and keep/discard ledger.

## v2 Documented / Consistent / Complete / Exercisable

**Documented.** Objective、task、claim IDs、primary/secondary outcomes、hard gates、baseline/control、budget、repeat、uncertainty、statistics、failure interpretation、artifact path 和 stop condition 都必须写入 `artifacts/protocol_map.yaml` 和 `artifacts/experiment_rigor_plan.yaml`。

**Consistent.** `docs/manuscript.md`、`protocol_map.yaml`、`experiment_rigor_plan.yaml`、`gate_report.md`、future result ledger 和 future claim_evidence_registry 使用同一 claim/hypothesis/status vocabulary。Graph、Canvas、dashboard 或 wrapper 文件不得作为 research truth。

**Complete.** 协议同时覆盖 success、unsupported、unclear、reject evidence、rate limit、missing baseline、missing uncertainty、adapter failure、schema failure 和 below-threshold review。任何 cherry-picked favorable metric 必须触发 hard gate。

**Exercisable.** 下游 worker 能在不重定义科学问题的情况下执行或记录比较：它知道输入、baseline、metric parser、repeat unit、artifact output、stop condition 和 downgrade action。若命令或人工记录模板缺失，协议必须报告 blocking gap，而不是写 vague future-completion prose。

## v2 Current Conclusion

P1_07 当前达到 protocol-ready：它把 H1-H3 映射到任务、baseline、metric、repeat/uncertainty、artifact 和 stop condition。它不证明 AutoResearch 已经有效，不证明 PHMGA formal rows 已经 selection-eligible，也不解除 P0_05/P1_06 记录的 dirty submodule、registry schema、selected backend、adapter preflight、Stage C/D 和 final validator blockers。

## Legacy Context

Legacy Context is retained only to preserve node history. It is non-normative and must not override the v3 review-fix lock, the parser contract, or the preregistered repeat/budget constants above.

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
