# Academic Expression And Claim Calibration

generated_at: 2026-05-05

## Scope And Inputs

This artifact audits the current P2 manuscript prose for template-like language, low-information transitions, claim inflation, and evidence-boundary drift. Inputs checked:

- `research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/introduction.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/preliminary.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/method.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/tex/sections/experiment.tex`
- `research/P2_论文撰写/P2_03_定稿_tex/artifacts/claim_evidence_registry.yaml`
- `research/P2_论文撰写/P2_02_初稿_md/P2_02_05_实验与讨论/artifacts/claim_map.yaml`
- `research/P2_论文撰写/P2_04_形式检查/artifacts/formal_check_report.md`
- `research/P2_论文撰写/P2_01_风格选择_IEEE_Elsevier_Nature/artifacts/venue_requirements.yaml`

This pass is node-local and bounded to academic expression and claim calibration. It now records which replacements are present in the synchronized TeX files, and it does not change scientific claims, result status, evidence strength, citation meaning, figure provenance, method variables, or final-submission blockers.

Application map: `research/P2_论文撰写/P2_05_去AI味道/artifacts/tex_rewrite_target_map.yaml`.

## Patch Entries

### P2_05_R001

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex:17`

原句：AutoResearch is studied as a human--agent research operating system whose unit of analysis is a schedulable research node.

判断：中风险，原因是 "research operating system" 容易读成宽泛系统口号。

替换：This draft evaluates AutoResearch at the level of schedulable research nodes, where each node carries local prompts, artifacts, review status, and closure conditions.

保留：unit of analysis、schedulable research node、prompt/artifact/review/closure terminology unchanged.

### P2_05_R002

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex:17`

原句：The contribution of this draft is the auditable connection among claims, evidence artifacts, review gates, response coverage, and transparent limitations.

判断：高风险，原因是 "the contribution is the auditable connection" 抽象且像总结模板。

替换：The draft's process claim is that manuscript statements should remain traceable to evidence artifacts, review gates, response coverage, and limitation records before stronger claims are allowed.

保留：process-claim boundary; no empirical performance claim added.

### P2_05_R003

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/introduction.tex:1`

原句：AutoResearch addresses a practical bottleneck in agent-assisted research: a fluent manuscript can hide whether claims, evidence, protocols, reviews, and responses are actually connected.

判断：低风险，原因是句子有具体问题对象和审稿风险。

替换：保持原句。

保留：agent-assisted research bottleneck and claim/evidence/protocol/review/response linkage unchanged.

### P2_05_R004

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/introduction.tex:3`

原句：The one-sentence contribution of this draft is that AutoResearch turns manuscript production into a claim-grounded operating procedure: every substantive claim should point to evidence, every evidence item should retain its boundary, and every phase transition should pass through review or recorded human gate logic.

判断：高风险，原因是 "turns manuscript production into" 和 "operating procedure" 带有宣传式转换口吻。

替换：The draft makes a narrower process contribution: it specifies that substantive manuscript claims should point to evidence, evidence items should retain explicit boundaries, and phase transitions should be backed by review evidence or recorded gate logic.

保留：one-sentence contribution, claim-to-evidence rule, evidence-boundary rule, review/gate rule unchanged.

### P2_05_R005

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/introduction.tex:5`

原句：The current TeX synchronization is intentionally conservative.

判断：中风险，原因是 "intentionally conservative" 说明态度但信息密度低。

替换：The current TeX synchronization carries forward only the evidence already accepted by upstream nodes.

保留：TeX synchronization scope and upstream-node evidence boundary unchanged.

### P2_05_R006

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/method.tex:3`

原句：The intervention is the AutoResearch contract, not the language model alone.

判断：中风险，原因是 "contract" 缺少组成内容时可能显得像标签。

替换：The intervention is the documented AutoResearch node package, which includes local framing, claim/evidence/protocol registries, pre-execution gates, independent review, and response coverage; it is not a test of a language model alone.

保留：intervention/comparison distinction and method variables unchanged.

### P2_05_R007

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/method.tex:9`

原句：The procedure is fixed before result interpretation.

判断：低风险，原因是句子短且服务方法可复现性。

替换：保持原句，或在 venue compression pass 中改为 "All procedure fields are fixed before result interpretation."

保留：pre-result protocol lock unchanged.

### P2_05_R008

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/sections/experiment.tex:19`

原句：The main discussion result is negative as much as positive: the workflow preserved unsupported and uncertain evidence instead of converting it into stronger prose.

判断：高风险，原因是 "negative as much as positive" 是修辞化对比。

替换：The discussion reports both the bounded synthetic/offline signal and the retained unsupported or uncertain evidence; unsupported rows are not rewritten as support.

保留：negative/unclear evidence retention and no-upgrade rule unchanged.

### P2_05_R009

目标位置：`research/P2_论文撰写/P2_03_定稿_tex/tex/main.tex:33`

原句：Those limitations remain explicit because reviewer trust depends on preserving negative and uncertain evidence rather than converting it into narrative confidence.

判断：中风险，原因是 "reviewer trust depends on" 解释过满，容易像通用审稿话术。

替换：Those limitations remain explicit so that negative and uncertain evidence stays part of the manuscript record rather than being converted into stronger claims.

保留：negative/uncertain evidence preservation and limitation boundary unchanged.

## Required Questions

哪些句子只是模板化语言？ High-risk entries are P2_05_R002, P2_05_R004, and P2_05_R008. Medium-risk entries are P2_05_R001, P2_05_R005, P2_05_R006, and P2_05_R009.

哪些段落缺少信息密度或逻辑推进？ The abstract and one-sentence-contribution paragraph carry the main density risk because they summarize the mechanism before naming local prompts, artifacts, review status, response coverage, and closure conditions. The methods section is denser, but the intervention sentence should name the node package components immediately.

去掉套路后，内容是否仍然精准？ Yes. The replacements keep the same claim boundaries: process support only, preliminary synthetic/offline quantitative signal only, formal result gates blocked, negative/uncertain evidence retained, and final submission readiness not established.

## TeX Application Status

The TeX target map records that P2_05_R001, P2_05_R002, P2_05_R004, P2_05_R005, P2_05_R006, P2_05_R008, and P2_05_R009 are applied or already present in the synchronized TeX files. P2_05_R003 and P2_05_R007 are retained as no-edit-needed records to show that the pass did not force unnecessary stylistic change.

## Non-Upgrade Ledger

- No new dataset, baseline, statistical test, citation, or figure is introduced.
- No real-data generalization claim is introduced.
- No RM101 resolution claim is introduced.
- No selected-backend success claim is introduced.
- No Stage C or Stage D success claim is introduced.
- No final submission readiness claim is introduced.
- No negative, failed, rejected, blocked, or unclear evidence is removed.
