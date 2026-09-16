# Paper 2 Figure Plan

结果图调用 Benchmark 共享绘图器；本仓库 `experiments/run.sh finish <root>` 负责统计与图。方法图可以独立 SVG，但不复制结果绘图实现。

遵循 `nature-figure` 原则：scientific semantics > decoration；物理尺寸与可编辑 SVG/PDF；source CSV；颜色有固定语义；不用 glow、3D、卡片式 dashboard、AI brain/icon。

## Figure 1 — What graph control actually changes
**Message:** 原 Graph 是 state cue + tool visibility 的联合干预。

A：公开 history/remaining budget；B：state selector；C：cue to model；D：tool mask；E：canonical action。标出 base reachable states，Monitor/Revise 只在 dynamic profile 中出现。

## Figure 2 — Cue × filter factorial
2×2：reactive/state/filter/both；所有格子统一处理历史 state 信息。箭头只表达 provider-visible intervention 与 action path。

## Figure 3 — Main effects and interaction
森林图：state main effect、filter main effect、interaction、original Graph vs Generic。task primary 与 cost 分面，不把 state-transition count 作为 headline。

## Figure 4 — Beneficial vs harmful restriction
左：finite toy 的 mask loss / selection loss；右：真实 task 中可审查的 lost/retained action case。toy 与 PHM result 明确分区。

## Figure 5 — Sequence/resource sensitivity
当前 horizon command 只能标为 sensitivity；纯 horizon 图只有 nested-prefix + 明确 budget regime 完成后才绘制。

## Figure 6 — Dynamic public event
只展示实际发布的 operating-condition event → state/action change；不得画成 Agent 从振动自主检测 fault onset。

## One-click output

```bash
bash experiments/run.sh finish "$STUDY_ROOT"
```

共享 plotter 输出 SVG/PDF/PNG 与 source CSV。图注注明 model/provider、task、asset/episode 数、interval 类型、study stage。若 component inactive，图中直接标为 inactive，不用空的“null effect”包装机制结论。
