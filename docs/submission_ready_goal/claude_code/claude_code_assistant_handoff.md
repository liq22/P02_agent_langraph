# Claude Code Assistant Handoff Protocol v2

Claude Code may assist the P02 submission-ready workflow, but Codex remains the gate owner.

## Why v2

The v2 protocol prevents a common failure mode: a helper agent produces a convincing summary, Codex accepts it, and the paper advances without a script-backed artifact. Every handoff must now include a non-authority statement, explicit scope, commands/logs, evidence links, and a bounded next action.

## Allowed helper tasks

- Data package audit summary.
- PHMGA artifact/result-ledger traceability review.
- Claim-evidence consistency review.
- Schema/checklist consistency review.
- Independent hard-fail review.

## Disallowed helper tasks

- Final submission-ready declaration.
- Unbounded repository edits.
- Same-file parallel edits with Codex.
- Writing positive scientific result claims without artifact evidence.
- Updating PHMGA main tables using pending/fail/no_evidence rows.
- Using Vibench DataLoader/trainer/evaluator as formal P02 result truth.

## Required handoff artifact

Use:

```text
docs/submission_ready_goal/teammate_templates/claude_code_handoff_template.yaml
```

The handoff must validate with:

```bash
python tools/submission_ready_goal/validate_claude_handoff.py --handoff <handoff.yaml>
```

## Merge rule

Codex may merge or act on a Claude Code handoff only when:

- `status=pass`
- `safe_to_merge=true`
- no blockers exist
- validator exits `0`
- changed files are within allowed scope
- the handoff does not claim submission-ready

## Agent teams

Agent teams may be used only for parallel review/audit tasks. Each teammate must have a file-disjoint scope and must produce a separate v2 handoff. Codex synthesizes the handoffs after validation.


## Prior v2 notes retained

# Claude Code Assistant and Teammate Handoff Protocol

## Purpose

Claude Code can be used as an assistant inside the P02 submission-ready workflow. Its role is to reduce Codex context load and accelerate bounded auxiliary tasks, not to replace the P02 `/goal` gate.

Use Claude Code when the work is:

```text
small, bounded, file-scoped, auditable, and safe to summarize back to Codex
```

Do not use Claude Code for unbounded formal-paper decisions, final table selection, or final submission-ready claims.

## Recommended operating model

```text
Codex /goal = lead and gate owner
Claude Code = auxiliary assistant
Claude Code subagents = focused workers inside one Claude Code session
Claude Code agent teams = optional parallel review/exploration lane
Handoff artifacts = only accepted communication channel back into the P02 truth chain
```

## When to use Claude Code subagents

Use subagents for focused tasks whose output can be summarized compactly:

- scan PHMGA docs for missing evidence paths;
- check whether a YAML schema and checklist agree;
- review a single artifact bundle;
- draft a small node-local checklist;
- inspect one test failure and propose a fix;
- verify that a handoff file contains all required fields.

Subagents should usually be read-only for P02 unless a task explicitly permits writing.

## When to use Claude Code agent teams

Use agent teams only when parallel exploration adds value, for example:

- one teammate audits DATA_ROOT manifest/checksums;
- one teammate audits PHMGA result ledger/main tables;
- one teammate audits paper claim-evidence consistency;
- one teammate plays reviewer and tries to find hard fails.

Do not use agent teams for sequential edits to the same file. File conflicts are more expensive than any coordination benefit.

## Minimum teammate roles

| Role | Recommended mode | Owns | Must not do |
|---|---|---|---|
| `data-auditor` | read-only or plan-first | DATA_ROOT manifest, H5/metadata audit summaries | modify formal paper tables |
| `phmga-artifact-auditor` | read-only or plan-first | PHMGA artifact_dir/result_md/ledger traceability | change experiment rows without evidence |
| `paper-evidence-reviewer` | read-only | claim-evidence registry, figure/table traceability | invent evidence |
| `handoff-reviewer` | read-only | handoff completeness and blocker detection | approve final submission alone |

## Delegation rules

A delegated task must include:

```yaml
task_id: <unique_id>
assigned_to: claude_code | claude_code_team::<teammate>
scope: <files/directories allowed>
mode: read_only | plan_first | edit_allowed
allowed_files:
  - <path>
forbidden_files:
  - backend/graph/graph.json
  - backend/graph/graph_status.json
  - obsidian/**
  - web/dashboard/**
expected_outputs:
  - <handoff markdown or yaml>
stop_conditions:
  - missing required input
  - file conflict risk
  - uncertain evidence
  - task exceeds scope
```

## Handoff artifact format

Every Claude Code output must be written or pasted in this format:

```yaml
handoff_version: claude_code_handoff_v1
task_id: <task id>
assistant: claude_code
role: <data-auditor | artifact-auditor | reviewer | other>
mode: read_only | plan_first | edit_allowed
status: pass | revise | block | incomplete

scope:
  allowed_files: []
  inspected_files: []
  changed_files: []

commands_run:
  - command: <command>
    exit_code: <int or unknown>
    evidence_file: <path or null>

findings:
  supported:
    - claim: <claim>
      evidence: <path>
  gaps:
    - gap: <gap>
      severity: low | medium | high | hard_fail
  risks:
    - risk: <risk>
      mitigation: <mitigation>

artifacts_produced:
  - <path>

handoff_to_codex:
  summary: <short summary>
  blockers: []
  recommended_next_action: <one bounded next step>
  safe_to_merge: true | false
```

## File ownership policy

Claude Code teammates should own disjoint files. Recommended ownership:

```text
data-auditor:
  docs/submission_ready_goal/resource_pack/*
  generated data audit outputs

phmga-artifact-auditor:
  docs/submission_ready_goal/phmga_experiment_readiness.md
  PHMGA result audit notes

paper-evidence-reviewer:
  docs/submission_ready_goal/paper_evidence_readiness.md
  claim-evidence review notes

handoff-reviewer:
  docs/submission_ready_goal/claude_code/*
  handoff checklist results
```

## Approval policy

Use this progression:

1. Read-only Claude Code exploration.
2. Plan-first teammate work.
3. Edit-allowed only for small, file-disjoint docs/checklists/tests.
4. Codex synthesizes and runs gates.
5. Human reviews any final paper or formal experiment-table change.

## Hard fails

Claude Code handoff is invalid if:

- it does not list inspected files;
- it changes files outside assigned scope;
- it claims pass without commands or evidence;
- it promotes pending PHMGA rows into paper results;
- it uses Vibench trainer/sampler/evaluator as formal result truth;
- it declares final submission-ready without Codex final gate and `validate_research_truth.py`.

## Suggested Claude Code lead prompt

```text
You are Claude Code assisting the P02 submission-ready workflow.
Codex remains the lead and final gate owner.
Use subagents or teammates only for bounded auxiliary tasks.
Every result must be returned as a handoff artifact following docs/submission_ready_goal/schemas/claude_code_handoff.schema.yaml.
Do not claim submission-ready.
Do not edit graph files, Canvas files, dashboard files, or large data files.
Do not use Vibench trainer/sampler/evaluator as P02 formal result truth.
```
