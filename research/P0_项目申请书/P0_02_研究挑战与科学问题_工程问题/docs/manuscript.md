# P0_02 研究挑战与科学问题/工程问题

## 节点范围

本节点只定义研究挑战、科学问题、工程问题和可证伪假设。它不声称 AutoResearch 已经有效，也不替代 P1 的实验设计、P2 的论文定稿、P3 的模拟评审或 P4 的回复打包。

## 核心挑战

P0_01 已将背景 gap 收敛为一个可检验问题：已引用的代表性 agentic research 系统展示了工具使用、多智能体协作或自动科学写作能力，但没有展示一套节点级操作程序，能在阶段转移前把每个 manuscript claim 绑定到证据、协议关卡、独立评审、response coverage 和负结果处理。P0_02 将这个 gap 拆成两类问题。

科学问题是：在固定节点集和固定预算下，显式的 claim-evidence-review-response 治理机制是否能减少不受支持的研究主张，并提高被独立 reviewer 接受的 claim validity？

工程问题是：能否构建一个轻量、可审计、不会变成第二套全局真相源的节点操作系统，使 claim、evidence、protocol、review、response、negative result 和 scheduler transition 都有可复查记录？

这两个问题不能互相替代。工程实现成功只说明流程能跑通；科学问题必须由对照、指标和失败条件来检验。

## 科学/工程边界

工程证据回答“系统是否按约束留下可复查记录”：节点是否有 manuscript、artifact、review、response 和 status；provider/model/data provenance 是否不泄露 secret；PHMGA/Vibench preflight、artifact contract 和 scheduler projection 是否可复跑或可解释。科学证据回答“这种治理机制是否真的改善研究质量”：在相同节点集、预算和 reviewer rubric 下，claim-evidence validity rate 是否提高，unsupported claim count 是否下降，hard-fail closure 和 negative-result retention 是否改善。

因此，工程闭环只能让 SQ1-SQ3 变得可测试，不能直接证明 SQ1-SQ3 成立。相反，如果工程记录完整但 gated workflow 与 manual checklist、prompt-only agent 或 ungated multi-agent baseline 在 claim validity、unsupported claim count、response coverage 和 negative-result retention 上没有差异，科学假设仍应判为不成立。这个分离是 P0_02 的核心防过度声明规则。

## 锁定的评分协议与对照预算

`artifacts/claim_evidence_scoring_protocol.yaml` 将 `claim_evidence_validity_rate` 锁定为 central manuscript claim 的三评审评分协议。每条 central claim 由 method/reproducibility、empirical/statistics、venue/claim-clarity 三个独立 reviewer 评分，支持等级为 `fully_supported=1.0`、`partially_supported=0.5`、`unsupported=0.0`、`not_evaluable=null`。每条 claim 取 reviewer 中位数；若评分从 fully supported 跨到 unsupported，或 reviewer 对证据边界是否允许正文措辞存在实质分歧，则进入 adjudication log。`not_evaluable` 不能静默删除，而是作为 final-threshold blocker。候选 final-submission 条件是 validity rate 不低于 0.90、unsupported claim count 为 0、not-evaluable central claims 为 0，且分歧项已通过降级措辞或 retained blocker 处理。

`artifacts/baseline_budget_protocol.yaml` 将 equal-baseline budget 转换成可检查对照协议。四个条件使用同一固定节点集：manual checklist、prompt-only agent、ungated multi-agent workflow、AutoResearch gated workflow。每个条件必须保留同样的节点范围、最大节点时间、最大 agent turn、允许工具、禁读路径和 reviewer rubric。若某条件无法完成节点，结果进入 `not_evaluable` 或 blocker，不能从分母中删除。正式 provider rows 只有在独立精确授权后才能进入比较，并且必须对所有条件保持一致；在授权前，provider-dependent evidence 对所有条件都保持 blocked。

## 科学问题

**SQ1: Claim governance effectiveness.** 相比 manual checklist、prompt-only agent 和 ungated multi-agent workflow，AutoResearch 的节点级 claim/evidence/protocol/review gate 是否能提高 claim-evidence validity rate，并降低 unsupported claim count？

这个问题可测试，因为它有固定比较对象、固定节点集、可计数输出和反证路径。如果简单 checklist 或 ungated multi-agent workflow 在同等预算下达到同等或更高的 claim validity，并且没有增加 unsupported claims，则 SQ1 不成立。评分细节、partial support 处理、reviewer disagreement 和 adjudication 规则以 `artifacts/claim_evidence_scoring_protocol.yaml` 为准。

