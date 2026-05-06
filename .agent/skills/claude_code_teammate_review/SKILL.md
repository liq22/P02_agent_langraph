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

## Standing Authorization

If the current conversation contains a user statement granting ongoing approval for similar Claude Code teammate reviews, treat that as authorization for the same class of node-local review-packet delegation. Continue to enforce the node's allowed read/write set, keep Codex as final gate owner, and write the required handoff.

This standing approval does not authorize unrelated provider execution, secret reads, closing P1 checklist fields, closing P3_04 actions, or claiming global submission readiness. Those actions still require their specific package-level approval text when applicable.

## P1_01 Default Teammate

For P1_01 human-review-slot delegation, use:

```bash
claude -p --agent p1-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-01-human-reviewer.md. Complete the P1_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_01_human_review_handoff.yaml`

## P0_01 Default Teammate

For P0_01 human-review-slot delegation, use only after explicit user approval to send the P0_01 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p0-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p0-01-human-reviewer.md. Complete the P0_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P0_项目申请书/P0_01_研究背景与调研/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_01_human_review_handoff.yaml`

## P0_02 Default Teammate

For P0_02 human-review-slot delegation, use only after explicit user approval to send the P0_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p0-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p0-02-human-reviewer.md. Complete the P0_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P0_项目申请书/P0_02_研究挑战与科学问题_工程问题/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_02_human_review_handoff.yaml`

## P0_03 Default Teammate

For P0_03 human-review-slot delegation, use only after explicit user approval to send the P0_03 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p0-03-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p0-03-human-reviewer.md. Complete the P0_03 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P0_项目申请书/P0_03_研究内容与创新点/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_03_human_review_handoff.yaml`

## P0_04 Default Teammate

For P0_04 human-review-slot delegation, use only after explicit user approval to send the P0_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p0-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p0-04-human-reviewer.md. Complete the P0_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P0_项目申请书/P0_04_技术路线_研究计划_OKR/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_04_human_review_handoff.yaml`

## P0_05 Default Teammate

For P0_05 human-review-slot delegation, use only after explicit user approval to send the P0_05 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p0-05-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p0-05-human-reviewer.md. Complete the P0_05 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P0_项目申请书/P0_05_项目约束_资源预算_风险边界/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p0_05_human_review_handoff.yaml`

## P1_02 Default Teammate

For P1_02 human-review-slot delegation, use only after explicit user approval to send the P1_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-02-human-reviewer.md. Complete the P1_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_02_伪代码/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_02_human_review_handoff.yaml`

## P1_03 Default Teammate

For P1_03 human-review-slot delegation, use only after explicit user approval to send the P1_03 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-03-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-03-human-reviewer.md. Complete the P1_03 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_03_仓库蓝图/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_03_human_review_handoff.yaml`

## P1_04 Default Teammate

For P1_04 human-review-slot delegation, use only after explicit user approval to send the P1_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-04-human-reviewer.md. Complete the P1_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_04_human_review_handoff.yaml`

## P1_05 Default Teammate

For P1_05 human-review-slot delegation, use only after explicit user approval to send the P1_05 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-05-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-05-human-reviewer.md. Complete the P1_05 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_05_初步验证结果整理/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_05_human_review_handoff.yaml`

## P1_06 Default Teammate

For P1_06 human-review-slot delegation, use only after explicit user approval to send the P1_06 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-06-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-06-human-reviewer.md. Complete the P1_06 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_06_human_review_handoff.yaml`

## P1_07 Default Teammate

For P1_07 human-review-slot delegation, use only after explicit user approval to send the P1_07 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-07-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-07-human-reviewer.md. Complete the P1_07 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_07_优化目标_任务_评测协议/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_07_human_review_handoff.yaml`

## P1_08 Default Teammate

For P1_08 human-review-slot delegation, use only after explicit user approval to send the P1_08 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-08-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p1-08-human-reviewer.md. Complete the P1_08 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_08_预期结果与表格/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_08_human_review_handoff.yaml`

## P1_09 Default Teammate

For P1_09 human-review-slot delegation, use only after explicit user approval to send the P1_09 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p1-09-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash "Follow .claude/agents/p1-09-human-reviewer.md. Complete the P1_09 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p1_09_human_review_handoff.yaml`

## P2_01 Default Teammate

For P2_01 human-review-slot delegation, use only after explicit user approval to send the P2_01 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-01-human-reviewer.md. Complete the P2_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_01_human_review_handoff.yaml`

## P2_02_01 Default Teammate

For P2_02_01 human-review-slot delegation, use only after explicit user approval to send the P2_02_01 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-02-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-02-01-human-reviewer.md. Complete the P2_02_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_02_初稿_md/P2_02_01_引言/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_02_01_human_review_handoff.yaml`

## P2_02_02 Default Teammate

