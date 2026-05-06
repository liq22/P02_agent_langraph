# P1_09 Result Figures and Claim-Figure Alignment

## Node Scope

This node prepares claim-safe result figure drafts. It does not promote P1_04/P1_05 lightweight validation into a formal paper result.

The current upstream claim map defines `c1` as the main-task fault-identification accuracy objective under `split_by_machine_v1`, with `main_results` as the source table and `fig_main` initially unset. P1_09 maps that claim to a limited draft figure only because the available observed evidence is synthetic/offline and single-run.

## Figure Draft

`fig_main_synthetic_signal` is the only kept figure draft in this node. It has two panels:

- Panel A plots `test_accuracy` for `simple_fullchain` baseline versus `supervisor_proving` controlled attempt.
- Panel B plots `test_macro_f1` for the same two rows.

Both panels use values copied from `research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv` and registered in P1_05. The figure may support the limited statement that `supervisor_proving` showed a positive synthetic/offline keep signal in the bounded P1_04 setup.

The SVG rendering is deterministic. Re-run it from the repository root with:

```bash
python3 research/P1_实验设计与仓库蓝图/P1_09_结果图与草稿/tools/render_fig_main_synthetic_signal.py
```

The renderer reads only `figures/fig_main_synthetic_signal_data.tsv` and rewrites `figures/fig_main_synthetic_signal.svg`.

## Legend Boundary

The legend should include the PHMGA Ottawa synthetic setup, `offline_stub` mode, the two workflow modes, the metrics, and the fact that no variance evidence is available.

The legend must not claim real-data generalization, RM101 resolution, selected-backend readiness, formal Stage C/D performance, or submission-ready evidence.

## Claim Alignment

The broad upstream `c1` objective is only partially covered. The local support status is `supported_limited_proxy`, not `supported_formal`. The local claim-evidence registry records this gap explicitly and keeps unsupported or unclear interpretations visible.

## Final-Threshold Score Boundary

`artifacts/figure_final_threshold_contract.yaml` 将 P1_09 的复评范围锁定为 node-local draft-figure score review。可被复评的正向主张只有：`fig_main_synthetic_signal` 的 plotted TSV、deterministic renderer、SVG、manifest、claim-figure map、caption/legend boundary、failure register、negative note 和 keep/discard ledger 已足够 documented、traceable、deterministic、claim-safe，并且上游 P1_08 table package 已经通过 distinct AI_002 final-threshold review。该 contract 不把 figure 写成 formal main-result figure，不声明 real-data generalization、RM101 resolution、selected backend readiness、Stage C/D success、variance stability 或 submission-ready performance。

因此，P1_09 可以请求 distinct AI_002 reviewer 判断 node-local draft-figure package score 是否达到 90 以上；即使通过，本节点仍必须保留全局 blocker：P1 checklist、P3/P4 低分、P3_04 action statuses、selected backend、RM101 positive evidence、adapter preflight、Stage C/D rows 和 final validator。

## Deferred Figures

Formal main-result, ablation, efficiency, and uncertainty/error-bar figures are deferred or discarded for now because the current evidence chain lacks real-data formal rows, ablation rows, efficiency metrics, and repeated-run variance.

## Handoff State

The P1_09 author package now contains:

- `artifacts/figure_plan.yaml`
- `artifacts/claim_figure_map.yaml`
- `artifacts/figure_manifest.yaml`
- `artifacts/claim_evidence_registry.yaml`
- `artifacts/failure_register.yaml`
- `artifacts/negative_result_note.md`
- `artifacts/keep_discard_ledger.yaml`
- `figures/fig_main_synthetic_signal.svg`
- `figures/fig_main_synthetic_signal_data.tsv`
- `tools/render_fig_main_synthetic_signal.py`
- `artifacts/figure_render_protocol.yaml`

The package is ready for independent review, with the caveat that P1_08 itself was still at `stage: seed` when this draft package was authored.
