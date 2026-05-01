# P1_05_初步验证结果整理

## 节点定位
本节点是叶子节点。
本节点首先是结果整理与证据定界节点。
本节点负责把 `P1_04` 的实验账本压缩成 claim-safe 的结果注册表、假设状态和可写入正文的最小摘要。

## 读取规则
- README.md 只作为入口，不承载正文
- 正文放在 @docs/manuscript.md
- 核心输入是 @research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
- 智能体默认不读取 @docs/HUMAN_ONLY.md
- index.md 由脚本自动生成，可先为空
- 静态 schema 与静态关系不在本节点重复维护
- 进入 `fix` 后，智能体不得修改 README.md 与 status.yaml

## 完成标准
- 已读取并核对 @research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
- 已生成或更新 @artifacts/result_registry.yaml
- 已生成或更新 @artifacts/hypothesis_status.yaml
- 已生成或更新 @artifacts/paper_ready_result_summary.md，且证据位置明确
- 已区分 supported / unsupported / unclear，不抬高 claim 强度

## TODO_AI
- [ ] 读取并校验 @research/P1_实验设计与仓库蓝图/P1_04_核心想法轻量验证/artifacts/auto_experiment/results.tsv
- [ ] 写出 @artifacts/result_registry.yaml
- [ ] 写出 @artifacts/hypothesis_status.yaml
- [ ] 写出 @artifacts/paper_ready_result_summary.md
- [ ] 标注证据位置与未决风险

## TODO_人类（按需）
- [ ] 审核 result registry 是否没有夸大结论
- [ ] 审核 hypothesis status 是否区分 supported / unsupported / unclear
- [ ] 审核结果摘要是否可直接服务 table / figure / claim
- [ ] 如需重开结果整理节点，手动修改 stage
