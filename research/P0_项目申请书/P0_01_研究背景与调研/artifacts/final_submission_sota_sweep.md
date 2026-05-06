# Final-Submission SOTA Sweep

generated_at: 2026-05-05

## Scope

This artifact answers the AI_002 final-threshold action for P0_01: broaden the novelty check beyond the original representative local sources. It covers the nearest current categories named by the reviewer: research-agent systems, automated-science systems, provenance and experiment-management systems, and review-workflow systems.

This is still a background-and-gap artifact. It does not claim that AutoResearch has validated better claim quality, review closure, or reproducibility. Those remain downstream metrics.

## Sweep Method

The sweep compares AutoResearch's candidate gap against systems that are close enough to weaken the novelty claim if they already provide stable claim-to-evidence-to-review-to-response traceability across a multi-node research workflow. A source is treated as nearest prior work when it automates research labor, runs ML experiments, produces research reports, supports software-agent execution, or records experiment/artifact provenance.

## Nearest Prior Systems

| Category | Sources | What They Establish | Remaining Boundary For AutoResearch |
| --- | --- | --- | --- |
| Tool-using and self-improving agents | ReAct; Reflexion | LLM agents can interleave reasoning/actions and use feedback-like traces. | Task trajectories and self-reflection logs do not by themselves bind manuscript claims to evidence status, review objections, response actions, and phase gates. |
| Multi-agent orchestration | AutoGen | Configurable agents can converse, use tools, and include humans. | Agent orchestration is not equivalent to a research-truth ledger with independent review and negative-result retention. |
| ML experiment agents | MLAgentBench | Language agents can be evaluated on ML experimentation tasks, including coding and result interpretation. | ML task success does not close manuscript-level claim/protocol/review/response traceability. |
| Automated scientist systems | The AI Scientist; Agent Laboratory | Agents can generate ideas, run experiments, write reports or papers, and include automated or human feedback stages. | These systems come closest, but the reviewed public descriptions center on producing research artifacts and evaluation workflows; they do not expose a canonical node-local ledger that must reconcile every central claim with evidence, protocol gates, independent review, author response, and negative-result status before phase transition. |
| Software engineering agents | SWE-agent | Agent-computer interfaces can improve repository issue solving and executable software tasks. | Software patch success is not a research-submission evidence contract; it lacks manuscript claim identity, reviewer-response coverage, and publication-stage truth boundaries. |
| Experiment tracking and artifact provenance | MLflow Tracking; Weights & Biases Artifacts | Modern ML tooling can record runs, metrics, parameters, artifacts, datasets, and artifact lineage. | Run/artifact provenance is necessary but insufficient: it does not decide claim support status, independent reviewer pass/fail, response coverage, or whether failed/blocked evidence may be promoted into manuscript claims. |
| Reporting and peer-review governance | Nature Portfolio reporting standards; IEEE submission and peer-review policies | Publication policy requires availability, originality, disclosure, and peer-review boundaries. | Policies define constraints but do not provide an executable human-agent workflow that keeps research claims synchronized with evidence and response artifacts during production. |

## Strengthened Novelty Boundary

AutoResearch should not claim novelty for:

- agents that use tools, code, or feedback;
- multi-agent conversation frameworks;
- automated ML experimentation;
- automated paper/report drafting;
- simulated or assisted review;
- repository-level software agents;
- experiment tracking, artifact versioning, or provenance tools;
- publication reporting policy.

The remaining candidate gap is narrower: a node-local operating procedure for human-agent research that forces central manuscript claims to stay linked to evidence identity, evidence support status, protocol gates, independent review, response coverage, and failed/blocked/negative evidence before a phase transition is accepted.

## Falsification Test

The novelty claim should be downgraded if a nearest prior system demonstrates all of the following as first-class workflow requirements rather than optional logs:

1. stable manuscript claim IDs;
2. evidence IDs with support status and source boundary;
3. protocol or execution gates before evidence is promotable;
4. independent review verdicts tied to node scope;
5. response coverage for review objections;
6. retained failed, blocked, negative, or unclear evidence;
7. a phase-transition rule that rejects unsupported claims even when an agent produces fluent text or executable results.

The current sweep did not find a prior source in the reviewed set that claims all seven together. This supports the P0_01 background gap, but it does not prove AutoResearch's mechanism is effective.

## Downstream Evidence Still Required

Before strong result wording, downstream work still needs a fixed-node comparison against manual checklist, prompt-only agent, and ungated multi-agent baselines on:

- claim-evidence validity rate;
- unsupported-claim count;
- independent reviewer pass rate;
- hard-fail closure rate;
- response coverage rate;
- reproducibility rerun agreement;
- time to author exit.

