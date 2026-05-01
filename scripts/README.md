# Scripts Guide

This file is the developer-facing usage map for the `scripts/` directory.

If you only need the normal operating path, start here:

```bash
python scripts/refresh_views.py --mode graph_only
python scripts/refresh_views.py --mode full
bash scripts/dev_start_agent_app.sh
python scripts/validate_research_truth.py --require-submission
```

Everything else in `scripts/` is either a substep of those entrypoints, a maintenance tool, or a legacy candidate.

## Developer Tasks

### Daily entrypoints

Use these first unless you are debugging one lower layer on purpose.

- `refresh_views.py`: unified graph/projection refresh entrypoint
- `dev_start_agent_app.sh`: local agent UI startup entrypoint
- `validate_research_truth.py`: final submission check, not a framework-health check

### Projection pipeline

These scripts build derived views and are normally called by `refresh_views.py`.

- `refresh_hypergraph.py`
- `build_hierarchy_projection.py`
- `build_node_details.py`
- `build_scope_rollup.py`
- `build_board_state.py`
- `build_canvas_from_graph.py`

### Skill and contract maintenance

These scripts maintain local-skill contracts and generated wrappers.

- `node_tier.py`
- `regenerate_local_skills.py`
- `validate_local_skills.py`
- `validate_skill_fit.py`
- `lint_jargon.py`
- `generate_agent_skill_wrappers.py`
- `sync_agent_skill_wrappers.sh`

### Environment and startup helpers

- `setup_venv.py`

### Legacy candidates or isolated utilities

- `bootstrap_agent_app.sh`
- `S_01_moctree.py`

## Where Each Script Is Used

### Refresh and projection chain

- `refresh_views.py`
  - Category: daily entrypoint
  - Used by: `README.md`, `docs/dev.md`, `backend/agent_gateway/app.py`, multiple tests, gateway fixture, and active runtime skills
  - Produces: graph refresh only, or full projection refresh depending on `--mode`
  - Run directly: yes
  - Status: `active-entry`

- `refresh_hypergraph.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, tests, acceptance specs, and graph-related docs
  - Produces: `backend/graph/graph.json`, `backend/graph/graph_status.json`
  - Run directly: only when debugging scheduler graph output; use `--strict --check` to validate without writing graph files
  - Status: `active-substep`

- `build_hierarchy_projection.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, projection/update docs
  - Produces: hierarchy projection for dashboard and app views
  - Run directly: only when debugging hierarchy projection
  - Status: `active-substep`

- `build_node_details.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, `docs/dev.md`, projection/update docs
  - Produces: node detail projection used by dashboard and agent UI
  - Run directly: only when debugging node readiness, missing files, review gates, or binder state
  - Status: `active-substep`

- `build_scope_rollup.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, projection/update docs
  - Produces: subtree and scope summaries
  - Run directly: only when debugging scope summaries
  - Status: `active-substep`

