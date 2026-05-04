# Install v4 into P02_agent_langraph

Run from the root of `liq22/P02_agent_langraph` after extracting this package.

```bash
cp -R p02_submission_ready_goal_package/docs/submission_ready_goal ./docs/
mkdir -p tools/submission_ready_goal
cp p02_submission_ready_goal_package/tools/*.py ./tools/submission_ready_goal/
```

Optional Claude Code assets:

```bash
cp -R p02_submission_ready_goal_package/claude_code_assets/.claude ./.claude
```

Initialize FSM state:

```bash
cp docs/submission_ready_goal/fsm/current_goal_state.template.yaml \
   docs/submission_ready_goal/fsm/current_goal_state.yaml
```

First validation command after P1_01 outputs are generated:

```bash
python tools/submission_ready_goal/validate_p1_01_node_outputs.py \
  --node-dir research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用
```

After review artifacts exist:

```bash
python tools/submission_ready_goal/validate_p1_01_node_outputs.py \
  --node-dir research/P1_实验设计与仓库蓝图/P1_01_数据层_集中数据与子模块引用 \
  --require-review
```
