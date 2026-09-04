# Paper 2 Reproducibility Contract

The authoritative task, split, sampling, window, and public-visibility source is
`../p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml`.
Goal-pack protocol copies are planning material and are not consumed by the Graph
experiment runner.

The active provider-bound launcher owns only the Benchmark Generic P0 prefix:
`../p01-phm-agent-benchmark/paper/experiments/run_formal_paper0_v6.sh`. The
Graph script is a single-arm implementation entry point; it must not replace
the Benchmark launcher, the provider-free downstream schedule, or the cohort
gates. P1/P2 execution is projected separately by
`../p01-phm-agent-benchmark/paper/experiments/schedule_downstream_formal_v2.py`.
Given its public schedule JSON, the Benchmark-owned executor derives the exact
completed prefix from canonical artifacts without credentials, private-path
arguments, authorization flags, or provider calls:

```bash
python ../p01-phm-agent-benchmark/paper/experiments/execute_joint_primary_schedule_v1.py \
  --schedule '<ABSOLUTE_PUBLIC_JOINT_SCHEDULE_JSON>' \
  --check
```

The required P0-only stamp records the separately excluded P0 authority; it does
not make that profile or its roots eligible for joint control or pooling. The
fresh schedule contains 45 inert commands over 15 units and three arms:
Benchmark Generic, PHMskills, and Graph. Twelve core units contribute 36 jobs
and three monitoring units contribute nine jobs. Generic executes once per unit
and supplies the common P1 and P2 control. The emitted plan remains
`execution_ready=false`, reports `provider_calls=0`, and is neither inference
nor result evidence. Benchmark has locally implemented the serialized
exact-prefix inspector/executor; the joint scheduler, acceptance producer, and
executor contract suite passes 43/43. The current formal source revisions are
dirty or unpublished and therefore fail the committed-clean, remote-contained
gate. In addition, P1/P2 joint provider/public-context egress has not been
separately authorized, a fresh exact-route/model zero-price two-turn admission
report is not bound, and 0/45 jobs have executed.

For clarity, the following is the gated command shape, not an authorization or
a command to run in the current state. Both authorization variables require
explicit approval, and the three execution-only private paths are deliberately
nonexistent placeholders:

```bash
PHM_EXTERNAL_INFERENCE_AUTHORIZED=1 \
PHM_JOINT_EXTERNAL_INFERENCE_AUTHORIZED=1 \
python ../p01-phm-agent-benchmark/paper/experiments/execute_joint_primary_schedule_v1.py \
  --schedule '<ABSOLUTE_PUBLIC_JOINT_SCHEDULE_JSON>' \
  --execute-next \
  --formal-provider-admission-report '<ABSOLUTE_PRIVATE_FRESH_ADMISSION_REPORT_JSON>' \
  --metadata '<ABSOLUTE_PRIVATE_PADERBORN_METADATA_PATH>' \
  --signal '<ABSOLUTE_PRIVATE_PADERBORN_SIGNAL_PATH>'
```

Even after those gates are separately satisfied, one `--execute-next`
invocation may start at most the single canonical next job.

Paper 2 uses runtime contract
`phase1_opaque_sample_vibration_feature_schema_v6`. Public task observations and
rollouts contain opaque sample handles but no bearing identifier or private target.
Each successful `op.run` result carries the `source_sample_id` inherited from its
source artifact, including chained operator outputs. For every `band_power`
feature, v6 linearly interpolates the PSD value at the exact requested low- and
high-Hz endpoints before trapezoidal integration. Evaluator-side experiment
records retain `bearing_id` only for split alignment and bearing-clustered analysis;
that value is not placed in the Agent's task observation, tool results, or policy
history.

The shared provider-free v6 Scripted references are complete. The core gate at
`../p01-phm-agent-benchmark/paper/experiments/results/deterministic_runbundle_v1/scripted_matched_cohort_acceptance.json`
accepts 64 episodes, and its canonical summary is
`../p01-phm-agent-benchmark/paper/experiments/results/deterministic_runbundle_v1/scripted_matched.json`.
The replay gate at
`../p01-phm-agent-benchmark/paper/experiments/results/deterministic_runbundle_v1/scripted_monitoring_cohort_acceptance.json`
accepts eight episodes, summarized in
`../p01-phm-agent-benchmark/paper/experiments/results/deterministic_runbundle_v1/scripted_monitor_matched.json`.
These artifacts verify the common v6 numerical and deterministic rollout basis;
they contain neither the Benchmark Generic LLM control nor the Graph LLM
treatment and therefore cannot estimate the Paper 2 treatment effect.

