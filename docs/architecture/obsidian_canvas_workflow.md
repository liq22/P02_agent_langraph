# Obsidian Canvas Workflow

## Role

Obsidian Canvas is the front-end IDE for the research OS. It is used for planning, visualization, navigation, and proposal drafting. Keep the top-level `obsidian/` directory because the Canvas builder, tests, and workflow docs use that path directly.

It is not the source of truth for node status, canonical graph edges, manuscript content, review content, or execution logic.

## Source Of Truth

- `research/**/README.md`
- `research/**/status.yaml`
- `research/**/skills/*`
- `backend/relations/edge_registry.json`
- `.agent/skills/*/SKILL.md`
- scripts in `scripts/`

## Derived Scheduler Layer

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`

## Complementary Server Dashboard

`web/dashboard/` is the server-side monitoring console. It reads only:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`

Typical server run:

```bash
python -m http.server 8000
```

Then open `http://<server>:8000/web/dashboard/`.
Use `docs/dev.md` when projections need to be rebuilt or a low-level refresh layer needs debugging.

## Canvas Files

- `obsidian/canvases/research_overview.canvas`
- `obsidian/canvases/current_focus.canvas`
- `obsidian/canvases/framework_workbench.canvas`
- `obsidian/canvases/layout_hints.json`

`research_overview.canvas` and `current_focus.canvas` are generated from the graph and can be ignored by Git. `layout_hints.json` is the tracked layout stability layer for those generated views. `framework_workbench.canvas` is initialized once and then preserved for manual planning.

## Proposal Inbox

- `obsidian/inbox/canvas_proposals.md`

Canvas sketches become actionable only after they are written into the inbox and validated by a local agent or human.

## Worker Boundary

`graph_driven_research_orchestrator` owns graph-level routing and then delegates to node-local entry skills. Heavy execution should stay in bounded terminal workers.

`auto_experiment_worker` is the canonical heavy experiment worker. It is called only after a local entry or wrapper skill has selected one node and bound the experiment contract. `local_wrapper` binds local IO for canonical workers; `local_execution` is reserved for stable closed-loop nodes that really execute locally. The experiment worker does not read graph files, select nodes, discover skills, or refresh global artifacts.

## Daily Loop

1. Update repo truth.
2. Rebuild projections when needed using `docs/dev.md`.
3. Optionally inspect the live scheduler in `web/dashboard/`.
4. Inspect `research_overview.canvas`.
5. Work in `current_focus.canvas`.
6. Put provisional relations, methods, skills, or framework notes in `framework_workbench.canvas`.
7. Move accepted proposals into `obsidian/inbox/canvas_proposals.md`.
8. Let a local agent or human write accepted proposals back to repo truth.
9. Return accepted changes to the graph scheduler before the next bounded step.
