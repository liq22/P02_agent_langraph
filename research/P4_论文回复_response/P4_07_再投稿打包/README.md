# P4_07_再投稿打包

## 节点定位
本节点是叶子节点。
本节点负责承载本主题的正文、局部 review 与局部执行状态。

## 读取规则
- README.md 只作为入口，不承载正文
- 正文放在 @docs/manuscript.md
- 智能体默认不读取 @docs/HUMAN_ONLY.md
- index.md 由脚本自动生成，可先为空
- 静态 schema 与静态关系不在本节点重复维护
- 进入 `fix` 后，智能体不得修改 README.md 与 status.yaml

## 完成标准
- 已读取并核对 @../../P2_论文撰写/P2_03_定稿_tex/tex/main.tex
- 已读取并核对 @../P4_04_正式回复_tex_或_doc/artifacts/response_letter.tex
- 已读取并核对 @../P4_06_修改证据/artifacts/revision_evidence_map.yaml
- 已生成或更新 @artifacts/resubmission_bundle_manifest.yaml
- 至少 1 份 AI review
- 独立 reviewer agent 已完成外部评审；人类按需介入
- 所有 comment 都已在 @review/response.yaml 中响应
- 当前节点确认可以进入 `fix`

## TODO_AI
- [ ] 校验 clean manuscript / response / evidence / figures / tables / metadata
- [ ] 写出 @artifacts/resubmission_bundle_manifest.yaml
- [ ] 完成一轮 AI review
- [ ] 更新 @review/response.yaml
- [ ] 检查是否满足进入 `fix` 的条件

## TODO_人类（按需）
- [ ] 审核 submission bundle 是否满足外部约束
- [ ] 审核 AI review 是否有效
- [ ] 决定是否进入 `fix`
- [ ] 如需重开节点，手动修改 stage
