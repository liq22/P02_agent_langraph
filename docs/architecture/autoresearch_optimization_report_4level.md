# Autoresearch 仓库优化内容报告（四级标题版）

本报告把当前仓库作为一个完整的 research OS / agent cockpit / node-skill workflow 审视。核心判断是：仓库已经具备 folder-backed research、minimal graph、explicit relations、bounded skills、Canvas projection、web cockpit 的骨架；当前主要问题不是缺模块，而是多个正确模块尚未完全收敛到一个低认知负担的研究路径。

## 1. 仓库优化总目标与边界

### 1.1 优化目标

优化不是增加更多页面、技能或 projection，而是让研究者更快进入当前 node，更少理解系统本身。

#### 1.1.1 研究者进入仓库后的主路径

用户打开系统后，应从当前 scheduler frontier 进入当前 node 的有界研究动作。

##### 1.1.1.1 本节应包含的内容

- 看到当前 phase 与 next node。
- 进入当前 node。
- 查看 node 的 manuscript、status、files、relations。
- 打开该 node 的 bounded session。
- 让 agent 在明确上下文里执行一个有限动作。
- 保存或回写研究产物。
- 刷新 graph/projection，进入下一轮。

#### 1.1.2 优化成功的定义

成功不是信息更多，而是路径更短、内容更安全、上下文更可审计。

##### 1.1.2.1 本节应包含的内容

- 从进入前端到打开当前 node：不超过 1 次主要选择。
- 从进入前端到开始 node session：不超过 2 次点击。
- 从进入前端到编辑 manuscript：不超过 1 次 tab 切换。
- 未保存 manuscript 不会被静默覆盖。
- agent session 的上下文一眼可见。
- graph 仍然只是 scheduler，不成为内容数据库。

### 1.2 不可推翻的 core 边界

这些边界已经正确，优化不能误伤。

#### 1.2.1 结构边界

各目录和文件只保留单一 owner。

##### 1.2.1.1 本节应包含的内容

- `research/` 是研究工作真源。
- `backend/graph/` 是最小 JSON 调度层和派生 projection 层。
- `backend/relations/edge_registry.json` 是显式跨节点关系真源。
- `.agent/skills/` 是全局技能层。
- `obsidian/` 是 Canvas IDE。
- `web/app/` 是 agent cockpit。
- `backend/agent_gateway/app.py` 是 app runtime 入口。

#### 1.2.2 行为边界

前端和 gateway 都不能接管研究真源或全局调度。

##### 1.2.2.1 本节应包含的内容

- 前端不重新推导 scheduler。
- 前端不直接扫描 `research/**` 来生成业务事实。
- Canvas 不成为第二真源。
- agent cockpit 不接管 global orchestration。
- bounded worker 不变成 global router。
- `graph.json` 不承载 manuscript、review 正文或长上下文。

### 1.3 奥卡姆剃刀原则

本轮只删除偶然复杂性，不误伤科研流程的本质复杂性。

#### 1.3.1 本质复杂性

这些复杂性来自研究工作本身，不能删除。

##### 1.3.1.1 本节应包含的内容

- P0-P4 研究流程复杂性。
- node status / review / manuscript / files / relations 的真实差异。
- general / scope / node 三类 session。
- bounded agent execution。
- manuscript 编辑安全。
- graph projection 与 Canvas projection。

#### 1.3.2 偶然复杂性

这些复杂性来自实现和迁移过程，应删除或压缩。

##### 1.3.2.1 本节应包含的内容

- 同一状态在顶部、左栏、右栏重复展示。
- 前端文档和代码叙事不一致。
- 旧 `scope rail / board` 语言残留。
- 右侧 drawer 语义残留但实现不统一。
- placeholder 承诺超出实际实现能力。
- 树导航承担过多状态语义。
- manuscript 可写但缺少足够安全栅栏。

## 2. 当前仓库现状复盘

