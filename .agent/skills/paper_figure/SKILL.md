---
name: paper_figure
description: Generate or refine one node-local figure plan, figure draft, or caption-ready visual mapping from already available local evidence. Use for figure-centric nodes after routing.
---

# Paper Figure

## 使用时机
- 当前 node 的核心产物是图、流程图、图注关联或 figure plan
- 上游结果或 claim 已经基本可用
- 需要单节点内的图表推进

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 必要时 `docs/manuscript.md`、figure plan、claim map
- 若存在，读取 `artifacts/figure_manifest.yaml` 以判断 provenance、版本和锁定状态

## Workflow
1. 确认图表任务只服务当前 node。
2. 若 `status.yaml` 中当前 node 已 `done`，不要覆盖已接受图；只能建议 reopen 或生成 revision version。
3. 读取最小必要的图表输入。
4. 接受三类初稿来源：TeX/TikZ/PGFPlots、Python 生成图、人类提供 PDF。
5. 生成或更新 figure plan、figure draft、claim-to-figure 对齐与 `artifacts/figure_manifest.yaml`；优先检查关键图是否能服务 skim reader，但不要把“好看”替代 evidence。
6. 为每张图写清 source_kind、source_path、output_path、claim_ref、evidence_ref、necessity、first_callout_location、caption obligation 与不能声称的边界。
7. 检查 Nature-style small/simple/clear、非本领域读者可读性、IEEE-style raster 至少 300 dpi 或 vector 输出、caption 自解释、色盲/灰度可读和来源/权限 provenance。
8. 把输出限制在本地 artifacts / figures 目录。
9. 更新状态并返回。

## 产出
- figure plan / figure draft / claim-figure map
- `artifacts/figure_manifest.yaml`
- 本地状态更新

## Figure Manifest
```yaml
figures:
  - figure_id: fig1
    source_kind: tex | python | pdf
    source_path: "<path>"
    output_path: "<path>"
    claim_ref: "<claim id>"
    evidence_ref: "<data/result/source>"
    necessity: essential | supporting | supplemental
    first_callout_location: "<manuscript location of first callout>"
    status: draft | accepted | locked
    locked_by_node_status: done
    quality_checks:
      vector_or_dpi_checked: true
      caption_self_contained: true
      colorblind_or_grayscale_checked: true
      source_permission_checked: true
```

## 边界
- 不选 node
- 不从零代替实验生成证据
- 不刷新 graph
- `fix` 是 review/response gate，不是 figure freeze；只有 `done` 锁定已接受图
- 不把 decorative figure 写入 manuscript gate；每张图必须有 claim_ref、evidence_ref 和 first_callout_location
- 不声称 figure manifest 通过就等于图有顶刊说服力；它只证明来源、证据绑定和叙事位置可审计

## stop_with
- 没有可用的上游结果或 claim
- 图无法对应到明确 claim 或 evidence source
- 图没有 first callout 或在正文叙事中不是必要/支持/补充关系
- node 已 `done` 且任务要求覆盖已接受 figure
- 图表需求不属于当前 node
- 需要 repo-wide figure reorganization
