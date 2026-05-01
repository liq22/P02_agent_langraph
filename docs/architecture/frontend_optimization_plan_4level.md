# Agent Cockpit 前端优化内容报告（四级标题版）

本报告只描述当前 `web/app/` 主 cockpit。`web/dashboard/` 是静态只读 monitor，不参与主工作台 IA。

## 1. 前端优化的第一性原理

### 1.1 前端的根本任务

前端不是 graph 真源，也不是 Canvas 替代品，而是让研究者快速进入当前 node、编辑 manuscript、启动 bounded session。

#### 1.1.1 用户真正需要完成的动作

用户打开页面后不是为了理解页面本身，而是为了进入一个有界研究动作。

##### 1.1.1.1 本节内容要求

- 看到 `current_phase`、`next_node`、runnable 状态。
- 进入当前 node。
- 查看 status、review、files、relations、local skills。
- 编辑当前 node 的 `docs/manuscript.md`。
- 创建 general、scope 或 node session。
- 执行 bounded prompt。
- 回看 session log 和执行结果。

#### 1.1.2 前端不应该承担的职责

前端不能成为第二真源。

##### 1.1.2.1 本节内容要求

- 不在前端硬编码 P0-P4 业务规则。
- 不在前端重新推导 ready、blocked、next node。
- 不把 Canvas 语义复制成第二套 IDE。
- 不让 agent cockpit 接管全局调度。
- 不让 bounded worker 变成 global router。

### 1.2 前端的最小事实依赖

前端只消费 projection 和 gateway API。

#### 1.2.1 前端需要读取的数据

页面每个区域依赖 derived data。

##### 1.2.1.1 本节内容要求

- `graph_status.json`：驱动 topbar、next node。
- `graph.json`：提供 node 和 explicit edge。
- `hierarchy.json`：提供 Tree Navigator 与 Overview。
- `node_details.json`：提供 Node tab、Context Drawer、tooltip。
- `scope_rollup.json`：提供 scope health summary。
- `board_state.json`：提供辅助 workset/flow projection，不是主 tab。
- `agent_gateway.yaml`：提供可运行 agent catalog。

#### 1.2.2 前端不直接读取的数据

避免浏览器现场拼装后端事实。

##### 1.2.2.1 本节内容要求

- 不在浏览器中递归读取 `research/**/status.yaml`。
- 不在浏览器中解析 `backend/relations/edge_registry.json`。
- 不在浏览器中读取 Obsidian Canvas。
- 不把 localStorage UI 状态写回 graph 文件。

## 2. 当前前端现状复盘

### 2.1 当前页面结构

当前 `web/app/index.html` 已经形成三栏 cockpit。

#### 2.1.1 已经成立的能力

这些方向应保留。

##### 2.1.1.1 本节内容要求

- Global Scheduler Bar。
- Tree Navigator。
- Main Workbench。
- Context Drawer。
- Overview / Node / Manuscript / Session 四 tab。
- Node-local manuscript GET/PUT。
- Session list / session log。
- 中英文切换。

#### 2.1.2 当前主要剩余问题

当前问题从结构错误转为收敛尾巴。

##### 2.1.2.1 本节内容要求

- `workspace.js`、`sessions.js` 仍偏厚。
- CSS 仍有壳层迁移残留。
- Markdown preview 是可信 subset，不是完整 authoring surface。
- Session mention 语义需要持续用测试固定。
- 文档必须继续避免旧 `scope rail / board workspace` 叙事。

### 2.2 当前架构边界

Core 边界基本正确。

#### 2.2.1 应保持不动的 core

前端优化不牵动底层真源。

##### 2.2.1.1 本节内容要求

- `research/` 仍是 canonical research workspace。
- `backend/relations/edge_registry.json` 仍是显式关系真源。
- `backend/graph/graph.json` 和 `graph_status.json` 仍是 scheduler derived outputs。
- `scripts/refresh_hypergraph.py` 仍负责最小 graph 刷新。
- `scripts/build_canvas_from_graph.py` 仍负责 Obsidian Canvas projection。
- bounded worker skills 保持 worker layer 边界。

#### 2.2.2 前端优化的真实范围

本轮只优化 app 层与可验证行为。

##### 2.2.2.1 本节内容要求

- 可以优化 `web/app/` 的布局、交互、session UX、manuscript safety。
- 可以优化 gateway bootstrap 信息可读性。
- 可以优化 projection refresh 的提示和验证。
- 不扩 canonical graph schema。
- 不把 UI 状态写回 scheduler graph。

## 3. 奥卡姆剃刀下的优化边界

### 3.1 保持 core 不动

前端问题在前端和 gateway 可见性层解决。

#### 3.1.1 不改 canonical source