### 2.1 当前架构已经成立的部分

优化时应保留已经稳定的方向。

#### 2.1.1 Core architecture 已基本稳定

当前架构边界已经能支撑 research OS 的主路径。

##### 2.1.1.1 本节应包含的内容

- `research/` 仍是 work layer。
- minimal graph 仍是 scheduler summary。
- Canvas 仍是 human IDE / workbench。
- auto experiment / autoresearch 类 worker 保持 bounded worker 边界。
- projection layer 提供 `hierarchy.json`、`node_details.json`、`scope_rollup.json`、`board_state.json`。

#### 2.1.2 Agent cockpit app 已经具备产品表面

`web/app` 和 gateway 已经具备最小可用链路。

##### 2.1.2.1 本节应包含的内容

- FastAPI gateway 提供 `/api/*`。
- Web app 读取 graph/status/projection。
- 支持 agent catalog。
- 支持 session creation / execution / log polling。
- 支持 node/scope/general session。
- 支持 manuscript GET/PUT API。

### 2.2 当前已经发生的前端转向

前端已从 dashboard 叙事转向四 tab research workbench。

#### 2.2.1 四 tab 主工作台

当前主界面是 `Overview / Node / Manuscript / Session`。

##### 2.2.1.1 本节应包含的内容

- `Overview` 看结构和流向。
- `Node` 理解当前节点。
- `Manuscript` 编辑当前 node 的 `docs/manuscript.md`。
- `Session` 在当前上下文内执行 bounded agent action。

#### 2.2.2 DOM contract 显式化

当前代码已经开始防止 HTML/JS 漂移。

##### 2.2.2.1 本节应包含的内容

- `app.js` 中存在 DOM contract 检查。
- 缺失核心 DOM id 会 fail fast。
- 这比静默渲染失败更可靠。
- 后续优化必须保留 contract-first 思路。

### 2.3 当前主要不一致

最大风险是多套叙事并存。

#### 2.3.1 文档与代码不一致

旧文档需要从 `scope rail / board workspace / node inspector / agent cockpit` 迁移到当前 canonical IA。

##### 2.3.1.1 本节应包含的内容

- 当前代码已转向 `Tree Navigator / Main Workbench / Context Drawer`。
- `frontend_optimization_plan_4level.md` 不应继续描述旧三模式结构。
- 后续协作者应以 `web/app/*`、gateway acceptance、browser smoke 为准。

#### 2.3.2 运行态、截图态、源码态不一致

截图只能作为同一 commit 的证据，不是真源。

##### 2.3.2.1 本节应包含的内容

- 每次前端评审注明 branch / commit。
- 截图必须来自同一 commit 的本地运行结果。
- 排查浏览器缓存、未提交改动、构建残留。
- 不允许基于旧截图继续设计新方案。

## 3. 前端 Agent Cockpit 优化报告

### 3.1 首屏主路径问题

研究者进入页面后应立刻知道现在做什么。

#### 3.1.1 顶部控制面

Topbar 只保留全局摘要和少量 utility。

##### 3.1.1.1 本节应包含的内容

- 品牌信息保持轻量。
- phase / next node / runnable status 只保留一处。
- 搜索、语言、刷新不挤压主 CTA。
- 不保留顶部 workspace select。
- 心跳状态只是辅助状态。

#### 3.1.2 中央主动作

`打开会话` 是唯一主 CTA。

##### 3.1.2.1 本节应包含的内容

- `打开会话` 为唯一主动作。
- `更多操作` 降级为 secondary actions。
- Pin / Focus next / Back / Relations 不干扰主路径。
- 从当前 node 到 Session 足够直接。

### 3.2 左侧 Tree Navigator 问题

左侧只回答“我去哪”。

#### 3.2.1 树行信息预算

每个树行只保留导航必要信息。

##### 3.2.1.1 本节应包含的内容

