# Codex Prompt: Patch PHMGA Handoff

```text
/goal
Inside the PHMGA submodule, add or validate the handoff from Vibench read bundle to PHMGA DatasetProtocol.

Read:
- PHMGA README.md
- PHMGA doc/structure/00_problem_and_protocol.md
- PHMGA src/data/protocol.py
- PHMGA config/data/ottawa.yaml
- PHMGA config/data/rm101.yaml
- docs/submission_ready_goal/schemas/phmga_handoff.schema.yaml

Tasks:
1. Ensure PHMGA can accept data_source.reader_backend = vibench_data_factory.
2. Ensure PHMGA still owns split and window.
3. Ensure signal shape normalization remains under PHMGA.
4. Ensure preflight works for Ottawa and RM101.
5. Write or update a handoff audit artifact.

Run if feasible:
- python main.py runtime.action=preflight +runs=ottawa_ml_test
- python main.py runtime.action=preflight +runs=rm101_ml_test
- python -m pytest tests/unit tests/smoke

Do not change agent, DAG, bridge, training, evaluation, or reporting semantics unless needed to preserve the handoff contract.
```
