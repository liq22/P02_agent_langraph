---
skill_id: P2_03_定稿_tex_local_wrapper
purpose: 为 draft_export_sync 绑定 manuscript -> tex/main.tex 的局部同步目标。
canonical_target: draft_export_sync
io_contract:
  inputs:
  - docs/manuscript.md
  - section_map.yaml
  - sync_map.yaml
  outputs:
  - tex/main.tex
required_local_reads:
- docs/manuscript.md
- section_map.yaml
- sync_map.yaml
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
