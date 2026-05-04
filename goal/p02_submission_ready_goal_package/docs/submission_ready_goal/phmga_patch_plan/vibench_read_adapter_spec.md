# VibenchReadAdapter Specification

## Purpose

Add a thin read-only boundary from PHM-Vibench data_factory to PHMGA DatasetProtocol.

## Adapter owns

- Reading metadata and H5 paths from a Vibench-style data root.
- Producing `vibench_read_bundle.yaml`.
- Validating sample ID, label, channel, sampling-rate, and shape availability.

## Adapter does not own

- split
- windowing
- DAG planning
- bridge compilation
- training/evaluation
- report

## Minimal API

```python
bundle = VibenchReadAdapter(data_cfg).read()
protocol = build_protocol_from_vibench_bundle(bundle, data_cfg)
```
