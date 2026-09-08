# Graph dynamic and ablation protocol v2

This protocol is the Generic-base successor to the historical v1 mechanics
profile. The matched control is `ReactiveSequentialAgent`, a zero-behavior
subclass of Benchmark `GenericLLMToolAgent`; the treatment is
`GraphDecisionAgent`, also derived directly from that Generic policy. No P1
runtime, skill catalog, or PHMskills provenance enters either arm.

The machine-readable authority is
`paper/experiments/graph_dynamic_ablation_protocol_v2.yaml`. It inherits the
unchanged public condition-event construction, horizons, budgets, state
profiles, metrics, and registered 240-unit design from v1 while replacing all
agent, runtime, output-root, and acceptance identities. This inheritance is a
source-level convenience only: v1 artifacts remain historical and cannot be
resumed or pooled into v2.

Current evidence is provider-free mechanics only: all ten registered v2 Mock
cells were materialized as exact-six bundles and the isolated gate accepted
with zero provider calls. The provider-bound 240-unit cohort has not started.
No performance, ablation, reliability, or transfer result is claimed.
