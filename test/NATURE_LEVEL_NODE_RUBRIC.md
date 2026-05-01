# Nature-Level Node Rubric

This rubric translates Nature Portfolio editorial, peer-review, and reporting expectations into node-level acceptance criteria for this repository.

It is a scoring guide, not proof that a paper will be accepted by Nature.

## Official Basis

- Nature Article criteria: original scientific research, outstanding scientific importance, and conclusions of interest to an interdisciplinary readership.
- Nature Portfolio reviewer guidance: novel conclusions, strong evidence for main conclusions, state-of-the-art data generation/processing, field interest, convincing claims, reproducible methods, sound statistics, and fair treatment of prior literature.
- Nature Portfolio reporting standards: readers must be able to replicate and build on published claims; data, materials, code, and protocols must be available without undue qualification.

Sources:

- https://www.nature.com/nature/for-authors/editorial-criteria-and-processes
- https://www.nature.com/nature-portfolio/about/communications-journals-guide-to-reviewers
- https://www.nature.com/ncomms/editorial-policies/reporting-standards
- https://www.nature.com/nature-portfolio/for-authors/publish

## Scoring Model

Score each node from `0` to `5` on the dimensions below, then map to 100 points.

| Dimension | Weight | Nature-level standard |
| --- | ---: | --- |
| Originality / Novelty | 20 | Clear advance over strong prior work, not incremental repackaging |
| Scientific Importance | 20 | Addresses a field-level scientific or engineering bottleneck |
| Evidence / Technical Soundness | 25 | Claims are supported by robust data, baselines, uncertainty, and controls |
| Reproducibility / Transparency | 15 | Data, code, protocol, config, and limitations are inspectable |
| Broad Interest / Story Clarity | 10 | A scientist outside the narrow subfield can understand why it matters |
| Review Robustness | 10 | Anticipates alternative explanations, negative results, and reviewer attacks |

Verdict thresholds:

| Score | Verdict |
| ---: | --- |
| `>=90` | Nature-ready candidate |
| `80-89` | Strong specialist paper |
| `60-79` | Incomplete / weak |
| `<60` | Blocked |

## Hard Fail

Any hard fail blocks downstream promotion regardless of score.

- Unsupported central claim.
- Missing reproducibility path for data, code, protocol, or configuration.
- Hidden negative result or omitted limitation.
- Graph, Canvas, or dashboard treated as research truth.
- Unbounded autonomous loop or undeclared handoff.
- Reviewer-critical concern not mapped to evidence or revision action.

## External Reviewer Independence

Every node-level Nature review must be produced by a reviewer agent or thread that is distinct from the autoresearch agent that authored the node output.

- The reviewer and author must not be the same runtime agent/thread.
- The per-node runtime rubric lives at `prompts/review_rubric.yaml`.
- The structured gate lives at `review/verdict.yaml`.
- `independence_confirmed` can be set to `true` only by that distinct reviewer run.

## Review Output Contract

Each reviewed node should emit:

- `review/AI_001.md`: human-readable reviewer comments
- `review/verdict.yaml`: structured pass/revise/block gate
- `review/response.yaml`: response tracking surface for later fix/review loops

## Node Rubric

