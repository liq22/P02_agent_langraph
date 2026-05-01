# Agent Cockpit App Architecture

## Why This Layer Exists

The app is a local product surface for a human researcher and bounded agents. It does not own graph truth, manuscript truth, execution contracts, or research artifacts.

It exists to make one loop fast:

1. see the current scheduler frontier
2. choose or accept the current node
3. inspect only the relevant context
4. edit the node manuscript or launch one bounded session

## Truth Boundary

Repo truth:
- `research/**/README.md`
- `research/**/status.yaml`
- `research/**/skills/*`
- `research/**/docs/manuscript.md`
- `backend/relations/edge_registry.json`
- `.agent/skills/*/SKILL.md`

Derived projections:
- `backend/graph/graph.json`
- `backend/graph/graph_status.json`
- `backend/graph/hierarchy.json`
- `backend/graph/node_details.json`
- `backend/graph/scope_rollup.json`
- `backend/graph/board_state.json`

Runtime surface:
- `backend/agent_gateway/app.py`
- `web/app/*`

## Canonical UI

The cockpit has four zones:

1. Global scheduler bar: compact phase, next node, one primary session CTA, search, language, refresh, and heartbeat.
2. Tree navigator: left-side hierarchy navigation only.
3. Main workbench: `Overview`, `Node`, `Manuscript`, and `Session`.
4. Context drawer: default-collapsed auxiliary context for setup, current object, watched workset, files, skills, reads, relations, and diagnostics.

The left side answers "where can I go". The center answers "what am I doing". The right side answers "what context helps without taking over the task".
Watched nodes are not an active queue or scheduler truth source.

## Deprecated Vocabulary

Do not use these terms when describing the primary cockpit IA:

| Deprecated term | Canonical replacement |
| --- | --- |
| scope rail | Tree navigator |
| board workspace | Main workbench |
| node inspector as separate zone | Context drawer |
| agent cockpit as right-side zone | Main workbench + context drawer |

These older terms may still appear in `web/dashboard/`, which remains a separate static read-only monitor rather than the primary cockpit.

## Agent Constraints

- Sessions are `general`, `scope`, or `node` scoped.
- Execution stays bounded by the selected graph context.
- Session prompts may use semantic mentions: `@current`, `@scope`, `@node`, `@readme`, `@status`, and `@manuscript`.
- Explicit node mentions use the current `@research::...` ID form.
- The app expands these mentions into explicit context before sending the prompt.
- The gateway writes session logs under `artifacts/agent_sessions/`.
- The app must not mutate graph source files or derived graph projections directly.

## Manuscript Constraints

- The editable manuscript is node-local: `research/**/docs/manuscript.md`.
- Unsaved edits must not be silently replaced by refresh, node switching, reload, or page close.
- `Ctrl/Cmd+S` saves through the node manuscript API.
- Preview is a safe Markdown subset with explicit saved/dirty/saving/error UI state, not a second source of manuscript truth.

## Consistency Note

- The current branch source under `web/app/` is the implementation truth.
- Browser smoke and gateway acceptance are the behavior truth for the primary workbench flow.
- Screenshots are reference artifacts only; they do not override the checked-in DOM, copy, or tests.

## Desktop Path

Build and verify the web app first. A future Tauri wrapper may host the same app, but desktop packaging is not an active runtime source of truth.
