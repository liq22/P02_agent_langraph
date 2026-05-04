# 01 Execute Actual P1_01 Node

```text
You are Codex executing exactly one selected node in `liq22/P02_agent_langraph`.

Selected node:
research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用

Node path:
research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用

Do not run PHMGA formal experiments.
Do not update unrelated nodes.
Do not edit graph JSON by hand.
Do not write to Canvas or dashboard files.

Use the node local contract. Required outputs:
- docs/manuscript.md
- artifacts/data_lineage.yaml
- artifacts/submodule_ref.yaml
- artifacts/claim_evidence_registry.yaml
- artifacts/failure_register.yaml
- artifacts/negative_result_note.md
- artifacts/keep_discard_ledger.yaml

Recommended P02-specific outputs:
- artifacts/vibench_data_factory_binding.yaml
- artifacts/data_reading_boundary.yaml
- artifacts/phmga_data_protocol_handoff.yaml
- artifacts/result_source_map.yaml
- logs/codex_run_001.md

Content requirements:
1. State that DATA_ROOT is user-provided and must not be committed.
2. State that PHM-Vibench data_factory is used only for reading metadata/H5/raw/cache.
3. State that PHMGA owns DatasetProtocol, split/window, DAG workflow, bridge, ML/Torch, evaluation, result ledger, main tables, and report.
4. Record PHMGA submodule path, URL, branch, and commit if available.
5. Record formal minimum data scope: RM_017_Ottawa19.h5 and RM_101_THU_GEARBOX.h5.
6. Record metadata lineage: metadata.xlsx is canonical, metadata_25_10_30.xlsx and metadata_25_11_13.xlsx are history unless promoted by user.
7. Do not state formal results as observed unless PHMGA ledger/main tables prove them.
8. Every claim must have claim_id/evidence_id or status=gap.

After writing outputs, run:
python tools/submission_ready_goal/validate_p1_01_node_outputs.py --node-dir research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用

Return files changed, command output, blockers, and next action.
```
