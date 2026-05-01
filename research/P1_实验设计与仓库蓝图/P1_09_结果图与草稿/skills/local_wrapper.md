---
skill_id: P1_09_结果图与草稿_local_wrapper
purpose: 为 paper_figure 绑定 figure plan、claim map 与 figures 输出路径。
canonical_target: paper_figure
io_contract:
  inputs:
  - docs/manuscript.md
  - ../P1_08_预期结果与表格/artifacts/claim_map.yaml
  - artifacts/figure_plan.yaml
  outputs:
  - artifacts/figure_plan.yaml
  - artifacts/claim_figure_map.yaml
  - artifacts/figure_manifest.yaml
  - figures/
required_local_reads:
- docs/manuscript.md
- ../P1_08_预期结果与表格/artifacts/claim_map.yaml
- artifacts/figure_plan.yaml
extra_status_updates:
- progress_pct
---

Use this wrapper only after `skills/local_entry.md` selected the wrapper path.
Bind the declared local figure IO, including `artifacts/figure_manifest.yaml` when present, then delegate exactly one bounded `paper_figure` round.
Figure drafts may come from TeX/TikZ/PGFPlots, Python, or human-provided PDF; once node status is `done`, do not overwrite accepted figure outputs.