| Node | Nature-level `5` criterion | Blocking failure |
| --- | --- | --- |
| `research/P0_项目申请书` | P0 leaves form a coherent research thesis with problem, novelty, route, resources, and risks. | Any critical P0 leaf is missing or below specialist-paper level. |
| `research/P0_项目申请书/P0_01_研究背景与调研` | SOTA, recent strong baselines, field disagreement, and unresolved gap are explicit. | Literature list without gap synthesis. |
| `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题` | Scientific question and engineering bottleneck are separated and testable. | Engineering task is relabeled as science. |
| `research/P0_项目申请书/P0_03_研究内容与创新点` | Novelty is compared against concrete prior work and tied to mechanism. | Vague claims such as first, better, or automatic without evidence. |
| `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR` | Route links hypothesis, experiments, metrics, and stop conditions. | OKR lists tasks but cannot validate a claim. |
| `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界` | Budget, resources, data limits, ethics/license issues, and exit criteria are explicit. | Missing budget, risk, or stop condition. |
| `research/P1_实验设计与仓库蓝图` | Experiment design produces a bounded, reproducible evidence chain. | P1_04 or P1_05 lacks executable evidence contract/result evidence. |
| `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用` | Data provenance, versioning, license, preprocessing, leakage risk, and minimal reproduction are inspectable. | Data path exists but provenance or leakage is unclear. |
| `research/P1_实验设计与仓库蓝图/P1_02_伪代码` | Pseudocode defines mechanism, invariants, inputs, outputs, and complexity boundary. | Narrative workflow cannot be implemented. |
| `research/P1_实验设计与仓库蓝图/P1_03_仓库蓝图` | Module boundary, experiment entry, config, logs, and artifact paths are minimal and reproducible. | Architecture ceremony hides the experiment path. |
| `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证` | Executable contract defines command, metric, parser, budget, failure signal, and editable scope. | Missing or non-executable `execution_contract.yaml`. |
| `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理` | Results map claims to supported, unsupported, negative, and limited evidence. | Summarizes before `artifacts/auto_experiment/results.tsv` exists. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略` | Repository strategy is reproducible, isolated, and does not create a second source of truth. | Manual path magic or unpinned dependency state. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_01_新仓库项目` | New project has minimal dependencies, clear entrypoint, and reproducible setup. | Scaffold exceeds research logic. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_02_现有仓库接入` | Existing repo is connected without destructive edits; environment and path mapping are explicit. | Hidden local environment dependency. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_03_子模块仓库引用` | Submodule is pinned, licensed, and has update policy. | Floating external dependency. |
| `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/P1_06_04_feature_branch_修改策略` | Branch strategy defines scope, rollback, and experiment isolation. | Direct mainline mutation without evidence trail. |
| `research/P1_实验设计与仓库蓝图/P1_07_优化目标_任务_评测协议` | Metrics map to scientific claims with baselines, repeats, uncertainty, and failure interpretation. | Cherry-picked favorable metric. |
| `research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格` | Tables preregister main result, ablation, negative result, and uncertainty. | Expected table assumes success only. |
| `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿` | Figures explain evidence or mechanism with baselines and uncertainty. | Decorative performance plot without statistical support. |
| `research/P2_论文撰写` | Manuscript claims are evidence-linked and ready for expert attack. | Writing proceeds before evidence or claim mapping. |
| `research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature` | Target venue, readership, story shape, figures, and scope are justified. | Template choice substitutes for venue fit. |
| `research/P2_论文撰写/P2_02_初稿_md` | Draft leaves combine into a complete Article argument with evidence anchors. | Draft stores claims not traceable to results. |
| `research/P2_论文撰写/P2_02_初稿_md/P2_02_01_引言` | Introduction creates a clear field-level hook from gap to claim. | Background dump or inflated promise. |
| `research/P2_论文撰写/P2_02_初稿_md/P2_02_02_preliminary` | Preliminary evidence lowers feasibility and reviewer-risk uncertainty. | Demo anecdote without controlled evidence. |
| `research/P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿` | Flow diagram makes mechanism and evidence path clear to non-specialists. | Pipeline decoration without claim linkage. |
| `research/P2_论文撰写/P2_02_初稿_md/P2_02_04_方法` | Methods contain enough detail to reproduce data, parameters, statistics, and code path. | Key steps omitted or hidden in prose. |
| `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论` | Experiments support claims and discuss alternatives, failures, and limits. | Reports best results only. |
| `research/P2_论文撰写/P2_03_定稿_tex` | TeX draft has complete structure, references, figures, supplementary links, and availability statements. | Text and evidence are disconnected. |
| `research/P2_论文撰写/P2_04_形式检查` | Checks cover format, references, figures, ethics, data, and code availability. | Only grammar or typography is checked. |
| `research/P2_论文撰写/P2_05_去AI味道` | Style becomes specific, restrained, evidence-led, and scientifically unchanged. | Rewrite changes scientific meaning or hides uncertainty. |
| `research/P3_论文模拟评审与修改_多轮` | Review loop is bounded and produces actionable evidence-backed revisions. | Infinite review cycle or untraceable critique. |
| `research/P3_论文模拟评审与修改_多轮/P3_01_评审轮次` | Round has target manuscript version, reviewer roles, inputs, and exit conditions. | Review runs without stopping rule. |
| `research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案` | Reviewer personas cover domain, method, statistics, reproducibility, and editor view. | Only friendly or single-perspective reviewer. |
| `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要` | Critique is classified as fatal, major, or minor and mapped to evidence or text. | Summary without location or severity. |
| `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作` | Each action has target node/file, evidence requirement, and done definition. | Vague action such as improve wording. |
| `research/P4_论文回复_response` | Response package covers all reviewer concerns with evidence and versioned changes. | Response proceeds without review mapping. |
| `research/P4_论文回复_response/P4_01_审稿意见收集` | Original comments, source, version, deadline, and constraints are preserved. | Only summarized reviewer concerns. |
| `research/P4_论文回复_response/P4_02_问题映射矩阵` | Every concern maps to claim, evidence, location, and response strategy. | Any reviewer concern is unmapped. |
| `research/P4_论文回复_response/P4_03_逐点回复草稿_md` | Each reply answers directly, cites evidence, and names manuscript changes. | Defensive or evasive reply. |
| `research/P4_论文回复_response/P4_04_正式回复_tex_或_doc` | Formal response has correct format, tone, cross-reference, and change locations. | Draft text is submitted as final response. |
| `research/P4_论文回复_response/P4_05_覆盖检查` | Coverage proves every concern is answered, especially fatal and major issues. | Checks only number of replies. |
| `research/P4_论文回复_response/P4_06_修改证据` | Each change has diff, experiment, figure, table, or text evidence. | Says changed without proof. |
| `research/P4_论文回复_response/P4_07_再投稿打包` | Bundle manifest lists manuscript, response, evidence, figures, tables, and metadata; all files exist. | Package has missing or mixed-version assets. |
