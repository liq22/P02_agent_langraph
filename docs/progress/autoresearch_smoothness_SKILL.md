# Autoresearch Smoothness Development Guardrail

Use this only while changing the cockpit UX. It is not a runtime research skill.

## Rules

- Treat repo files as truth and `backend/graph/*` as derived projections.
- Never add content payloads, ownership, priority, or summaries to `graph.json`.
- Keep agent execution selected-node scoped and bounded.
- Prefer explicit readiness and disabled actions over hidden retries.
- A UI convenience may create a session and run once, but it must not create an unbounded loop.

## Done Check

- User can see why the app cannot run.
- User can select a node without copying ids.
- User can launch one bounded prompt with one action.
- Tests cover readiness, blocked run state, projection, and static frontend hooks.
