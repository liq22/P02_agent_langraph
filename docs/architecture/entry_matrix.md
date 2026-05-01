# Entry Matrix

Use one starting skill per run:

- I do not know the next node -> `graph_driven_research_orchestrator`.
- I know the rough task but the scope is still wide -> `auto_research_campaign`.
- I explicitly want hands-off repeated progression until a human decision, evidence, citation, review, or budget stop -> `autonomous_research_lane`.
- I already selected an experiment node and its execution contract is `executable` -> `auto_experiment_worker`.

`backend/registry/skill_registry/skill_catalog.yaml` classifies global skills as entry, workflow mode, worker, helper, or profile. It is role metadata for validation and operator orientation. Actual skill behavior stays in `.agent/skills/*/SKILL.md`, and selected-node routing stays in `skills/local_entry.md`.

Historical `autoresearch` is only a legacy concept label in older notes. It is not an active skill in this repo.

## Node Types

Node-local optimization follows four node types instead of treating every node-local file as an independent execution unit:

- `parent_coordination_family`: parent nodes that only coordinate child routing and status.
- `lite_research_leaf_family`: thin research leaves that use `local_entry.md + prompts/*` and delegate directly.
- `standard_research_leaf_family`: leaves that need a node-local strategy layer via `skills/SKILL.md`.
- `execution_leaf_family`: execution leaves that require `skills/SOP.md` plus a local binder path.

These labels are derived from `node_mode`. They are valid optimization and generated-view labels, but they do not override `local_entry.md`.
