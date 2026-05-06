# P3_01 Review Round Definition

## Scope

This node defines the first simulated review round for the current manuscript package. It does not rewrite P2 text, edit TeX, adjudicate reviewer responses, or claim final submission readiness. Its output is a bounded review-round plan that downstream P3 nodes can use to generate critique summaries and revision actions.

## Manuscript Snapshot

The round reviews `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex` as the current export snapshot after P2 section closures. The snapshot contains title, abstract, introduction, preliminaries, methods, results, discussion, data availability, code availability, and references. It carries only a preliminary synthetic/offline single-run quantitative signal. P2_05 produced a patch-ready academic-expression calibration packet, but those prose patches have not yet been applied to the TeX snapshot.

## Round Identity

The active round is `p3-round-001`. It simulates adversarial external reviewers whose job is to map blockers, not to perform author defense or manuscript rewriting. The round decision is `blocker_mapping_only`: every fatal or major concern must become a specific issue with evidence location, affected claim or manuscript section, severity, and proposed next action.

## Reviewer Lenses

The first lens is a method and reproducibility reviewer. This reviewer checks whether node-level governance, data/code/protocol availability, PHMGA/Vibench boundaries, evidence registries, review gates, and result ledgers are sufficient for external audit. It focuses on methods, reproducibility, evidence eligibility, and stop conditions.

The second lens is an empirical and statistics reviewer. This reviewer checks whether result claims are supported by baselines, uncertainty, repeatability, negative evidence, and formal eligibility gates. It focuses on the preliminary synthetic/offline signal, missing real-data rows, RM101, selected backend, Stage C/D rows, and final-review score thresholds.

The third lens is a venue and claim-clarity reviewer. This reviewer checks whether the title, abstract, contribution thesis, figure/table callouts, citations, AI/agent disclosure, and limitation language match the selected Elsevier/IEEE-style profile without overclaiming.

## Output Format For This Round

Each reviewer issue should use the same fields: `issue_id`, `lens_id`, `severity`, `claim_or_section`, `evidence_location`, `problem`, `required_action`, `target_node_or_artifact`, `validation_gate`, and `blocks_submission`. Fatal and major issues must include a concrete evidence location and proposed action. Minor clarity comments may be recorded only if they do not obscure unresolved hard blockers.

## Stop Conditions

Stop the round if the manuscript snapshot is missing, if a reviewer lens lacks a declared checklist dimension, if critique cannot be mapped to an evidence location or target action, or if the round starts rewriting P2 or P4 content. Stop also if final submission readiness is inferred from node-local pass reviews below the 90-point final threshold.

## Final-Threshold Score Boundary

This node is eligible only for a score-only final-threshold re-review of the review-round definition itself. The local claim is that P3_01 provides a complete and bounded round definition for downstream issue/action mapping: it names the manuscript snapshot, required TeX section inputs, reviewer lenses, issue fields, stop conditions, and the no-submission-ready boundary. It does not claim that the manuscript is ready for submission, that formal provider runs or real-data evidence are complete, that P1 checklist fields are closed, or that P3_04 revision actions are done.

The node-local final-threshold contract is `artifacts/review_round_final_threshold_contract.yaml`. Any AI_002 verdict for this node must keep `checklist_status_closed: false` and `global_submission_ready: false` even if the node-local score reaches 90 or above.

## Current Decision

This round should not produce a pass verdict for submission readiness. Before the requested AI_002 re-review, the global gate still preserves 109 pending P1 checklist fields, 11 below-threshold score nodes across P3/P4 including this node, 6 blocked or planned P3_04 actions, unexecuted formal provider runs, selected-backend and RM101 real-data evidence gaps, and adapter preflight plus Stage C/D incompleteness. If P3_01 clears the node-local 90-point threshold, the remaining score blockers move downstream to P3_02-P3_04 and P4_01-P4_07; the other global blockers remain outside this node's authority.
