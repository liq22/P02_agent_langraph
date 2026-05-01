# 自动化高水平研究验收 checklist（P0-P4 + submission gate）

> 融合来源：`_reference/_update2/checklist.md` 与 `_reference/_update2/checklist2.md` `_reference/_update2/checklist_merge.md`。
> 本文件是合并优化版；原始素材文件不得作为本次合并的一部分被修改。

---

## 0. 使用方式与硬边界

### 0.1 这不是“文档存在性检查表”

本 checklist 的判断对象不是“仓库能不能跑”“节点有没有文件”“agent 是否执行过”，而是：

- [ ] 顶级研究者是否会信任这个系统能推进真实研究，而不是制造流程幻觉
- [ ] 每个节点是否产出可验证、可交接、可复核的研究增量
- [ ] prompt / skill / flow 是否逼迫 agent 走强问题、强 baseline、强证据、强边界路径
- [ ] 下游节点、外部 reviewer、人类 PI 是否能直接消费产物，而不是重新猜测上下文

### 0.2 当前 phase 边界

- [ ] 当前仓库真实主轨是 P0-P4：项目定义、实验设计、论文撰写、模拟评审、回复与再投稿
- [ ] submission-ready 只能由最终 truth gate 判定，不能由 graph 绿色、dashboard 绿色或文件齐全代替

### 0.3 每个节点的三层验收

每个节点都必须同时通过三层检查：

- [ ] 研究质量：问题、方法、证据、边界是否足够清楚
- [ ] 技能与 prompt 完整性：`local_entry / prompt / SKILL / SOP / wrapper` 是否各司其职
- [ ] 高水平投稿适配：是否满足 Nature / TPAMI 级研究者对清晰性、可复现性、图表、评审与回复的要求

### 0.4 顶级研究者的四个核心问题

四个核心问题：

- [ ] 该节点是否把问题压到了足够清楚、可证伪、可 handoff 的粒度
- [ ] 该节点是否明确了最强 baseline、主要 metric、证据类型和失败条件
- [ ] 该节点是否会制造伪推进：表面上很忙，实际上没有可判定增量
- [ ] 该节点的输出是否能被下游节点、reviewer 或 human gate 直接消费

这里的“这个节点”指 `research/` 下所有带 `status.yaml` 的 P0-P4 schedulable research nodes。一级 phase 节点也要检查，但重点应放在会产出研究判断、实验结果、论文正文、评审结论或回复证据的 leaf / decision / execution nodes。

适用节点范围：

- [ ] P0：`P0_项目申请书`、`P0_01_研究背景与调研`、`P0_02_研究挑战与科学问题_工程问题`、`P0_03_研究内容与创新点`、`P0_04_技术路线_研究计划_OKR`、`P0_05_项目约束_资源预算_风险边界`
- [ ] P1：`P1_实验设计与仓库蓝图`、`P1_01_数据层_集中数据与子模块引用`、`P1_02_伪代码`、`P1_03_仓库蓝图`、`P1_04_核心想法轻量验证`、`P1_05_初步验证结果整理`、`P1_06_代码仓库_已有_重新初始化_子模块策略`、`P1_06_01_新仓库项目`、`P1_06_02_现有仓库接入`、`P1_06_03_子模块仓库引用`、`P1_06_04_feature_branch_修改策略`、`P1_07_优化目标_任务_评测协议`、`P1_08_预期结果与表格`、`P1_09_结果图与草稿`
- [ ] P2：`P2_论文撰写`、`P2_01_风格选择_IEEE_Elsevier_Nature`、`P2_02_初稿_md`、`P2_02_01_引言`、`P2_02_02_preliminary`、`P2_02_03_流程图草稿`、`P2_02_04_方法`、`P2_02_05_实验与讨论`、`P2_03_定稿_tex`、`P2_04_形式检查`、`P2_05_去AI味道`
- [ ] P3：`P3_论文模拟评审与修改_多轮`、`P3_01_评审轮次`、`P3_02_评价者档案`、`P3_03_批评摘要`、`P3_04_修订动作`
- [ ] P4：`P4_论文回复_response`、`P4_01_审稿意见收集`、`P4_02_问题映射矩阵`、`P4_03_逐点回复草稿_md`、`P4_04_正式回复_tex_或_doc`、`P4_05_覆盖检查`、`P4_06_修改证据`、`P4_07_再投稿打包`

