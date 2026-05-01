# 父节点标题

## 节点定位
本节点是父节点。
它只负责组织子节点边界与局部路由，不承载完整正文或替子节点执行深层工作。

## 读取规则
- README.md 只做入口，不承载详细正文
- status.yaml 是本节点调度状态真源
- 子节点 folder 是实际研究与执行单位
- docs / prompts / skills / artifacts / review / logs 按需创建
- 不把 graph、Canvas、dashboard 或 index 当真源

## 子节点
- @子节点A/
- @子节点B/

## 完成标准
- 子节点边界清楚且没有重复职责
- 必要依赖关系已写入 backend/relations/edge_registry.json
- 如需协调状态更新，只更新本父节点 local truth

## TODO_AI
- [ ] 检查子节点边界是否清楚
- [ ] 检查是否应 route child first
- [ ] 只更新当前父节点必要的局部状态或 handoff

## TODO_人类
- [ ] 审核子节点划分是否合理
- [ ] 决定是否激活关键 review / fix / submission gate
