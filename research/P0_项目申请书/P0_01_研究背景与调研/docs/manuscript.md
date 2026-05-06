# P0_01 Research Background and Literature Gap

## Main Problem

Agentic AI is moving from single prompt-response assistance toward systems that plan, use tools, coordinate multiple agents, execute code, and draft research artifacts. ReAct showed that language models can interleave reasoning traces with environment actions; AutoGen generalized multi-agent conversation patterns; MLAgentBench evaluated language agents on machine-learning experimentation; and The AI Scientist pushed the idea toward automated idea generation, experiments, paper writing, and simulated review. These works make the same broad direction credible: language-model agents can perform parts of research work that used to be manual.

The central problem for this project is not whether agents can produce fluent research artifacts. They can. The harder problem is whether a human-agent research workflow can keep claims, evidence, protocols, review objections, responses, and phase transitions inspectable enough that a skeptical reviewer can tell what is supported, what is merely planned, and what failed. Publication policies and reporting standards reinforce this pressure: manuscripts must preserve originality, citation integrity, data/code/protocol availability, and review confidentiality rather than treating generated text as research truth.

## Prior-Work Clusters

The first cluster is tool-using language agents. ReAct and Reflexion demonstrate that agents can combine reasoning, actions, feedback, and memory-like traces. Their strength is task execution. Their limitation for this project is that they do not by themselves define a manuscript-level research truth system: a successful trajectory is not the same as a claim-evidence registry or a review-closed phase transition.

The second cluster is multi-agent application infrastructure. AutoGen shows that configurable agents can converse, call tools, and involve humans in complex workflows. This makes human-agent collaboration technically plausible. Its limitation is that a framework for composing agents is not automatically a scientific audit protocol; it still needs node-local evidence boundaries, reviewer independence, and response coverage.

The third cluster is ML experimentation and autonomous discovery. MLAgentBench and The AI Scientist test whether agents can run experiments and produce research-like outputs. They are the nearest prior work because they bring agents close to the scientific process. Their limitation is the open question this project targets: how to prevent experiment logs, generated papers, or simulated reviews from being over-promoted into accepted evidence without a durable claim/protocol/review ledger.

The fourth cluster is publication and reproducibility governance. Nature Portfolio reporting standards emphasize materials, data, code, and protocols; IEEE policy emphasizes original work, disclosure, plagiarism boundaries, peer review, and AI-generated content disclosure. These sources do not provide an agent workflow, but they define the bar that an agent-assisted research process must respect.

The fuller final-submission SOTA sweep adds three adjacent clusters. Agent Laboratory and The AI Scientist are the closest automated-science systems because they connect agents to idea generation, experiments, report or paper production, and review or feedback stages. SWE-agent represents executable software-agent work on repositories, where agent-computer interfaces can solve concrete coding tasks. MLflow Tracking and Weights & Biases Artifacts represent experiment and artifact provenance tooling: they can record runs, metrics, parameters, datasets, artifacts, and lineage. These systems make the background stronger because they show that substantial parts of research execution and provenance are already supported. They also narrow the claim: AutoResearch is not novel because it uses agents, runs code, drafts reports, or records artifacts.

## Novelty Boundary Against Current SOTA Sweep

The current SOTA sweep supports a narrow novelty boundary. AutoResearch should not be framed as inventing tool-using agents, feedback-based agent improvement, multi-agent coordination, ML experiment automation, generated research papers, simulated peer review, repository agents, artifact lineage, or journal reporting policy. Those functions are already represented by the cited clusters. The candidate contribution is the governance layer between agent output and accepted research claim: node-local records that keep claim identity, evidence status, protocol gates, independent review, response coverage, and negative-result handling inspectable before a phase transition is accepted.

This boundary is intentionally falsifiable. It fails if a prior system already provides stable claim-to-evidence-to-review-to-response traceability across a multi-node research workflow, or if a simpler prompt-only or ungated multi-agent workflow matches AutoResearch on claim-evidence validity, unsupported-claim reduction, review pass rate, and hard-fail closure under the same budget. The current sweep did not identify a nearest prior system that exposes all seven required elements together: stable manuscript claim IDs, evidence IDs with support status, protocol gates, independent review verdicts, response coverage, retained negative/blocked evidence, and phase-transition rejection of unsupported claims.

## One-Sentence Gap

The concrete gap is that current agentic research, automated-science, software-agent, and experiment-provenance systems demonstrate tool use, multi-agent coordination, automated scientific writing, repository task solving, or artifact lineage, but do not show a node-local operating procedure that binds each manuscript claim to evidence, protocol gates, independent review, response coverage, and explicit negative-result handling before phase transition.

## Falsifiable Problem Definition

The gap is falsifiable. It would be weakened if a nearest prior system already showed that every generated research claim can be traced to a stable evidence artifact, citation status, review objection, response action, and phase-gate decision across a multi-node research workflow. It would also be weakened if prompt-only or generic multi-agent workflows achieved the same claim-evidence validity rate, unsupported-claim reduction, and review-closure rate under the same node set and budget.

The minimum evidence needed downstream is therefore not a better-looking paper draft. It is a controlled comparison over fixed research nodes: manual checklist workflow, prompt-only agent workflow, multi-agent workflow without independent gate, and AutoResearch with node-local claim/evidence/protocol/review gates. The primary metric should be claim-evidence validity rate; secondary metrics should include unsupported-claim count, reviewer pass rate, hard-fail closure rate, reproducibility rerun agreement, and time to author exit.

This P0_01 package is proposal-stage evidence: it justifies a falsifiable research question and comparison design, but it does not validate the downstream AutoResearch mechanism.

## Project Boundary

This P0_01 node only establishes the background, nearest prior-work clusters, and falsifiable literature gap. It does not claim that the project has already solved real-data performance, RM101, selected-backend readiness, Stage C/D formal evidence, or final submission readiness. Those remain downstream evidence gates.
