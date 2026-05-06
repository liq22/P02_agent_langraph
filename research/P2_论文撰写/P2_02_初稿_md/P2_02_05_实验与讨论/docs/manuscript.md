# Experiments and Discussion

## Evidence-Maturity Order

The results are reported by evidence maturity rather than by narrative attractiveness. The only positive observation available at this stage is a bounded synthetic/offline sanity check from the P1_04/P1_05 lightweight validation. Formal PHMGA/Vibench evidence is not yet table-eligible because selected backend, sample-level metadata-H5 alignment, Stage C main rows, Stage D ablations, repeat counts, result-ledger rows, and main-table mappings remain incomplete. The primary manuscript outcome therefore cannot be a performance-improvement claim; the primary result for this draft is an evidence-governance finding: the workflow keeps supported-limited, unsupported, unclear, rejected, and blocked evidence in separate rows before interpretation. The secondary supporting outcomes are the bounded synthetic/offline signal, the blocked formal-eligibility gate, and the retained negative/unclear evidence ledger.

The reporting order follows this rule. First, the section states the limited synthetic/offline signal and its boundary. Second, it reports the formal-eligibility gate as blocked rather than absent. Third, it retains unsupported and unclear evidence in the denominator. Fourth, it discusses what the current signal may suggest, what it cannot show, and what evidence would be required to upgrade claims.

## Limited Synthetic/Offline Sanity Check

In the P1_04 bounded offline synthetic Ottawa check, the `supervisor_proving` controlled attempt reached test accuracy 1.0 and test macro-F1 1.0, while the `simple_fullchain` baseline reached test accuracy 0.8333333333333334 and test macro-F1 0.8285714285714285. The observed deltas are +0.16666666666666663 in test accuracy and +0.17142857142857149 in macro-F1. The split is intentionally small: four synthetic sample IDs are used for training, two for validation, and two for testing before windowing, so the perfect test score is ceiling-sensitive and cannot carry a broad performance interpretation. This is a weak, supported-limited signal that the supervisor/proving path is worth carrying forward as a candidate mechanism.

The result is not a formal performance claim. It is single-run, synthetic, offline, Ottawa-only, and generated with an offline stub mode. It does not establish selected-backend success, real-data generalization, RM101 resolution, Stage C completion, Stage D completion, variance stability, or submission readiness. In table form, this row belongs in a limited sanity-check slot with its claim boundary visible beside the metric values.

## Formal Eligibility Gate and Blocked Rows

Formal PHMGA/Vibench result rows remain blocked. A row is not eligible for positive interpretation until provider policy, metadata-H5 alignment, artifact contract, selected backend, Stage C main rows, Stage D ablations, repeat count, result markdown, artifact directory, ledger row, and main-table mapping all pass. OpenRouter use is restricted to free models, BigModel use is restricted to the free GLM-4.7-flash lane, and provider credentials are excluded from research artifacts.

The current package therefore treats formal result tables as planned gate tables, not as success tables. Missing or rejected RM101 rows remain reject evidence or limitation rows. Missing Stage C and Stage D rows remain blockers. The dirty PHMGA submodule state also remains a reproducibility boundary until local dirty or untracked entries are protected or resolved before any future parent pointer update.

## Negative, Unsupported, and Unclear Evidence

The unsupported result is real-data generalization: the available P1_04 ledger contains no real-data repeated-run row. The second unsupported result is RM101 resolution: the lightweight evidence uses synthetic Ottawa data and does not address RM101 Stage B reject evidence. The unclear result is stability: the ledger has one baseline row and one controlled attempt row, so repeat-run variance and harder-split behavior remain unknown. The perfect synthetic score is also unclear as a broad signal because it may reflect an easy synthetic fixture.

These rows are part of the evidence package. They are not removed from the denominator, hidden in prose, or rewritten as support. Their table roles are limitation, reject evidence, or blocker, and each row requires a source artifact, affected claim, support status, boundary label, retained location, and downgrade action.

## Discussion

The finding is narrow but useful. The current evidence suggests that the supervisor/proving workflow path can produce a cleaner outcome than the simple baseline in a controlled synthetic/offline Ottawa fixture. The interpretation is not that the method improves PHMGA performance. The interpretation is that the candidate path is worth preserving for formal evaluation because it survived a bounded sanity check while remaining auditable through result, claim, and limitation records.

The main scientific value of this draft stage is the evidence discipline around the result, not the magnitude of the synthetic score. A conventional results narrative could overpromote the 1.0 synthetic score. The evidence-governed narrative instead records the score, binds it to its source ledger, labels it weak for submission-facing claims, and keeps the missing real-data, RM101, Stage C, Stage D, repeat, uncertainty, and selected-backend evidence visible.

The limitations are therefore central to the result. The current data do not support real-data generalization, stable performance under repeated runs, RM101 resolution, formal Stage C or Stage D success, or a selected backend. The future upgrade path is explicit: pass the PHMGA/Vibench adapter preflight, lock the selected backend, run the preregistered formal rows with repeats, produce result ledgers and artifact directories, preserve failed rows, and map each eligible row back to claim and evidence identifiers before strengthening the manuscript wording.

## Local Evidence Boundary

This node reports an experiments/discussion draft and claim-result mapping only. It does not resolve final-score thresholds, global schema blockers outside this node, missing P1_05 failure-truth artifacts, PHMGA dirty-worktree protection, selected-backend lock, RM101 reject evidence, Stage C rows, Stage D ablations, P3/P4 response-package gaps, or final submission readiness.
