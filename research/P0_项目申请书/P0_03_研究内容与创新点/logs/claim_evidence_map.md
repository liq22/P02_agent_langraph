# Claim Evidence Map

| claim_id | candidate claim | current evidence | required evidence before strong wording | boundary |
|---|---|---|---|---|
| p0_claim_node_contract | Research nodes as auditable scientific work units can expose unsupported completion states | `artifacts/literature_gap_map.yaml`, `test/NATURE_LEVEL_NODE_RUBRIC.md` [4] | NodeBench comparison, independent reviewer verdict, failure distribution | Process audit only until empirical comparison exists |
| p0_claim_cross_phase_traceability | Shared claim/evidence/protocol IDs can reduce untraceable claims across P0-P4 | `artifacts/contribution_claims.yaml` [4] | Registry coverage, unsupported-claim count, response coverage matrix | Traceability does not prove scientific truth |
| p0_claim_preregistered_protocol_gate | Pre-execution protocol gates can reduce post-hoc metric and baseline selection | P1 protocol plan and gate report [4] | primary/secondary metrics, baselines, repeats, uncertainty, negative result ledger | Protocol claim only until experiments run |
| p0_claim_independent_phase_gate | Separating author exit from node close can reduce premature promotion | `prompts/review_rubric.yaml` and human gate policy [4] | independent `review/verdict.yaml`, human gate note, hard-fail closure record | Gate quality still depends on reviewer quality |

## Reviewer Objection Path

The strongest reviewer objection is that AutoResearch may be an engineering governance wrapper rather than a scientific advance. The response path is to keep each claim tied to a falsifiable comparison, a minimum evidence artifact, and a downgrade rule. Local harness reports can support feasibility, but they cannot replace controlled comparison, external review, and uncertainty reporting [1][2][4].

## Author Exit

required_artifacts_exist: true。key_research_judgment_answered_or_gap_reported: true。citation_status_checked_when_external_sources_are_used: true。

[1] Nature editorial criteria: https://www.nature.com/nature/for-authors/editorial-criteria-and-processes

[2] Nature reporting standards: https://www.nature.com/ncomms/editorial-policies/reporting-standards

[4] Local evidence gate: `test/NATURE_LEVEL_NODE_RUBRIC.md` and node-local evaluation artifacts.
