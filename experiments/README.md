# GraphDecisionAgent experiments

This repository owns its study conditions and contrasts. Shared execution and CSV analysis are imported from Benchmark `phm_agent_benchmark.research`; the numerical/runtime contracts are reused unchanged.

## Local or cloud checkout

Use the existing Python environment. For a cloud method checkout, separately check out Benchmark `dev` at an explicit compatible commit (the September-15 research interface or later compatible source); initialize its declared Data Factory dependency using its own instructions. No other method checkout is required. No data or model credential is needed for `plan` or offline fixtures. These commands never discover or clone a dependency automatically.

```bash
export PHM_BENCHMARK_ROOT=/absolute/path/phm-agent-benchmark
export PHM_PYTHON=/absolute/path/existing/venv/bin/python
bash experiments/run.sh plan --experiment graph-components \
  --provider glm --model glm-4.7-flash --stage smoke --protocol "$DEV_PROTOCOL"
bash experiments/run.sh test
```

`DEV_PROTOCOL` must name an explicitly reserved development protocol; smoke only limits assets. `--provider`, `--model` and full `--endpoint` are explicit request settings, not availability claims. Authorized `run` invocations must specify `--request-cap` and `--max-tokens`; the former is not a monetary limit. New source or science conditions use a new output root. `--only` selects cells within the same plan, and `--resume` continues compatible interrupted cells. `all` contains only this paper's conditions.

## Existing controls and outputs

`--control-root /absolute/path/completed-study` explicitly references compatible completed Generic cells. It checks provider settings, protocol, budget/seed/rotation cells and clean Benchmark source versions before execution, and requires retained canonical attempts. An incompatible or incomplete control stops reuse; it is never silently rerun. Original attempts remain read-only in their source directory, and analysis reads those references together with this study's cells. Archive or move both output roots together.

```bash
bash experiments/run.sh availability "$STUDY_ROOT"
bash experiments/run.sh finish "$STUDY_ROOT"
```

`finish` writes availability from every attempt, then task metrics, matched effects, ranking diagnostics and SVG/PDF/600-dpi PNG figures with CSV source data. Missing cost remains unknown; ranking identification bounds have no midpoint estimate and are distinct from confidence intervals. Plotting reads CSV only. Private `analysis.json` remains in ignored local outputs, never in agent input or paper assets.

Frozen historical protocols use their original scripts and worktrees. Old mixed studies retain their original version; they are not silently migrated or relabeled.
