# Final Submission Gate

## Gate order

```text
Data-ready → Project-ready → Paper-ready → final submission check
```

## Required final command

From the root of `P02_agent_langraph`:

```bash
python scripts/validate_research_truth.py --require-submission
```

Expected success line:

```text
research truth: pass mode=submission-ready
```

## Final hard failures

- DATA_ROOT not recorded.
- canonical metadata missing.
- formal H5 files missing.
- Vibench read bundle missing.
- PHMGA submodule commit missing.
- PHMGA main tables empty.
- `selected_global_best_backend` pending.
- pending/fail/no-evidence rows used in paper tables.
- claim without evidence ID.
- final TeX missing.
- final submission check failed.


## Optional assistant-handoff gate

If Claude Code, subagents, or teammates contributed to the work, every contribution must have a valid handoff artifact and pass:

```text
docs/submission_ready_goal/checklists/06_claude_code_handoff_checklist.yaml
```

Claude Code handoffs are optional when Claude Code is not used. They are mandatory for any delegated assistant work that is merged into the submission-ready chain.

Assistant handoff hard failures:

- Claude Code claims final submission-ready.
- A teammate changes files outside assigned scope.
- A handoff promotes pending PHMGA rows into paper results.
- A handoff lacks inspected files or evidence.
