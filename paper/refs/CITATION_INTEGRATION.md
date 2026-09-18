# Foundational citation integration map

These citations constrain claims already present in `paper/draft/main.md`. They are not additional contribution claims.

| Manuscript claim | Citekeys | Required interpretation |
|---|---|---|
| State-machine structure is established prior work | `hansen1997`, `wu2024stateflow` | P02 does not claim finite-state controllers or state-driven LLM workflows as new. |
| Tool filtering changes the executable support | `huang2022masking`, `evendar2006` | The implemented gate is broader than invalid-action masking and is not justified by calibrated action-value confidence. |
| Executed logs do not reveal excluded-action value | `jiang2016`, `khan2024` | Without overlap or additional assumptions, omitted PHM continuations are not point-identified. |
| Repeated agent reliability is an existing evaluation objective | `yao2024tau` | First-attempt reporting defines the operational endpoint; it does not introduce a new reliability metric. |

Recommended inline placements:

1. Introduction, after “State-machine structure itself is established prior work”: `[@hansen1997; @wu2024stateflow]`.
2. Related Work, after the AgentBench discussion of interactive-agent failures: `[@yao2024tau]` for repeated-trial reliability.
3. Section 3.3, when introducing retained action sets: `[@huang2022masking; @evendar2006]`.
4. Section 3.3, after stating that invalid-call rates do not estimate excluded value: `[@jiang2016; @khan2024]`.

The bibliography entries are maintained in `paper/refs/references.bib`; source-bounded claims are recorded in `paper/literature_matrix.md`.
