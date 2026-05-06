# Contribution Attack Boundary Refinement

generated_at: 2026-05-05

## Purpose

This artifact addresses P0_03 final-threshold strengthening notes without changing the proposal-stage evidence boundary. It adds reviewer-attack and falsification boundaries for each research content unit.

## Attack Matrix

| Content Unit | Reviewer Attack | Falsification Or Downgrade |
| --- | --- | --- |
| RC1 node-level evidence governance contract | Node closure may still be decided by file presence, successful execution, or author exit rather than reviewer-visible claim/evidence/review/response state. | If claim validity and unsupported-claim count do not improve against baselines, RC1 remains a governance design rather than proven quality improvement. |
| RC2 cross-phase claim-evidence-protocol chain | Claims may be locally coherent in P0, P1, P2, P3, or P4 while losing identity across phase boundaries. | If claim IDs, evidence IDs, review issues, responses, and revisions cannot be traced end to end, RC2 is only a traceability scaffold. |
| RC3 independent review and negative-result gate | Independent review may become formal bookkeeping, allowing hard fails, low scores, or reject evidence to disappear after node close. | If hard-fail closure does not improve or negative evidence retention drops, RC3 does not support a scientific contribution. |
| RC4 formal evidence eligibility gate | PHMGA/Vibench execution success may be mistaken for a new algorithmic contribution or main-result evidence. | If provider policy, adapter alignment, artifact contract, Stage C/D rows, and selected-backend lock are incomplete, RC4 can only report blocker or reject evidence. |

## Boundary Clarifications

- RC1 governs node close conditions.
- RC2 governs cross-phase claim identity.
- RC3 governs independent review and retained negative evidence as phase-transition requirements.
- RC4 governs eligibility of result evidence and is not a PHMGA/Vibench algorithm contribution.

## Current Evidence State

All four contributions remain proposal-stage candidate contributions. Stronger wording requires fixed-node baselines, claim-evidence audits, response coverage audits, negative-result retention evidence, PHMGA/Vibench preflight closure, formal Stage C/D rows, selected-backend lock, and distinct re-review.
