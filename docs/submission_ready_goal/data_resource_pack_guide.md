# Data Resource Pack Guide

## Expected DATA_ROOT

```text
<DATA_ROOT>/
├── README.md
├── metadata.xlsx
├── metadata_25_10_30.xlsx
├── metadata_25_11_13.xlsx
├── RM_001_CWRU.h5
├── RM_002_XJTU.h5
├── RM_003_FEMTO.h5
├── RM_004_IMS.h5
├── RM_005_Ottawa23.h5
├── RM_006_THU.h5
├── RM_007_MFPT.h5
├── RM_008_UNSW.h5
├── RM_010_SEU.h5
├── RM_015_susu.h5
├── RM_016_JNU.h5
├── RM_017_Ottawa19.h5
├── RM_018_THU24.h5
├── RM_020_DIRG.h5
├── RM_023_HIT23.h5
├── RM_024_JUST.h5
├── RM_027_PU.h5
├── RM_031_HUST24.h5
└── RM_101_THU_GEARBOX.h5
```

## Canonical policy

- `metadata.xlsx` is the canonical metadata file unless the user explicitly promotes another file.
- `metadata_25_10_30.xlsx` and `metadata_25_11_13.xlsx` are metadata lineage files.
- `RM_017_Ottawa19.h5` and `RM_101_THU_GEARBOX.h5` are the minimum formal P02 datasets.
- Other `RM_*.h5` files are extension resources and do not block the first submission-ready path.

## Required audit outputs

```text
<data_audit_output>/
├── data_manifest.yaml
├── dataset_registry.yaml
├── checksums.sha256
├── metadata_audit.json
├── h5_audit.json
├── metadata_h5_alignment.json
└── data_readiness_scorecard.yaml
```

## Minimal metadata-H5 alignment check

For each formal dataset:

1. Metadata contains rows matching the dataset name.
2. H5 contains keys referenced by selected sample IDs, or the data-read adapter documents the mapping.
3. Sampling rate, length, channel count, and label can be resolved.
4. Missing or inconsistent records are written to a failure register.
