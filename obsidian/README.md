# Obsidian Projection Surface

This directory is an active Obsidian IDE projection surface. Keep it at the repository root because Canvas generation scripts, smoke tests, and workflow docs use this path directly.

`obsidian/` is not a source of truth. Canonical research state stays in `research/**/status.yaml`, `research/**/README.md`, node-local skills, and `backend/relations/edge_registry.json`.

## Layout

- `canvases/`: generated and preserved `.canvas` files for overview, current focus, and framework workbench views.
- `inbox/`: proposal notes that must be promoted back into repo truth before they become canonical.

## Contract

- Keep `obsidian/` at the repository root.
- Do not merge it into `docs/` or `web/`; those surfaces serve different users.
- Generated Canvas files can be rebuilt, but accepted proposals must be written back to repo truth before they become canonical.