优先重点审查节点：

- [ ] `P0_02_研究挑战与科学问题_工程问题`、`P0_03_研究内容与创新点`
- [ ] `P1_04_核心想法轻量验证`、`P1_05_初步验证结果整理`、`P1_07_优化目标_任务_评测协议`、`P1_09_结果图与草稿`
- [ ] `P2_02_04_方法`、`P2_02_05_实验与讨论`
- [ ] `P3_03_批评摘要`、`P3_04_修订动作`
- [ ] `P4_02_问题映射矩阵`、`P4_05_覆盖检查`、`P4_06_修改证据`、`P4_07_再投稿打包`

---

## 1. 全局自动化研究执行纪律

### 1.1 Root coordinator 职责

- [ ] root coordinator 负责拆分目标、分派最小任务、综合证据和最终判断
- [ ] root coordinator 不应变成 monolithic executor，除非任务本身局部、明显、低风险
- [ ] 每次复杂执行前必须重述目标、约束、done criteria 和最小计划
- [ ] 每个子任务必须有可验证输出，不能只给“继续推进”的泛结论

### 1.2 何时保持 single-agent

- [ ] 任务局部、文件边界清楚、风险低时保持 single-agent
- [ ] 只读融合、轻量文档整理、小范围 typo/fix 不应强行多 agent 化
- [ ] 若单 agent 已能用明确证据完成，不应为了形式制造 delegation

### 1.3 何时需要 subagent

- [ ] 任务有两个以上独立维度，且并行探索能减少不确定性
- [ ] 代码路径或执行路径不清楚，需要 read-heavy explorer
- [ ] 变更有跨模块、用户可见、数据损坏或 submission 风险
- [ ] 需要 verifier 独立复现行为或 reviewer 对抗审查

### 1.4 角色边界

- [ ] explorer：只读定位真实代码路径、所有权、依赖和事实证据
- [ ] implementer：只做最小可辩护 patch，不做机会主义重构
- [ ] verifier：执行最窄验证，记录命令、输出和失败面
- [ ] reviewer：对 correctness、regression、security、missing tests 做对抗审查

### 1.5 Delegation discipline

- [ ] 只有 root coordinator 默认可分派任务
- [ ] 不递归 fan-out，除非用户明确要求且风险需要
- [ ] 两个 write-capable agent 不得同时编辑同一文件
- [ ] patch 前必须有证据；patch 后必须有验证
- [ ] 证据弱或冲突时停止 patch，先解决歧义

### 1.6 Patch / evidence / validation discipline

- [ ] patch 必须小、局部、可回滚、可 review
- [ ] 不添加 speculative abstraction、fallback layer、compatibility shim 或额外 indirection
- [ ] 不把 opportunistic cleanup 混入主修复
- [ ] 每个 agent 必须引用具体文件、符号、命令或观察行为
- [ ] 先运行最窄充分检查，再根据残余风险扩大验证
- [ ] final response 必须报告：目标约束、agent 分工、证据、patch summary、validation、residual risk、next smallest action

---

## 2. P0：项目申请书 / 问题定义阶段

### 2.1 P0 总体验收

