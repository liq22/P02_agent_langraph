
# P02 Submission-Ready Goal Package v4

This package is optimized for the actual current state of `liq22/P02_agent_langraph`.

## Key correction from generic packages

The current repository is not ready for final paper writing or PHMGA formal experiments. Its graph currently points to:

```text
research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用
```

Therefore this package starts by closing the P1_01 data/provenance/submodule node.

## Actual first path

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

## What is included

- Actual-repo calibration files under `docs/submission_ready_goal/actual_repo/`.
- P1_01 node-specific templates under `docs/submission_ready_goal/node_templates/P1_01_actual/`.
- Updated FSM and master Codex `/goal` prompt.
- Validator `tools/validate_p1_01_node_package.py`.
- Existing data/project/paper readiness guides, traceability lock, Claude Code handoff lane, and validation tools.

## Recommended installation

From `liq22/P02_agent_langraph` root:

```bash
unzip p02_submission_ready_goal_package_v4_p02_actual.zip
cp p02_submission_ready_goal_package/AGENTS.md ./AGENTS.md
cp -R p02_submission_ready_goal_package/docs/submission_ready_goal ./docs/
mkdir -p tools/submission_ready_goal
cp p02_submission_ready_goal_package/tools/*.py ./tools/submission_ready_goal/
```

Optional Claude Code assets:

```bash
cp -R p02_submission_ready_goal_package/claude_code_assets/.claude ./.claude
```

## First validator

```bash
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root .
```

After the node-local outputs are created:

```bash
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs
```
