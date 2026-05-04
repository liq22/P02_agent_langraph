# Codex Prompt: Update P02 Paper Nodes

```text
/goal
Backfill P02_agent_langraph research nodes with verified data provenance, PHMGA evidence, and claim-evidence registries.

Rules:
- Read backend/graph/graph_status.json.
- Work on the selected node only unless explicitly updating docs/submission_ready_goal.
- Do not write manuscript or evidence bodies into graph files or Canvas files.
- Every supported claim must have claim_id and evidence_id.
- Every table must trace to PHMGA result ledger, result_md, and artifact_dir.
- Every data source must trace to DATA_ROOT and vibench_read_bundle.

Required node outputs when applicable:
- docs/manuscript.md
- artifacts/claim_evidence_registry.yaml
- artifacts/data_lineage.yaml
- artifacts/result_source_map.yaml
- artifacts/failure_register.yaml
- artifacts/negative_result_note.md
- review/AI_001.md
- review/verdict.yaml
- review/response.yaml

Stop if:
- PHMGA main tables remain empty.
- selected_global_best_backend is pending.
- any central claim lacks evidence.
```
