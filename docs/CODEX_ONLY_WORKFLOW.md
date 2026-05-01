# Codex-Only Workflow

This guide explains what a new user can automate with Codex in this repository.

Codex can advance one selected research node at a time. It should not claim a finished paper unless the final submission check passes.

## 1. What Codex Writes

Codex writes selected-node files only:

- `docs/manuscript.md`
- `artifacts/`
- `logs/`
- `review/`
- `status.yaml`

Codex must not write manuscript content into:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`
- Obsidian Canvas files
- dashboard files

Those files are generated views, not research content.

## 2. First Run

Start from current graph files and one selected node. Developer setup, refresh, acceptance, and final submission commands live in `docs/dev.md`.

Framework checks prove the operating substrate is coherent. They do not prove the paper is complete.

## 3. Manual Codex Loop

Use this path when running Codex from the terminal rather than the agent UI.

1. Read `backend/graph/graph_status.json`.
2. Use `next_node` as the only target.
3. Resolve that node path from `backend/graph/graph.json`.
4. Enter the node and read:

   ```text
   README.md
   status.yaml
   prompts/research_prompt.md
   prompts/acceptance_checklist.yaml
   skills/local_entry.md
   ```

5. Read `prompts/review_rubric.yaml` and `review/verdict.yaml` only when the acceptance checklist explicitly requires external review.
6. If `skills/local_entry.md` delegates to `manuscript_worker`, Codex should write the current node's `docs/manuscript.md`.
7. Stop after one selected-node step.
8. Return to graph scheduling. Use `docs/dev.md` only when generated views or checks are needed.

## 4. Agent UI Codex Loop

The agent UI can launch Codex directly when `codex` is already on your `PATH`. The shipped example gateway config is treated as the default catalog.
Claude Code entries in that catalog are optional teammates; Codex-only use does not require them, and they only run when the local `claude` binary is installed.

```bash
bash scripts/dev_start_agent_app.sh
```

If you need local overrides, copy `config/agent_gateway.yaml.example` to `config/agent_gateway.yaml` and edit that file.

Open:

```text
http://127.0.0.1:8765/app/
```

Select a node and use one run. The gateway injects a stable `author_agent_id` for the run into the prompt context; persist that value to `status.yaml` when the run materially updates selected-node files. Inspect changed files before running another step.

## 5. Manuscript Map

The paper draft is intentionally split by node:

- P2 paper-writing folder index: `research/P2_论文撰写/docs/manuscript.md`
- P2 draft subtree index: `research/P2_论文撰写/P2_02_初稿_md/docs/manuscript.md`
- Leaf section bodies: `research/P2_论文撰写/P2_02_初稿_md/*/docs/manuscript.md`
- Final TeX engineering node: `research/P2_论文撰写/P2_03_定稿_tex/docs/manuscript.md`
- Final TeX file: `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex`

Folder-node `docs/manuscript.md` files are navigation indexes. Leaf-node `docs/manuscript.md` files are the section-level writing files.

## 6. Completion Check

Only the final submission check documented in `docs/dev.md` can claim `submission-ready`. Do not treat framework acceptance, graph readiness, or Canvas visibility as paper completion.
