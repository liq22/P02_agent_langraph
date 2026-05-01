# Refresh Modes

Refresh modes define how derived graph and projection outputs are rebuilt. Minimal runtime only requires `graph.json` and `graph_status.json`; the other graph files are projection surfaces.

Concrete commands live in `docs/dev.md` so user and agent docs do not turn maintenance commands into the operating loop.

## graph_only

Use `graph_only` after a high-frequency bounded agent step when only scheduler truth must be current.

This mode refreshes:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`

## full

Use `full` for cockpit, Canvas, dashboard, or human review sessions.

This mode refreshes:

- graph truth and graph status
- hierarchy projection
- node details, including `node_mode`, `node_profile`, and required vs optional local-read buckets
- scope rollup, including smoothness diagnostics such as missing node-skill / SOP / execution-binder counts
- board state
- Canvas projections

The CLI default remains `full` for backward compatibility. Agent-facing workflows should use the light refresh path unless they need cockpit, Canvas, dashboard, or human review projections.
