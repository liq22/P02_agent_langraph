---
skill_id: P1_08_预期结果与表格_local_wrapper
purpose: 为 structured_map_builder 绑定表格计划与 claim map 的本地路径。
canonical_target: structured_map_builder
io_contract:
  inputs:
  - docs/manuscript.md
  outputs:
  - artifacts/table_plan.yaml
  - artifacts/claim_map.yaml
required_local_reads:
- docs/manuscript.md
extra_status_updates:
- progress_pct
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
