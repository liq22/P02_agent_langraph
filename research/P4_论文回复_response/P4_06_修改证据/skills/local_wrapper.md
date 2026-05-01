---
skill_id: P4_06_修改证据_local_wrapper
purpose: 为 structured_map_builder 绑定修改证据映射的本地输入输出。
canonical_target: structured_map_builder
io_contract:
  inputs:
  - ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
  - ../P4_03_逐点回复草稿_md/docs/manuscript.md
  - ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
  outputs:
  - artifacts/revision_evidence_map.yaml
required_local_reads:
- ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
- ../P4_03_逐点回复草稿_md/docs/manuscript.md
- ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local IO contract and delegate exactly one bounded canonical worker round.
