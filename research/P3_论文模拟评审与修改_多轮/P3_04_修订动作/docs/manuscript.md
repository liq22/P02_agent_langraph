# P3_04 Revision Action Map

## Scope

This node converts the P3_03 critique digest and review issue register into a concrete revision-action map. It does not apply manuscript edits, run PHMGA/Vibench experiments, repair P1/P2 evidence artifacts, draft P4 responses, or claim final submission readiness.

Inputs used:

- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/artifacts/review_issue_register.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/artifacts/critique_digest.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/artifacts/claim_evidence_registry.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_03_批评摘要/review/verdict.yaml`
- `research/P3_论文模拟评审与修改_多轮/prompts/standards.md`

Protected paths were not read.

## Required Questions

What is the smallest revision action for each critique?

The smallest actions are not manuscript rewrites. They are routing actions with validation gates. `issue-p3-001` requires a formal-evidence action that either repairs real-data/RM101/selected-backend/Stage C-D evidence or preserves the limitation. `issue-p3-002` requires a reproducibility action that targets PHMGA/Vibench dirty-state, adapter-preflight, selected-backend, and formal-ledger gaps. `issue-p3-003` requires a submission-gate action that keeps global validator and response-package gaps visible. `issue-p3-004` through `issue-p3-006` become non-blocking or cosmetic manuscript-action candidates guarded by a no-upgrade policy.

How will each modification be verified?

Each action in `artifacts/revision_action_map.yaml` has `expected_evidence`, `validation_gate`, `next_iteration_trigger`, closure evidence, and explicit user authorization. The original blocking actions are now `status: done` through retained-limitation closure; non-blocking and cosmetic actions are now `status: done` through applied or verified P4_06 evidence.

Does `revision_action_map.yaml` specify target phase, target node, action type, expected evidence, validation gate, and next iteration trigger for every blocking issue?

Yes. The three blocking actions all include `target_phase`, `target_node`, `action_type`, `expected_evidence`, `validation_gate`, `next_iteration_trigger`, `prerequisite_gap`, and `scheduler_dependency_closure_allowed: true`. The map does not pretend that blocked upstream targets are ready leaves.

## Current Decision

P3_04 is ready for node-local review when the action map is accepted as complete routing infrastructure. After explicit user authorization on 2026-05-06, the six mapped actions are closed as `done` against P4_05/P4_06 coverage, applied revision, verified no-op, or retained-limitation evidence.

## Final-Threshold Score Boundary

This node is eligible only for a score-only final-threshold re-review of the revision-action map as routing infrastructure. The local claim is that P3_04 maps all six P3_03 issues into actionable rows with target phase, target node, action type, expected evidence, validation gate, next-iteration trigger, prerequisite gap, source provenance, and no-final-readiness boundaries.

The original node-local review did not close the mapped actions. After package-level explicit approval, the canonical statuses in `artifacts/revision_action_map.yaml` are now `done` for `action-p3-001` through `action-p3-006`. This closure does not rewrite retained limitations into positive formal evidence and does not run providers.

The node-local final-threshold contract is `artifacts/revision_action_final_threshold_contract.yaml`. The later package-level closure supersedes the contract's pre-approval action-status boundary for final-validator purposes while preserving the no-overclaim evidence boundary.
