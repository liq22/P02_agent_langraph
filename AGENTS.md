# Agent Entry — GraphDecisionAgent Paper 2

Read `CORE.md` first. It overrides conflicting AutoResearch, scheduler, Canvas, Goal, review, submission, and historical manuscript narratives.

## Active objective

Advance the matched experiment:

```text
Sequential/Reactive Agent
versus
GraphDecisionAgent
```

Use the shared benchmark's TaskSpec, actions, budget, rollout, and evaluator. Do not create a second benchmark or data layer.

## Graph rules

- Keep the graph small and library-independent.
- Nodes represent decision states, not wrappers for every function.
- The primary recovery object is decision revision under equipment/data changes, not a catalogue of injected LLM/action failures.
- Preserve time order and prevent future-window access in replay tasks.
- Formal scoring uses PHM task outputs and observable state/action/result events.
- Optional agent-emitted reasoning traces may be retained when permitted; hidden chain-of-thought is not required or reconstructed.
- The historical PHMGA submodule is reference material, not active runtime authority.

## Work priorities

1. real replay/streaming task performance;
2. GraphDecisionAgent state and transition correctness;
3. matched sequential-versus-graph experiments;
4. focused graph ablations;
5. secondary branch, completion, stability, cost, and latency analysis;
6. figures, tables, and manuscript claims.

Do not add custom hash/checksum/digest/receipt/ledger systems, exhaustive defensive state machines, project-management graphs, or UI infrastructure unrelated to the scientific comparison.

Use Python for actual experiments, analysis, plots, and focused tests. Fail fast on temporal leakage, hidden-target access, unmatched budgets, or evaluator ambiguity.
