"""Graph-guided treatment policy over the benchmark Generic LLM agent."""

from __future__ import annotations

from collections.abc import Mapping
import json
import re
from typing import Any

from phm_agent_benchmark.phase1 import (
    EpisodeTrajectory,
    GenericLLMToolAgent,
    TaskInstance,
)

from .state import (
    GRAPH_DYNAMIC_RUNTIME_CONTRACTS,
    GraphPolicyConfig,
    decision_state,
)


STATE_TOOLS = {
    "Inspect": {"data.search", "data.describe", "data.read_window", "data.summarize"},
    "Hypothesize": {"op.list", "model.list", "data.summarize"},
    "Analyze": {
        "data.summarize",
        "op.list",
        "op.schema",
        "op.run",
        "model.list",
        "model.schema",
    },
    "Check": {
        "data.summarize",
        "op.schema",
        "op.run",
        "model.list",
        "model.schema",
        "model.predict",
    },
    "Monitor": {
        "data.describe",
        "data.read_window",
        "data.summarize",
        "op.list",
        "op.schema",
        "op.run",
        "model.list",
        "model.schema",
        "model.predict",
    },
    "Revise": {
        "data.describe",
        "data.read_window",
        "data.summarize",
        "op.list",
        "op.schema",
        "op.run",
        "model.list",
        "model.schema",
        "model.predict",
    },
    "Recover": {
        "data.describe",
        "data.read_window",
        "data.summarize",
        "op.list",
        "op.schema",
        "op.run",
        "model.list",
        "model.schema",
        "model.predict",
    },
    "Submit": {"submit"},
}


def _event_from_mapping(
    value: Mapping[str, Any],
    *,
    dynamic: bool = False,
) -> tuple[str, str] | None:
    raw = value.get("public_condition_event")
    if not isinstance(raw, Mapping):
        return None
    event = raw.get("event")
    if not isinstance(event, str):
        return None
    event_id = raw.get("event_id")
    if dynamic:
        if set(raw) != {"event", "event_id", "release_index"}:
            raise ValueError("dynamic public_condition_event has an invalid payload shape")
        if event != "operating_condition_change":
            raise ValueError(
                "dynamic public_condition_event cannot name a fault or anomaly onset"
            )
        if not isinstance(event_id, str) or re.fullmatch(r"occ-\d{8}", event_id) is None:
            raise ValueError(
                "dynamic public_condition_event requires an opaque occ event ID"
            )
        release_index = raw.get("release_index")
        if type(release_index) is not int or release_index < 1:
            raise ValueError(
                "dynamic public_condition_event release_index must be positive"
            )
    token = event if event_id is None else f"{event}:{event_id}"
    return event, token


def public_observation_event(
    task: TaskInstance,
    trajectory: EpisodeTrajectory,
    *,
    runtime_contract: str | None = None,
) -> tuple[str, str] | None:
    """Read only an explicit public graph event; never infer one from signal values."""

    dynamic = runtime_contract in GRAPH_DYNAMIC_RUNTIME_CONTRACTS
    context = task.public_context
    if dynamic:
        if not isinstance(context, Mapping):
            return None
        signal = _event_from_mapping(context, dynamic=True)
        if signal is None:
            return None
        raw = context["public_condition_event"]
        if raw["release_index"] != context.get("replay_cursor"):
            raise ValueError("dynamic graph event does not match the released replay cursor")
        return signal
    if trajectory.steps:
        latest = trajectory.steps[-1].observation_summary
        if isinstance(latest, Mapping):
            context = latest.get("context")
            if isinstance(context, Mapping):
                signal = _event_from_mapping(context)
                if signal is not None:
                    return signal
            signal = _event_from_mapping(latest)
            if signal is not None:
                return signal
    context = task.public_context
    if isinstance(context, Mapping):
        return _event_from_mapping(context)
    return None


class ReactiveSequentialAgent(GenericLLMToolAgent):
    """Matched Generic LLM control with no behavior override."""

    agent_id = "reactive-sequential-agent"


class GraphDecisionAgent(GenericLLMToolAgent):
    """Generic LLM treatment whose only extension is graph decision control."""

    agent_id = "graph-decision-agent"

    def __init__(
        self,
        *args: Any,
        policy_config: GraphPolicyConfig | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.policy_config = GraphPolicyConfig() if policy_config is None else policy_config
        self._active_state = "Inspect"
        self._last_observation_token: str | None = None

    def decision_state(
        self, task: TaskInstance, trajectory: EpisodeTrajectory
    ) -> str:
        replay_sample_ids = tuple(
            str(value) for value in task.public_context.get("replay_sample_ids", [])
        )
        signal = public_observation_event(
            task,
            trajectory,
            runtime_contract=self.policy_config.runtime_contract,
        )
        event: str | None = None
        if signal is not None:
            event, token = signal
            if self.policy_config.persistent_graph_state:
                if token == self._last_observation_token:
                    event = None
                else:
                    self._last_observation_token = token
        previous_state = (
            self._active_state if self.policy_config.persistent_graph_state else None
        )
        self._active_state = decision_state(
            trajectory,
            replay_sample_ids,
            config=self.policy_config,
            previous_state=previous_state,
            observation_event=event,
        )
        return self._active_state

    def available_tools(
        self,
        task: TaskInstance,
        trajectory: EpisodeTrajectory,
        tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        del task, trajectory
        allowed = STATE_TOOLS[self._active_state]
        return [tool for tool in tools if tool["function"]["name"] in allowed]

    def conversation(
        self, task: TaskInstance, trajectory: EpisodeTrajectory
    ) -> list[dict[str, Any]]:
        messages = super().conversation(task, trajectory)
        if not (
            self.policy_config.dynamic
            and not self.policy_config.persistent_graph_state
        ):
            return messages
        sanitized: list[dict[str, Any]] = []
        for message in messages:
            clean = dict(message)
            if clean.get("role") == "tool" and isinstance(clean.get("content"), str):
                content = json.loads(str(clean["content"]))
                content.pop("decision_state", None)
                clean["content"] = json.dumps(content, sort_keys=True)
            sanitized.append(clean)
        return sanitized

    def system_prompt(self, task: TaskInstance) -> str:
        guidance = {
            "Inspect": "Acquire the bounded public signal context.",
            "Hypothesize": "Choose the analysis family that can test the task hypothesis.",
            "Analyze": "Produce the typed feature artifacts required by a model.",
            "Check": "Run or verify the numerical prediction before accepting it.",
            "Monitor": "Inspect the explicit public data-condition change before continuing.",
            "Revise": "Replan the data, operator, or diagnosis branch from public results.",
            "Recover": "Use the previous error to make one corrected, non-repeated call.",
            "Submit": "Submit the numerical result with supporting artifact references.",
        }[self._active_state]
        return (
            super().system_prompt(task)
            + f"\n\nCurrent decision state: {self._active_state}. {guidance} "
            "Choose exactly one of the tools exposed for this state."
        )


# Compatibility import for local callers created before the CORE correction.
# The formal runner constructs ``GraphDecisionAgent`` directly.
GraphGuidedPHMAgent = GraphDecisionAgent
