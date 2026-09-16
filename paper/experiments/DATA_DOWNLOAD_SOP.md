# Data acquisition and admission — checked 2026-09-16

No dataset in this document was downloaded or admitted by this revision. Data belong outside P02. Set `DATA_ROOT` to private local storage; retain original archives, version/terms and conversion notes. A download command is not a tested DataPort or an approved experiment. Do not send restricted raw data to an external model service merely because an API key exists.

## Main mechanical source: Paderborn

Official source: https://mb.uni-paderborn.de/en/kat/research/bearing-datacenter ; downloads: https://mb.uni-paderborn.de/kat/forschung/bearing-datacenter/data-sets-and-download . Academic noncommercial use is allowed under CC BY-NC 4.0 with attribution to Lessmeier et al. (2016); commercial use requires separate permission. Select the original bearing archives and bearing fact sheets, not a third-party prewindowed split.

Use the archive link copied from that official page:

```bash
mkdir -p "$DATA_ROOT/paderborn/raw"
curl -fL "$OFFICIAL_PADERBORN_ARCHIVE_URL" -o "$DATA_ROOT/paderborn/raw/$ARCHIVE_NAME"
```

The input URL and name are explicit manual selections, not a tested auto-downloader. Keep bearing identity as the independent unit, machine/operating setting as metadata, and file-level acquisition groups intact. Convert MATLAB signal records through the existing data preparation path to the already registered HDF5/metadata format or supported per-record CSV source; preserve channels, sample rate and units. Fit normalizers/experts on training assets only. The current benchmark uses a fixed short window and expert contract; do not infer a fault-onset timestamp from a file's fault class.

## X1 — Physiological waveforms: PTB-XL 1.0.3

Source/version: https://physionet.org/content/ptb-xl/1.0.3/ ; DOI 10.13026/kfzx-aw45, CC BY 4.0. Retain the WFDB files, `ptbxl_database.csv` and `scp_statements.csv`.

```bash
aws s3 sync --no-sign-request s3://physionet-open/ptb-xl/1.0.3/ "$DATA_ROOT/ptbxl-1.0.3"
```

Use either 100-Hz or 500-Hz records as an explicit condition, not a mixed array. Patient identity defines the split unit; official `strat_fold` 1–8/9/10 defines train/validation/test. Parse SCP code mappings as multilabel targets; do not silently convert coexisting diagnoses into a single label. A multilabel task/evaluator binding is missing in current Phase1. Convert WFDB physical samples to per-record arrays with units and patient groups preserved. This is a supplementary research dataset, not clinical validation.

## X2 — Inertial activity: UCI HAR, dataset 240

Official source: https://archive.ics.uci.edu/dataset/240/human+activity+recognition+using+smartphones ; DOI 10.24432/C54S4K, CC BY 4.0. Select its official Download link and save `UCI HAR Dataset.zip` under `$DATA_ROOT/uci-har/raw/`; the download click could not be executed by the browsing tool in this session.

```bash
mkdir -p "$DATA_ROOT/uci-har/raw"
curl -fL "$UCI_HAR_OFFICIAL_DOWNLOAD_URL" -o "$DATA_ROOT/uci-har/raw/UCI-HAR.zip"
unzip -n "$DATA_ROOT/uci-har/raw/UCI-HAR.zip" -d "$DATA_ROOT/uci-har/source"
```

Use `Inertial Signals`, not just the precomputed 561-feature table. Preserve 50-Hz, 128-reading windows, activity labels 1–6 and subject IDs. The official split is subject-based; reserve validation subjects from training only. Windows overlap by 50%; do not reshuffle them across partitions or claim that the published window collection is an uninterrupted online stream. A subject/task binding and numerical adapter are still missing.

## X3 — Spacecraft telemetry: SMAP/MSL (Telemanom release)

Author source: https://github.com/khundman/telemanom ; its current README points to the Kaggle dataset below. Record the downloaded Kaggle version and the author-source revision. Apache 2.0 is stated for the software; the archive's data-usage terms still need inspection rather than being inferred from the code license.

```bash
kaggle datasets download -d patrickfleith/nasa-anomaly-detection-dataset-smap-msl \
  -p "$DATA_ROOT/telemanom/raw"
```

This requires the user's Kaggle setup. Retain `.npy` train/test streams and `labeled_anomalies.csv`; labels are interval indices, not physical timestamps. Check endpoint inclusivity against the author's label conversion before scoring. Each stream contains telemetry as its first feature plus encoded commands. Preserve official temporal halves and retain whole related subsystems in uncertainty analysis. The source explicitly says values are pre-scaled using **test-set extrema**. Thus this release is a legacy telemetry comparison, not evidence of strict no-future normalization. Raw train-normalized data would be needed for that stronger claim. No current shared-runtime binding exists.

## X4 — Server telemetry: SMD / OmniAnomaly author release

Source: https://github.com/NetManAIOps/OmniAnomaly , `ServerMachineDataset/{train,test,test_label,interpretation_label}`. The author repository is MIT-licensed; record the original snapshot and check whether separate dataset terms accompany it.

```bash
git clone https://github.com/NetManAIOps/OmniAnomaly.git "$DATA_ROOT/smd-source"
```

The source describes 28 machines, 38 dimensions and earlier/later temporal halves. Preserve machine IDs, train/test ordering and point labels. Train each registered normal reference without test labels; derive validation from training. The upstream example selects best F1 on test in one analysis path: do **not** copy that selection into the confirmatory protocol. Convert text arrays without dropping channels and bind per-machine scores. Machine-level transfer and within-machine temporal detection are different conditions. Loader/task integration remains pending.

## X5 — Process instrumentation: SWaT.A2_Dec2015 normal version 1

Official page: https://www.sutd.edu.sg/itrust/itrust-labs/datasets/ ; request: https://www.sutd.edu.sg/itrust/request-for-datasets/ ; terms: https://www.sutd.edu.sg/itrust/itrust-labs/datasets/terms-of-usage/ . Request the historian sensor dataset and its readme, not network traces. Terms require attribution/notification and prohibit sharing the received data, including private sharing. There is no public anonymous wget path.

Download manually from the granted link to `$DATA_ROOT/swat/source/`. Record the provided files and exact release. Version 1 of the normal collection excludes the first 30-minute drainage period; do not apply that deletion again. Preserve timestamps, sensor/actuator columns and normal/abnormal labels. Normal training, contiguous training-derived validation and later abnormal evaluation must remain ordered. The physical unit is one plant, not 51 independent machines; block intervals do not establish cross-plant generalization. This study consumes prerecorded abnormal sensor data, not an attack-generation benchmark. The task binding is not implemented.

## Admission after acquisition

For every source, complete a small real read: file count, one named record, shape/dtype, sample rate, units, missing-value policy, label mapping and independent-unit assignment. Freeze the split before fitting. Save checkpoint metadata (training units, input representation, chosen validation epoch and parameters); reload it and reproduce saved predictions and the same metrics. Predictions used for test may not select the checkpoint. No new model checkpoint is necessary for a training-free Graph policy, but its frozen numerical experts still require recorded fits.

Implement conversions only in Benchmark/DataPort consumer code, not P02 and not by altering PHMFactory core to accept a mistaken split. Keep all five external groups marked `source_verified_binding_pending` until actual read, label, split, numerical and evaluator checks pass. Do not produce expected result curves while awaiting access.
