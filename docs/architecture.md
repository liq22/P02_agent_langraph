# Architecture

This document holds the longer architecture explanation. The root `README.md` is the startup protocol.

## Current Architecture

The repository is built around six surfaces:

- folder-backed research nodes under `research/`
- a minimal JSON scheduler graph under `backend/graph/`
- canonical explicit relations under `backend/relations/`
- global reusable skills under `.agent/skills/`
- reusable scaffolds under `templates/`
- front-end surfaces under `web/app/`, `web/dashboard/`, and the top-level `obsidian/` IDE projection surface

The repository is a structured research workspace for humans and agents. It is not a document dump and not a monolithic autonomous pipeline.

## Directory Contract

The top-level directory layout is intentionally small. Keep these directories at the root because scripts, tests, or agent startup rules depend on their paths:

- `research/`: source workspace for node README, status, prompts, and local skills.
- `backend/`: minimal scheduler substrate, explicit relations, registries, and local gateway.
- `.agent/`: global reusable skills.
- `obsidian/`: active Obsidian IDE projection surface; not source truth, but path-stable.
- `web/`: browser UI surfaces for the cockpit and static monitor.

Supporting directories should not be promoted into runtime truth:

- `templates/`: reusable scaffolds and examples.
- `docs/`: architecture and workflow documentation, including future desktop wrapper notes.
- `_reference/`: reference material and historical imports only.

Do not move `obsidian/`, `web/app/`, or `web/dashboard/` without changing the scripts, tests, docs, and launch instructions that reference those exact paths.

## Research Layer

`research/` stores the actual research work.

Each node is a folder-backed unit with a light contract:

- `README.md` is the node entry point.
- `status.yaml` is the execution state.
- `skills/` holds node-local routing and bounded execution contracts.
- substantive body content belongs under node-local docs rather than graph files.

README files are entry surfaces, not body stores. `docs/HUMAN_ONLY.md` is not read by agents unless explicitly requested.

## Local Stack Semantics

The local stack stays smooth only if two concerns remain separate:

- `node_mode`: local stack depth and required file surface
- `node_profile`: execution-tier semantic role when one node needs specialized binder wording

Each local file then has a narrow job:

- `prompts/research_prompt.md`: node-local research semantics
- `prompts/acceptance_checklist.yaml`: done-state truth
- `skills/SKILL.md`: strategy delta only
- `skills/SOP.md`: ordered procedure only

This is why `lite` and `parent` nodes intentionally omit `SKILL.md` and `SOP.md`: the repo wants one prompt-led semantic layer for light nodes, not four competing semantic layers.

The current repo uses `node_profile` only where semantic drift is otherwise expensive:

- `experiment_execution`: contract-gated bounded experiment execution
- `result_synthesis`: results-ledger-driven evidence synthesis

This keeps `node_mode` structural instead of turning it into a second routing brain.

## Backend Layer

`backend/` stores the minimal global substrate:

- `backend/relations/edge_registry.json` is the canonical explicit cross-node relation source.
- `backend/graph/graph.json` is the derived minimal scheduler graph.
- `backend/graph/graph_status.json` is the derived scheduler summary.
- `backend/graph/hierarchy.json`, `node_details.json`, `scope_rollup.json`, and `board_state.json` are cockpit/dashboard projections, not minimal runtime requirements.
- `.agent/skills/*/SKILL.md` and node-local `skills/local_entry.md` are runtime skill truth.
- `backend/registry/skill_registry/` is a validation and generation catalog, not a second runtime contract.
- `backend/views/*` and `backend/indexes/*`, when present, are inactive or rebuildable projection surfaces rather than canonical truth.

The graph is a scheduler, not a content database. It should only store the minimum facts required for refresh, judgment, and routing.

## Template Layer

`templates/` stores reusable scaffolds and examples only:

- `templates/execution_contract.template.yaml` for execution contract fixtures and setup flows.
- `templates/nodes/` for parent and leaf node file scaffolds.
- `templates/shared/` for reusable minimal review and sync templates.

Templates are not runtime state and are not scheduler truth.

## Front-End Projections

`web/app/` is the primary graph-aware cockpit served by `backend/agent_gateway/app.py`.

`web/dashboard/` remains a secondary static read-only monitor over:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`

Obsidian Canvas is a local IDE for planning, visualization, proposal drafting, and navigation into real repo files. The top-level `obsidian/` directory is intentionally retained because scripts and tests write to `obsidian/canvases/` and `obsidian/inbox/`. Canvas is not the source of truth.

Desktop wrapper notes live under `docs/desktop/tauri/`; there is no active top-level desktop runtime yet.

## Minimal Hypergraph Principle

The graph should keep only the minimum runnable facts:

- node existence
- node path
- node status
- explicit cross-node edges

The practical relation set is intentionally small:

- `depends_on`
- `addresses`

`graph.json` stores only node `path`/`status` and edge `src`/`rel`/`dst`. `graph_status.json` stores only low-token scheduling facts such as `current_phase`, `ready_nodes`, `blocked_nodes`, `next_node`, and `unfinished_count`.

## Graph-Driven Orchestration

The repository uses a graph-aware orchestrator pattern:

1. refresh the graph
2. read `graph_status.json` and `graph.json`
3. determine `next_node`
4. enter the target node directory
5. resolve a local skill first
6. delegate to one bounded worker path
7. update node-local state
8. refresh the minimal scheduler graph
9. report the scheduling delta

The global orchestrator is a router, not a full-pipeline brain. Full projection refresh is for cockpit, Canvas, dashboard, or human review sessions, not the default agent loop. Detailed research actions belong inside node-local skills, canonical workers, or bounded phase fallback workers.

## Entry Matrix

The active entry surfaces are intentionally small:

- `graph_driven_research_orchestrator`: choose the next node from `graph_status.json` and route one scheduler round.
- `auto_research_campaign`: take a broad user prompt and resolve it into exactly one bounded node-local or canonical step.
- `auto_experiment_worker`: run one bounded experiment round only after one node is already selected and the execution contract is `executable`.

Historical `autoresearch` is only a legacy label in old notes. The current repo does not keep an active `.agent/skills/autoresearch/SKILL.md` runtime object.

## Auto Experiment Worker Boundary

The repository supports `auto_experiment_worker`-style experimentation only in the worker layer.

- The global orchestrator must not inherit `NEVER STOP` behavior.
- `.agent/skills/auto_experiment_worker/SKILL.md` is the canonical bounded experiment worker.
- `auto_experiment_worker` must be invoked only after a local entry or wrapper skill has selected one experiment node and supplied an execution contract whose `contract_mode` is `executable`.
- A bounded campaign may run several internal experiment iterations, but it must stop on budget, blocker, status change, crash budget, missing metric, or explicit stop conditions.

## Refresh Modes

Refresh commands are developer maintenance details and live in `docs/dev.md`.

- `--mode graph_only`: refresh only graph truth and scheduler status for bounded agent rounds.
- `--mode full`: refresh graph plus hierarchy, node details, scope rollup, board state, and Canvas projections for cockpit, dashboard, Canvas, or human review sessions.

The default mode stays `full` for backward compatibility. Use the graph-only mode when the caller needs a light scheduler refresh rather than the whole projection stack.

## Design Rules

- Keep graph minimal; do not add progress, owner, priority, tags, review counts, or long summaries to graph files.
- Keep Canvas file-first; link to README/status/skill files rather than copying manuscript or review text.
- Keep global orchestration bounded; detailed research actions belong in local or phase worker skills.
- Follow Occam's razor and first principles when adding structure.
