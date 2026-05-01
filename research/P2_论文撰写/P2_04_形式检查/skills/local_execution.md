---
skill_id: P2_04_形式检查_local_execution
purpose: 执行一次有界形式检查，只输出高置信格式问题。
required_inputs:
- docs/manuscript.md
outputs:
- artifacts/formal_check_report.md
stop_conditions:
- missing_manuscript
- target_format_unspecified
required_local_reads:
- docs/manuscript.md
- ../P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml
- ../P2_03_定稿_tex/artifacts/citation_registry.yaml
- ../P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml
extra_status_updates:
- progress_pct
---

Use this execution path only after `skills/local_entry.md` selected it.
Verify the declared required inputs, then run exactly one bounded local execution round without widening scope or refreshing graph.