- 必须显示 title、缩进、展开状态。
- 允许显示 status dot、next、blocked。
- 不常驻显示 pinned、session target、flags、长文本 badge。
- 树标题不应中文竖向碎裂。
- 超过两行应截断。

#### 3.2.2 树状态连续性

树展开状态必须跨刷新保留。

##### 3.2.2.1 本节应包含的内容

- `expandedNodeIds` 写入 `localStorage`。
- 刷新页面后保留展开路径。
- `next_node` path 自动展开。
- collapse all 与 expand active path 行为可预测。

### 3.3 中央四 tab 工作台问题

每个 tab 只承担一个主对象。

#### 3.3.1 Overview

Overview 只负责结构理解。

##### 3.3.1.1 本节应包含的内容

- 显示 hierarchy graph。
- 支持 scope drill-down。
- 支持局部 dependency overlay。
- 不常驻 setup diagnostics。
- 不承担 board / session / inspector 职责。

#### 3.3.2 Node

Node tab 只解释当前节点。

##### 3.3.2.1 本节应包含的内容

- 显示 status、truth status、progress、heartbeat、review。
- 显示当前 node 的 files / relations 概览。
- 深层 files / local skills / diagnostics 移入右侧 drawer。
- 不形成中央双主屏。

#### 3.3.3 Manuscript

Manuscript 是可信写作面，不是 demo。

##### 3.3.3.1 本节应包含的内容

- 只编辑当前 node 的 `docs/manuscript.md`。
- 有 dirty state。
- 切 node、刷新、离页前保护未保存内容。
- 支持 `Ctrl/Cmd+S`。
- preview 至少支持基础 markdown 语义。
- Save / Revert / Reload 语义清楚。
- 不扩张成全仓通用文件编辑器。

#### 3.3.4 Session

Session 是 graph-bound execution surface。

##### 3.3.4.1 本节应包含的内容

- 支持 general / scope / node 三类 session。
- 当前 session header 显示绑定上下文。
- action chips 不隐藏 boundedness。
- run disabled 时显示具体 block reason。
- session list 只显示当前上下文相关会话。
- session log 清晰显示执行结果。

### 3.4 右侧 Context Drawer 问题

右侧只放辅助上下文。

#### 3.4.1 Drawer 职责

Drawer 不承载主工作流。

##### 3.4.1.1 本节应包含的内容

- quick metadata。
- files。
- local skills。
- incoming / outgoing relations。
- setup diagnostics。
- 当前 node/session 的简短 context。

#### 3.4.2 Drawer 状态

Drawer 默认折叠，异常时提示。

##### 3.4.2.1 本节应包含的内容

- 默认可折叠。
- 抽屉开合状态持久化。
- 正常状态下不抢中心视觉。
- projection/config/agent 异常时自动提示。
- 不在右侧放完整 session log。

## 4. Backend Graph 与 Projection 优化报告

### 4.1 Minimal graph 边界

`graph.json` 和 `graph_status.json` 保持 scheduler 层。

#### 4.1.1 `graph.json`

Graph 只表达调度结构。

##### 4.1.1.1 本节应包含的内容

- node 只保留 path/status。
- edge 只保留 src/rel/dst。
- 不加入 manuscript、review 正文、长摘要。
- 不加入 owner、priority、tags。
- 所有复杂内容回到 node 文件夹。

#### 4.1.2 `graph_status.json`

Graph status 只表达 scheduler summary。

##### 4.1.2.1 本节应包含的内容

- current_phase。
- next_node。
- ready_nodes。
- blocked_nodes。
- unfinished_count。
- 不承载 UI-only 状态。
- 不承载 agent session 状态。

### 4.2 Projection 层优化

Projection 是前端读模型，不是真源。

#### 4.2.1 `hierarchy.json`

供 Tree Navigator / Overview 使用。

##### 4.2.1.1 本节应包含的内容

