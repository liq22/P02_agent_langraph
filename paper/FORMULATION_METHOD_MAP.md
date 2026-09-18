# PHMGraph: formulation, method and evidence map

The active manuscript is `draft/main.md`; the current manifest is `paper.yaml`. This file explains source bindings and figure purpose, not experimental results. Numerical tools, execution, scoring and all figure source remain in `liq22/phm-agent-benchmark`.

## Scientific chain and boundary

Question: with the same PHM procedures and potential fitted experts, what is the effect of an active instruction pointer, and the additional effect of progress gating?

Foundation → history-conditioned tool use, finite controllers, standard finite-horizon value accounting and cohort-level classification metrics. Reformulation → distinguish fixed setting X, interface intervention Z, public trajectory τ, process T and evaluator outcome Y. Studied mechanisms → independent pointer and gate under common content. Measurement → first-attempt diagnosis contrasts 10−00 and 11−10. Current evidence → implemented interface and derived execution boundaries, not measured diagnostic effects.

Chapter 2 defines the task and the comparison. Chapter 3 instantiates that comparison. No state-machine novelty, new Bellman theorem, pure topology effect, guaranteed recovery or evidence-sufficiency claim is made. The exposed menus encode progress even without an explicit pointer.

## Mechanism-to-evidence correspondence

| Object / mechanism | Formula and definition | Figure position | Method / algorithm | Comparison and supported interpretation |
|---|---|---|---|---|
| Fixed capability and private target | Xₖ; evaluator-only cₖ, Section 2.1–2.3 | Figure 1 top and evaluator blocks | Shared Algorithm 1 inputs; cₖ excluded | Same task, data scope, experts, fitted parameters, model and budgets; realized computations may differ |
| Instruction localization | iL(sₜ), full catalog B, Section 3.2 | Figure 2 block 3 | Algorithm 1 steps 2–5 | 10−00 under global tools; effect conditional on common catalog, not new knowledge |
| Temporal executable gate | Γg(sₜ), name-admission rule, Section 3.3 | Figure 2 block 4; same menu to blocks 5 and 6 | Algorithm 1 steps 4–7 | 11−10 after indexing; total gate effect including implicit phase cue and opportunity restriction |
| Progress abstraction | sₜ=f(hₜ), error/read/catalog/prediction/schema precedence | Figure 2 block 2 and feedback loop | Section 3.4; steps 2, 7 | Source-derived adaptation; not a belief state or a learned diagnostic posterior |
| Early submission and closure | Inspect→…→prediction→Submit on supported base path | Figure 2 execution and history/output branches | Section 3.3–3.4; steps 6–8 | Prediction use, early submission, continuation, final-label and resolved-numerical-content changes; descriptive mechanism evidence |
| Recovery exception | Latest error precedes ordinary phase conditions | Figure 2 history return | Section 3.4; steps 2, 6–8 | May reopen reading/analysis; no one-step or no-repetition guarantee |
| Delivered diagnosis | Yₖ; M(DZ) as pooled three-class Macro-F1 | Figure 1 outcome and cohort endpoint; Figure 2 output | Section 2.3 and Section 5 | Canonical non-submissions retained; indeterminate records not fabricated |

The standard opportunity–selection identity concerns expected episodic return, not pooled Macro-F1. It motivates competing explanations but does not estimate regret from invalid-action rates. Conditional continuation/submission summaries are not causal mediation estimates.

## Figures: purpose and contract

**Figure 1 — Problem formulation and observation boundaries.** Section 2.3. Needed to distinguish fixed X, manipulated Z, observed τ/T and evaluator-derived Y before the method is introduced. Required elements: common capabilities, generic interaction, public trajectory, private class, evaluated outcome and cohort metric. Text directly defines every displayed variable. Arrows are dependencies, not an identified mediation graph. This replaces the displayed motivation schematic; its older source and asset remain historical, not duplicated.

**Figure 2 — PHMGraph overview and execution loop.** Section 3.1. Needed because locator and gate share a progress abstraction but affect different parts of sequential execution. Required elements: public context and full B, adapted f, independent i/g switches, fixed model, common menu supplied to model and executor, shared validation/tools, error feedback and submission. Pale solid blocks are inherited components, dashed progress abstraction is adapted, and heavy borders identify the controlled intervention. Numbered blocks map to Algorithm 1. A short overview paragraph introduces the complete route, followed by definitions in Sections 3.2–3.4 and Algorithm 1.

Both figures are original vector diagrams, not empirical plots. Editable SVG text and named object groups are preserved. There are no embedded raster images or external fonts. The source exports SVG, PDF and PNG at a physical width of 180 mm. Its Python source is the only drawing implementation; it neither imports the agent runtime nor reads PHM data or calls a model.

## Exact inspected runtime binding

Repository: `liq22/phm-agent-benchmark`.

Commit: `8206cfef540d5f602adba482e9dcc0ebd6b0f437` (migration PR #20; paper integration does not accept it).

| Source at that commit | Blob / scientific role |
|---|---|
| `src/phm_graph_agent/components.py` | `0a824598216b04471afabd66d1667ce8f4f93bd0`: same B01–B06 catalog, optional identifier, shared history sanitization |
| `src/phm_graph_agent/agent.py` | `72927562b055e2cbb7141f03e0db57cec47bcb22`: actual six base menus and optional dynamic menus |
| `src/phm_graph_agent/state.py` | `4272b5b748853009327b7c4a1208ae79714684e8`: deterministic precedence, recovery exceptions, sample-bound replay progression |
| `src/phm_agent_benchmark/research/conditions.py` | `aee6e1dd1349652140294d610588c01183b70802`: four interfaces and primary contrast definitions |
| `src/phm_agent_benchmark/phase1/agents.py` | `86f896d69ebfbcaadbcab2d6b9b485198aaef148`: one-request policy output and shared allowed-tool metadata |
| `configs/paper02_graph/indexing_first_attempt.yaml` | Pinned smoke configuration, not a confirmatory sample size |

The method is training-free. Primary diagnosis has one distinct legal raw window. The replay profile counts eleven successful sample-bound feature calls, not eleven distinct features. Full history is retained; no condition-change event is part of the primary intervention.

## Manifest and historical outputs

`paper.yaml` is the schema-version-2 active scientific manifest. The previous schema-version-1 manifest is preserved byte-for-byte at `legacy/graph_v6_manifest.yaml`, blob `9930405db6b41ce0a4a743285dc97defb696706a`. Its original replay, dynamic, reliability and external-dataset profiles are not current indexing controls. Historical tooling must use its corresponding legacy protocol; do not feed the new manifest into a legacy renderer without explicit compatibility support. Six original manuscript insertion-marker pairs are retained exactly once, with their original meanings. This manuscript change neither runs those renderers nor changes their result records.

## Necessary empirical continuation

Follow the pinned Benchmark goal. First resolve the actual Scripted and four-condition task/data/fitting assignments and verify bounded reads against the real waveforms. Then run the approved paired first-attempt pilot using those assignments. Retain terminal non-submissions, provider failures and unresolved attempts under the existing rules. Only evaluated outcomes can establish whether indexing or gating helps, hurts or is inactive. No extra expert, data scope or metric is introduced to make a favorable effect easier to obtain.
