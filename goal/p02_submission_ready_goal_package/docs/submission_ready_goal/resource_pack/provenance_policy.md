# Provenance Policy

## Must record

- data root path
- canonical metadata file
- metadata lineage files
- H5 file list
- checksum manifest
- access/license statement
- audit date
- PHM-Vibench commit or version, if available
- PHMGA submodule commit

## Formal result provenance

Every formal result must trace to:

```text
data_manifest.yaml
vibench_read_bundle.yaml
PHMGA submodule commit
experiment_id
artifact_dir
result_md
ledger row
main table row
```

## Do not

Do not claim a result is reproducible if the data root, checksum, or submodule commit is missing.
