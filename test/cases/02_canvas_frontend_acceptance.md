# 02_canvas_frontend_acceptance

## Objective

Validate Obsidian Canvas as the front-end IDE rather than a truth source.

## Preconditions

- `backend/graph/graph.json` exists
- `backend/graph/graph_status.json` exists
- `scripts/build_canvas_from_graph.py` exists
- `obsidian/canvases/` exists or can be created by the bridge script

## Checks

### FE-01 Projection build

Run:

```bash
python scripts/build_canvas_from_graph.py --dry-run
```

Pass if the script validates graph inputs and reports the target Canvas views without writing files.

For a full projection rebuild, run:

```bash
python scripts/build_canvas_from_graph.py
```

Pass if it creates or updates:

- `obsidian/canvases/research_overview.canvas`
- `obsidian/canvases/current_focus.canvas`

Pass if it creates `obsidian/canvases/framework_workbench.canvas` only when missing, and otherwise preserves it.

### FE-02 Phase readability

Pass if the Canvas makes these visible without opening bodies:

- current phase
- next node
- ready nodes or ready count
- blocked nodes or blocked count

### FE-03 File-first navigation

Pass if node cards link to real repo files, preferably:

- `README.md`
- `status.yaml`
- local skill file when present

### FE-04 Generated vs manual separation

Pass if rebuilding the Canvas:

- updates generated scheduler views
- preserves the manual framework workbench
- keeps method notes, relation ideas, and proposal cards out of graph truth until promoted

### FE-05 Non-authoritative Canvas

Pass if changing Canvas layout or free-text notes does not silently mutate:

- `status.yaml`
- `edge_registry.json`
- local skill files

### FE-06 Proposal workflow

Pass if new method, relation, skill, or framework ideas can be captured in a manual proposal area and then promoted deliberately through `obsidian/inbox/canvas_proposals.md`.