- [ ] 研究问题对广泛读者重要，不只是局部工程优化
- [ ] 一句话 gap 可以精确表述，并能解释 why now
- [ ] 每个节点都回答：为什么值得做、为什么难、为什么不是换皮 baseline
- [ ] 目标、预期结果、风险、资源边界在同一逻辑链中闭合
- [ ] prompt 明确要求最强相关工作、强反例、已知负结果和最强对手
- [ ] skill 鼓励收缩问题与提出判别性假设，而不是继续铺背景
- [ ] flow 结束时形成可交给 P1 的 research contract，而不是 loose notes
- [ ] lite 节点不默认要求重型 SOP 或 review gate

### 2.2 P0_01_研究背景与调研

- [ ] 背景指向明确问题，不是材料堆砌
- [ ] 相关工作按“解决了什么 / 没解决什么”组织
- [ ] prompt 要求 5-10 篇最强相关工作、3 个核心矛盾、1 个 why-now thesis
- [ ] skill 优先产出 `gap map`、`contradiction map`、`strongest baselines list` 若无法确认 strongest baseline，必须记录检索范围、候选 baseline、缺口原因与后续补证动作。
- [ ] flow 必须回答到底缺什么尚未解决。
- [ ] output 能 handoff 给 P0_02 / P0_03，而不是只生成 prose

### 2.3 P0_02_研究挑战与科学问题_工程问题

- [ ] 明确区分 scientific question、engineering problem、measurable problem
- [ ] 给出可检验的失败条件，避免把工程难点伪装成科学问题
- [ ] skill 逼出核心瓶颈与实现噪音的区别
- [ ] flow 产生最小问题树：主问题、子问题、不研究的问题
- [ ] 不允许把所有困难都列一遍当作完成；必须有优先级与删减

### 2.4 P0_03_研究内容与创新点

- [ ] 创新点需要具备问题意识，真正地解决了问题。
- [ ] 创新点不是 feature list，而是相对最强 baseline 的不可替代增量。
- [ ] 每条创新对应具体差异、证据需求、预期负例和失败解释。
- [ ] 区分主要创新与次要技术贡献，避免创新点膨胀。
- [ ] flow 形成“创新点 -> 证据类型 -> 最小实验”映射。
- [ ] reviewer 应能在 1 分钟内理解 novelty。

### 2.5 P0_04_技术路线_研究计划_OKR

- [ ] 技术路线服务于前述问题，而不是方法先行
- [ ] 阶段计划、OKR、风险分支一致
- [ ] 技术路线被压成最小阶段序列，每一步有 done condition、风险和 fallback
- [ ] flow 能映射到 P1 主链节点
- [ ] OKR 含 kill criteria：什么情况下方向应被停止或降 scope

### 2.6 P0_05_项目约束_资源预算_风险边界

- [ ] 计算预算、时间预算、实现边界、引用/数据约束、伦理/合规约束明确
- [ ] 风险、资源、人力、时间是真实约束，不是形式性条目
- [ ] skill 输出不做什么、不能承诺什么、需要人类裁决什么
- [ ] flow 产出 risk register，并将高风险事项映射到 human gate
- [ ] 约束必须能限制 P1/P2/P4 的实际行为

---

## 3. P1：实验设计与仓库蓝图阶段

### 3.1 P1 总体验收

- [ ] 所有关键实验 baseline-first
- [ ] 每个实验节点回答：baseline 是什么、metric 是什么、单轮只改什么、什么结果算 keep/discard
- [ ] task、metric、protocol、artifact、contract 可追踪
- [ ] experiment path 由 execution contract 驱动，而不是靠 agent 猜
- [ ] 执行类 skill bounded，不把 node 内 loop 偷偷上升为全局 loop
- [ ] P1 输出能进入 P1_05 做结果归一，而不是停留在跑过一些实验

### 3.2 P1_01_数据层_集中数据与子模块引用

- [ ] 数据对象、来源、split、license、version、权限和不可变约束明确
- [ ] 显式处理 leakage / contamination 风险
- [ ] 子模块和依赖可以追溯
- [ ] skill 禁止 agent 先改数据流程再说，必须先说明 lineage 与 provenance
- [ ] handoff 给 P1_02 时，清楚哪些输入已可信、哪些仍是假设

