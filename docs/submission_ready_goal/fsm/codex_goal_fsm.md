
# Codex Goal FSM — Actual P02_agent_langraph Version

This FSM is optimized for the current state of `liq22/P02_agent_langraph`, whose active node is `P1_01_数据层_集中数据与子模块引用`.

## States

```text
S0_REPO_FACT_SYNC
→ S1_P1_01_NODE_PACKAGE
→ S2_DATA_RESOURCE_AUDIT
→ S3_VIBENCH_READ_BOUNDARY
→ S4_PHMGA_HANDOFF_AND_PREFLIGHT
→ S5_PHMGA_FORMAL_EXPERIMENTS
→ S6_PAPER_EVIDENCE_LOCK
→ S7_FINAL_SUBMISSION_VALIDATION
```

## S0_REPO_FACT_SYNC

Confirm root README, graph status, `.gitmodules`, selected-node path, and PHMGA submodule branch. Do not write research content yet.

Exit requires:
- `backend/graph/graph_status.json` read.
- `next_node` recorded.
- `.gitmodules` read.
- PHMGA submodule path and branch recorded.

## S1_P1_01_NODE_PACKAGE

Produce and review the selected node-local data/provenance package.

Exit requires:
- selected node `docs/manuscript.md` exists.
- selected node required artifacts exist.
- `review/verdict.yaml` is complete and pass.
- `python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs` exits 0.
- `python scripts/refresh_views.py --mode graph_only` runs after the bounded step.

## S2_DATA_RESOURCE_AUDIT

Audit external DATA_ROOT. Do not commit H5 files.

Exit requires:
- data manifest generated.
- checksums generated.
- RM_017 and RM_101 minimum formal data present.
- metadata-H5 alignment audit present.

## S3_VIBENCH_READ_BOUNDARY

Patch or document PHM-Vibench read-only data_factory boundary.

Exit requires:
- Vibench read bundle schema satisfied.
- Vibench owns reading only.
- PHMGA downstream ownership preserved.

## S4_PHMGA_HANDOFF_AND_PREFLIGHT

Make PHMGA consume the read bundle through its own DatasetProtocol and pass preflight for formal datasets.

Exit requires:
- PHMGA preflight passes for Ottawa and RM101 or blocker recorded.
- PHMGA submodule commit recorded.

## S5_PHMGA_FORMAL_EXPERIMENTS

Run Stage B, choose selected backend, run Stage C and minimum Stage D.

Exit requires:
- Stage B eligible rows.
- `selected_global_best_backend` not pending.
- Stage C main rows passed.
- minimum Stage D ablation rows passed.
- PHMGA `doc/experiments/02_main_tables.md` non-empty with passed rows only.

## S6_PAPER_EVIDENCE_LOCK

Lock claim/table/figure traceability.

Exit requires:
- all central claims have evidence IDs.
- every table/figure traces to data manifest, Vibench read bundle, PHMGA commit, artifact_dir, result_md, ledger/main table.
- unsupported/unclear/negative findings are not rewritten as positive claims.

## S7_FINAL_SUBMISSION_VALIDATION

Run final paper checks.

Exit requires:
- final TeX complete.
- required reviews complete.
- `python scripts/validate_research_truth.py --require-submission` prints `research truth: pass mode=submission-ready`.
