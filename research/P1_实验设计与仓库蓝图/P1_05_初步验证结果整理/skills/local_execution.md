---
skill_id: P1_05_初步验证结果整理_local_execution
purpose: 收敛初步验证结果、证据状态与结论边界。
required_inputs:
- research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
outputs:
- artifacts/result_registry.yaml
- artifacts/hypothesis_status.yaml
- artifacts/claim_evidence_registry.yaml
- artifacts/paper_ready_result_summary.md
stop_conditions:
- missing_results_tsv
- evidence_still_incoherent
execution_profile: result_synthesis
required_local_reads:
- research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
optional_local_reads:
- docs/manuscript.md
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Use this execution path only after `skills/local_entry.md` selected it.
Verify the declared results ledger, then run exactly one bounded result-synthesis round: classify supported / unsupported / unclear, update the declared registry files, and stop without consulting any experiment gate or refreshing graph.