### 3.3 P1_02_伪代码

- [ ] 伪代码表达接口、不变量、关键步骤、关键变量和可消融位点
- [ ] skill 压缩为算法骨架，不偷渡具体工程实现
- [ ] flow 形成“伪代码 -> 模块 contract -> repo blueprint”的直接映射
- [ ] 不允许伪代码写成 marketing description 或口语化愿景

### 3.4 P1_03_仓库蓝图

- [ ] 目录、模块、CLI、config、artifacts、logs、failure surface 清楚
- [ ] 模块边界、输入输出和 artifact 目录支持最小可复现运行
- [ ] flow 回答 execution contract 从哪里来、谁生成、谁消费
- [ ] handoff 到 P1_04 前，蓝图足够支持最小 pilot
- [ ] 不允许一开始追求完美工程，或把 blueprint 写成概念图

### 3.5 P1_04_核心想法轻量验证

- [ ] README 保持 experiment node first 语义，不回退成 generic leaf node
- [ ] `local_entry` 先判断 contract 是否完整；缺失时只退回 contract-prep，不直接猜实验
- [ ] `local_wrapper` 只做本地 IO 绑定，不重复发明实验逻辑
- [ ] `auto_experiment_worker` 是唯一 active runtime experiment worker
- [ ] prompt 要求 baseline、primary metric、single conceptual change、keep/discard rule
- [ ] flow 形成 baseline -> one bounded experiment round -> ledger/log -> handoff decision
- [ ] 完成标准是可解释的 keep/discard 结论，而不是实验笔记数量

### 3.6 P1_05_初步验证结果整理

- [ ] 节点语义是 result-synthesis node，不是 generic review/fix node
- [ ] 读取 `results.tsv`，输出 `result_registry.yaml` 与 `hypothesis_status.yaml`
- [ ] 结果 registry 区分 positive / negative / inconclusive
- [ ] 产出 hypothesis status，而不是单纯结果堆表
- [ ] skill 围绕 evidence normalization / hypothesis decision，而不是 generic review
- [ ] flow 回答继续实验、推进写作、还是证伪归档
- [ ] handoff 到 P2 时提供结论包，而不是 raw experiment logs
- [ ] evidence 不 coherent 时明确退回 P1_04，不伪推进到写作阶段

### 3.7 P1_06_代码仓库_已有_重新初始化_子模块策略

- [ ] 明确 attach existing repo / new repo / submodule 的判定条件
- [ ] 禁止混淆研究仓库与执行仓库
- [ ] 产出 upstream ref、branch policy、sync policy、rollback plan
- [ ] 子树协调节点不做深执行
- [ ] 不允许把 P1_06 变成所有 repo 操作的垃圾桶节点

### 3.8 P1_06_01_新仓库项目

- [ ] 明确何时必须新开仓库
- [ ] 新仓库与主研究仓库的 truth 边界清楚
- [ ] baseline 在新仓库中被最小实现
- [ ] 避免在新仓库中复制研究系统语义

### 3.9 P1_06_02_现有仓库接入

- [ ] 记录现有仓库的 contract、接口、版本和依赖风险
- [ ] 不把“已有 repo 可跑”当作“已有 baseline 合格”
- [ ] 明确哪些部分可信，哪些只是复用入口
- [ ] 具备最小 rollback 方案

### 3.10 P1_06_03_子模块仓库引用

- [ ] 写清引用而不复制的边界
- [ ] 记录 upstream、patch scope、sync policy
- [ ] 说明子模块失败时主系统如何退化
- [ ] 不允许 agent 直接把子模块逻辑当本仓库真源改写

### 3.11 P1_06_04_feature_branch_修改策略

- [ ] 明确何时允许改 feature branch
- [ ] 每次 patch 有目的、diff scope 和 rollback
- [ ] 禁止为了实验方便直接污染 upstream 主线
- [ ] 具备 merge / abandon criteria

