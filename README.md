# Graph-Guided PHM Agent

This repository studies whether an explicit decision-state graph changes
long-horizon PHM-agent rollouts when the Benchmark world and the underlying
Generic LLM policy are held fixed.

## Active comparison

```text
Control:   Benchmark Generic (Reactive-equivalent)
           ReactiveSequentialAgent = GenericLLMToolAgent with zero behavior overrides

Treatment: GraphDecisionAgent over the same Generic base
           + registered state guidance and state-specific tool visibility
```

Neither arm imports the Paper-1 PHMskills runtime. Both arms use the same
Paderborn tasks, split, model/provider profile, base prompt, data tools,
vibration operators, numerical experts, budget, episode order, and evaluator
from `../p01-phm-agent-benchmark`. The graph has eight states: Inspect,
Hypothesize, Analyze, Check, Monitor, Revise, Recover, and Submit. The active v6
primary registers no `public_condition_event`, so Monitor and Revise are
unreachable there. Their observation-conditioned execution belongs only to the
separate task-primary dynamic-v3 profile.

## Current evidence boundary

- P2-E0-v2 accepts provider-free real-Paderborn adapter/world mechanics: 16
  matched exact-six units per arm, 352 canonical actions and 16 submitted
  terminal paths per arm, and zero provider calls.
- The frozen P2-E1 Generic-base snapshot records that no four-root audit has
  been performed and emits no effect estimate. The finalizer binds every
  accepted result to the protocol identity, resolved Benchmark control stamp,
  frozen model profile, registered design, analysis contract, and exact
  Benchmark/Data Factory/P2 Git topology, then publishes readiness and result as
  one group with exception rollback. The accepted-only manuscript
  consumer independently rechecks those bindings, all displayed deltas and
  replay assigned-window accounting; it deterministically emits the primary
  table, core figure, Graph-state artifacts, full-cohort replay-mechanism JSON,
  and manuscript update as one group. The mechanism projection uses all 24
  exact replay pairs, public canonical actions, and evaluator rollout metrics;
  it admits no hidden-target selection, reasoning trace, or post-hoc case.
  Focused finalizer and consumer checks pass, including a full
  192-core/24-replay-per-arm fixture. No accepted P2-E1 result exists.
- Dynamic-v3 retains the unchanged 10/10 provider-free exact-six v2 Mock
  mechanics cells. Its task-primary endpoint is target-adverse assigned-window
  Average Precision; grounded completion is secondary. The dedicated runner
  and dry scheduler validate 240/240 commands, none invoked, with formal
  coverage 0/240. Its accepted-only analyzer rebuilds the eight private
  12-window masters through the registered DataPort and reads predictions from
  canonical rollout submit prefixes; derived `evaluation.jsonl` rows are not
  target or prediction authority. Its accepted-result consumer recomputes and
  separately labels eight task-primary and 26 P2-E3--P2-E7 mechanism rows; a
  real 240-unit provider-free analyzer fixture reaches the consumer. The
  consumer binds every input/output path to the protocol, rejects filesystem
  aliases, nonordinary or multiply linked existing outputs, source/parent
  symlink escapes, and raw/result-root publication. It binds the accepted root
  to the protocol formal root, reports valid bootstrap counts, fixes the
  production CLI protocol, and passes focused checks for full staging,
  cleanup, mode preservation, rollback, and idempotence.
- Horizon-v3 projects the same endpoint and matched bearing-cluster inference
  over 144 registered units. Its provider-free dry schedule emits 144/144
  commands; none has been invoked and no formal result exists.
- Reliability-v2 is runner-ready and its provider-free dry schedule emits
  160/160 inert commands. It invokes none of them, performs zero provider calls
  and zero writes, has zero formal results, and passes its focused checks. Its
  accepted-only analyzer now uses private DataPort targets plus canonical
  rollout submit prefixes to recompute target-adverse AP over all 24 assigned
  windows per repeat; grounded completion remains explanatory. Its accepted
  consumer applies the same protocol-bound publication contract and passes
  focused checks, including formal-root provenance, valid bootstrap
  counts, and path-identity containment.
- Cross-dataset-v3 registers the accepted Ottawa ordered-state target and its
  CSV DataPort. The provider-free preflight emits 18/18 commands for 72 episode
  bundles, 36 matched pairs, and 216 assigned windows; the accepted-only
  analyzer is implemented. Its accepted-result consumer rechecks the exact
  cohort, target-adverse accounting, displayed task deltas, and bootstrap
  metadata before a fully staged, mode-preserving grouped replacement with
  reverse rollback. Its result schema binds the accepted stamped run root to
  the scheduled base, and the consumer rejects nonordinary output identities
  plus source/parent symlink escapes. The E8 chain passes its provider-free
  checks. No command
  has run, no formal result or result row exists, and external provider
  execution remains unauthorized.
- The provider-free repository suite passes. Tests and mechanics gates
  are implementation evidence, not task-performance or treatment-effect
  evidence.

The generated current snapshot is available as
`paper/assets/tables/p2_current_mechanics_status.md` and
`paper/assets/figures/p2_current_mechanics_status.svg`. Neither artifact
contains a task score or Graph performance claim.

## Active execution paths

- graph implementation and single-arm runner: `src/phm_graph_agent/` and
  `scripts/run_graph_experiment.py`;
- P2-E8 Ottawa dry scheduler and accepted-only analyzer:
  `scripts/schedule_graph_cross_dataset_replay.py` and
  `scripts/analyze_graph_cross_dataset_replay.py`;
- authoritative task/data contract:
  `../p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml`;
- Benchmark Generic P0-only launcher:
  `../p01-phm-agent-benchmark/paper/experiments/run_formal_paper0_v6.sh`;
- Benchmark-owned provider-free P1/P2 joint-primary schedule:
  `../p01-phm-agent-benchmark/paper/experiments/schedule_downstream_formal_v2.py`;
- Benchmark-owned joint-prefix inspector and one-job executor:
  `../p01-phm-agent-benchmark/paper/experiments/execute_joint_primary_schedule_v1.py`;
- manuscript and evidence authority: `paper/draft/main.md`, `paper/paper.yaml`,
  and `paper/experiments/evidence_matrix.md`.

The downstream scheduler emits a 45-job joint counterbalance over 15 units and
three arms: Benchmark Generic, PHMskills, and Graph. Twelve core units contribute
36 jobs and three monitoring units contribute nine jobs. Generic executes once
per unit and is the shared control for both the P1 and P2 comparisons. The P0
B3 profile and roots are ineligible as joint controls and cannot be pooled with
the fresh joint Generic cohort. Benchmark now locally implements the serialized
exact-prefix inspector/executor, and its joint scheduler, acceptance producer,
and executor contract suite passes 43/43. `--check` is provider-free;
`--execute-next` can start at most one registered job and does not itself grant
permission. The current formal source revisions are dirty or unpublished, P1/P2
joint provider/public-context egress has not been separately authorized, no
fresh admission report is bound, and none of the 45 jobs has run. The schedule
therefore remains `execution_ready=false`, reports `provider_calls=0`, and
supplies neither inference nor result evidence.

Historical six-state, PHMskills-derived, dynamic-v1, scheduler, graph-UI, PHMGA,
and autoresearch artifacts are non-authoritative. They cannot be resumed,
pooled, or reported as the current Generic-base treatment.