- 稳定 id。
- name/path/children。
- parent path 查找。
- 定位 `next_node` 路径。
- 避免冗余重字段。

#### 4.2.2 `node_details.json`

供 Node tab / Drawer / tooltip 使用。

##### 4.2.2.1 本节应包含的内容

- status、lifecycle、progress、heartbeat。
- review gate。
- files、local skills。
- readme/status path。
- flags。
- 只提供 UI 摘要，不塞正文。

#### 4.2.3 `scope_rollup.json`

只服务 scope-level health summary。

##### 4.2.3.1 本节应包含的内容

- children_count、leaf_count。
- ready_count、blocked_count。
- review_due_count、active_count。
- diagnostics count。
- 不承担 node detail 职责。

#### 4.2.4 `board_state.json`

Board 是 projection，不是第五个主工作模式。

##### 4.2.4.1 本节应包含的内容

- 如果产品已转向四 tab，board 降级为 active-set 数据。
- 不恢复 board tab。
- active_set 只可作为 drawer 或 overview 的辅助信号。

## 5. Agent Gateway 与 Session Runtime 优化报告

### 5.1 Gateway API 边界

Gateway 是薄运行层，不是第二后端平台。

#### 5.1.1 Graph APIs

Graph/projection API 只读。

##### 5.1.1.1 本节应包含的内容

- `/api/app/bootstrap`
- `/api/graph/status`
- `/api/graph/structure`
- `/api/graph/hierarchy`
- `/api/graph/details`
- `/api/graph/rollup`
- `/api/graph/board`
- 失败时错误带 missing 文件列表。
- bootstrap 区分 graph_ready / full_projection_ready / can_run_agents。

#### 5.1.2 Manuscript APIs

只支持当前 node 的 manuscript。

##### 5.1.2.1 本节应包含的内容

- `GET /api/node/{node_id}/manuscript`
- `PUT /api/node/{node_id}/manuscript`
- node_id 通过 graph 校验。
- path 限制在 `research/` 内。
- 只写 `docs/manuscript.md`。
- 返回 updated_at。

### 5.2 Session runtime

Session 绑定上下文，不是无界聊天。

#### 5.2.1 Session metadata

每个 session 必须可审计。

##### 5.2.1.1 本节应包含的内容

- session_id、agent、session_type。
- target_node、target_scope。
- context_key、context_label、context_path。
- command、log_path、status。

#### 5.2.2 Session log location

日志靠近上下文，同时可恢复。

##### 5.2.2.1 本节应包含的内容

- node/scope session log 写入对应 research context 下。
- general session 写入 artifacts。
- restore_from_disk 能恢复历史 session。
- 不把 session log 写入 graph。

#### 5.2.3 Run blocked reason

前端必须在运行前知道为什么不能运行。

##### 5.2.3.1 本节应包含的内容

- graph missing。
- projection missing。
- example config。
- missing binary。
- missing target node。
- unknown node。
- missing prompt。
- session already running。

## 6. Obsidian Canvas IDE 优化报告

### 6.1 Canvas 职责

Canvas 只做 human IDE projection。

#### 6.1.1 Canvas 应显示什么

Canvas 适合低频、高层、空间组织。

##### 6.1.1.1 本节应包含的内容

- research hierarchy。
- node relation。
- proposal workspace。
- method relation。
- human planning notes。
- 不承载 session runtime。
- 不成为 source of truth。

#### 6.1.2 Canvas 不应显示什么

避免 Canvas 变成第二系统。

##### 6.1.2.1 本节应包含的内容

- 不塞入所有 status 细节。
- 不复制 manuscript 正文。
- 不放 session log。
- 不手工维护 graph truth。
- 不手工维护 edge registry 副本。

### 6.2 Canvas 与 Web App 的关系

两者都是 projection consumer，但服务不同心智模式。

#### 6.2.1 Canvas 面向规划

Canvas 用于路线理解、proposal/method mapping 和人工思考。

