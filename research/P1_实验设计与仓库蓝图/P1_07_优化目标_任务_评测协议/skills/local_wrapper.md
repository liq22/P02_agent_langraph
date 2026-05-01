---
skill_id: P1_07_优化目标_任务_评测协议_local_wrapper
purpose: 为 structured_map_builder 绑定协议图与实验严谨性计划的本地输入输出。
canonical_target: structured_map_builder
io_contract:
  inputs:
  - docs/manuscript.md
  outputs:
  - artifacts/protocol_map.yaml
  - artifacts/experiment_rigor_plan.yaml
required_local_reads:
- docs/manuscript.md
extra_status_updates:
- progress_pct
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
