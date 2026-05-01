---
skill_id: P4_07_再投稿打包_local_entry
purpose: 执行一次有界再投稿打包检查，核对 submission bundle consistency、citation registry、figure manifest、venue
  requirements 并生成 bundle manifest。
node_mode: execution
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_execution_skill: local_execution
required_local_reads:
- ../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
- ../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex
- ../P4_06_修改证据/artifacts/revision_evidence_map.yaml
- artifacts/evidence_registry.yaml
- artifacts/submission_metadata.yaml
- ../../P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml
- ../../P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml
- ../../P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml
- artifacts/figures/
- artifacts/tables/
outputs:
- artifacts/resubmission_bundle_manifest.yaml
extra_status_updates:
- progress_pct
---

Runtime entry shim for this execution node.

This shim applies to `research/P4_论文回复_response/P4_07_再投稿打包`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex`
5. `../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex`
6. `../P4_06_修改证据/artifacts/revision_evidence_map.yaml`
7. `artifacts/evidence_registry.yaml`
8. `artifacts/submission_metadata.yaml`
9. `../../P2_论文撰写/P2_03_定稿_tex/artifacts/citation_registry.yaml`
10. `../../P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml`
11. `../../P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`
12. `artifacts/figures/`
13. `artifacts/tables/`
14. `skills/SKILL.md`
15. `skills/SOP.md`
16. `skills/local_execution.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
