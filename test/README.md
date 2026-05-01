# test/

This directory is the acceptance gate for the current experiment stack.

It is not the node-level adversarial red-team layer. Deterministic single-node hostile validation now lives under `_reference/test/redteam/`.

It tests three layers that now exist in the repository:

1. back-end scheduler substrate
2. Obsidian Canvas front-end projection
3. graph-driven orchestration plus tier-aware node-local stacks and bounded `auto_experiment_worker`

The current repository already contains a valid architecture direction, a minimal graph refresh script, a Canvas bridge script, and a thin orchestrator / bounded worker split. The remaining gap is that testing is still mostly specification-heavy. This package adds a runnable minimal fixture and lightweight smoke runners so the current stack can be checked without rebuilding the architecture.

## Included files

```text
test/
├── README.md
├── TESTING_QUICKSTART.md
├── run_fixture_acceptance.py
├── run_live_repo_smoke.py
├── run_all_acceptance.py
├── cases/
│   ├── 01_backend_graph_acceptance.md
│   ├── 02_canvas_frontend_acceptance.md
│   └── 03_experiment_stack_acceptance.md
├── skills/
│   └── validate_experiment_stack/
│       └── SKILL.md
└── fixtures/
    └── min_experiment_stack_repo/
```

## What the runners do

### `run_fixture_acceptance.py`

Uses a deterministic three-node fixture and the repository's real scripts:

- `scripts/refresh_hypergraph.py`
- `scripts/refresh_views.py --mode graph_only`
- `scripts/refresh_views.py --mode full`
- `scripts/build_canvas_from_graph.py`

It validates:

- minimal graph generation
- scheduler summary correctness
- cycle-safe refresh failure
- Canvas dry-run and full projection generation
- file-first Canvas output
- node-mode-aware local entry / prompt assets / SKILL / SOP / wrapper / execution contract handoff signals
- `node_profile`-aware execution semantics, including required vs optional local-read buckets

### `run_live_repo_smoke.py`

Runs a non-destructive smoke check against the live repository state:

- refreshes graph in `graph_only` and `full` modes
- dry-runs Canvas projection
- checks that `next_node` resolves to a real node path
- checks that the orchestrator and bounded worker skills exist
- checks that node-local stacks follow the declared `node_mode` contract
- checks that execution-tier nodes also follow the declared `node_profile` contract
- checks that experiment-heavy nodes expose the expected execution-tier local-entry / local-wrapper pattern
- checks that result-synthesis nodes read `artifacts/auto_experiment/results.tsv` as required input and keep manuscript reads optional
- reports missing execution contract as blocking `partial`, and malformed or wrongly gated contract states as `fail`

### `run_nature_rubric_presence.py`

Runs a read-only coverage check for `test/NATURE_LEVEL_NODE_RUBRIC.md`:

- requires official Nature Portfolio source links
- requires scoring, hard-fail, and node-rubric sections
- requires every `research/**/status.yaml` node to have one rubric row
- rejects stale rubric rows for nodes that no longer exist

### `run_nature_capability_acceptance.py`

Runs a synthetic truth-gate acceptance suite:

- accepts a complete minimal Nature-ready submission fixture
- rejects missing `P1_04` experiment results
- rejects `review_only` execution contracts
- rejects missing external-reviewer independence
- rejects placeholder TeX manuscripts
- rejects missing `P4_07` submission manifests

### `scripts/validate_research_truth.py --require-submission`

Checks the live `research/` tree for actual submission readiness. This is intentionally stricter than framework acceptance and should fail until the real paper evidence chain is complete.

### `run_all_acceptance.py`

Runs the fixture, gateway, Nature rubric, Nature capability, and live repository checks and returns `0` only when every framework layer is fully `pass`.

## Philosophy

- repo files remain canonical truth
- graph JSON remains derived scheduler state
- Canvas remains a projection / IDE layer
- the global orchestrator remains thin
- each node owns prompt assets plus the minimum local stack required by its `node_mode`
- archetype families are derived from `node_mode` for projection and optimization grouping only
- `node_profile` defines execution-tier semantics without becoming graph truth or scheduler policy
- required local reads belong in the default bounded read order; optional local reads stay on-demand
- `skills/SKILL.md` is required only for `standard` and `execution` nodes
- `skills/SOP.md` is required only for `execution` nodes
- bounded experiment execution belongs to node-local handoff, not to the global router
