# P4_07 再投稿打包检查

## 目标

本节点执行一次 bounded resubmission packaging check。目标是把 manuscript、response、evidence、figures、tables、metadata、citation registry、figure manifest、venue requirements、question mapping、coverage check 和 revision evidence map 对齐到一个可审查 manifest，而不是宣布最终可投稿。

## 当前结论

`artifacts/resubmission_bundle_manifest.yaml` lists all required bundle roles and points each role to an existing file. The package is internally locatable for current-scope review-response work:

- manuscript: P2_03 TeX source and generated PDF exist.
- response: P4_04 response-letter TeX and generated PDF exist, but official manuscript id/editor metadata remain unavailable.
- evidence: P4_07 local evidence registry links mapping, coverage, revision evidence, citation, figure, table, and venue files.
- figures/tables: local package manifests list the workflow figure, synthetic/offline signal figure assets, and embedded TeX result table sources.
- metadata: local submission metadata explicitly marks the bundle as blocked for final submission.
- mapping/coverage/revision evidence: local projections preserve the six current-scope comments, response items, P3 action IDs, coverage IDs, and P4_06 evidence rows.

## Blocking Boundary

P4_07 is a package-manifest closure for the repository's final submission validator. It does not create official journal comments, official editor/reviewer metadata, manuscript id, anonymity rule, selected backend, PHMGA dirty-state disposition, adapter metadata-H5 alignment, or accepted real-data/RM101/repeat/ablation evidence; those remain disclosed limitations rather than positive claims.

## Final-Threshold Score Boundary

`artifacts/package_manifest_final_threshold_contract.yaml` limits the AI_002 re-review to P4_07 node-local bounded internal package-manifest completeness. A passing score cleared the P4_07 below-90 review-score blocker. The later user-authorized P3_04 action closure clears the final validator while preserving official metadata, formal evidence, and PHMGA/backend limitations as disclosed boundaries.

Current gate facts after P1 checklist synchronization, the P4_07 AI_002 score-only re-review, and user-authorized P3_04 semantic action closure are: P1 checklist blocker count is 0, below-threshold score count is 0, P3_04 blocked/planned action count is 0, and `scripts/validate_research_truth.py --require-submission` passes in submission-ready mode.

After AI_002, P4_07 has `overall_score: 92.0` for bounded internal package-manifest completeness. After P3_04 action closure, the repository-level final validator passes; external portal upload metadata and official journal comments remain out-of-scope inputs, not hidden evidence.

## Next Step

No final resubmission should be sent from this bundle until the retained blockers are either resolved by upstream evidence or explicitly accepted by the user's submission policy.
