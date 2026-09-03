# Graph horizon-scaling scheduler contract v2

**Status:** Generic-base preregistration; provider-free scheduler and dedicated
formal runner ready; formal execution not started

**Machine-readable authority:** `graph_horizon_scaling_protocol_v2.yaml`

This protocol replaces the retired PHMskills-base v1 projection. The control
is `reactive-sequential-agent`, whose matched control identity is
`benchmark_generic_llm_tool_agent_v1`; the treatment is
`graph-decision-agent`. Both belong to `p2_graph_vs_generic_llm_v1` and use the
Generic-base dynamic authority `graph_dynamic_ablation_protocol_v2.yaml` under
runtime `phase1_graph_dynamic_generic_ablation_v2`.

The 144-unit design remains three seeds by eight public sequences by three
nested horizons by two matched arms. Horizons 3 and 6 are prefixes of the same
12-window sequence. Horizon is released-window count in offline metadata order,
not physical time, fault onset, detection delay, or time to failure.

Run the provider-free projection with:

```bash
python scripts/schedule_graph_horizon_scaling.py --dry-run
```

The scheduler never reads environment values or invokes a provider. It first
checks the actual runner flags, Generic-base identity literals, and source
implementation declarations. When any prerequisite is missing, every unit is
still registered but `argv` and `command` are `null`, readiness is `false`, and
strict mode exits nonzero. When readiness eventually becomes true, every
OpenAI command must explicitly include both
`--input-usd-per-million 0.0` and `--output-usd-per-million 0.0`.

The current dynamic-v2 authority declares `formal_runner_implemented: true`,
and this projection's static runtime readiness is true. Its provider-free dry
schedule emits 144/144 commands. None has been invoked, and zero formal results
exist. The scheduler itself remains dry-run-only and does not launch those
commands. Readiness and emitted commands are implementation evidence, not
performance evidence, and cannot support a horizon or Graph-effect claim. The
superseded v1 protocol is rejected even when passed explicitly and no v1
artifact may be resumed or pooled with v2.
