# P02 repository semantic merge and cleanup plan

**Audit date:** 2026-09-18  
**Source branch:** `feat/paper2-active-formal-20260903` at `0ac95c66a5740ca03945896480bf4b3a1fa0e75a`  
**Target branch before merge:** `dev` at `b43056842bda605f348e00f2bee57afa24e0d3de`  
**Inventory scope:** 219 user-listed paths, one decision per path.

## 1. Merge decision

The source branch is not safe for a normal content merge. Relative to `dev`, it is one commit ahead and eight commits behind. Its unique commit contains useful Paper-2 provenance, but it also contains historical run bundles, duplicate Graph implementation, AutoResearch governance, browser/application code, local-agent wrappers, and generated artifacts that later work has already superseded.

The correct operation is a **semantic merge**:

1. retain current `dev` as the content base;
2. record `0ac95c6` as the second parent so the branch history is genuinely merged;
3. add only the citation additions and this cleanup inventory;
4. do not restore stale runtime code, raw run trees, `.venv`, local settings, UI backends, or duplicate governance systems.

This is not a squash or a claim that every historical file remains active. The historical commit stays reachable through Git ancestry.

## 2. Single-source ownership after cleanup

### P02 keeps

```text
paper/draft/                  one canonical manuscript
paper/theory/                 paper-specific propositions, proofs and boundaries
paper/refs/                   bibliography and source-bounded literature matrix
paper/experiments/            estimands, comparison matrix and claim mapping only
paper/assets/                 selected editable publication figures/tables
paper/GOAL.md
paper/RESEARCH.md
paper/paper.yaml              only while consistent with the active manuscript
README.md / README_CN.md
AGENTS.md / CLAUDE.md / CORE.md
LICENSE
```

P02 is the scientific-writing repository. It must not remain a second runtime, evaluator, result authority, workflow platform, or application repository.

### `phm-agent-benchmark` owns

```text
src/phm_graph_agent/
Graph conditions and configuration
data/Runner/provider/evaluator integration
assignment and first-attempt scheduling
experiment execution and analysis
canonical attempt bundles and derived result tables
runtime, integration and statistical tests
```

Only unique, currently valid, test-backed semantics are migrated. A file is not moved merely because its name contains `graph`.

### Archive outside the active repositories

```text
_reference/
research/ historical workflow trees
Obsidian canvases
AutoResearch/node-governance backend and web application
submission-ready Goal packages
historical debug/formal run trees that are not canonical Benchmark evidence
obsolete agent skill wrappers and generated local-tool configuration
```

Archive material is evidence/history, not an executable or manuscript truth source.

## 3. Decision vocabulary

| Decision | Meaning |
|---|---|
| `KEEP_P02` | permanent paper-repository content |
| `KEEP_MINIMAL` / `KEEP_SELECTIVE` / `KEEP_P02_THIN` | retain only a reduced paper-facing form |
| `MOVE_THEN_REMOVE_DUPLICATE` | migrate missing tested semantics to Benchmark, validate, then delete P02 copy |
| `SPLIT_OWNERSHIP` / `AUDIT_AND_SPLIT` | separate scientific specification from executable implementation |
| `DISTILL_THEN_ARCHIVE` | extract unique scientific content, then archive the source |
| `ARCHIVE_THEN_REMOVE` / `ARCHIVE_OUTSIDE_ACTIVE_REPO` | no active role after preservation |
| `AUDIT_THEN_REMOVE` | inspect for unique contracts first; do not move wholesale |
| `DELETE_LOCAL_GENERATED` | delete immediately and ignore |
| `KEEP_TEMPORARILY` | retain only through the cleanup acceptance cycle |

## 4. Inventory summary

