"""Observation-conditioned PHM decision graph derived from public rollout state."""

from __future__ import annotations

from dataclasses import dataclass

from phm_agent_benchmark.phase1 import EpisodeTrajectory
from phm_agent_benchmark.phase1.environment import (
    PHASE1_BASE_RUNTIME_CONTRACT,
)


GRAPH_DYNAMIC_RUNTIME_CONTRACT = "phase1_graph_dynamic_generic_ablation_v3"
GRAPH_DYNAMIC_RUNTIME_CONTRACTS = frozenset(
    {
        "phase1_graph_dynamic_generic_ablation_v2",
        GRAPH_DYNAMIC_RUNTIME_CONTRACT,
    }
)


STATES = (
    "Inspect",
    "Hypothesize",
    "Analyze",
    "Check",
    "Monitor",
    "Revise",
    "Recover",
    "Submit",
)

# These are public environment events, not labels inferred by the Agent.  The
# environment may omit ``public_condition_event`` entirely; that is the current
# default and retains the original six-state path.
MONITOR_EVENTS = ("fault_onset", "operating_condition_change")
REVISION_EVENTS = ("no_information", "hypothesis_contradiction")
OBSERVATION_EVENTS = MONITOR_EVENTS + REVISION_EVENTS

ALLOWED_TRANSITIONS = {
    "Inspect": {"Inspect", "Hypothesize", "Analyze", "Monitor", "Revise", "Recover"},
    "Hypothesize": {"Hypothesize", "Analyze", "Monitor", "Revise", "Recover"},
    "Analyze": {"Analyze", "Check", "Monitor", "Revise", "Recover"},
    "Check": {"Inspect", "Check", "Analyze", "Monitor", "Revise", "Recover", "Submit"},
    "Monitor": {
        "Inspect",
        "Hypothesize",
        "Analyze",
        "Check",
        "Monitor",
        "Revise",
        "Recover",
        "Submit",
    },
    "Revise": {
        "Inspect",
        "Hypothesize",
        "Analyze",
        "Check",
        "Monitor",
        "Revise",
        "Recover",
        "Submit",
    },
    "Recover": {
        "Inspect",
        "Hypothesize",
        "Analyze",
        "Check",
        "Monitor",
        "Revise",
        "Submit",
        "Recover",
    },
    "Submit": {"Monitor", "Revise", "Recover"},
}

GRAPH_POLICY_PROFILES = (
    "full",
    "no_recovery_revision_edge",
    "no_observation_conditioned_branching",
    "no_persistent_graph_state",
    "no_replanning",
)


