# P0_05 项目约束、资源预算与风险边界

## 节点范围

本节点把 P0_01-P0_04 已收敛的问题、候选贡献、技术路线和 OKR 转换成项目约束、资源预算、风险边界和降级计划。它不执行 PHMGA formal rows，不选择最终 backend，不替代 P1/P2/P3/P4 的实验、撰写或审稿闭环，也不把 graph、Canvas、dashboard、single run log、synthetic/offline sanity check 或 reviewer pass 写成最终研究真相。

## 必答问题

**项目最大的资源瓶颈是什么？** 最大瓶颈不是单次本地计算，而是 formal evidence eligibility chain：OpenRouter/BigModel 免费模型边界、PHMGA/Vibench sample-level metadata-H5 alignment、artifact contract、Stage C main rows、Stage D ablation rows、selected_global_best_backend、claim/evidence registry schema 和最终 review score threshold 必须同时闭合。只要其中一环未闭合，项目只能保留 proposal-stage 或 preliminary evidence wording。

**最可能失败的路径是什么？** 最可能失败路径是把已经存在的局部进展误读成最终论文证据：P1_04 的 synthetic/offline positive signal、RM101 reject-evidence rows、rate-limit interruption、低于 90 的节点评审分数、或 graph next_node 推进，被写成 formal result 或 submission-ready proof。第二常见失败路径是 claim registry 与 manuscript/figure/review response 不一致，导致 reviewer 认为证据治理只是文件堆叠。

**哪些边界必须主动写清楚以避免 reviewer 误解？** 必须写清楚：Vibench 只作为 data reading/catalog interface；PHMGA 才拥有 protocol、split、windowing、DAG、ML/Torch evaluation 和 result ledger；OpenRouter 只允许免费模型，BigModel 只允许 GLM-4.7-flash 免费边界；synthetic/offline evidence 只能是 preliminary sanity signal；RM101 reject evidence 必须保留；Claude Code teammate review 是用户授权的 review-slot delegate，不是生物学意义上的人工评审；最终投稿前仍需 `scripts/validate_research_truth.py --require-submission` 通过。

## 资源预算草案

| Budget ID | 资源面 | 当前预算/约束 | 成功条件 | 停止或降级条件 |
| --- | --- | --- | --- | --- |
| P0_05_B001 | 数据与许可 | Formal scope 限定为 `/mnt/k/D01_vibench` 下 RM_017_Ottawa19 和 RM_101_THU_GEARBOX；extension datasets 只作后续扩展候选。 | data manifest、dataset registry、checksum、metadata audit、H5 audit 均可追踪。 | 若 sample-level metadata-H5 alignment 未由 PHMGA/Vibench adapter 全量确认，则不写 formal result claim。 |
| P0_05_B002 | 实验与计算 | 当前只承认 P1_04 synthetic/offline evidence 为 lightweight sanity signal；formal rows 必须走 Stage B/C/D。 | Stage B 选择 backend；Stage C 产生 Ottawa/RM101 ML/Torch main rows；Stage D 产生 minimum ablations。 | 若 artifact contract、result_md、artifact_dir 或 passed rows 缺失，则保留 blocker/reject evidence。 |
| P0_05_B003 | LLM provider | OpenRouter 只使用免费模型；BigModel 只使用 GLM-4.7-flash 免费模型；API key 只从 `.env` 读取且不得写入审计文件。 | provider/model policy pass，secret-fragment scan clean，rate-limit or provider failure 进入 ledger。 | 若模型不合规、rate-limited 或 key 暴露风险出现，停止该 provider row，记录 failure evidence。 |
| P0_05_B004 | Review 与人工/teammate 预算 | 每个 hard-gate 节点至少 1 个 distinct AI reviewer 和 1 个用户授权 Claude Code teammate review slot；Codex 保持 final gate owner。 | verdict pass、hard_fail false、independence confirmed、response coverage complete。 | 若 reviewer score 能推进但低于 final threshold 90，节点可推进但 final submission-ready 保持 blocked。 |
| P0_05_B005 | Manuscript/registry/final-gate 维护 | 每条 central claim 必须能回指 claim_id/evidence_id/support status；figure/table/citation/review response 不得脱离 registry；final gate 当前事实必须同步。 | registry schema pass，unsupported central claim count 为 0，negative/reject evidence retained，P1 checklist、review score、P3 action status 均关闭。 | 最新 final validator 已不再报告旧 schema blockers、P1 checklist blockers、score blockers 或 P3 action-status blockers；`scripts/validate_research_truth.py --require-submission` 已通过。 |

## 风险边界与降级计划

**R1: Formal evidence eligibility fails.** 如果 provider policy、metadata-H5 alignment、artifact contract、Stage C/D formal rows 或 selected backend 任一失败，则结果层 claim 停止，保留 blocker/reject evidence，并把正文降级为 protocol-stage 或 limitation。

**R2: Preliminary evidence is overpromoted.** 如果 P1_04 synthetic/offline positive signal、P1_09 draft figure、single run metrics 或 graph progression 被写成 formal performance improvement，则阻断 handoff，恢复 preliminary/synthetic wording。

**R3: RM101 remains reject evidence.** 如果 RM101 rows 仍是 reject-evidence bundle 或 feature/contract/selection gate 不通过，则不得作为 positive selection evidence，只能用于失败模式、boundary preservation 或 future work。

**R4: Claim registry diverges from manuscript.** 如果 manuscript、figure、citation、review response 或 revision evidence 中的 central claim 缺 claim_id/evidence_id，或 support status 与 registry 不一致，则先修 registry/schema 或降级 claim，再进入后续节点。

**R5: Review gate passes but final threshold fails.** 如果节点级 score 达到 downstream pass 但低于 submission min 90，则保留 node progression，同时把 low-score blocker 写入 FSM/audit，最终投稿前再做 targeted strengthening 和 re-review。

**R6: Secret/provider boundary leaks.** 如果 API key、provider credential、paid-model path 或未授权模型使用出现在非 `.env` 工件中，则立即停止 provider evidence claim，清理泄漏风险，并重新运行 secret-fragment scan。

**R7: Final gate facts drift.** 如果资源/风险文档继续引用已经修复的旧 schema、template-marker、parent-phase、P1 checklist、score 或 P3 action blockers，而没有记录当前 final validator 已通过及保留限制边界，则审计本身失真。此时先同步 completion audit 和 resource/risk map，再讨论 submission-ready。

## 不做什么的边界说明

- 不把 P0_05 写成全局项目管理脑或替代 scheduler。
- 不在本节点执行 PHMGA formal experiments、backend selection、Stage C/D rows 或 ablation。
- 不把 Vibench trainer/evaluator/DataLoader 输出作为 PHMGA formal result source。
- 不把 OpenRouter/BigModel 可调用性写成模型质量或研究有效性证据。
- 不把 Claude Code teammate review 隐藏成未说明身份的 biological human review。
- 不删除或改写 low-score reviews、rate-limit failures、RM101 reject evidence、schema errors 或 adapter blockers。

## 当前结论

P0_05 将项目范围压缩为一个可审计的资源和风险合同：formal result claim 只能在 provider、data adapter、artifact contract、formal rows、backend lock、claim registry schema、independent review 和 final validator 同时通过后成立。当前节点可以交给独立评审检查约束是否充分；它本身不解除现有 submission-ready blockers。
