# Autoresearch User Guidebook

This guide is for a researcher or maintainer who wants to place existing material into the right part of the workspace without first learning the full developer UI.

## 1. Start From Your Current Material

You can enter from any phase. Pick the closest match:

- `P0`: raw idea, background, gap, research question, novelty, scope.
- `P1`: data, code, experiment protocol, metrics, baselines, preliminary results.
- `P2`: manuscript outline, section draft, figures, claim-evidence material.
- `P3`: critique, simulated review, revision plan, blocking issues.
- `P4`: reviewer comments, response draft, response evidence, resubmission material.

Record material with either a phase:

```bash
python scripts/intake_research_materials.py --input material.yaml --target-phase P2
```

or an exact node:

```bash
python scripts/intake_research_materials.py --input material.yaml --target-node research::P2_论文撰写::P2_02_初稿_md::P2_02_01_引言
```

The input file should contain:

```yaml
material_summary: What you already have.
available_assets: Papers, code, data, results, draft text, reviews, or notes.
desired_output: What you want next.
constraints: Time, data, compute, venue, non-goals, or unavailable actions.
known_gaps: What remains weak, missing, unclear, or unverified.
```

The expected result is node-local:

```text
research/<target-node>/artifacts/intake/material_<timestamp>.yaml
research/<target-node>/docs/intake_<timestamp>.md
one recommended worker
one bounded next action
advisory unmet prerequisites from explicit dependencies
```

This intake records where your material should enter. It does not mark earlier phases complete, bypass node checklists, or claim that the material is ready for publication.

## 2. Two Modes

### Researcher Material Intake

Use material intake when your goal is to place research material and get the next bounded action. This path asks for:

- current phase or target node
- material summary
- available assets
- desired output
- constraints
- known gaps

### Developer Mode

Use `/app/`, `/web/dashboard/`, or `obsidian/` when maintaining or debugging the research workspace.

Developer Mode exposes authoritative repository files, generated views, node status, agent sessions, and projection health. It is useful for maintainers, but it is not required before recording research material.

## 3. Mental Model

Autoresearch is a folder-backed research workspace, not a fully autonomous paper factory.

Edit these files when research meaning changes:

- `research/**/README.md`
- `research/**/status.yaml`
- `research/**/prompts/`
- `research/**/skills/`
- `research/**/docs/`
- `research/**/artifacts/`
- `research/**/review/`
- `.agent/skills/*/SKILL.md`
- `backend/relations/edge_registry.json`

These files are generated views:

- `backend/graph/graph.json`
- `backend/graph/graph_status.json`
- `backend/graph/node_details.json`
- `backend/graph/scope_rollup.json`
- `backend/graph/board_state.json`
- `obsidian/canvases/*.canvas`
- `web/app/`
- `web/dashboard/`

Do not edit generated graph or Canvas files to prove progress. Write evidence back to the selected node, then refresh generated views.

## 4. First Run For Developers

If you are maintaining the system rather than starting a project, use the agent UI, dashboard, or Obsidian view in sections 7 and 8. Developer setup, refresh, acceptance, and final submission commands live in `docs/dev.md`.

Important distinction:

- Framework checks prove the operating substrate is coherent.
- They do not prove the project already has a finished paper.
- A submission-ready claim is valid only after the final submission check in `docs/dev.md` passes.

## 5. Daily Developer Loop

Use one limited run at a time.

1. Read `backend/graph/graph_status.json`.
2. Use `next_node` as the only target for this run.
3. Find the target path in `backend/graph/graph.json`.
4. Enter the node and read the entry files first:

   ```text
   README.md
   status.yaml
   prompts/research_prompt.md
   prompts/acceptance_checklist.yaml
   skills/local_entry.md
   ```

5. Read `prompts/review_rubric.yaml` and `review/verdict.yaml` only when `prompts/acceptance_checklist.yaml` explicitly requires external review.
6. Follow local skill resolution:

   ```text
   skills/local_entry.md
   -> optional skills/local_wrapper.md or skills/local_execution.md
   -> required project worker in .agent/skills/
   ```

7. Run one unit only.
8. Update only selected-node files: docs, artifacts, logs, review, or status under that node.
9. Return to graph scheduling. If generated views need rebuilding, use `docs/dev.md`.

