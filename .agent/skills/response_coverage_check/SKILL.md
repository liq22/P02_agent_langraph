---
name: response_coverage_check
description: Check whether one selected response node covers its target comments, mappings, or evidence rows. Use for bounded completeness checks before packaging or submission.
---

# Response Coverage Check

## 使用时机
- 当前 node 需要覆盖率检查
- 已有 critique / mapping / response 草稿
- 需要发现漏项、弱证据或未响应行

## 必要输入
- 目标 node 的 `README.md`、`status.yaml`
- 本地 mapping / response / evidence 文件

## Workflow
1. 确认检查范围只在当前 node。
2. 读取 critique 行、mapping 行与 response 行。
3. 标出 covered、weakly-covered、missing、unsupported-commitment 四类状态。
4. 对每条 factual sentence 检查 provenance，对每个 promise 检查 approval。
5. 输出一份紧凑 coverage report。
6. 更新状态并返回。

## 产出
- coverage/provenance/commitment report
- 本地状态更新

## 边界
- 不替代 response_worker 写正文
- 不刷新 graph
- 不跨 node 汇总

## stop_with
- 缺 mapping 或 response 输入
- 覆盖检查范围不明确