`scripts/run_graph_experiment.py` consumes the production protocol by default.
`ReactiveSequentialAgent` is a direct, zero-behavior-override subclass of the
Benchmark `GenericLLMToolAgent`. `GraphDecisionAgent` is derived directly from
the same Generic base and adds only registered current-state guidance and
state-specific visibility over the unchanged global tool catalog. Neither
production arm imports P1 runtime code or carries P1 bundle provenance.
Every episode attempt is immutable below
`episodes/<rotation>/<sample>/<task>/attempt-NNN/` and contains exactly
`run.json`, canonical `rollout.jsonl`, `submission.json`, `metrics.json`,
`failures.jsonl`, and `artifacts.json`. The unit root retains evaluator-private
`evaluation.jsonl` plus derived `summary.json` and `run_manifest.json`; it does
not contain a competing root rollout, state trajectory, or provider-failure
archive. Provider errors remain exact-six attempt leaves, and a matched-profile
retry writes a new attempt. Graph state summaries are recomputed from
`decision_state` on canonical action records. The Benchmark Generic
(Reactive-equivalent) control and Graph arms use the same Generic base prompt,
data, numerical experts, runtime, budgets, seeds, and episode order. Every new
bundle records the versioned experiment, matched
control, agent-control, and implementation identities. Resume fails closed on
missing or mismatched identities, so historical PHMskills-derived Graph leaves
cannot be reused or mixed. Formal aggregation requires an accepted complete
Generic-base cohort under v6. Known v1, v4, and v5 rows, historical MockLLM
runs, pilots, and incomplete provider-bound prefixes do not support the active
treatment claim.

P2-E0-v2 has an accepted provider-free real-data Generic-base adapter/world
mechanics gate for the fixed seed-20260808 rotation-0 slice. Running
`PYTHONDONTWRITEBYTECODE=1 python scripts/analyze_p2_e0_generic_base_adapter_equivalence_v2.py`
rebuilds
`paper/experiments/results/p2_e0_generic_base_adapter_equivalence_v2.json`
without a provider call. It accepts 16 matched statistical keys per arm,
verifies 32 exact-six leaves and 352 canonical actions per arm, and observes all
16 units in each arm submitting. TaskSpec, budget, full-rate window, sampling,
evaluator, model identity, numerical-model selection, validation scores, and
global action surface match. The gate also verifies direct Generic inheritance,
zero Reactive behavior overrides, registered Graph control only, and no P1
runtime import or bundle provenance. This closes mechanics only and supplies no
P2-E1, performance, reliability, dynamic, horizon, ablation, or transfer result.
The earlier PHMskills-derived E0 artifact is historical and non-authoritative.

The P2-E1 authority is `paper/experiments/p2_e1_generic_base_formal_v2.yaml`.
Its four joint-primary timestamped roots are explicit Generic-core,
Generic-replay, Graph-core, and Graph-replay finalizer inputs. The provider
execution path is the Benchmark-owned 45-job schedule
`p1_p2_joint_primary_counterbalance_v1` under profile
`p1-p2-joint-primary-v1`; the P0 B3 profile is rejected. Each Graph command
carries the scheduler's exact 13-field identity, and the runner independently
reconstructs seed, rotation, scope, unit, position, ordinal, predecessor, and
output before persisting both that object and the derived
`joint_graph_core|joint_graph_replay` scope. Graph-first execution validates the
committed local Benchmark/Data-Factory topology without requiring its later
same-unit Generic comparison to exist. Supplying that Generic unit later causes
an additional schedule-identity, completion, and topology cross-check.

Formal joint OpenAI execution requires both
`PHM_EXTERNAL_INFERENCE_AUTHORIZED=1` and the separate
`PHM_JOINT_EXTERNAL_INFERENCE_AUTHORIZED=1`, the exact registered OpenRouter
route/model, explicit zero input/output prices, and a fresh official two-turn
provider-admission report. Benchmark's locally implemented exact-prefix
executor injects the report, metadata, and signal paths only at execution and
starts at most one canonical next job. Its focused scheduler, acceptance, and
executor contract suite passes 43/43. The current dirty or unpublished formal
source revisions, absent separate joint authorization, absent fresh report,
and 0/45 execution state keep `execution_ready=false`; no joint provider call
or outcome exists.

