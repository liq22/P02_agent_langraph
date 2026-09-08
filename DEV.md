# Paper 2 research on dev — 2026-09-08

The latest GraphDecisionAgent method branch was merged through PR #2. Continue new research on `dev`; keep `main` and frozen formal worktrees unchanged. A development merge is not a task-performance or reliability result.

The shared specification is [Benchmark dev / paper/graph/RESEARCH.md](https://github.com/liq22/phm-agent-benchmark/blob/dev/paper/graph/RESEARCH.md), with filtering and state-sufficiency proofs in its `theory/` directory. See Benchmark `paper/DEV_RESEARCH.md`, `paper/EXPERIMENT_LIMITS.md` and `paper/LOCAL_AGENT_PROMPT.md` for execution.

This repository owns the graph method. Import its current `src/phm_graph_agent` policy; do not copy the Benchmark DataPort, Runner, numerical operators or evaluator. The research specification is not a second full manuscript.

```bash
export PHM_GRAPH_SRC=/absolute/path/P02_agent_langraph/src
cd /absolute/path/phm-agent-benchmark
bash paper/run_study.sh plan --experiment graph-components --provider deepseek
bash paper/run_study.sh run --experiment graph-components --provider deepseek \
  --output local_outputs/graph-components-deepseek
```

The original graph profile remains unchanged. The new factorial study removes historical state labels from provider-visible messages in all four arms, then independently varies the current-state suffix and tool visibility. Its controls are not interchangeable with old Generic/Graph results. The no-memory comparison uses the existing profile and must report identical behavior honestly if that ablation is inactive in a given task.

Base and dynamic profiles remain separate. Public condition events are not signal-inferred fault onsets. The supplied horizon entry changes sampled windows and proportional budgets together; a pure nested-prefix horizon intervention needs a new explicit assignment binding. Reuse completed compatible cells. Reserve development assets before tuning. Credentials remain local environment variables.
