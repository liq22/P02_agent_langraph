# AutoResearch 框架大纲与核心创新点

## 一句话定义

Human 定方向与约束，Agent 在单个节点内推进一次，Graph 把结果纳入下一轮调度。

---

## 1. 框架概述

### 1.1 定位

这是一个**轻量级人机协作研究工作空间**（AutoResearch with Human），不是完全自主的论文工厂，也不是文档存储库。

核心设计哲学：研究内容存储在仓库文件中，图只负责选择下一个节点，每次智能体运行只更新一个选定节点。

### 1.2 六大核心表面

| 表面 | 路径 | 职责 |
|------|------|------|
| **研究节点层** | `research/` | 研究内容的真源，每个节点是一个文件夹支持的研究单元 |
| **最小调度层** | `backend/graph/` | 最小化 JSON 调度图，只做调度不存储内容 |
| **显式关系层** | `backend/relations/` | 跨节点关系的唯一真源 |
| **全局技能层** | `.agent/skills/` | 可复用的项目级技能库 |
| **模板脚手架层** | `templates/` | 可复用的节点和配置模板 |
| **前端投影层** | `web/`, `obsidian/` | Web 驾驶舱、Obsidian Canvas IDE 和静态监控面板 |

### 1.3 核心设计原则

1. **奥卡姆剃刀原则** - 先删除偶然复杂性，不误伤科研流程的本质复杂性
2. **最小超图原则** - 图只保留调度所需的最小事实：节点存在、路径、状态、显式边
3. **局部入口优先** - 节点内的读取顺序由 `local_entry.md` 决定，而非全局搜索
4. **有界执行** - 每次执行都有明确的输入/输出/停止条件
5. **真源单一** - 每种事实只在一个文件中作为真源存在

---

## 2. 核心架构设计

### 2.1 研究节点层（Research Layer）

#### 节点文件夹协议

每个节点（Node）是研究的最小单元，采用文件夹支持的轻量级协议：

```
research/<node_path>/
├── README.md                 # 节点入口点：目标、边界、完成标准、TODO
├── status.yaml               # 执行状态：lifecycle、progress、review gate
├── config.yaml               # 节点配置：node_mode、node_profile
├── prompts/                  # 语义层
│   ├── research_prompt.md    # 节点研究目标、问题、输出标准
│   ├── acceptance_checklist.yaml  # 完成定义
│   └── review_rubric.yaml    # 审查标准（可选）
├── skills/                   # 执行层
│   ├── local_entry.md        # 本地入口文件（必需）
│   ├── SKILL.md              # 策略增量（standard 节点）
│   ├── SOP.md                # 有序程序（execution 节点）
│   ├── local_wrapper.md      # IO 绑定器（可选）
│   └── local_execution.md    # 执行绑定器（可选）
├── docs/
│   ├── manuscript.md         # 节点正文
│   └── HUMAN_ONLY.md         # 人类专用笔记（Agent 默认不读）
├── artifacts/                # 节点产物
├── review/                   # 审查材料
│   ├── AI_001.md
│   ├── 人类_001.md
│   └── verdict.yaml
└── logs/agent_sessions/      # 会话日志
```

#### 节点模式（Node Modes）

