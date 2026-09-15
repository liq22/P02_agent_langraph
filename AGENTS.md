# Agent Entry — GraphDecisionAgent

Read DEV.md, CORE.md, paper/GOAL.md, paper/LOCAL_AGENT_PROMPT.md and obsidian/log/LOCAL_AGENT_STATE.md. This repository owns its paper and `src/phm_graph_agent`. The current source of truth is `dev`; short feature/review/figure/experiment/agent branches return through PRs to `dev`.

Review semantic changes against dev. Keep mature text, verified citations and figures serving an explicit argument; patch useful subsets; exclude duplicated plans, stale drafts and workflow infrastructure. Preserve necessary scientific limitations and every registered result under its original conditions. The manuscript is paper/draft/main.md.

Reuse Benchmark TaskSpec, DataPort, run_rotation, Runner, evaluator and canonical rollout writer. Benchmark must run without downstream policies. Keep inference separate from evaluation; never expose private targets. RandomValid contains a planned-call candidate and is not a uniform random baseline.

Use experiments/run.sh for new studies. Preserve frozen formal scripts and source dependencies. A changed provider, model, prompt, visible tools, dataset or metric defines a new condition. Retain all attempts, failures and abstentions. Reuse existing environments and completed checks; run affected tests after relevant changes. Do not add hash/receipt/ledger mechanisms, duplicated factories or automatic backend switching.

Online inference requires current-task authorization and explicit request/token limits. Credentials remain environment variables; a request cap is not a monetary cap. No external inference is needed to inspect a plan.

End a bounded task by updating the rolling state with actual commands, reused cells, new outputs and one next step. A merge is not an empirical or publication claim.
