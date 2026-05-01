# 更新指导手册（中文）

## 目标

把当前 `obsidian-canvas-ide` 分支升级为一个 **Research Agent Cockpit**：

- 研究节点层级监控
- graph-aware 对话与执行
- 多 agent 会话
- 中英切换
- Web-first，后续可包桌面壳

## 0. 前提

这次更新 **不重写 core**，保持以下边界不变：

- `research/` 仍然是真实工作层
- `backend/graph/graph.json` 仍然是最小结构图
- `backend/graph/graph_status.json` 仍然是调度摘要
- Obsidian Canvas 仍然是 IDE / workbench
- `.agent/skills/auto_experiment_worker/SKILL.md` 仍然是 bounded worker

## 1. 创建工作分支

```bash
git checkout obsidian-canvas-ide
git pull origin obsidian-canvas-ide
git checkout -b feat/research-agent-cockpit-v2
```

## 2. 复制本包中的文件

把以下目录复制进仓库：

```text
backend/agent_gateway/
config/agent_gateway.yaml.example
web/app/
scripts/build_hierarchy_projection.py
scripts/build_node_details.py
scripts/build_scope_rollup.py
scripts/build_board_state.py
scripts/refresh_views.py
docs/desktop/tauri/
docs/architecture/agent_cockpit_v2.md
```

## 3. 创建真实 agent 配置

```bash
cp config/agent_gateway.yaml.example config/agent_gateway.yaml
```

然后手工编辑：

- `agents.codex.command`
- `agents.claude_code.command`
- 需要时增加本地 wrapper agent

不要直接保留 example placeholder。

## 4. 刷新全部投影

使用 `docs/dev.md` 中的 full refresh 开发命令。

这一步会统一刷新：

- `graph.json`
- `graph_status.json`
- `hierarchy.json`
- `node_details.json`
- `scope_rollup.json`
- `board_state.json`
- Canvas projections

## 5. 安装 gateway 依赖

开发环境依赖安装命令见 `docs/dev.md`。

## 6. 启动 app

启动 Web app 的当前命令见 `docs/dev.md`。

打开：

```text
http://127.0.0.1:8765/app/
```

## 7. 验证项

### 结构层
- 能看到 P0 / P1 / P2 / P3 / P4 顶层 scope
- hierarchy map 可以 drill-down
- blocked / ready / next 高亮正常

### 详情层
- 点击节点后可见：
  - status
  - progress
  - review gate
  - heartbeat
  - files
  - relations

### 会话层
- agent catalog 能加载
- 能创建 general / node-bound session
- Codex / Claude Code / wrapper 可至少跑一个 bounded 命令
- session log 能持续刷新

### 语言层
- 中文 / English 切换正常
- 切换后布局不乱

## 8. 建议的 commit 顺序

### Commit A — projections

按实际 projection 变更文件提交。开发命令见 `docs/dev.md`。

### Commit B — gateway
```bash
git add backend/agent_gateway config/agent_gateway.yaml.example docs/architecture/agent_cockpit_v2.md
git commit -m "feat(agent-gateway): add graph-aware local agent gateway"
```

### Commit C — web app
```bash
git add web/app
git commit -m "feat(frontend): add bilingual research agent cockpit app"
```

### Commit D — desktop wrapper docs
```bash
git add docs/desktop/tauri
git commit -m "docs(desktop): add tauri wrapper integration notes"
```

## 9. 推送并开 PR

```bash
git push origin feat/research-agent-cockpit-v2
```

PR 标题建议：

```text
feat(app): add graph-aware bilingual research agent cockpit
```

## 10. 回滚策略

如果需要最小回滚，只回滚新增层：

- `backend/agent_gateway/`
- `web/app/`
- projection scripts
- `docs/desktop/tauri/`
- `config/agent_gateway.yaml.example`
- `docs/architecture/agent_cockpit_v2.md`

不要动现有 core。

## 11. 后续演进建议

1. 保持 chat session 的 node / scope binding 显式可见
2. 不要把 graph 变成内容数据库
3. 不要把 bounded experiment worker 再放大成全局 brain
4. 先把 Web 版本打磨稳定，再包桌面壳
