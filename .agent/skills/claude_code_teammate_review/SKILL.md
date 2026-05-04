---
name: claude-code-teammate-review
description: Use when a node review gate requires a user-authorized Claude Code teammate delegate, especially when `review/人类_001.md` or a teammate handoff is needed. Calls Claude Code with a project-local teammate agent, requires a v2 handoff, and leaves Codex as final gate owner.
---

# Claude Code Teammate Review

Use this skill when the user explicitly authorizes Claude Code teammates to satisfy a review slot or when a selected node has a prepared Claude teammate prompt.

## Preconditions

- The user has explicitly delegated the review to Claude Code teammates.
- A node-local prompt such as `review/human_reviewer_prompt.md` exists.
- Codex remains the final gate owner.
- The teammate must not claim final submission-ready.

## P1_01 Default Teammate

For P1_01 human-review-slot delegation, use:

```bash
claude -p --agent p1-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-01-human-reviewer.md. Complete the P1_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_01_human_review_handoff.yaml`

## P1_02 Default Teammate

For P1_02 human-review-slot delegation, use only after explicit user approval to send the P1_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-02-human-reviewer.md. Complete the P1_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_02_伪代码/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_02_human_review_handoff.yaml`

## Required Validation

Run after Claude returns:

```bash
python tools/submission_ready_goal/validate_claude_handoff.py --handoff docs/submission_ready_goal/runtime_logs/claude_code/p1_01_human_review_handoff.yaml
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-review --json
python tools/submission_ready_goal/validate_goal_fsm_state.py --state docs/submission_ready_goal/fsm/current_goal_state.yaml
```

## Acceptance Rules

Accept the teammate output only if:

- the Claude handoff validates;
- changed files are inside the allowed scope;
- `review/人类_001.md` is explicit that the review was delegated to a Claude Code teammate;
- no placeholder markers remain in review outputs;
- the node package review validator passes;
- Codex performs the final status, graph refresh, and scheduling decision.

## Boundaries

- Do not use this skill without user delegation.
- Do not let Claude edit graph, Canvas, dashboard, PHMGA experiment truth, or broad manuscript files.
- Do not let Claude declare final submission-ready.
- Do not hide that the human-review slot was delegated to a Claude Code teammate.