##### 6.2.1.1 本节应包含的内容

- Canvas 用于路线理解。
- Canvas 用于 proposal / method mapping。
- Canvas 用于人工重排和思考。
- Canvas 不负责实时执行。

#### 6.2.2 Web App 面向执行

Web app 适合高频状态、session、写作。

##### 6.2.2.1 本节应包含的内容

- Web app 看状态。
- Web app 进 node。
- Web app 写 manuscript。
- Web app 开 session。
- Web app 读 logs。
- Web app 暴露 setup diagnostics。

## 7. Research Node 体系优化报告

### 7.1 Node 文件夹协议

每个 node 是最小研究单元。

#### 7.1.1 必需文件

最小 node contract 服务入口、状态和验收。

##### 7.1.1.1 本节应包含的内容

- `README.md`：入口、边界、done criteria、TODO。
- `status.yaml`：状态与进度。
- `docs/manuscript.md`：当前 node 正文。
- `skills/local_entry.md`：本地技能入口。
- `prompts/research_prompt.md`：节点主研究 prompt。
- `prompts/acceptance_checklist.yaml`：验收标准。

#### 7.1.2 可选文件

按节点类型存在，不作为所有节点强制负担。

##### 7.1.2.1 本节应包含的内容

- `docs/HUMAN_ONLY.md`
- `prompts/review_rubric.yaml`
- `skills/SKILL.md`
- `skills/SOP.md`
- `skills/local_wrapper.md`
- `skills/local_execution.md`
- `artifacts/*`
- `review/*`
- `logs/agent_sessions/*`

### 7.2 Node 状态协议

状态字段必须少而稳定。

#### 7.2.1 status.yaml 最小字段

状态服务 scheduler 和人类判断。

##### 7.2.1.1 本节应包含的内容

- status、truth_status、progress。
- lifecycle_stage、heartbeat、last_actor。
- can_enter_fix。
- review gate summary。
- 不把长评论和正文塞进 status。

#### 7.2.2 状态变更规则

状态变化必须可追踪。

##### 7.2.2.1 本节应包含的内容

- 状态变更需要 actor。
- 重要状态变化需要 heartbeat。
- review/fix/done 需要 evidence。
- 不允许 silent state mutation。
- 状态变更后刷新 graph/projection。

### 7.3 P0-P4 阶段节点优化

协议统一，研究任务不同。

#### 7.3.1 P0 项目申请书

关注问题定义、动机、路线、约束。

##### 7.3.1.1 本节应包含的内容

- 背景可进入 manuscript。
- 科学问题明确。
- 创新点和约束对应。
- 项目边界可评审。
- local prompt 针对项目申请书。

#### 7.3.2 P1 实验设计与仓库蓝图

关注数据、伪代码、仓库、实验、验证链路。

##### 7.3.2.1 本节应包含的内容

- 数据对象清楚。
- 伪代码能转向代码仓库。
- 仓库蓝图有模块边界。
- 实验矩阵可执行。
- negative result / keep-discard 可记录。

#### 7.3.3 P2 论文撰写

关注章节写作、claim-evidence、figures、citation。

##### 7.3.3.1 本节应包含的内容

- 每个章节有 node manuscript。
- claim 有 evidence。
- citation 可验证。
- figure 有 manifest。
- 语言去 AI 套话。

#### 7.3.4 P3 模拟评审与修改

关注多轮 review、issue register、revision action。

##### 7.3.4.1 本节应包含的内容

- review issue 结构化。
- critique 映射 action。
- 修改有 evidence。
- hard fail 明确。
- 可进入 response 阶段。

#### 7.3.5 P4 回复与再投稿

关注 response mapping 和 package。

##### 7.3.5.1 本节应包含的内容

- 问题映射矩阵。
- response item。
- revision evidence。
- cover letter。
- resubmission package。
- coverage check。

## 8. Skills 与 Prompt 体系优化报告

