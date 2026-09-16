# Completed slice and exact stop point — 2026-09-16

## Read-only audit

P02 PR #4: base dev, open Draft, paper-only branch. Benchmark PR #20: base dev, open Draft, centralized implementation branch. Neither was merged in this session. The source manuscript still contained obsolete local scripts/finalizer paths and unobserved treatment-result placeholders. Its actual evidence was mechanics and Scripted references, not a Graph effect.

Source audit read main manuscript, AGENTS, graph state/controls, main/config dispatch, factory submodule and upstream main. PHMFactory pinned580507 is ahead of main458fb0 by five commits; a switch to main would be a rollback, not the requested fast-forward. Parent pointer is unchanged.

## Completed work

- Rewrote the existing full manuscript, not a parallel draft; removed obsolete execution/finalizer instruction prose while retaining factual historical evidence and Git source history.
- Added value-coverage assumptions/proofs, explicit conditional exposure, empirical/population distinctions and a violated-coverage counterexample.
- Added source-located StateFlow/PHMForge/masking and JMLR confidence-based action-elimination review, five-domain official download/admission SOP, experiment mapping and local GPU/API goals.
- Added only independent theory/toy/plot code to Benchmark. Main PHM/ablation/statistics routes delegate to the existing single runtime.

## Commands actually run in the editing runtime

```bash
python -m unittest discover -v -s benchmark/experiments/graph_control/tests
python benchmark/experiments/graph_control/toy.py --output benchmark/results/graph_control/toy_20260916
bash benchmark/experiments/graph_control/run.sh plot --csv benchmark/results/graph_control/toy_20260916/toy.csv --output benchmark/results/graph_control/toy_20260916/figures
```

Results: 9/9 tests; 24 computed rows; max identity residual1.6653345369377348e-16. At four steps: best-fixed0.6000, static-uniform0.55833, aligned-mask0.7625, harmful-mask0.5000, expanded-uniform0.7125, known-value oracle/covered-greedy0.9250. The bad-interval example has certified bound0 and actual loss0.85. PNG previews inspected, editable PDF text checked. These are exact-model outputs, not Agent/API/PHM observations.

## Not completed and not claimed

Full installed Benchmark integration; real Paderborn record/labels/split/checkpoint recomputation; five external task adapters; StateFlow/Reflexion/MOMENT etc. reproductions; real LLM calls; calibrated PHM Q intervals; pure nested-prefix horizon; eight-GPU execution; factory advancement. Source verification and a mode name are not evidence that these ran.

## Merge decision and next action

Do not merge the whole pending migrations from leaf tests alone. Run Goal01/03 in the authenticated local Benchmark checkout, first resolving the actual factory/data condition. Then one reserved-development Generic/Graph pair, before a larger API cohort. Only after relevant real-entry and document checks pass: merge implementation normally into dev, then paper-only cleanup into dev. No force push/master update/branch deletion. Continue from existing outputs rather than replaying old migrations.
