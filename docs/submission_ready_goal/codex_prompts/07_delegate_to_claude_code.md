# Codex Prompt 07 — Delegate a Bounded Task to Claude Code

Use this prompt only when a side task can be isolated from Codex's main `/goal` context.

## Codex responsibilities

Codex remains the owner of:

- FSM state;
- scorecards;
- checklist completion;
- PHMGA ledger/main-table trust;
- final submission-ready judgment.

Claude Code may produce an advisory handoff only.

## Delegation template

```text
Claude Code task:
<one bounded task>

Allowed files:
<exact files or directories>

Forbidden files:
- backend/graph/**
- obsidian/**
- web/dashboard/**
- PHMGA main tables unless explicitly read-only

Required output:
A handoff artifact following docs/submission_ready_goal/teammate_templates/claude_code_handoff_template.yaml.

Important:
Do not claim submission-ready. Do not update scorecards. Do not write positive paper claims. Return findings, gaps, risks, and one recommended next Codex action.
```

## Codex validation after receiving handoff

```bash
python tools/submission_ready_goal/validate_claude_handoff.py --handoff <handoff.yaml>
```

Codex may merge/use the handoff only if:

- validator exits 0;
- `status=pass`;
- `safe_to_merge=true`;
- blockers are empty;
- no forbidden file changed;
- no final submission-ready claim is made.
```