### 8.1 全局 skills

`.agent/skills/` 保留 canonical 能力。

#### 8.1.1 Orchestrator 类 skill

只做路由，不做具体研究执行。

##### 8.1.1.1 本节应包含的内容

- 只读 graph/status。
- 选择 next node。
- 进入 local_entry。
- 避免读取大正文。
- 避免成为 global executor。

#### 8.1.2 Worker 类 skill

只做一个边界清晰的任务。

##### 8.1.2.1 本节应包含的内容

- manuscript worker。
- experiment worker。
- citation verifier。
- response worker。
- review loop。
- result-to-claim。
- 每个 worker 有明确输入/输出/停止条件。

### 8.2 本地 skills

每个 node 需要 local_entry，但不一定需要复杂本地执行 skill。

#### 8.2.1 local_entry

本地入口只做路由和节点约束。

##### 8.2.1.1 本节应包含的内容

- node 目标。
- 必读文件。
- 可选文件。
- 可调用 global skill。
- node-specific caveats。
- 不把完整研究内容写进 local_entry。

#### 8.2.2 local_wrapper / local_execution

只有需要转换 IO 或执行本地命令时才存在。

##### 8.2.2.1 本节应包含的内容

- 是否真的需要 wrapper。
- 是否只是复制 global skill。
- 是否只有名字不同。
- 是否有 input/output contract。
- 是否有 execution binder。

### 8.3 Prompt assets

Prompt 是科研质量的核心，不是装饰文件。

#### 8.3.1 research_prompt.md

每个 node 的主要研究任务。

##### 8.3.1.1 本节应包含的内容

- 研究问题。
- 输入材料。
- 输出格式。
- 质量标准。
- 禁止项。
- 和 P0-P4 当前阶段的关系。

#### 8.3.2 acceptance_checklist.yaml

验收标准必须可判定。

##### 8.3.2.1 本节应包含的内容

- 必须完成什么。
- 如何判定通过。
- 如何判定失败。
- 缺什么 evidence 会阻断。
- agent/human 共同理解。

## 9. 文档体系优化报告

### 9.1 README 优化

README 说明仓库是什么、如何启动、如何进入研究。

#### 9.1.1 README 主叙事

仓库是 folder + graph + skills 的 research OS。

##### 9.1.1.1 本节应包含的内容

- 研究真源在 `research/`。
- graph 是 scheduler。
- skills 是执行能力。
- Canvas 是人类 IDE。
- Web app 是 agent cockpit。
- 如何从 next node 开始工作。

#### 9.1.2 README 快速启动

一条路径启动系统。

##### 9.1.2.1 本节应包含的内容

- 安装依赖。
- refresh views。
- 启动 gateway。
- 打开 `/app/`。
- 配置 agent gateway。
- 常见错误修复。

### 9.2 Architecture docs 优化

架构文档必须和当前代码一致。

#### 9.2.1 废弃旧前端叙事

清理 `scope rail / board workspace` 等旧描述。

##### 9.2.1.1 本节应包含的内容

- `agent_cockpit_app.md`
- `agent_cockpit_v2.md`
- `frontend_optimization_plan_4level.md`
- 统一为 Global Scheduler Bar / Tree Navigator / Main Workbench / Context Drawer。
- 四 tab：Overview / Node / Manuscript / Session。

#### 9.2.2 增加 canonical UI spec

后续实现以这个 spec 为准。

##### 9.2.2.1 本节应包含的内容

- DOM contract。
- state model。
- tab duties。
- drawer duties。
- tree duties。
- manuscript safety。
- session semantics。
- verification checklist。

## 10. 测试与验收体系优化报告

### 10.1 Smoke tests

系统可用不能只靠肉眼截图。

#### 10.1.1 Gateway API smoke

API 应返回核心数据。

##### 10.1.1.1 本节应包含的内容

