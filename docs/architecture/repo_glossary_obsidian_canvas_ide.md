# 仓库项目名词、缩写解释表（obsidian-canvas-ide）

基于当前 `obsidian-canvas-ide` 分支中已经落地的 README、graph 脚本、Canvas 脚本、edge registry、sample status 和 `auto_experiment_worker` skill 整理。
目标是统一术语，减少 README / Canvas / skill / status / graph 之间的认知漂移。

---

## 1. 核心架构术语

| 术语 | 英文/标识 | 解释 | 备注 |
|---|---|---|---|
| 研究 OS | research OS | 以节点文件夹、最小 graph、skills、Canvas 为核心的研究工作系统 | 仓库自我定位 |
| Autoresearch with Human | repo name | 仓库名；强调“人类 + 智能体”共同维护研究系统 | 项目名 |
| 节点 | node | 以文件夹承载的研究单元 | 目录级原语 |
| 文件夹驱动节点 | folder-backed research node | 节点不是数据库记录，而是一个真实目录 | README 中的核心立场 |
| 父节点 | parent node | 含子节点的目录节点 | `refresh_hypergraph.py` 内部会推导 `kind=parent` |
| 叶子节点 | leaf node | 不再含子节点的末端节点 | 通常更接近可执行或正文节点 |
| 轻量节点协议 | light contract / lightweight node protocol | 节点默认只要求少量必要文件，而不是重模板 | 当前仓库方向 |
| 入口面 | entry surface | 节点的最小入口文件，通常是 `README.md` | 不等于正文 |
| 正文 | body content | 节点的实体内容，如论文草稿或长文说明 | 不写进 graph |
| 真源 | source of truth / canonical source | 最终可信的结构化文件来源 | 例如 `research/**/README.md`, `status.yaml`, `edge_registry.json` |
| 派生物 | derived / rebuildable | 可以通过脚本重建的文件 | 如 `graph.json`, `graph_status.json`, `.canvas` |
| 投影 | projection | 为人类或前端展示而生成的视图，不是真源 | Canvas 属于此类 |
| 本地优先 skill | local-first skills | 先在节点目录找 skill，再回退到全局 | README 已明确 |
| 项目级 fallback skill | project fallback skills | 放在 `.agent/skills/` 的全局后备技能 | 当前实际落点 |

---

## 2. 顶层目录与层次

| 术语 | 路径/标识 | 解释 | 备注 |
|---|---|---|---|
| 研究层 | `research/` | 真实研究工作内容所在层 | 真源层 |
| 后端层 | `backend/` | graph、relations、registry 等最小系统基底 | 不是正文层 |
| 关系层 | `backend/relations/` | 保存显式跨节点边 | 当前真源文件是 `edge_registry.json` |
| 图层 | `backend/graph/` | 保存最小 JSON 调度图和调度摘要 | 派生层 |
| 注册表 | `backend/registry/` | 保存技能目录等元数据 | 当前 README 说明它更像 registry/catalog |
| 技能层 | `.agent/skills/` | 项目级 runtime canonical skills 所在目录 | 唯一 active runtime skill truth |
| Obsidian 层 | `obsidian/` | 作为人类前端 IDE 的 projection 区 | 不是结构化真源 |
| Canvas 层 | `obsidian/canvases/` | 生成出的 `.canvas` 文件所在目录 | projection |
| 收件箱 | `obsidian/inbox/` | 暂存 proposal / 草案想法 | 更接近 scratch，而不是真源 |
| 脚本层 | `scripts/` | refresh graph / build canvas 等可执行入口 | CLI 入口层 |
| 架构文档 | `docs/architecture/` | 解释仓库架构与工作流的文档 | 推荐放长期说明 |

---

## 3. P0–P4 主轨术语

| 缩写/术语 | 解释 | 备注 |
|---|---|---|
| P0 | 项目申请书 / 研究问题与约束层 | 通常承接背景、科学问题、创新点、路线、约束 |
| P1 | 实验设计与仓库蓝图层 | 从数据层、伪代码到轻量验证、结果整理、仓库策略 |
| P2 | 论文撰写层 | 论文正文、形式检查、去 AI 味道等 |
| P3 | 模拟评审与修改层 | reviewer profiles、critique digests、revision actions |
| P4 | 回复与再投稿层 | response、coverage、evidence、resubmission |

### 常见节点中文释义

