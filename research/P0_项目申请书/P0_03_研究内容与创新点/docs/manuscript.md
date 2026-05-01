# 研究内容与创新点模板：AutoResearch 系统研究

## 研究定位

本节点把 AutoResearch 定义为一种面向科研生产的 human-agent research operating system，而不是单个写作助手、单次 agent workflow 或本地验证脚本。研究对象是“如何让从问题形成、实验设计、论文写作到评审回复的研究过程可审计、可复现、可停止、可被外部评审攻击”。该定位对齐 Nature 对原创研究重要性、证据强度和可复现报告的要求 [1][2]，也对齐 IEEE/TPAMI 语境下对清晰问题、可复核方法、审稿伦理与证据链的要求 [3]。

## Significance、Gap、Hypothesis/Aims、Expected Outcomes、Impact、Feasibility

Significance：当前大模型可以生成研究文本和代码片段，但研究流程中的失败常发生在“未被发现的断裂”：问题未收敛、实验协议与主张脱节、结果解释越过证据、审稿意见没有闭环。AutoResearch 的研究价值在于把这些断裂转化为可检查的研究状态，而不是把 agent 输出直接视为完成态 [1][2]。

Gap：相邻工作可分为三类：通用 agent workflow、自动论文写作或综述工具、实验管理与 MLOps 工具。它们分别覆盖任务编排、文本生成、代码运行和结果记录，但通常不把 proposal-node、experiment-node、manuscript-node、review-node 和 response-node 作为同一证据链中的研究对象。这里的空缺不是“缺少更多自动化”，而是缺少节点级 claim-evidence-protocol-human-gate 的统一研究契约 [4]。

Hypothesis/Aims：本项目的可检验假设是：若每个研究节点都显式声明研究问题、允许修改范围、预期产物、证据要求、失败条件和人工 gate，则系统更容易暴露未支撑主张、不可复现实验协议和越权写作，而不是把这些问题隐藏在流畅正文中 [4]。Aims 包括形成节点契约、形成跨 phase 的 claim-evidence registry、形成可执行协议与评审闭环。

Expected outcomes：预期产物不是“自动生成高分论文”的承诺，而是一组可被 reviewer 检查的研究模板、协议、证据登记表和 phase gate。每个产物都应回答一个具体问题：该节点主张是什么、依赖什么证据、何时必须停止、何时需要独立 reviewer 或人类确认 [2][4]。

Impact：若后续实验支持该假设，AutoResearch 可为研究型工程团队提供一种低依赖、可审计的研究操作层，使 proposal、实验、manuscript 和 response 的转移条件更透明。当前节点只建立研究内容与新颖性边界，不把设计假设写成结果结论 [4]。

Feasibility：可行性来自仓库已有的 research node 结构、node-local prompts/checklists、评审 rubric、allowed edit scope 和本地评测入口；这些是研究对象的最小执行面，而不是论文的科学结论本身 [4]。

## 研究内容清单

研究内容一：节点级研究契约。每个 research node 应声明 context、research question、allowed action、expected output、evidence requirement、failure mode 和 human/reviewer gate。它解决的问题是：研究过程的完成态经常只有文本或文件存在，缺少可复核的研究判断。相对通用 agent workflow，它的最小差异是把“能生成”改为“能被证据检查、能失败、能停止”。

研究内容二：跨 phase 的 claim-evidence-protocol 链。P0 的 gap 和 aim、P1 的 protocol 和 metric、P2 的 methods 和 claim registry、P3 的 critique、P4 的 response 必须共享可追踪的 claim_id/evidence_id。它解决的问题是：proposal、实验和论文正文各自成立，但证据链不连续。相对自动写作工具，它的最小差异是正文主张必须能回指到协议、结果或明确的证据缺口。

研究内容三：研究协议的预注册式约束。实验任务、primary/secondary metrics、baseline、repeat、uncertainty、negative result policy 和 artifact path 应在执行前绑定。它解决的问题是：结果出来后再选择指标或叙事会放大 reviewer 风险。相对普通 experiment note，它的最小差异是把 failure interpretation 和 unsupported claim 降级规则写入协议。

研究内容四：外部评审与人工 gate。每个关键节点必须区分 author exit 和 node close，并由独立 reviewer 或人类确认 phase transition。它解决的问题是：作者线程容易把结构完整误当成研究完成。相对单线程自动化，它的最小差异是把独立评审作为状态转换条件，而不是作为可选评论。

