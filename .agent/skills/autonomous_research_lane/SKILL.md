---
name: autonomous_research_lane
description: Run repeated selected-node research rounds until a human decision, evidence, citation, review, or budget stop is reached. Use when the user explicitly asks for无人自动推进, fully autonomous work, continuous autoresearch, or hands-off progression across ready nodes.
---

# Autonomous Research Mode

## Plain-language role

Use this skill only when the user explicitly asks for hands-off progress until a stop condition.

It repeatedly runs bounded selected-node steps and stops at human, evidence, citation, review, budget, or graph blockers.

It does not cross a human decision point by guessing.

## 使用时机
- 用户明确要求无人连续推进、fully autonomous、自动跑到需要人介入为止。
- 当前 graph frontier 有 ready node，且下一步不需要立即由人类提供判断、PDF、数据或 venue choice。
- 需要跨多个 ready nodes 连续调用现有 selected-node flow。

## 必要输入
- `backend/graph/graph_status.json`
- `backend/graph/graph.json`
- 每个选中 node 的 `README.md`、`status.yaml`、`skills/local_entry.md`
- 由 `skills/local_entry.md` 指定的 prompt、local skill、wrapper 或 execution 文件

## Loop Contract
1. Refresh minimal graph with `python scripts/refresh_views.py --mode graph_only` when a prior step changed selected-node files.
2. Read graph frontier and select exactly the current `next_node`; do not invent a separate scheduler.
3. Enter the selected node through `skills/local_entry.md`.
4. Execute exactly one selected-node round using local entry, wrapper, local execution, or one project worker.
5. Check selected-node acceptance and any explicit external review.
6. Refresh graph-only again if node status or dependencies changed.
7. Continue only while no stop condition is present and the checkpoint budget remains.

## Stop Conditions
- human decision, human review, venue choice, or user-provided PDF/data/explanation required
- citation remains unverified and materially supports a claim
- evidence, experiment contract, figure source, metric parser, or manuscript input is missing
- `review/verdict.yaml` is `revise` or `block`
- local acceptance checklist is incomplete
- checkpoint budget reached
- graph frontier is empty or no ready node exists

## Autonomy Rules
- Autonomy means repeated selected-node rounds, not bypassing node contracts.
- `graph_driven_research_orchestrator` remains the single-round router; do not rewrite it into this mode.
- `autoresearch-system-optimizer` owns repo-wide prompt / skill / validator optimization; do not turn this mode into a system self-repair loop.
- Do not change graph schema, Canvas, or dashboard to store progress.
- Do not cross a human stop condition by guessing.
- At each checkpoint, report nodes advanced, stops hit, files changed, and next safe continuation point.

## Boundaries
- 不替代 `auto_experiment_worker`、`external_node_reviewer`、`citation_verifier` 或 manuscript worker。
- 不把 missing evidence 当成 permission to fabricate evidence。
- 不把 framework acceptance pass 当成 paper submission readiness。
- 不负责 prompt / skill / validator / v2 loop 的持续优化；那属于 `autoresearch-system-optimizer`。

## stop_with
- human_stop_reached
- citation_check_failed
- evidence_check_failed
- review_check_failed
- acceptance_check_failed
- checkpoint_budget_reached
- graph_frontier_empty
