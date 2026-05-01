---
name: idea_discovery_or_problem_formulation
description: Advance one selected P0 node with one bounded idea-discovery, problem-definition, gap-framing, or scope-clarification step after local entry has loaded the node prompt and checklist.
---

# Idea Discovery Or Problem Formulation

## Use When

Use after the orchestrator or local entry has selected one P0 node and loaded its node-local prompt and checklist.

Use this for:
- background-to-problem synthesis
- important problem discovery
- gap formulation
- aim or novelty boundary clarification
- feasibility and scope narrowing

## Terms

- Problem framing: define why the problem matters, what prior work already covers, and what concrete gap remains.
- Proposal problem definition: turn background material into a fundable or writable research problem without treating literature summary as contribution.
- Reviewer objection path: the most likely way a reviewer could reject the idea, such as weak novelty, false gap, unavailable data, missing metric, overbroad claim, or infeasible scope.
- Falsification path: the minimum evidence that could disprove the current gap, hypothesis, or proposed claim.

Avoid ambiguous legacy labels in outputs. Prefer "problem definition", "reviewer objection", or "falsification path".

## Method Kernel

For one bounded node-local step, convert available context into a sharper problem definition:

1. State the important problem in one concrete sentence.
2. Identify the nearest prior work or existing method family.
3. Name the unresolved gap without pretending that a literature summary is a contribution.
4. Separate facts, hypotheses, proposed claims, and unknowns.
5. Mark which citation-backed facts are verified, unverified, or need `citation_verifier`.
6. Identify the most likely reviewer objection or falsification path.
7. State the minimum evidence needed before this idea can move toward experiment design or manuscript claim.

## Decision Checks

Before writing, check:

- Importance: who cares if this problem is solved?
- Novelty: what nearest prior work could make the idea look incremental?
- Falsifiability: can the gap be contradicted by evidence?
- Feasibility: what data, metric, baseline, or resource is minimally required?
- Citation: which prior-work claims depend on verified sources rather than memory?
- Scope: is this still a P0 problem-definition step, not P1 execution or P2 writing?

## Output Shape

Write only node-local increments requested by the local prompt and checklist, usually one of:

- sharper problem statement
- background synthesis paragraph
- gap and prior-work map
- aim or innovation boundary note
- unknowns or reviewer-objection list
- citation verification gaps that should route to `citation_verifier`

## Boundaries

- Do not become a literature-search controller.
- Do not promote an idea to experiment execution before novelty and feasibility are minimally screened.
- Do not enter P1/P2/P3/P4 execution logic.
- Do not modify graph artifacts directly.

## Stop Conditions

Stop and report the gap if:

- the node goal is unclear
- the evidence base is too thin to state a concrete problem
- a material prior-work or gap claim depends on an unverified citation
- the gap cannot be written as one falsifiable sentence
- the task has moved outside P0 problem definition