| 节点名 | 解释 |
|---|---|
| `P1_01_数据层_集中数据与子模块引用` | 数据来源、数据模式、数据引用边界 |
| `P1_02_伪代码` | 方法主流程与接口 contract |
| `P1_03_仓库蓝图` | 模块边界、文件映射、CLI/脚本布局 |
| `P1_04_核心想法轻量验证` | 正式实现前的轻量验证节点 |
| `P1_05_初步验证结果整理` | 实验结果收敛、假设状态更新与结论边界整理节点 |
| `P1_06_代码仓库_已有_重新初始化_子模块策略` | 代码仓库接入方式与 branch / submodule 策略 |
| `P2_02_初稿_md` | Markdown 版论文主稿 |
| `P2_03_定稿_tex` | LaTeX / TeX 版终稿 |
| `P3_03_批评摘要` | critique digest / review aggregation |
| `P4_02_问题映射矩阵` | critique → response_item 的映射矩阵 |
| `P4_06_修改证据` | response 与正文修改之间的证据链接 |

---

## 4. 关键文件名解释

| 文件名 | 解释 | 是否真源 |
|---|---|---|
| `README.md` | 节点入口面；写目标、规则、完成标准、TODO，而不是正文 | 是 |
| `status.yaml` | 节点执行状态、进度和 gate 信息 | 是 |
| `docs/manuscript.md` | 节点正文、长文草稿、主体内容 | 是（节点正文真源） |
| `docs/HUMAN_ONLY.md` | 人类私有内容，不默认进入 agent 读取路径 | 是，但默认 agent 不读 |
| `backend/relations/edge_registry.json` | 显式跨节点边的真源 | 是 |
| `backend/graph/graph.json` | 最小调度图 | 否，派生 |
| `backend/graph/graph_status.json` | 低 token 调度摘要 | 否，派生 |
| `scripts/refresh_views.py` | 稳定 refresh 入口；按 mode 刷新 graph 或完整 projection | 是（系统逻辑真源） |
| `scripts/refresh_hypergraph.py` | 从 research + relations 刷新 graph 的脚本 | 是（系统逻辑真源） |
| `scripts/build_canvas_from_graph.py` | 从 graph 构建 Canvas projection 的底层脚本 | 是（系统逻辑真源） |
| `*.canvas` | Obsidian Canvas 文件 | 否，projection |
| `artifacts/auto_experiment/results.tsv` | bounded auto_experiment_worker 的实验账本 | 节点本地真源 |
| `logs/auto_experiment/latest_run.log` | 最近一次实验日志 | 节点本地日志 |

### refresh 模式释义

| 术语 | 解释 |
|---|---|
| `graph_only` | 只刷新 `graph.json` 与 `graph_status.json` 的轻量模式 |
| `full` | 刷新 graph + hierarchy + node_details + scope_rollup + board_state + Canvas 的完整模式 |

---

## 5. graph / scheduler 术语

| 术语 | 英文/字段 | 解释 | 备注 |
|---|---|---|---|
| 最小 JSON 调度图 | minimal JSON scheduler graph | 当前 graph 的定位：只保留最少还能驱动路由的事实 | 不是内容数据库 |
| 节点存在 | node existence | 节点目录真实存在且满足 node 识别规则 | refresh 扫描得到 |
| 节点路径 | `path` | 节点相对仓库根目录的路径 | node 最小字段之一 |
| 节点状态 | `status` | 节点当前生命周期状态 | node 最小字段之一 |
| 边 | edge | 跨节点关系 | 当前极简三元组 |
| 源节点 | `src` | 边的起点节点 ID | edge 字段 |
| 关系类型 | `rel` | 边类型 | 当前允许 `depends_on` / `addresses` |
| 目标节点 | `dst` | 边的终点节点 ID | edge 字段 |
| 节点 ID | `node_id` | 由路径经 `"/" -> "::"` 转换得到的内部 ID | 运行时派生 |
| 当前阶段 | `current_phase` | 当前未完成主轨中最早的 phase | 来自 `graph_status.json` |
| 就绪节点 | `ready_nodes` | 当前依赖已满足、可推进的节点集合 | 调度输入 |
| 阻塞节点 | `blocked_nodes` | 依赖未满足、当前不可推进的节点集合 | 调度诊断 |
| 下一节点 | `next_node` | 当前最应推进的单个节点 | 调度输出 |
| 未完成计数 | `unfinished_count` | 处于未终结状态的节点总数 | 调度摘要 |
| refresh 成功标记 | `refresh_ok` | graph 刷新是否成功 | 调度摘要 |
| 终结状态 | terminal statuses | 当前脚本中 `done` / `archive` | 调度逻辑使用 |
| 未完成状态 | unfinished statuses | 当前脚本中 `seed / active / review / fix` | 调度逻辑使用 |

---

## 6. 关系类型解释

| 关系类型 | 解释 | 何时用 |
|---|---|---|
| `depends_on` | A 节点依赖 B 节点先完成或终结 | 调度主关系 |
| `addresses` | 当前节点处理、回应或覆盖另一个节点中的问题/批评 | P3/P4 闭环中最重要 |
| （未采用）`supports` | 支撑关系 | 当前分支未作为正式 relation type 落地 |

