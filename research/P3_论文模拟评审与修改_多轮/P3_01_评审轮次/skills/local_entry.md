---
skill_id: P3_01_评审轮次_local_entry
purpose: 推进单轮评审或单轮 critique 生成，不扩成全 repo review 系统。
node_mode: lite
node_profile: lite_research_leaf
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  canonical_global_skill: auto_review_loop
required_local_reads:
- ../prompts/standards.md
- ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
outputs:
- artifacts/review_round_notes.md
---

Runtime entry shim for this lite node.

This shim applies to `research/P3_论文模拟评审与修改_多轮/P3_01_评审轮次`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../prompts/standards.md`
5. `../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