### 3.12 P1_07_优化目标_任务_评测协议

- [ ] primary / secondary outcomes 明确
- [ ] task、metric、protocol、failure signal 写清
- [ ] 评测协议能被第三方理解并复现
- [ ] wrapper 只做 protocol map 的 IO 绑定
- [ ] 不允许一个节点同时定义过多任务而没有优先级

### 3.13 P1_08_预期结果与表格

- [ ] table shell 围绕 claim 设计
- [ ] 提前定义 negative / null results 的位置
- [ ] prompt 要求 table plan、claim map、protocol map
- [ ] skill 回答哪张表支持哪个 claim
- [ ] flow 形成 protocol -> metric -> table -> figure -> writing node

### 3.14 P1_09_结果图与草稿

- [ ] 图服务 claim，而不只是可视化
- [ ] `paper_figure` 与 `result_to_claim` 分工清楚
- [ ] figure plan / claim_figure_map 可追踪
- [ ] prompt 要求 figure/table provenance
- [ ] 没有证据来源、caption 和 callout 逻辑的图不得进入最终稿

---

## 4. P2：论文撰写阶段

### 4.1 P2 总体验收

- [ ] 写作结构服从问题与证据，不是材料堆积
- [ ] 每个 P2 节点有明确 claim-evidence-section 对齐
- [ ] prompt 要求 one-sentence contribution、section role、读者 skim path
- [ ] skill 鼓励压缩、去歧义、证据对齐，而不是漫无边际改写
- [ ] Methods 足够支持第三方 replication
- [ ] Results 顺序服从论证顺序
- [ ] Figures / Tables / legends 自洽且服务 claim
- [ ] 只在必要时读取 manuscript，不让全局路由器预读全文

### 4.2 P2_01_风格选择_IEEE_Elsevier_Nature

- [ ] venue 类型、字数、图表、格式约束明确
- [ ] venue 风格转成具体结构、写作和排版约束，而不是口号
- [ ] title / abstract / figure / table / methods / data-code statements 差异明确
- [ ] flow 输出写作约束，不停在“想投 Nature / TPAMI”

### 4.3 P2_02_初稿_md（父节点）

- [ ] 它是 parent orchestration node，不是正文本体
- [ ] 负责组织、约束、汇总与评审门控，不承载完整正文
- [ ] skill 检查子节点边界冲突、空洞与重复
- [ ] 子节边界清楚，不相互吞并
- [ ] review gate 检查 section-level readiness，而不是机械要求有 review 文件

### 4.4 P2_02_01_引言

- [ ] 清楚回答问题是什么、为什么重要、现有方法哪里不够、本文贡献是什么
- [ ] prompt 包含 why-now、problem pressure、thesis statement
- [ ] flow 形成 problem -> gap -> method preview -> contribution summary
- [ ] 引言 claim 与 P0/P1 证据链一致
- [ ] 避免把结果和方法细节塞进引言

### 4.5 P2_02_02_preliminary

- [ ] 只给理解本文所必需的背景
- [ ] 避免教材式扩写
- [ ] prompt 回答什么预备知识必要、什么冗余
- [ ] 定义、符号、假设与方法部分一致
- [ ] 不把方法细节误塞进 preliminary

### 4.6 P2_02_03_流程图草稿

- [ ] 图帮助方法理解，而不是重复正文
- [ ] prompt 要求图的 purpose，而不是只要求“有图”
- [ ] caption / legend 自解释
- [ ] 图绑定 claim、caption、figure callout 和 provenance
- [ ] 没有证据来源和 callout 逻辑的图不得进入最终稿

### 4.7 P2_02_04_方法

- [ ] 方法核心假设、模块、输入输出、复杂度和边界明确
- [ ] 研究设计、实现细节、统计与复现信息写全
- [ ] claim-equation-algorithm 对齐
- [ ] flow 回答方法创新落在哪一层
- [ ] 不允许方法段落只写框架口号而没有可执行骨架

