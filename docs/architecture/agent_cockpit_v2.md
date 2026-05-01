# Research Agent Cockpit v2

This is the current canonical cockpit shape for the `obsidian-canvas-ide` branch.

## Unchanged Core

- `research/` remains the research work layer.
- `backend/relations/edge_registry.json` remains the explicit relation source.
- `backend/graph/graph.json` and `backend/graph/graph_status.json` remain derived scheduler outputs.
- Obsidian Canvas remains a projection workbench, not a source of graph truth.
- `.agent/skills/*/SKILL.md` remains the reusable skill truth.

## Projection Layer

The app consumes these derived files:

- `hierarchy.json` for tree navigation and overview graph layout
- `node_details.json` for node panels, context drawer, and session context
- `scope_rollup.json` for scope-level health
- `board_state.json` for active-set and flow projections

## Gateway Layer

`backend/agent_gateway/app.py` is the only browser-facing runtime gateway. It provides:

- graph and projection APIs
- agent catalog
- session creation and bounded session execution
- session log polling
- node-local manuscript read/write

It does not become a scheduler brain and does not hand-edit graph projections.

## Web App Shape

`web/app/` is the primary cockpit:

- top bar: compact scheduler summary, one primary session action, search, language, refresh, and heartbeat
- left: collapsible tree navigator
- center: `Overview`, `Node`, `Manuscript`, and `Session`
- right: default-collapsed context drawer for setup, current object, watched workset, files, skills, reads, relations, and diagnostics

There is one workspace-mode control: the center tab strip. Topbar duplicates are intentionally avoided.
Watched nodes are local human workset state only. They do not change scheduler next-node, graph status, or queue truth.

Deprecated IA terms for the primary cockpit:

- `scope rail` -> `Tree Navigator`
- `board workspace` -> `Main Workbench`
- `node inspector` as a fourth zone -> `Context Drawer`
- `agent cockpit` as a right-side zone -> `Main Workbench` plus `Context Drawer`

## Safety Rules

- Manuscript edits must be protected from silent overwrite and expose an explicit saved/dirty/saving/error state.
- Files and diagnostics are progressive disclosure, not always-on panel noise.
- Session semantic mentions must match actual implementation.
- Frontend surfaces do not create alternate graph, status, manuscript, or artifact truth.

## Runtime Consistency

- Checked-in `web/app/*` code is the implementation source of truth.
- `test/run_gateway_acceptance.py` and `test/run_browser_smoke.py` are the expected behavior checks.
- Screenshots may illustrate the branch state, but they do not override code, copy, or validated runtime behavior.

## Desktop Wrapper

Tauri remains a later wrapper path around the same web app. Wrapper notes live under `docs/desktop/tauri/` until desktop packaging becomes active.