`scripts/finalize_p2_e1_generic_base_formal_v2.py` validates every cohort index
against its canonical exact-six leaves and preserves provider attempts outside
the statistical denominator until a same-profile retry terminates. It binds the
replay analysis to `phase1_replay_target_adverse_missing_score_v1`, retains all
assigned windows in the replay task population, and registers replay
`task.average_precision` as the study primary. Its 2,000-resample absolute and
paired bearing bootstraps use the shared Benchmark analysis seed `20260808`;
the earlier local `20260820` registration was corrected before any accepted
P2-E1 result existed. It first requires an accepted
`joint_primary_schedule_acceptance_v1` artifact and exact five-field pairing
over `seed`, `rotation`, `bearing_id`, `sample_id`, and `task_id`. Once that
schedule gate, all four arm gates, and both pairing gates accept, it emits four absolute arm summaries and two paired
bearing-bootstrap results in the single combined result file. That accepted
result also carries the validated protocol identity, resolved Benchmark control
stamp, frozen model profile, registered design, analysis contract, and exact
canonical Benchmark/Data Factory/P2 Git topology. The
finalizer publishes readiness and result together with exception rollback.
The `--combined-result` mode of
`scripts/render_graph_manuscript_table.py` requires the frozen protocol and an
explicit expected formal stamp, rejects external state overrides, recomputes
every displayed Graph-minus-Generic point and replay assigned-window identity,
and deterministically produces the primary table, core SVG, canonical Graph
state JSON/Markdown, full-cohort replay-mechanism JSON, and marked manuscript
blocks as one group with exception rollback.
The active publication path rejects legacy multi-file inputs and writes only the
paths declared by the protocol. The replay mechanism projection is generated
only from the accepted combined result, binds all 24 exact replay pairs, and
forbids external case overrides, hidden-target selection, and reasoning-trace
inputs. Finalizer checks pass 16/16 and consumer checks pass 20/20, including a
complete 192-core/24-replay-per-arm analyzer-to-publication fixture. The
checked-in readiness snapshot records that no external-root audit was performed
and therefore contains no effect estimate. Historical PHMskills-derived and
retired-layout roots are excluded from the active comparison.

The Generic-base dynamic-ablation v3 profile makes target-adverse assigned-window
Average Precision the task-primary endpoint and treats grounded completion as a
secondary rollout measure. Each seed-level endpoint is recomputed across all
eight held-out bearing sequences; bearing-cluster bootstrap and exact 256-way
matched swaps recompute the nonlinear metric. Failed and partial episodes keep
their assigned windows under `phase1_replay_target_adverse_missing_score_v1`.
The shared Benchmark emits the generic `public_condition_event` under its
opt-in `phase1_public_condition_event_v1` contract, and P02 maps the released
event into the full and four registered Graph profiles.

The unchanged dynamic-v2 Mock gate remains the mechanics source: ten
sequence-0001 exact-six bundles on local Paderborn windows validate matched
release-bounded events, profile legality, no-persistent state stripping, and
zero provider calls. Dynamic-v3 uses the isolated runtime identity
`phase1_graph_dynamic_generic_ablation_v3` and new formal roots. Its scheduler
emits 240/240 dry commands and invokes none; validate-only reads no provider
environment or probe evidence and writes no result. Runner checks pass 19/19,
the current dynamic-related aggregate passes 57/57, and formal coverage is
0/240. The
accepted-only analyzer rebuilds all eight private 12-window masters through
the registered Paderborn DataPort using `--private-metadata-env` and
`--private-signal-env`, uses canonical rollout successful-submit prefixes as
prediction authority, and ignores runner-derived `evaluation.jsonl` for
targets and effects. Private paths and assignments are not serialized. V1 and v2
formal profiles remain historical and separate from v3 and active v6.

The extension studies remain at provider-free readiness:

- P2-E2 horizon-v3 projects the task-primary dynamic-v3 endpoint over 144
  registered units and emits 144/144 dry commands, with zero executions and
  results;
