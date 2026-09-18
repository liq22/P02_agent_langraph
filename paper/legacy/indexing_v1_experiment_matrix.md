# PHMGraph: sequential simple effects and evidence requirements

Implementation, canonical records, fitting, scoring and analysis belong to `liq22/phm-agent-benchmark`. This file specifies the experiment; it is not another runner or result authority. The inspected snapshot is `8206cfef540d5f602adba482e9dcc0ebd6b0f437` in Draft PR #20. Its active entry is `configs/paper02_graph/indexing_first_attempt.yaml`, with `paper/goals/P02_MATCHED_CONTROL.md`. Do not substitute the older dev `indexing.yaml` or legacy best-available-outcome profiles.

## 1. Fixed conditions and assigned interfaces

Hold the task, raw window/channel/sample-rate scope, label ontology, procedural B01–B06 catalog, numerical input contract, fitted model assets, language-model route/settings and budget caps fixed. Match asset-level data/fitting assignments, not merely filenames or model IDs. Realized computations, prompt length, usage and errors may differ as consequences of the intervention.

| Cell | Name | Full catalog | Correct active-block sentence | Visible tools | Admitted tool names |
|---|---|---|---|---|---|
| 00 | catalog-global | common | absent | global eleven-tool surface | same global surface |
| 10 | indexed-global | common | present | global eleven-tool surface | same global surface |
| 01 | catalog-masked | common | absent | progress subset | same progress subset |
| 11 | indexed-masked | common | present | progress subset | same progress subset |

Primary comparisons: **10−00 at g=0**, then **11−10 at i=1**. The first estimates appending the correct sentence, including salience/token changes, not correctness versus a sham pointer. The second estimates the bundle of exposure, admission and associated resource/trajectory changes, not a pure executor effect. Other simple effects and interaction are exploratory. No additional placebo or exposure-only arm is added in this revision.

The exact active surface is in `paper.yaml`. The canonical adapter's two extra actions are not part of these eleven. Verify actual schemas and admission metadata, not just `STATE_TOOLS` or a declared count, before accepting installed-method equivalence.

## 2. Primary and grounded outcomes

The primary operational score is unchanged: pooled three-class Macro-F1 over all assigned resolved first-attempt outcomes. A canonical non-submission contributes FN to its true class; it is not averaged as a fourth class. Indeterminate attempts remain unresolved and are never silently resent, dropped or replaced.

The prospective secondary score uses the same cohort, class set, canonical attempts and native scorer after applying this fixed label mapping:

| Native first-attempt record | Operational scored label | Grounded scored label |
|---|---|---|
| Accepted; `submission_grounding == 1` and `artifact_lineage_completeness == 1` | accepted label | same label |
| Accepted; both native flags are resolved and at least one is 0 | accepted label | `no_submission` |
| Resolved terminal non-submission | `no_submission` | `no_submission` |
| Accepted; required support fields missing, malformed or unresolved | accepted label, if otherwise complete | unresolved; no inferred zero |
| Indeterminate attempt | unresolved | unresolved |

Use per-attempt native submission output and its selected prediction reference; never cohort-averaged flags, prose claims or a retrospective best-matching prediction. Native values are numeric indicators, not arbitrary truthy strings. Agreement and inclusion of required feature references do not certify correct physical diagnosis or validity of every extra reference. Report `supporting_reference_validity` separately; it does not silently alter the fixed secondary criterion.

The secondary mapping is **defined here but not yet validated as a Benchmark cohort endpoint**. Required native validation covers a correctly supported label, a supported wrong label, a correct unsupported accepted label, missing feature support, a terminal non-submission and unresolved support/attempt records. Validate without changing submission acceptance, the primary scorer, historical records or attempt selection. A paper-local scorer or fabricated real-data example is not acceptable evidence.

The two primary contrasts retain their nominal 97.5% paired percentile intervals. Secondary estimates do not inherit that multiplicity allocation. Report both endpoints and their uncertainty. A gain in grounded Macro-F1 can support improved contract-grounded delivery even if operational Macro-F1 is unchanged; it cannot be relabelled as an overall operational gain. A rise in grounding rate alone is not a diagnosis-accuracy result. Do not infer equivalence from a nonsignificant pilot.

## 3. Minimal experiment sequence