---

## 7. 生命周期 / 状态术语

| 状态 | 解释 |
|---|---|
| `seed` | 已建节点，但尚未真正启动 |
| `active` | 正在推进中的节点 |
| `review` | 已进入待审、聚合、评估或修订前状态 |
| `fix` | 需修复、需处理 gate 问题的状态；当前脚本接受它，但 `auto_experiment_worker` 默认不主动写入 |
| `done` | 已完成；主要用于 graph runtime 终结态 |
| `archive` | 已归档/终止，不再推进 |

### `status.yaml` 里高频字段

| 字段 | 解释 |
|---|---|
| `lifecycle.stage` | 生命周期主状态 |
| `progress_pct` | 粗粒度进度百分比 |
| `review_gate.ai_review_count` | AI review 数量 |
| `review_gate.human_review_count` | 人类 review 数量 |
| `review_gate.all_comments_responded` | comment 是否都已 response |
| `can_enter_fix` | 是否允许进入 fix |
| `heartbeat_at` | 最近心跳时间 |
| `last_actor` | 最近修改主体，如 `human` |

---

## 8. Canvas / IDE 术语

| 术语 | 解释 | 备注 |
|---|---|---|
| Obsidian Canvas | Obsidian 的画布视图格式 | 当前作为前端 IDE |
| file-first IDE | Canvas 里默认挂文件卡，而不是复制长正文 | 当前脚本已经这样做 |
| `research_overview.canvas` | 研究全景图 | phase 视图 + scheduler summary |
| `current_focus.canvas` | 当前聚焦图 | next_node、邻域、status、skills |
| `framework_workbench.canvas` | 手工工作台 | methods / skills / relations / framework proposals |
| badge | Canvas 上的轻提示，如 `missing-local-entry`、`thin-local-entry` | 脚本内由状态派生 |
| `zero-progress-active` | active 但 `progress_pct=0` 的提示 | 说明状态可能偏虚 |
| `review-not-started` | review 还没启动的提示 | 用于 IDE 诊断 |
| `missing-local-entry` | 节点缺少 `skills/local_entry.md` | 用于 IDE 诊断 |
| `thin-local-entry` | `local_entry.md` 没有声明该 tier 所需最小读取栈 | 用于 IDE 诊断 |
| `missing-node-skill` | `standard/execution` 节点缺少 `skills/SKILL.md` | 用于 IDE 诊断 |
| `missing-sop` | `execution` 节点缺少 `skills/SOP.md` | 用于 IDE 诊断 |
| `missing-execution-binder` | `execution` 节点缺少 `local_wrapper.md` 或 `local_execution.md` | 用于 IDE 诊断 |
| layout hint | 布局提示 | 推荐新增，稳定 Canvas 布局但不是真源 |

---

## 9. orchestrator / worker / skill 术语

| 术语 | 解释 | 当前语义 |
|---|---|---|
| orchestrator | 全局调度器 | 负责读 graph、选 node、路由 skill、refresh graph |
| graph-driven orchestrator | graph 驱动的全局 router | 当前 README 已明确为目标模式 |
| local skill | 节点目录里的 skill | 节点本地优先 |
| fallback skill | 项目级兜底 skill | 放在 `.agent/skills/` |
| canonical worker | 可复用的重执行 worker | 如 bounded `auto_experiment_worker` |
| bounded control unit | 一次有限控制单元 | orchestrator 一次只推进一个 node round |
| node round | 单节点一轮推进 | 选节点 → 调 skill → 回写状态 → refresh |
| local entry | 节点本地入口 skill / contract | 常见设计术语，未必每个节点都实体化为文件 |
| local wrapper | 本地包装 skill | 用来绑定 IO、路径、输出 |
| local execution | 本地重执行 skill | 少数节点才需要 |
| node archetype family | 由 `node_mode` 派生出的 family 标签，如 `lite_research_leaf_family` | 只用于 projection / 优化分组 |
| phase fallback | 按 P0–P4 回退到 phase worker | `build_canvas_from_graph.py` 中已有 fallback 映射 |

### 当前 Canvas 脚本中的 phase fallback 映射

| Phase | Fallback skill |
|---|---|
| `P0` | `idea_discovery_or_problem_formulation` |
| `P1` | `experiment_design_or_execution` |
| `P2` | `manuscript_worker` |
| `P3` | `auto_review_loop` |
| `P4` | `response_worker` |

---

## 10. auto_experiment_worker 专用术语

