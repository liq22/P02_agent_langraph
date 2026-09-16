# Matched Agent and numerical experiments

Scope: original Graph/Generic policies and independent cue/filter contrasts, first on reserved development assets and then on a frozen confirmatory cohort. Outputs: Benchmark six-file attempts, resolved configs, task metrics, paired effects and all-attempt costs. Acceptance: the same assigned assets/trials, numerical pool, observations and budgets across arms; all terminal outcomes retained.

## Executable contrasts

The component cells are reactive $(0,0)$, state $(1,0)$, filter $(0,1)$ and both $(1,1)$. Report cue effects at filter=0 and filter=1, filtering effects at cue=0 and cue=1, and their difference-of-differences. The direct memory contrast is `graph minus graph-no-memory`, not a subtraction involving an absent Generic arm. Benchmark `research/conditions.py` now defines these contrasts; its policy dispatch and the shared evaluator are unchanged.

Before spending on a memory cohort, show that the switch changes a reachable state or action distribution. If it is inactive in the base task, retain the null manipulation and do not present it as evidence that memory is useless. Do not introduce events or remove history merely to make the contrast nonzero.

After installed migration/data validation, from Benchmark:

```bash
: "${DEVELOPMENT_PROTOCOL:?Set the inspected development protocol path}"
bash experiments/graph_control/run.sh phm \
  --override command=plan protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-dev
bash experiments/graph_control/run.sh ablation \
  --override command=probe protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-probe
bash experiments/graph_control/run.sh ablation \
  --override command=run protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-components
# Run only after the persistence manipulation is shown to be active:
python main.py --config configs/paper02_graph/memory.yaml \
  --override command=run protocol="$DEVELOPMENT_PROTOCOL" output=local_outputs/graph-memory
```

The commands above are real existing entrypoints but were not run in this continuation's partial source environment. Metadata/signals and provider configuration must be supplied through the existing options/environment. Use a named model/endpoint, explicit request/token caps and approved spending. A failed probe stops inference; do not change provider or silently retry.

## New completed CPU slice

`run.sh counterexamples` evaluates covered-but-harmful expansion and unsupported logging. It is a separate exact-model experiment, not a PHM run or an implementation of a learned coverage estimator. Its nine CSV rows and manuscript Sections 4.3, 7.2–7.3 complete the analytical slice. Local validation and commands are recorded in Benchmark `results/graph_control/boundaries_20260916/README.md`.

## Remaining experiments

The five external families in DATA_DOWNLOAD_SOP still need task/DataPort/evaluator admission. `run.sh external` and `run.sh sota` explicitly exit 2; these are not completed experiment launchers. StateFlow and Reflexion require faithful shared-runtime reproductions, not renamed local methods. Do not repeatedly run unchanged blocked commands.

Best-single representation, static fusion and learned numerical routing are a secondary shared-expert-pool axis. A frozen graph has no trainable loss to ablate. Pure horizon requires nested prefixes; public operating-condition events are not inferred fault onset. Statistical and cost analyses use all assigned outcomes, not selected successful attempts. Negative outcomes remain in the declared comparison.

Failure handling: preserve failed attempts and partial outputs; fix the first protocol/implementation failure without altering test assets or targets. If the necessary adapter or trainer does not exist, implement and test that explicit binding in Benchmark before launching it. Eight-card GPU execution follows Goal03 only after those CPU/data gates pass.
