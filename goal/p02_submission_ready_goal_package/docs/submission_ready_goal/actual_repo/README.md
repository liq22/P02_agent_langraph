
# Actual Repository Calibration

This directory records the concrete facts that distinguish the current `P02_agent_langraph` repository from a generic submission-ready template.

## Current graph state

The current scheduler state is expected to point to:

```text
research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用
```

The resource package therefore starts from `P1_01`, not from paper prose, PHMGA formal experiments, or final TeX.

## Current selected node

```text
research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用
```

This is an `evidence_leaf` node. Its purpose is to converge data objects, data lineage, and submodule references. It is not an execution node.

## Current PHMGA submodule

```text
path: research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
url: https://github.com/PHMbench/PHMGA.git
branch: journal_thesis
```

## Current critical blocker

PHMGA main tables currently must not be treated as completed evidence until passed rows exist. The paper package therefore blocks `S5_PAPER_EVIDENCE_LOCK` if no passed formal rows are available.
