
# P1_01 Actual Execution Order

Use this file before starting `/goal` execution in the current repository.

## 1. Confirm selected node

```bash
cat backend/graph/graph_status.json
```

Expected:

```text
next_node = research::P1_实验设计与仓库蓝图::P1_01_数据层_集中数据与子模块引用
```

If this is not true, stop and follow the actual `next_node`.

## 2. Confirm PHMGA submodule declaration

```bash
cat .gitmodules
git submodule status --recursive
```

Expected path:

```text
research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA
```

## 3. Read node stack in order

```text
README.md
status.yaml
skills/local_entry.md
prompts/research_prompt.md
prompts/acceptance_checklist.yaml
prompts/review_rubric.yaml
skills/SKILL.md
```

## 4. Produce node-local outputs only

Write into the selected node only:

```text
docs/
artifacts/
logs/
review/
status.yaml only if stage/progress update is justified
```

Do not write into graph JSON or Canvas.

## 5. Run node package validation

```bash
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs
```

## 6. Refresh graph after bounded step

```bash
python scripts/refresh_views.py --mode graph_only
```

## 7. Do not advance to P1_02 until P1_01 external review passes

`review/verdict.yaml` must contain:

```yaml
review_complete: true
overall_verdict: pass
hard_fail: false
independence_confirmed: true
```
