"""Provider-independent construction for the registered Graph dynamic runtime."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from numbers import Real
from typing import Any

from phm_agent_benchmark.phase1 import (
    Budget,
    EpisodeRunner,
    EpisodeTrajectory,
    Phase1Evaluator,
    Phase1ModelPool,
    Phase1ToolRuntime,
    TaskInstance,
    TaskSpec,
    anomaly_target,
    diagnosis_label,
    fit_model_pool,
)
from phm_agent_benchmark.phase1.environment import (
    PHASE1_PUBLIC_CONDITION_EVENT_RUNTIME_CONTRACT,
    Phase1EnvironmentAdapter,
    Phase1PublicConditionEventSchedule,
)
from phm_agent_benchmark.phase1.experiment import (
    _fold_bearings,
    _rotation,
    _select_evenly,
    samples_by_bearing,
    select_diagnosis_model,
)
from phm_agent_benchmark.phase1.policy_adapter import (
    Phase1PolicyAdapter,
    phase1_task_spec,
)


@dataclass(frozen=True, slots=True)
class DynamicPublicSequence:
    public_sequence_id: str
    sample_ids: tuple[str, ...]
    public_domain_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class DynamicEpisodeResult:
    task: TaskInstance
    task_spec: TaskSpec
    trajectory: EpisodeTrajectory
    evaluation: Any
    artifact_descriptors: Mapping[str, Mapping[str, Any]]


def build_master_sequences(
    data: Any,
    dataset_protocol: Mapping[str, Any],
    dynamic_protocol: Mapping[str, Any],
    rotation_name: str,
) -> dict[str, DynamicPublicSequence]:
    """Construct eight public master sequences without returning bearing identity."""

    sequence_contract = dynamic_protocol["sequence_construction"]
    master_horizon = int(sequence_contract["master_horizon"])
    if master_horizon != 12:
        raise ValueError("graph dynamic v1 requires a 12-sample master horizon")
    groups = samples_by_bearing(data)
    rotation = _rotation(dataset_protocol, rotation_name)
    test_bearings = _fold_bearings(dataset_protocol, [rotation["test"]])
    expected_count = int(dynamic_protocol["dataset"]["held_out_bearings"])
    if len(test_bearings) != expected_count:
        raise ValueError("held-out bearing count disagrees with the dynamic protocol")

    masters: list[tuple[str, ...]] = []
    for bearing in test_bearings:
        available = tuple(groups[bearing])
        if len(available) < master_horizon:
            raise ValueError("held-out bearing cannot supply the master horizon")
        indices = tuple(
            (index * (len(available) - 1)) // (master_horizon - 1)
            for index in range(master_horizon)
        )
        if len(set(indices)) != master_horizon:
            raise ValueError("master sequence selection produced a duplicate index")
        masters.append(tuple(available[index] for index in indices))

    expected_domains = tuple(
        int(value) for value in sequence_contract["expected_public_domain_schedule"]
    )
    sequences: dict[str, DynamicPublicSequence] = {}
    for ordinal, sample_ids in enumerate(sorted(masters), start=1):
        sequence_id = f"sequence-{ordinal:04d}"
        public_domains = tuple(
            _normalize_domain_id(data.describe_sample(sample_id).get("domain_id"))
            for sample_id in sample_ids
        )
        if public_domains != expected_domains:
            raise ValueError(
                f"{sequence_id} public domain schedule disagrees with the protocol"
            )
        sequences[sequence_id] = DynamicPublicSequence(
            public_sequence_id=sequence_id,
            sample_ids=sample_ids,
            public_domain_ids=public_domains,
        )
    if len(sequences) != expected_count:
        raise ValueError("dynamic sequence IDs are not one-to-one with held-out bearings")
    return sequences


def build_event_catalog(dynamic_protocol: Mapping[str, Any]) -> dict[tuple[Any, ...], str]:
    """Assign opaque event IDs by the frozen sorted logical key; no hash is used."""

    design = dynamic_protocol["experiment_design"]
    rotations = sorted({str(value) for value in design.get("rotations", ["rotation_0"])})
    if not rotations:
        rotations = ["rotation_0"]
    sequence_count = int(dynamic_protocol["dataset"]["held_out_bearings"])
    sequence_ids = [f"sequence-{index:04d}" for index in range(1, sequence_count + 1)]
    release_indices = sorted(
        int(value)
        for value in dynamic_protocol["sequence_construction"][
            "expected_change_release_indices_zero_based"
        ]
    )
    keys = sorted(
        (
            int(seed),
            rotation,
            sequence_id,
            release_index,
        )
        for seed in design["seeds"]
        for rotation in rotations
        for sequence_id in sequence_ids
        for release_index in release_indices
    )
    catalog = {
        key: f"occ-{ordinal:08d}" for ordinal, key in enumerate(keys, start=1)
    }
    expected = int(
        dynamic_protocol["public_event_contract"]["event_id_catalog"][
            "expected_logical_events"
        ]
    )
    if len(catalog) != expected:
        raise ValueError("event catalog size disagrees with the dynamic protocol")
    return catalog


def event_schedule_for_horizon(
    dynamic_protocol: Mapping[str, Any],
    sequence: DynamicPublicSequence,
    *,
    seed: int,
    rotation: str,
    horizon: int,
) -> tuple[tuple[str, ...], Phase1PublicConditionEventSchedule]:
    allowed_horizons = tuple(
        int(value) for value in dynamic_protocol["sequence_construction"]["horizons"]
    )
    if horizon not in allowed_horizons:
        raise ValueError("horizon is not registered by the dynamic protocol")
    sample_ids = sequence.sample_ids[:horizon]
    domains = sequence.public_domain_ids[:horizon]
    catalog = build_event_catalog(dynamic_protocol)
    event_ids = {
        release_index: catalog[
            (int(seed), str(rotation), sequence.public_sequence_id, release_index)
        ]
        for release_index in range(1, horizon)
        if domains[release_index] != domains[release_index - 1]
    }
    return sample_ids, Phase1PublicConditionEventSchedule(
        sample_domain_ids=dict(zip(sample_ids, domains, strict=True)),
        event_ids_by_release_index=event_ids,
    )


def budget_for_horizon(
    dynamic_protocol: Mapping[str, Any], horizon: int
) -> Budget:
    try:
        raw = dynamic_protocol["budgets"]["by_horizon"][horizon]
    except KeyError:
        raw = dynamic_protocol["budgets"]["by_horizon"].get(str(horizon))
    if not isinstance(raw, Mapping):
        raise ValueError("dynamic protocol has no budget for the selected horizon")
    expected = {
        "max_tool_calls",
        "max_window_reads",
        "max_operator_calls",
        "max_model_calls",
        "max_llm_turns",
        "max_data_points",
        "max_data_bytes",
        "max_wall_clock_seconds",
    }
    if set(raw) != expected:
        raise ValueError("dynamic horizon budget fields do not match Benchmark Budget")
    return Budget(**dict(raw))


def fit_dynamic_model_pool(
    data: Any,
    dataset_protocol: Mapping[str, Any],
    rotation_name: str,
    *,
    train_samples_per_bearing: int,
    validation_samples_per_bearing: int,
) -> tuple[Phase1ModelPool, str]:
    """Fit the same frozen numerical experts used by every matched dynamic cell."""

    groups = samples_by_bearing(data)
    rotation = _rotation(dataset_protocol, rotation_name)
    train_bearings = _fold_bearings(dataset_protocol, rotation["train"])
    validation_bearings = _fold_bearings(dataset_protocol, [rotation["validation"]])
    diagnosis_train = [
        sample_id
        for group in train_bearings
        for sample_id in _select_evenly(groups[group], train_samples_per_bearing)
    ]
    healthy_train = [
        sample_id
        for sample_id in diagnosis_train
        if diagnosis_label(data.private_record(sample_id)) == "healthy"
    ]
    diagnosis_validation = [
        sample_id
        for group in validation_bearings
        for sample_id in _select_evenly(groups[group], validation_samples_per_bearing)
    ]
    healthy_validation = [
        sample_id
        for sample_id in diagnosis_validation
        if diagnosis_label(data.private_record(sample_id)) == "healthy"
    ]
    window = dataset_protocol["window_protocol"]
    window_args = {
        "start": int(window["start_point"]),
        "end": int(window["end_point"]),
        "channels": tuple(int(value) for value in window["channel_indices"]),
        "max_points": int(window["max_returned_points"]),
    }
    models = fit_model_pool(
        data,
        diagnosis_train,
        healthy_train,
        healthy_validation_sample_ids=healthy_validation,
        **window_args,
    )
    selected, _scores = select_diagnosis_model(
        data,
        models,
        diagnosis_validation,
        **window_args,
    )
    return models, selected


async def run_dynamic_episode(
    data: Any,
    models: Phase1ModelPool,
    policy: Any,
    dataset_protocol: Mapping[str, Any],
    dynamic_protocol: Mapping[str, Any],
    sequence: DynamicPublicSequence,
    *,
    seed: int,
    rotation: str,
    horizon: int,
    strip_historical_decision_state: bool,
) -> DynamicEpisodeResult:
    sample_ids, schedule = event_schedule_for_horizon(
        dynamic_protocol,
        sequence,
        seed=seed,
        rotation=rotation,
        horizon=horizon,
    )
    window = dataset_protocol["window_protocol"]
    private_targets = {
        sample_id: anomaly_target(data.private_record(sample_id))
        for sample_id in sample_ids
    }
    task = TaskInstance(
        "online_replay_monitoring",
        sequence.public_sequence_id,
        private_targets,
        {
            "replay_sample_ids": list(sample_ids),
            "window_start": int(window["start_point"]),
            "window_end": int(window["end_point"]),
            "channels": [int(value) for value in window["channel_indices"]],
            "max_points": int(window["max_returned_points"]),
        },
    )
    budget = budget_for_horizon(dynamic_protocol, horizon)
    environment = Phase1EnvironmentAdapter(
        Phase1ToolRuntime(data, models, task),
        task_instance=task,
        runtime_contract=PHASE1_PUBLIC_CONDITION_EVENT_RUNTIME_CONTRACT,
        public_condition_events=schedule,
    )
    adapter = Phase1PolicyAdapter(
        policy,
        runtime_contract=PHASE1_PUBLIC_CONDITION_EVENT_RUNTIME_CONTRACT,
        strip_historical_decision_state=strip_historical_decision_state,
    )
    task_spec = phase1_task_spec(task, budget)
    trajectory = await EpisodeRunner(environment).run(task_spec, adapter)
    evaluation = Phase1Evaluator().evaluate(task, trajectory)
    return DynamicEpisodeResult(
        task=task,
        task_spec=task_spec,
        trajectory=trajectory,
        evaluation=evaluation,
        artifact_descriptors=environment.artifact_descriptors,
    )


def _normalize_domain_id(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("public domain_id must be a finite integral number")
    numeric = float(value)
    if not math.isfinite(numeric) or not numeric.is_integer():
        raise ValueError("public domain_id must be a finite integral number")
    normalized = int(value)
    return normalized


__all__ = [
    "DynamicEpisodeResult",
    "DynamicPublicSequence",
    "budget_for_horizon",
    "build_event_catalog",
    "build_master_sequences",
    "event_schedule_for_horizon",
    "fit_dynamic_model_pool",
    "run_dynamic_episode",
]