- `/api/app/bootstrap`
- `/api/graph/status`
- `/api/graph/hierarchy`
- `/api/graph/details`
- `/api/agents/catalog`
- `/api/node/{node_id}/manuscript`

#### 10.1.2 Frontend smoke

页面应能渲染核心区域。

##### 10.1.2.1 本节应包含的内容

- 页面不是白屏。
- Topbar 有 next node。
- Tree 有 node。
- Tab 可切换。
- Manuscript 可加载。
- Session 可显示 composer。
- Console 无阻断性错误。

### 10.2 Manuscript safety tests

内容安全必须单独验收。

#### 10.2.1 Dirty guard test

未保存内容不能被静默覆盖。

##### 10.2.1.1 本节应包含的内容

- 编辑 manuscript。
- 切换 node。
- 触发 confirm。
- 取消后内容保留。
- 确认后内容丢弃并加载新 node。

#### 10.2.2 Save shortcut test

快捷保存必须可靠。

##### 10.2.2.1 本节应包含的内容

- 在 Manuscript tab 按 `Ctrl/Cmd+S`。
- 触发 PUT API。
- dirty state 变为 saved。
- reload 后内容一致。

### 10.3 Session tests

Session 必须绑定正确上下文。

#### 10.3.1 Context binding test

node/scope/general 三类 session 不串线。

##### 10.3.1.1 本节应包含的内容

- node session 绑定 target_node。
- scope session 绑定 target_scope。
- general session 不绑定 node/scope。
- session list 只显示当前 context。
- session log 可恢复。

#### 10.3.2 Mention semantics test

placeholder 承诺必须和实现一致。

##### 10.3.2.1 本节应包含的内容

- `@current`
- `@scope`
- `@readme`
- `@status`
- `@manuscript`
- `@node`
- 每个 token 都产生可解释的上下文注入。

## 11. Code Razor 优化执行包

### 11.1 Delete

先删除重复和旧残留。

#### 11.1.1 删除前端重复控制面

一个概念只允许一个控制面。

##### 11.1.1.1 本节应包含的内容

- 顶部 workspace select。
- 左栏 scheduler cards。
- 旧 board 主模式残留。
- 未落地 drawer 样式残留，或真正恢复 drawer。
- 重复 setup diagnostics。
- 多处展示同一 session context。

#### 11.1.2 删除文档旧叙事

统一替换旧词汇。

##### 11.1.2.1 本节应包含的内容

- `scope rail` -> `Tree Navigator`。
- `Board workspace` -> active set projection，不作为主 tab。
- `Node inspector` -> Context Drawer / Node tab 摘要。
- `Agent cockpit` -> Session tab + bounded execution surface。

### 11.2 Inline

减少一次性 wrapper 和透传层。

#### 11.2.1 前端一次性函数

只在降低认知负担时保留 helper。

##### 11.2.1.1 本节应包含的内容

- 单次调用 render helper。
- 只是透传 DOM 的 wrapper。
- 过度拆分的 tiny function。
- 与渲染主体距离过远的辅助函数。

#### 11.2.2 Skill wrapper

本地 wrapper 必须有 IO 转换价值。

##### 11.2.2.1 本节应包含的内容

- 是否只是重复 global skill。
- 是否只有名字不同。
- 是否没有 node-specific constraint。
- 是否可以改成 local_entry 的一段说明。

### 11.3 Normalize

统一命名、状态、错误、返回结构。

#### 11.3.1 前端状态命名

HTML/JS/CSS 中状态名保持一致。

##### 11.3.1.1 本节应包含的内容

- `workspaceTab`
- `selectedNodeId`
- `activeScopeId`
- `currentSessionId`
- `drawerOpen`
- `manuscript.dirty`
- `expandedNodeIds`

#### 11.3.2 后端错误结构

Gateway 错误应可被前端直接展示。

##### 11.3.2.1 本节应包含的内容

- message。
- missing。
- command。
- hint。
- source。
- can_retry。

