# Graph TII/MSSP experimental contract

Existing historical P2 cohorts are not relabelled. P02 owns this scientific specification; Benchmark owns all executables. Use `experiments/graph_control` and `configs/paper02_graph` in Benchmark, not a second P02 runtime.

| ID | Hypothesis / competing explanation | Manipulation and estimand | Status / mapping |
|---|---|---|---|
| G-T1 | Simultaneous coverage bounds mask loss | Exact values and covering intervals; true loss versus C | Original 24 rows reproduced; `run.sh theory/toy` |
| G-T2 | Narrow intervals alone provide coverage | Deliberately uncovered intervals; actual loss versus asserted bound | Bound 0, actual loss 0.85; retained negative example |
| G-T3 | Lower exclusion bound implies policy improvement | Valid intervals; same uniform selector over progressively expanded masks | New 3 rows; C 0.2/0.1/0, return 0.8/0.4/0.5667; `run.sh counterexamples` |
| G-T4 | More masked logs identify omitted action values | Two worlds with zero omitted-action probability; full logging-law enumeration | New 6 rows; total variation 0, mask loss 0/0.45; `run.sh counterexamples` |
| G-P1 | Original Graph changes task performance | Same model/data/knowledge/tools/budget; Graph-minus-Generic task statistic | Shared main config exists; real integration/cohort pending |
| G-P2 | Cue and filtering have distinct effects | Four cells; both simple effects for each factor and difference-of-differences | Complete contrast definitions; analytical algebra tested; no new PHM effects |
| G-P3 | Relevant filtering matters beyond tool count | Correct versus equal-size irrelevant mask, without test-label access | Explicit condition still missing; compare task outcomes, not an asserted observed Q* |
| G-P4 | Persistent state/revision changes behavior | Direct Graph-minus-no-memory, after reachable-behavior check | Direct contrast fixed; base may be inactive; dynamic dispatch missing |
| G-P5 | Benefit depends on actual horizon | Nested prefixes; fixed-total and fixed-per-window budgets separately | Prefix binding pending; current horizon is mixed sensitivity |
| G-N1 | Numerical capability, not controller, limits outcome | Same classifier on time/PSD/envelope; validation-selected best single | Graph expert-pool admission pending; original pool unchanged |
| G-N2 | Static fusion or numeric routing explains gain | Frozen validation-fit fusion and train-only router; shared representation bank | Central numerical work remains a separate axis; not yet an admitted Graph PHM comparison |
| G-N3 | Strong numerical reference removes Agent advantage | MOMENT, with appropriate MiniROCKET diagnosis / Deep SVDD anomaly controls | Faithful reproduction, checkpoints and Graph-pool admission pending |
| G-A1 | Training loss changes the graph effect | Current graph is training-free | Graph-loss ablation N/A; a learned gate is a different method |
| G-A2 | Structure, statistics, interpretation and cost explain effects | Cue/filter, relevant mask, budgets, retained failures and source-grounded calls | Reuse shared evaluator; grounding is not proof of physical causality |
| G-X1..5 | Control transports beyond vibration | Five separately admitted domains and matched within-domain policies | Acquisition and binding pending; see below |
| G-S1 | Effects repeat across physical units and trials | Paired asset-block uncertainty; all assigned outcomes and all-attempt expense | Requires real cohorts; no selected best attempt |

## Numerical capability versus control

Reference models and Scripted establish the fixed numerical capability. Best-single representation is selected on validation, not per-test ground truth. Static-fusion weights and numerical routers are fitted without test access; their training and execution costs are included. Every admitted numerical capability is available to every compared Agent. The main cue/filter intervention changes only the policy.

The original toy's time/spectrum/envelope labels designate abstract actions with specified reward probabilities. Static uniform selection is not probability fusion; the oracle is analysis-only. The new exact counterexamples are not checkpointed predictors, Agent task results or sample-based confidence estimates.

## Five external domains

The current Graph-paper specification uses PTB-XL ECG (patient-disjoint multilabel targets), UCI HAR inertial signals (subject groups), SMAP/MSL spacecraft telemetry (ordered streams), SMD server telemetry (machine groups), and SWaT process instrumentation (one plant with ordered periods). These are five domain families, not five extra mechanical test sets. DATA_DOWNLOAD_SOP records primary sources, versions, licensing/access and conversion requirements. None is admitted into the shared Graph runtime in this continuation; public availability does not establish task/evaluator compatibility. Existing central single-label numerical consumers must not silently collapse PTB-XL targets or replace this protocol with another ECG dataset.

## Baseline fidelity and ablations

Start with unchanged Generic, Scripted, original Graph and four component cells. StateFlow needs its state/output/prompt mechanisms and refined-prompt control. Reflexion needs its permitted feedback/memory loop and all associated calls. A renamed local graph or an added reflection sentence is not faithful reproduction. Learned representation/loss, tool relevance, dynamic event structure, horizon, statistical units, explanatory measurements and costs are separate manipulations; do not change several to rescue a failed hypothesis.

## Estimation and claims

Let theta_cf be the declared cohort statistic for cue c and filter f. Report theta_10-theta_00, theta_11-theta_01, theta_01-theta_00, theta_11-theta_10, and their common interaction theta_11-theta_10-theta_01+theta_00. Original Graph-minus-Generic is a different contrast because the factorial cells share history sanitation. Memory uses Graph-minus-no-memory on the same assignments; an inactive switch is reported as such.

Freeze task metric/cohort before test. Recompute Macro-F1/AP in paired, identically drawn asset-block resamples; do not average episode F1/AP or treat adjacent windows/channels as independent equipment. Report undefined resamples, failures and complete denominators. Primary task effects do not identify latent mask-loss mediation. Direct intervention results, numerical capability and logged process explanations stay distinct.

## Artifact mapping

Real runs use the existing six-file episode bundle and shared metrics/effects CSV. Exact G-T1/T2 use their original config/toy/counterexample files; G-T3/T4 use `results/graph_control/boundaries_20260916/{design.json,expansion.csv,support.csv}` in Benchmark. Main Sections 4.3 and 7.2–7.3 correspond to those new calculations. Figures read these CSVs directly. All failures and negative cases remain, and neither unimplemented adapters nor test counts support a PHM superiority claim.
