# Eval Report: research/P2_论文撰写/P2_02_初稿_md/P2_02_04_方法

- score: `0.9429`
- pass_threshold: `0.8`
- passed: `True`
- blocking_validator: `None`
- human_gate_required: `True`

## Validators

### markdown_structure
- passed: `True`
- score: `1.0`
- summary: Markdown 结构可接受。

### acceptance_checklist
- passed: `True`
- score: `1.0`
- summary: 验收契约完成率 15/15。

### claim_evidence_check
- passed: `True`
- score: `1.0`
- summary: 识别强主张 1 条，缺证据 0 条。
- details:
  - 检测到 claim_evidence_map，可提升可审计性。

### citation_integrity
- passed: `True`
- score: `0.8`
- summary: 检测到数字引用 18 个、链接 2 个。

### edit_scope_check
- passed: `True`
- score: `1.0`
- summary: 修改范围符合 harness。

### latex_build
- passed: `True`
- score: `0.8`
- summary: 未发现 .tex 文件；跳过 LaTeX 构建。

### node_status_check
- passed: `True`
- score: `1.0`
- summary: status.yaml 检查完成，当前状态：seed。
