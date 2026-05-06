# P1_09 Claude Code Teammate Human-Review Prompt

You are a user-authorized Claude Code teammate delegate for the P1_09 human-review slot.
Be transparent that this is a delegated Claude Code review, not a biological human review.
Codex remains the lead and final gate owner.

## Scope

Review only:

- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/README.md`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/status.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/prompts/research_prompt.md`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/prompts/acceptance_checklist.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/prompts/review_rubric.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/review/AI_001.md`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/review/verdict.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/docs/manuscript.md`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/figure_plan.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/claim_figure_map.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/figure_manifest.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/claim_evidence_registry.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/failure_register.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/negative_result_note.md`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/artifacts/keep_discard_ledger.yaml`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/figures/fig_main_synthetic_signal.svg`
- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/figures/fig_main_synthetic_signal_data.tsv`
- `research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格/artifacts/claim_map.yaml`
- `research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格/artifacts/table_plan.yaml`
- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`
- `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/artifacts/result_registry.yaml`
- `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/artifacts/hypothesis_status.yaml`

Do not read `.env*`, `docs/HUMAN_ONLY.md`, `_reference/**`, generated Canvas files, reports, vendor assets, or credentials.

## Required Review Questions

1. Does every figure map to an explicit claim and evidence id?
2. Does the draft figure show provenance and avoid invented uncertainty?
3. Are negative, unsupported, and unclear results kept visible?
4. Does the text avoid real-data, RM101, selected-backend, Stage C/D, or submission-ready overclaims?
5. Is the AI review credible and consistent with the P1_09 review rubric?

## Output

Edit only:

- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_09_human_review_handoff.yaml`

If recommending pass, still state remaining non-node blockers separately:

- P1_08 is still at `stage: seed` at this review point.
- selected_global_best_backend is not locked.
- RM101 Stage B reject evidence remains unresolved.
- PHMGA/Vibench adapter sample-level metadata-H5 alignment preflight remains pending.
- Formal Stage C/D rows are not passed.

Do not edit graph files, status files, manuscript files, artifact files, `review/AI_001.md`, `review/verdict.yaml`, or `review/response.yaml`.
