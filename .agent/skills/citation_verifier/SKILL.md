---
name: citation_verifier
description: Verify citation facts and claim support inside one selected research node. Use when P0, P2, P3, or P4 work depends on references, bibliography entries, local PDFs, DOI/URL metadata, or citation-backed claims before handoff.
---

# Citation Verifier

## 使用时机
- 当前 node 的 gap、related work、claim、review issue 或 response 依赖 citation。
- 需要核验 BibTeX、PDF、DOI、URL、标题、作者、年份、venue 或引用是否真正支持对应表述。
- `prompts/research_prompt.md`、review verdict 或用户明确要求 citation 验证。

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- `prompts/research_prompt.md` 与 `prompts/acceptance_checklist.yaml`
- 本地正文、claim map、review comment、response map、BibTeX、PDF、DOI、URL 或其他可核验来源

## Workflow
1. 确认本轮只验证当前 node 中会影响 handoff 的 citation。
2. 抽取 citation key、claim_id、claim context、claim_criticality、source_ref 和该 citation 支撑的具体表述。
3. 用本地 PDF、BibTeX、DOI、URL 或用户提供来源核验 title、authors、year、venue 与 claim support。
4. 不从记忆生成 BibTeX；无法核验时标为 `unverifiable`、`unverifiable_access` 或 `contradiction`，不要把它写成确定事实。
5. 生成或更新 `artifacts/citation_registry.yaml` 与 `artifacts/citation_verification_report.md`。
6. 对每条 citation 给出 action：`keep`、`revise_claim`、`replace_source` 或 `block_handoff`。
7. 只有 `core_claim` 与 `comparison_baseline` citation 的重大问题默认阻断 submission handoff；`background_context` 的不可核验默认是 advisory，除非 action 明确为 `block_handoff`。
8. 返回 blocking gaps、可保留引用和必须改写的 claim。

## Output Contract
`artifacts/citation_registry.yaml` 最小结构：

```yaml
citations:
  - citation_key: "<key-or-placeholder>"
    claim_id: "<claim id supported by this citation>"
    claim_context: "<which sentence/claim uses it>"
    claim_criticality: core_claim | background_context | method_reference | comparison_baseline | format_supporting
    source_ref: "<local pdf/bib/url/doi>"
    source_locator: "<page/section/doi/url/bib entry locator>"
    bibliographic_facts_checked:
      title: true
      authors: true
      year: true
      venue: true
    support_status: verified | minor_distortion | major_distortion | unverifiable | unverifiable_access | contradiction
    support_strength: "<how directly the source supports this claim>"
    action: keep | revise_claim | replace_source | block_handoff
```

Submission hard-block policy:
- Hard block if `action: block_handoff`.
- Hard block if `claim_criticality` is `core_claim` or `comparison_baseline` and `support_status` is `major_distortion`, `unverifiable`, `unverifiable_access`, or `contradiction`.
- Do not hard block a `background_context` citation solely because it is unverifiable; mark the claim as advisory/rewrite debt instead.

`artifacts/citation_verification_report.md` 应列出：
- verified citations
- citation-claim support status by claim criticality
- missing or unverified sources
- handoff blockers

## Boundaries
- 不替代文献综述写作、manuscript worker 或 reviewer。
- 不凭记忆补全 citation metadata。
- 不把未验证引用改写成确定事实。
- 不声称 citation registry 通过就等于 claim scientifically true；它只证明 citation support 可审计。
- 不跨 node 重建全局 bibliography，除非当前 node 明确声明该输出。

## stop_with
- 没有可核验来源且 citation 支撑关键 claim
- citation key 或 claim context 无法定位
- 需要用户提供 PDF、DOI、URL 或 bibliography source
- 验证结果要求正文改写但当前 node 不允许编辑正文
