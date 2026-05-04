# P02 Paper Evidence Readiness

## Evidence chain

Every paper claim, table, and figure must trace through:

```text
DATA_ROOT
→ data_manifest.yaml
→ vibench_read_bundle.yaml
→ PHMGA DatasetProtocol
→ validated_dag.json
→ compiled_dag_manifest.json
→ feature_pipeline.json
→ metrics.json
→ final_report.md
→ doc/experiments/01_result_ledger.md
→ doc/experiments/02_main_tables.md
→ P02_agent_langraph claim_evidence_registry
→ main.tex
```

## Claim record format

```yaml
claim_id: C-P02-001
claim: <paper claim>
section: Method | Experiment | Discussion
status: supported | unsupported | unclear | planned
evidence:
  - evidence_id: E-P02-001
    type: data | artifact | result | figure | table | review
    data_manifest: <path>
    vibench_read_bundle: <path>
    phmga_submodule_commit: <sha>
    phmga_experiment_id: <id>
    artifact_dir: <path>
    result_md: <path>
    ledger_row: <id>
    main_table: <table id>
```

## Hard rule

If a claim does not have an evidence ID, it may remain in notes, but it cannot enter final manuscript as a supported claim.
