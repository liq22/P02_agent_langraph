# Developer Commands

This page is the command reference for repository maintenance. It is not the user or agent operating loop.

For script categories, real callers, and legacy status, see `scripts/README.md`.

## Setup

Install gateway dependencies when preparing a local development environment:

```bash
python -m pip install -r backend/agent_gateway/requirements.txt
```

Install browser smoke dependencies only when validating the primary web app in a real browser:

```bash
python -m pip install -r test/requirements-browser.txt
python -m playwright install chromium
```

## Refresh

Refresh only the minimal scheduler graph after a bounded agent step:

```bash
python scripts/refresh_views.py --mode graph_only
```

This rebuilds:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`

Refresh all human-facing projections before a web app, dashboard, Canvas, or review session:

```bash
python scripts/refresh_views.py --mode full
```

This also rebuilds hierarchy, node details, scope rollup, board state, and generated Canvas projections.

Use low-level refresh scripts only when debugging one projection layer:

```bash
python scripts/refresh_hypergraph.py
python scripts/refresh_hypergraph.py --strict --check
python scripts/build_canvas_from_graph.py
```

## Checks

Run a fast syntax check after Python script edits:

```bash
python -m py_compile scripts/refresh_hypergraph.py scripts/build_canvas_from_graph.py scripts/refresh_views.py backend/agent_gateway/app.py
```

Run strict jargon lint for user entry documents:

```bash
python scripts/lint_jargon.py --strict README.md docs/USER_GUIDEBOOK.md docs/CODEX_ONLY_WORKFLOW.md docs/architecture/entry_matrix.md
```

Run warning-only jargon lint for skills and research nodes:

```bash
python scripts/lint_jargon.py --warn-only .agent/skills research
```

Run the live repo smoke check after a bounded node-local change:

```bash
python test/run_live_repo_smoke.py
```

Run the optimizer in bounded advisory mode when maintaining prompts, skills, validator configs, or optimizer helpers:

```bash
python .agent/skills/autoresearch-system-optimizer/scripts/run_optimization_cycle.py --scope repo --apply none --dry-run
```

Run the browser smoke check when changing `web/app/`, session UX, keyboard navigation, or manuscript editing behavior:

```bash
python test/run_browser_smoke.py
```

Run the full framework acceptance suite after changing graph, projection, gateway, template, or validation behavior:

```bash
python test/run_all_acceptance.py
```

Framework acceptance passing means the operating substrate is coherent. It does not mean the live paper is complete.

Run the final submission check only when evaluating a `submission-ready` claim:

```bash
python scripts/validate_research_truth.py --require-submission
```

The expected success line is:

```text
research truth: pass mode=submission-ready
```

## Local Web Surfaces

Start the agent UI:

```bash
bash scripts/dev_start_agent_app.sh
```

Open:

```text
http://127.0.0.1:8765/app/
```

Record phase-aware research material without opening a browser:

```bash
python scripts/intake_research_materials.py --input material.yaml --target-phase P1
```

Serve the static dashboard from the repository root:

```bash
python -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/web/dashboard/
```

Surface boundary:

- `web/app/` is the primary graph-aware agent UI and operates only through `backend/agent_gateway/app.py`.
- `web/dashboard/` is a static read-only generated view. Do not turn it into a second operation path or state authority.

Open `obsidian/` as an Obsidian vault when inspecting generated Canvas projections or using the proposal inbox.

## Local Skill Wrappers

Generate local Claude/Codex wrapper skills from the canonical `.agent/skills/*/SKILL.md` files:

```bash
bash scripts/sync_agent_skill_wrappers.sh .
```

This writes only repository-local derived files under `.claude/skills/` and `.codex/skills/`. These wrapper directories are ignored by Git and can be regenerated.

Do not treat wrapper files as authoritative. If a wrapper and `.agent/skills/<skill>/SKILL.md` differ, the `.agent/skills` file wins.

## Failure Boundaries

- A green graph, dashboard, or Canvas does not prove manuscript completion.
- A passing framework check does not prove submission readiness.
- A failing final submission check is useful when it lists missing evidence.
- Do not add broad fallback behavior to hide invalid YAML, missing experiment evidence, or incomplete submission artifacts.

Current fallback boundaries:

- `scripts/build_node_details.py` should fail loudly on invalid YAML in node details or frontmatter.
- `scripts/refresh_hypergraph.py` may extract legacy `status` or `lifecycle.stage` values from older status files. This is scheduler compatibility, not silent completion.
- `backend/agent_gateway/app.py` may skip unreadable historical session logs. This protects the UI from stale local artifacts, not research content.
- Tests may read missing optional files as empty strings or dicts so they can report all missing contract parts in one run.
- `scripts/validate_research_truth.py` aggregates blockers because submission readiness needs a complete failure list.
