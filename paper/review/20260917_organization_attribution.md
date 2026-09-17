# Adversarial review — organization with fixed instructions

## Scientific decision and prior work

The original factorial separates a label-plus-instruction cue from a mask; it does not separate organizing advice from supplying it. Retain that experiment. The new fixed-bank comparison supplies the same six original instructions once, in the same order, and varies only a current-stage name and the existing mask. It changes no PHMskills content or retrieval rule.

StateFlow v5, Sections 3.1 and 4.1 and the state-ablation paragraph, already uses state-dependent instructions, refined ReAct and state removals. Refined ReAct follows an intended workflow without the full controller, and the paper discusses prompt length as a cost factor. This is a direct precedent, not a missing baseline to infer from its abstract. Source: https://arxiv.org/html/2403.11322v5 .

PHMForge v3, Section 3.4 and Appendix H, already studies verification, distractors and data discovery. Its scores are not same-protocol results here. Source: https://arxiv.org/html/2604.01532v3 . The present gap is specific to this PHM comparison; no universal absence-of-prior-work or first-state-machine claim is supported.

## Theory and interpretation checks

The existing theory07 now proves a policy-class consequence: with full retained public history, fixed initialization and deterministic annotation, an unrestricted history-conditioned rule can compute that annotation. Composition gives equal unrestricted optima with/without annotation; masking restricts the policy class. This is elementary specialization, not a new general theorem. It predicts neither the computation nor the token/latency cost of a frozen finite language model. Additional hidden-target information, missing event history or truncation would require a different premise.

Matching the instruction inventory is not matching prompt length. Correct annotation versus added-line salience/token cost remains unseparated. Masks may disclose phase implicitly. The estimands therefore concern implemented interfaces, not pure topology, latent mask regret or persistent-memory efficacy. Base memory/replanning remain negative controls under the existing event-free proof.

## Actual validation

Benchmark `cafc2885723c9f956ed8af69bd74e62db9e6b201` adds four conditions, eight within-profile contrasts and a plan-first YAML through the existing factory/entry/scorer. Original Graph/factorial/cardinality wording is preserved. No K code, Runner, task metric, data protocol or Factory pointer changed in this slice.

First installed run **35214535666**: 144 tests, four errors in the concurrent K-request fixture; all eight new Graph checks passed. That fixture was repaired by independent work. Later run **35214966018**, head **0ba1121**, job **105181159405**: **144 research tests in 19.104 s** and **33 production-boundary tests in 0.047 s**, all passed. The downloaded source matches the Graph patch exactly. Both failure and success logs are retained. These totals include existing/concurrent tests, not 177 new Graph tests.

The eight additions check the common bank, annotation/mask independence, history sanitation, exact old wording, inherited response handling, contrast algebra and actual `main.py --config` plan. Twenty-four input rows contain six guide entries each; annotation-off system text has 684 characters, annotation-on 716–722. Characters are not tokens. One test supplies deterministic responses; real model API calls and new real PHM episodes are both zero. No old toy was rerun, no fixture-count performance plot was produced, and all existing manuscript Results paragraphs were preserved byte-for-byte.

A later independent shared-reference change expanded production checks. After CI commit `c4aaee9` aligned all steps to the project virtual environment, run **35215969880** passed **153 research tests**, including the same eight Graph tests, but only **52/53 production checks**. The remaining check reaches `PHMDataRepository.from_local` and fails because `/mnt/e/D01_vibench/metadata.xlsx` is absent. This is a retained real-data blocker, not a green full integration result. No test was skipped, no assertion weakened, and no replacement sensor data supplied. The 144/33 success above remains scoped to its earlier snapshot.

## Claim and next gate

Interface construction and native dispatch are verified; diagnostic benefit is undecided. A positive old cue-package effect does not establish a fixed-bank annotation effect. Negative or null new effects must remain. No long-horizon or reliability improvement follows from this slice.

The narrow migration gate is the existing provider-free real Paderborn development smoke, not a new API/GPU/checkpoint requirement. Scientific efficacy separately needs an approved endpoint and matched assignments. Execution instructions remain only in Benchmark `paper/goals/P02_MATCHED_CONTROL.md`. Actual effects belong in P02 Results 7.4 before Paper 0 synthesis. Do not expand the runtime or repeat completed toys in place of the unavailable resources.