| 术语 | 解释 |
|---|---|
| bounded auto_experiment_worker | 有预算、有停止条件的实验 worker |
| execution contract | 调用 `auto_experiment_worker` 前绑定的最小执行契约 |
| `contract_mode` | contract 当前强度；`review_only` 只供审阅，`executable` 才允许进入 worker |
| `repo_path` | 被实验的代码仓库路径 |
| `editable_paths` | 允许编辑的文件范围 |
| `run_command` | 实验运行命令 |
| `metric.name` | 目标指标名 |
| `metric.direction` | 指标方向，如 `higher_is_better` |
| `metric.pattern` | 从日志解析指标的正则/模式 |
| `metric.min_delta` | 最小改进阈值 |
| `budget.max_rounds` | 最大实验轮数 |
| `budget.max_no_improve_rounds` | 连续无改进上限 |
| `budget.max_crashes` | 最大 crash 次数 |
| `budget.max_minutes_per_run` | 单轮最长分钟数 |
| baseline | 基线运行；第一轮必须先建 baseline |
| one-factor change | 每轮只测试一个概念变化 |
| keep | 保留该候选变更 |
| discard | 丢弃该候选变更并回退 |
| simplicity bias | 若收益相近，优先保留更简单的方案 |
| crash discipline | crash 记账，但不为坏想法无限调试 |
| ledger | 实验账本，默认 `results.tsv` |
| latest log | 最新实验日志，默认 `latest_run.log` |

---

## 11. 高价值“统一用词”建议

| 建议统一词 | 不建议混用 |
|---|---|
| 研究层 `research/` | 不要再和旧顶层 `P0–P4 + graph + relations + registry` 视图混写在根 README |
| 后端层 `backend/` | 不要与“正文/工作内容层”混写 |
| 真源 / 派生 / 投影 | 不要笼统都叫“数据” |
| 节点入口面 | 不要把 README 再叫正文 |
| bounded auto_experiment_worker | 不要再说 endless auto_experiment_worker |
| fallback skill | 不要和 canonical worker、local skill 混叫 |
| current focus | 不要和 overview canvas 混用 |
| frontier / ready leaf | 比“ready nodes 全部”更适合作为 scheduler 语言 |

---

## 12. 设计讨论高频词（不一定已全面落仓）

这些词在设计材料里高频出现，适合保留到 glossary，但要和“当前已落仓”区分开：

| 术语 | 解释 | 当前状态 |
|---|---|---|
| local_entry_skill | 节点本地入口 skill | 设计高频词，未必每个节点都已实体化 |
| local_wrapper_skill | 本地包装 skill | 设计高频词 |
| local_execution_skill | 本地重执行 skill | 设计高频词，少数节点适合 |
| progress skill | 低 token 进度评估器 | 设计高频词 |
| critique digest | 批评摘要 | P3/P4 设计高频词 |
| response coverage | 回复覆盖检查 | P4 设计高频词 |
| manual gate | 人工闸门/人工批准点 | 设计高频词 |
| claim map | claim 与表/图/证据的映射 | 设计高频词 |
| protocol map | 任务—协议—指标映射 | 设计高频词 |
| sync map | md → tex 或多表示之间的同步映射 | 设计高频词 |

---

## 13. 建议你后续固定的一套“最小简称表”

| 缩写 | 全称 | 仓库内建议解释 |
|---|---|---|
| OS | Operating System | research OS，不是传统操作系统 |
| IDE | Integrated Development Environment | 这里特指 Obsidian Canvas 前端工作台 |
| JSON | JavaScript Object Notation | graph / canvas / relations 当前主格式之一 |
| YAML | YAML Ain't Markup Language | 节点状态与部分结构化配置常用格式 |
| MD | Markdown | 文本草稿、README、技能文档常用格式 |
| TeX | TeX / LaTeX | 论文定稿排版格式 |
| CLI | Command Line Interface | `scripts/*.py` 提供的命令行入口 |
| AI | Artificial Intelligence | AI review / AI actor / agent |
| GPU | Graphics Processing Unit | 实验运行资源 |
| VRAM | Video RAM | 显存，auto_experiment_worker 里常作为软约束 |
| TSV | Tab-Separated Values | `results.tsv` 的账本格式 |
| IO | Input / Output | 本地 wrapper 常绑定输入输出路径 |
| MCP | Model Context Protocol | 若你后续在 skill 或 review 体系中继续使用，可单列说明 |

---

## 14. 推荐后续动作

1. 把这份 glossary 放到 `docs/architecture/glossary.md`
2. 根 `README.md` 只保留当前有效架构；旧“完整文档包”迁到 `docs/architecture/legacy_design_notes.md`
3. 在 Canvas 中只显示 glossary 的核心子集，不把整份表塞进画布
4. 在本地 agent prompt 里统一采用本表用词，尤其是：
   - 真源 / 派生 / 投影
   - orchestrator / worker / fallback
   - ready leaf frontier
   - bounded auto_experiment_worker
