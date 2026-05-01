# 03_experiment_stack_acceptance

## Objective

Validate that the current stack supports tier-aware node-local stacks plus bounded `auto_experiment_worker` behavior correctly.

## Preconditions

- `.agent/skills/graph_driven_research_orchestrator/SKILL.md` exists
- `.agent/skills/auto_research_campaign/SKILL.md` exists
- `.agent/skills/auto_experiment_worker/SKILL.md` exists
- at least one experiment-heavy node exists or is planned
- the experiment node has, or can provide, an execution contract before invoking `auto_experiment_worker`
- the execution contract distinguishes `review_only` from `executable`

## Checks

### AR-01 Low-token orchestrator entry

Pass if the orchestrator first reads only:

- `backend/graph/graph_status.json`
- `backend/graph/graph.json`

### AR-02 Node-first routing

Pass if the orchestrator:

- selects `next_node`
- enters that node directory
- reads only `README.md`, `status.yaml`, and then the node-local prompt assets / stack required by that node's `node_mode`
- uses `node_profile` only after `node_mode` has selected the local stack depth
- treats node archetype family as a derived optimization / projection label from `node_mode`, not as a second runtime read policy

### AR-03 Local skill priority

Pass if skill resolution order is:

1. local `skills/local_entry.md`
2. local `prompts/research_prompt.md` and `prompts/acceptance_checklist.yaml`
3. local `skills/SKILL.md` only when `node_mode` is `standard` or `execution`
4. local `skills/SOP.md` only when `node_mode` is `execution`
5. local `skills/local_wrapper.md` or `skills/local_execution.md` when explicitly delegated by local entry and allowed by the node mode
6. the canonical worker selected by the wrapper or execution contract
7. phase fallback skill only when the local path does not already bind a deeper worker

Also pass if:

- `required_local_reads` are included in the default bounded read order
- `optional_local_reads` remain out of the default read order and are loaded only when they materially change the round

### AR-04 Campaign eligibility

Pass if the orchestrator can distinguish:

- standard node -> one bounded worker step
- experiment-heavy node with an `executable` execution contract -> bounded `auto_experiment_worker` campaign
- experiment-heavy node with a `review_only` execution contract -> route to contract preparation instead of running
- experiment-heavy node without a valid execution contract -> route to contract preparation instead of running
- result-synthesis node -> route to one bounded local execution round that consumes the declared results ledger rather than an execution contract

Suggested lightweight eligibility signals:

- `node_mode`
- local `prompts/research_prompt.md`
- local `prompts/acceptance_checklist.yaml`
- local `skills/SKILL.md`
- local `skills/SOP.md`
- local `skills/local_wrapper.md`
- local `skills/local_execution.md`
- local `artifacts/execution_contract.yaml`
- `contract_mode`
- an explicit local entry delegation to local wrapper plus canonical `auto_experiment_worker`
- an explicit local entry delegation to local execution plus `node_profile: result_synthesis` when the node is a synthesis leaf

### AR-05 Bounded campaign behavior

Pass if the `auto_experiment_worker`:

- starts from a baseline
- records result deltas
- keeps improvements and discards regressions
- stops on budget, blocker, status transition, crash budget, missing metric, or explicit stop condition
- does not export `NEVER STOP` behavior to the global orchestrator

And pass if the `result_synthesis` execution path:

- treats `artifacts/auto_experiment/results.tsv` as the required ledger input
- updates only the declared synthesis outputs and status fields
- does not consult `artifacts/execution_contract.yaml`

### AR-06 State update and refresh

Pass if after the worker runs:

- node-local state is updated
- `python scripts/refresh_views.py --mode full` is the default integrated refresh entry when projections must be rebuilt
- `python scripts/refresh_views.py --mode graph_only` is the default light fast path after a bounded step when only scheduler truth changed
- low-level `refresh_hypergraph.py` and `build_canvas_from_graph.py` remain valid underlying steps
- the system reports delta in `next_node`, `current_phase`, or node status when changed

### AR-07 Crash discipline

Pass if a failed experiment:

- is logged as failure or crash
- does not corrupt graph state
- does not trap the global orchestrator in an infinite loop
