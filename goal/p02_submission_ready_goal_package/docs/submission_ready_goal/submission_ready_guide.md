# Submission-Ready Guide

## Goal

Make `P02_agent_langraph` and the `PHMGA` submodule jointly submission-ready.

## Definitions

### Data-ready

The user-provided data pack has been audited, the canonical metadata and formal H5 files exist, checksums are recorded, and PHM-Vibench data_factory can read the formal datasets.

### Project-ready

PHMGA can run formal experiments from the Vibench-read data handoff, has a selected backend, has completed main and minimum ablation runs, and has non-empty paper main tables whose rows trace to ledger rows, `result_md`, and `artifact_dir`.

### Paper-ready

P02_agent_langraph has all required nodes completed, final TeX assembled, claim-evidence complete, reviews addressed, and `python scripts/validate_research_truth.py --require-submission` passes.

## Required execution order

```text
0. Install this package under docs/submission_ready_goal/
1. Close current P1_01 data/submodule node
2. Audit DATA_ROOT
3. Create Vibench read bundles for RM_017_Ottawa19 and RM_101_THU_GEARBOX
4. Patch or validate PHMGA handoff from Vibench read bundle to DatasetProtocol
5. Run PHMGA Stage B backend comparison
6. Select selected_global_best_backend
7. Run Stage C main results
8. Run minimum Stage D ablations
9. Update PHMGA ledger and main tables
10. Backfill paper nodes and claim-evidence registries
11. Assemble final TeX
12. Run final submission check
```

## Non-negotiable constraints

- Vibench data_factory reads data only.
- PHMGA owns all downstream experiment logic.
- P02_agent_langraph owns paper evidence and final submission.
- Pending or failed rows cannot enter main tables.
- Unsupported claims cannot enter the paper.


## Claude Code as an assistant, not a truth source

Claude Code can accelerate the submission-ready process by taking small, bounded tasks. The preferred pattern is:

```text
Codex owns `/goal` → Claude Code investigates or drafts → Claude returns handoff → Codex validates and merges → final gates decide
```

Use Claude Code subagents for focused single-session tasks and agent teams only for parallel review/exploration tasks with file-disjoint ownership. Claude Code output becomes project evidence only after a handoff artifact passes `06_claude_code_handoff_checklist.yaml`.
