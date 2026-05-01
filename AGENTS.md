# Repository Guidelines

## Project Structure & Module Organization

`research/` is the canonical research workspace. Each schedulable node has `README.md` for entry context, `status.yaml` for state, and optional node-local `skills/`, `docs/`, `artifacts/`, and `logs/`.

`backend/relations/edge_registry.json` is the canonical explicit relation source. `backend/graph/graph.json` and `backend/graph/graph_status.json` are derived scheduler outputs and should be regenerated, not hand-edited. Global reusable skills live under `.agent/skills/<skill>/SKILL.md`.

Project-local Claude/Codex skill wrappers, when generated, are derived files under `.claude/skills/` and `.codex/skills/`. They only expose `.agent/skills/*/SKILL.md`; they are not a second skill truth.

The repo has two front-end surfaces. `obsidian/` is the Obsidian Canvas IDE and proposal workbench. `web/` contains browser surfaces: `web/app/` is the primary graph-aware agent cockpit served by `backend/agent_gateway/app.py`, and `web/dashboard/` is the secondary static read-only graph monitor. Both front ends are projection and operation surfaces, not sources of truth for graph edges, node status, execution logic, manuscript text, or research artifacts.

## Development Command Boundary

Developer maintenance commands live in `docs/dev.md`. Do not present low-level refresh, projection, validation, or acceptance commands as the normal agent loop.

When performing development maintenance, use the narrow command in `docs/dev.md` that matches the changed subsystem.

## Coding Style & Naming Conventions

Keep Python scripts small, deterministic, and standard-library first unless a dependency already exists in the repo. Use explicit JSON/YAML field names and avoid adding graph fields such as owner, priority, tags, progress, or long summaries.

Use path-backed IDs consistently: `research/P0_x/P0_01_y` becomes `research::P0_x::P0_01_y` only inside derived graph files.

## Testing Guidelines

For graph changes, verify that `graph.json` contains only `nodes` and `edges`, node payloads contain only `path` and `status`, and edge payloads contain only `src`, `rel`, and `dst`.

For scheduler changes, inspect `backend/graph/graph_status.json` and confirm `ready_nodes`, `blocked_nodes`, `next_node`, and `unfinished_count` match the intended frontier.

## Commit & Pull Request Guidelines

Keep commits scoped by subsystem, for example `graph: narrow ready frontier` or `canvas: add layout hints`. PR descriptions should include changed truth sources, regenerated artifacts, and the exact validation commands run.

## Agent-Specific Instructions

Follow Occam's razor and first principles. Do not turn Canvas, web front ends, graph, or `autoresearch` into a second source of truth or global pipeline brain.

For new or resumed research material, first identify the explicit `entry_phase` or `target_node`. Use `.agent/skills/research_material_intake/SKILL.md` to record the material into the right node-local intake artifacts. Do not default every first-use prompt to P0, and do not expose scheduler details unless the user asks for developer-mode operation.

Default context is bounded by `docs/architecture/context_hygiene.md` and `backend/registry/runtime_policy/context_hygiene.yaml`. Do not read `_reference/**`, `research/**/docs/HUMAN_ONLY.md`, `.env*`, credentials, tokens, private keys, generated Canvas files, reports, or vendor assets unless the user explicitly names a specific file for the current run. Verifying that such paths are ignored or quarantined is allowed without reading their contents.
