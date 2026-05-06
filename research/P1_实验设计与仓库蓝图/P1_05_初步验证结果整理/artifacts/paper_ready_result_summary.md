# Paper-ready result summary

P1_04 produced a bounded offline synthetic sanity check on Ottawa synthetic data. The baseline row (`ottawa_synth_ml_simple`, simple_fullchain, offline_stub) reached test accuracy `0.8333333333333334` and test macro-F1 `0.8285714285714285`. The controlled attempt (`ottawa_ml_codex_proving`, supervisor_proving, `data=ottawa_synth`, `llm.mode=offline_stub`) reached test accuracy `1.0` and test macro-F1 `1.0`.

The safe conclusion is limited: supervisor_proving shows a preliminary synthetic/offline keep signal over simple_fullchain in this two-row P1_04 check, with test accuracy delta `+0.16666666666666663`.

This summary may be used only as a preliminary/synthetic sanity-check statement. It must not be used as a formal Stage C/D result, selected-backend evidence, RM101-resolution evidence, or submission-ready performance claim.

Final-threshold note: `artifacts/result_synthesis_final_threshold_contract.yaml` permits this paragraph to support P1_05 score readiness only as a preliminary result-synthesis handoff. It does not change any unsupported or unclear state.

Evidence:

- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv`
- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/runs/baseline_simple/metrics.json`
- `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/runs/attempt_supervisor_proving/metrics.json`
