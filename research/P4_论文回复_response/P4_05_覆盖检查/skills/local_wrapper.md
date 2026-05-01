---
skill_id: P4_05_覆盖检查_local_wrapper
purpose: 为 response_coverage_check 绑定 mapping、response 与 report 路径。
canonical_target: response_coverage_check
io_contract:
  inputs:
  - ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
  - ../P4_03_逐点回复草稿_md/docs/manuscript.md
  outputs:
  - artifacts/coverage_check_report.yaml
required_local_reads:
- ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
- ../P4_03_逐点回复草稿_md/docs/manuscript.md
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