所有真源继续保持当前职责。

##### 3.1.1.1 本节内容要求

- `status.yaml` 继续表达 node state。
- `edge_registry.json` 继续表达 explicit relations。
- `graph.json` 只包含 `nodes` 和 `edges`。
- graph node payload 只包含 `path` 和 `status`。
- graph edge payload 只包含 `src`、`rel`、`dst`。
- 不往 `graph.json` 加 progress、owner、summary、priority、tags。

#### 3.1.2 不扩张 Canvas 职责

Canvas 和 Web app 的职责不能混。

##### 3.1.2.1 本节内容要求

- Canvas 用于 Obsidian IDE、规划、导航、proposal workspace。
- Web app 用于状态、node、manuscript、session、setup diagnostics。
- 两者都读取 projection。
- 两者都不是 source of truth。

### 3.2 删除无效复杂度

延后看似高级但不服务主路径的能力。

#### 3.2.1 当前不需要的能力

当前用户痛点不是这些能力。

##### 3.2.1.1 本节内容要求

- 全量 edge 常驻显示。
- 多图布局切换。
- 拖拽式 board reorder。
- 复杂 session transcript search。
- 桌面壳深度集成。
- 自动多 agent 编排。

#### 3.2.2 当前必须优先的能力

先让用户能稳定看见、理解、行动。

##### 3.2.2.1 本节内容要求

- 加载链路可解释。
- 错误态可见。
- tree/node 选择稳定。
- manuscript 不静默丢内容。
- session 上下文可审计。

## 4. Canonical Cockpit IA

### 4.1 Global Scheduler Bar

顶部只回答全局状态和当前主动作。

#### 4.1.1 内容预算

Topbar 不再承担 workspace mode 控制。

##### 4.1.1.1 本节内容要求

- phase / next node / runnable 摘要。
- 一个主 CTA：打开会话。
- 搜索、语言、刷新、heartbeat 作为 utility。
- 不出现 `workspace-tab-toggle`。

### 4.2 Tree Navigator

左侧只回答“我去哪”。

#### 4.2.1 树行预算

树行不能变成压缩 dashboard。

##### 4.2.1.1 本节内容要求

- title、缩进、展开状态。
- status dot。
- next 或 blocked。
- 不常驻 pinned、session target、flags、长 badge。
- 展开状态持久化。

### 4.3 Main Workbench

中央只回答“我现在做什么”。

#### 4.3.1 四个 tab

每个 tab 保持一个主对象。

##### 4.3.1.1 本节内容要求

- `Overview`：结构与流向。
- `Node`：当前节点状态和 review/execution gate。
- `Manuscript`：当前 node 文稿编辑与预览。
- `Session`：当前上下文的 bounded execution。

### 4.4 Context Drawer

右侧只回答“还有哪些辅助上下文”。

#### 4.4.1 Drawer 预算

Drawer 不能成为第二主屏。

##### 4.4.1.1 本节内容要求

- setup diagnostics。
- current object metadata。
- watched workset。
- files / skills / reads。
- incoming / outgoing relations。
- 不放完整 session log。

## 5. 安全与验收

### 5.1 Manuscript safety

研究正文安全优先。

#### 5.1.1 必备行为

未保存内容不能被静默覆盖。

##### 5.1.1.1 本节内容要求

- dirty state。
- 切 node confirm。
- refresh confirm。
- beforeunload。
- `Ctrl/Cmd+S`。
- safe Markdown subset preview。

### 5.2 Session semantics

placeholder 与真实能力一致。

#### 5.2.1 最小 mention 集合

每个 token 都必须可审计。

##### 5.2.1.1 本节内容要求

- `@current`
- `@scope`
- `@node`
- `@readme`
- `@status`
- `@manuscript`
- 显式跨节点引用使用 `@research::...`。

### 5.3 自动化验收

用行为而不是截图验收。

#### 5.3.1 最小测试

测试固定主路径。

##### 5.3.1.1 本节内容要求

- `python test/run_gateway_acceptance.py`
- `.venv/bin/python test/run_browser_smoke.py`
- `python test/run_all_acceptance.py`
- 页面非白屏、四 tab、tree persistence、drawer persistence、manuscript safety、session mentions。

## 6. 结论

### 6.1 最终判断

当前前端已经是 research workbench 骨架，后续只做收敛。

#### 6.1.1 下一步原则

先删噪声，再补安全，再收敛语义，最后美化。

##### 6.1.1.1 本节内容要求

- 不恢复 board 主模式。
- 不恢复顶部 mode toggle。
- 不让右 drawer 承担 session 主工作流。
- 不引入重编辑器或前端框架。
- 不把 `web/dashboard/` 合并进 `web/app/`。
