# TESTING_QUICKSTART

Run these commands from the repository root.

## 1. Deterministic fixture acceptance

```bash
python test/run_fixture_acceptance.py
```

This validates the minimal back-end / Canvas / skill contract against a controlled fixture rooted at:

```text
test/fixtures/min_experiment_stack_repo/
```

## 2. Gateway and cockpit acceptance

```bash
python test/run_gateway_acceptance.py
```

This validates setup readiness, one-shot bounded agent launch, session log restore, and the static front-end hooks for node selection and prompt actions.

## 3. Live repository smoke test

```bash
python test/run_live_repo_smoke.py
```

This checks the current repository state without redesigning anything and without requiring a fully completed research run.

## 4. Nature-level rubric coverage

```bash
python test/run_nature_rubric_presence.py
```

This checks that every `research/**/status.yaml` node has an explicit Nature-level scoring entry in `test/NATURE_LEVEL_NODE_RUBRIC.md`.

## 5. Nature capability acceptance

```bash
python test/run_nature_capability_acceptance.py
```

This proves the truth validator accepts a complete synthetic Nature-ready submission package and rejects missing results, review-only contracts, missing reviewer independence, placeholder TeX, and missing submission manifests.

## 6. Live submission truth gate

```bash
python scripts/validate_research_truth.py --require-submission
```

This checks whether the current live `research/` tree is actually submission-ready. It is expected to fail while real research content, executable results, review closure, or the final bundle are still missing.

## 7. Combined gate

```bash
python test/run_all_acceptance.py
```

## Exit codes

- `0` = pass
- `1` = fail
- `partial` in text output is a blocking diagnostic state, not a passing exit condition
