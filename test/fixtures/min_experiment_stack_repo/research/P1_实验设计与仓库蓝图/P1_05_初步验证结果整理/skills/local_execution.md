---
skill_id: P1_05_初步验证结果整理_local_execution
purpose: 收敛轻量验证结果，形成支持/不支持/待澄清的结论边界。
required_inputs:
- artifacts/auto_experiment/results.tsv
outputs:
- artifacts/result_registry.yaml
- artifacts/hypothesis_status.yaml
stop_conditions:
- missing_results_tsv
- evidence_still_incoherent
node_profile: result_synthesis
required_local_reads:
- artifacts/auto_experiment/results.tsv
optional_local_reads:
- docs/manuscript.md
extra_status_updates:
- lifecycle.stage
- progress_pct
---

Use this execution path only after `skills/local_entry.md` selected it.
Verify the declared results ledger, then run exactly one bounded result-synthesis round: classify supported / unsupported / unclear, update the declared registry files, and stop without consulting any experiment gate or refreshing graph.
