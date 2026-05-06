# P0_03 研究内容与创新点

## 节点范围

本节点把 P0_01 的背景 gap 和 P0_02 的科学/工程问题转化为研究内容单元、候选贡献和创新边界。它只定义要研究什么、每项内容解决什么问题、最小创新差异是什么，以及哪些只是实现细节。它不声称 AutoResearch 已经提高研究质量，也不把 YAML 字段、脚本、graph、Canvas、dashboard 或本地日志当成科学贡献。

## 研究定位

AutoResearch 在本项目中的候选定位不是“更会写论文的 agent”，也不是“更复杂的多智能体框架”。它是一个可检验的 research-operation mechanism：用节点级 claim/evidence/protocol/review/response gate 约束研究生产过程，观察这种约束是否能减少 unsupported claims、提高 review-response closure，并保留失败与阶段边界。

P0_01 已限定 nearest prior work：工具型语言智能体、反馈型智能体、多智能体框架、ML 实验 agent、自动科学家系统，以及出版治理政策。P0_02 已将问题拆成科学问题 SQ1-SQ3 与工程问题 EQ1-EQ3。P0_03 的任务是把这些问题压成 2-4 个可评审研究内容单元，避免把实现细节包装成 novelty。

## 研究内容清单

**内容一：节点级证据治理契约。** 该内容解决“研究节点完成态缺少可复核判断”的问题。每个节点必须明确问题、允许动作、预期产物、证据要求、失败条件、review gate 和 response coverage。相对 ReAct/Reflexion 一类 tool-using 或 feedback agent，最小差异不是 action trajectory 更复杂，而是节点完成必须绑定可审计的 claim/evidence/review state。后续证据是 claim-evidence validity rate、unsupported claim count、reviewer pass rate 和 hard-fail closure rate。

**内容二：跨阶段 claim-evidence-protocol 链。** 该内容解决“proposal、实验、正文、评审、回复分别完整但主张身份断裂”的问题。P0 的 gap/aim、P1 的 protocol/metric、P2 的 manuscript claim、P3 的 reviewer critique、P4 的 response action 必须共享可追踪 claim_id/evidence_id。相对自动写作或实验记录工具，最小差异不是生成更多文本或记录更多文件，而是每条 manuscript claim 都能回指协议、结果、引用或明确的 evidence gap。

**内容三：独立 review 与负结果保留 gate。** 该内容解决“作者线程自我关闭”和“负结果被叙事抹平”的问题。作者退出和节点关闭必须分离；独立 reviewer verdict、human-review lane、response coverage、failure register、keep/discard ledger 和 negative-result note 共同决定阶段是否推进。相对单线程自评或自动 critique，最小差异是 review objection 必须映射到 response/evidence/blocker，且 reject evidence 不能被节点关闭删除。

**内容四：provider/dataset provenance 与 formal-evidence eligibility。** 该内容解决“运行成功被误当成可选主结果”的问题。PHMGA/Vibench 的 provider/model policy、API-key loading boundary、artifact contract、sample-level metadata-H5 alignment、Stage C/D rows 和 selected_global_best_backend 必须共同决定结果是否 selection-eligible。相对普通 experiment log，最小差异是数据/模型/contract/preflight 共同形成 evidence eligibility gate；不满足时只能记录 blocker 或 reject evidence。

## 创新点清单

**创新点一：以可失败节点作为研究操作最小单元。** 候选贡献是把 research node 设计为可被外部 reviewer 攻击、可失败、可保留 blocker 的科学工作单元。它不是“第一个 agent workflow”，也不是“自动化程度更高”。强表述只有在 gated workflow 相比 prompt-only 或 ungated multi-agent baseline 降低 unsupported claims 后才能成立。

**创新点二：跨 phase 的 claim identity 和 evidence boundary。** 候选贡献是将 claim、evidence、protocol、review issue、response action 和 revision evidence 维持为同一条可审计链。它不是 citation formatting、字段命名或 UI 显示。强表述需要 claim registry coverage、unsupported claim audit、response coverage audit 和 independent reviewer pass evidence 支持。

**创新点三：把独立 gate 和负结果保留变成阶段转移条件。** 候选贡献是将 author exit 与 node close 分离，把 hard fail、reject evidence、low score、rate limit 和 unresolved adapter blocker 保留到目标状态与 ledger。它不是“多一个评审文件”。强表述需要证明 gate 能捕获作者线程会漏掉的问题，且不会隐藏 negative evidence。

**创新点四：结果资格而非运行成功作为实验进入主张的门槛。** 候选贡献是把 provider policy、dataset alignment、artifact contract 和 formal row status 作为 evidence eligibility。它不是 PHMGA 或 Vibench 本身的新算法贡献。强表述需要 adapter preflight、Stage C/D formal rows 和 selected backend lock。

## 内容-问题-创新映射

