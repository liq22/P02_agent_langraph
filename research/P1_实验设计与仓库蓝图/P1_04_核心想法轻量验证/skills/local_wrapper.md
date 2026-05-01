---
skill_id: P1_04_核心想法轻量验证_local_wrapper
purpose: 为 auto_experiment_worker 绑定本地 contract、ledger 与日志路径。
canonical_target: auto_experiment_worker
io_contract:
  inputs:
  - artifacts/execution_contract.yaml
  outputs:
  - artifacts/auto_experiment/results.tsv
  - logs/auto_experiment/latest_run.log
execution_profile: experiment_execution
required_local_reads:
- artifacts/execution_contract.yaml
optional_local_reads:
- docs/manuscript.md
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path and confirmed that the contract is executable, `repo_path` exists in the workspace, and the run target is bindable.
Bind the declared execution contract and fixed auto-experiment artifact paths, then delegate exactly one bounded `auto_experiment_worker` round.
