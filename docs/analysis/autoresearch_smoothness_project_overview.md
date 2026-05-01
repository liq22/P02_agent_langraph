# Autoresearch Smoothness Project Overview

## Goal

Make the existing autoresearch cockpit usable without requiring the human to infer setup state, hand-copy node ids, or manually stitch together create/run session steps.

## Current Shape

- Repo truth remains in `research/**`, `backend/relations/edge_registry.json`, and `.agent/skills/**/SKILL.md`.
- Derived graph projections live under `backend/graph/`.
- `backend/agent_gateway/app.py` serves the web app and local bounded agent gateway.
- `web/app` is the primary cockpit surface; `web/dashboard` remains a read-only graph monitor.

## Friction Points

- Missing graph projections previously surfaced as generic refresh failure.
- Example gateway config did not clearly block execution in the UI.
- Running an agent required manual target id and session lifecycle management.
- Session history existed on disk but the gateway started with an empty in-memory list.
- Node details projected docs, but not local skill and prompt files into the inspector.

## Constraints

- Keep `graph.json` and `graph_status.json` minimal.
- Keep autoresearch bounded to a selected node and explicit prompt/contract.
- Do not add a database, daemon, build system, or new frontend dependency.
