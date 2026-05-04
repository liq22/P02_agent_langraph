# PHM-Vibench Data Factory to PHMGA Boundary

## Boundary statement

P02 uses PHM-Vibench `data_factory` as the data reading and catalog interface only. It does not use Vibench task wrappers, samplers, trainers, or evaluators as formal paper result sources.

## PHM-Vibench owns

- metadata loading
- dataset reader selection
- raw/H5 signal access
- cache/materialization
- ID lookup
- metadata-H5 alignment audit

## PHMGA owns

- `DatasetProtocol`
- `SplitManifest`
- `WindowSpec`
- `SignalRecord`
- split-before-windowing
- signal layout normalization
- `PHMState / StateGraph`
- `plan_agent -> execute_agent -> dag_quality_evaluator -> reflect_agent`
- `validated DAG JSON`
- `compile_dag_for_path()` bridge
- graph-dependent artifacts
- ML/Torch evaluation
- report generation
- result ledger
- main paper tables

## Read-only handoff

The only accepted handoff from Vibench to PHMGA is a read bundle:

```text
vibench_read_bundle.yaml
```

PHMGA then builds its own protocol and experiment artifacts from that read bundle.

## Forbidden shortcuts

- Do not let Vibench DataLoader determine PHMGA training semantics.
- Do not let Vibench sampler define paper split semantics.
- Do not use Vibench trainer/evaluator output as PHMGA formal result.
- Do not bypass PHMGA `DatasetProtocol`.
