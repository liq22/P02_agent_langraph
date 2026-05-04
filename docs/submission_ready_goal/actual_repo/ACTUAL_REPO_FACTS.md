# Actual Repository Facts for P02_agent_langraph

This file records the current repository facts that the `/goal` workflow must obey.

## Paper workspace

- Repository: `liq22/P02_agent_langraph`
- Role: P02 paper/autoresearch workspace.
- Research content lives under `research/`.
- Graph files under `backend/graph/` schedule work and are not content stores.
- Each Codex loop must advance one selected node unless a documented maintenance command is being run.

## Current selected node

Current `backend/graph/graph_status.json` reports:

```text
current_phase = P1
next_node = research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用
unfinished_count = 34
```

The selected node path is:

```text
research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用
```

The node is an `evidence_leaf`. Its local purpose is to converge data objects, data lineage, and submodule references.

## Required node-local outputs

The local entry declares these node outputs:

```text
docs/manuscript.md
artifacts/data_lineage.yaml
artifacts/submodule_ref.yaml
```

The node acceptance checklist additionally requires:

```text
artifacts/claim_evidence_registry.yaml
artifacts/failure_register.yaml
artifacts/negative_result_note.md
artifacts/keep_discard_ledger.yaml
```

This package adds optional but recommended P02-specific artifacts:

```text
artifacts/vibench_data_factory_binding.yaml
artifacts/data_reading_boundary.yaml
artifacts/phmga_data_protocol_handoff.yaml
artifacts/result_source_map.yaml
logs/codex_run_001.md
```

## PHMGA submodule

PHMGA is included as a submodule:

```text
path = research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
url = https://github.com/PHMbench/PHMGA.git
branch = journal_thesis
```

## PHMGA project truth

PHMGA is the implementation/project repository. Its current paper mainline is:

```text
protocol -> PHMState/StateGraph -> plan_agent -> execute_agent -> dag_quality_evaluator -> reflect_agent -> validated DAG JSON -> bridge -> graph-dependent artifacts -> inquirer_agent -> report_agent
```

The official PHMGA human entrypoint is `main.py`. Formal runs must not be redefined by ad hoc scripts.

## Data reading truth

PHM-Vibench data_factory is used for data reading only:

```text
metadata loading
reader selection
H5/raw signal/cache access
metadata-H5 alignment audit
```

PHMGA owns everything after reading:

```text
DatasetProtocol
SplitManifest
WindowSpec
SignalRecord
split-before-windowing
DAG workflow
bridge compilation
ML/Torch evaluation
result ledger
main tables
report
```

## Current hard blocker

PHMGA formal main tables are not yet paper-ready until they contain passed run IDs with traceability to result files and artifact directories.
