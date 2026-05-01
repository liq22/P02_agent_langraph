# Legacy Design Notes

This file preserves the older generated template notes for reference only. It is not the current operating architecture. Use the root `README.md`, `docs/architecture/obsidian_canvas_workflow.md`, `docs/dev.md`, and `.agent/skills/` as the current path.

# 研究OS_完整文档包

本包基于“轻节点协议 + 全局 graph + 按需生长能力槽位”的主方案生成。

## 根规则

- README.md 只做入口，不承载正文
- 叶子节点正文统一放在 docs/manuscript.md
- docs/HUMAN_ONLY.md 默认不进入智能体读取路径
- schema 默认上收至 registry/schema_registry
- 关系默认上收至 graph/ 与 relations/
- index.md 由脚本自动生成，可先为空
- 父节点默认只保留壳，docs/skills/templates/artifacts/logs 可为空

## 主目录

- P0_项目申请书
- P1_实验设计与仓库蓝图
- P2_论文撰写
- P3_论文模拟评审与修改_多轮
- P4_论文回复_response
- graph
- relations
- views
- indexes
- registry
- archived shared skills reference
- 共享模板

# 快速开始

use this template 来初始化仓库，

codex/cc 来初始化

# skill

1. /Research_graph_manager
2.

# prerequisites

1. tex 环境
2. torch 环境
3. 其他依赖见 requirements.txt
4. claude code / codex 二者都有
