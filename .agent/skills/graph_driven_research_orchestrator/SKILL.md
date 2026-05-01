---
name: graph-driven-research-orchestrator
description: Read minimal graph files, select exactly one actionable node, enter its local entry file, allow one worker handoff, refresh the scheduler graph, and report the scheduling delta. Use when the system needs one global routing run.
---

# Graph-Driven Research Orchestrator

## Plain-language role

Use this skill when the system must choose the next research node.

It reads the graph, picks one node, enters that node, follows its `skills/local_entry.md`, allows one worker handoff, and stops after one bounded action.

It does not write manuscript content directly.
It does not run experiments directly.
It does not read all nodes.

## Public organization policy

Use this as the default public entry when a user asks the system to advance the research workspace and no exact selected node is already fixed.

The orchestrator organizes the other skills by narrowing scope, not by owning their internal rules:

- It uses the scheduler graph to choose one node.
- It lets the selected node's `skills/local_entry.md` decide the local read order and delegate.
- It allows one handoff to a local wrapper, local execution file, canonical worker, or helper.
- It stops after one bounded step and reports the scheduler delta.

Do not ask users to pick from the full global skill list during a normal graph-led run. Only expose a specific worker when the selected node or the user's explicit request already makes that worker the narrow target.

## 使用时机
- 需要从 `backend/graph/graph.json` 与 `backend/graph/graph_status.json` 中选择下一步节点。
- 需要执行一次且仅一次全局路由。
- 需要进入目标 node，并调用该 node 的 `skills/local_entry.md`。

## 必要输入
- `backend/graph/graph.json`
- `backend/graph/graph_status.json`
- 目标 node 的 `README.md`、`status.yaml`、`skills/local_entry.md`
- 目标 node 的 prompt assets
- 可选 projection：`backend/graph/node_details.json` 中的 node entry packet，只用于 UI/debug 展示；不得替代节点文件或驱动控制流判断。
- 更深的本地读取栈只由 `local_entry.md` 的 read order 决定。

## Workflow
1. 如 graph 或 graph_status 缺失或过期，先触发一次 `python scripts/refresh_views.py --mode graph_only`。
2. 只读取最小 graph 工件，判定当前 operating condition。
3. 选择唯一 `next_node`；如果没有可行动节点，则报告并停止。
4. 进入该 node；不得用 `node_details.*` 决定 delegate、completion、review、execution 或 skip/no-op，只能读取 `README.md`、`status.yaml`、`skills/local_entry.md` 后由节点文件决策。
5. 通过 `local_entry.md` 读取节点 prompt 资产和后续本地层；`node_mode`、`node_profile`、`execution_profile` 只做结构合法性与 projection 辅助，不在 orchestrator 内解释成第二套节点读取或路由策略。
6. 允许一次委托到 wrapper、execution 或 project worker。
7. 回写本地状态前，若本轮声称节点完成或可交接，必须满足节点 `acceptance_checklist.yaml`；只有当 acceptance 明确启用 external review 时，才要求 `review/verdict.yaml`。
8. 回写本地状态后刷新 minimal scheduler graph，并只报告 scheduling delta；只有 web app、Canvas、dashboard 或 human review view 需要更新时才跑 full refresh。

## 产出
- 一次节点级执行结果
- 刷新后的 `graph.json` / `graph_status.json`
- 简洁的调度差异报告

## 边界
- 不预读 manuscript / review / response 正文。
- 不执行多节点链式推进。
- 不替代 local skill 做节点内细节判断。
- 不依赖 `node_details.json`、Canvas、dashboard 或 web app projection 做任何 runtime 控制流判断。
- graph 只是调度层，不是内容仓库。
- 方法论知识由 node prompt 或 worker 消化；orchestrator 只做单节点路由。
- 不用 graph / Canvas / dashboard 证明论文完成；提交就绪只能由节点证据、显式要求的独立 review verdict 和 `scripts/validate_research_truth.py --require-submission` 判定。

## stop_with
- 没有 `next_node` 且 unfinished_count 为 0
- graph 不一致或缺失关键工件
- 目标 node 缺 `local_entry.md` 且当前策略禁止 fallback
- 下一步需要 hands-off repeated progression
- 本轮完成声明无法通过 node-local acceptance 或显式 external review
