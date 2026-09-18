# PHMGraph: formulation, method and evidence map

The active manuscript is `draft/main.md`; `paper.yaml` records its scientific specification, not executable scoring. Numerical tools, execution, fitting, evaluation, trace extraction and all figure source belong only to `liq22/phm-agent-benchmark`.

## Scientific chain and identification boundary

Question: under the same PHM procedures, numerical contract and fitted experts, how does appending a correct active-block pointer affect first-attempt diagnosis with global tools, and how does adding progress-gated exposure and admission affect diagnosis with that pointer present?

Foundation → history-conditioned decisions, finite controllers, standard action-value accounting and pooled classification metrics. Formulation → fixed X, interface Z=(i,g), public trajectory τ, process T and evaluated outcome Y. Method → an appended pointer and a jointly exposed/enforced progress menu. Measurement → two sequential simple effects, 10−00 and 11−10, on operational diagnosis, plus the prospectively specified grounded counterpart. Evidence → pinned source inspection and execution boundaries; real paired effects and numerical headroom remain unestimated.

Chapter 2 defines the problem; Chapter 3 instantiates the interface. The pointer contrast includes adding a correct sentence, its tokens and salience; without a sham control it does not isolate pointer correctness. The gate contrast includes schema exposure, implicit progress information, admission, resulting errors and resource changes. It is not an isolated executor restriction or averaged main effect. Cell 01 supplies exploratory simple effects and interaction, not a new primary contrast.

## Mechanism-to-evidence correspondence

| Object / mechanism | Mathematical object | Figure position | Method / algorithm | Experiment and claim boundary |
|---|---|---|---|---|
| Fixed capability and private class | Xₖ, evaluator-only cₖ | Figure 1 common setting/evaluator; Figure 2 shared blocks | Shared inputs; cₖ excluded | E0 matches task, window, fitted assets, tools, model and budgets; realized computations can differ |
| Appended correct pointer | iL(sₜ), full B | Figure 2 block 3 | 3.2; Algorithm 1 steps 2–5 | E2: 10−00 at g=0; no new procedure and no isolated attention/correctness claim |
| Exposure-and-admission gate | Γg(sₜ) supplied to both branches | Figure 2 block 4 → blocks 5/6 | 3.3; steps 4–7 | E2: 11−10 at i=1; compound interface effect |
| Public progress and nonterminal recovery | sₜ=f(hₜ), error/read/catalog/prediction/schema precedence | Figure 2 block 2 and feedback loop | 3.4; steps 2, 6–8 | E4: actual transitions and recovery; terminal episodes never reopen |
| Numerically effective continuation | Model-admissible input, feasible continuation, resolved prediction/label | Figure 2 shared numerical execution and history/output branches | 3.4; steps 6–8 | E1/E4: distinguish available operators, legal features, changed output, changed label and correctness; no useful-opportunity assumption |
| Operational delivery | Y, accepted label ĉ, M(D) | Figure 1 outcome/cohort endpoint; Figure 2 output | 2.3; step 8 and 5.1 | Original primary score and first-outcome selection unchanged |
| Contract-grounded delivery | G, label mapping ĉ→c̃, M(D̃) | Same evaluator/output blocks, expanded captions | 2.3; evaluator part of step 8; 5.1 | E3: prospective secondary mapping; no new execution requirement and no dropping unsupported outcomes |

E0–E5 are specified in `experiments/EXPERIMENT_MATRIX.md`. Conditional stage rates are descriptive, not causal mediation effects. The compressed action-value identity is prior foundation, not a new theorem, a Macro-F1 decomposition or an estimator from action counts.

## Native meaning of the grounded endpoint

For a resolved accepted diagnosis, G=1 requires both native submission-output fields to equal numeric 1:

- `submission_grounding`: the submitted class agrees with the selected numerical prediction for the task sample.
- `artifact_lineage_completeness`: that prediction's required feature references are included in the submitted supporting references.

The runtime also requires a legal diagnosis label and a nonempty supporting-reference list for acceptance. Acceptance does not require either of the above fields to be 1. This is why a correct but unsupported accepted label can contribute to operational Macro-F1.

For the secondary mapping, accepted labels with G=0 become `no_submission`; true classes, assigned episodes and the three-class averaging set do not change. Resolved terminal non-submissions already have that scored label. Missing or malformed support fields in an accepted outcome are unresolved, not inferred zeros. Such a record can leave only the secondary endpoint unresolved when the operational record is otherwise complete. A genuinely indeterminate attempt blocks any full-cohort endpoint requiring its final outcome. Never replace an attempt, silently drop a row or create a fourth diagnosis class.

This criterion verifies numerical agreement and required-feature inclusion. It does not guarantee physical validity, correct diagnosis, validity of every extra reference, or a complete semantic explanation. Keep native `supporting_reference_validity` as a separate diagnostic rather than silently adding a new threshold to G. Use the native selected prediction reference; do not search retrospectively for a more favorable one.

The secondary definition is fixed by this revision before this work inspects four-condition outcomes. It is **specified, not yet implemented and validated as a cohort endpoint in Benchmark**. Recompute it from native canonical evidence only after the shared extractor and metric path are validated. Historical operational scores and result records must remain unchanged. Secondary claims do not inherit the primary two-contrast Bonferroni allocation.