### 11.4 Make invariants explicit

关键边界必须显式检查。

#### 11.4.1 前端不变量

DOM 和状态不变量。

##### 11.4.1.1 本节应包含的内容

- 必需 DOM id 存在。
- tab value 属于 allowed set。
- session type 属于 allowed set。
- selected node 存在于 graph。
- manuscript node_id 与当前 editor 对象一致。
- dirty manuscript 不可静默覆盖。

#### 11.4.2 后端不变量

路径和 node 校验。

##### 11.4.2.1 本节应包含的内容

- node_id 必须在 graph 中。
- manuscript path 必须在 `research/` 下。
- PUT content 必须是 string。
- session target 必须有效。
- command template 必须可执行。
- projection missing 时 fail fast。

## 12. 最终优先级路线图

### 12.1 P0：先统一真源与安全

不解决会继续造成错误讨论或内容风险。

#### 12.1.1 统一文档/代码/运行态

先确认当前实现真源。

##### 12.1.1.1 本节应包含的内容

- 确认 branch 与 commit。
- 清理浏览器缓存。
- 用当前源码重新截图。
- 更新 architecture docs。
- 删除旧前端叙事。

#### 12.1.2 Manuscript safety

保护研究正文。

##### 12.1.2.1 本节应包含的内容

- dirty guard。
- beforeunload。
- `Ctrl/Cmd+S`。
- switch node confirm。
- reload confirm。
- markdown preview。

### 12.2 P1：收敛主路径

减少研究者进入研究前的决策数。

#### 12.2.1 Topbar/Tree/Workbench/Drawer 分工

四区职责固定。

##### 12.2.1.1 本节应包含的内容

- Topbar 只保留全局摘要和主 CTA。
- Tree 只导航。
- Workbench 只做当前主任务。
- Drawer 只做辅助上下文。

#### 12.2.2 Session 语义补齐

Session 兑现上下文 token。

##### 12.2.2.1 本节应包含的内容

- `@current`
- `@scope`
- `@readme`
- `@status`
- `@manuscript`
- `@node`
- 注入内容可审计。

### 12.3 P2：视觉减法

最后做风格统一。

#### 12.3.1 降低面板感

让界面从后台控制台变成研究工作台。

##### 12.3.1.1 本节应包含的内容

- 降低边框数量。
- 去重阴影。
- 去不必要渐变。
- 增加留白。
- 统一字号阶梯。
- 状态色收敛。

### 12.4 P3：验收与回归

优化完成必须可重复验证。

#### 12.4.1 最小验收清单

用行为而不是截图验收。

##### 12.4.1.1 本节应包含的内容

- 页面可加载。
- graph 可读。
- tree 可展开并持久化。
- next node 可进入。
- manuscript 不丢。
- session 可运行或明确说明不能运行。
- docs 与代码术语一致。

## 13. 报告结论

### 13.1 最终判断

当前仓库优化的核心不是加功能，而是收敛。

#### 13.1.1 关键判断

Autoresearch 仓库已经具备 research OS 的核心骨架，但仍处于半收敛状态。当前最需要优化的不是增加更多技能、更多页面或更多 projection，而是统一真源叙事、压缩前端主路径、保护 manuscript 内容安全、兑现 session 语义上下文，并用最小测试固定关键行为。

##### 13.1.1.1 本节应包含的内容

这句话是后续优化的判断锚点：先统一真源，再保护内容，再收敛语义，最后美化。

#### 13.1.2 下一步执行原则

按风险和认知负担排序。

##### 13.1.2.1 本节应包含的内容

1. 先统一文档、源码、运行态。
2. 先修 manuscript 安全。
3. 再删重复控制面。
4. 再归位 Context Drawer。
5. 再补 Session semantics。
6. 最后做视觉和审美优化。

核心原则：先删噪声，再补安全，再收敛语义，最后美化。