- P2-E9 reliability-v2 registers 80 matched pairs/160 episode bundles. Its
  dedicated runner contract is ready and the validate-only dry schedule emits
  160/160 inert commands, invokes none of them, makes zero provider calls and
  zero writes, has zero results, and passes 12/12 focused tests. The wrapper
  serializes provider execution across the reliability profile, uses unique
  temporary files, and leaves already stamped attempt records unchanged. The pre-result
  analyzer correction makes target-adverse `task.average_precision` primary,
  recomputes it over all 24 assigned windows within each repeat, requires
  registered private DataPort targets through `--private-metadata-env` and
  `--private-signal-env`, ignores derived `evaluation.jsonl` authority, and
  retains grounded pass@1/pass-all-10 as explanatory reliability diagnostics;
  and
- P2-E8 cross-dataset-v3 registers the accepted Ottawa ordered-state target and
  CSV DataPort. Its provider-free preflight emits 18/18 commands for 72 episode
  bundles, 36 exact matched pairs, and 216 assigned windows. The accepted-only
  analyzer independently reconstructs private assignments and refuses any
  partial cohort before the 2,000-resample bearing-clustered analysis. The
  analyzer/scheduler/runtime checks pass 22/22, but no command has run and no
  result exists; the external provider execution remains unauthorized.

Accepted complete cohorts are required for the registered horizon, ablation,
cross-dataset, reliability, and Graph-effect estimates.

After the P2-E8 analyzer accepts all 72 Ottawa bundles and writes the registered
result, its provider-free manuscript consumer is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:src:../p01-phm-agent-benchmark/src \
  python scripts/render_graph_cross_dataset_manuscript.py
```

The consumer reads only the protocol, accepted `formal_result.json`, and active
manuscript. It does not inspect the 72 raw bundles, private DataPort inputs, or
provider environment. It rechecks the embedded arm acceptances, 36 exact
pairs, 108 assigned windows per arm, target-adverse accounting, five displayed
task deltas, and physical-bearing bootstrap metadata. The protocol fixes the
result, table, SVG, and manuscript paths. Result schema v2 records a canonical
run root equal to the scheduled base plus formal stamp. The consumer requires
lexical and resolved source containment, rejects aliases and publication under
raw/result roots, and accepts existing targets only as ordinary single-link
regular files. Its production CLI accepts only the registered protocol and
keeps resolved outputs in the repository. It stages and fsyncs all three
outputs, preserves existing modes, and restores replaced files in reverse
order after a failure. Its 18/18 focused checks include direct analyzer
integration, provenance, staging cleanup, rollback, and idempotence. With
formal coverage 0/72, it has emitted zero rows and the result assets remain
absent.

After the isolated P2-E9 gate accepts all 160 bundles and the analyzer writes a
matching result, its provider-free manuscript consumer is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=.:src:../p01-phm-agent-benchmark/src \
  python scripts/render_graph_reliability_manuscript.py
```

The consumer reads only the protocol, `formal_acceptance.json`,
`formal_result.json`, and active manuscript. It does not read canonical run
bundles, DataPort inputs, or provider credentials. It rechecks the 80 matched
pairs, ten repeat rows, target-adverse task-primary deltas, pass@1 and
pass-all-10 projections, selected rollout/cost deltas, and primary-cohort
isolation before updating `paper/assets/tables/p2_e9_reliability_results.md`,
`paper/assets/figures/p2_e9_reliability_primary.svg`, and the unique
`P2_E9_RELIABILITY` marker under the same protocol-bound, fully staged,
mode-preserving publication contract. The result root must equal the protocol
formal root; every table interval includes its valid/2,000 bootstrap count.
Existing targets must be ordinary single-link regular files, source
containment is both lexical and resolved, the production CLI fixes the active
protocol, and resolved outputs stay in the repository. Its 20/20 focused
checks include direct 160-bundle analyzer integration, provenance, path and
protected-root rejection, staging cleanup, reverse rollback, idempotence,
arithmetic, denominator, identity, N/A, marker, and no-write cases. With 0/160
formal coverage, the result assets remain absent and the manuscript block
stays Pending.

The primary estimand is Graph-minus-Generic target-adverse replay Average
Precision over 24 exact episode pairs and 72 assigned windows per arm, at JSON
key `estimate.online_replay_monitoring.task.average_precision`, with a
2,000-resample bearing-clustered paired bootstrap. Future formal reports must
bind accepted complete Generic and versioned Generic-derived Graph core and
monitoring gates before producing absolute or paired estimates. The current v2
readiness artifact is the primary-status authority and records no matched keys
or effect estimate.

