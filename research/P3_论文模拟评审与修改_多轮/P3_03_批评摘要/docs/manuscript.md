# P3_03 Critique Digest

## Scope

This node converts the P3_01 review-round schema and the P3_02 reviewer-profile bundles into a compact critique digest. It does not rewrite the manuscript, apply P2_05 prose patches, draft P4 responses, or claim final submission readiness.

Inputs used:

- `research/P3_论文模拟评审与修改_多轮/P3_01_评审轮次/artifacts/review_round_index.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案/artifacts/reviewer_profile_map.yaml`
- `research/P3_论文模拟评审与修改_多轮/P3_02_评价者档案/artifacts/reviewer_lens_matrix.yaml`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/introduction.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/method.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/experiment.tex`
- `research/P2_论文撰写/P2_05_去AI味道/artifacts/academic_expression_claim_calibration.md`
- `docs/submission_ready_goal/completion_audit_current.md`

Protected paths were not read.

## Required Questions

Which critiques are the same root cause stated in different ways?

The recurring reviewer objections reduce to three blocking root causes: formal empirical evidence is not yet submission eligible, the reproducibility path is still blocked by PHMGA/Vibench state, and global submission validation still has pending P1 checklist fields, remaining below-threshold P3/P4 scores, and P3_04 blocked/planned action statuses. Comments about result strength, RM101, selected backend, variance, and Stage C/D rows all point to the first root cause. Comments about dirty submodule state, adapter preflight, model/provider metadata, and rerun inspectability point to the second. Comments about final validator failure, P3_04 action status, P4 coverage, and remaining review scores point to the third. Repaired schema and failure-truth issues are historical context only, not current emitted final-gate blockers.

Which problems should be fixed first?

The first repair should keep the manuscript conservative while routing the three blocking clusters into P3_04 revision actions. P3_04 can then decide whether each action routes to upstream evidence repair, manuscript downgrade, or explicit blocker retention. Non-blocking prose and figure-caption improvements should wait until the blocking evidence and reproducibility rows are either repaired or deliberately preserved as limitations.

Does `review_issue_register.yaml` retain source comment IDs, severity, affected claim, evidence gap, location, and next action?

Yes. The register records six atomic issues. Each row includes `source_comment_ids`, `severity`, `claim_or_section`, `claim_id`, `evidence_id`, `evidence_location`, `evidence_gap`, `location`, `required_action`, `target_node_or_artifact`, `validation_gate`, `blocks_submission`, and `next_action`. The three blocking rows are explicitly routed to P3_04 or upstream evidence artifacts; the non-blocking and cosmetic rows are kept separate so style comments do not hide evidence gaps.

## Digest Decision

P3_03 passes as a critique-aggregation node if independent review agrees that the issue register is specific, traceable, and action-ready. The paper itself remains not submission ready. The blocking issues are not solved here; they are preserved for P3_04 revision-action mapping and later P4 response evidence.

## Final-Threshold Score Boundary

This node is eligible only for a score-only final-threshold re-review of the critique digest and issue register package itself. The local claim is that P3_03 provides traceable critique clusters and atomic issue rows ready for P3_04 revision-action mapping. It does not rewrite P2 TeX, close P3_04 actions, verify upstream evidence as scientific support, close P1 checklist fields, complete P4 response coverage, run providers, or claim global submission readiness.

The node-local final-threshold contract is `artifacts/critique_digest_final_threshold_contract.yaml`. Any AI_002 verdict for this node must keep `checklist_status_closed: false`, `p3_04_actions_closed: false`, and `global_submission_ready: false` even if the node-local score reaches 90 or above.
