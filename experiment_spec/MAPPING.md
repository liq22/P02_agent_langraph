# Paper 2 → Benchmark mapping

All execution remains in `liq22/phm-agent-benchmark`; configurations live in `configs/paper02_graph/`. Existing historical P2-E* results retain their identities. The next execution goal is Benchmark `paper/goals/P02_MATCHED_CONTROL.md`.

| Mapping | Question / estimand | Conditions and config | Evidence boundary |
|---|---|---|---|
| G-main | Joint Graph control | Generic / original Graph; `main.yaml` | Not topology-only; no new real matched result in this slice |
| G-components | Cue package, visibility, interaction | `factorial-reactive/state/filter/both`; `components.yaml` | Same historical-state rendering; fresh controls, not old Generic |
| G-relevance | Analysis-stage identity beyond count | `factorial-filter` / `factorial-cardinality`; `mask_relevance.yaml` | Existing Analyze/Check control preserved, not replaced by the earlier local ZIP |
| G-memory | Activation before efficacy | Graph / Graph-no-memory; `memory.yaml` | Event-free base is a null manipulation under theory07; retain as negative control |
| G-horizon | Length/sampling/resource sensitivity | Existing `horizon.yaml` | Pure horizon requires fixed-longest nested prefixes and separate budget regimes |
| G-dynamic | Recurrence and revision | Future `dynamic-history-matched` cohort; shared event/assignment dispatch pending | All dynamic profiles share history sanitation; legacy full-dynamic results are not equivalent |
| G-extension | Repeated reliability / transport | Within-task matched studies, followed by admitted external bindings | Task outcomes primary; no state/Mock substitute |

Implementation: `src/phm_graph_agent/{agent,state,components,cardinality_control}.py`, with the existing shared conditions, Runner and evaluator. The new `experiments/tests/test_graph_intervention_contract.py` captures model inputs and stops before generating a response. Its 24 public-history/factorial fixture rows are not Agent episodes or PHM results. The native suite passed in GitHub Actions run 35110539101: 83 research tests, including all eleven new Graph checks, after installing the real pinned Factory and Benchmark. This does not supply a real-data episode, exhaustive migration equivalence or a task effect. Reproduce the applicable checks on the local data host before inference.

Theory04–06 retain the existing exact value, support and cardinality calculations. Theory07 adds the complete recursive state (including event token), the reachable-interface coupling argument, inactive base ablations and prospective dynamic-history matching. Main Sections 3–6 implement that interpretation; existing exact result paragraphs are retained, not rerun in this slice.

All real outcomes still use the existing six-file attempt bundle and shared scorer. Task metrics/data protocols are unchanged. P02 stores scientific interpretation and locations, not a copied raw-result tree. Feed actual G findings, not test counts, to Benchmark Paper 0.
