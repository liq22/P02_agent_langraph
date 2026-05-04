# Codex Prompt 09 — Traceability Lock

Use this prompt before writing or merging any paper claim, table, or figure.

## Required steps

1. Read `docs/submission_ready_goal/traceability/traceability_lock.md`.
2. Create or update `docs/submission_ready_goal/traceability/traceability_matrix.yaml`.
3. For every claim/table/figure, fill:
   - item_id
   - item_type
   - paper_section
   - evidence_id
   - data_manifest
   - vibench_read_bundle
   - PHMGA submodule commit
   - experiment_id
   - artifact_dir
   - result_md
   - ledger row
   - main table row or limitation note
4. Run `python tools/submission_ready_goal/validate_traceability_lock.py --matrix docs/submission_ready_goal/traceability/traceability_matrix.yaml`.
5. Do not write positive result prose for entries whose status is not `supported`.