| Stage | Required work in Benchmark | Result it can establish |
|---|---|---|
| E0: real-data mechanics | Verify metadata–HDF5/sample-rate/window correspondence; disjoint fitting/evaluation assets; identical Scripted/four-cell resolved assignments and reloaded fitted assets; one native Scripted episode, canonical bundle and metric recomputation | The installed task and numerical path execute on admitted real data, not treatment efficacy |
| E1: provider-free numerical headroom | On reserved development bearings, obtain the existing diagnosis experts' legal predictions, label disagreements, resolved output differences and resource-feasible second-prediction witnesses | Whether the audited numerical alternatives can change a supported label |
| E2: paired pilot | Run the four original cells in independent sessions with the fixed balanced first-attempt assignments and complete-block reserve | Executability, trajectory variation and mechanism frequency; not stable population effects |
| E3: endpoint audit | Validate the above secondary mapping in the shared parser/scorer before inspecting treatment outcomes; report both matrices, submissions, grounding and failures on the same cohort | Distinguish correct label delivery from contract-grounded delivery |
| E4: mechanism observations | Link prediction, feasible opportunity, selected continuation, numerical change, supported label change and evaluated correctness | Descriptive evidence compatible with the proposed control mechanism |
| E5: confirmatory freeze | Fix cohort/class composition, window scope, repeats, order, exact provider/model/settings, native timeouts/failures, budgets, endpoints, inference families and bootstrap count | A prospectively specified confirmatory comparison |

Execution order is E0 → E1 and native E3 preparation → E2/E4 → E5. E3 defines and validates measurement before treatment outcomes are inspected; its result report accompanies E2. E1 uses no LLM provider. Data-independent native parser checks can proceed while E0 is blocked, but cannot be called real-data acceptance. Do not expand the operator/expert pool to manufacture positive headroom.

## 4. Numerical opportunity: what E1 must distinguish

The diagnosis pool uses the existing nearest-centroid, ridge one-versus-rest and k-nearest-neighbour experts with their shared fitted assets. Use the exact native schema and input validator. Six time-domain features and four prescribed Welch-derived band powers are required from the same raw window; additional callable operators do not automatically create accepted model inputs.

For a prespecified development cohort, retain each expert's prediction and any contract failure. Report pairwise disagreement with explicit denominators and do not hide missing predictions. Distinguish a different score vector from a different class. A best-available-expert correctness calculation may quantify oracle headroom within this audited pool relative to the declared reference expert; it must not select test-time models, gates or samples. Development and final evaluation bearings remain disjoint.

For each audited first-prediction context, record the shortest validated continuation to a different legal prediction, its required feature/model references and its incremental calls. Include the reserve needed for final submission. Respect tool, model-call, turn and token caps; where provider-free checks cannot certify a resource limit, mark feasibility unresolved rather than absent. Do not infer agent feasibility from tool-call counts alone or claim measured latency without provider execution.

A reread with a new identifier but identical array is not new raw information. An operator output that the predictor rejects is only an artifact-level opportunity. A legal second prediction with the same label does not establish label-changing headroom. Zero observed disagreement constrains only the audited contract, pool and development support, not every possible PHM analysis.

## 5. Trace measurements and denominators

For each assigned attempt, retain whether it reached prediction, whether a budget-feasible legal alternative was established at that context, whether continuation was selected, whether resolved numerical output changed, whether the supported submitted label changed, and whether correctness changed. Include early submission attempts and nonterminal recovery paths. The ordinary closure statement excludes error paths; a native terminal failure cannot subsequently recover.

Report counts over all assigned attempts, plus explicitly named at-risk denominators for conditional rates. Distinguish false, inapplicable and unresolved events. No prediction is not proof of zero available expert disagreement; no selected continuation is not proof that none was feasible. Feasibility and subsequent execution must use the same raw scope and fitted assets. Trace stages are not causal mediation estimates and are not multiplied into a purported Macro-F1 decomposition.

## 6. Freeze and interpretation

The current single-seed/single-rotation smoke entry does not define a confirmatory sample size. Use pilot variability and event occurrence to plan a stated precision target, not pilot significance to decide whether to continue. Freeze exact model identifiers, provider route, temperature/top-p/seed, budgets, timeout handling and condition order. Keep absolute request times, complete-block identities and resumed gaps; balanced position does not remove provider drift. A route/model change creates a new study root.

Only complete, compatible native evidence can support a performance claim. Retain adverse findings, unsupported correct guesses, supported mistakes and inactive observed restrictions. Do not merge migration PR #20 until its own real-data and equivalence requirements pass; after normal integration, update the paper's binding to the accepted Benchmark dev commit and keep one authoritative current configuration.
