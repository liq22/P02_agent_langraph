# Autoresearch Smoothness Implementation Plan

## Backend

- Add `/api/app/bootstrap` as a non-failing readiness endpoint for graph projection state, config state, agent readiness, and setup commands.
- Add `/api/agents/run` to create a session and launch one bounded run from a selected node.
- Restore session summaries from `artifacts/agent_sessions/*/session.log` on gateway startup.

## Projection

- Keep scheduler graph unchanged.
- Extend `node_details.json` only with projection file entries for `skills/` and `prompts/`.

## Frontend

- Show setup readiness before graph data is available.
- Default agent target to the selected graph node and expose a datalist of known nodes.
- Provide prompt action chips for inspect, graph step, bounded experiment, and blocker review.
- Disable Run with a visible reason when graph/config/target/prompt is incomplete.

## Docs And Tests

- Update README with the gateway cockpit path.
- Add gateway API acceptance tests and a static frontend contract check.
- Re-run syntax, fixture acceptance, gateway acceptance, and live smoke where safe.
