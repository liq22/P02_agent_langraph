# Novelty Boundary Refinement

generated_at: 2026-05-05

## Scope

This artifact records the first P0_01 novelty-boundary tightening against the registered local source set. It is now paired with `artifacts/final_submission_sota_sweep.md`, which broadens the final-threshold SOTA sweep with additional research-agent, automated-science, software-agent, provenance, and experiment-management sources.

## Registered Source Boundary

The current local source set contains four representative clusters:

- tool-using language agents: ReAct and Reflexion;
- multi-agent application infrastructure: AutoGen;
- ML experimentation and automated-scientist systems: MLAgentBench and The AI Scientist;
- reporting and review governance: Nature Portfolio reporting standards and IEEE submission/peer-review policies.

## Non-Novelty Claims

AutoResearch should not claim novelty for:

- language agents that interleave reasoning and actions;
- feedback or memory-like loops for agent improvement;
- configurable multi-agent conversation frameworks;
- agents that run ML experiments;
- generated research ideas, papers, or simulated reviews;
- journal reporting, disclosure, originality, or review policies.

These capabilities are already represented by the registered source clusters.

## Candidate Novelty Claim

The candidate novelty is the research-governance layer between agent output and accepted manuscript claim. In the current formulation, the project asks whether a node-local workflow can keep these records auditable before a phase transition is accepted:

- claim identity;
- evidence status and evidence boundaries;
- protocol gates;
- independent review verdicts;
- response coverage;
- negative, failed, blocked, or unclear evidence.

This is a process and evidence-governance claim, not a claim that AutoResearch already improves real-data model performance or passes final submission review.

## Falsification Conditions

The novelty boundary would fail if a prior system already showed stable claim-to-evidence-to-review-to-response traceability across a multi-node research workflow. It would also fail if a simpler manual checklist, prompt-only agent workflow, or ungated multi-agent workflow matched AutoResearch under the same node set and budget on:

- claim-evidence validity rate;
- unsupported-claim count;
- independent reviewer pass rate;
- hard-fail closure rate;
- response coverage rate;
- reproducibility rerun agreement.

## Remaining Final-Submission Need

The broader SOTA sweep is now recorded in `artifacts/final_submission_sota_sweep.md`. Strong mechanism claims still require downstream comparative evidence before result-level wording.