For P2_02_02 human-review-slot delegation, use only after explicit user approval to send the P2_02_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-02-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-02-02-human-reviewer.md. Complete the P2_02_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_02_初稿_md/P2_02_02_preliminary/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_02_02_human_review_handoff.yaml`

## P2_02_03 Default Teammate

For P2_02_03 human-review-slot delegation, use only after explicit user approval to send the P2_02_03 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-02-03-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-02-03-human-reviewer.md. Complete the P2_02_03 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_02_初稿_md/P2_02_03_流程图草稿/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_02_03_human_review_handoff.yaml`

## P2_02_04 Default Teammate

For P2_02_04 human-review-slot delegation, use only after explicit user approval to send the P2_02_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-02-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-02-04-human-reviewer.md. Complete the P2_02_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_02_初稿_md/P2_02_04_方法/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_02_04_human_review_handoff.yaml`

## P2_02_05 Default Teammate

For P2_02_05 human-review-slot delegation, use only after explicit user approval to send the P2_02_05 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-02-05-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-02-05-human-reviewer.md. Complete the P2_02_05 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_02_05_human_review_handoff.yaml`

## P2_04 Default Teammate

For P2_04 human-review-slot delegation, use only after explicit user approval to send the P2_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-04-human-reviewer.md. Complete the P2_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_04_形式检查/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_04_human_review_handoff.yaml`

## P2_05 Default Teammate

For P2_05 human-review-slot delegation, use after user authorization to send the P2_05 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p2-05-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p2-05-human-reviewer.md. Complete the P2_05 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P2_论文撰写/P2_05_去AI味道/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p2_05_human_review_handoff.yaml`

## P3_01 Default Teammate

For P3_01 human-review-slot delegation, use after user authorization to send the P3_01 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p3-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p3-01-human-reviewer.md. Complete the P3_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P3_论文模拟评审与修改_多轮/P3_01_评审轮次/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p3_01_human_review_handoff.yaml`

## P3_02 Default Teammate

For P3_02 human-review-slot delegation, use after user authorization to send the P3_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p3-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p3-02-human-reviewer.md. Complete the P3_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p3_02_human_review_handoff.yaml`

## P3_03 Default Teammate

For P3_03 human-review-slot delegation, use after user authorization to send the P3_03 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p3-03-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p3-03-human-reviewer.md. Complete the P3_03 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p3_03_human_review_handoff.yaml`

## P3_04 Default Teammate

For P3_04 human-review-slot delegation, use after user authorization to send the P3_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p3-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p3-04-human-reviewer.md. Complete the P3_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P3_论文模拟评审与修改_多轮/P3_04_修订动作/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p3_04_human_review_handoff.yaml`

## P4_04 Default Teammate

For P4_04 human-review-slot delegation, use after user authorization to send the P4_04 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-04-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-04-human-reviewer.md. Complete the P4_04 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_04_正式回复_tex_或_doc/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_04_human_review_handoff.yaml`

## P4_01 Default Teammate

For P4_01 human-review-slot delegation, use after user authorization to send the P4_01 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-01-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-01-human-reviewer.md. Complete the P4_01 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_01_审稿意见收集/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_01_human_review_handoff.yaml`

## P4_02 Default Teammate

For P4_02 human-review-slot delegation, use after user authorization to send the P4_02 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-02-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-02-human-reviewer.md. Complete the P4_02 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_02_问题映射矩阵/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_02_human_review_handoff.yaml`

## P4_03 Default Teammate

For P4_03 human-review-slot delegation, use after user authorization to send the P4_03 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-03-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-03-human-reviewer.md. Complete the P4_03 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_03_逐点回复草稿_md/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_03_human_review_handoff.yaml`

## P4_05 Default Teammate

For P4_05 human-review-slot delegation, use after user authorization to send the P4_05 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-05-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-05-human-reviewer.md. Complete the P4_05 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_05_覆盖检查/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_05_human_review_handoff.yaml`

## P4_06 Default Teammate

For P4_06 human-review-slot delegation, use after user authorization to send the P4_06 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-06-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-06-human-reviewer.md. Complete the P4_06 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_06_修改证据/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_06_human_review_handoff.yaml`

## P4_07 Default Teammate

For P4_07 human-review-slot delegation, use after user authorization to send the P4_07 review packet to Claude Code/Anthropic:

```bash
claude -p --agent p4-07-human-reviewer --permission-mode acceptEdits --allowedTools Read,Grep,Glob,Edit,Bash -- "Follow .claude/agents/p4-07-human-reviewer.md. Complete the P4_07 user-authorized Claude Code teammate review. Edit only the allowed files and write the required handoff."
```

Expected changed files:

- `research/P4_论文回复_response/P4_07_再投稿打包/review/人类_001.md`
- `docs/submission_ready_goal/runtime_logs/claude_code/p4_07_human_review_handoff.yaml`

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
