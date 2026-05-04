# Codex Prompt: Patch or Document Vibench Read Boundary

```text
/goal
Patch or document the read-only PHM-Vibench data_factory boundary for P02.

Scope:
- PHM-Vibench data_factory should provide metadata/H5/raw/cache reading only.
- PHMGA must retain DatasetProtocol, split/window, DAG workflow, bridge, ML/Torch evaluation, reports, ledger, and main tables.

Preferred implementation:
- Add or use a read-only data_factory path if available.
- If modifying PHM-Vibench is out of scope, implement a PHMGA-side VibenchReadAdapter that imports the minimal reading components and does not use Vibench trainer/evaluator.

Required outputs:
- vibench_read_bundle.yaml for RM_017_Ottawa19
- vibench_read_bundle.yaml for RM_101_THU_GEARBOX
- documentation showing Vibench-owned vs PHMGA-owned responsibilities
- tests or smoke checks proving Vibench DataLoader/trainer is not used as formal result source

Stop if:
- Vibench task wrappers or samplers are needed to define PHMGA split/window.
- PHMGA DatasetProtocol is bypassed.
```