| 模式 | 描述 | 必需文件 |
|------|------|----------|
| `parent` | 父节点，仅协调子节点路由和状态 | README.md, status.yaml |
| `lite` | 轻量级研究叶节点，使用 local_entry + prompts | README.md, status.yaml, local_entry.md, prompts/* |
| `standard` | 标准研究叶节点，需要本地策略层 | + skills/SKILL.md |
| `execution` | 执行叶节点，需要本地执行程序 | + skills/SOP.md, local_execution.md |

#### 节点画像（Node Profiles）

- `experiment_execution`: 受执行契约约束的有界实验执行
- `result_synthesis`: 结果分类账驱动的证据合成

### 2.2 最小调度层（Backend Graph Layer）

#### 图文件契约

```json
// backend/graph/graph.json
{
  "nodes": {
    "research::P0_x::P0_01_y": {
      "path": "research/P0_x/P0_01_y",
      "status": "ready|done|blocked|..."
    }
  },
  "edges": [
    {"src": "...", "rel": "depends_on|addresses", "dst": "..."}
  ]
}
```

```json
// backend/graph/graph_status.json
{
  "refresh_ok": true,
  "current_phase": "P0|P1|P2|P3|P4",
  "ready_nodes": ["..."],
  "blocked_nodes": ["..."],
  "next_node": "research::...",
  "unfinished_count": 0
}
```

**关键设计决策**：
- 图只存储 `path` 和 `status`，不存储 manuscript、review 正文、长摘要
- 不添加 `owner`、`priority`、`tags` 等字段到图文件
- 所有复杂内容回到节点文件夹中

#### 派生投影（可选）

| 文件 | 用途 | 必需性 |
|------|------|--------|
| `hierarchy.json` | 树导航和概览 | 可选 |
| `node_details.json` | Node Tab / Drawer / Tooltip | 可选 |
| `scope_rollup.json` | 范围级健康摘要 | 可选 |
| `board_state.json` | 活跃集投影 | 可选 |

### 2.3 显式关系层（Relations Layer）

```json
// backend/relations/edge_registry.json
{
  "edges": [
    {
      "src": "research/P1_...",
      "rel": "depends_on|addresses",
      "dst": "research/P0_..."
    }
  ]
}
```

**关系类型**：
- `depends_on`: 依赖关系，前驱完成后后继才可调度
- `addresses`: 应答关系，P4 回应 P3 的批评

### 2.4 全局技能层（Global Skills Layer）

#### 技能目录结构

```
.agent/skills/
├── graph_driven_research_orchestrator/   # 全局路由器
├── auto_research_campaign/               # 自动研究步骤
├── autonomous_research_lane/             # 无人自动推进
├── auto_experiment_worker/               # 有界实验执行器
├── manuscript_worker/                    # 稿件工作器
├── experiment_design_or_execution/       # 实验设计执行
├── citation_verifier/                    # 引文验证器
├── response_worker/                      # 回复工作器
└── ...
```

#### 技能分类

1. **入口技能（Entry Skills）**
   - `graph_driven_research_orchestrator`: 读取最小图文件，选择一个可行动节点
   - `auto_research_campaign`: 将宽泛研究提示解析为单个有界步骤
   - `autonomous_research_lane`: 无人自动推进直到人类决策点

2. **工作器技能（Worker Skills）**
   - `manuscript_worker`: 推进选定的稿件节点
   - `auto_experiment_worker`: 执行有界实验轮次
   - `response_worker`: 推进回复节点
   - `citation_verifier`: 验证引用事实

3. **辅助技能（Helper Skills）**
   - `result_to_claim`: 判断结果支持什么，不支持什么
   - `structured_map_builder`: 构建节点本地映射或矩阵
   - `aggregate_reviews`: 聚合审查文件

### 2.5 前端投影层（Frontend Projection Layer）

#### Web 驾驶舱（`web/app/`）

**四标签工作台**：
- `Overview`: 结构理解（层次图、依赖覆盖）
- `Node`: 当前节点状态、文件、关系概览
- `Manuscript`: 编辑当前节点的 `docs/manuscript.md`
- `Session`: 在有界上下文中执行 Agent 动作

**关键特性**：
- Manuscript dirty state 保护
- Session 上下文绑定（node/scope/general 三类）
- @current, @scope, @readme, @manuscript 等语义注入

#### Obsidian Canvas IDE

**职责**：
- 低频、高层、空间组织
- 路线理解、proposal/method mapping
- 人工规划和思考

**不是**：
- 内容真源
- Session 运行时

#### 静态监控面板（`web/dashboard/`）

- 只读监控图和调度状态
- 不支持 Agent 执行

### 2.6 刷新模式（Refresh Modes）

| 模式 | 刷新内容 | 使用场景 |
|------|----------|----------|
| `graph_only` | graph.json, graph_status.json | 高频有界 Agent 步骤后 |
| `full` | 图 + 所有投影 + Canvas | 驾驶舱、Canvas、人工评审会话 |

---

## 3. 核心创新点

### 3.1 最小超图调度器

**问题**：传统工作流引擎在图中存储太多信息，导致图成为内容数据库。

**解决方案**：
- 图只存储最小事实：节点存在、路径、状态、显式边
- 所有研究内容回到节点文件夹
- 图是调度器，不是内容数据库

**价值**：
- 保持图轻量，易于刷新和验证
- 防止图和节点内容不一致
- 降低认知负担

### 3.2 局部入口优先（Local Entry First）

**问题**：Agent 容易陷入全局搜索，找到错误的技能或指令。

**解决方案**：
- 每个节点的 `skills/local_entry.md` 是唯一的入口文件
- Agent 必须先读取 `local_entry.md`，再按其决定的读取顺序继续
- 不允许在找到有效入口文件后搜索整个仓库

**价值**：
- 确保每次执行都在明确的上下文中
- 防止指令污染
- 提高可审计性

### 3.3 有界技能与工作器

**问题**：Agent 容易陷入无限循环或过度执行。

**解决方案**：
- 每个技能都有明确的输入、输出、停止条件
- 工作器只执行一个有界任务
- `auto_experiment_worker` 必须在选定节点和可执行契约后才能调用

**价值**：
- 防止无限循环
- 每次执行都可审计
- 资源消耗可控

### 3.4 图驱动编排（Graph-Driven Orchestration）

**问题**：全局编排器容易变成复杂的流水线大脑。

**解决方案**：
- 编排器只是路由器，不做具体研究执行
- 每次只选一个节点，执行一个有界步骤
- 详细研究动作属于节点本地技能或规范工作器

**工作流**：
1. 刷新图
2. 读取 `graph_status.json` 和 `graph.json`
3. 确定 `next_node`
4. 进入目标节点目录
5. 解析本地技能
6. 委托给一个有界工作器路径
7. 更新节点本地状态
8. 刷新最小调度图
9. 报告调度差异

**价值**：
- 保持编排器简单
- 研究复杂性在节点本地处理
- 易于调试和恢复

### 3.5 上下文卫生（Context Hygiene）

**问题**：外部参考、生成视图、私有笔记容易静默成为当前运行的指令。

**解决方案**：
- 默认只读取必要文件
- 隔离 `_reference/**`、`research/**/docs/HUMAN_ONLY.md`、生成 Canvas 文件
- 不读取 `.env`、凭证、令牌、私钥

**默认读取顺序**：
1. `AGENTS.md`
2. `README.md`
3. `backend/graph/graph_status.json`
4. 选定节点路径从 `graph.json`
5. 选定节点的 `README.md`
6. 选定节点的 `status.yaml`
7. 选定节点的 `skills/local_entry.md`
8. 由 `local_entry.md` 明确命名的文件

**价值**：
- 防止指令污染
- 降低 token 消耗
- 提高可审计性

### 3.6 P0-P4 阶段结构

**问题**：学术研究流程复杂，需要清晰的阶段划分。

**解决方案**：

| 阶段 | 职责 | 关键节点 |
|------|------|----------|
| **P0 项目申请书** | 问题定义、动机、路线、约束 | 研究背景、科学问题、创新点、技术路线、资源预算 |
| **P1 实验设计** | 数据、伪代码、仓库、实验、验证 | 数据层、伪代码、仓库蓝图、轻量验证、结果整理 |
| **P2 论文撰写** | 章节写作、claim-evidence、图表 | 风格选择、初稿 md、定稿 tex、形式检查、去 AI 味道 |
| **P3 模拟评审** | 多轮 review、issue 注册、修订 | 评审轮次、评价者档案、批评摘要、修订动作 |
| **P4 回复与再投稿** | response mapping、package | 审稿意见收集、问题映射、逐点回复、修改证据 |

**价值**：
- 清晰的研究流程
- 每个阶段有明确的目标和验收标准
- 易于追踪进度

### 3.7 显式关系注册表

**问题**：跨节点关系容易隐式散落在多个文件中。

**解决方案**：
- `backend/relations/edge_registry.json` 是唯一的显式关系真源
- 图是从关系注册表派生的
- 前端和 Canvas 也是从关系派生的投影

**价值**：
- 关系定义单一真源
- 易于验证和维护
- 防止不一致

### 3.8 多前端投影但真源单一

**问题**：多个前端容易导致真源分散。

**解决方案**：
- Web 驾驶舱、Obsidian Canvas、Dashboard 都是投影和操作面
- 真源始终在 `research/` 和 `backend/relations/`
- Manuscript 只编辑当前节点的 `docs/manuscript.md`

**价值**：
- 真源清晰
- 前端可替换
- 数据一致性

### 3.9 节点模式与画像的分离

**问题**：节点类型容易混杂结构和语义。

**解决方案**：
- `node_mode`：本地栈深度和必需文件表面
- `node_profile`：执行层语义角色指导

**价值**：
- 结构和语义分离
- 验证和生成视图更简单
- 避免节点模式成为第二路由大脑

### 3.10 Manuscript 安全保护

**问题**：编辑 Manuscript 时容易被静默覆盖。

**解决方案**：
- Dirty state 保护
- 切换节点前确认
- `Ctrl/Cmd+S` 快捷保存
- 离页前保护

**价值**：
- 保护研究正文
- 防止数据丢失
- 提高用户信任

---

## 4. 运行时契约

### 4.1 Agent 启动序列

1. 读取根 `README.md`
2. 确保最小调度图文件最新
3. 读取 `backend/graph/graph_status.json`
4. 使用 `next_node` 作为目标节点
5. 读取目标节点在 `backend/graph/graph.json` 中的条目获取路径
6. 进入该节点目录
7. 只先读取该节点的 `README.md`、`status.yaml`、`skills/local_entry.md`
8. 从本地入口解析到可选 wrapper/execution 或项目工作器
9. 运行一个步骤并只更新选定节点文件
10. 回到图调度。只在需要时重建生成视图

### 4.2 完成词定义

| 完成词 | 含义 |
|--------|------|
| `ready` | 节点可被调度 |
| `done` | 选定节点已满足本地验收清单 |
| `pass` | 某个命名检查通过 |
| `submission-ready` | 最终提交检查通过 |
| `framework healthy` | 维护检查通过；论文可能仍不完整 |

### 4.3 停止条件

- 没有 `next_node` 且 `unfinished_count` 为 0
- 图不一致或缺失关键工件
- 目标节点缺 `local_entry.md` 且当前策略禁止回退
- 下一步需要 hands-off repeated progression
- 本轮完成声明无法通过节点本地验收或显式外部审查

---

## 5. 设计哲学总结

### 5.1 先统一真源，再保护内容，再收敛语义，最后美化

1. **统一真源**：每种事实只在一个文件中作为真源
2. **保护内容**：Manuscript 安全、上下文卫生
3. **收敛语义**：删除重复控制面、统一术语
4. **美化**：最后做视觉和审美优化

### 5.2 先删噪声，再补安全，再收敛语义，最后美化

1. **删除噪声**：重复控制面、旧叙事、未落地功能
2. **补充安全**：Manuscript dirty guard、session 语义
3. **收敛语义**：四区职责固定、session 语义补齐
4. **美化**：降低面板感、统一字号、状态色收敛

### 5.3 本质复杂性与偶然复杂性

**保留的本质复杂性**：
- P0-P4 研究流程复杂性
- 节点 status/review/manuscript 的真实差异
- general/scope/node 三类 session
- 有界 agent 执行
- manuscript 编辑安全
- graph projection 与 Canvas projection

**删除的偶然复杂性**：
- 同一状态在顶部、左栏、右栏重复展示
- 前端文档和代码叙事不一致
- 旧 scope rail / board 语言残留
- 右侧 drawer 语义残留但实现不统一
- placeholder 承诺超出实际实现能力
- 树导航承担过多状态语义

---

## 6. 技术栈与依赖

### 6.1 后端

- **Python**: 主要脚本语言
- **FastAPI**: Agent Gateway API
- **JSON/YAML**: 数据序列化

### 6.2 前端

- **原生 HTML/CSS/JavaScript**: Web 驾驶舱
- **Obsidian**: Canvas IDE

### 6.3 脚本

- `scripts/refresh_views.py`: 刷新图和投影
- `scripts/validate_research_truth.py`: 验证研究真源

### 6.4 最小依赖

- 优先使用标准库
- 只在依赖已存在时才添加新依赖

---

## 7. 文件清单

### 7.1 真源文件（可编辑）

```
research/
backend/relations/
.agent/skills/
scripts/
templates/
docs/
```

### 7.2 派生文件（可重建）

```
backend/graph/
backend/views/
backend/indexes/
obsidian/canvases/
web/app/
web/dashboard/
```

### 7.3 局地文件（不提交）

```
.env*
credentials/
tokens/
private keys/
```

---

## 8. 验证与测试

### 8.1 Smoke Tests

- Gateway API smoke
- Frontend smoke
- Manuscript safety tests
- Session context tests

### 8.2 验收清单

- 页面可加载
- 图可读
- 树可展开并持久化
- next node 可进入
- manuscript 不丢
- session 可运行或明确说明不能运行
- docs 与代码术语一致

---

## 9. 参考文档

- `README.md`: 仓库启动协议
- `AGENTS.md`: 仓库指南
- `docs/architecture.md`: 架构详解
- `docs/architecture/glossary.md`: 术语定义
- `docs/architecture/entry_matrix.md`: 入口矩阵
- `docs/architecture/refresh_modes.md`: 刷新模式
- `docs/architecture/obsidian_canvas_workflow.md`: Canvas 工作流
- `docs/architecture/context_hygiene.md`: 上下文卫生
- `docs/architecture/autoresearch_optimization_report_4level.md`: 优化报告
- `docs/dev.md`: 开发者命令
- `docs/USER_GUIDEBOOK.md`: 用户指南
- `docs/CODEX_ONLY_WORKFLOW.md`: Codex 专用工作流

---

**一句话总结**：

这是一个以**节点为单元、图为调度、技能为执行、人为主导**的学术研究操作系统，通过**最小化图、局部入口优先、有界执行、上下文卫生**等设计，实现了人机协作的高效研究工作流。
