# Tools for P02 Submission-Ready Goal Package v3

Run from the P02 repository root after copying this directory into `tools/submission_ready_goal/`.

## Data audit

```bash
python tools/submission_ready_goal/audit_data_resource_pack.py --data-root <DATA_ROOT> --output-dir docs/submission_ready_goal/runtime_logs/data_audit
```

## LLM key check

```bash
python tools/submission_ready_goal/verify_llm_keys.py --output docs/submission_ready_goal/runtime_logs/llm_key_check.json
```

The verifier reads `OPENROUTER_API_KEY` and `BIGMODEL_API_KEY` from the environment and never writes key values to logs.

## Claude handoff validation

```bash
python tools/submission_ready_goal/validate_claude_handoff.py --handoff <handoff.yaml>
```

## FSM state validation

```bash
python tools/submission_ready_goal/validate_goal_fsm_state.py --state docs/submission_ready_goal/fsm/current_goal_state.yaml
```

## P1_01 package validation

```bash
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-outputs --json
python tools/submission_ready_goal/validate_p1_01_node_package.py --repo-root . --require-review --json
```

`--require-review` checks the independent review gate, not just file presence: `review/verdict.yaml` must be complete/pass/non-hard-fail with confirmed independence and a non-pending reviewer id, and the AI/human review files must not still contain placeholder markers.

## Traceability lock validation

```bash
python tools/submission_ready_goal/validate_traceability_lock.py --matrix docs/submission_ready_goal/traceability/traceability_matrix.yaml
```

## Submission gate validation

```bash
python tools/submission_ready_goal/validate_submission_gate.py --gate docs/submission_ready_goal/final_submission_gate_status.yaml
```
