# Graph-guided PHM Agent Paper — Benchmark Adapter

`CORE.md` is the repository authority. This repository owns Paper 2: testing whether a compact PHM decision graph improves long-horizon tool use, state transitions, recovery, and grounded completion under the frozen `phm-agent-benchmark` protocol.

```text
B3 Generic / reactive LLM Agent
             vs
B5 GraphDecisionAgent
```

The graph is a policy scaffold over the benchmark action interface. It does not replace benchmark tasks, tools, budgets, RunBundle, evaluator, or numerical PHM operators.

## Active implementation

```text
src/graph_phm_paper/adapter.py
src/graph_phm_paper/state_metrics.py
scripts/run_graph_experiment.py
tests/test_graph_adapter.py
```

Active method graph:

```text
orient → acquire → analyze → model → submit
                     ↘ recover ↗
```

The generic Autoresearch graph, Canvas, Web UI, Tauri wrapper, and project scheduler remain secondary infrastructure, not Paper-2 method components.

Focused test:

```bash
PYTHONDONTWRITEBYTECODE=1 \
PYTHONPATH=src:../phm-agent-benchmark/src \
python -m unittest -v tests/test_graph_adapter.py
```

Formal B5 execution requires the same Paderborn data, provider model, temperature, seeds, budgets, and evaluator used for B3. Mock output validates mechanics only.
