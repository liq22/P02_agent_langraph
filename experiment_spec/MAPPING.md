# Paper 2 → Benchmark mapping

All execution remains in `liq22/phm-agent-benchmark`; configurations live in `configs/paper02_graph/`. Existing historical P2-E* results retain their identities. The next execution goal is Benchmark `paper/goals/P02_MATCHED_CONTROL.md`; distinguish the provider-free real-data migration check from the subsequent model-based organization study.

| Mapping | Question / estimand | Conditions and config | Evidence boundary |
|---|---|---|---|
| G-main | Joint Graph control | Generic / original Graph; `main.yaml` | Not topology-only; no new real matched result in this slice |
| G-components | Cue package, visibility, interaction | `factorial-reactive/state/filter/both`; `components.yaml` | Same historical-state rendering; fresh controls, not old Generic |
| G-organization | Current-stage annotation / restriction with fixed procedural inventory | `organization-reactive/state/filter/both`; `organization.yaml` | Same six instructions in each arm; no PHM effect estimated; see theory07 |
| G-relevance | Analysis-stage identity beyond count | `factorial-filter` / `factorial-cardinality`; `mask_relevance.yaml` | Existing Analyze/Check control preserved, not replaced by the earlier local ZIP |
| G-memory | Activation before efficacy | Graph / Graph-no-memory; `memory.yaml` | Event-free base is a null manipulation under theory07; retain as negative control |
| G-horizon | Length/sampling/resource sensitivity | Existing `horizon.yaml` | Pure horizon requires fixed-longest nested prefixes and separate budget regimes |
| G-dynamic | Recurrence and revision | Future `dynamic-history-matched` cohort; shared event/assignment dispatch pending | All dynamic profiles share history sanitation; legacy full-dynamic results are not equivalent |
| G-extension | Repeated reliability / transport | Within-task matched studies, followed by admitted external bindings | Task outcomes primary; no state/Mock substitute |

Implementation: `src/phm_graph_agent/{agent,state,components,cardinality_control}.py`, with the existing conditions, Runner and evaluator. The new `test_graph_organization.py` checks the fixed bank, annotation/mask separation, legacy wording, inherited response path, contrast algebra and actual YAML plan. CI run **35214966018** on Benchmark **0ba1121** passed **144 research tests** and **33 production-boundary tests**, including all eight new checks. The emitted 24 rows are input fixtures, not PHM episodes. Code and compact evidence are in Benchmark `results/graph_control/organization_20260917`; execution is still subject to the real-data gate and verification of any later concurrent runtime changes in its Goal.

Theory04–06 retain the existing exact value, support and cardinality calculations. Theory07 adds the complete recursive state (including event token), the reachable-interface coupling argument, inactive base ablations and prospective dynamic-history matching. Main Sections 3–6 implement that interpretation; existing exact result paragraphs are retained, not rerun in this slice.

All real outcomes still use the existing six-file attempt bundle and shared scorer. Task metrics/data protocols are unchanged. P02 stores scientific interpretation and locations, not a copied raw-result tree. Feed actual G findings, not test counts, to Benchmark Paper 0.

The fixed-instruction profile narrows the previously specified information-matched prompt comparison to identical instruction inventory, not identical tokens. It does not reuse old factorial-reactive or alter K content. Existing exact result paragraphs remain unchanged; real organization effects belong in manuscript Results 7.4 only after a matched study completes.

Later runtime validation is separately scoped: run 35215969880 passed 153 research tests, including the eight organization checks, and 52/53 production checks. The remaining CLI check reaches real loading but lacks `/mnt/e/D01_vibench/metadata.xlsx`; the latest full run is not green. Keep Draft until real-data acceptance, without replacing the test input.
