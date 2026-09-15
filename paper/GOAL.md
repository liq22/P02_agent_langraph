# P2 Goal — 分离状态提示与工具过滤

主要产物：cue/filter 四格的真实任务后果、成本，以及有效／有害控制的具体证据。方法属于 P02_agent_langraph。读取 [RESEARCH](RESEARCH.md) 与[控制损失推导](theory/03_control_loss.md)。

## 干预检查

对相同可达历史检查四个组件条件的 provider 消息和可见工具。四组历史消息都去除旧 `decision_state` 字段；当前状态提示和工具过滤分别由各自开关决定。规范 rollout 保留可观测状态。原 `graph` 与组件实验作为不同处理报告。

先检查 `graph-no-memory` 是否改变状态、消息或可见动作。如果每步从完整历史重建同一策略，记录其非辨识性，停止该无效消融的完整 cohort；不将机械零差异解释为记忆没有价值。

## 执行与比较

```bash
bash experiments/run.sh plan --experiment graph-components \
  --provider "$PHM_PROVIDER" --model "$PHM_MODEL" --protocol "$DEV_PROTOCOL"
# 对应在线实验授权后，以同一模型、资产、预算和显式限额运行。
bash experiments/run.sh finish "$STUDY_ROOT"
```

主比较为 `factorial-reactive/state/filter/both` 的任务效果、交互与成本。检查必要行动被过滤后是否造成任务损失，并展示实际可观察结果。最优 $Q^*$ 未知时，以受控任务证据解释机制；invalid-call rate 不作为 regret。

当前 `horizon` 同时改变选样与比例预算；报告长度／选样／资源敏感性。纯 horizon 研究需另行实现固定最长序列的嵌套前缀。dynamic-v3 使用公开条件事件，按原协议单独分析。

## 验收

所有四格实际输入符合定义、共享匹配环境、分配分母完整，结果支持具体的提示效应、过滤效应或其未确定范围。保留负效应和有害过滤案例。将任务结果和控制适用范围回写所属仓库现有全文；图结构示意图本身不构成效果证据。

## 开始与结束

先读 [DEV](../DEV.md)、[CORE](../CORE.md) 和[当前状态](../obsidian/log/LOCAL_AGENT_STATE.md)。本仓库 `dev` 是写作与实验集成的唯一核心分支。正文入口为 [main.md](draft/main.md)。

每轮完成一个主要产物，记录实际命令、复用结果、新输出与一个下一步。在线推理须有当前任务的授权和明确请求／token 限额；历史授权不自动延续。