For a Codex-only operator path, use `docs/CODEX_ONLY_WORKFLOW.md`. It explains the manual Codex loop, agent UI configuration, and where manuscript updates are expected to land.

## 6. From Any Phase To Submission-Ready Paper

The repository is organized as a research progression:

- `P0`: research background, scientific question, novelty, plan, constraints.
- `P1`: experiment design, repository blueprint, executable validation, result synthesis.
- `P2`: manuscript drafting, TeX finalization, formal checks, anti-AI-style cleanup.
- `P3`: simulated review and revision loops.
- `P4`: reviewer response, coverage check, revision evidence, resubmission bundle.

Material intake can place notes into any phase, but the final submission path still depends on local evidence, explicit dependencies, and acceptance checks.

Manuscript navigation starts at `research/P2_论文撰写/docs/manuscript.md`. P2 folder-node manuscript files are indexes; section-level writing remains in leaf-node `docs/manuscript.md` files.

Each node can advance only when its own local evidence passes:

- `status.yaml` is moved to `done` or `archive`.
- `prompts/acceptance_checklist.yaml` items are complete.
- If external review is explicitly required, `review/verdict.yaml` has `review_complete: true`, `overall_verdict: pass`, `hard_fail: false`, and `independence_confirmed: true`.
- If external review is explicitly required, the Nature-level review score is at least the configured threshold, default `90`.
- Placeholder text is gone from manuscript, review, response, verdict, and TeX files.

The final submission check also requires hard artifacts:

- `P1_04` has `artifacts/execution_contract.yaml` with `contract_mode: executable`.
- `P1_04` has `artifacts/auto_experiment/results.tsv`.
- `P1_04` has `logs/auto_experiment/latest_run.log`.
- `P1_05` has `artifacts/result_registry.yaml`.
- `P2_03` has a complete `tex/main.tex` with abstract, introduction, methods, results, discussion, data availability, and code availability.
- `P4_07` has `artifacts/resubmission_bundle_manifest.yaml` whose listed assets exist.

Only the final submission check documented in `docs/dev.md` can claim `submission-ready`.

Expected success line:

```text
research check: pass mode=submission-ready
```

Completion words:

- `ready`: the node can be scheduled.
- `done`: the selected node has met its local acceptance checklist.
- `pass`: one named check passed.
- `submission-ready`: the final submission check passed.
- `framework healthy`: maintenance checks passed; the paper may still be incomplete.

## 7. Agent UI Workflow

The agent UI is optional. It helps launch selected-node agent runs but does not replace repo files.
Codex is enough for the documented loop. Claude Code entries in the gateway catalog are optional teammates and only run when the local `claude` binary is installed.

```bash
bash scripts/dev_start_agent_app.sh
```

If you need local command overrides, copy `config/agent_gateway.yaml.example` to `config/agent_gateway.yaml` and edit that file. Otherwise the shipped example config is used directly when `codex` or other referenced binaries are already available on your machine.

Open:

```text
http://127.0.0.1:8765/app/
```

Use the agent UI to select a graph node and launch one run. The UI requires full generated views, but the agent still writes selected-node files. After the run, inspect local changes before refreshing generated views.

## 8. Dashboard And Obsidian

Serve the static dashboard from the repository root:

```bash
python -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/web/dashboard/
```

Open `obsidian/` as an Obsidian vault when inspecting Canvas views or using `obsidian/inbox/canvas_proposals.md`.

If these views are stale, rebuild them using `docs/dev.md`.

## 9. Blocking Conditions

These are blocking failures, not cosmetic warnings:

- `partial` is not pass.
- `review_only` is not executable experiment completion.
- Missing `results.tsv` means no experiment evidence.
- Missing `latest_run.log` means no reproducible run trace.
- Placeholder TeX is not a manuscript.
- Graph, dashboard, or Canvas green states do not prove paper completion.
- A review verdict without independence confirmation is not an external review pass.
- A submission bundle manifest with missing files is not a submission package.

If a framework check passes but the final submission check fails, the framework is healthy but the paper is not done.

## 10. Developer Maintenance

Developer-only setup, refresh, validation, and low-level fallback notes live in `docs/dev.md`.
