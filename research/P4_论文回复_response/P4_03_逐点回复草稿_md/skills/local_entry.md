---
skill_id: P4_03_逐点回复草稿_md_local_entry
purpose: 推进逐点回复草稿，保持一条评论对应一条局部 response 逻辑。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: response_worker
required_local_reads:
- ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
- ../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml
outputs:
- docs/manuscript.md
- artifacts/response_items.yaml
- logs/session_manifest.yaml
---

Runtime entry shim for this lite node.

This shim applies to `research/P4_论文回复_response/P4_03_逐点回复草稿_md`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex`
5. `../P4_02_问题映射矩阵/artifacts/question_mapping_matrix.yaml`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