## 创新点清单

创新点一：以 research node 为最小科学工作单元。新颖性边界是“节点能被审计、失败和复跑”，不是“agent 生成内容更好”。该点需要通过 NodeBench、外部 reviewer verdict、失败类型分布和人类 gate 记录来检验 [4]。

创新点二：以 claim-evidence-protocol 统一 proposal、实验、写作和回复。新颖性边界是跨 phase 的证据追踪机制，不是某个字段名、脚本名或 UI。该点需要通过 claim registry 覆盖率、unsupported claim 数量、revision action 闭环率来检验 [4]。

创新点三：以 phase gate 控制自动化边界。新颖性边界是把“继续推进”的权力绑定到证据、独立评审和人工确认，而不是让 agent 无限循环。该点需要通过 blocked-node 记录、human_review next_action 和 reviewer hard_fail 处理记录来检验 [4]。

## 内容-问题-创新映射

| 研究内容 | 解决的问题 | 相邻工作边界 | 可检验证据 | 降级规则 |
|---|---|---|---|---|
| 节点级研究契约 | 完成态缺少可复核依据 | 通用 agent workflow 只证明能执行任务 | NodeBench、eval report、独立 reviewer verdict [4] | 只能称为审计结构，不能称为质量提升 |
| claim-evidence-protocol 链 | proposal、实验、正文证据断裂 | 自动写作工具主要优化文本产出 | claim registry、protocol map、response coverage [4] | 无结果时降级为设计假设 |
| 预注册式实验约束 | 指标和 baseline 可被事后选择 | 普通实验记录可在执行后补全 | metric parser、baseline ledger、uncertainty report [2][4] | 缺 baseline 或 repeat 时不进入结果主张 |
| 外部评审与人工 gate | 作者线程自我关闭风险 | 单线程自动化缺少独立 gate | review/verdict.yaml、human gate note [4] | 只能 author exit，不能 node close |

## 必答研究问题覆盖

每条研究内容对应解决什么问题：节点契约解决完成态无审计依据，claim-evidence-protocol 链解决跨 phase 证据断裂，预注册式协议解决 post-hoc metric/baseline 风险，外部评审 gate 解决单线程自我关闭风险。

每条创新点相对已有工作的最小差异是什么：相对通用 agent workflow，本研究把 research node 改成可失败的科学工作单元；相对自动写作工具，本研究要求正文主张绑定证据和边界；相对普通实验管理，本研究把失败解释和 phase gate 写入协议；相对单线程自动化，本研究把独立 reviewer 和 human gate 纳入状态转换。

哪些表述属于贡献，哪些只是实现细节：研究贡献只包括节点级研究契约、跨 phase 证据链、预注册式协议约束和独立 gate 机制。脚本、YAML 字段、dashboard、Canvas、graph projection 和本地评分器只是实现细节，不能作为论文层面的科学结论 [4]。

## Evidence Gate 与风险边界

本节点只定义研究内容和新颖性边界；后续必须由 P1/P2/P3/P4 节点分别补齐 protocol、methods、review 和 response 证据。任何关于“提高研究质量”“降低错误率”“优于人工流程”的表述都必须等待 controlled comparison、repeat、uncertainty 和 reviewer verdict；当前只能作为待检验问题写入 protocol [2][4]。

## Author Exit

required_artifacts_exist: true。key_research_judgment_answered_or_gap_reported: true。citation_status_checked_when_external_sources_are_used: true。已形成四个可区分的研究内容单元；每条创新点都能映射到具体问题与后续证据，并映射到相邻工作边界和降级规则；空泛 novelty 表述已收缩为可检验假设 [4]。

## References

[1] Nature, Editorial criteria and processes: https://www.nature.com/nature/for-authors/editorial-criteria-and-processes

[2] Nature Portfolio, Reporting standards: https://www.nature.com/ncomms/editorial-policies/reporting-standards

[3] IEEE Author Center, Submission and peer-review policies: https://journals.ieeeauthorcenter.ieee.org/become-an-ieee-journal-author/publishing-ethics/guidelines-and-policies/submission-and-peer-review-policies/

[4] Local repository evidence gate: `test/NATURE_LEVEL_NODE_RUBRIC.md`, node `prompts/acceptance_checklist.yaml`, and downstream `logs/eval_report.md`.