- `build_board_state.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, projection/update docs
  - Produces: board lanes such as `scheduler_now`, `truth_ready`, `review_blocked`, `execution_blocked`, and `truth_blocked`
  - Run directly: only when debugging board state
  - Status: `active-substep`

- `build_canvas_from_graph.py`
  - Category: projection pipeline
  - Used by: `refresh_views.py`, tests, `obsidian/canvases/README.md`, frontend docs, and acceptance specs
  - Produces: generated Obsidian Canvas projections
  - Run directly: yes, mainly for Canvas debugging or `--dry-run` validation
  - Status: `active-substep`

### Startup and environment helpers

- `dev_start_agent_app.sh`
  - Category: daily entrypoint
  - Used by: `README.md`, `docs/dev.md`, `docs/CODEX_ONLY_WORKFLOW.md`, `docs/USER_GUIDEBOOK.md`, `web/app/app.js`, and frontend state docs
  - Produces: refreshed projections and a running uvicorn gateway for `web/app/`
  - Run directly: yes
  - Status: `active-entry`

- `setup_venv.py`
  - Category: environment helper
  - Used by: `dev_start_agent_app.sh`, `bootstrap_agent_app.sh`
  - Produces: local `.venv` from `requirement.yaml`
  - Run directly: yes, but usually only when rebuilding local environment
  - Status: `maintenance`

- `bootstrap_agent_app.sh`
  - Category: startup helper
  - Used by: no active docs, tests, gateway code, or frontend runtime surfaces
  - Produces: `.venv`, copied gateway config, and a one-time projection refresh
  - Run directly: only if someone still wants the older bootstrap flow
  - Status: `legacy-candidate`

### Skill and contract maintenance

- `node_tier.py`
  - Category: maintenance library
  - Used by: `build_canvas_from_graph.py`, `build_node_details.py`, `regenerate_local_skills.py`, `validate_local_skills.py`, `validate_skill_fit.py`, and smoke tests
  - Produces: no direct output; shared mode/profile parsing helpers
  - Run directly: no
  - Status: `maintenance`

- `regenerate_local_skills.py`
  - Category: maintenance tool
  - Used by: local-skill regeneration flows, fixture acceptance, and legacy/reference optimization notes
  - Produces: regenerated local skill and prompt layers
  - Run directly: yes, only after changing tier policy, overrides, or generation contracts
  - Status: `maintenance`

- `validate_local_skills.py`
  - Category: maintenance tool
  - Used by: live repo smoke, fixture acceptance, changelog references, and developer checks
  - Produces: validation pass/fail for local stacks and prompt contracts
  - Run directly: yes
  - Status: `maintenance`

- `validate_skill_fit.py`
  - Category: maintenance tool
  - Used by: live repo smoke, changelog references, and developer checks
  - Produces: validation pass/fail for global skill catalog, local fit, and node-mode distribution
  - Run directly: yes
  - Status: `maintenance`

- `lint_jargon.py`
  - Category: maintenance tool
  - Used by: live repo smoke and developer checks
  - Produces: report of banned internal terms in entry docs, skills, and node-local files
  - Run directly: yes
  - Status: `maintenance`

- `generate_agent_skill_wrappers.py`
  - Category: maintenance tool
  - Used by: `sync_agent_skill_wrappers.sh` and wrapper-pack references
  - Produces: local `.claude/skills/` and `.codex/skills/` wrapper files
  - Run directly: yes, but the shell wrapper is usually easier
  - Status: `maintenance`

- `sync_agent_skill_wrappers.sh`
  - Category: maintenance tool
  - Used by: `docs/dev.md`
  - Produces: regenerated local wrapper directories through `generate_agent_skill_wrappers.py`
  - Run directly: yes
  - Status: `maintenance`

### Final submission check

- `validate_research_truth.py`
  - Category: daily entrypoint for final submission readiness
  - Used by: `docs/dev.md`, tests, runtime skills, `research/P2_论文撰写/docs/manuscript.md`, and acceptance plans
  - Produces: submission-readiness or consistency validation result
  - Run directly: yes
  - Status: `active-entry`

### Isolated legacy utility

- `S_01_moctree.py`
  - Category: isolated utility
  - Used by: no active docs, tests, runtime skills, gateway code, or projection chain
  - Produces: Markdown directory-tree documentation for `backend/` and `research/`
  - Run directly: only when a human wants a snapshot tree document
  - Status: `legacy-candidate`

## Dependency Map

```text
refresh_views.py
  -> refresh_hypergraph.py
  -> build_hierarchy_projection.py
  -> build_node_details.py
  -> build_scope_rollup.py
  -> build_board_state.py
  -> build_canvas_from_graph.py

dev_start_agent_app.sh
  -> setup_venv.py
  -> refresh_views.py --mode full
  -> uvicorn backend.agent_gateway.app:app

sync_agent_skill_wrappers.sh
  -> generate_agent_skill_wrappers.py
```

## Script Status Legend

- `active-entry`: recommended direct entrypoint
- `active-substep`: current substep in an active build/refresh chain
- `maintenance`: active maintenance or validation tool, but not part of the normal user loop
- `legacy-candidate`: low-use or replaced tool; keep only if still needed

## Do Not Confuse

- `refresh_views.py` is the normal entrypoint; the `build_*` scripts are lower-level projection tools.
- `validate_research_truth.py` is the final submission check; `validate_local_skills.py` and `validate_skill_fit.py` are contract checks.
- `node_tier.py` is a library module, not a user-facing command.
- `bootstrap_agent_app.sh` is not the recommended agent UI startup path.
