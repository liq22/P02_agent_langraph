---
name: auto_experiment_worker
description: Run one bounded experiment campaign inside one already selected node using an explicit execution contract. Use for lightweight validation, ablation, or controlled code experiments after local entry or local execution has bound repo_path, run_command, metric, and budget.
---

# Auto Experiment Worker

## 使用时机
- 已经选定一个实验 node
- 已经提供显式 execution contract
- 需要执行 baseline-first、metric-driven 的有界实验循环

## 必要输入
- `artifacts/execution_contract.yaml` 或等价显式 contract
- `contract_mode: executable`
- `repo_path`、`editable_paths`、`run_command`
- `metric.*` 与 `budget.*`

## Workflow
1. 验证 contract 完整性与 `contract_mode`；缺字段或 mode 不是 `executable` 就立即停止。
2. 先跑 clean baseline，不先改代码。
3. 每轮只尝试一个 conceptual change，并记录 hypothesis 与 expected signal。
4. 解析 metric，按 keep / discard 规则决定保留还是回滚；相近结果优先选择更简单、风险更低的方案。
5. 把 run log、metric row、decision、claim impact 写入本地 ledger 与日志。
6. 只有在 `artifacts/auto_experiment/results.tsv` 与 `logs/auto_experiment/latest_run.log` 都写入且 keep/discard 结论明确后，才允许报告本节点实验部分完成。
7. 只更新当前 node 的本地状态，不碰 graph。

## 产出
- `artifacts/auto_experiment/results.tsv`
- `logs/auto_experiment/latest_run.log`
- 当前 node 的局部状态更新

## 边界
- 不读 graph
- 不选 node
- 不发现 skill
- 不刷新全局
- 不猜 execution contract
- 不执行无界循环
- 不把候选 ranking / tournament 扩成全局自动研究
- 不把 `review_only` contract、缺 baseline、缺 metric parser、缺 results.tsv 或无法复现的实验称为 Nature-ready evidence

## stop_with
- 缺 execution contract
- execution contract 仍处于 `review_only`
- metric 无法解析
- budget 用尽
- baseline 未通过或 metric parser 不可信
- 需要未授权的破坏性修改
- 当前 node 状态被外部改变
- 无法形成可供 `scripts/validate_research_truth.py --require-submission` 追踪的本地证据
