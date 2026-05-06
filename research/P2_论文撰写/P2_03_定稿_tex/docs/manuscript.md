# P2_03 TeX Synchronization Note

This node synchronizes the current manuscript state into an exportable TeX draft. It does not declare the whole paper submission-ready.

## Venue Format Key Items

The current export target is a Nature-style article draft boundary: abstract, introduction, preliminaries, methods, results, discussion, data availability, and code availability must be visible in `tex/main.tex`. The draft also keeps the P2_03 section hierarchy and availability statements explicit so later venue-specific formatting can be applied without changing scientific content.

## Markdown Specialization

The section map points to four Markdown sources. The Methods source is substantive and was synchronized into `tex/sections/method.tex`. The Introduction, Preliminary, and Experiment/Discussion sources were not substantive at synchronization time, so P2_03 generated conservative TeX sections that disclose the evidence boundary rather than pretending the source drafts were complete.

## Current Output

This round produced:

- `tex/main.tex`
- `tex/sections/introduction.tex`
- `tex/sections/preliminary.tex`
- `tex/sections/method.tex`
- `tex/sections/experiment.tex`
- `artifacts/export_constraints.yaml`
- `artifacts/tex_sync_plan.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/citation_registry.yaml`
- `artifacts/tex_compile_report.yaml`

The only quantitative signal carried into the TeX draft is the P1_04/P1_05/P1_09 preliminary synthetic/offline single-run evidence. It is embedded as a table-style TeX figure with a label, caption, claim_ref, evidence_ref, and provenance note. The draft explicitly blocks formal real-data performance, RM101 resolution, selected-backend readiness, and final submission-readiness claims.
