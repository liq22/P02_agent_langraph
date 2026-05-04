# P02 Submission-Ready Goal Package v3

This directory is the material package that lets Codex `/goal` operate as a finite-state, evidence-gated orchestrator for the P02 paper and PHMGA project submodule.

## What changed in v3

- Codex is an orchestrator, not a solo writer.
- Claude Code handoff is upgraded to `claude_code_handoff_v2`.
- State transitions are script-driven.
- Scorecards and checklists cannot be completed without command output or documented validation.
- A traceability lock is required before any claim, figure, or table becomes positive paper evidence.

## Read first

1. `../AGENTS.md` at repo root after installation.
2. `fsm/codex_goal_fsm.md`.
3. `tools/submission_ready_goal/verify_llm_keys.py` for secret-safe provider checks.
4. `traceability/traceability_lock.md`.
5. `final_submission_gate.md`.
6. `claude_code/claude_code_assistant_handoff.md` if Claude Code is used.

## Final rule

No component may claim submission-ready until the repository final check passes:

```bash
python scripts/validate_research_truth.py --require-submission
```

Expected success line:

```text
research truth: pass mode=submission-ready
```

---

## Prior package overview

# P02 Submission-Ready Goal Materials

This directory stores the material package for Codex `/goal`.
It is not a manuscript store, not graph truth, and not a replacement for node-local `research/**/docs/manuscript.md`.

## Three truth sources

```text
1. Data truth: PHM-Vibench data_factory + user-provided DATA_ROOT
2. Project truth: PHMGA submodule, journal_thesis branch, formal artifacts and result ledger
3. Paper truth: P02_agent_langraph autoresearch nodes, claim-evidence registries, reviews, final TeX
```

## Required outcome

A submission-ready state exists only when all three gates pass:

```text
Data-ready    -> data package and Vibench read bundle are auditable
Project-ready -> PHMGA formal runs have passed rows in main tables
Paper-ready   -> every claim/table/figure traces to data + PHMGA artifacts and final submission check passes
```

## Current canonical implementation submodule

```text
submodule path:
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA

submodule url:
https://github.com/PHMbench/PHMGA.git

submodule branch:
journal_thesis
```

## Data policy

The user provides a local data folder containing `metadata.xlsx`, metadata lineage files, and `RM_*.h5` files. Do not commit large H5 files to the paper repository. Record manifest, checksums, provenance, and data-read audit outputs instead.


## Optional Claude Code assistant lane

Claude Code can be used as an auxiliary assistant for bounded, auditable tasks. It must not replace Codex as the `/goal` owner and must not declare final submission readiness.

Use the Claude Code lane for simple tasks such as:

- DATA_ROOT audit summaries;
- PHMGA artifact/result-ledger traceability reviews;
- claim-evidence consistency checks;
- schema/checklist consistency review;
- handoff review.

Required protocol:

```text
Read docs/submission_ready_goal/claude_code/claude_code_assistant_handoff.md
Delegate a bounded task
Receive a handoff artifact
Validate 06_claude_code_handoff_checklist.yaml
Merge only if safe_to_merge=true and no hard fail
```

Project-level Claude Code helper assets are provided under:

```text
claude_code_assets/.claude/
```

Copy them into the repository root only when you want Claude Code project subagents and commands enabled.
