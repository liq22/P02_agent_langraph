# Graph-Guided PHM Agent Entry

This repository owns the graph-guided policy implementation and Paper 2 of the active three-paper PHM-Agent program.

## Primary products

- an executable graph policy under `src/phm_graph_agent/`;
- matched Reactive-vs-Graph experiments using the shared Benchmark Generic LLM base;
- real state transitions, trajectories, metrics, tables, and figures;
- the active manuscript at `paper/draft/main.md`.

Legacy `research/`, scheduler, web, Canvas, historical PHMGA snapshots, and old Goal material is not the active execution authority for this paper. Read a legacy artifact only when a current code or manuscript claim explicitly requires it.

## Default execution

```text
identify the highest-impact graph/code/experiment/manuscript defect
→ output a four-line dry-run
→ modify one primary product
→ run one direct test, matched episode, metric check, or manuscript check
→ continue with the next research slice
```

Local reversible edits and tests proceed without per-file approval. Ask once before private-data transfer, unbudgeted paid inference, remote Git writes, release, or submission.

## Scientific constraints

- Control is `ReactiveSequentialAgent`, a zero-behavior-override subclass of the
  shared Benchmark `GenericLLMToolAgent`.
- Treatment is `GraphDecisionAgent`, derived from the same Generic base and
  differing only by the registered graph decision control.
- PHMskills is not part of the active Paper 2 control or treatment; historical
  PHMskills-derived Graph leaves are retained only as non-authoritative records.
- Model, runtime, data, split, tools, numerical experts, budget, evaluator, and episode order remain identical.
- The graph states must affect actual next-action selection and appear in the shared trajectory.
- The benchmark core must not depend on LangGraph or this repository.
- Mock and synthetic runs prove mechanics only.
- Do not fabricate citations, data, results, authors, or venue policy.
- Do not build completion controllers, content-hash checks, approval workflows, review state machines, security platforms, UI DAGs, or speculative fallback frameworks.
- Python is for graph policy, experiments, statistics, figures, and direct tests—not project-governance scripts.

Paper 2 is complete only when code, matched real-data results, figures/tables, a full manuscript, and the final ten-lens review are complete.
