# Graph dynamic and ablation protocol v3

The machine-readable authority is
`paper/experiments/graph_dynamic_ablation_protocol_v3.yaml`. Version 3 amends
the unexecuted v2 formal profile before any affected provider inference. The
dataset, split, public event construction, horizons, cells, seeds, budgets,
Generic-derived agents, provider model, temperature, and tool surface are
unchanged. V1 and v2 output roots remain historical and cannot be resumed or
pooled into v3.

Task performance is primary. The primary endpoint is target-adverse Average
Precision recomputed over every protocol-assigned replay window in all eight
matched held-out bearing sequences within a seed and condition. Failed,
partial, timed-out, budget-exhausted, and invalid-submission windows stay in
the denominator under
`phase1_replay_target_adverse_missing_score_v1`. Grounded completion and other
rollout measures are secondary.

Formal acceptance and analysis independently reconstruct the eight
evaluator-private 12-window masters through the Benchmark-registered Paderborn
DataPort. Horizon 3 and 6 assignments are exact prefixes of the same horizon-12
master across every seed and arm. Prediction truth is the immutable successful
`submit` prefix in canonical `rollout.jsonl`; `submission.json` is only a
consistency check. Runner-derived `evaluation.jsonl` remains a resume
diagnostic and is never ingested as target or prediction authority. The CLI
requires `--dataset-protocol`, `--private-metadata-env`, and
`--private-signal-env`; environment values and private assignments are not
serialized into acceptance or result artifacts.

Average Precision is not computed and averaged per bearing: a single bearing
sequence may contain only one target class. Paired intervals resample the eight
matched bearing clusters and recompute the nonlinear endpoint; the exact test
enumerates all 256 matched cluster arm swaps and recomputes it. The formal v3
cohort remains 0/240, so no Graph performance or ablation effect is claimed.

`scripts/render_graph_dynamic_manuscript.py` is the accepted-result consumer.
It reads only this protocol, `formal_acceptance.json`, `formal_result.json`, and
the active manuscript. Before writing, it revalidates the exact 240-unit
inclusion report, ten 24-episode cells, assigned-window accounting, seed-level
task-primary arithmetic, horizon interaction, exact-test metadata, and Holm
adjustment. The accepted result also exposes each secondary metric's 24 opaque
seed/sequence values and eight paired sequence-cluster differences. The
consumer uses those projections to recompute every displayed mechanism delta,
bootstrap interval, exact sign test, defined numerator, and per-metric
four-ablation Holm family.

The output keeps eight task-primary rows separate from 26 secondary mechanism
rows. P2-E3 reports revision and recovery behavior; P2-E4 reports all seven
condition-event outcomes and is co-labeled as the single reused P2-E7
full-versus-no-branching comparison; P2-E5 reports revision, repeated action,
and loop behavior; P2-E6 reports revision, post-event action/prediction steps,
repetition, and budget exhaustion. Seven additional P2-E7 rows compare full
Graph with Reactive on the same horizon-12 condition events. This produces no
fault-onset, event-F1, detection-delay, or physical-time claim and never
duplicates an episode denominator. The consumer updates the standalone table,
task-primary SVG, and one marked manuscript block as a group with exception
rollback. Rejected,
partial, identity-drifted, or arithmetically inconsistent inputs leave all
three outputs unchanged. With formal coverage at 0/240, the manuscript block
remains Pending.
