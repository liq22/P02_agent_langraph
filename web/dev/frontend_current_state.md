# 前端现状整理

本文记录当前 `web/` 前端的真实状态和下一轮改造约束。它不是新的大规划，也不是设计愿景；它的作用是让后续前端修改先对齐现状，再做最小正确改动。

## 1. 当前前端入口

`web/app/` 是主入口，定位是 Research Agent Cockpit。它由 `backend/agent_gateway/app.py` 提供服务，必须通过 gateway 打开，例如：

```bash
bash scripts/dev_start_agent_app.sh
```

默认地址是：

```text
http://127.0.0.1:8765/app/
```

如果指定端口，例如 `PORT=8766 bash scripts/dev_start_agent_app.sh`，则入口是：

```text
http://127.0.0.1:8766/app/
```

`web/app/` 不应通过 `file://` 或普通 `python -m http.server` 打开，因为它依赖 `/api/*`：

- `/api/app/bootstrap`
- `/api/graph/status`
- `/api/graph/structure`
- `/api/graph/hierarchy`
- `/api/graph/details`
- `/api/graph/rollup`
- `/api/graph/board`
- `/api/agents/*`
- `/api/node/{node_id}/manuscript`

`web/dashboard/` 是次级静态只读监控面。它适合看 projection，不是主要操作入口，也不负责 agent session、manuscript 编辑或 gateway 操作。

## 2. 当前 `web/app` 结构

当前页面已经从多窗口堆叠收缩为一个主 cockpit：

- Top bar：展示全局状态、搜索、语言、工作模式、刷新和 heartbeat。
- Left navigator：展示 scheduler、树状导航、active set，并支持整体收起。
- Center workspace：唯一主工作区，包含 `Overview / Node / Manuscript / Session` 四个模式。
- Node view：左侧展示节点主状态、review、relations；右侧展示 node-local profile、files、skills、required reads、optional reads、links。
- Manuscript view：读取和保存当前节点的 `docs/manuscript.md`。
- Session view：创建、运行、停止 bounded agent session，并查看 session log。

当前 DOM contract 由 `app.js` 中的 `assertDomContract()` 保护。缺少关键挂载点时，页面应显式报错，而不是静默空白。

## 3. 已经成立的能力

当前前端已经具备以下真实能力：

- Gateway 不可用时，中心工作区会显示启动提示和错误面板。
- `Overview` 使用 `hierarchy.json` 和 D3 circle packing 展示层级。
- 左侧树支持节点展开、折叠、全部折叠、展开当前路径。
- 左侧导航整体支持收起，收起状态写入 `localStorage`。
- Node 模式已经把主信息和 node-local 细节分开，避免文件和关系重复占据主视觉。
- Files、local skills、required reads、optional reads、links 使用原生 `<details>` 折叠。
- Manuscript 模式通过 gateway 读写当前节点的 `docs/manuscript.md`，不写 graph 或 Canvas。
- Session 模式支持 general、scope、node 三类上下文，并把 prompt 绑定到当前上下文。
- `@node` mention 已接入前端候选列表。
- Gateway acceptance 已覆盖 DOM contract、manuscript API、可折叠导航、文件折叠、context drawer 移除等关键契约。

## 4. 当前主要问题

当前主要问题不是缺少功能，而是视觉和认知结构仍偏后台系统：

- CSS 有历史叠加层，仍可见 `.scope-*`、`.board-*`、`.sidebar-right` 等旧概念残留。
- 页面视觉语言偏“管理后台”，研究工作台的叙事感不足。
- Top bar、左树、中心工作区的信息已经分层，但用户打开后仍需要主动理解“现在该做什么”。
- `Overview` 更像状态图，不像一个引导研究行动的开场页。
- Node view 已经去重，但仍偏字段面板，尚未形成“问题 -> 证据 -> 下一步”的叙事。
- Manuscript view 可编辑真实文件，但 preview 只是安全文本换行，不是完整 Markdown 渲染。
- Session view 能跑 bounded action，但 session 的成功、失败、下一步建议仍不够突出。

这些问题应在 `web/app/` 的布局、视觉层级和内容组织中解决，不应扩展 graph schema，也不应把前端变成第二真源。

## 5. 下一轮 GPT-5.4 前端约束

如果用 GPT-5.4 继续优化前端，先锁定约束，再让模型写代码：

- 布局系统先行：Top global status、Left navigation、Center narrative workspace、Local foldouts。
- 页面按叙事组织，而不是按数据库字段组织。
- 首页先回答：现在在哪个 phase、next node 是什么、为什么是它、下一步怎么做。
- Node 页先回答：这个节点的目标、证据状态、阻塞点、最小下一步。
- Session 页先回答：当前 agent 被绑定到什么上下文、允许做什么、不允许做什么、运行结果在哪里。
- 使用真实 API 内容，不写假卡片、假指标、假进度。
- 缺数据时显式显示缺失来源和修复动作，不用占位符伪装完成。
- 推理预算保持 low 或 medium，避免一次性大重写。
- 每次改动只推进一个明确 UX 问题，并用 acceptance 或静态契约锁住。

这类前端优化的目标不是“更炫”，而是降低用户判断下一步研究动作的成本。

## 6. 不动边界

前端优化不得改变下面边界：

- `research/` 仍是 canonical research workspace。
- `backend/relations/edge_registry.json` 仍是显式关系真源。
- `backend/graph/*` 仍是 projection，不是手写真源。
- Obsidian Canvas 仍是 projection 和空间规划面，不承载 manuscript truth。
- `web/dashboard/` 仍是静态只读监控面。
- `web/app/` 不重新实现 scheduler，不在浏览器推导 ready、blocked、next node。
- UI 状态可以放在 `localStorage`，但不得写回 graph truth。
- Agent session 必须保持 bounded，不把 cockpit 变成无界 autoresearch 编排器。

## 7. 最小验证入口

文档或前端契约修改后，优先运行最小检查：

```bash
test -f web/dev/frontend_current_state.md
rg -n "web/app|web/dashboard|Overview|Node|Manuscript|Session|GPT-5.4|不动边界" web/dev/frontend_current_state.md
python test/run_gateway_acceptance.py
```

失败定位：

- `test -f` 失败：文档没有落在约定位置。
- `rg` 失败：文档没有覆盖前端现状关键概念。
- `run_gateway_acceptance.py` 失败：文档描述的前端契约和代码事实可能已经漂移。