**SQ2: Review-response closure.** 独立 reviewer gate 和 response coverage 是否能在不隐藏负结果的前提下，提高 reviewer pass rate 与 hard-fail closure rate？

这个问题可评价，因为每个 reviewer comment 都必须映射到 response、revision evidence 或保留的 blocker。如果 response coverage 只是形式上填表，或者负结果被隐藏，则 SQ2 不成立。

**SQ3: Evidence boundary preservation.** AutoResearch 是否能持续区分 proposal-stage boundary、synthetic/offline sanity check、Stage B reject evidence、Stage C main result 和 Stage D ablation，而不把投影文件、成功运行日志或生成文本当作 research truth？

这个问题可完成，因为边界错误可以通过 claim registry、failure register、keep/discard ledger 和 final submission validator 直接检查。

## 工程问题

**EQ1: Node-local traceability.** 每个 leaf node 需要产生正文、artifact、review verdict 和 response records；scheduler 只读取最小状态，不能把 Canvas、dashboard 或 graph projection 当作内容真相。

**EQ2: Provider and dataset provenance.** PHMGA/Vibench 运行必须能说明数据目录、provider/model、rate-limit/reject state、artifact contract、sample-level metadata-H5 alignment 和 selection eligibility。OpenRouter 只允许免费模型；BigModel 只允许 GLM-4.7-flash 免费模型。API key 只从 `.env` 加载，不能写入节点产物或日志。

**EQ3: Failure-preserving progression.** RM101 reject-evidence rows、rate-limit 中断、adapter preflight pending、score 低于 final threshold 等状态必须保留为 blocker 或 limitation，不能被节点关闭掩盖。

**EQ4: Lightweight reproducibility.** 每个可执行或可渲染产物需要有最小 rerun path、输入/输出位置、版本边界和失败解释。不可复跑的人工判断只能作为 review evidence，不能作为实验结果。

## 可证伪假设

**H1.** 在同一节点集、预算和 reviewer rubric 下，AutoResearch 的 claim-evidence validity rate 高于 prompt-only 或 ungated multi-agent baseline，unsupported claim count 更低。

**H2.** 增加独立 review、response coverage 和 negative-result ledger 后，hard-fail closure rate 提高，同时没有减少已记录的 negative or reject evidence。

**H3.** 当 PHMGA/Vibench adapter preflight、provider model policy 和 artifact contract 均被锁定后，formal Stage C/D runs 可以产生 selection-eligible evidence；如果 sample-level metadata-H5 alignment 失败，或主结果仍只产生 reject-evidence bundle，则 H3 不成立。

## 不可接受表述与修正

- 不写“AutoResearch 已证明更可靠”；改为“后续将通过 claim validity、unsupported claim count 和 reviewer pass rate 检验”。
- 不写“多智能体系统缺乏科学能力”；改为“已引用代表性系统没有展示本文要求的 claim-evidence-review-response phase-gate 操作程序”。
- 不写“工程闭环等于科学贡献”；改为“工程闭环提供可测试机制，科学贡献取决于对照实验和 reviewer gate 的证据”。

## 最小后续证据

1. 固定节点集和基线：manual checklist、prompt-only agent、ungated multi-agent workflow、AutoResearch gated workflow。
2. 指标：claim-evidence validity rate、unsupported claim count、independent reviewer pass rate、response coverage rate、hard-fail closure rate、reproducibility rerun agreement。
3. PHMGA/Vibench 证据：provider/model policy 合规、dataset adapter preflight、artifact contract pass、Stage C main-result rows、Stage D ablation rows、selected_global_best_backend lock。
4. 负结果保留：RM101 reject evidence、rate-limit failure、low review score 和 unresolved adapter blocker 均进入 ledger，而不是从叙事中删除。

## 当前结论

P0_02 的可交接问题定义是：AutoResearch 的研究挑战不是“再做一个 agent 框架”，而是检验一套节点级证据治理机制是否能在真实研究流水线中降低 unsupported claims、提高 review-response closure，并保留负结果和阶段边界。科学问题由可证伪指标检验；工程问题由节点 artifact、provider/dataset provenance、review response 和 scheduler transition 的可复查性检验。
