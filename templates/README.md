# Templates

This directory stores reusable scaffolds and examples. Templates are not scheduler truth and are not runtime state.

## Layout

- `execution_contract.template.yaml`: execution contract scaffold used by acceptance and smoke flows.
- `nodes/`: parent and leaf node scaffolds. New nodes should start with only `README.md` and `status.yaml`; `config.yaml` is an optional local override scaffold, not a default file.
- `shared/`: reusable minimal review and Markdown/TeX sync templates.

Keep canonical research state under `research/**/status.yaml` and explicit cross-node relations under `backend/relations/edge_registry.json`.

## Contract

- Keep templates out of `backend/graph/` and `research/` unless a concrete node is being instantiated.
- Do not treat template files as current node status or scheduler input.
- Do not pre-create review, response, verdict, HUMAN_ONLY, or index files from a node template. Create those slots only after a bounded step or explicit gate requires them.
- If a script or test needs a scaffold, reference it from `templates/` rather than duplicating a backend template directory.
