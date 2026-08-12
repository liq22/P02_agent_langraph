"""Secondary decision-graph metrics; shared benchmark metrics remain primary."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .adapter import ALLOWED_TRANSITIONS, GRAPH_STATES


def evaluate_decision_states(steps: Sequence[Mapping[str, Any]]) -> dict[str, float | None]:
    states = [str(step.get("decision_state")) for step in steps if step.get("decision_state") is not None]
    if not states:
        return {
            "state_transition_validity": None,
            "graph_loop_ratio": None,
            "replan_count": None,
            "distinct_state_coverage": None,
        }
    invalid = sum(
        right not in ALLOWED_TRANSITIONS.get(left, set())
        for left, right in zip(states, states[1:])
    )
    loops = sum(left == right for left, right in zip(states, states[1:]))
    recoveries = sum(state == "recover" for state in states)
    denominator = max(1, len(states) - 1)
    return {
        "state_transition_validity": 1.0 - invalid / denominator,
        "graph_loop_ratio": loops / denominator,
        "replan_count": float(recoveries),
        "distinct_state_coverage": len(set(states)) / len(GRAPH_STATES),
    }
