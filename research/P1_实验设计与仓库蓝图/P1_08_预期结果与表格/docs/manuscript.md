# P1_08 预期结果与表格

## Current Effective Revision

P1_08 的当前有效产物是一个 table/claim planning package，而不是结果报告。本节点把 P1_07 的 protocol-ready 评测协议转成可审计的表格结构：每张表必须说明支持或限制哪个 claim、必需列是什么、负结果和不确定结果放在哪里、哪些条件缺失时必须降级。当前节点不执行 PHMGA formal rows，不锁定 `selected_global_best_backend`，不把 P1_04/P1_05 synthetic/offline signal、RM101 reject evidence、graph progression 或 review pass 写成正式 observed result。

## Table Strategy

表格服务论证而不是堆数据。本节点采用四类表：

1. `main_results`: workflow governance comparison and limited synthetic signal table. It can show the existing P1_04/P1_05 synthetic/offline signal only as a limited sanity-check row, and reserves parser-ready rows for future fixed-node governance comparison.
2. `formal_eligibility_gate`: PHMGA/Vibench formal result eligibility table. It records provider policy, metadata-H5 alignment, artifact contract, selected backend, Stage C/D completion, `result_md`, `artifact_dir`, repeat count, and formal eligibility status. A row is positive only if every gate passes.
3. `ablation_and_efficiency_results`: ablation, budget, and efficiency table. It separates Stage D ablations from runtime/token/manual budget accounting, and cannot be used when Stage D rows are missing.
4. `negative_unclear_result_ledger`: negative, rejected, unclear, low-power, and blocked evidence table. This is where RM101 reject evidence, rate limits, missing metadata-H5 alignment, registry schema errors, missing repeats, and below-threshold reviews stay visible.

## Claim Alignment

`artifacts/claim_map.yaml` keeps the downstream-compatible `c1` claim reference used by P1_09 while narrowing its meaning to a limited synthetic/offline sanity-check claim. The formal table claims are separate: `c2` covers formal eligibility, `c3` covers ablation/efficiency evidence, `c4` covers negative/unclear evidence retention, and `c5` covers uncertainty/reproducibility reporting. Any future manuscript table must cite these claim IDs and the corresponding evidence IDs before strengthening wording.

## Required Columns

Every planned table row must include `claim_id`, `evidence_id`, `support_status`, `boundary_label`, `source_artifact`, and `failure_or_limitation_ref`. Rate metrics and ablation delta rows must expose numerator, denominator, direction, repeat count, and uncertainty interval fields; ablation rows additionally carry `primary_metric_delta` to make changed-factor effects parseable. Formal PHMGA rows must include dataset, backend, provider/model policy, metadata-H5 alignment, artifact contract, selected backend lock, stage, `result_md`, `artifact_dir`, ledger row, repeat count, and eligibility status.

Two support-status vocabularies are kept explicit. Table/parser rows may use the P1_07 protocol vocabulary, where the limited synthetic/offline signal is `supported_limited`. The local `artifacts/claim_evidence_registry.yaml` also carries `protocol_support_status: supported_limited`, but its required `support_status` field uses the repository-wide claim registry vocabulary, where this same limited evidence is represented as `weak`. This preserves both parser meaning and global registry schema validity.

## Final-Threshold Score Boundary

`artifacts/table_final_threshold_contract.yaml` 将 P1_08 的复评范围锁定为 node-local table-package score review。可被复评的正向主张只有：本节点的表格规划、claim/table/evidence mapping、dual-vocabulary support-status bridge、negative/unclear evidence ledger、formal-row gate fields、repeat/uncertainty columns 和 prior review response coverage 已足够 documented、consistent、complete、parser-exercisable。该 contract 不执行 PHMGA formal rows，不填入未来 Stage C/D 结果，不锁定 selected backend，不把 RM101 reject evidence 改成 positive evidence，也不把 P1_04/P1_05 synthetic/offline sanity signal 写成 observed formal improvement。

因此，P1_08 可以请求 distinct AI_002 reviewer 判断 node-local expected-results/table-package score 是否达到 90 以上；即使通过，本节点仍必须保留全局 blocker：P1 checklist、P1_09/P3/P4 低分、P3_04 action statuses、selected backend、RM101 positive evidence、adapter preflight、Stage C/D rows 和 final validator。

## Negative And Uncertain Results

Negative and uncertain evidence is not an appendix afterthought. It has a first-class table, registry entries, failure records, and keep/discard decisions. RM101 reject evidence remains reject evidence until an eligible formal rerun passes. Missing Stage C/D rows, missing adapter alignment, missing selected backend, and missing uncertainty do not disappear from denominators; they are represented as blocked, unsupported, weak, or limitation records.

## Current Conclusion

P1_08 is table-plan ready after the local artifacts are reviewed. It provides table shells, column contracts, claim mappings, evidence registry entries, failure interpretation, negative-result notes, and keep/discard decisions. It does not prove AutoResearch effectiveness, PHMGA formal eligibility, selected backend, RM101 resolution, Stage C/D success, or final submission readiness.
