# P0_04 技术路线、研究计划与 OKR

## 节点范围

本节点把 P0_01-P0_03 已收敛的 gap、科学/工程问题和候选贡献，组织成可执行但仍属 proposal-stage 的技术路线、阶段计划、OKR 和风险分支。它不执行 P1/P2/P3/P4，也不把 preliminary synthetic/offline evidence、graph projection、single run log 或 generated prose 写成最终研究真相。

## 技术路线草图

主路线是一个五阶段 evidence-governed research loop。

**Stage 0: Problem and contribution lock.** 目标是锁定可证伪问题、候选贡献和 novelty boundary。输入来自 P0_01 的 background gap、P0_02 的 science/engineering split、P0_03 的 contribution_claims。成功条件是每个候选贡献都有 claim_id、nearest-prior boundary、required evidence 和 downgrade rule。失败条件是贡献仍停留在 first/better/automatic 叙事，或实现细节被写成科学贡献。

**Stage 1: Protocol and data eligibility.** 目标是把 H1-H3 变成固定节点集、固定预算、baseline、metric、provider/model policy、dataset adapter preflight 和 artifact contract。成功条件是 manual checklist、prompt-only agent、ungated multi-agent workflow、AutoResearch gated workflow 的比较协议可复查，且 PHMGA/Vibench provider/data/contract 资格可审计。失败条件是 sample-level metadata-H5 alignment 未通过、OpenRouter/BigModel model policy 不合规、或 RM101 仍只能产生 reject-evidence bundle。

**Stage 2: Evidence production and boundary preservation.** 目标是产生 claim-evidence validity、unsupported claim count、response coverage、negative-result retention、artifact contract、Stage C/D rows 等证据。成功条件不是运行日志存在，而是结果满足 eligibility gate 并能被 claim_evidence_registry 引用。失败条件是 synthetic/offline sanity check 被提升为 main result，或 rate-limit/reject evidence 被隐藏。

**Stage 3: Manuscript integration.** 目标是把 evidence-bearing claims 写入 P2 manuscript/TeX，并保持每条 claim 可追踪到 protocol、evidence、review issue 或 limitation。成功条件是 manuscript claim registry、figure/table provenance、citation registry、compile report 和 export constraints 一致。失败条件是正文主张超过 evidence registry，或 graph/Canvas/dashboard 被用作研究真相。

**Stage 4: Independent review and response closure.** 目标是用 P3/P4 的 reviewer rounds、issue maps、response drafts、revision evidence maps 和 coverage checks 验证主张是否经得住攻击。成功条件是 hard fail 有 claim_id/evidence_id/location/actionable fix，response coverage 完整，negative/reject evidence 未被移除。失败条件是 author exit 被当成 node close，或 reviewer-critical blocker 被改写成 advisory note。

## Stage-Hypothesis Mapping

Stage 0 supports H1 and H2 by fixing the problem, contribution boundary, and reviewer-attack surface before evidence is interpreted. Stage 1 supports H1 and H3 by fixing the node set, baseline workflows, budget, metrics, provider/model allowance, adapter preflight, and artifact contract. Stage 2 is the main evidence stage for H1, H2, and H3: H1 depends on claim validity and unsupported-claim comparisons; H2 depends on response coverage, hard-fail closure, and negative-result retention; H3 depends on provider/data/artifact eligibility and Stage C/D rows. Stage 3 supports H1 and H2 by allowing only registry-backed claims into the manuscript. Stage 4 tests H2 most directly through independent review and response closure, while also blocking H1/H3 if reviewers find unsupported claims or ineligible result evidence.

## Fixed-Budget Planning Boundary

The planned comparison must use a fixed node set, fixed run budget, fixed provider/model allowance, and fixed review rounds before results are interpreted. The current proposal-stage allowance is: manual checklist, prompt-only agent, ungated multi-agent workflow, and AutoResearch gated workflow as baselines/conditions; OpenRouter free models only and BigModel GLM-4.7-flash free only for provider-controlled runs; and distinct independent review rounds before any final-threshold score update. These are planning constraints, not proof that provider policy, adapter alignment, selected backend, or formal rows are already resolved.

## Route Final-Threshold Readiness

