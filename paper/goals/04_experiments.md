# Matched Agent and numerical experiments

Scope: original policy and cue/filter contrasts on an explicitly reserved development cohort, then a frozen confirmatory cohort. Outputs: Benchmark six-file runs, config snapshot, metrics/effects and full-attempt costs. Acceptance: same assigned assets/trials across arms, declared endpoint and all terminal outcomes retained. No new score is selected after seeing effects.

After local integration and data checks:

```bash
# All commands are launched from Benchmark, not P02.
bash experiments/graph_control/run.sh phm \
  --override command=plan protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-dev
bash experiments/graph_control/run.sh ablation \
  --override command=probe protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-probe
bash experiments/graph_control/run.sh ablation \
  --override command=run protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-components
```

Keys remain in the selected provider's environment; no key was used by this revision. Current profiles include API backends, but this slice does not assert live model availability. Probe a new endpoint/settings combination once; no silent fallback. Paid models need an explicit request/token cap and the user's provider spending setting. A fixed model condition cannot absorb another route's attempts.

Five external domains and external SOTA reproduction are **blocked before execution** until their task/data adapters are admitted. `run.sh external` and `run.sh sota` exit2 with the missing binding, instead of emitting fake metrics. Their scientific contracts are in EXPERIMENT_MATRIX. Do not keep rerunning these unchanged blocked modes.

Representation/static-fusion/dynamic-numerical-routing experiments are a secondary shared-expert-pool axis. Existing graph has no loss to ablate. No-memory must be active; pure horizon requires nested prefixes; dynamic events are not inferred fault onset. These conditions cannot be made true by renaming configs. A negative result closes the relevant hypothesis and must remain in the report.
