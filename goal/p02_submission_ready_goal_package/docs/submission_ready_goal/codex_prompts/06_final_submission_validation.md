# Codex Prompt: Final Submission Validation

```text
/goal
Validate final P02 submission readiness.

Run:
- git submodule status --recursive
- git -C research/P1_实验设计与仓库蓝图/P1_06_代码仓库_已有_重新初始化_子模块策略/artifacts/PHMGA rev-parse HEAD
- python scripts/refresh_views.py --mode graph_only
- python test/run_live_repo_smoke.py
- python scripts/validate_research_truth.py --require-submission

Check:
- data gate pass
- project gate pass
- paper gate pass
- final TeX exists
- claim-evidence complete
- all tables/figures trace to source artifacts

Declare submission-ready only if final submission check prints:
research truth: pass mode=submission-ready
```
