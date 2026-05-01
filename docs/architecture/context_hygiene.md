# Context Hygiene

This document defines the default context boundary for agents working in this repository.

The goal is not to hide useful material. The goal is to prevent external references, generated views, private notes, secrets, and historical plans from silently becoming instructions for the current run.

## Default Read Order

For a normal selected-node run, read only:

1. `AGENTS.md`
2. `README.md`
3. `backend/graph/graph_status.json`
4. the selected node path from `backend/graph/graph.json`
5. the selected node's `README.md`
6. the selected node's `status.yaml`
7. the selected node's `skills/local_entry.md`
8. files explicitly named by that `local_entry.md` for the current bounded round

Do not search the whole repository for a better instruction after a valid selected-node entry file is found.

## Quarantined Context

These paths are not default context:

- `_reference/**`: external repositories, historical packs, downloaded examples, and old agent instructions.
- `research/**/docs/HUMAN_ONLY.md`: human-only notes; read only when the user explicitly requests them for the current run.
- `reports/**`: generated analysis reports, not live instructions.
- `backend/graph/*.json`: derived scheduler/projection data, not content truth. Read only the minimal graph files needed for scheduling.
- `obsidian/canvases/**`: generated Canvas views, not source truth.
- `web/app/vendor/**`, binary assets, package locks, and cached artifacts: implementation or noise, not agent instruction.

## Secrets

Never read or summarize secret-like files during normal work. This includes `.env`, `.env.*`, credentials, tokens, private keys, and local tool state.

It is acceptable to verify that a secret-like path is ignored or untracked by inspecting file names and git metadata. Do not inspect its contents unless the user explicitly asks.

## Source Truth

- `research/` is the research work truth.
- `backend/relations/edge_registry.json` is the explicit relation truth.
- `backend/graph/*.json` is derived scheduler/projection output.
- `.agent/skills/*/SKILL.md` is the global skill truth.
- Node-local `skills/local_entry.md` controls selected-node read order.
- `web/` and `obsidian/` are operation/projection surfaces, not content truth.

## Validation

Run:

```bash
python test/run_context_hygiene_acceptance.py
```

The check fails on protected context leaks, tracked secret-like paths, and default read-order violations. It may report lower-risk warnings for legacy or reference-heavy material that remains available only by explicit request.
