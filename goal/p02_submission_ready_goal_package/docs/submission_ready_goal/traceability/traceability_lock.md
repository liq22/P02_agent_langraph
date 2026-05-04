# Traceability Lock

The P02 paper can only use a claim, figure, or table after it is locked to evidence.

## Required path

```text
claim/table/figure
→ evidence_id
→ DATA_ROOT / data_manifest
→ vibench_read_bundle
→ PHMGA submodule commit
→ PHMGA experiment_id
→ artifact_dir
→ result_md
→ result_ledger row
→ main table row or limitation note
```

If any link is missing, the item remains `planned`, `unclear`, or `unsupported` and must not be written as a positive result.

## Main table rule

A PHMGA row can enter a paper table only when:

- `keep=accept`
- `artifact_contract_pass=pass`
- `feature_separability_pass=pass` when applicable
- `result_md` exists
- `artifact_dir` exists
- the row is present in `doc/experiments/02_main_tables.md`

Pending, failed, transport-failure, planner-timeout, and no-evidence rows are forbidden in paper tables.

## Claim status vocabulary

- `supported`: artifact-backed and reviewable.
- `planned`: expected but not yet observed.
- `unclear`: evidence exists but is insufficient.
- `unsupported`: no valid evidence.
- `negative`: failure or counter-evidence recorded.
