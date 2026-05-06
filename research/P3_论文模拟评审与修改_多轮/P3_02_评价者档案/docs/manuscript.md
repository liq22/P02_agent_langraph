# P3_02 Reviewer Profile Package

## Scope

This node materializes reviewer profiles for `p3-round-001` from the P3_01 review-round definition. It does not generate critique text, rewrite the manuscript, or claim submission readiness. Its job is to define adversarial reviewer lenses that downstream P3_03 and P3_04 can use to produce issue rows and revision actions.

## Reviewer Coverage

The package covers six reviewer perspectives: editor-in-chief, method expert, domain expert, cross-disciplinary reader, reproducibility skeptic, and devil's advocate. These six lenses are grouped into three downstream profile bundles: method and reproducibility, empirical and statistics, and venue/claim clarity. Each lens has a domain, method/statistical stance, writing preference, primary attack surface, required evidence, and hard-fail conditions.

## Attack Surface

The reviewers are designed to attack the current manuscript's known weak points: preliminary synthetic/offline evidence, missing formal real-data rows, RM101 unresolved reject evidence, selected-backend uncertainty, Stage C/D incompleteness, PHMGA dirty-state protection, claim/evidence registry schema gaps, low final-review scores, and the risk that P2_05 prose calibration could be applied without TeX sync and formal checks.

## Evidence Boundary

The profiles cite the P3_01 round index, P2_03 TeX snapshot, P2_05 calibration artifact, P2_04 formal check report, and completion audit as planning evidence. They do not convert those sources into positive scientific results. Negative and blocked evidence remains part of the review surface.

## Final-Threshold Score Boundary

This node is eligible only for a score-only final-threshold re-review of the reviewer-profile package itself. The local claim is that P3_02 provides a complete, evidence-bound, six-lens reviewer profile surface for P3_03 critique synthesis and P3_04 revision-action mapping. It does not instantiate atomic issue rows, verify upstream evidence as scientific support, rewrite the manuscript, close P1 checklist fields, close P3_04 actions, run providers, or claim global submission readiness.

The node-local final-threshold contract is `artifacts/reviewer_profile_final_threshold_contract.yaml`. Any AI_002 verdict for this node must keep `checklist_status_closed: false`, `p3_04_actions_closed: false`, and `global_submission_ready: false` even if the node-local score reaches 90 or above.

## Current Decision

P3_02 is complete when the reviewer profile map, reviewer lens matrix, session manifest, required evidence-retention artifacts, and final-threshold boundary contract exist and pass review. The next P3 nodes should use these profiles to generate concrete critique summaries and revision actions, not to bypass the unresolved global blockers. Before the requested AI_002 re-review, the global gate still preserves 109 pending P1 checklist fields, 10 below-threshold score nodes including P3_02, 6 blocked or planned P3_04 actions, unexecuted formal provider runs, selected-backend and RM101 real-data evidence gaps, and adapter preflight plus Stage C/D incompleteness.
