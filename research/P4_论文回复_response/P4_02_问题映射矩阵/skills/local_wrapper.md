---
skill_id: P4_02_问题映射矩阵_local_wrapper
purpose: 为 structured_map_builder 绑定审稿问题映射矩阵的本地工件路径。
canonical_target: structured_map_builder
io_contract:
  inputs:
  - artifacts/review_comment_register.yaml
  outputs:
  - artifacts/question_mapping_matrix.yaml
required_local_reads:
- artifacts/review_comment_register.yaml
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
