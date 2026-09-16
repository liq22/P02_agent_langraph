# Graph TII/MSSP experimental contract

A changed condition requires a new declared experiment. Existing historical P2 cohorts are not relabelled. Executable code belongs to Benchmark; this file is the scientific specification. `experiments/p19` is a borrowed representation-project path, not this paper's implementation location. Use Benchmark `experiments/graph_control` and its existing `configs/paper02_graph`.

| ID | Hypothesis or competing explanation | Manipulation and estimand | Status / executable mapping |
|---|---|---|---|
| G-T1 | A valid conditional certificate bounds mask loss | Exact Q and covering intervals; compare true loss with C | Executed: 24 finite-model rows; `run.sh theory/toy` |
| G-T2 | Uncalibrated intervals invalidate the bound | False intervals held fixed; actual loss versus zero certificate | Executed: bound0, actual loss0.85; not PHM |
| G-P1 | Original graph changes task performance | Same provider/model/data/budget; Graph-minus-Generic cohort metric | Shared main/components configs; not executed in this revision |
| G-P2 | State and visibility have distinct effects | Cue0/1 × filter0/1, same history sanitation; main effects and interaction | Migrated component factory exists; full installed integration pending |
| G-P3 | Mask helps because of relevant selection, not just fewer tools | Correct state mask versus equal-size irrelevant mask; never use test-label oracle in Agent | Additional explicit condition not implemented; retain as missing experiment |
| G-P4 | Memory/revision manipulation is active | Compare reachable state/action visibility before a cohort; separate public event profile | Base may be inert; dynamic dispatch missing |
| G-P5 | Graph benefit varies with actual length | Same longest sequence nested prefixes; fixed-total vs fixed-per-window budgets | Prefix binding not implemented; existing horizon is only mixed sensitivity |
| G-N1 | Numerical ceiling rather than controller limits outcome | Same classifier on time/PSD/envelope; best single selected on validation | New numerical-pool condition; existing fixed ten-feature pool unchanged |
| G-N2 | Static fusion or dynamic numeric routing already explains gain | Fixed/validation-fit probability weights; train-only router, identical representation bank | Not implemented; no representation-superiority claim |
| G-N3 | Strong numerical reference removes apparent Agent advantage | MOMENT; optionally MiniROCKET diagnosis or Deep SVDD anomaly | Official-source reproduction needed; results absent |
| G-A1 | Controller objective changes outcome | There is no trainable graph loss in current method | Loss ablation N/A; learning a gate would introduce a new method |
| G-A2 | Structural, statistical, interpretive and cost alternatives | Cue/filter, masks, budgets; failed outcomes retained; source-bound call and latency analysis | Current stats reuse shared evaluator; do not equate grounding with physical causality |
| G-X1..5 | Control transports beyond vibration | Five distinct external domains below, matched tasks within each domain | Sources verified; none admitted into shared runtime here |
| G-S1 | Effect is repeatable across assets, models and trials | Asset-block paired uncertainty; all assigned outcomes and all-attempt expenditure | Requires real model/data; no selected best attempt |

## Reference-model axis versus Agent-policy axis

Reference is the frozen existing numerical pool and Scripted path. Best-single representation is chosen on validation, not by per-test true labels. Static fusion uses frozen weights fitted without test access. Dynamic numerical routing is trained only on training/dev data and consumes its own cost. These change numerical capability and must be available to every compared Agent. The main cue/filter contrast changes only the policy, with that capability fixed. A learned loss or representation is not added simply to satisfy a generic ablation list.

In the executed toy, 'time/spectrum/envelope' are action labels with specified reward probabilities. `static_uniform` randomizes an abstract route; it is not implemented probability fusion. `oracle_dynamic` is analysis-only. Do not put their returns in the PHM benchmark table.

## Baseline fidelity

Use Generic, Scripted, original Graph and four component cells first. StateFlow has actual state prompts/output functions and a published refined-prompt control; a faithful comparison reproduces its mechanism and accounts for all calls. Reflexion needs its feedback/memory loop under permitted feedback, not a one-sentence 'reflect' suffix. Both remain reproduction tasks. Recent or expensive backbones are not automatically PHM SOTA. Report model IDs, sampling settings, observable tool contracts and actual cost; no automatic provider switching.

## Statistics

Freeze primary task metric and expected cohort before test; keep existing historical scoring separate. Diagnose with Macro-F1, anomaly/replay with declared assigned-population score. Conditional performance, coverage and registered penalties are distinct quantities. Preserve stops, invalid submissions, budget exhaustion and provider failures. Repeated trials stay within the physical asset/subject/machine block. Data channels and adjacent windows are not independent assets. Main-effect and interaction CIs use identical bootstrap draw indices; no per-episode F1/AP averaging. Report undefined resamples and no-op ablations.

## Required artifact / claim mapping

Real Agent runs use Benchmark's existing six-file episode bundle, config snapshot and derived metrics/effects CSV. Paper figures cite exact experiment IDs and artifact paths; raw data are not copied here. Theory runs are a separate exact-model class with config.json, toy.csv and counterexample.json. A notebook, download command or renderer smoke is not an external benchmark result. Until real cohorts finish, the paper can claim only the conditional analysis and its finite-model verification.
