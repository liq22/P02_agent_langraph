# P1_04_核心想法轻量验证

## 节点定位
本节点是叶子节点。
本节点首先是轻量实验节点，而不是通用正文 / review 节点。
本节点负责在显式 execution contract 下完成一轮 baseline-first 的有界验证，并产出最小实验账本。

## 读取规则
- README.md 只作为入口，不承载正文
- 正文放在 @docs/manuscript.md
- 实验执行依赖 @artifacts/execution_contract.yaml
- 智能体默认不读取 @docs/HUMAN_ONLY.md
- index.md 由脚本自动生成，可先为空
- 静态 schema 与静态关系不在本节点重复维护
- 进入 `fix` 后，智能体不得修改 README.md 与 status.yaml

## 完成标准
- @artifacts/execution_contract.yaml 已存在，且 `contract_mode` 明确
- baseline 已跑通或已被明确记录为当前可复现实验基线
- 已生成或更新 @artifacts/auto_experiment/results.tsv
- 已生成或更新 @logs/auto_experiment/latest_run.log
- 至少形成一轮可解释的 keep / discard 结论
- 节点可以推进到 `review`，或把结果交给 `P1_05`

## TODO_AI
- [ ] 生成或校验 @artifacts/execution_contract.yaml；若缺失，先从 `templates/execution_contract.template.yaml` 起步
- [ ] 若当前仅能审阅边界，维持 `contract_mode: review_only`
- [ ] 仅在 repo_path / run_command / metric parser 可执行时，升级到 `contract_mode: executable`
- [ ] 跑通 baseline，并记录最小可复现条件
- [ ] 执行一轮 bounded experiment campaign
- [ ] 判断 keep / discard，并形成结论摘要
- [ ] 写回本节点的 `lifecycle.stage` 与 `progress_pct`

## TODO_人类
- [ ] 审核 execution contract 是否可信
- [ ] 审核 `contract_mode` 是否与当前真实可执行性一致
- [ ] 审核 baseline 与结果账本是否可解释
- [ ] 决定是推进到 `review` 还是交给 `P1_05`
- [ ] 如需重开实验节点，手动修改 stage
