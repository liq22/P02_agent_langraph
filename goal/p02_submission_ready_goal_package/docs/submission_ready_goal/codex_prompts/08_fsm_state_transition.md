# Codex Prompt 08 — FSM State Transition

Use this prompt when advancing from one `/goal` state to the next.

## Required steps

1. Read `docs/submission_ready_goal/fsm/codex_goal_fsm.yaml`.
2. Identify current state.
3. List required artifacts for current state.
4. Run the current state's validator or documented check.
5. Write command output to `docs/submission_ready_goal/runtime_logs/<state>_<timestamp>.log` or selected-node `logs/`.
6. Update the relevant checklist only if the validation output supports it.
7. Update `docs/submission_ready_goal/fsm/current_goal_state.yaml`.
8. Stop and report.

## Forbidden

- Do not skip states.
- Do not manually mark complete without validation output.
- Do not move to paper writing from data or project gates.
