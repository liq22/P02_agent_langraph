# P1_06 Repository Strategy Summary

- node_id: `research::P1_实验设计与仓库蓝图::P1_06_代码仓库_已有_重新初始化_子模块策略`
- generated_at: 2026-05-05
- actor: codex-local
- node_mode: parent / routing summary

## Scope Decision

P1_06 is a repository-strategy parent node. It coordinates boundaries for the existing PHMGA submodule and records reproducible update/rollback rules. It does not execute PHMGA experiments, edit PHMGA implementation files, select the final backend, or convert any submodule result into manuscript evidence.

No explicit child node directories exist under P1_06 besides the node-local `artifacts/`, `prompts/`, `review/`, and `skills/` folders. Therefore `route_child_first` is not triggered by a ready child in this round. The parent action is limited to repository strategy, submodule reference facts, and reviewable handoff state.

## Required Questions

### Which code belongs in the main repository?

The main repository owns research orchestration truth:

- scheduler inputs and derived graph refresh commands;
- node-local manuscripts, artifacts, reviews, responses, and status files;
- submission-ready validators, FSM/audit files, and review handoff logs;
- PHMGA/Vibench boundary documents and read-bundle specifications;
- Claude/Codex wrapper skills that expose local review or orchestration workflows.

The main repository must not duplicate PHMGA source code, PHMGA experiment ledgers, PHMGA training/evaluation semantics, or Vibench data internals as a second source of truth.

### Which code should be connected rather than copied?

PHMGA is connected as a git submodule at:

`research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA`

The submodule tracks branch `journal_thesis` from `https://github.com/PHMbench/PHMGA.git`. The current local HEAD and fetched `origin/journal_thesis` are both `914bc5925d5230917a5de95d88784075fb2b041e`; `git pull --ff-only` reports `Already up to date.`

Vibench data under `/mnt/k/D01_vibench` is connected as an external data root, not copied into the repository. `.env` credentials are connected only as local runtime configuration and must not be copied into artifacts.

### Which code should remain inside the PHMGA submodule?

PHMGA owns its own source, configs, tests, scripts, experiment docs, result ledgers, and `paper_phmga/` evidence bundles. The parent repo can reference these paths and record their eligibility state, but should not recreate PHMGA internals in parent-node artifacts.

### How do we reduce future maintenance cost and version confusion?

Use a three-layer version contract:

1. Parent repo records only submodule path, URL, expected branch, pinned commit, remote comparison, dirty count, and allowed update policy.
2. PHMGA changes remain inside the submodule and are reviewed or committed there before the parent pointer is advanced.
3. Paper-facing claims cite PHMGA result ledgers and node-local claim/evidence registries, not ad hoc file paths or generated graph projections.

Current PHMGA status is intentionally not clean: 66 dirty/untracked entries are present after prior provider, config, experiment, and runtime work. This is not a reason to reset. It is a reason to require a protection step before any future submodule pointer update.

### How do we guarantee minimal edits and rollback?

- Pull/update policy: fetch first, compare `HEAD...origin/journal_thesis`, then use `git pull --ff-only` only when dirty state is protected or the update is known to be a no-op.
- Dirty-work policy: do not run `git reset`, `git checkout --`, or cleanup commands against PHMGA without explicit user approval and a backup/commit/stash plan.
- Pointer policy: parent repo may advance the submodule pointer only after PHMGA dirty work is intentionally committed/stashed/discarded inside the submodule and the new commit is validated.
- Rollback policy: parent rollback is a submodule pointer revert plus restoration of node-local handoff/failure ledger state; it is not a manual copy of PHMGA files back into the parent repo.

## Current Repository Boundary Conclusion

P1_06 is complete enough for independent review as a parent coordination package: submodule identity is pinned and up to date with remote, dirty state is visible, and future updates are constrained to fast-forward-only or explicitly protected workflows. It does not make PHMGA formal evidence selection-ready and does not close downstream Stage C/D, selected-backend, or final submission-validator blockers.
