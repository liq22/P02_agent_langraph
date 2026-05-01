# 01_backend_graph_acceptance

## Objective

Validate the minimal back-end scheduler substrate implemented by the current repository.

## Preconditions

- `research/` exists and contains at least one valid node
- `backend/relations/edge_registry.json` exists
- `scripts/refresh_hypergraph.py` exists

## Checks

### BE-01 Refresh success

Run:

```bash
python scripts/refresh_hypergraph.py
```

Pass if:

- `backend/graph/graph.json` exists
- `backend/graph/graph_status.json` exists

### BE-02 Minimal graph payload

Pass if `backend/graph/graph.json` contains only:

- `nodes`
- `edges`

Pass if each node stores only:

- `path`
- `status`

Pass if each edge stores only:

- `src`
- `rel`
- `dst`

### BE-03 Scheduler summary

Pass if `backend/graph/graph_status.json` contains:

- `refresh_ok`
- `current_phase`
- `ready_nodes`
- `blocked_nodes`
- `next_node`
- `unfinished_count`

### BE-04 Safe failure behavior

Inject one bad dependency or a `depends_on` cycle in a disposable fixture or temporary copy.

Pass if refresh:

- fails explicitly
- preserves the previous good graph files
- does not leave partial writes

### BE-05 Routing sanity

Pass if `next_node` is stable across repeated refresh calls when no canonical source files changed.
