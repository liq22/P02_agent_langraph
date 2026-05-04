# Codex Prompt: Audit Data Resource Pack

```text
/goal
Audit the user-provided DATA_ROOT for P02 submission readiness.

Inputs:
- DATA_ROOT path supplied by the user.
- docs/submission_ready_goal/resource_pack/data_manifest_template.yaml
- docs/submission_ready_goal/checklists/00_data_package_intake_checklist.yaml

Tasks:
1. Verify required files exist:
   - metadata.xlsx
   - RM_017_Ottawa19.h5
   - RM_101_THU_GEARBOX.h5
2. Record metadata lineage files if present:
   - metadata_25_10_30.xlsx
   - metadata_25_11_13.xlsx
3. Compute SHA-256 checksums for canonical metadata and formal H5 files.
4. Audit H5 top-level keys and basic shapes for formal H5 files.
5. Audit metadata row count and likely dataset columns.
6. Produce:
   - data_manifest.yaml
   - dataset_registry.yaml
   - checksums.sha256
   - metadata_audit.json
   - h5_audit.json
   - metadata_h5_alignment.json
   - data_readiness_scorecard.yaml

Do not copy large H5 files into the repository.
Do not claim data-ready if metadata-H5 alignment cannot be checked.
```