DYNAMIC_LEGAL_TRANSITIONS = {
    "full": {
        "Inspect": {"Inspect", "Hypothesize", "Analyze", "Monitor", "Recover"},
        "Hypothesize": {"Hypothesize", "Analyze", "Recover"},
        "Analyze": {"Analyze", "Check", "Recover"},
        "Check": {"Inspect", "Check", "Submit", "Recover"},
        "Monitor": {"Monitor", "Revise", "Recover"},
        "Revise": {
            "Inspect",
            "Hypothesize",
            "Analyze",
            "Check",
            "Monitor",
            "Submit",
            "Recover",
        },
        "Recover": {
            "Inspect",
            "Hypothesize",
            "Analyze",
            "Check",
            "Monitor",
            "Recover",
            "Submit",
        },
        "Submit": {"Recover"},
    },
    "no_recovery_revision_edge": {
        "Inspect": {"Inspect", "Hypothesize", "Analyze", "Monitor"},
        "Hypothesize": {"Hypothesize", "Analyze"},
        "Analyze": {"Analyze", "Check"},
        "Check": {"Inspect", "Check", "Submit"},
        "Monitor": {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Submit"},
        "Submit": {"Submit"},
    },
    "no_observation_conditioned_branching": {
        "Inspect": {"Inspect", "Hypothesize", "Analyze", "Recover"},
        "Hypothesize": {"Hypothesize", "Analyze", "Recover"},
        "Analyze": {"Analyze", "Check", "Recover"},
        "Check": {"Inspect", "Check", "Submit", "Recover"},
        "Recover": {"Inspect", "Hypothesize", "Analyze", "Check", "Recover", "Submit"},
        "Submit": {"Recover"},
    },
    "no_persistent_graph_state": {
        "Inspect": {"Inspect", "Hypothesize", "Analyze", "Monitor", "Recover"},
        "Hypothesize": {"Hypothesize", "Analyze", "Recover"},
        "Analyze": {"Analyze", "Check", "Recover"},
        "Check": {"Inspect", "Check", "Submit", "Recover"},
        "Monitor": {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Recover", "Submit"},
        "Recover": {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Recover", "Submit"},
        "Submit": {"Recover"},
    },
    "no_replanning": {
        "Inspect": {"Inspect", "Hypothesize", "Analyze", "Monitor", "Recover"},
        "Hypothesize": {"Hypothesize", "Analyze", "Recover"},
        "Analyze": {"Analyze", "Check", "Recover"},
        "Check": {"Inspect", "Check", "Submit", "Recover"},
        "Monitor": {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Recover", "Submit"},
        "Recover": {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Recover", "Submit"},
        "Submit": {"Recover"},
    },
}


@dataclass(frozen=True, slots=True)
class GraphPolicyConfig:
    """The four preregistered graph toggles; all are enabled by default."""

    recovery_revision_edge: bool = True
    observation_conditioned_branching: bool = True
    persistent_graph_state: bool = True
    replanning: bool = True
    runtime_contract: str = PHASE1_BASE_RUNTIME_CONTRACT

    def __post_init__(self) -> None:
        if self.runtime_contract not in {
            PHASE1_BASE_RUNTIME_CONTRACT,
            *GRAPH_DYNAMIC_RUNTIME_CONTRACTS,
        }:
            raise ValueError(
                f"unsupported Graph runtime contract: {self.runtime_contract}"
            )

    @classmethod
    def for_profile(
        cls,
        profile: str,
        *,
        runtime_contract: str = PHASE1_BASE_RUNTIME_CONTRACT,
    ) -> "GraphPolicyConfig":
        if profile not in GRAPH_POLICY_PROFILES:
            raise ValueError(f"unknown graph policy profile: {profile}")
        disabled = {
            "no_recovery_revision_edge": "recovery_revision_edge",
            "no_observation_conditioned_branching": "observation_conditioned_branching",
            "no_persistent_graph_state": "persistent_graph_state",
            "no_replanning": "replanning",
        }.get(profile)
        values = {
            "recovery_revision_edge": True,
            "observation_conditioned_branching": True,
            "persistent_graph_state": True,
            "replanning": True,
        }
        if disabled is not None:
            values[disabled] = False
        return cls(**values, runtime_contract=runtime_contract)

    @property
    def profile(self) -> str:
        toggles = (
            self.recovery_revision_edge,
            self.observation_conditioned_branching,
            self.persistent_graph_state,
            self.replanning,
        )
        profiles = {
            (True, True, True, True): "full",
            (False, True, True, True): "no_recovery_revision_edge",
            (True, False, True, True): "no_observation_conditioned_branching",
            (True, True, False, True): "no_persistent_graph_state",
            (True, True, True, False): "no_replanning",
        }
        try:
            return profiles[toggles]
        except KeyError as exc:
            raise ValueError("graph policy toggles do not name a registered profile") from exc

    @property
    def dynamic(self) -> bool:
        return self.runtime_contract in GRAPH_DYNAMIC_RUNTIME_CONTRACTS

    def to_dict(self) -> dict[str, bool]:
        return {
            "recovery_revision_edge": self.recovery_revision_edge,
            "observation_conditioned_branching": self.observation_conditioned_branching,
            "persistent_graph_state": self.persistent_graph_state,
            "replanning": self.replanning,
        }


def _successful(trajectory: EpisodeTrajectory, tool_name: str) -> bool:
    return any(
        step.tool_name == tool_name and step.error is None for step in trajectory.steps
    )


def _rollout_state(
    trajectory: EpisodeTrajectory, replay_sample_ids: tuple[str, ...]
) -> str:
    """Return the original six-state decision from public rollout fields."""

    if replay_sample_ids:
        predicted_samples = {
            str(step.tool_result["source_sample_id"])
            for step in trajectory.steps
            if step.tool_name == "model.predict"
            and step.error is None
            and step.tool_result is not None
            and "source_sample_id" in step.tool_result
        }
        if all(sample_id in predicted_samples for sample_id in replay_sample_ids):
            return "Submit"
        current = next(
            sample_id
            for sample_id in replay_sample_ids
            if sample_id not in predicted_samples
        )
        read_index = next(
            (
                index
                for index, step in enumerate(trajectory.steps)
                if step.tool_name == "data.read_window"
                and str(step.tool_args.get("sample_id")) == current
                and step.error is None
            ),
            None,
        )
        if read_index is None:
            return "Inspect"
        if not (
            _successful(trajectory, "op.list")
            or _successful(trajectory, "model.list")
        ):
            return "Hypothesize"
        operator_calls = sum(
            step.tool_name == "op.run"
            and step.error is None
            and step.tool_result is not None
            and str(step.tool_result.get("source_sample_id")) == current
            for step in trajectory.steps[read_index + 1 :]
        )
        return "Check" if operator_calls >= 11 else "Analyze"
    if not _successful(trajectory, "data.read_window"):
        return "Inspect"
    if not (
        _successful(trajectory, "op.list")
        or _successful(trajectory, "model.list")
    ):
        return "Hypothesize"
    if _successful(trajectory, "model.predict"):
        return "Submit"
    if _successful(trajectory, "model.schema"):
        return "Check"
    return "Analyze"


def decision_state(
    trajectory: EpisodeTrajectory,
    replay_sample_ids: tuple[str, ...] = (),
    *,
    config: GraphPolicyConfig | None = None,
    previous_state: str | None = None,
    observation_event: str | None = None,
) -> str:
    """Select a state without reading targets or inferring unobserved events."""

    policy = GraphPolicyConfig() if config is None else config
    if policy.dynamic and observation_event not in {None, "operating_condition_change"}:
        raise ValueError(
            "dynamic graph routing accepts only operating_condition_change events"
        )
    candidate: str
    if trajectory.steps and trajectory.steps[-1].error is not None:
        if policy.recovery_revision_edge:
            candidate = "Recover"
            return _validate_dynamic_state(candidate, previous_state, policy)

    if policy.observation_conditioned_branching and observation_event in OBSERVATION_EVENTS:
        if observation_event in MONITOR_EVENTS:
            candidate = "Monitor"
            return _validate_dynamic_state(candidate, previous_state, policy)
        if policy.recovery_revision_edge and policy.replanning:
            candidate = "Revise"
            return _validate_dynamic_state(candidate, previous_state, policy)
        candidate = "Monitor"
        return _validate_dynamic_state(candidate, previous_state, policy)

    if (
        policy.persistent_graph_state
        and previous_state == "Monitor"
        and policy.recovery_revision_edge
        and policy.replanning
    ):
        candidate = "Revise"
        return _validate_dynamic_state(candidate, previous_state, policy)

    candidate = _rollout_state(trajectory, replay_sample_ids)
    return _validate_dynamic_state(candidate, previous_state, policy)


def _validate_dynamic_state(
    candidate: str,
    previous_state: str | None,
    config: GraphPolicyConfig,
) -> str:
    if not config.dynamic:
        return candidate
    transitions = DYNAMIC_LEGAL_TRANSITIONS[config.profile]
    if candidate not in transitions:
        raise ValueError(
            f"state {candidate} is unreachable for graph profile {config.profile}"
        )
    if previous_state is not None:
        if previous_state not in transitions:
            raise ValueError(
                f"prior state {previous_state} is unreachable for graph profile {config.profile}"
            )
        if candidate not in transitions[previous_state]:
            raise ValueError(
                f"illegal {config.profile} transition: {previous_state} -> {candidate}"
            )
    return candidate


def legal_transitions(
    config: GraphPolicyConfig | None = None,
) -> dict[str, set[str]]:
    policy = GraphPolicyConfig() if config is None else config
    source = DYNAMIC_LEGAL_TRANSITIONS[policy.profile] if policy.dynamic else ALLOWED_TRANSITIONS
    return {state: set(targets) for state, targets in source.items()}


def transition_validity_from_states(
    states: list[str] | tuple[str, ...],
    config: GraphPolicyConfig | None = None,
) -> float:
    if not states:
        return 0.0
    if len(states) == 1:
        return 1.0
    transitions = legal_transitions(config)
    return sum(
        left in transitions and right in transitions[left]
        for left, right in zip(states, states[1:])
    ) / (len(states) - 1)


def transition_validity(
    trajectory: EpisodeTrajectory,
    config: GraphPolicyConfig | None = None,
) -> float:
    states = [step.decision_state for step in trajectory.steps if step.decision_state]
    return transition_validity_from_states(states, config)