P0_04 的最终阈值问题不是“formal evidence 是否已经被 P0_04 执行完成”，而是“技术路线是否已经把每个 formal-evidence gate 分配给明确阶段、owner、metric、stop condition、fallback branch 和 no-overclaim boundary”。如果一个 reviewer 要求 P0_04 自身证明 metadata-H5 alignment、selected backend、Stage C/D rows、P3/P4 response closure 或 final validator pass，评审对象就从“技术路线节点”漂移成了下游执行节点。

本节点的路线合格标准是：S0 锁定 P0_01-P0_03 的问题、假设和贡献边界；S1 锁定固定节点集、baseline、预算、provider/model allowance、adapter preflight 和 artifact contract 的进入条件；S2 锁定 claim validity、unsupported claim、response coverage、negative-result retention、Stage C/D formal rows 的证据行；S3 规定只有 registry-backed claims 能进入 manuscript/figure/table/citation/TeX；S4 规定 reviewer attack 必须映射到 claim/evidence/location/action，并保留 hard fail、blocked status、negative/reject evidence 和 final validator blocker。

因此，P0_04 可以声称“路线、OKR、证据 owner、停止规则和降级路径已经可审计”，但不能声称 provider/model compliance 已由本节点证明、metadata-H5 alignment 已全量通过、selected_global_best_backend 已锁定、Stage C/D rows 已接受、P3/P4 response closure 已完成，或 final validator 已通过。

## 阶段性计划与 OKR

**O1: 让候选贡献可证伪。** KR1: RC1-RC4 均映射到 H1-H3 或 EQ1-EQ3。KR2: 每个 contribution claim 有 required evidence、downgrade rule 和 stop condition。KR3: final narrative 不使用未证实的 first/better/automatic 表述。

**O2: 让 formal evidence 可选择。** KR1: provider/model policy 只允许 OpenRouter free model 和 BigModel GLM-4.7-flash free model。KR2: Vibench adapter 完成 sample-level metadata-H5 alignment preflight。KR3: PHMGA artifact contract、Stage C main rows、Stage D ablation rows 和 selected_global_best_backend 均被锁定。KR4: RM101 reject-evidence rows 保留，不作为 positive selection evidence。

**O3: 让 manuscript claims 可审计。** KR1: 每条 P2/P3/P4 manuscript or response claim 都有 claim_id/evidence_id。KR2: unsupported, weak, contradicted, not_applicable 等 support status 明确保留。KR3: figure/table/citation/review response 均能回指到 registry。

**O4: 让审稿攻击闭环。** KR1: independent reviewer pass rate、hard-fail closure rate、response coverage rate 和 negative-result retention rate 被记录。KR2: 任何 below-threshold score、unresolved adapter blocker、rate-limit interruption 或 reject evidence 都进入 blocker/risk ledger。KR3: final submission 前 `scripts/validate_research_truth.py --require-submission` 通过。

## 风险分支说明

**Risk branch A: formal evidence not eligible.** 如果 provider policy、adapter alignment、artifact contract、Stage C/D rows 或 backend lock 任一失败，则停止 result-level claim，保留为 blocker/reject evidence，并把 manuscript wording 降级为 protocol or limitation。

**Risk branch B: governance contribution not distinguishable.** 如果 RC1/RC2/RC3/RC4 在 reviewer view 中塌缩成 generic multi-agent orchestration 或 engineering bookkeeping，则回到 P0_03 收窄 novelty boundary，增加 reviewer-attack/falsification sentence，而不进入实验执行。

**Risk branch C: claim registry and manuscript diverge.** 如果正文 claim 没有 claim_id/evidence_id，或 evidence registry 与 figure/table/review response 不一致，则阻断 handoff，修正 registry 或降级 claim。

**Risk branch D: review gate below final threshold.** 如果节点级 review 能推进但 final submission threshold 仍低于 90，则记录 blocker，后续通过 targeted strengthening 或 re-review 处理；不得因为 graph 已推进就声称 submission-ready。

## 当前结论

P0_04 的技术路线把 hypothesis、实验/评价、指标、stop condition 和风险分支绑定到同一套 claim/evidence 身份层。当前只证明路线和 OKR 可审计、可评审、可降级；不证明 AutoResearch 已经优于任何 baseline，也不证明 formal PHMGA/Vibench evidence 已可用于最终投稿。
