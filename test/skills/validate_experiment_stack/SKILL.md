---
name: validate_experiment_stack
description: Validate the current experiment stack across backend graph refresh, Obsidian Canvas front-end projection, graph-driven orchestration, and bounded canonical auto_experiment_worker behavior. Prefer the runnable acceptance scripts in test/ before doing ad hoc inspection.
---

# Validate Experiment Stack

The stack has three layers:

- backend scheduler substrate
- Obsidian Canvas front-end IDE
- graph-driven orchestration plus tier-aware node-local stacks and bounded auto_experiment_worker campaigns

Do not redesign the system during validation.
Do not expand the graph schema during validation.
Do not turn the validator into a feature-building skill.

## Phase 0 - Entry

Prefer these commands when they exist:

```bash
python test/run_fixture_acceptance.py
python test/run_live_repo_smoke.py
```

If both scripts are present, use their outputs as the primary acceptance evidence.

Only fall back to manual inspection when a script is missing or broken.

## Phase 1 - Validate Backend

Check:

1. whether `python scripts/refresh_hypergraph.py` can run
2. whether it produces `backend/graph/graph.json`
3. whether it produces `backend/graph/graph_status.json`
4. whether graph payload remains minimal
5. whether scheduler frontier fields are leaf-only (`ready_nodes`, `blocked_nodes`, `next_node`, `unfinished_count`)
6. whether parent `depends_on` edges fail safely in a disposable fixture or temporary copy
7. whether bad edges or cycles fail safely in a disposable fixture or temporary copy

Record findings under:

- pass
- fail
- partial

## Phase 2 - Validate Canvas Front-End

Check:

1. whether `python scripts/build_canvas_from_graph.py --dry-run` can validate Canvas projection inputs
2. whether generated Canvas views are projection-oriented rather than truth-oriented
3. whether node cards can navigate into `README.md` and `status.yaml`
4. whether generated overview/focus views are separated from the manual framework workbench
5. whether proposals flow through `obsidian/inbox/canvas_proposals.md`

If the Canvas bridge is missing, report this as a concrete gap rather than redesigning the whole system.

## Phase 3 - Validate Orchestrator Routing

Check:

1. whether the orchestrator reads graph first
2. whether it selects `next_node`
3. whether it enters the node directory before reading deeper content
4. whether it resolves local `skills/local_entry.md` -> prompt assets -> mode-required `skills/SKILL.md` / `skills/SOP.md` before deeper fallback
5. whether it recognizes local `skills/local_wrapper.md`, `skills/local_execution.md`, or `artifacts/execution_contract.yaml` as campaign eligibility signals when the node mode allows them
6. whether it uses `python scripts/refresh_views.py --mode graph_only` for light refresh and `python scripts/refresh_views.py --mode full` for full projection refresh after execution
7. whether missing wrapper inputs are reported as blocking gaps instead of being guessed
8. whether `contract_mode: review_only` is treated as non-runnable

## Phase 4 - Validate Experiment Capability

Check:

1. whether experiment-heavy nodes can be marked campaign-eligible
2. whether experiment-heavy nodes expose an execution-tier local stack with `SKILL.md`, `SOP.md`, and a binder (`local_wrapper.md` or `local_execution.md`)
3. whether there is a bounded canonical `auto_experiment_worker`
4. whether the worker requires a local execution contract before running
5. whether the worker follows baseline -> experiment -> keep/discard -> state update
6. whether the worker has stop conditions
7. whether `NEVER STOP` is absent from the global orchestrator
8. whether experiment-heavy nodes without `artifacts/execution_contract.yaml` are reported as partial/blocking rather than run
9. whether experiment-heavy nodes with `contract_mode: review_only` are blocked from direct worker execution

## Phase 5 - Report

Return exactly these sections:

### A. Backend status

- pass / fail / partial
- minimal graph verdict
- refresh safety verdict

### B. Front-end status

- pass / fail / partial
- Canvas projection verdict
- file-first navigation verdict
- manual proposal zone verdict

### C. Experiment stack status

- pass / fail / partial
- routing verdict
- bounded campaign verdict
- state refresh verdict

### D. Blocking gaps

List only the smallest missing pieces required to make the stack usable.

### E. Next fixes

Recommend the next 1-3 concrete fixes only.
