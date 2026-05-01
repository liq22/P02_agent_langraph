# P0_02_研究挑战与科学问题_工程问题

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
- 正文已收敛到 @docs/manuscript.md
- 至少 1 份 AI review
- 至少 1 份人类 review
- 所有 comment 都已在 @review/response.yaml 中响应
- 当前节点确认可以进入 `fix`

## TODO_AI
- [ ] 补正文到 @docs/manuscript.md
- [ ] 完成一轮 AI review
- [ ] 更新 @review/response.yaml
- [ ] 检查是否满足进入 `fix` 的条件

## TODO_人类
- [ ] 审核正文是否成立
- [ ] 审核 AI review 是否有效
- [ ] 决定是否进入 `fix`
- [ ] 如需重开节点，手动修改 stage