### 4.8 P2_02_05_实验与讨论

- [ ] 按结果 -> 含义 -> 限制组织
- [ ] prompt 要求主结果、消融、失败案例、局限性
- [ ] 每张表/图都有对应 claim
- [ ] 失败结果、负结果、边界条件得到诚实处理
- [ ] 避免过度 claim 和只堆数字而不做判别性讨论

### 4.9 P2_03_定稿_tex

- [ ] 明确它是发布版排版真源
- [ ] 导出同步只服务 venue 提交目标
- [ ] 检查 section_map / sync_map 一致
- [ ] 防止 md/tex 双轨漂移
- [ ] 不允许 tex 只是复制 md 而无正式排版约束

### 4.10 P2_04_形式检查

- [ ] 检查范围覆盖引用、图表、符号、一致性、格式错误
- [ ] 只输出高置信、可执行问题
- [ ] formal issues 结构化为 actionable fix list
- [ ] formal pass 不得掩盖 scientific weakness

### 4.11 P2_05_去AI味道

- [ ] 目标是去模板腔，不是去清晰度
- [ ] 更清楚、更克制、更可读，而不是简单同义改写
- [ ] 保留 technical precision
- [ ] 修改限定在 style / rhetoric 层，不偷改 scientific claims
- [ ] “更像人类”不得以牺牲可验证性为代价

---

## 5. P3：论文模拟评审与修订阶段

### 5.1 P3 总体验收

- [ ] 节点设计真的帮助发现 reviewer 关注点
- [ ] 每条 critique 带 claim、evidence、location、actionable fix
- [ ] skill 禁止 same-author / same-worker 伪独立评审
- [ ] critique / digest / revision map 形成闭环
- [ ] review 被 atomize 成 issue，而不是大段情绪化反馈
- [ ] review gate 不被默认施加到所有节点
- [ ] review 产物能被 P4 直接消费

### 5.2 P3_01_评审轮次

- [ ] 定义一轮评审的目标、输入、输出
- [ ] 不同类型 reviewer 的轮次清楚
- [ ] flow 产出 round summary、critical issues、action list
- [ ] 不允许只记录“进行了第 N 轮”而无质量增量

### 5.3 P3_02_评价者档案

- [ ] reviewer profile 真实区分理论型、系统型、审稿严格度
- [ ] profile 能映射到预期 critique 维度和 critique 风格
- [ ] reviewer profile 服务 issue diversity，而不是人设装饰
- [ ] standard 节点的 `SKILL.md` 只写局部策略

### 5.4 P3_03_批评摘要

- [ ] 评论按根因去重、聚类，标记 severity 和冲突
- [ ] 区分 blocking / non-blocking / cosmetic
- [ ] `aggregate_reviews` 可辅助，但不得把聚合误当成完整 review round
- [ ] 输出可 handoff 的 critique cluster
- [ ] 不允许把关键强反对意见在聚合中磨平

### 5.5 P3_04_修订动作

- [ ] 每个 action 绑定 critique source、目标节点、预期证据
- [ ] critique 真正转成 action map
- [ ] action 是可执行对象，而不是 loose TODO
- [ ] 形成 comment -> action -> evidence -> file location 链条
- [ ] action 能 handoff 给 P2 / P4 / experiment node

---

## 6. P4：论文回复与 rebuttal 阶段

### 6.1 P4 总体验收

- [ ] point-by-point response 真实闭环
- [ ] 每条 response 有 direct answer、evidence refs、manuscript location、commitment status
- [ ] critique-response-evidence-manuscript 链条完整
- [ ] 回复、正文、修改证据、再投稿打包一致
- [ ] 无法绑定证据时只能写 unresolved blocker，不能假装已覆盖

### 6.2 P4_01_审稿意见收集

