
# P02 Submission-Ready Goal Package — Actual Repo Operating Contract

This package is optimized for the current `liq22/P02_agent_langraph` repository state.
It is a Codex `/goal` support package, not a `/goal` filesystem directory.

## Actual repository facts

- Paper/autoresearch repository: `liq22/P02_agent_langraph`.
- Current active graph state: `current_phase=P1` and `next_node=research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用`.
- Current selected node path: `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用`.
- Selected node lifecycle is expected to start at `stage: seed` with `progress_pct: 0`.
- PHMGA implementation submodule path:
  `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA`.
- PHMGA submodule branch: `journal_thesis`.
- PHMGA is the only project implementation and experiment evidence source.
- PHM-Vibench `data_factory` is the data-reading system only.

## Non-negotiable authority split

```text
DATA_ROOT / manifest / checksum / Vibench read bundle = data truth
PHMGA submodule / artifact_dir / result_md / ledger / main tables = project truth
P02_agent_langraph selected nodes / claim-evidence / reviews / final TeX = paper truth
```

## Current first action

Do not jump to experiments or manuscript prose. First close the selected node:

```text
research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用
```

The node-local done-state is its own `prompts/acceptance_checklist.yaml` and `prompts/review_rubric.yaml`.
The minimum node-local outputs are:

```text
docs/manuscript.md
artifacts/data_lineage.yaml
artifacts/submodule_ref.yaml
artifacts/vibench_data_factory_binding.yaml
artifacts/data_reading_boundary.yaml
artifacts/phmga_data_protocol_handoff.yaml
artifacts/result_source_map.yaml
artifacts/claim_evidence_registry.yaml
artifacts/failure_register.yaml
artifacts/negative_result_note.md
artifacts/keep_discard_ledger.yaml
logs/codex_run_001.md
review/AI_001.md
review/verdict.yaml
review/response.yaml
```

## Codex role

Codex is the `/goal` orchestrator and gate owner. Codex may draft selected-node text only after the relevant evidence state is explicit. Codex must not act as a solo writer for the whole paper.

## Claude Code role

Claude Code may be used only as a bounded assistant for audit/review/exploration. Claude Code must return a `claude_code_handoff_v2` artifact. Codex validates the handoff before any merge or checklist update.

## Forbidden

- Do not manually edit `backend/graph/graph.json` or `backend/graph/graph_status.json`.
- Do not write manuscript/review/artifact bodies into graph or Canvas files.
- Do not scan `_reference/**` unless explicitly requested.
- Do not commit H5 files or large DATA_ROOT contents into the paper repo.
- Do not use PHM-Vibench task wrappers, samplers, trainers, evaluators, or DataLoader outputs as formal P02 result truth.
- Do not use pending/fail/no_evidence/planner-timeout/transport-failure rows in paper tables.
- Do not declare submission-ready before `python scripts/validate_research_truth.py --require-submission` passes.