## Figures: purpose and contract

**Figure 1 — Problem formulation and observation boundaries (Section 2.3).** Distinguishes X, Z, τ/T, private c, outcome Y and cohort M(D). The revised caption explains that the grounded endpoint is another mapping of the same evaluator outcome, not a new feedback path. Every displayed variable is defined in the text. Dependencies do not identify causal mediation. No controller architecture is introduced here.

**Figure 2 — PHMGraph overview and execution loop (Section 3.1).** Separates shared history, full B, fixed model and numerical tools from adapted progress f and independently configurable i/g. The gate's model and executor branches receive the same menu. Nonterminal feedback, submission and evaluator-only outcome assessment map to Algorithm 1. The pointer and gate are decomposed in Sections 3.2–3.4.

Both existing SVG assets are retained unchanged; captions and the mapping above are updated. No third figure or new state is needed. Editable text and semantic groups remain in the existing vector artwork. The sole drawing source is `scripts/figures/plot_phmgraph_formulation_method.py` in Benchmark; no drawing or runtime implementation is copied here. The reference Nature-figure skill informed this decision to retain the existing diagrams rather than add decoration.

## Exact inspected implementation snapshot

Repository: `liq22/phm-agent-benchmark`.

Commit: `8206cfef540d5f602adba482e9dcc0ebd6b0f437`, **unmerged Draft PR #20** at this inspection. This is an inspected implementation snapshot, not released-runtime or installed-method acceptance. Merging this paper revision does not accept PR #20 or its dependent implementation deletions.

| Source at that commit | Blob / scientific role |
|---|---|
| `src/phm_graph_agent/components.py` | `0a824598216b04471afabd66d1667ce8f4f93bd0`: full B01–B06 catalog, appended active-block sentence, shared history sanitization |
| `src/phm_graph_agent/agent.py` | `72927562b055e2cbb7141f03e0db57cec47bcb22`: ordinary phase menus and separately defined dynamic menus |
| `src/phm_graph_agent/state.py` | `4272b5b748853009327b7c4a1208ae79714684e8`: progress precedence, recovery and sample-bound replay progression |
| `src/phm_agent_benchmark/research/conditions.py` | `aee6e1dd1349652140294d610588c01183b70802`: four interfaces and conditional contrast definitions |
| `src/phm_agent_benchmark/phase1/agents.py` | `86f896d69ebfbcaadbcab2d6b9b485198aaef148`: one-request decisions and allowed-tool metadata |
| `src/phm_agent_benchmark/phase1/runtime.py` | `c005f90ab9d042fd95ae69f457083dae40ac1537`: exact feature checks, prediction references, acceptance and native grounding fields |
| `src/phm_agent_benchmark/phase1/environment.py` | `a2e0f9547888d3377a27cbd442051a05f2aa5817`: broader adapter actions and native terminal boundaries; do not infer recovery from state logic after termination |
| `configs/paper02_graph/indexing_first_attempt.yaml` | Authoritative configuration for this draft snapshot; smoke, not a confirmatory design |

The declared global experiment surface is the eleven Phase-1 tools listed in `paper.yaml`. Verify the actual presented and admitted names when binding the installed method; the broader adapter's `artifact.describe` and `stop` must not enter only the global arms. Do not silently expand the comparison to thirteen tools.

Primary diagnosis uses one raw window and a fixed numerical contract. Source inspection confirms strict feature-name, raw-source and spectral-path checks; the actual set of useful alternative computations remains an empirical question. Replay's eleven successful operator-call threshold is neither eleven distinct features nor a sufficiency certificate.

## Prior-art reading and source versions

The manuscript retains the existing citation keys rather than inflating its bibliography. StateFlow (arXiv:2403.11322v5, background/method and state ablations) establishes state-driven execution as prior work. TimeSage-MT (arXiv:2606.01498v1, Sections 4.1–4.4) supplies paired system comparisons and distinct outcome/capability assessments. PHMForge's accessible HTML identifies itself as arXiv:2604.01532v2; Appendix H supports the stated verification, distractor and discovery controls. This revision cites that inspected v2 rather than claiming to have reread the inaccessible v3. Standard policy-value notation follows Schulman et al. (2015). These sources support positioning; their performance values are not transferred to this PHM cohort.

## Historical outputs and empirical continuation

The schema-version-1 manifest remains byte-for-byte at `legacy/graph_v6_manifest.yaml`, blob `9930405db6b41ce0a4a743285dc97defb696706a`. Its profiles and six original insertion-marker pairs retain their meanings. This revision does not run historical renderers or rewrite results.

Next: E0 real waveform/assignment/native-outcome acceptance; E1 provider-free numerical headroom on reserved development data; E3 native secondary-endpoint validation; then the approved four-condition E2 pilot and E4 trace analysis. Freeze E5 before confirmatory execution. Normal PR #20 integration and rebinding to a validated Benchmark dev commit require its own acceptance gates. Do not substitute metadata readability, portable fixtures, figure rendering or this paper merge for that evidence.