| 研究内容 | 对应问题 | 最小创新差异 | 后续证据 | 降级规则 |
| --- | --- | --- | --- | --- |
| 节点级证据治理契约 | SQ1, EQ1 | 节点完成绑定 claim/evidence/review state，而不只看 agent trajectory | claim validity、unsupported claim count、reviewer pass rate | 无对照时只能称为治理设计 |
| 跨阶段 claim-evidence-protocol 链 | SQ1, SQ3 | 同一 claim identity 穿过 P0-P4，而不只是局部文档完整 | registry coverage、protocol map、response coverage | 无 reviewer 确认时只能称为 traceability scaffold |
| 独立 review 与负结果保留 gate | SQ2, SQ3, EQ3 | phase transition 依赖 independent verdict 和 blocker ledger，而不是作者自评 | hard-fail closure、negative-result retention、human-review handoff | 无独立 gate 时只能 author exit |
| provider/dataset provenance 与结果资格 gate | H3, EQ2 | 以 evidence eligibility 决定能否写入主结果，而不把运行成功当结论 | adapter alignment、artifact contract、Stage C/D rows、backend lock | preflight 或 formal row 未过时只能记录 blocker/reject evidence |

## Reviewer-Attack Boundary

RC1 is attacked if node closure can be decided from file presence, successful execution, or author exit without a reviewer-visible claim/evidence/review/response state. RC2 is attacked if a claim can be coherent inside one phase but lose its identity when it moves from proposal to protocol, manuscript, review, and response. RC3 is attacked if independent review becomes a checklist that lets hard fails, low scores, or reject evidence disappear after a node closes. RC4 is attacked if PHMGA/Vibench success is framed as a new algorithmic contribution or a main-result claim before provider policy, adapter alignment, artifact contract, formal rows, and selected-backend evidence are all locked.

This attack surface preserves two distinctions. RC1 governs whether a node may close; RC2 governs whether the same claim remains traceable across phases. RC4 governs whether a result is eligible to support a claim; it is not a PHMGA/Vibench algorithm contribution.

## 贡献与实现细节边界

论文层面的候选贡献只包括：节点级证据治理契约、跨阶段 claim identity、独立 gate 与负结果保留、结果资格 gate。以下内容只是实现细节或投影，不得作为科学贡献单独宣传：YAML 字段名、脚本文件名、graph.json、graph_status.json、Canvas、dashboard、Claude/Codex wrapper、单次成功日志、synthetic/offline sanity check、review 文本数量。

## Proposal-Stage Evidence Boundary

当前节点只证明研究内容和创新边界已经收敛到可评审的候选贡献。任何关于“提高研究质量”“优于人工流程”“减少错误率”“生成可投稿论文”的强表述，都必须等待固定节点集、固定预算、明确 baseline、claim-evidence audit、response coverage audit、negative-result ledger、PHMGA/Vibench adapter preflight、Stage C/D formal rows 和 independent reviewer evidence。

## Final-Threshold Evidence Readiness

P0_03 的最终阈值问题不是“下游实验是否已经完成”，而是“研究内容与创新点是否已经被压缩成可被下游证据判真伪的贡献单元”。本节点只在以下条件同时满足时通过最终阈值：每项贡献都有 nearest-prior boundary、reviewer attack path、下游 evidence row、降级规则和禁止宣传的实现细节；所有尚未完成的正式证据都被保留为下游 blocker 或 protocol-locked item，而不是被写成支持性结果。

该判据已经接入两个上游锁定结果。P0_01 的 final-submission SOTA sweep 明确了最接近的工具型 agent、反馈 agent、多智能体框架、ML experiment agent、automated scientist、software agent、experiment tracking/provenance 和 publication-governance 类 prior work，并给出七项 novelty falsification test。P0_02 的 claim-evidence scoring protocol 与 baseline budget protocol 已固定 claim_evidence_validity_rate 的评审人数、partial-support 计分、not-evaluable blocker、disagreement/adjudication 规则，以及 manual checklist、prompt-only agent、ungated multi-agent 和 AutoResearch gated workflow 的固定节点集与同预算比较。

因此，P0_03 可以声称“贡献边界和证据需求已准备好进入下游测试”，但不能声称 AutoResearch 已经提升研究质量、减少 unsupported claims、提高 response closure、改善 reproducibility，或得到 selection-eligible 的 PHMGA/Vibench 主结果。固定节点 baseline comparison、claim-evidence validity audit、unsupported-claim audit、response coverage audit、negative-result retention audit、Stage C/D formal rows、selected backend lock 和 live citation verification 都仍是下游证据行。

## 当前结论

P0_03 的可交接结论是：AutoResearch 的研究内容应聚焦于 evidence governance，而不是泛化为 agent 能力叙事。四项候选创新都被绑定到具体问题、nearest prior boundary、后续证据和降级规则；当前只处于 proposal-stage，尚不能写成已验证贡献。
