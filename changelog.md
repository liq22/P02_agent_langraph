# Changelog

## v0.0.1 - 2026-04-19

Initial runnable version of Autoresearch with Human.

This version establishes the repository as a folder-backed research OS: human sets direction and constraints, agents perform one bounded node-local step at a time, and the graph only schedules the next global step.

### Added

- Canonical research workspace under `research/`, where each schedulable node is a folder with `README.md`, `status.yaml`, and optional node-local prompts, skills, docs, artifacts, review, and logs.
- Minimal scheduler graph substrate under `backend/graph/`, generated from node status files and `backend/relations/edge_registry.json`.
- Explicit relation registry with the small practical relation set: `depends_on` and `addresses`.
- Unified refresh entrypoint: `python scripts/refresh_views.py --mode graph_only` for agent rounds and `python scripts/refresh_views.py --mode full` for cockpit, Canvas, dashboard, or human review projection refresh.
- Three active runtime entry surfaces: `graph_driven_research_orchestrator`, `auto_research_campaign`, and `auto_experiment_worker`.
- Node-local skill stack discipline using `local_entry.md`, optional wrapper/execution files, and canonical project skills under `.agent/skills/`.
- Execution contract path for bounded experiments, including baseline-first, metric-driven, one-change-at-a-time worker behavior.
- Local agent gateway and web cockpit for graph-aware bounded sessions.
- Validation suite for graph refresh, projection refresh, gateway behavior, node-local skill fit, experiment stack acceptance, and submission truth gates.

### Changed

- Graph, Canvas, dashboard, cockpit state, views, and indexes are treated as derived projections rather than research truth.
- Agent-facing workflow defaults to `graph_only` refresh; full projection refresh is reserved for human-facing surfaces.
- Review rubrics and verdict files are required only when a node explicitly enables an external review gate.
- Node templates were reduced toward minimal `README.md` plus `status.yaml` scaffolds, with deeper files activated only when a bounded step requires them.
- `backend/registry/skill_registry/` is used as a validation and generation catalog, not as a second runtime contract.

### Removed

- The old direction of a repo-global autonomous brain as the active runtime model.
- The assumption that every node needs a default full local skill stack, AI review, human review, response file, or verdict file.
- The idea that Canvas, dashboard, graph files, or generated projections can prove research completion.
- Legacy standalone operator docs in the repository root in favor of current docs under `docs/`.

### Validation

Use these checks to validate the framework:

```bash
python test/run_all_acceptance.py
python test/run_live_repo_smoke.py
python scripts/validate_local_skills.py
python scripts/validate_skill_fit.py
```

Use this command as the only live submission-readiness gate:

```bash
python scripts/validate_research_truth.py --require-submission
```

Framework checks passing means the system is coherent. It does not mean the paper is complete.

### Known Gaps

- The live paper should still fail submission readiness until real experiment results, manuscript content, review closure, TeX output, and resubmission bundle evidence exist.
- `auto_experiment_worker` requires a selected node plus an explicit executable contract; missing or `review_only` contracts remain blockers.
- Cockpit, Canvas, and dashboard projections remain convenience surfaces and must be regenerated from repo truth.
- Future cleanup should continue removing unused legacy scripts or docs only after confirming there is a safe replacement path.
