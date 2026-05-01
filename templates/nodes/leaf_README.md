# 叶子节点标题

## 节点定位
本节点是叶子节点。
它是最小研究单元，也是最小调度单元。

## 读取规则
- README.md 只作为入口，不承载正文
- status.yaml 是本节点调度状态真源
- 正文、prompt、skill、review、artifact 与 log 按需创建
- 不把 graph、Canvas、dashboard 或 index 当真源

## 完成标准
- 本节点目标、边界与停止条件已明确
- 必要产物已写回 node-local truth
- status.yaml 已更新到真实当前状态
- 如需 human / reviewer gate，先显式创建 review slot 与 acceptance gate

## TODO_AI
- [ ] 读取 README.md 与 status.yaml
- [ ] 只在本节点内执行一次 bounded control unit
- [ ] 按需创建 docs / prompts / skills / artifacts / review / logs
- [ ] 写回本节点真源并停止

## TODO_人类
- [ ] 确认本节点目标与边界
- [ ] 判断是否需要激活 review gate
- [ ] 审核关键结论或高风险分叉
