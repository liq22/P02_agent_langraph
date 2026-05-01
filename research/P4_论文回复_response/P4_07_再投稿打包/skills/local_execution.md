---
skill_id: P4_07_再投稿打包_local_execution
purpose: 执行一次有界再投稿打包检查并生成 bundle manifest。
required_inputs:
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
stop_conditions:
- missing_submission_assets
- naming_inconsistency_detected
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
extra_status_updates:
- progress_pct
---

Use this execution path only after `skills/local_entry.md` selected it.
Verify the declared required inputs, then run exactly one bounded local execution round without widening scope or refreshing graph.