Formal values enter the manuscript only after all four arm gates and both exact
pairing gates accept. The compact comparison schema is fixed to
scope/task, metric, Benchmark Generic (Reactive-equivalent) estimate and
interval, Graph estimate and interval, Graph-minus-Generic estimate and paired
interval, and the corresponding valid bootstrap counts. The replay task-AP
primary row precedes explanatory replay rollout rows; diagnosis Macro-F1 and
anomaly completion-adjusted AP lead their core task blocks. The registered rollout registry is the one in
`paper/paper.yaml` and the shared protocol; it includes tool-call validity and
failure, Agent-decision error, reference validity, repeated errors, bounded data
and operator/model calls, and LLM turns. There is no separate cycle-ratio
endpoint.

The historical single-case extractor does not bind the active combined-result
identity or exact paired-cohort membership and is not an accepted publication
input. The active finalizer instead embeds a complete-cohort mechanism
projection after all four arm gates and both pairing gates accept. The
accepted-only consumer independently reconciles public canonical actions and
evaluator rollout endpoints across all 24 replay pairs, checks Graph state and
transition counts, and writes `p2_e1_replay_mechanism_v1.json` with no hidden
targets, reasoning traces, or post-hoc case selection. These diagnostics remain
explanatory; task-primary effects require the matched evaluator gates.
Undefined metrics remain N/A rather than zero, every reported bootstrap
interval includes its valid-replicate count, and provider latency remains
descriptive.

The current provider-free P02 test suite passes, covering executable
contracts, assigned-window denominators, cluster inference, document-linked
mechanics, task/mechanism separation, and protocol-bound accepted-result
publication.

The current mechanics-only manuscript assets are regenerated directly from the
retained P2-E0-v2 and dynamic-v2 Mock gates plus the dynamic-v3 formal schedule:

```bash
PYTHONDONTWRITEBYTECODE=1 python scripts/render_current_mechanics_evidence.py
```

The outputs are `paper/assets/tables/p2_current_mechanics_status.md` and
`paper/assets/figures/p2_current_mechanics_status.svg`. The renderer validates
the zero-override Benchmark Generic control and displayed denominators, then
reports dynamic-v3 formal coverage 0/240 without a task estimate.

After—and only after—the dynamic-v3 acceptance and analysis commands create a
matching accepted 240-unit pair, the provider-free manuscript consumer is:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:../p01-phm-agent-benchmark/src \
  python scripts/render_graph_dynamic_manuscript.py
```

It reads the frozen protocol plus `formal_acceptance.json` and
`formal_result.json`; it does not inspect raw run bundles, DataPort inputs, or
provider credentials. It recomputes every displayed task-primary seed contrast,
the h12-minus-h3 interaction, and the registered task-primary Holm values. For
secondary mechanism outcomes it reopens the 24 opaque seed/sequence values per
cell, recomputes paired sequence-cluster deltas, 10,000-resample intervals,
exact sign tests, defined numerators, and each metric's four-ablation Holm
family. The generated table keeps eight task-primary rows separate from 26
P2-E3--P2-E7 mechanism rows; P2-E4 supplies the single reused P2-E7
full-versus-no-branching comparison without duplicating an episode denominator.
It then updates
`paper/assets/tables/p2_dynamic_formal_results.md`,
`paper/assets/figures/p2_dynamic_formal_primary.svg`, and the unique
`P2_DYNAMIC_FORMAL` manuscript block through the protocol-bound, fully staged,
mode-preserving publication contract. The result and acceptance roots must
equal the protocol formal root, every displayed interval includes its valid
bootstrap count, source containment is lexical and resolved, existing outputs
must be ordinary single-link regular files, and the production CLI fixes the
active protocol while keeping resolved outputs inside the repository. Its
20/20 focused tests cover acceptance rejection, declared-path and alias
boundaries, protected roots, staging cleanup, idempotence, task/mechanism
arithmetic, bootstrap metadata, Holm adjustment, P2-E7 source reuse, N/A
rendering, marker uniqueness, and reverse rollback after a simulated third
replacement failure. A real 240-unit
provider-free analyzer fixture also feeds the consumer directly. The current
0/240 state leaves all accepted-result outputs absent and the manuscript block
Pending.

The final ten-lens review is not started while formal results, final tables and
figures, or the result-grounded conclusion remain pending. It starts only after
the accepted formal artifacts above are inserted, the runnable method path is
still verified, and every numeric claim traces to a formal run, table, or figure.
