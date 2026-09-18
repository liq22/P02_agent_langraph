# Matched Graph experiments

Scope: compare the original Graph/Generic policies, cue/filter components and a count-preserving tool-identity control. Outputs: native Benchmark attempts, frozen configs, assigned-cohort metrics/effects and all-attempt costs. Acceptance: shared assets/trials, numerical capability, observations, budget and evaluator; all terminal outcomes retained. P02 contains no executable implementation.

## Completed source-level slice

`factorial-cardinality` joins the existing component factory. Its matched comparator is cue-free `factorial-filter`; Analyze/Check nonterminal tool identities are replaced while count, submit/stop permissions, schema contents/order and all other state masks are preserved. The existing run seed fixes the subset across revisits. Coincident masks remain; do not redraw until the control looks different. Equal count does not imply equal prompt tokens or equal visited histories.

Seventeen new source tests passed and the exact counting experiment produced 63 subset rows plus six summaries. They test the implementation's local invariants and the mathematical alternative, not native episodes. The attempted native test import failed with `ModuleNotFoundError: phm_agent_benchmark.phase1`; its three test functions have not run.

## Installed gate before provider calls

From the full Benchmark checkout, first reconcile local work and install its existing dependencies. Then:

```bash
PYTHONPATH=src python -m unittest discover -v -s experiments/tests -p 'test_consolidated_*.py'
PYTHONPATH=src python -m unittest discover -v -s experiments/tests -p 'test_graph_cardinality_integration.py'
bash experiments/graph_control/run.sh theory
```

These native interface tests check seed dispatch and old-cell preservation; they do not replace one real PHM episode. Do not satisfy an import failure with a fake package, substituted Runtime or stub Agent.

## Real development cohort

The added config is plan-first, with the existing model setting retained as an explicit request, not a claim of availability. Supply inspected metadata/signals, a reserved development protocol, endpoint/model and a permitted request budget through the existing options/environment. Then:

```bash
: "${DEVELOPMENT_PROTOCOL:?Set the inspected development protocol path}"
bash experiments/graph_control/run.sh relevance --override command=plan \
  protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-relevance-dev
bash experiments/graph_control/run.sh relevance --override command=probe \
  protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-relevance-probe
bash experiments/graph_control/run.sh relevance --override command=run \
  protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-relevance-dev
bash experiments/graph_control/run.sh statistics local_outputs/graph-relevance-dev
```

The plan/probe/run/statistics path requires full installation and actual data/settings; it was not completed in this source-only editing environment. A failed probe stops execution. No retry, alternate provider, automatic repair or replacement test set is permitted.

Primary effect: `state mask minus cardinality control` from the registered pooled cohort statistic. Recompute nonlinear F1/AP inside paired asset-block resamples; do not substitute mean per-seed scores. Also inspect whether the mask actually differs on reached Analyze/Check states, their allowed tools, missing prerequisites, repetition, completion, numerical grounding and all incurred cost. A nonpositive effect rejects benefit of the chosen stage identities under this protocol; preserve it.

## Existing comparisons and remaining extensions

Use `run.sh phm` for original Graph/Generic and `run.sh ablation` for the four cue/filter cells. Persistence uses the direct Graph-minus-no-memory contrast only after checking activation. An inactive base switch remains a null manipulation, not general evidence against memory.

The five external families in DATA_DOWNLOAD_SOP still need shared DataPort/task/evaluator bindings. `run.sh external` and `run.sh sota` explicitly stop with the missing implementations; those modes are not completed benchmark launchers. StateFlow/Reflexion need faithful mechanisms and complete call accounting. The numerical reference, best-single, static-fusion and dynamic-routing axis must expose identical admitted expert pools to all Agent arms. Graph-loss ablation is inapplicable to the frozen training-free policy. Nested-prefix horizon and dynamic public-condition profiles remain separate unfinished work.

Failure handling: retain partial attempts and actual errors; fix the smallest direct protocol or implementation cause. Missing CPU/data adapters are not GPU work. When training/local inference genuinely requires GPUs, follow Goal03 on eight RTX4090 cards; no two-card fallback or invented trainer command.
