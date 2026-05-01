---
name: auto_research_campaign
description: Resolve a broad research prompt into exactly one selected-node research step. Use when the user says "自动研究" a node, section, experiment, review round, or response task and the system must choose graph-first, local entry, local wrapper, local execution, or one project worker without widening into an endless loop.
---

# Auto Research Step

## Plain-language role

Use this skill when the user gives a broad request such as "advance this node" or "work on this section."

It turns the broad request into one bounded selected-node action.

It does not run an open-ended loop.
It does not bypass `skills/local_entry.md`.

## 使用时机
- 用户给的是宽 prompt，例如“自动研究这个节点”“自动推进这一节方法”“自动做这轮回复”。
- 需要先判断 scope，再决定走 graph、selected node 还是 project worker。
- 需要执行一次且仅一次有界步骤。
- 如果用户明确要求无人连续推进、fully autonomous 或自动推进到人类检查点，转交 `autonomous_research_lane`，不要在本 skill 内展开循环。
- 如果用户要持续评估和修复系统本身，例如 prompt / skill / validator / test loop 的自优化闭环，转交 `autoresearch-system-optimizer`。
- 如果用户带着素材进入系统，并明确给出 `entry_phase`、`target_node`，或表达“从 P1/P2/P3/P4 开始”，先转交 `research_material_intake`，不要强制走 P0。

## 必要输入
- 用户 prompt 或已解析的目标 node。
- 若目标 node 已明确：该 node 的 `README.md`、`status.yaml`、`skills/local_entry.md`。
- 由 `skills/local_entry.md` 决定本轮 selected-node read order。
- 若 projection 可用，可读取 node entry packet 作为压缩入口；packet 只做缓存摘要，不替代 `local_entry.md`。
- `node_mode`、`node_profile`、`execution_profile` 只做结构合法性与 projection 辅助，不作为第二套 read policy。

## Workflow
1. 先解析 scope：目标 node 是否明确，任务是研究、写作、评审、回复还是执行检查。
2. 若用户明确要求无人连续推进、fully autonomous、自动跑到需要人介入为止，停止本单步并转交 `autonomous_research_lane`。
3. 若请求本质是 repo 级系统评估、批量打分、low-risk 修复和复评循环，停止本单步并转交 `autoresearch-system-optimizer`。
4. 若用户是在提交研究素材并明确阶段或目标节点，停止本单步并转交 `research_material_intake`。
5. 若目标 node 不明确，但请求明显是“从系统里找下一步”，走 graph-first：只读取最小 graph 工件并交给 `graph_driven_research_orchestrator` 做一轮路由，然后停止。
6. 若目标 node 已明确，走 node-first：可先用 node entry packet 快速确认 purpose、delegate、read order 与 blocking gap；随后必须检查 `skills/local_entry.md` 与最小 prompt 资产是否存在，再按 `local_entry.md` 的 read order 继续。缺关键资产就停止，不猜，也不绕过 `local_entry` 直跳 project worker。
7. 在当前 node 内只选择一条下一跳：
   - `local_entry`
   - `local_wrapper`
   - `local_execution`
   - 一个 project worker
8. 只执行一个 round，然后返回结果、缺口和下一阻塞点。
9. 若本轮输出声称节点完成、稿件就绪或可进入下游，必须检查 selected-node acceptance；若该节点显式启用 external review，也必须检查 verdict。提交就绪必须通过 `scripts/validate_research_truth.py --require-submission`，否则只能报告 blocked/revise。

## 选择规则
- 若目标 node 未明确，先 graph-first；不要在本 skill 内自己发明下一步 node。
- 若目标 node 已明确，先 node-first；不要因为 project worker 存在就绕过 node entry file。
- 默认优先让 `local_entry.md` 说话，而不是直接绕过它。
- `local_entry.md` 是唯一 selected-node entry file。
- prompt assets 是节点语义层；`acceptance_checklist.yaml` 是完成定义层。
- citation 支撑关键 claim 时，优先确认是否已有 verified citation；缺失时转交 `citation_verifier` 或停止为 citation check。
- 只有当目标 node 和 worker 适配关系已经非常明确时，才直接进入 project worker。
- `auto_experiment_worker` 是唯一 active experiment worker。
- 只有当 execution contract 已显式存在且 `contract_mode: executable` 时，才进入 `local_execution` 或 `auto_experiment_worker`。
- 只在“未指定 node 且确实需要系统选下一步”时 graph-first。

## 边界
- 不是 repo-global orchestrator。
- 不替代 `graph_driven_research_orchestrator`。
- 不替代 `auto_experiment_worker`。
- 不替代 selected-node `local_entry` 语义。
- 不制造第二个 experiment runtime source。
- 不猜 execution contract。
- 不掩盖缺失的 node prompt assets。
- 不执行 endless loop 或多节点链式推进。
- 不在本 skill 内实现 fully autonomous；连续无人推进由 `autonomous_research_lane` 承担。
- 不在本 skill 内实现 repo-global 系统自优化循环；prompt / skill / validator 的持续修复由 `autoresearch-system-optimizer` 承担。
- 不把 review-only contract、缺 results.tsv、占位 TeX、未关闭 review verdict 或缺 submission manifest 当成 submission_ready。

## stop_with
- ambiguous_target_scope
- missing_local_entry
- missing_node_skill
- missing_sop
- missing_prompt_assets
- missing_execution_contract
- target_node_not_ready_for_direct_worker
- broad_autonomous_loop_requested
- handoff_to_autonomous_research_lane
- handoff_to_autoresearch-system-optimizer
- citation_check_failed
- research_check_failed
