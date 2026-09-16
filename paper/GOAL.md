# Paper 2 Goal — 分离状态提示与工具过滤的真实作用

当前目标不是增加 graph 节点，而是回答：**在相同模型、PHM 知识、观测序列、全局工具和预算下，状态提示与工具可见性约束分别何时有益、何时会删掉必要分析。**

先读 [THEORY_CONTRIBUTION_PLAN.md](THEORY_CONTRIBUTION_PLAN.md)、[FIGURE_PLAN.md](FIGURE_PLAN.md)、[RESEARCH.md](RESEARCH.md) 和 `theory/`。完整正文唯一入口仍是 `draft/main.md`；Graph 方法只在 `src/phm_graph_agent/`，实验只在 `experiments/`。

## 当前贡献链

1. **Joint graph-control treatment**：原始 Graph 同时加入 current-state cue 与 state-dependent tool visibility；不称为纯 topology effect。
2. **Cue × filter identification**：`factorial-reactive/state/filter/both` 分离两个可见干预。
3. **Control applicability boundary**：识别 harmful mask、inactive ablation、sequence/budget confounding；动态 public event 不等于 signal-inferred onset。

`graph-no-memory` 只有在可达开发 history 上实际改变 state/tool exposure 时才值得跑完整 cohort。base profile 的 Monitor/Revise 不可作为 dynamic revision 证据。

## 本地最短执行

```bash
export PHM_BENCHMARK_ROOT=/absolute/path/phm-agent-benchmark

bash experiments/run.sh test
bash experiments/run.sh plan --experiment graph-components \
  --provider "$PHM_PROVIDER" --model "$PHM_MODEL" --protocol "$DEV_PROTOCOL" --tasks replay

# 当前在线实验获得授权后再执行
bash experiments/run.sh run --experiment graph-components \
  --provider "$PHM_PROVIDER" --model "$PHM_MODEL" --protocol "$DEV_PROTOCOL" --tasks replay \
  --request-cap 128 --max-tokens 2048 --output "$STUDY_ROOT"

# 不再调用模型：统计、availability、bounds 与绘图
bash experiments/run.sh finish "$STUDY_ROOT"
```

同一 plan 用 `--only` 分批执行，不用旧 Graph/Generic 结果代替历史消息条件不同的新 factorial control。

## 必做实验

- G-E1：原始 Generic vs original Graph，估计 joint graph-control effect。
- G-E2：cue × filter 四格，状态提示/过滤 main effects 与 interaction。
- G-E3：no-memory activity precheck；inactive 就停止该消融，不浪费付费 cohort。
- G-E4：有益/有害 mask 的小型精确模型，验证控制损失分解；不冒充 PHM 性能。
- G-E5：当前 `horizon` 只作为长度/选样/资源敏感性；纯 horizon 结论需新增 nested-prefix binding 与明确 budget regime。
- G-E6：dynamic profile 只解释对已发布工况变化事件的响应，不写自主 fault-onset detection。

## 停止条件

如果 filter harm 大于 selection gain，报告 action restriction 的失效边界；如果 component 不改变 provider-visible intervention，停止该消融；如果 task primary 没有改善但成本下降，只写 efficiency result；不通过继续增加节点追求正结果。

## 写作顺序

Results：joint effect → cue/filter attribution → inactive/harmful controls → sequence/resource sensitivity → dynamic public-event extension → limits。图状态数量、节点访问次数和 workflow 复杂度都不能替代 task performance。