| Decision | Paths |
|---|---:|
| `ARCHIVE_OUTSIDE_ACTIVE_REPO` | 10 |
| `ARCHIVE_THEN_REMOVE` | 86 |
| `AUDIT_AND_SPLIT` | 4 |
| `AUDIT_THEN_REMOVE` | 15 |
| `DELETE_LOCAL_GENERATED` | 11 |
| `DISTILL_THEN_ARCHIVE` | 5 |
| `KEEP_MINIMAL` | 8 |
| `KEEP_P02` | 14 |
| `KEEP_P02_THIN` | 6 |
| `KEEP_SELECTIVE` | 2 |
| `KEEP_TEMPORARILY` | 11 |
| `MOVE_THEN_REMOVE_DUPLICATE` | 44 |
| `REMOVE_AFTER_DEPENDENCY_MIGRATION` | 1 |
| `REVIEW_REMOVE_OBSOLETE` | 1 |
| `SPLIT_OWNERSHIP` | 1 |

The complete row-level matrix is `path_inventory.md`.

## 5. Migration order

### Phase A — immediate hygiene

Delete from version control and add ignore rules for:

```text
.env
.venv/
**/__pycache__/
.claude/settings.local.json
local outputs, credentials and machine-specific settings
```

If `.env` or a credential was ever committed with a real value, rotate it; deletion alone is not remediation.

### Phase B — compare executable semantics with Benchmark

Compare, function by function, against the current Benchmark implementation:

```text
src/phm_graph_agent/**
scripts/analyze_graph_*.py
scripts/run_graph_*.py
scripts/schedule_graph_*.py
scripts/analyze_p2_*.py
scripts/audit_p2_*.py
scripts/finalize_p2_*.py
tests/test_graph_*.py
tests/test_p2_*.py
```

For each candidate:

1. identify the scientific contract it protects;
2. locate the current Benchmark equivalent;
3. migrate only a missing, supported behavior;
4. add or strengthen the Benchmark test first;
5. run the installed Benchmark suite;
6. delete the P02 duplicate only after parity is demonstrated.

Do not copy old execution engines, evaluator logic, raw-result parsers or checkpoints into Benchmark as parallel authorities.

### Phase C — paper consolidation

1. choose one active manuscript;
2. align `paper.yaml`, `GOAL.md`, `RESEARCH.md`, theory and experiment matrix;
3. keep one bibliography;
4. retain final editable figures/tables plus provenance pointers;
5. move executable configs, schedulers, analyzers and canonical results to Benchmark;
6. convert historical development results into a concise evidence/provenance note or external archive.

### Phase D — remove legacy platform surfaces

After scientific content is distilled, remove:

```text
backend/
web/
obsidian/
templates/
test/                    legacy gateway/browser/node tests
goal/p02_submission_ready_goal_package/
tools/submission_ready_goal/
.agent/ .agents/ .claude/skills/ .codex/
most of docs/architecture, docs/desktop, docs/plan and docs/progress
```

None should be migrated into Benchmark unless a narrowly identified PHM contract is both unique and covered by a direct test.

## 6. Hard acceptance gates before deleting duplicated Graph code

- Benchmark imports and runs without P02 on `PYTHONPATH`.
- Benchmark owns the only maintained `phm_graph_agent` package.
- Every active Graph condition uses Benchmark's DataPort, Runner, provider, evaluator, assignment and output paths.
- Current Graph tests pass in an installed environment.
- P02 manuscript paths point to Benchmark configs/results rather than deleted local scripts.
- Real-data acceptance remains distinct from synthetic/runtime tests.
- Historical outputs are either canonical Benchmark attempts or explicitly archived, never two competing result authorities.
- No paper claim depends on a file scheduled for removal without a replacement citation or provenance pointer.

## 7. Citation additions

The bibliography and literature matrix add the minimum foundations needed for current claims:

- Hansen (1997): finite-state controllers under partial observability;
- Huang and Ontañón (2022): invalid-action masking;
- Even-Dar, Mannor and Mansour (2006): action elimination and stopping;
- Jiang and Li (2016): off-policy evaluation;
- Khan, Saveski and Ugander (2024): partial identification without overlap;
- Yao et al. (2024), $\tau$-bench: repeated tool-agent reliability.

These sources delimit novelty and identification. They do not establish that the P02 gate improves PHM performance.