- [ ] reviewer / editor comments 统一结构化
- [ ] 保留原始 critique 的 source id 与 provenance
- [ ] 先归档原意，不先改写再归档
- [ ] 形成后续映射所需的原始评论真源
- [ ] 不在这里提前“解释掉”审稿意见

### 6.3 P4_02_问题映射矩阵

- [ ] 节点语义是 mapping node，不是 generic 正文/review/fix 节点
- [ ] prompt 要求 critique id、response item、evidence refs、manuscript location、commitment status
- [ ] skill 优先做映射与缺口识别，而不是正文写作
- [ ] flow 输出 response matrix，不停在散乱评论与回复草稿
- [ ] comment -> issue -> action -> evidence -> location 完整
- [ ] 无法映射到 evidence/location 的 critique 必须显式标 blocker

### 6.4 P4_03_逐点回复草稿_md

- [ ] prompt 要求 point-to-point structure
- [ ] 每条回复先回应，再说明修改
- [ ] 一条 critique 对应一条 response block
- [ ] 避免“整封信式”泛回复
- [ ] 不把未批准实验或数字写成已完成承诺

### 6.5 P4_04_正式回复_tex_或_doc

- [ ] 正式格式、礼貌度、审稿规范明确
- [ ] 与草稿和 evidence 保持一致
- [ ] 保留 evidence 与 manuscript change traceability
- [ ] formal polish 不覆盖 factual mismatch

### 6.6 P4_05_覆盖检查

- [ ] 每条 comment 有 covered / uncovered / partially covered 判定
- [ ] 每条 response 有证据与落点
- [ ] coverage pass 能阻断“写了很多但没回关键问题”
- [ ] evidence 为空时不得误判完成

### 6.7 P4_06_修改证据

- [ ] 记录 diff、figure/table provenance、manuscript location、claim impact
- [ ] “改了什么”与“为什么改”绑定
- [ ] 修改位置可定位
- [ ] 输出 reviewer 可验证的 evidence package
- [ ] 证据节点不扩成第二份回复正文

### 6.8 P4_07_再投稿打包

- [ ] 覆盖 manuscript、response、evidence、figures、metadata、venue package
- [ ] submission assets 齐全，命名、格式、清单一致
- [ ] package readiness 与 final truth gate 分开
- [ ] package 层面做最终一致性检查
- [ ] 不允许“所有文件都在”就被当成 submission-ready

---

## 7. Submission Gate：伪 P5 / Final Truth Gate

### 7.1 研究 truth gate

- [ ] 所有核心 claims 都能追到证据
- [ ] 所有 claims 都可证伪、不过度、不过界
- [ ] 所有 figures / tables 都有 provenance
- [ ] 所有引用都通过 citation gate
- [ ] manuscript、response、evidence、artifact 四者一致
- [ ] 不存在 framework pass 但 paper truth 不通过的错觉

### 7.2 外部评审 gate

- [ ] 顶级投稿默认建议启用 external review gate
- [ ] external reviewer 与 authoring worker 独立
- [ ] `review/verdict.yaml` 不能仍是 revise/block 占位状态
- [ ] hard fail 必须被真实关闭，而不是降级措辞掩盖
- [ ] 对强反对意见有证据回应或明确 unresolved blocker

### 7.3 Reproducibility gate

- [ ] execution contract 可复现
- [ ] baseline 可重跑
- [ ] result ledger 可解释
- [ ] 数据来源、split、环境、随机性、artifact 路径可追踪
- [ ] 关键实验的 keep/discard 决策有审计轨迹

### 7.4 Packaging gate

- [ ] venue 格式、metadata、匿名化/署名状态正确
- [ ] manuscript package、response package、evidence package 一致
- [ ] figures、tables、supplementary、code/data statement 对齐
- [ ] submission package 不含过期草稿、冲突版本或未解释缺口

---

## 8. 全局 skills / flow 附加检查

### 8.1 `auto_research_campaign`

