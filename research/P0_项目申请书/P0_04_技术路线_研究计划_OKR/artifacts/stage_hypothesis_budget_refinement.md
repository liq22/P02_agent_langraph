# Stage Hypothesis And Budget Refinement

generated_at: 2026-05-05

## Purpose

This artifact strengthens the P0_04 route by making the stage-to-hypothesis mapping and fixed-budget planning boundary explicit. It is a proposal-stage route refinement and does not claim downstream preflight, selected-backend, formal-row, or final-validator closure.

## Stage-To-Hypothesis Map

| Stage | H1 Claim Validity | H2 Review/Negative Evidence | H3 Formal Evidence Eligibility |
| --- | --- | --- | --- |
| Stage 0 problem/contribution lock | fixes contribution definitions and downgrade rules | fixes reviewer-attack boundaries | records that formal evidence is downstream |
| Stage 1 protocol/data eligibility | fixes node set, baselines, budget, and metrics | fixes review-rubric inputs | fixes provider policy, adapter preflight, artifact contract, and eligibility criteria |
| Stage 2 evidence production | measures claim validity and unsupported claims | measures response coverage, hard-fail closure, and negative-result retention | produces or rejects Stage C/D formal rows under eligibility gates |
| Stage 3 manuscript integration | admits only registry-backed claims | preserves limitations and negative evidence in text | blocks ineligible result claims from figures/tables |
| Stage 4 independent review/response | detects unsupported claims through reviewer attack | directly tests review closure and response coverage | blocks final readiness when formal evidence remains ineligible |

## Fixed-Budget Planning Table

| Planning Item | Current Proposal-Stage Constraint | Final-Submission Requirement |
| --- | --- | --- |
| Node set | fixed P0-P4 leaf-node workflow | exact node list and inclusion/exclusion record locked before interpretation |
| Baselines | manual checklist, prompt-only agent, ungated multi-agent workflow, AutoResearch gated workflow | comparable budget and reviewer rubric across all conditions |
| Provider/model allowance | OpenRouter free models only; BigModel GLM-4.7-flash free only | command/config logs prove the allowed model policy was followed without exposing secrets |
| Dataset/provenance | Vibench/PHMGA adapter and artifact-contract gates | sample-level metadata-H5 alignment, artifact contract, and selected backend locked |
| Formal evidence rows | Stage C main rows and Stage D ablation rows required before strong claims | accepted rows in ledger with reject/unclear evidence retained |
| Review rounds | distinct independent review before score-threshold updates | final-threshold re-review after evidence and validator closure |

## Guardrail

Provider/model policy statements are planning constraints until downstream preflight or formal-run evidence verifies them. Final submission readiness remains blocked while adapter preflight, selected backend, formal Stage C/D rows, P3 action statuses, review scores, or the final validator remain unresolved.

## Route-Readiness Clarification

`artifacts/route_readiness_contract.yaml` defines the P0_04 node-specific threshold. P0_04 should be judged on whether the route locks stage owners, metrics, evidence rows, stop conditions, fallback branches, and no-overclaim boundaries. Missing provider/formal rows, selected-backend lock, P3/P4 closure, and final-validator pass remain downstream blockers for global submission readiness; they are not evidence against P0_04 if the route preserves them as blockers instead of using them as support.
