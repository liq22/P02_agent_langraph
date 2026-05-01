---
skill_id: P2_04_形式检查_local_entry
purpose: 执行一次有界形式检查，核对 citation criticality、figure provenance、venue requirements 与高置信格式问题。
node_mode: execution
node_profile: hard_gate
required_prompt_refs:
- prompts/research_prompt.md
- prompts/acceptance_checklist.yaml
- prompts/review_rubric.yaml
default_delegate:
  local_execution_skill: local_execution
required_local_reads:
- docs/manuscript.md
- ../P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml
- ../P2_03_定稿_tex/artifacts/citation_registry.yaml
- ../P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml
outputs:
- artifacts/formal_check_report.md
extra_status_updates:
- progress_pct
---

Runtime entry shim for this execution node.

This shim applies to `research/P2_论文撰写/P2_04_形式检查`.

Assume `README.md` and `status.yaml` are already loaded by the caller.

Read in this order:
1. `prompts/research_prompt.md`
2. `prompts/acceptance_checklist.yaml`
3. `prompts/review_rubric.yaml`
4. `docs/manuscript.md`
5. `../P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`
6. `../P2_03_定稿_tex/artifacts/citation_registry.yaml`
7. `../P2_02_初稿_md/P2_02_03_流程图草稿/artifacts/figure_manifest.yaml`
8. `skills/SKILL.md`
9. `skills/SOP.md`
10. `skills/local_execution.md`

After the tier-required local stack is loaded, honor `decision_rule` and `default_delegate` exactly once.
Keep all work node-local, bounded, and auditable against the acceptance checklist.
Do not synthesize deeper local layers than this tier requires.