- [ ] 只做宽 prompt -> bounded campaign step
- [ ] 不默认全栈读取所有节点
- [ ] 按 node mode 决定 deeper read
- [ ] 不替代 orchestrator、worker 或 reviewer
- [ ] 输出一个可验证的单轮推进结果

### 8.2 `graph_driven_research_orchestrator`

- [ ] 只做 graph-level routing round
- [ ] 不预读正文
- [ ] 不吸收节点内策略
- [ ] 选择 exactly one actionable node
- [ ] 刷新 scheduler graph 后报告 scheduling delta

### 8.3 `auto_experiment_worker`

- [ ] 只做 experiment execution
- [ ] 不猜 contract
- [ ] baseline-first、metric-driven、bounded
- [ ] 只写 node-local ledger 与状态
- [ ] 不把轻量实验扩大成全局研究循环

### 8.4 Darwin / queue / never-stop

- [ ] 优先优化高杠杆真源
- [ ] 不被海量 node-local 变体淹没
- [ ] never-stop 是 bounded ratchet，不是全局失控
- [ ] 每个自动推进回合都有 stop condition、budget 和 evidence output

---

## 9. 顶尖学者论文生成总验收

### 9.1 问题与贡献

- [ ] 论文能用一句话说明核心问题、关键 gap 和不可替代贡献
- [ ] 贡献不是功能列表，而是相对最强 baseline 的证据化增量
- [ ] 读者不用学习内部框架黑话即可理解研究主张
- [ ] 负结果、边界条件和失败路径不被隐藏

### 9.2 方法与实验

- [ ] 方法部分足以让第三方复现关键逻辑
- [ ] 实验协议提前定义，而不是根据结果倒写
- [ ] baseline 强、metric 合理、ablation 指向机制
- [ ] 每个实验结果能支持一个明确 claim
- [ ] inconclusive 或 negative result 有解释和后续决策

### 9.3 图表与论证

- [ ] 每张图表都有 provenance、claim、caption、正文 callout
- [ ] 图表顺序服从论证顺序，不服从生成顺序
- [ ] legend 自解释，读者脱离正文仍能理解主要信息
- [ ] 表格不是数字堆积，而是 claim 的审计面

### 9.4 写作与风格

- [ ] 引言快速建立 problem pressure、gap、thesis 和 contribution
- [ ] preliminary 最小足够，不做教材化扩写
- [ ] 方法、实验、讨论边界清楚
- [ ] 去 AI 味不损伤技术精度和可验证性
- [ ] venue 风格落实为结构约束，而不是语气模仿

### 9.5 评审与回复

- [ ] critique 被原子化为可执行 issue
- [ ] revision action 与 critique source、evidence、location 绑定
- [ ] rebuttal 每条先 direct answer，再说明修改和证据
- [ ] response matrix 可追踪 comment -> action -> evidence -> manuscript location
- [ ] 未解决事项明确 blocker，不伪装成已覆盖

### 9.6 自动化可信度

- [ ] agent 的每次推进有输入、输出、证据、验证和停止条件
- [ ] 系统减少机械劳动，而不是增加内部流程复杂性
- [ ] 自动化不替代科学判断；高风险 claim、submission、ethics、scope 由 human gate 裁决
- [ ] 没有证据时系统倾向于停下或退回上游，而不是继续生成文本

---

## 10. 最终一句话验收标准

一个 Nature / TPAMI 级别研究者第一次打开仓库后，不需要先学一套内部黑话，就能：

- [ ] 理解系统当前状态
- [ ] 知道下一步该进哪个节点
- [ ] 看懂该节点真正的目标、完成定义与默认下一跳
- [ ] 发起一次 bounded research step
- [ ] 判断当前节点是否过重、过薄或重复
- [ ] 追踪 claim、evidence、experiment、manuscript、response 的闭环
- [ ] 相信这个系统是在提高研究质量和减少机械劳动，而不是制造更复杂的内部框架
