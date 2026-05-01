---
name: deai_cn_skill
description: Patch Chinese doctoral thesis prose to reduce AI-like style with minimal local edits while preserving mathematical logic, experimental settings, terminology, chapter structure, and claims.
---

# DeAI CN Skill

## Use When

Use for Chinese doctoral thesis prose when the task is to reduce AI-like style through local, patch-ready edits.

Use this for:
- high-risk sentences with template-like structure, slogans, labels, or empty summaries
- local cleanup of brackets, quotation marks, stock transitions, and path-string prose
- chapter-level risk triage when the user asks for minimal de-AI revision
- P2 writing nodes that need style repair without changing scientific content

Do not use this to rewrite a chapter, expand content, invent terms, or change the paper's mathematical logic, experimental protocol, terminology, section structure, or claim scope.

## Non-Negotiables

- Preserve mathematical logic, formula symbols, experimental settings, result criteria, formal definitions, field names, search queries, protocols, status codes, and operator/table headers.
- Make the smallest useful edit. Prefer one sentence replacement over paragraph rewriting.
- Keep serious academic tone. Do not make the prose conversational just to avoid AI-like style.
- Do not make a sentence longer, more abstract, or less falsifiable.
- Do not add unsupported claims, new limitations, new datasets, new baselines, or new terminology.
- For appendices, protocol wording, system output, retrieval strings, and official fields, preserve exact wording unless the user explicitly asks otherwise.

## Risk Triage

- Chapter 6 is the highest-risk area. Prioritize process slogans, role labels, state-word packaging, bracket overload, and path-string prose.
- Chapter 4 has a smaller number of explanatory or colloquial sentences. Tighten them first when they appear.
- Chapters 2, 3, and 5 mainly need cleanup of stock connectors such as "需要指出的是", "需要说明的是", "换言之", and "也就是说".
- Chapter 1 is not the main battlefield. Only remove unnecessary quotation-mark emphasis or obvious template wording.

## Two-Layer Check

Check visual structure and language/content together.

Visual and structure checks:
- Keep bullets and enumerations only for contributions, experimental settings, notation, definitions, checklists, or other genuinely list-shaped material.
- Convert unnecessary lists into continuous argument chains.
- Avoid frequent bold emphasis; let sentence structure carry emphasis.
- Avoid page-level outline stacking where several dense lists appear back to back.
- Avoid the repeating pattern of one topic sentence, three bullets, and a closing summary.

Language and content checks:
- Remove correct but empty claims such as "具有重要意义", "显著提升性能", or "体现了优势" unless a number, formula, dataset, baseline, ablation result, setting, boundary condition, or failure mode supports them nearby.
- Each paragraph should anchor at least one hard detail when possible: a number, symbol, dataset, comparison method, ablation finding, experimental setup, boundary condition, or failure mode.
- Replace neutral encyclopedia summary with a judgment about tradeoff, scope, cost, failure condition, or applicability when the source text supports it.
- Add a short boundary sentence only when needed and only when it follows from existing evidence.

## Patch Rules

1. Bracket examples: avoid frequent "概念（即...）", "方法（如...）", and "模块（包括...）" chains. Rewrite with attributive, appositive, or adverbial phrasing, such as "包括注意力机制与特征拼接在内的现有深度融合方法".
2. Quotation marks: use quotes only for direct quotations, first formal definitions, real system fields, retrieval strings, protocol labels, condition names, policy names, and legal names. Replace decorative quotes with direct academic phrasing.
3. Sentence stitching: after removing brackets, quotes, or labels, repair word order so the sentence reads as one smooth academic sentence. Prefer connectors such as "基于", "包括...在内的", "表现为", "呈现出", "在...条件下", and "对应于" when they clarify syntax.
4. Template connectors: reduce "不是...而是...", "需要指出的是", "需要说明的是", "换言之", and "也就是说". Keep them only when a real contrast, definition, or boundary clarification requires them.
5. Write/read metaphors: replace "写入/落实/落盘/读出" by object-specific verbs. For priors, rules, constraints, or knowledge entering a model, prefer "融入", "嵌入", "编码到", "纳入", "施加", or "体现在...中". For information obtained from signals, features, models, or results, prefer "提取", "识别", "估计", "恢复", "揭示", "反映", "表明", or "追溯". Keep hardware or storage usages when literal.
6. Slogan verbs: tighten "赋能", "驱动", "构建", "实现", "刻画", and "闭环" only when they sound managerial or empty. Preserve fixed technical terms and mature academic collocations.
7. Path strings: do not write process chains as labels such as "STFT--RMS--转矩归一化" unless it is a real system output or log. Prefer normal prose: "先进行短时傅里叶变换，再计算均方根特征，并结合转矩信号进行归一化处理".
8. System-scheme tone: avoid slogan-like roles or stages such as "感知-规划-执行-审查", "规划者-执行者-审查者", or "先验证、后执行" unless formally defined. Rewrite them as direct module relationships, constraints, or procedures.

## Output Contract

For each edited sentence or compact passage:

1. State whether it is a high-risk AI-like sentence.
2. Name the risk source in one short phrase.
3. Provide the minimal patch-ready replacement.
4. Mention any preserved mathematical, experimental, terminological, or field-level constraint when relevant.

Default output shape:

```text
原句：...
判断：高风险/中风险/低风险，原因是...
替换：...
保留：公式、术语、实验口径或字段未改。
```

When the source sentence is acceptable, say so and avoid editing it.
