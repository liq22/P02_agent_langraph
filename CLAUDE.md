# CLAUDE.md

This file is an agent-orientation pointer, not an independent architecture source.

Use the current operating truth in this order:

1. `README.md`
2. `AGENTS.md`
3. `docs/architecture.md`
4. `docs/architecture/refresh_modes.md`
5. node-local `README.md`, `status.yaml`, and `skills/local_entry.md`

## Current Runtime Contract

- Repo files are truth.
- `backend/graph/graph.json` and `backend/graph/graph_status.json` are the minimal scheduler projection.
- `hierarchy.json`, `node_details.json`, `scope_rollup.json`, `board_state.json`, Canvas, dashboard, and cockpit state are rebuildable projections.
- Developer refresh and validation commands live in `docs/dev.md`; do not treat them as user-facing or agent-facing operating instructions.
- Active global entry surfaces are `graph_driven_research_orchestrator`, `auto_research_campaign`, and `auto_experiment_worker`.

Do not revive older assumptions that every node needs a default AI review, human review, response file, verdict file, or full local skill stack. Those slots are created only when a node-local contract or explicit human/reviewer gate requires them.
