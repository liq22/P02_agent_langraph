# Paper 2 — State-guided control versus action-set restriction

Method owner: `liq22/P02_agent_langraph`, dev. Base and dynamic profiles remain distinct. A graph representation is not itself a new algorithmic contribution.

## Question and candidate contributions

When do state cues and tool constraints improve PHM decisions, and when do they remove necessary analysis? [GOAL](GOAL.md) selects the next experiment; [literature roles](LITERATURE_MAP.md) locate the closest control methods.

1. A finite-horizon decomposition into action-set loss and within-set selection loss.
2. A state-cue-by-tool-filter factorial design over unchanged global numerical capabilities.
3. Task evidence for useful control, harmful filtering and behaviorally ineffective ablations.

## Abstract — research-stage wording

State-guided PHM agents combine decision cues with restrictions on available tools. These components can improve selection while removing actions needed for a task. We analyze their trade-off in a fixed finite-budget environment. A Bellman telescoping identity separates lost value from filtering the action set and from choosing within the retained set. We also give a distributional equivalence criterion for ablations that leave the conditional action policy unchanged. A cue-by-filter factorial experiment tests these mechanisms through matched PHM task outcomes and costs. The theoretical quantities motivate controlled comparisons; real task effects, including harmful masks, determine the practical value of graph control.

## Introduction: detailed semantic units

| Paragraph | Main point | Development |
|---|---|---|
| I1 | Long-horizon diagnosis is a sequence of hypothesis updates, not a single label. | The current task releases bounded windows and numerical results. Identify where a wrong branch can persist. |
| I2 | ReAct, Reflexion and StateFlow already organize tool-using agents. | Use `yao2023react`, `shinn2023reflexion` and `wu2024stateflow` as direct prior work for tool loops, feedback and state-driven workflows. |
| I3 | Graph guidance typically changes more than topology. | Current-state prompt and visible-tool subset are two mechanisms. Treating their joint effect as a pure topology effect is invalid. |
| I4 | Restricting tools is beneficial only if useful actions are retained. | Introduce action-set loss and within-set selection loss; the known-value finite example verifies their decomposition. |
| I5 | A compact state can also merge histories requiring different decisions. | Connect state aliasing to available history and check whether a no-memory intervention actually changes the conditional policy. |
| I6 | State the matched factorial question. | Fixed base model, PHM knowledge, release sequence, global tools, budgets and evaluator. |
| I7 | Tie contributions to experiments. | Joint effect, state/filter separation, horizon-dependent limits, dynamic public-event extension. |

## Method

Let $z_t=f(h_t)$ be the selected decision state. The treatment controls a state cue $C(z_t)$ and a visible action mask $A(z_t)$. The four new conditions are $C\in\{0,1\}$ by $A\in\{0,1\}$. They all retain the same numerical tools and private-target boundary.

The original `graph` condition is preserved. `graph-components` creates four explicitly new policies. For all four, historical `decision_state` fields are removed from provider-visible tool messages; otherwise a filter-only arm would still see graph cues in history. The canonical rollout still records states for analysis. State-only removes schema filtering, filter-only removes the state suffix, and combined applies both. These are new conditions, not retroactive reinterpretations of previous runs.

The base profile reaches six states and does not receive a public condition event. Its `Monitor` and `Revise` states cannot support a dynamic finding. The separate dynamic-v3 profile receives an opaque operating-condition-change event at a registered release position. It is an externally signalled change, not an anomaly label inferred from raw signal.

[theory/03_control_loss.md](theory/03_control_loss.md) defines nonnegative mask and selection losses using the unrestricted $Q^*$. Their expected finite-horizon sum equals the policy value gap. The real PHM $Q^*$ is unknown, so task contrasts and concrete filtering consequences provide the empirical evidence. Invalid-call rates remain rollout diagnostics.

## Experiments

| ID | Entry / status | Question |
|---|---|---|
| G-E1 | `graph` / implemented | Original reactive Generic vs original joint graph |
| G-E2 | `graph-components` / implemented | State cue, mask, and interaction in the new sanitized-history 2x2 |
| G-E3 | inspect reachable history/state/tools before `graph-memory` | Run a cohort only if the ablation changes provider-visible behavior or conditional actions; otherwise record non-identification |
| G-E4 | `horizon --tasks replay` / implemented | 2/3/5 windows with declared horizon-scaled budget; total budget is a confound to analyse, not conceal |
| G-E5 | existing dynamic-v3 runner / separate | no-revision/no-branch/no-memory/no-replanning under the same explicit public event |
| G-E6 | prespecified repeated trials | task effect and repeated-run variation, not a single successful graph |

Primary metrics remain task outcomes. Completion, repetition, state transitions and cost explain the result but cannot replace it. For fixed-total-budget horizon sensitivity, save a separate budget profile; the supplied horizon command uses budget proportional to horizon so it measures scaling at approximately fixed resource per window.

Comparators: unchanged Generic, Scripted, original Graph, four component arms, no-memory. StateFlow is the closest architectural prior; a faithful reimplementation needs its own state/prompt and budget specification and is not represented by merely renaming our Graph. ReAct/Reflexion serve as additional Agent methods only when their actual actions and extra calls are implemented and counted. No cross-benchmark leaderboard numbers are transplanted.

## Results, limitations and figures

Report original joint effect first, then the new component effect, then horizon and costs. Do not pool original and sanitized-history controls. Negative mask effects are scientifically informative. A constant or unreachable-state ablation must be reported as non-identifying, not as a successful ablation.

Figures: state/control boundary; 2x2 paired effect; horizon/task/completion curves; retained versus excluded tool classes; a released-window revision example only if actually observed. No graph image is evidence for improved reasoning. The main decomposition and ablation criterion are in [theory/03_control_loss.md](theory/03_control_loss.md); retention and state-aliasing notes provide additional context.
