---
skill_id: P4_04_正式回复_tex_或_doc_local_wrapper
purpose: 为 draft_export_sync 绑定 response draft -> response letter 的局部导出目标。
canonical_target: draft_export_sync
io_contract:
  inputs:
  - docs/manuscript.md
  outputs:
  - artifacts/response_letter.tex
required_local_reads:
- docs/manuscript.md
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
