# Claim Evidence Map

| claim_id | evidence_id | method claim | evidence location | boundary |
|---|---|---|---|---|
| p2_methods_unit_of_analysis | p2_node_contract_record | Research node is the unit of analysis | `docs/manuscript.md:Methods Scope`, P1 rigor plan [3] | Defines study object only |
| p2_methods_intervention_definition | p2_intervention_record | Intervention includes node framing, registry, gates, independent review, and response coverage | `docs/manuscript.md:Study Design`, P0 contribution claims [3] | Intervention definition is not a result |
| p2_methods_primary_metric | p2_metric_contract | Claim_evidence_validity_rate is the primary outcome | `docs/manuscript.md:Study Design`, P1 protocol [3] | Requires baseline comparison and uncertainty |
| p2_methods_reproducibility | p2_reproduction_record | Reproduction requires node paths, prompts, rubrics, budgets, assignments, commands or manual ledgers, and artifact schemas | `docs/manuscript.md:别人需要哪些细节才能理解与复现？` [3] | Covers procedural reproduction |
| p2_methods_negative_results | p2_failure_policy | Negative results and failed gates remain visible | `docs/manuscript.md:Limitations and Negative Results` [3] | Final transition still requires reviewer or human gate |

## Methods Boundary

Methods covers study design, unit of analysis, intervention and baseline definitions, metric contract, statistics plan, data-code/protocol statements, reproducibility record, figure/table logic, and limitations. Appendix/protocol holds long node lists, raw logs, reviewer forms, run commands, budget records, result ledgers, and coverage matrices.

## Author Exit

claim_evidence_ids_are_explicit_or_gap_is_reported: true。negative_or_failed_results_recorded: true。protected_paths_respected: true。

[3] Local evidence gate: `test/NATURE_LEVEL_NODE_RUBRIC.md`, P1 `artifacts/experiment_rigor_plan.yaml`, and this node `artifacts/claim_evidence_registry.yaml`.
