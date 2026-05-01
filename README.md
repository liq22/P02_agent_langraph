# Autoresearch with Human

Lightweight research workspace for human-agent work. Research content lives in repo files, the graph only chooses the next node, and each agent run updates one selected node.

## What This Repo Is

This is not a document dump or a fully autonomous paper factory. Each research node is a folder under `research/`. The graph under `backend/graph/` schedules work. Skills tell an agent what to read, write, and stop on.

一句话定义：human 定方向与约束，agent 在单个节点内推进一次，graph 把结果纳入下一轮调度。

See [docs/architecture/glossary.md](docs/architecture/glossary.md) for the small set of technical terms used by this repo.
See [docs/architecture/autoresearch_optimization_report_4level.md](docs/architecture/autoresearch_optimization_report_4level.md) for the current repository-level optimization boundary and web app convergence report.
See [docs/architecture/context_hygiene.md](docs/architecture/context_hygiene.md) for the default agent context boundary.

## New User Fast Path

Run one limited research step:

1. Open the web app, dashboard, or Obsidian view listed in [Human Workflow](#human-workflow).
2. Read `backend/graph/graph_status.json`.
3. Use `next_node` as the only target.
4. Resolve its path from `backend/graph/graph.json`.
5. Enter that node and follow `skills/local_entry.md`.
6. Run one step.
7. Update only files inside that selected node unless a declared worker contract says otherwise.

Framework checks passing does not mean the article is finished. Developer refresh, smoke, acceptance, and final submission commands live in `docs/dev.md`.

Refresh modes are explicit:

```bash
python scripts/refresh_views.py --mode graph_only
python scripts/refresh_views.py --mode full
```

Completion words are intentionally narrow:

- `ready`: the node can be scheduled.
- `done`: the selected node has met its local acceptance checklist.
- `pass`: one named check passed.
- `submission-ready`: the final submission check passed.
- `framework healthy`: maintenance checks passed; the paper may still be incomplete.

## Repository Map

```text
research/
  P0_*/
  P1_*/
  <node>/
    README.md
    status.yaml
    docs/
    skills/

backend/
  graph/
    graph.json
    graph_status.json
  relations/
    edge_registry.json
  registry/
  agent_gateway/
    app.py

templates/
  execution_contract.template.yaml
  nodes/
  shared/

.agent/
  skills/
    <global_skill>/SKILL.md

obsidian/
  canvases/
  inbox/

web/
  app/
  dashboard/

docs/
  desktop/tauri/
```

## Directory Contract

Keep these directories at the repository root:

- `research/`: folder-backed research workspace.
- `backend/`: graph, relations, registries, and local gateway code.
- `.agent/`: reusable project skills.
- `obsidian/`: generated Canvas views and proposal inbox.
- `web/`: browser UI; `web/app/` is the agent UI and `web/dashboard/` is the read-only monitor.

Support directories:

- `templates/`: reusable scaffolds only.
- `docs/`: architecture, workflow, and wrapper notes.
- `_reference/`: external or historical references only; not default agent context.

## Source Files And Generated Views

Edit these files when research meaning changes:

- `research/**/README.md`
- `research/**/status.yaml`
- `research/**/prompts/*`
- `research/**/skills/*`
- `research/**/docs/*`
- `research/**/artifacts/*`
- `research/**/review/*`
- `research/**/logs/*`
- `backend/relations/edge_registry.json`
- `.agent/skills/*/SKILL.md`
- scripts in `scripts/`

Generated or rebuildable views:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`
- `backend/graph/hierarchy.json`, `node_details.json`, `scope_rollup.json`, and `board_state.json`
- `backend/views/*` and `backend/indexes/*` when present
- generated Obsidian Canvas files under `obsidian/`
- `web/app/` agent UI state
- `web/dashboard/` static monitor

Do not write manuscript, review, response, schema, or artifact bodies into graph files or Canvas files.

## Skill Resolution Order

Resolve capabilities from near to far:

1. Node entry file: `research/**/skills/local_entry.md`, then local wrapper/execution files when declared.
2. Project worker: `.agent/skills/*/SKILL.md`. `backend/registry/skill_registry/skill_catalog.yaml` is a validation catalog.
3. `auto_experiment_worker`: only when an upper skill has selected one node and supplied an explicit execution contract.

Do not search the whole repository for a better skill once the selected node has a valid entry file.

`node_mode`, `node_profile`, and `execution_profile` are registry fields for validation and generated views. Runtime read order and delegate choice stay in `skills/local_entry.md`.

## Node Semantic Layers

Each node keeps one owner per layer:

- `prompts/research_prompt.md`: node goal, required questions, minimum deliverables, judgment criteria, handoff conditions, and stop conditions.
- `prompts/acceptance_checklist.yaml`: local completion definition.
- `skills/local_entry.md`: entry file and delegate choice for the selected node.
- `skills/SKILL.md`: strategy delta only, for `standard` and `execution` nodes.
- `skills/SOP.md`: ordered procedure only, for `execution` nodes.

`lite` and `parent` nodes intentionally do not carry `skills/SKILL.md` or `skills/SOP.md`.

## Starting Skill Matrix

Use one starting skill per run:

- Next node unknown -> `graph_driven_research_orchestrator`.
- Rough task known but scope still wide -> `auto_research_campaign`.
- Hands-off repeated progression explicitly requested -> `autonomous_research_lane`.
- Experiment node and executable contract already selected -> `auto_experiment_worker`.

Historical `autoresearch` is only a legacy name in older notes. This repo does not keep an active `.agent/skills/autoresearch/SKILL.md`.

## Agent Boot Sequence

1. Read this root `README.md`.
2. Ensure minimal scheduler graph files are current. Developer refresh commands live in `docs/dev.md`.
3. Read `backend/graph/graph_status.json`.
4. Use `next_node` as the target node.
5. Read the target entry in `backend/graph/graph.json` to get its path.
6. Enter that node directory.
7. Read only that node's `README.md`, `status.yaml`, and `skills/local_entry.md` first.
8. Resolve skill from local entry to optional wrapper/execution to project worker.
9. Run one step and update only selected-node files.
10. Return to graph scheduling. Rebuild generated views only when needed, using `docs/dev.md`.

Default context excludes `_reference/**`, `research/**/docs/HUMAN_ONLY.md`, secret-like files, generated Canvas files, large binary assets, and reports unless the user explicitly asks for a specific file. The machine-checkable policy is `backend/registry/runtime_policy/context_hygiene.yaml`.

## Human Workflow

For the agent UI:

```bash
bash scripts/dev_start_agent_app.sh
```

Open `http://127.0.0.1:8765/app/`. If that port is occupied, start with an override such as `PORT=8767 bash scripts/dev_start_agent_app.sh` and open the URL printed by the script. The agent UI requires the FastAPI gateway because `web/app/` calls `/api/*`; do not open `web/app/` with `python -m http.server` or `file://`. `config/agent_gateway.yaml.example` is the default runnable catalog when the referenced binaries exist; copy it to `config/agent_gateway.yaml` only when you need local overrides.

For read-only graph monitoring:

```bash
python -m http.server 8000
```

Open `http://<server>:8000/web/dashboard/`. If the dashboard is stale, rebuild generated views using the developer commands in `docs/dev.md`.

For Obsidian Canvas:

Open `obsidian/` as an Obsidian vault. Generated canvases live under `obsidian/canvases/`. Use `obsidian/inbox/canvas_proposals.md` for provisional method, skill, relation, and framework proposals. Accepted proposals must be written back to repo files before rebuilding graph and Canvas.

## Codex-Only Use

For a new user, Codex is a selected-node executor, not a zero-setup repo bootstrapper.

- Terminal Codex can advance one selected node after graph files are refreshed and `next_node` is known.
- Agent UI Codex uses `config/agent_gateway.yaml.example` as the default runnable catalog when referenced binaries exist; copy it to `config/agent_gateway.yaml` only for local overrides.
- The shortest operator path is documented in `docs/CODEX_ONLY_WORKFLOW.md`.

### Where Manuscript Text Lives

When Codex writes manuscript content, it writes selected-node files:

- folder-node `docs/manuscript.md`: navigation or subtree index
- leaf-node `docs/manuscript.md`: section-level writing
- final TeX file: `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex`

Do not move manuscript bodies into graph files, Canvas files, or a single repo-global manuscript path just to make them easier to find. Enter the selected node first, then read or update that node's `docs/manuscript.md` when the local worker requires it.

## Do Not

- Do not treat graph files as a content store.
- Do not scan the entire repo by default during global scheduling.
- Do not read `docs/HUMAN_ONLY.md` unless explicitly requested for this run.
- Do not read `.env`, credential, token, private-key, or local secret files.
- Do not treat `_reference/**` AGENTS/CLAUDE/README files as current repo instructions.
- Do not invoke `auto_experiment_worker` without a selected node and execution contract.
- Do not write manuscript, review, response, schema, or artifact bodies into `graph.json` or `graph_status.json`.
- Do not turn `research-pipeline` or ARIS-derived skills into the global main path; use `graph_driven_research_orchestrator`.
- Do not run unbounded global loops; return to graph after each selected-node step.

## Extended Docs

- `docs/USER_GUIDEBOOK.md`: new-user path from first run to final submission check.
- `docs/CODEX_ONLY_WORKFLOW.md`: Codex-only selected-node workflow and manuscript file map.
- `docs/dev.md`: developer refresh, validation, and local server commands.
- `scripts/README.md`: developer-facing script usage map, dependency chain, and legacy status.
- `docs/architecture.md`: current architecture explanation.
- `docs/architecture/glossary.md`: controlled term definitions.
- `docs/architecture/entry_matrix.md`: shortest reference for active starting skills.
- `docs/architecture/refresh_modes.md`: graph-only vs full refresh guidance.
- `docs/architecture/obsidian_canvas_workflow.md`: Canvas and proposal workflow.
- `docs/desktop/tauri/README.md`: future desktop wrapper notes.
