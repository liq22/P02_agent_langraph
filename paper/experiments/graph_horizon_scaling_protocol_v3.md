# Graph horizon-scaling scheduler contract v3

The machine-readable authority is
`paper/experiments/graph_horizon_scaling_protocol_v3.yaml`. It is the P2-E2
projection of `graph_dynamic_ablation_protocol_v3.yaml`. The 144-unit design
remains three seeds by eight public sequences by three nested horizons by two
matched Generic-derived arms; no provider execution has started.

The primary endpoint is target-adverse Average Precision over every assigned
replay window. Each seed-level value is recomputed jointly across all eight
held-out bearing sequences at one horizon. Failed and partial episodes keep
their assigned windows in the denominator under
`phase1_replay_target_adverse_missing_score_v1`; grounded completion is a
secondary rollout measure. Per-bearing AP averaging is forbidden because an
individual bearing sequence can contain only one target class.

The scheduler remains provider-free and dry-run-only. It emits the 144 v3
command projections only after static runner checks pass, but never invokes
them. V1 and v2 roots are historical, cannot be resumed or pooled, and contain
no formal results supporting a horizon or Graph-effect claim.
