#!/usr/bin/env python3
"""Accept and analyze the isolated P2-E2--P2-E7 dynamic formal cohort.

This module is deliberately provider-free.  It reads the preregistered
Generic-base dynamic-v3 protocol and canonical episode bundles, selects exactly one
non-provider terminal for every scheduled unit, and fails closed on profile,
sequence, event, transition, or denominator drift.

The result schema has no pooled-across-horizon or pooled-across-profile view:
all absolute summaries are keyed by ``horizon:cell`` and all estimates are
registered matched contrasts.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import re
import statistics
import sys
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

_GRAPH_SRC = Path(__file__).resolve().parents[1] / "src"
_BENCHMARK_SRC = Path(__file__).resolve().parents[2] / "p01-phm-agent-benchmark" / "src"
for _source_root in (_GRAPH_SRC, _BENCHMARK_SRC):
    if _source_root.is_dir() and str(_source_root) not in sys.path:
        sys.path.insert(0, str(_source_root))

from phm_agent_benchmark.phase1 import LocalPaderbornDataPort, anomaly_target
from phm_agent_benchmark.phase1.experiment import aggregate_results, load_dataset_protocol
from phm_agent_benchmark.rollout_io import read_run_bundle

from phm_graph_agent.dynamic_runtime import build_master_sequences


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
DEFAULT_DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
)
PROTOCOL_SCHEMA = "graph_dynamic_ablation_protocol_v3"
ACCEPTANCE_SCHEMA = "graph_dynamic_formal_acceptance_v3"
RESULT_SCHEMA = "graph_dynamic_formal_result_v3"
CANONICAL_FILES = frozenset(
    {
        "run.json",
        "rollout.jsonl",
        "submission.json",
        "metrics.json",
        "failures.jsonl",
        "artifacts.json",
    }
)
PROVIDER_FAILURE_KIND = "provider_error"
FORMAL_EVIDENCE_CLASS = "real_data_formal_candidate"
TASK_ID = "online_replay_monitoring"
CHANGE_INDICES = (3, 6, 9)
EVENT_NAME = "operating_condition_change"
REPLAY_MISSING_SCORE_POLICY_ID = "phase1_replay_target_adverse_missing_score_v1"
TASK_COHORT_METRICS = {
    "target_adverse_window_average_precision": "average_precision",
    "target_adverse_window_auroc": "auroc",
    "target_adverse_false_alarm_rate": "false_alarm_rate",
    "target_adverse_true_positive_rate": "true_positive_rate",
    "replay_score_coverage": "score_coverage",
}
EXPECTED_SEEDS = (20260808, 20260809, 20260810)
EXPECTED_ROTATIONS = ("rotation_0",)
EXPECTED_CELL_MATRIX = {
    "horizon_3": ["reactive", "graph_full"],
    "horizon_6": ["reactive", "graph_full"],
    "horizon_12": [
        "reactive",
        "graph_full",
        "graph_no_recovery_revision_edge",
        "graph_no_observation_conditioned_branching",
        "graph_no_persistent_graph_state",
        "graph_no_replanning",
    ],
}
MECHANISM_ABLATION_METRICS = {
    "P2-E3": (
        "event_to_Revise_transition_rate",
        "grounded_recovery_success",
        "steps_to_next_success_after_failure",
    ),
    "P2-E4": (
        "operating_condition_event_delivery_count",
        "event_to_Monitor_transition_rate",
        "event_to_Revise_transition_rate",
        "steps_from_event_to_next_successful_action",
        "steps_from_event_to_next_model_prediction",
        "post_event_repeated_action_ratio",
        "post_event_budget_exhaustion_rate",
    ),
    "P2-E5": (
        "event_to_Revise_transition_rate",
        "post_event_repeated_action_ratio",
        "repeated_action_ratio",
        "loop_incidence",
    ),
    "P2-E6": (
        "event_to_Revise_transition_rate",
        "steps_from_event_to_next_successful_action",
        "steps_from_event_to_next_model_prediction",
        "post_event_repeated_action_ratio",
        "post_event_budget_exhaustion_rate",
    ),
}
P2_E7_DYNAMIC_METRICS = (
    "operating_condition_event_delivery_count",
    "event_to_Monitor_transition_rate",
    "event_to_Revise_transition_rate",
    "steps_from_event_to_next_successful_action",
    "steps_from_event_to_next_model_prediction",
    "post_event_repeated_action_ratio",
    "post_event_budget_exhaustion_rate",
)
_ENVIRONMENT_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class GraphDynamicFormalError(ValueError):
    """Raised when a formal cohort violates the frozen dynamic contract."""


@dataclass(frozen=True, slots=True)
class Cell:
    horizon: int
    name: str
    arm: str
    graph_profile: str | None
    agent_profile_id: str

    @property
    def key(self) -> str:
        return f"h{self.horizon}:{self.name}"


@dataclass(frozen=True, slots=True)
class Unit:
    seed: int
    rotation: str
    public_sequence_id: str
    cell: Cell

    @property
    def key(self) -> tuple[int, str, str, int, str]:
        return (
            self.seed,
            self.rotation,
            self.public_sequence_id,
            self.cell.horizon,
            self.cell.name,
        )


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GraphDynamicFormalError(f"{label} must be a mapping")
    return dict(value)


def _list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise GraphDynamicFormalError(f"{label} must be a list")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GraphDynamicFormalError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise GraphDynamicFormalError(f"{label} must be finite")
    return result


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphDynamicFormalError(f"cannot read {label} {path}: {exc}") from exc
    return _mapping(value, f"{label} {path}")


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise GraphDynamicFormalError(f"cannot read {label} {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GraphDynamicFormalError(
                f"invalid {label} line {line_number} in {path}: {exc}"
            ) from exc
        rows.append(_mapping(value, f"{label} line {line_number}"))
    return rows


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _load_protocol_chain(
    protocol_path: Path, *, stack: tuple[Path, ...] = ()
) -> dict[str, Any]:
    resolved = protocol_path.resolve()
    if resolved in stack:
        raise GraphDynamicFormalError("dynamic protocol extension cycle detected")
    try:
        value = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphDynamicFormalError(
            f"cannot load dynamic protocol {protocol_path}: {exc}"
        ) from exc
    protocol = _mapping(value, "dynamic protocol")
    base_name = protocol.pop("extends_protocol", None)
    if base_name is not None:
        if not isinstance(base_name, str) or Path(base_name).name != base_name:
            raise GraphDynamicFormalError(
                "dynamic protocol extension must be one sibling filename"
            )
        base_path = protocol_path.parent / base_name
        protocol = _deep_merge(
            _load_protocol_chain(base_path, stack=(*stack, resolved)), protocol
        )
    return protocol


def load_protocol(path: str | Path = DEFAULT_PROTOCOL) -> dict[str, Any]:
    protocol = _load_protocol_chain(Path(path))
    return validate_protocol(protocol)


def _private_path(environment_name: str, *, label: str) -> Path:
    if _ENVIRONMENT_NAME.fullmatch(environment_name) is None:
        raise GraphDynamicFormalError(
            f"{label} environment-variable name is invalid"
        )
    raw = os.environ.get(environment_name)
    if not isinstance(raw, str) or not raw.strip():
        raise GraphDynamicFormalError(
            f"{label} environment variable {environment_name} is unset or empty"
        )
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise GraphDynamicFormalError(f"{label} environment value must be absolute")
    return path


def _unique_strings(value: Any, label: str, *, count: int) -> list[str]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise GraphDynamicFormalError(f"{label} must be a string list")
    result = [str(item) for item in value]
    if len(result) != count:
        raise GraphDynamicFormalError(f"{label} must contain exactly {count} values")
    if len(result) != len(set(result)):
        raise GraphDynamicFormalError(f"{label} must contain unique values")
    return result


def _validate_private_dynamic_assignments(
    value: Mapping[str, Any], protocol_value: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    """Validate one evaluator-private 12-window master per public sequence."""

    protocol = validate_protocol(protocol_value)
    assignments = _mapping(value, "private dynamic assignments")
    sequence_count = int(protocol["dataset"]["held_out_bearings"])
    expected_sequences = [
        f"sequence-{index:04d}" for index in range(1, sequence_count + 1)
    ]
    if set(assignments) != set(expected_sequences):
        raise GraphDynamicFormalError(
            "private dynamic assignments do not cover the registered sequences"
        )
    master_horizon = int(protocol["sequence_construction"]["master_horizon"])
    normalized: dict[str, dict[str, Any]] = {}
    seen_samples: set[str] = set()
    for sequence_id in expected_sequences:
        row = _mapping(assignments[sequence_id], f"private assignment {sequence_id}")
        sample_ids = _unique_strings(
            row.get("sample_ids"),
            f"private assignment {sequence_id}.sample_ids",
            count=master_horizon,
        )
        targets = _mapping(
            row.get("private_target"),
            f"private assignment {sequence_id}.private_target",
        )
        if set(targets) != set(sample_ids):
            raise GraphDynamicFormalError(
                f"private targets do not match assigned samples for {sequence_id}"
            )
        normalized_targets: dict[str, int] = {}
        for sample_id in sample_ids:
            target = targets[sample_id]
            if type(target) is not int or target not in {0, 1}:
                raise GraphDynamicFormalError(
                    f"private dynamic target is not binary for {sequence_id}"
                )
            normalized_targets[sample_id] = target
        overlap = seen_samples & set(sample_ids)
        if overlap:
            raise GraphDynamicFormalError(
                "private dynamic samples overlap across registered sequences"
            )
        seen_samples.update(sample_ids)
        normalized[sequence_id] = {
            "sample_ids": sample_ids,
            "private_target": normalized_targets,
        }
    return normalized


def build_private_dynamic_assignments(
    protocol_value: Mapping[str, Any],
    *,
    dataset_protocol_path: str | Path,
    metadata_path: str | Path,
    signal_path: str | Path,
) -> dict[str, dict[str, Any]]:
    """Rebuild the eight evaluator-private masters through the registered DataPort."""

    protocol = validate_protocol(protocol_value)
    authority = _mapping(
        protocol["formal_analysis"].get("evaluator_authority"),
        "formal_analysis.evaluator_authority",
    )
    try:
        dataset = load_dataset_protocol(Path(dataset_protocol_path))
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise GraphDynamicFormalError(
            f"cannot load registered dataset protocol: {type(exc).__name__}"
        ) from exc
    dataset_identity = _mapping(dataset.get("dataset"), "dataset protocol identity")
    sample_handle = _mapping(
        dataset.get("agent_visibility", {}).get("sample_handle"),
        "dataset sample-handle contract",
    )
    monitoring = _mapping(
        dataset.get("tasks", {}).get("monitoring"),
        "dataset monitoring contract",
    )
    split = _mapping(dataset.get("split"), "dataset split contract")
    missing_policy = _mapping(
        monitoring.get("missing_assigned_score_policy"),
        "dataset replay missing-score policy",
    )
    observed_identity = {
        "dataset_protocol_id": dataset.get("protocol_id"),
        "dataset_protocol_schema": dataset.get("schema_version"),
        "dataset_id": dataset_identity.get("dataset_id"),
        "provider_name": dataset_identity.get("provider_name"),
        "evaluator_assignment_contract": dataset_identity.get(
            "evaluator_assignment_contract"
        ),
        "sample_handle_scheme": sample_handle.get("scheme"),
        "sample_handle_seed": sample_handle.get("seed"),
        "split_strategy": split.get("strategy"),
        "monitoring_task_id": monitoring.get("task_id"),
        "missing_score_policy_id": missing_policy.get("policy_id"),
    }
    identity_drift = {
        key: {"observed": observed_identity.get(key), "expected": authority.get(key)}
        for key in observed_identity
        if observed_identity.get(key) != authority.get(key)
    }
    if identity_drift:
        raise GraphDynamicFormalError(
            f"private dataset/DataPort authority drifted: {identity_drift}"
        )
    protocol_dataset = protocol["dataset"]
    if (
        protocol_dataset.get("dataset_id") != observed_identity["dataset_id"]
        or protocol_dataset.get("dataset_protocol_schema")
        != observed_identity["dataset_protocol_schema"]
        or protocol_dataset.get("sample_handle_seed")
        != observed_identity["sample_handle_seed"]
    ):
        raise GraphDynamicFormalError(
            "dynamic protocol and private dataset identity disagree"
        )

    try:
        with LocalPaderbornDataPort(
            metadata_path,
            signal_path,
            public_id_seed=int(observed_identity["sample_handle_seed"]),
        ) as data:
            sequences = build_master_sequences(
                data,
                dataset,
                protocol,
                str(protocol_dataset["rotation"]),
            )
            assignments = {
                sequence_id: {
                    "sample_ids": list(sequence.sample_ids),
                    "private_target": {
                        sample_id: anomaly_target(data.private_record(sample_id))
                        for sample_id in sequence.sample_ids
                    },
                }
                for sequence_id, sequence in sequences.items()
            }
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise GraphDynamicFormalError(
            f"cannot rebuild private dynamic assignments: {type(exc).__name__}"
        ) from exc
    return _validate_private_dynamic_assignments(assignments, protocol)


def _private_assignment_for_unit(
    assignments: Mapping[str, Mapping[str, Any]], unit: Unit
) -> dict[str, Any]:
    try:
        master = assignments[unit.public_sequence_id]
        sample_ids = list(master["sample_ids"][: unit.cell.horizon])
        targets = master["private_target"]
    except (KeyError, TypeError) as exc:
        raise GraphDynamicFormalError(
            f"private dynamic assignment missing for {unit.key}"
        ) from exc
    if len(sample_ids) != unit.cell.horizon:
        raise GraphDynamicFormalError(
            f"private dynamic horizon prefix drifted for {unit.key}"
        )
    return {
        "sample_ids": sample_ids,
        "private_target": {sample_id: int(targets[sample_id]) for sample_id in sample_ids},
    }


def registered_cells(protocol: Mapping[str, Any]) -> tuple[Cell, ...]:
    design = _mapping(protocol.get("experiment_design"), "experiment_design")
    raw = _mapping(
        design.get("cells_per_seed_sequence"),
        "experiment_design.cells_per_seed_sequence",
    )
    cells: list[Cell] = []
    for horizon in (3, 6, 12):
        names = _list(raw.get(f"horizon_{horizon}"), f"horizon_{horizon} cells")
        for value in names:
            if not isinstance(value, str) or not value:
                raise GraphDynamicFormalError("dynamic cell names must be strings")
            if value == "reactive":
                identity = _mapping(
                    protocol["formal_analysis"].get("agent_identity"),
                    "formal_analysis.agent_identity",
                )
                cells.append(
                    Cell(
                        horizon,
                        value,
                        "reactive",
                        None,
                        str(identity["reactive_agent_profile_id"]),
                    )
                )
            elif value.startswith("graph_"):
                profile = value.removeprefix("graph_")
                cells.append(
                    Cell(
                        horizon,
                        value,
                        "graph",
                        profile,
                        str(protocol["graph_profiles"][profile]["agent_profile_id"]),
                    )
                )
            else:
                raise GraphDynamicFormalError(f"unsupported registered cell {value!r}")
    expected = design.get("total_cells_per_seed_sequence")
    if len(cells) != expected or len({cell.key for cell in cells}) != expected:
        raise GraphDynamicFormalError("dynamic matrix is not ten unique cells")
    return tuple(cells)


def expected_units(protocol: Mapping[str, Any]) -> tuple[Unit, ...]:
    design = _mapping(protocol.get("experiment_design"), "experiment_design")
    dataset = _mapping(protocol.get("dataset"), "dataset")
    seeds = _list(design.get("seeds"), "experiment_design.seeds")
    rotations = _list(design.get("rotations"), "experiment_design.rotations")
    sequence_count = dataset.get("held_out_bearings")
    if type(sequence_count) is not int or sequence_count <= 0:
        raise GraphDynamicFormalError("held_out_bearings must be positive")
    sequence_ids = [f"sequence-{index:04d}" for index in range(1, sequence_count + 1)]
    units = tuple(
        Unit(int(seed), str(rotation), sequence_id, cell)
        for seed in seeds
        for rotation in rotations
        for sequence_id in sequence_ids
        for cell in registered_cells(protocol)
    )
    expected = design.get("expected_formal_episode_bundles")
    if len(units) != expected or len({unit.key for unit in units}) != expected:
        raise GraphDynamicFormalError("formal matrix does not contain 240 unique units")
    return units


def validate_protocol(value: Mapping[str, Any]) -> dict[str, Any]:
    protocol = _mapping(value, "protocol")
    if protocol.get("schema_version") != PROTOCOL_SCHEMA:
        raise GraphDynamicFormalError("unsupported dynamic protocol schema")
    if protocol.get("protocol_id") != "paderborn_graph_dynamic_ablation_v3":
        raise GraphDynamicFormalError("dynamic protocol ID drifted")
    dataset = _mapping(protocol.get("dataset"), "dataset")
    if dataset.get("rotation") != "rotation_0" or dataset.get("held_out_bearings") != 8:
        raise GraphDynamicFormalError("formal cohort must freeze eight rotation_0 sequences")
    sequence = _mapping(protocol.get("sequence_construction"), "sequence_construction")
    if sequence.get("horizons") != [3, 6, 12]:
        raise GraphDynamicFormalError("registered horizons drifted")
    if sequence.get("horizon_sequence") != "sequence_h = master_sequence[0:h]":
        raise GraphDynamicFormalError("horizons must remain exact nested prefixes")
    if sequence.get("independently_resample_each_horizon") is not False:
        raise GraphDynamicFormalError("independent horizon resampling is forbidden")
    if sequence.get("expected_change_release_indices_zero_based") != [3, 6, 9]:
        raise GraphDynamicFormalError("condition-change releases drifted")

    design = _mapping(protocol.get("experiment_design"), "experiment_design")
    exact_design = {
        "seeds": list(EXPECTED_SEEDS),
        "rotations": list(EXPECTED_ROTATIONS),
        "cells_per_seed_sequence": EXPECTED_CELL_MATRIX,
        "total_cells_per_seed_sequence": 10,
        "total_sequences_per_cell": 24,
        "expected_formal_episode_bundles": 240,
    }
    design_drift = {
        key: {"observed": design.get(key), "expected": expected}
        for key, expected in exact_design.items()
        if design.get(key) != expected
    }
    if design_drift:
        raise GraphDynamicFormalError(f"registered formal design drifted: {design_drift}")

    runtime = _mapping(
        protocol.get("runtime_and_provider_profile"),
        "runtime_and_provider_profile",
    )
    expected_runtime = {
        "effective_runtime_contract": "phase1_graph_dynamic_generic_ablation_v3",
        "formal_provider_profile_id": "openrouter_north_graph_dynamic_generic_ablation_v3",
        "provider": "openrouter-free",
        "model": "cohere/north-mini-code:free",
        "protocol": "openai_chat_completions",
        "input_usd_per_million": 0.0,
        "output_usd_per_million": 0.0,
        "route_switch_within_profile": "forbidden",
        "model_switch_within_profile": "forbidden",
        "pool_with_active_paderborn_v6_primary": False,
        "pool_across_provider_model_or_runtime_profiles": False,
    }
    drift = {
        key: {"observed": runtime.get(key), "expected": expected}
        for key, expected in expected_runtime.items()
        if runtime.get(key) != expected
    }
    if drift:
        raise GraphDynamicFormalError(f"formal runtime profile drifted: {drift}")

    treatment = _mapping(protocol.get("treatment_construction"), "treatment_construction")
    expected_treatment = {
        "base_agent_class": "phm_agent_benchmark.phase1.GenericLLMToolAgent",
        "reactive_agent_id": "reactive-sequential-agent",
        "graph_agent_id": "graph-decision-agent",
        "legacy_phmskills_superclass_allowed": False,
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "reactive_agent_control_id": "benchmark_generic_llm_tool_agent_v1",
        "graph_agent_control_id": "graph_decision_control_v1",
        "reactive_implementation_id": "reactive_sequential_agent_v1",
        "graph_implementation_id": "graph_decision_agent_v1",
    }
    treatment_drift = {
        key: {"observed": treatment.get(key), "expected": expected}
        for key, expected in expected_treatment.items()
        if treatment.get(key) != expected
    }
    if treatment_drift:
        raise GraphDynamicFormalError(
            f"Generic-base treatment construction drifted: {treatment_drift}"
        )

    failure = _mapping(
        protocol.get("formal_analysis", {}).get("failure_and_attempt_contract"),
        "formal_analysis.failure_and_attempt_contract",
    )
    if failure.get("effective_non_provider_terminal_per_unit") != "exactly_one":
        raise GraphDynamicFormalError("each formal unit needs one non-provider terminal")
    if failure.get("provider_failure_kind") != PROVIDER_FAILURE_KIND:
        raise GraphDynamicFormalError("provider failure kind drifted")
    if failure.get("non_provider_failure_policy") != "retain_in_denominator":
        raise GraphDynamicFormalError("non-provider failures must remain in denominators")

    evaluator_authority = _mapping(
        protocol.get("formal_analysis", {}).get("evaluator_authority"),
        "formal_analysis.evaluator_authority",
    )
    expected_evaluator_authority = {
        "dataset_protocol_id": "paderborn_phase1_v1",
        "dataset_protocol_schema": "phm_agent_dataset_protocol_v1",
        "dataset_id": "paderborn-bearing-datacenter",
        "provider_name": "RM_027_PU",
        "evaluator_assignment_contract": "phase1_registered_data_port_assignment_v1",
        "sample_handle_scheme": "seeded_permutation_v1",
        "sample_handle_seed": 20260808,
        "split_strategy": "bearing_grouped_cyclic_four_fold",
        "monitoring_task_id": TASK_ID,
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "target_source": "registered_private_data_port_assignment",
        "prediction_source": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_ingested": False,
        "private_paths_serialized": False,
    }
    authority_drift = {
        key: {"observed": evaluator_authority.get(key), "expected": expected}
        for key, expected in expected_evaluator_authority.items()
        if evaluator_authority.get(key) != expected
    }
    if authority_drift:
        raise GraphDynamicFormalError(
            f"private evaluator authority drifted: {authority_drift}"
        )

    profiles = _mapping(protocol.get("graph_profiles"), "graph_profiles")
    state_tools = _mapping(protocol.get("state_machine"), "state_machine").get(
        "state_tools"
    )
    state_tools = _mapping(state_tools, "state_machine.state_tools")
    for name in ("full", "no_recovery_revision_edge", "no_observation_conditioned_branching", "no_persistent_graph_state", "no_replanning"):
        profile = _mapping(profiles.get(name), f"graph_profiles.{name}")
        reachable = set(_list(profile.get("reachable_states"), f"{name}.reachable_states"))
        legal = _mapping(profile.get("legal_transitions"), f"{name}.legal_transitions")
        if set(legal) != reachable:
            raise GraphDynamicFormalError(f"{name} transition sources do not equal reachable states")
        for source, targets in legal.items():
            if source not in state_tools or any(target not in reachable for target in targets):
                raise GraphDynamicFormalError(f"{name} contains an invalid transition target")

    statistics_contract = _mapping(protocol.get("statistics"), "statistics")
    if statistics_contract.get("exact_paired_permutation") != (
        "all_256_matched_bearing_cluster_arm_swaps_with_metric_recomputation"
    ):
        raise GraphDynamicFormalError("exact paired permutation contract drifted")
    if statistics_contract.get("interval_method") != (
        "paired_bearing_cluster_bootstrap_with_metric_recomputation"
    ):
        raise GraphDynamicFormalError("paired interval method drifted")
    primary = _mapping(protocol.get("metrics", {}).get("primary"), "metrics.primary")
    if (
        primary.get("name") != "target_adverse_window_average_precision"
        or primary.get("missing_score_policy_id")
        != REPLAY_MISSING_SCORE_POLICY_ID
    ):
        raise GraphDynamicFormalError("task-primary replay metric contract drifted")
    if statistics_contract.get("bootstrap_iterations") != 10000:
        raise GraphDynamicFormalError("bootstrap iteration count drifted")
    consumer = _mapping(
        protocol.get("formal_analysis", {}).get("accepted_manuscript_consumer"),
        "formal_analysis.accepted_manuscript_consumer",
    )
    mechanism = _mapping(
        consumer.get("mechanism_reporting"),
        "accepted_manuscript_consumer.mechanism_reporting",
    )
    ablation_rows = _mapping(
        mechanism.get("ablation_rows"), "mechanism_reporting.ablation_rows"
    )
    expected_controls = {
        "P2-E3": "graph_no_recovery_revision_edge",
        "P2-E4": "graph_no_observation_conditioned_branching",
        "P2-E5": "graph_no_persistent_graph_state",
        "P2-E6": "graph_no_replanning",
    }
    if set(ablation_rows) != set(expected_controls):
        raise GraphDynamicFormalError("mechanism-reporting ablation set drifted")
    for experiment_id, control in expected_controls.items():
        row = _mapping(
            ablation_rows.get(experiment_id),
            f"mechanism_reporting.ablation_rows.{experiment_id}",
        )
        if row.get("control") != control or row.get("metrics") != list(
            MECHANISM_ABLATION_METRICS[experiment_id]
        ):
            raise GraphDynamicFormalError(
                f"{experiment_id} mechanism-reporting contract drifted"
            )
    if ablation_rows["P2-E4"].get(
        "also_serves_p2_e7_no_branching_comparison"
    ) is not True:
        raise GraphDynamicFormalError("P2-E4/P2-E7 reuse contract drifted")
    e7 = _mapping(
        mechanism.get("operating_condition_change_rows"),
        "mechanism_reporting.operating_condition_change_rows",
    )
    expected_e7 = {
        "experiment_id": "P2-E7",
        "control": "reactive",
        "metrics": list(P2_E7_DYNAMIC_METRICS),
        "no_branching_source_reused_from": "P2-E4",
        "duplicate_no_branching_rows": False,
        "forbidden_interpretations": [
            "fault_onset",
            "event_f1",
            "detection_delay",
            "physical_time",
        ],
    }
    if e7 != expected_e7:
        raise GraphDynamicFormalError("P2-E7 mechanism-reporting contract drifted")
    expected_consumer_flags = {
        "displayed_mechanism_arithmetic_recomputed": True,
        "task_primary_and_mechanism_sections_separate": True,
    }
    for key, expected in expected_consumer_flags.items():
        if consumer.get(key) is not expected:
            raise GraphDynamicFormalError(f"accepted consumer flag drifted at {key}")
    expected_consumer_scalars = {
        "render_schema": "p2_dynamic_formal_manuscript_render_v2",
        "task_primary_rows_after_acceptance": 8,
        "secondary_mechanism_rows_after_acceptance": 26,
    }
    for key, expected in expected_consumer_scalars.items():
        if consumer.get(key) != expected:
            raise GraphDynamicFormalError(f"accepted consumer contract drifted at {key}")
    if (
        mechanism.get("role") != "secondary_explanatory_not_task_performance"
        or mechanism.get("horizon") != 12
        or mechanism.get("direction") != "graph_full_minus_control"
    ):
        raise GraphDynamicFormalError("mechanism-reporting role or estimand drifted")
    expected_units(protocol)
    return protocol


def unit_root(output_root: Path, unit: Unit) -> Path:
    return (
        output_root
        / unit.cell.agent_profile_id
        / f"seed_{unit.seed}"
        / unit.rotation
        / f"horizon_{unit.cell.horizon}"
        / "episodes"
        / unit.public_sequence_id
    )


def _json_contains_sample_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in {"sample_id", "source_sample_id"} and isinstance(item, str):
                refs.add(item)
            else:
                refs.update(_json_contains_sample_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(_json_contains_sample_refs(item))
    return refs


def _action_signature(row: Mapping[str, Any]) -> str:
    action = _mapping(row.get("action"), "rollout action")
    return json.dumps(
        {"name": action.get("name"), "arguments": action.get("arguments")},
        sort_keys=True,
        separators=(",", ":"),
    )


def _expected_base_state(
    prior_actions: Sequence[Mapping[str, Any]], released: Sequence[str]
) -> str:
    """Recompute the frozen public-only base router for the current prefix."""

    predicted: set[str] = set()
    for row in prior_actions:
        output = row["result"].get("output")
        if (
            row["action"].get("name") == "model.predict"
            and row["result"].get("status") == "ok"
            and isinstance(output, Mapping)
            and "source_sample_id" in output
        ):
            predicted.add(str(output["source_sample_id"]))
    if released and all(sample_id in predicted for sample_id in released):
        return "Submit"
    current = next(sample_id for sample_id in released if sample_id not in predicted)
    read_index = next(
        (
            index
            for index, row in enumerate(prior_actions)
            if row["action"].get("name") == "data.read_window"
            and row["action"].get("arguments", {}).get("sample_id") == current
            and row["result"].get("status") == "ok"
        ),
        None,
    )
    if read_index is None:
        return "Inspect"
    if not any(
        row["action"].get("name") in {"op.list", "model.list"}
        and row["result"].get("status") == "ok"
        for row in prior_actions
    ):
        return "Hypothesize"
    operator_calls = sum(
        row["action"].get("name") == "op.run"
        and row["result"].get("status") == "ok"
        and isinstance(row["result"].get("output"), Mapping)
        and str(row["result"]["output"].get("source_sample_id")) == current
        for row in prior_actions[read_index + 1 :]
    )
    return "Check" if operator_calls >= 11 else "Analyze"


def _expected_event_id(protocol: Mapping[str, Any], unit: Unit, release_index: int) -> str:
    if release_index not in CHANGE_INDICES:
        raise GraphDynamicFormalError("event ID requested for an unregistered release")
    design = _mapping(protocol.get("experiment_design"), "experiment_design")
    seeds = [int(value) for value in design["seeds"]]
    sequence_count = int(protocol["dataset"]["held_out_bearings"])
    seed_index = seeds.index(unit.seed)
    sequence_index = int(unit.public_sequence_id.removeprefix("sequence-")) - 1
    change_index = CHANGE_INDICES.index(release_index)
    ordinal = (seed_index * sequence_count + sequence_index) * len(CHANGE_INDICES)
    ordinal += change_index + 1
    return f"occ-{ordinal:08d}"


def build_public_event_catalog(protocol_value: Mapping[str, Any]) -> dict[str, Any]:
    """Build the frozen 72-event public catalog without data or provider access."""

    protocol = validate_protocol(protocol_value)
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    rotations = [str(value) for value in protocol["experiment_design"]["rotations"]]
    sequence_ids = [f"sequence-{index:04d}" for index in range(1, 9)]
    catalog_cell = Cell(12, "reactive", "reactive", None, "reactive")
    events: list[dict[str, Any]] = []
    for seed in seeds:
        for rotation in rotations:
            for sequence_id in sequence_ids:
                unit = Unit(seed, rotation, sequence_id, catalog_cell)
                for release_index in CHANGE_INDICES:
                    events.append(
                        {
                            "event": EVENT_NAME,
                            "event_id": _expected_event_id(
                                protocol, unit, release_index
                            ),
                            "seed": seed,
                            "rotation": rotation,
                            "public_sequence_id": sequence_id,
                            "release_index": release_index,
                        }
                    )
    if len(events) != 72 or len({item["event_id"] for item in events}) != 72:
        raise GraphDynamicFormalError("public event catalog is not 72 unique events")
    return {
        "schema_version": "graph_dynamic_public_event_catalog_v3",
        "protocol_id": protocol["protocol_id"],
        "event_count": len(events),
        "provider_calls_performed": False,
        "private_identifiers_included": False,
        "events": events,
    }


def _profile_semantics(
    actions: Sequence[Mapping[str, Any]],
    *,
    unit: Unit,
    protocol: Mapping[str, Any],
    leaf: Path,
) -> dict[str, Any]:
    event_positions: list[int] = []
    monitor_events = 0
    revise_events = 0
    next_success_distances: list[int] = []
    next_prediction_distances: list[int] = []
    states: list[str] = []
    signatures = [_action_signature(row) for row in actions]

    profile: Mapping[str, Any] | None = None
    legal: dict[str, set[str]] = {}
    reachable: set[str] = set()
    state_tools = _mapping(protocol["state_machine"]["state_tools"], "state tools")
    if unit.cell.graph_profile is not None:
        profile = _mapping(
            protocol["graph_profiles"][unit.cell.graph_profile],
            f"graph profile {unit.cell.graph_profile}",
        )
        reachable = set(str(value) for value in profile["reachable_states"])
        legal = {
            str(source): {str(target) for target in targets}
            for source, targets in profile["legal_transitions"].items()
        }

    released_master: tuple[str, ...] = ()
    last_prefix: tuple[str, ...] = ()
    event_payloads: list[dict[str, Any]] = []
    for position, row in enumerate(actions):
        if row.get("index") != position:
            raise GraphDynamicFormalError(f"non-contiguous action indices at {leaf}")
        observation = _mapping(row.get("observation"), f"observation at {leaf}")
        context = _mapping(observation.get("context"), f"observation context at {leaf}")
        released = context.get("replay_sample_ids")
        cursor = context.get("replay_cursor")
        if (
            not isinstance(released, list)
            or not released
            or type(cursor) is not int
            or cursor not in {len(released) - 1, len(released)}
            or (cursor == len(released) and len(released) != unit.cell.horizon)
            or len(released) > unit.cell.horizon
        ):
            raise GraphDynamicFormalError(f"malformed released prefix at {leaf}")
        prefix = tuple(str(value) for value in released)
        if (
            len(set(prefix)) != len(prefix)
            or (last_prefix and prefix[: len(last_prefix)] != last_prefix)
            or (last_prefix and len(prefix) > len(last_prefix) + 1)
            or (not last_prefix and len(prefix) != 1)
        ):
            raise GraphDynamicFormalError(f"non-prefix or duplicate replay release at {leaf}")
        first_observation_after_release = not last_prefix or len(prefix) > len(last_prefix)
        if first_observation_after_release and cursor != len(prefix) - 1:
            raise GraphDynamicFormalError(f"release cursor skipped its first observation at {leaf}")
        if len(prefix) > len(released_master):
            released_master = prefix

        action = _mapping(row.get("action"), f"action at {leaf}")
        result = _mapping(row.get("result"), f"action result at {leaf}")
        visible = set(prefix)
        refs = _json_contains_sample_refs(action.get("arguments", {}))
        refs.update(_json_contains_sample_refs(result.get("output", {})))
        future = sorted(ref for ref in refs if ref.startswith("sample-") and ref not in visible)
        if future:
            raise GraphDynamicFormalError(f"future sample reference at {leaf}: {future[:3]}")

        event = context.get("public_condition_event")
        expected_release = (
            len(prefix) - 1
            if first_observation_after_release and len(prefix) - 1 in CHANGE_INDICES
            else None
        )
        if (event is None) != (expected_release is None):
            raise GraphDynamicFormalError(
                f"condition event was not a one-observation release pulse at {leaf}"
            )
        if event is not None:
            event = _mapping(event, f"public event at {leaf}")
            expected_keys = {"event", "event_id", "release_index"}
            if set(event) != expected_keys:
                raise GraphDynamicFormalError(f"public event shape drifted at {leaf}")
            release_index = event.get("release_index")
            if (
                event.get("event") != EVENT_NAME
                or type(release_index) is not int
                or release_index not in CHANGE_INDICES
                or release_index >= unit.cell.horizon
                or release_index >= len(prefix)
                or release_index != cursor
                or event.get("event_id")
                != _expected_event_id(protocol, unit, release_index)
            ):
                raise GraphDynamicFormalError(f"event identity/release drift at {leaf}")
            if event_payloads and release_index <= event_payloads[-1]["release_index"]:
                raise GraphDynamicFormalError(f"events are duplicated or out of order at {leaf}")
            event_positions.append(position)
            event_payloads.append(event)
        last_prefix = prefix

        state = action.get("decision_state")
        if profile is None:
            if state is not None:
                raise GraphDynamicFormalError(f"Reactive emitted Graph state at {leaf}")
        else:
            if not isinstance(state, str) or state not in reachable:
                raise GraphDynamicFormalError(f"unreachable/missing Graph state at {leaf}")
            action_name = action.get("name")
            if action_name not in state_tools[state]:
                raise GraphDynamicFormalError(
                    f"tool {action_name!r} is illegal in state {state!r} at {leaf}"
                )
            states.append(state)
            observation_branching = bool(profile["toggles"]["observation_conditioned_branching"])
            recovery = bool(profile["toggles"]["recovery_revision_edge"])
            persistent = bool(profile["toggles"]["persistent_graph_state"])
            replanning = bool(profile["toggles"]["replanning"])
            previous_error = (
                position > 0 and actions[position - 1]["result"].get("status") != "ok"
            )
            previous_state = states[-2] if persistent and len(states) >= 2 else None
            if previous_error and recovery:
                expected_state = "Recover"
            elif event is not None and observation_branching:
                expected_state = "Monitor"
            elif previous_state == "Monitor" and recovery and replanning:
                expected_state = "Revise"
            else:
                expected_state = _expected_base_state(actions[:position], prefix)
            if state != expected_state:
                raise GraphDynamicFormalError(
                    f"state precedence drift at {leaf}: action {position} "
                    f"observed {state}, expected {expected_state}"
                )

    if profile is not None:
        for source, target in zip(states, states[1:]):
            if target not in legal[source]:
                raise GraphDynamicFormalError(
                    f"illegal {unit.cell.graph_profile} transition {source}->{target} at {leaf}"
                )
        unreachable_by_profile = {
            "no_recovery_revision_edge": {"Recover", "Revise"},
            "no_observation_conditioned_branching": {"Monitor", "Revise"},
            "no_persistent_graph_state": {"Revise"},
            "no_replanning": {"Revise"},
        }.get(unit.cell.graph_profile, set())
        if set(states) & unreachable_by_profile:
            raise GraphDynamicFormalError(f"ablated state was observed at {leaf}")

    expected_reached_events = [
        index for index in CHANGE_INDICES if index < len(released_master)
    ]
    observed_indices = [int(event["release_index"]) for event in event_payloads]
    if observed_indices != expected_reached_events:
        raise GraphDynamicFormalError(f"event delivery schedule drifted at {leaf}")

    for event_position in event_positions:
        if profile is not None:
            if actions[event_position]["action"].get("decision_state") == "Monitor":
                monitor_events += 1
            for later in range(event_position + 1, len(actions)):
                later_context = actions[later]["observation"]["context"]
                if later_context.get("public_condition_event") is not None:
                    break
                if actions[later]["action"].get("decision_state") == "Revise":
                    revise_events += 1
                    break
        for later in range(event_position, len(actions)):
            if actions[later]["result"].get("status") == "ok":
                next_success_distances.append(later - event_position)
                break
        for later in range(event_position, len(actions)):
            if (
                actions[later]["action"].get("name") == "model.predict"
                and actions[later]["result"].get("status") == "ok"
            ):
                next_prediction_distances.append(later - event_position)
                break

    post_event_repeat_flags: list[int] = []
    for event_position in event_positions:
        end = len(actions)
        for later in event_positions:
            if later > event_position:
                end = later
                break
        post_event_repeat_flags.extend(
            int(signatures[index] == signatures[index - 1])
            for index in range(event_position + 1, end)
        )

    return {
        "released_prefix": list(released_master),
        "event_payloads": event_payloads,
        "operating_condition_event_delivery_count": float(len(event_positions)),
        "event_to_Monitor_transition_rate": (
            None
            if profile is None or not event_positions
            else monitor_events / len(event_positions)
        ),
        "event_to_Revise_transition_rate": (
            None
            if profile is None or not event_positions
            else revise_events / len(event_positions)
        ),
        "steps_from_event_to_next_successful_action": (
            statistics.fmean(next_success_distances) if next_success_distances else None
        ),
        "steps_from_event_to_next_model_prediction": (
            statistics.fmean(next_prediction_distances)
            if next_prediction_distances
            else None
        ),
        "post_event_repeated_action_ratio": (
            statistics.fmean(post_event_repeat_flags)
            if post_event_repeat_flags
            else None
        ),
        "observed_state_count": len(states),
        "valid_state_transition_rate": (
            None if profile is None or len(states) < 2 else 1.0
        ),
        "invalid_action_rate": (
            None
            if not actions
            else sum(
                    row["result"].get("failure_kind") == "invalid_action"
                    for row in actions
                )
                / len(actions)
        ),
        "loop_incidence": float(
            any(left == right for left, right in zip(signatures, signatures[1:]))
        ),
    }


def _validate_exact_six(leaf: Path) -> None:
    try:
        children = list(leaf.iterdir())
    except OSError as exc:
        raise GraphDynamicFormalError(f"cannot inspect canonical leaf {leaf}: {exc}") from exc
    files = {item.name for item in children if item.is_file()}
    directories = [item.name for item in children if item.is_dir()]
    if files != CANONICAL_FILES or directories:
        raise GraphDynamicFormalError(
            f"bundle is not exact-six at {leaf}: files={sorted(files)}, dirs={directories}"
        )


def _validate_terminal_failure_pair(
    terminal_status: Any,
    failure_kind: Any,
    *,
    attempt_contract: Mapping[str, Any],
    leaf: Path,
) -> bool:
    allowed_statuses = set(attempt_contract["canonical_terminal_statuses"])
    allowed_failures = set(attempt_contract["canonical_failure_kinds"])
    if terminal_status not in allowed_statuses:
        raise GraphDynamicFormalError(f"unknown canonical terminal status at {leaf}")
    if failure_kind is not None and failure_kind not in allowed_failures:
        raise GraphDynamicFormalError(f"unknown canonical failure kind at {leaf}")
    provider_failure = failure_kind == PROVIDER_FAILURE_KIND
    required_failure_by_status = {
        "timeout": "timeout",
        "budget_exhausted": "budget_exhausted",
        "invalid_submission": "invalid_submission",
    }
    if terminal_status in required_failure_by_status:
        if failure_kind != required_failure_by_status[terminal_status]:
            raise GraphDynamicFormalError(f"terminal/failure mapping drift at {leaf}")
    elif terminal_status in {"submitted", "stopped", "partial"}:
        if failure_kind is not None:
            raise GraphDynamicFormalError(f"non-failure terminal carries failure kind at {leaf}")
    elif terminal_status == "failed":
        if failure_kind not in {
            "provider_error",
            "agent_decision_error",
            "invalid_action",
            "tool_error",
        }:
            raise GraphDynamicFormalError(f"failed terminal has noncanonical failure kind at {leaf}")
    if provider_failure and terminal_status != "failed":
        raise GraphDynamicFormalError(f"provider failure is not canonical failed status at {leaf}")
    return provider_failure


def _read_attempt(
    leaf: Path,
    *,
    unit: Unit,
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    _validate_exact_six(leaf)
    try:
        bundle = read_run_bundle(leaf)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        raise GraphDynamicFormalError(
            f"benchmark canonical bundle validation failed at {leaf}: {exc}"
        ) from exc
    run = dict(bundle.run)
    rollout = list(bundle.rollout_records)
    submission = dict(bundle.submission)
    metrics = dict(bundle.metrics)
    failures = list(bundle.failures)
    metadata = _mapping(run.get("metadata"), f"run metadata at {leaf}")
    runtime = protocol["runtime_and_provider_profile"]
    provider_attempt = run.get("failure_kind") == PROVIDER_FAILURE_KIND
    expected_metadata = {
        "runtime_contract": runtime["effective_runtime_contract"],
        "runtime": "openai",
        "provider": runtime["provider"],
        "model": runtime["model"],
        "inference_protocol": runtime["protocol"],
        "thinking_mode": "not_requested",
        "seed": unit.seed,
        "rotation": unit.rotation,
        "horizon": unit.cell.horizon,
        "public_sequence_id": unit.public_sequence_id,
        "sample_id": unit.public_sequence_id,
        "task_id": TASK_ID,
        "episode_key": [unit.rotation, unit.public_sequence_id, TASK_ID],
        "arm": unit.cell.arm,
        "graph_policy_profile": (
            "reactive" if unit.cell.graph_profile is None else unit.cell.graph_profile
        ),
        "agent_profile_id": unit.cell.agent_profile_id,
        "evidence_class": (
            "real_data_provider_failure_not_performance_evidence"
            if provider_attempt
            else FORMAL_EVIDENCE_CLASS
        ),
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": (
            "benchmark_generic_llm_tool_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_control_v1"
        ),
        "agent_implementation_id": (
            "reactive_sequential_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_agent_v1"
        ),
    }
    drift = {
        key: {"observed": metadata.get(key), "expected": expected}
        for key, expected in expected_metadata.items()
        if metadata.get(key) != expected
    }
    if drift:
        raise GraphDynamicFormalError(f"episode profile drift at {leaf}: {drift}")
    identity = protocol["formal_analysis"]["agent_identity"]
    expected_agent = (
        identity["reactive_agent_id"]
        if unit.cell.arm == "reactive"
        else identity["graph_agent_id"]
    )
    if run.get("agent_id") != expected_agent:
        raise GraphDynamicFormalError(f"agent identity drift at {leaf}")
    expected_budget = protocol["budgets"]["by_horizon"][unit.cell.horizon]
    if run.get("budget") != expected_budget or run.get("task", {}).get("budget") != expected_budget:
        raise GraphDynamicFormalError(f"horizon budget drift at {leaf}")
    attempt_index = metadata.get("attempt_index")
    expected_attempt_name = f"attempt_{attempt_index:03d}" if type(attempt_index) is int else None
    if type(attempt_index) is not int or attempt_index < 0 or leaf.name != expected_attempt_name:
        raise GraphDynamicFormalError(f"attempt index/path drift at {leaf}")

    actions = [row for row in rollout if row.get("event_type") == "action"]
    terminals = [row for row in rollout if row.get("event_type") == "terminal"]
    if len(terminals) != 1 or rollout[-1] is not terminals[0]:
        raise GraphDynamicFormalError(f"rollout event stream is not canonical at {leaf}")
    if any(
        row.get("run_id") != run.get("run_id")
        or row.get("task_id") != TASK_ID
        or row.get("agent_id") != expected_agent
        or row.get("protocol_version") != run.get("protocol_version")
        for row in rollout
    ):
        raise GraphDynamicFormalError(f"rollout identity fields drift at {leaf}")
    if any(
        row.get("observation", {}).get("sample_id") != unit.public_sequence_id
        or row.get("observation", {}).get("task_id") != TASK_ID
        for row in actions
    ):
        raise GraphDynamicFormalError(f"action observation identity drift at {leaf}")
    terminal_status = run.get("terminal_status")
    failure_kind = run.get("failure_kind")
    if (
        terminals[0].get("terminal_status") != terminal_status
        or terminals[0].get("failure_kind") != failure_kind
        or metrics.get("terminal_status") != terminal_status
        or submission.get("terminal_status") != terminal_status
        or submission.get("failure_kind") != failure_kind
    ):
        raise GraphDynamicFormalError(f"terminal/failure fields disagree at {leaf}")
    attempt_contract = protocol["formal_analysis"]["failure_and_attempt_contract"]
    provider_failure = _validate_terminal_failure_pair(
        terminal_status,
        failure_kind,
        attempt_contract=attempt_contract,
        leaf=leaf,
    )

    rollout_metrics = _mapping(metrics.get("rollout_metrics"), f"rollout metrics at {leaf}")
    task_metrics = _mapping(metrics.get("task_metrics"), f"task metrics at {leaf}")
    if not provider_failure:
        grounded = rollout_metrics.get("grounded_completion")
        if isinstance(grounded, bool) or grounded not in (0, 0.0, 1, 1.0):
            raise GraphDynamicFormalError(
                f"non-provider terminal lacks binary grounded completion at {leaf}"
            )
    observed_cost = rollout_metrics.get("estimated_model_cost_usd")
    if observed_cost is not None and not math.isclose(
        _finite(observed_cost, f"estimated model cost at {leaf}"),
        0.0,
        rel_tol=0.0,
        abs_tol=1e-12,
    ):
        raise GraphDynamicFormalError(f"free-profile canonical cost is nonzero at {leaf}")
    usage = _mapping(run.get("usage", {}), f"usage at {leaf}")
    for name in (
        "input_tokens",
        "output_tokens",
        "llm_turns",
        "model_calls",
        "operator_calls",
        "tool_calls",
        "window_reads",
        "data_points_read",
        "data_bytes_read",
        "wall_clock_seconds",
    ):
        if name in rollout_metrics and name in usage:
            if not math.isclose(
                _finite(rollout_metrics[name], f"rollout {name} at {leaf}"),
                _finite(usage[name], f"usage {name} at {leaf}"),
                rel_tol=0.0,
                abs_tol=1e-12,
            ):
                raise GraphDynamicFormalError(
                    f"canonical metric and run usage disagree for {name} at {leaf}"
                )
    diagnostics = _profile_semantics(actions, unit=unit, protocol=protocol, leaf=leaf)
    diagnostics["post_event_budget_exhaustion_rate"] = (
        None
        if diagnostics["operating_condition_event_delivery_count"] == 0.0
        else float(terminal_status == "budget_exhausted")
    )
    return {
        "leaf": str(leaf),
        "unit_key": unit.key,
        "seed": unit.seed,
        "rotation": unit.rotation,
        "public_sequence_id": unit.public_sequence_id,
        "horizon": unit.cell.horizon,
        "cell": unit.cell.name,
        "arm": unit.cell.arm,
        "agent_profile_id": unit.cell.agent_profile_id,
        "graph_profile": unit.cell.graph_profile,
        "attempt_index": attempt_index,
        "terminal_status": str(terminal_status),
        "failure_kind": failure_kind,
        "provider_failure": provider_failure,
        "task_metrics": task_metrics,
        "rollout_metrics": rollout_metrics,
        "usage": usage,
        "submission_payload": submission.get("payload"),
        "submission_document": submission,
        "metrics_document": metrics,
        "rollout_records": rollout,
        "actions": actions,
        "failures": failures,
        "diagnostics": diagnostics,
    }


def _validate_manifest(
    path: Path,
    *,
    unit: Unit,
    protocol: Mapping[str, Any],
    attempt_count: int,
) -> None:
    manifest = _read_json(path, "dynamic run manifest")
    runtime = protocol["runtime_and_provider_profile"]
    expected = {
        "study": "graph_dynamic_ablation_v3",
        "dynamic_protocol": protocol["schema_version"],
        "dataset_protocol": protocol["dataset"]["dataset_protocol_schema"],
        "runtime_contract": runtime["effective_runtime_contract"],
        "runtime": "openai",
        "provider_profile_id": runtime["formal_provider_profile_id"],
        "provider": runtime["provider"],
        "model": runtime["model"],
        "inference_protocol": runtime["protocol"],
        "thinking_mode": "not_requested",
        "temperature": protocol["shared_agent_contract"]["shared"]["temperature"],
        "max_output_tokens_per_turn": protocol["shared_agent_contract"]["shared"]["max_output_tokens_per_turn"],
        "input_usd_per_million": runtime["input_usd_per_million"],
        "output_usd_per_million": runtime["output_usd_per_million"],
        "arm": unit.cell.arm,
        "graph_policy_profile": (
            "reactive" if unit.cell.graph_profile is None else unit.cell.graph_profile
        ),
        "agent_profile_id": unit.cell.agent_profile_id,
        "seed": unit.seed,
        "rotation": unit.rotation,
        "public_sequence_id": unit.public_sequence_id,
        "horizon": unit.cell.horizon,
        "budget": protocol["budgets"]["by_horizon"][unit.cell.horizon],
        "canonical_episode_count": attempt_count,
        "evidence_class": FORMAL_EVIDENCE_CLASS,
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": (
            "benchmark_generic_llm_tool_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_control_v1"
        ),
        "agent_implementation_id": (
            "reactive_sequential_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_agent_v1"
        ),
    }
    drift = {
        key: {"observed": manifest.get(key), "expected": expected_value}
        for key, expected_value in expected.items()
        if manifest.get(key) != expected_value
    }
    if drift:
        raise GraphDynamicFormalError(f"formal manifest drift at {path}: {drift}")


def _average_precision(targets: Sequence[int], scores: Sequence[float]) -> float | None:
    positives = sum(targets)
    if positives == 0:
        return None
    order = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    true_positives = 0
    contribution = 0.0
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and scores[order[end]] == scores[order[start]]:
            end += 1
        group_positives = sum(targets[order[index]] for index in range(start, end))
        true_positives += group_positives
        contribution += (true_positives / end) * group_positives
        start = end
    return contribution / positives


def _auroc(targets: Sequence[int], scores: Sequence[float]) -> float | None:
    positives = [scores[index] for index, target in enumerate(targets) if target == 1]
    negatives = [scores[index] for index, target in enumerate(targets) if target == 0]
    if not positives or not negatives:
        return None
    wins = sum(
        1.0 if positive > negative else 0.5 if positive == negative else 0.0
        for positive in positives
        for negative in negatives
    )
    return wins / (len(positives) * len(negatives))


def _assert_metric_fields(
    observed: Mapping[str, Any], expected: Mapping[str, float | None], *, path: Path
) -> None:
    for key, expected_value in expected.items():
        if key not in observed:
            raise GraphDynamicFormalError(f"recomputed metric {key} is missing at {path}")
        observed_value = observed[key]
        if expected_value is None:
            if observed_value is not None:
                raise GraphDynamicFormalError(f"recomputed metric {key} disagrees at {path}")
            continue
        if not math.isclose(
            _finite(observed_value, f"observed {key} at {path}"),
            expected_value,
            rel_tol=0.0,
            abs_tol=1e-12,
        ):
            raise GraphDynamicFormalError(f"recomputed metric {key} disagrees at {path}")


def _payload_decisions(value: Any, *, label: str) -> list[dict[str, Any]]:
    payload = _mapping(value, label)
    decisions_value = payload.get("decisions")
    alarms_value = payload.get("alarms")
    if decisions_value is not None and alarms_value is not None:
        if decisions_value != alarms_value:
            raise GraphDynamicFormalError(
                f"{label} has conflicting decisions and alarms"
            )
        raw = decisions_value
    else:
        raw = decisions_value if decisions_value is not None else alarms_value
    if not isinstance(raw, list) or any(not isinstance(item, Mapping) for item in raw):
        raise GraphDynamicFormalError(f"{label} lacks a decision list")
    return [dict(item) for item in raw]


def _canonical_replay_decisions(
    record: Mapping[str, Any], assigned_sample_ids: Sequence[str]
) -> list[dict[str, Any]]:
    """Project the last immutable successful submit prefix from rollout truth."""

    prefix: list[dict[str, Any]] = []
    rows = _list(record.get("rollout_records"), "canonical rollout records")
    if not rows or not isinstance(rows[-1], Mapping) or rows[-1].get("event_type") != "terminal":
        raise GraphDynamicFormalError(
            f"canonical rollout lacks its terminal event: {record['leaf']}"
        )
    terminal = rows[-1]
    if terminal.get("terminal_status") != record["terminal_status"]:
        raise GraphDynamicFormalError(
            f"canonical rollout terminal status drift: {record['leaf']}"
        )
    assigned = list(assigned_sample_ids)
    for row in rows[:-1]:
        if not isinstance(row, Mapping):
            raise GraphDynamicFormalError(
                f"canonical rollout row is not a mapping: {record['leaf']}"
            )
        action = row.get("action")
        result = row.get("result")
        if (
            not isinstance(action, Mapping)
            or action.get("name") != "submit"
            or not isinstance(result, Mapping)
            or result.get("status") != "ok"
        ):
            continue
        observed = _payload_decisions(
            result.get("output"),
            label=f"successful submit output at {record['leaf']}",
        )
        observed_ids = [str(item.get("sample_id")) for item in observed]
        if observed_ids != assigned[: len(observed_ids)]:
            raise GraphDynamicFormalError(
                f"canonical successful submission is not an assigned prefix: {record['leaf']}"
            )
        if len(observed) <= len(prefix) or observed[: len(prefix)] != prefix:
            raise GraphDynamicFormalError(
                f"canonical successful submissions rewrite their prefix: {record['leaf']}"
            )
        prefix = observed

    submission = _mapping(
        record.get("submission_document"),
        f"canonical submission at {record['leaf']}",
    )
    if submission.get("terminal_status") != record["terminal_status"]:
        raise GraphDynamicFormalError(
            f"canonical submission status drift: {record['leaf']}"
        )
    payload = submission.get("payload")
    if record["terminal_status"] == "submitted":
        final = _payload_decisions(
            payload, label=f"canonical terminal submission at {record['leaf']}"
        )
        if final != prefix or len(prefix) != len(assigned):
            raise GraphDynamicFormalError(
                f"terminal submission differs from rollout submit truth: {record['leaf']}"
            )
        last_action = rows[-2] if len(rows) >= 2 else None
        if (
            not isinstance(last_action, Mapping)
            or not isinstance(last_action.get("action"), Mapping)
            or last_action["action"].get("name") != "submit"
            or not isinstance(last_action.get("result"), Mapping)
            or last_action["result"].get("status") != "ok"
        ):
            raise GraphDynamicFormalError(
                f"submitted terminal lacks a final canonical submit: {record['leaf']}"
            )
    elif payload is not None:
        raise GraphDynamicFormalError(
            f"failed terminal unexpectedly has a submission payload: {record['leaf']}"
        )
    return prefix


def _recompute_evaluator_metrics(
    *,
    record: Mapping[str, Any],
    master: Sequence[str],
    target: Mapping[str, Any],
    evaluation: Mapping[str, Any],
    path: Path,
) -> None:
    """Independently derive every registered evaluator metric from event truth."""

    if (
        evaluation.get("evaluator_id") != "phase1"
        or evaluation.get("evaluator_method") != "deterministic"
        or evaluation.get("task_id") != TASK_ID
        or evaluation.get("terminal_status") != record["terminal_status"]
    ):
        raise GraphDynamicFormalError(f"evaluator identity/status drift at {path}")
    actions = list(record["actions"])
    failures = list(record["failures"])
    payload = record["submission_payload"]
    submitted = record["terminal_status"] == "submitted"
    grounded = 0.0
    expected_task: dict[str, float | None] = {
        "submission": float(submitted),
        "grounded_submission": 0.0,
    }
    if submitted:
        payload_map = _mapping(payload, f"submitted payload at {path}")
        alarm_rows = _canonical_replay_decisions(record, master)
        alarm_ids = [str(item.get("sample_id")) for item in alarm_rows]
        if alarm_ids != list(master):
            raise GraphDynamicFormalError(f"submitted alarm coverage/order drift at {path}")
        successful_predictions: dict[str, str] = {}
        for action_row in actions:
            output = action_row["result"].get("output")
            if (
                action_row["action"].get("name") == "model.predict"
                and action_row["result"].get("status") == "ok"
                and isinstance(output, Mapping)
                and output.get("source_sample_id") in master
                and isinstance(output.get("prediction_ref"), str)
            ):
                successful_predictions[str(output["source_sample_id"])] = str(
                    output["prediction_ref"]
                )
        provenance_valid = all(
            sample_id in successful_predictions
            and successful_predictions[sample_id] in item.get("supporting_refs", [])
            for sample_id, item in zip(master, alarm_rows, strict=True)
        )
        grounding_fields = (
            payload_map.get("submission_grounding"),
            payload_map.get("artifact_lineage_completeness"),
            payload_map.get("supporting_reference_validity"),
        )
        grounded = float(provenance_valid and grounding_fields == (1.0, 1.0, 1.0))
        targets = [int(target[sample_id]) for sample_id in master]
        if any(value not in {0, 1} for value in targets):
            raise GraphDynamicFormalError(f"private target is not binary at {path}")
        scores = [_finite(item.get("score"), f"alarm score at {path}") for item in alarm_rows]
        predictions = [str(item.get("predicted_class")) for item in alarm_rows]
        if any(value not in {"normal", "anomaly"} for value in predictions):
            raise GraphDynamicFormalError(f"alarm class drift at {path}")
        healthy = [index for index, value in enumerate(targets) if value == 0]
        anomalous = [index for index, value in enumerate(targets) if value == 1]
        expected_task.update(
            {
                "grounded_submission": grounded,
                "average_precision": _average_precision(targets, scores),
                "auroc": _auroc(targets, scores),
                "false_alarm_rate": (
                    sum(predictions[index] == "anomaly" for index in healthy) / len(healthy)
                    if healthy
                    else None
                ),
                "true_positive_rate": (
                    sum(predictions[index] == "anomaly" for index in anomalous)
                    / len(anomalous)
                    if anomalous
                    else None
                ),
            }
        )
    task_metrics = _mapping(evaluation.get("task_metrics"), f"task metrics at {path}")
    _assert_metric_fields(task_metrics, expected_task, path=path)

    valid = sum(row["result"].get("status") == "ok" for row in actions)
    signatures = [_action_signature(row) for row in actions]
    repeated = len(signatures) - len(set(signatures))
    failed_positions = [
        int(row["index"])
        for row in actions
        if row["result"].get("status") != "ok"
    ]
    first_failure = next(
        (
            int(item["step"])
            for item in failures
            if type(item.get("step")) is int
        ),
        failed_positions[0] if failed_positions else None,
    )
    next_success: float | None = None
    if first_failure is not None:
        corrected = next(
            (
                int(row["index"])
                for row in actions
                if int(row["index"]) > first_failure
                and row["result"].get("status") == "ok"
                and row["action"].get("name") != "submit"
            ),
            None,
        )
        if corrected is not None:
            next_success = float(corrected - first_failure)
    grounded_recovery = float(
        bool(failures) and next_success is not None and grounded == 1.0
    )
    usage = record["usage"]
    rollout_expected: dict[str, float | None] = {
        "grounded_completion": grounded,
        "valid_tool_call_rate": valid / len(actions) if actions else 0.0,
        "grounded_recovery_success": grounded_recovery,
        "steps_to_next_success_after_failure": next_success,
        "repeated_action_ratio": repeated / len(actions) if actions else 0.0,
        "budget_exhaustion": float(record["terminal_status"] == "budget_exhausted"),
        "steps": float(len(actions)),
        "llm_turns": float(usage.get("llm_turns", 0)),
        "input_tokens": float(usage.get("input_tokens", 0)),
        "output_tokens": float(usage.get("output_tokens", 0)),
        "wall_clock_seconds": _finite(
            usage.get("wall_clock_seconds", 0.0), f"usage wall clock at {path}"
        ),
        "estimated_model_cost_usd": 0.0,
    }
    rollout_metrics = _mapping(
        evaluation.get("rollout_metrics"), f"rollout metrics at {path}"
    )
    _assert_metric_fields(rollout_metrics, rollout_expected, path=path)


def _validate_private_evaluation(
    path: Path,
    *,
    record: Mapping[str, Any],
    unit: Unit,
) -> tuple[str, ...]:
    """Validate runner-derived resume diagnostics, never formal target authority."""
    rows = _read_jsonl(path, "private evaluation")
    if len(rows) != 1:
        raise GraphDynamicFormalError(f"{path} must contain one effective evaluation row")
    row = rows[0]
    if (
        row.get("rotation") != unit.rotation
        or row.get("sample_id") != unit.public_sequence_id
        or row.get("task_id") != TASK_ID
    ):
        raise GraphDynamicFormalError(f"private evaluation identity drift at {path}")
    sample_ids = row.get("sample_ids")
    if (
        not isinstance(sample_ids, list)
        or len(sample_ids) != unit.cell.horizon
        or len(set(str(value) for value in sample_ids)) != unit.cell.horizon
    ):
        raise GraphDynamicFormalError(f"private master-prefix length drift at {path}")
    master = tuple(str(value) for value in sample_ids)
    if tuple(record["diagnostics"]["released_prefix"]) != master[: len(record["diagnostics"]["released_prefix"])]:
        raise GraphDynamicFormalError(f"released prefix disagrees with evaluator sequence at {path}")
    target = row.get("private_target")
    if not isinstance(target, Mapping) or set(str(key) for key in target) != set(master):
        raise GraphDynamicFormalError(f"private target coverage drift at {path}")
    normalized_target = {str(key): value for key, value in target.items()}
    if row.get("submission") != record["submission_payload"]:
        raise GraphDynamicFormalError(f"private/public submission disagreement at {path}")
    evaluation = _mapping(row.get("evaluation"), f"private evaluation payload at {path}")
    public_evaluation = {
        "evaluator_id": evaluation.get("evaluator_id"),
        "evaluator_method": evaluation.get("evaluator_method"),
        "task_id": evaluation.get("task_id"),
        "task_metrics": evaluation.get("task_metrics"),
        "rollout_metrics": evaluation.get("rollout_metrics"),
        "terminal_status": evaluation.get("terminal_status"),
    }
    metrics_path = Path(str(record["leaf"])) / "metrics.json"
    if public_evaluation != _read_json(metrics_path, "public canonical metrics"):
        raise GraphDynamicFormalError(f"canonical metrics were not evaluator-recomputed at {path}")
    _recompute_evaluator_metrics(
        record=record,
        master=master,
        target=normalized_target,
        evaluation=evaluation,
        path=path,
    )
    return master


def _validate_attempt_prefixes(
    attempts: Sequence[Mapping[str, Any]], master: Sequence[str], *, directory: Path
) -> None:
    for attempt in attempts:
        released = tuple(attempt["diagnostics"]["released_prefix"])
        if released != tuple(master[: len(released)]):
            raise GraphDynamicFormalError(
                f"attempt prefix changed within registered unit at {directory}"
            )


def _analysis_replay_record(
    record: Mapping[str, Any], assignment: Mapping[str, Any]
) -> dict[str, Any]:
    sample_ids = list(assignment["sample_ids"])
    return {
        "task_id": TASK_ID,
        "bearing_id": record["public_sequence_id"],
        "sample_ids": sample_ids,
        "private_target": dict(assignment["private_target"]),
        "replay_decisions": _canonical_replay_decisions(record, sample_ids),
        "submission": record["submission_payload"],
        "evaluation": {
            "task_metrics": dict(record["task_metrics"]),
            "rollout_metrics": dict(record["rollout_metrics"]),
        },
    }


def collect_formal_records(
    output_root: str | Path,
    protocol_value: Mapping[str, Any],
    *,
    private_dynamic_assignments: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Select one non-provider terminal for each of the 240 registered units."""

    protocol = validate_protocol(protocol_value)
    assignments = _validate_private_dynamic_assignments(
        private_dynamic_assignments, protocol
    )
    root = Path(output_root).resolve()
    records: list[dict[str, Any]] = []
    accepted_leaves: set[Path] = set()
    provider_attempt_count = 0
    terminal_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    cell_counts: Counter[str] = Counter()
    non_provider_failure_count = 0
    master_by_sequence: dict[str, dict[int, tuple[str, ...]]] = defaultdict(dict)

    for unit in expected_units(protocol):
        directory = unit_root(root, unit)
        if not directory.is_dir():
            raise GraphDynamicFormalError(f"missing registered formal unit: {directory}")
        attempt_dirs = sorted(
            path for path in directory.iterdir() if path.is_dir() and path.name.startswith("attempt_")
        )
        if not attempt_dirs:
            raise GraphDynamicFormalError(f"formal unit has no canonical attempts: {directory}")
        attempts = [
            _read_attempt(path, unit=unit, protocol=protocol) for path in attempt_dirs
        ]
        indexes = [int(item["attempt_index"]) for item in attempts]
        if indexes != list(range(len(indexes))):
            raise GraphDynamicFormalError(f"attempt history is not contiguous at {directory}")
        selected = [item for item in attempts if not item["provider_failure"]]
        if len(selected) != 1:
            raise GraphDynamicFormalError(
                f"{unit.key} has {len(selected)} non-provider terminals; expected exactly one"
            )
        record = selected[0]
        if record["attempt_index"] != attempts[-1]["attempt_index"]:
            raise GraphDynamicFormalError(f"attempt exists after effective terminal at {directory}")
        if any(not item["provider_failure"] for item in attempts[:-1]):
            raise GraphDynamicFormalError(f"multiple non-provider terminals at {directory}")
        _validate_manifest(
            directory / "run_manifest.json",
            unit=unit,
            protocol=protocol,
            attempt_count=len(attempts),
        )
        assignment = _private_assignment_for_unit(assignments, unit)
        master = tuple(assignment["sample_ids"])
        released = tuple(record["diagnostics"]["released_prefix"])
        if released != master[: len(released)]:
            raise GraphDynamicFormalError(
                f"released prefix disagrees with private DataPort assignment at {directory}"
            )
        _recompute_evaluator_metrics(
            record=record,
            master=master,
            target=assignment["private_target"],
            evaluation=record["metrics_document"],
            path=Path(str(record["leaf"])),
        )
        # Keep evaluator-only targets in memory solely for canonical metric
        # recomputation. They are never copied into acceptance or result JSON,
        # and runner-derived evaluation.jsonl is not read here.
        record = dict(record)
        record["_analysis_replay_record"] = _analysis_replay_record(
            record, assignment
        )
        _validate_attempt_prefixes(attempts, master, directory=directory)
        previous = master_by_sequence[unit.public_sequence_id].get(unit.cell.horizon)
        if previous is not None and previous != master:
            raise GraphDynamicFormalError(
                f"sequence changed across seed/cell at {unit.public_sequence_id}/h{unit.cell.horizon}"
            )
        master_by_sequence[unit.public_sequence_id][unit.cell.horizon] = master

        provider_attempt_count += sum(item["provider_failure"] for item in attempts)
        accepted_leaves.update(Path(str(item["leaf"])).resolve() for item in attempts)
        records.append(record)
        terminal_counts[record["terminal_status"]] += 1
        cell_counts[unit.cell.key] += 1
        if record["failure_kind"] is not None:
            failure_counts[str(record["failure_kind"])] += 1
        if record["terminal_status"] != "submitted":
            non_provider_failure_count += 1

    for sequence_id, horizons in master_by_sequence.items():
        if set(horizons) != {3, 6, 12}:
            raise GraphDynamicFormalError(f"nested horizon coverage missing for {sequence_id}")
        if horizons[12][:6] != horizons[6] or horizons[6][:3] != horizons[3]:
            raise GraphDynamicFormalError(f"horizons are not exact prefixes for {sequence_id}")

    observed_run_leaves = {
        path.parent.resolve() for path in root.rglob("run.json")
    } if root.exists() else set()
    unexpected = sorted(str(path) for path in observed_run_leaves - accepted_leaves)
    if unexpected:
        raise GraphDynamicFormalError(f"unregistered/cross-profile bundles: {unexpected[:5]}")

    expected_count = int(protocol["experiment_design"]["expected_formal_episode_bundles"])
    if len(records) != expected_count:
        raise GraphDynamicFormalError(
            f"selected {len(records)} terminals; expected {expected_count}"
        )
    if set(cell_counts.values()) != {24} or len(cell_counts) != 10:
        raise GraphDynamicFormalError(f"cell denominators drifted: {dict(cell_counts)}")
    pair_keys: dict[tuple[int, str, str, int], set[str]] = defaultdict(set)
    for record in records:
        pair_keys[(
            int(record["seed"]),
            str(record["rotation"]),
            str(record["public_sequence_id"]),
            int(record["horizon"]),
        )].add(str(record["cell"]))
    if len(pair_keys) != 72:
        raise GraphDynamicFormalError("P2-E2 paired horizon units are incomplete")
    for key, cells in pair_keys.items():
        if not {"reactive", "graph_full"}.issubset(cells):
            raise GraphDynamicFormalError(f"P2-E2 matched pair missing at {key}")

    inclusion = {
        "scheduled_unit_denominator": expected_count,
        "effective_non_provider_terminal_count": len(records),
        "retained_provider_failure_attempt_count": provider_attempt_count,
        "retained_non_provider_failure_count": non_provider_failure_count,
        "terminal_status_counts": dict(sorted(terminal_counts.items())),
        "failure_kind_counts": dict(sorted(failure_counts.items())),
        "cell_denominators": dict(sorted(cell_counts.items())),
        "p2e2_matched_pair_count": len(pair_keys),
        "public_sequence_cluster_count": 8,
        "failures_retained_in_denominator": True,
        "cross_horizon_pooling_performed": False,
        "cross_profile_pooling_performed": False,
        "private_assignment_sequence_count": len(assignments),
        "private_target_authority": "registered_private_data_port_assignment",
        "prediction_authority": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_ingested": False,
    }
    return records, inclusion


def accept_formal_cohort(
    output_root: str | Path,
    protocol_value: Mapping[str, Any],
    *,
    private_dynamic_assignments: Mapping[str, Any],
) -> dict[str, Any]:
    """Return an acceptance report; incomplete or drifted cohorts return false."""

    protocol = validate_protocol(protocol_value)
    root = Path(output_root).resolve()
    try:
        _records, inclusion = collect_formal_records(
            root,
            protocol,
            private_dynamic_assignments=private_dynamic_assignments,
        )
    except (GraphDynamicFormalError, KeyError, TypeError, IndexError) as exc:
        return {
            "schema_version": ACCEPTANCE_SCHEMA,
            "accepted": False,
            "protocol_id": protocol["protocol_id"],
            "provider_profile_id": protocol["runtime_and_provider_profile"]["formal_provider_profile_id"],
            "output_root": str(root),
            "provider_calls_performed_by_gate": False,
            "errors": [str(exc)],
        }
    return {
        "schema_version": ACCEPTANCE_SCHEMA,
        "accepted": True,
        "protocol_id": protocol["protocol_id"],
        "provider_profile_id": protocol["runtime_and_provider_profile"]["formal_provider_profile_id"],
        "output_root": str(root),
        "expected_episode_bundles": 240,
        "observed_effective_non_provider_terminals": 240,
        "provider_calls_performed_by_gate": False,
        "grouping_contract": {
            "absolute_cell_key": ["horizon", "agent_profile_id"],
            "paired_unit": protocol["statistics"]["paired_unit"],
            "pool_episode_rows_across_horizons": False,
            "pool_across_provider_model_or_runtime_profiles": False,
        },
        "evaluator_authority": {
            "target_source": "registered_private_data_port_assignment",
            "prediction_source": "canonical_rollout_successful_submit_prefix",
            "derived_evaluation_jsonl_ingested": False,
            "private_paths_serialized": False,
        },
        "canonical_inclusion": inclusion,
        "errors": [],
    }


def validate_acceptance(
    output_root: str | Path,
    protocol: Mapping[str, Any],
    acceptance_value: Mapping[str, Any],
) -> dict[str, Any]:
    report = _mapping(acceptance_value, "formal acceptance")
    expected = {
        "schema_version": ACCEPTANCE_SCHEMA,
        "accepted": True,
        "protocol_id": protocol["protocol_id"],
        "provider_profile_id": protocol["runtime_and_provider_profile"]["formal_provider_profile_id"],
        "output_root": str(Path(output_root).resolve()),
        "expected_episode_bundles": 240,
        "observed_effective_non_provider_terminals": 240,
        "provider_calls_performed_by_gate": False,
        "errors": [],
    }
    drift = {
        key: {"observed": report.get(key), "expected": value}
        for key, value in expected.items()
        if report.get(key) != value
    }
    if drift:
        raise GraphDynamicFormalError(f"formal acceptance report drifted: {drift}")
    grouping = _mapping(report.get("grouping_contract"), "acceptance grouping contract")
    if (
        grouping.get("absolute_cell_key") != ["horizon", "agent_profile_id"]
        or grouping.get("pool_episode_rows_across_horizons") is not False
        or grouping.get("pool_across_provider_model_or_runtime_profiles") is not False
    ):
        raise GraphDynamicFormalError("acceptance grouping contract permits pooling")
    evaluator_authority = _mapping(
        report.get("evaluator_authority"), "acceptance evaluator authority"
    )
    if evaluator_authority != {
        "target_source": "registered_private_data_port_assignment",
        "prediction_source": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_ingested": False,
        "private_paths_serialized": False,
    }:
        raise GraphDynamicFormalError("acceptance evaluator authority drifted")
    return report


def _metric_value(record: Mapping[str, Any], metric: str) -> float | None:
    if metric in TASK_COHORT_METRICS:
        raise GraphDynamicFormalError(
            f"{metric} is a cohort-level assigned-window metric and cannot be "
            "computed from one bearing episode"
        )
    task = record["task_metrics"]
    rollout = record["rollout_metrics"]
    diagnostics = record["diagnostics"]
    grounded = _finite(rollout.get("grounded_completion"), "grounded completion")
    if metric == "grounded_completion_rate":
        return grounded
    if metric == "window_average_precision_over_grounded_submissions":
        value = task.get("average_precision") if grounded == 1.0 else None
    elif metric == "completion_adjusted_window_average_precision":
        value = 0.0 if grounded == 0.0 else task.get("average_precision")
    elif metric == "window_auroc_over_grounded_submissions":
        value = task.get("auroc") if grounded == 1.0 else None
    elif metric in {"false_alarm_rate", "true_positive_rate"}:
        value = task.get(metric)
    elif metric == "wall_clock_latency":
        value = rollout.get("wall_clock_seconds", record["usage"].get("wall_clock_seconds"))
    elif metric in diagnostics:
        value = diagnostics.get(metric)
    else:
        value = rollout.get(metric, record["usage"].get(metric))
    if value is None:
        return None
    return _finite(value, f"{metric} at {record['leaf']}")


def _replay_task_summary(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, float | int | None]:
    if not records:
        raise GraphDynamicFormalError("cannot summarize an empty replay cohort")
    analysis_records = [
        _mapping(record.get("_analysis_replay_record"), "private replay analysis row")
        for record in records
    ]
    expected_windows = sum(len(_list(row.get("sample_ids"), "assigned sample ids")) for row in analysis_records)
    try:
        summary = aggregate_results(
            analysis_records,
            replay_missing_score_policy_id=REPLAY_MISSING_SCORE_POLICY_ID,
        )[TASK_ID]
    except (KeyError, TypeError, ValueError) as exc:
        raise GraphDynamicFormalError(
            f"canonical target-adverse replay aggregation failed: {exc}"
        ) from exc
    contract = _mapping(summary.get("evaluation_contract"), "replay evaluation contract")
    if contract.get("missing_assigned_score_policy_id") != REPLAY_MISSING_SCORE_POLICY_ID:
        raise GraphDynamicFormalError("canonical replay missing-score policy drifted")
    task = _mapping(summary.get("task"), "canonical replay task summary")
    if task.get("assigned_windows") != expected_windows:
        raise GraphDynamicFormalError("canonical assigned-window denominator drifted")
    submitted = task.get("submitted_windows")
    missing = task.get("missing_assigned_scores")
    if (
        type(submitted) is not int
        or type(missing) is not int
        or submitted + missing != expected_windows
    ):
        raise GraphDynamicFormalError("canonical replay window coverage drifted")
    return task


def _task_metric_value(
    records: Sequence[Mapping[str, Any]], metric: str
) -> float | None:
    try:
        canonical_name = TASK_COHORT_METRICS[metric]
    except KeyError as exc:
        raise GraphDynamicFormalError(f"unknown task cohort metric: {metric}") from exc
    value = _replay_task_summary(records).get(canonical_name)
    return None if value is None else _finite(value, metric)


def _task_cell_report(
    records: Sequence[Mapping[str, Any]], metric: str
) -> dict[str, Any]:
    by_seed: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for record in records:
        by_seed[int(record["seed"])].append(record)
    seed_values = {
        str(seed): _task_metric_value(seed_records, metric)
        for seed, seed_records in sorted(by_seed.items())
    }
    defined = [value for value in seed_values.values() if value is not None]
    all_windows = _replay_task_summary(records)
    return {
        "estimate": statistics.fmean(defined) if defined else None,
        "aggregation": "mean_of_seed_level_metrics_each_recomputed_over_all_eight_bearing_sequences",
        "seed_estimates": seed_values,
        "defined_seed_numerator": len(defined),
        "registered_seed_denominator": 3,
        "assigned_episode_denominator": len(records),
        "assigned_window_denominator": all_windows["assigned_windows"],
        "submitted_window_numerator": all_windows["submitted_windows"],
        "missing_assigned_scores": all_windows["missing_assigned_scores"],
        "score_coverage": all_windows["score_coverage"],
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "per_bearing_metric_averaging_performed": False,
        "undefined_values_imputed_as_zero": False,
    }


def _selected_task_records(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    seed: int,
    horizon: int,
    cell: str,
    sequences: Sequence[str],
) -> list[Mapping[str, Any]]:
    return [
        records_by_key[(seed, sequence_id, horizon, cell)]
        for sequence_id in sequences
    ]


def _task_seed_contrast(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    seed: int,
    horizon: int,
    treatment: str,
    control: str,
    metric: str,
    treatment_sequences: Sequence[str],
    control_sequences: Sequence[str] | None = None,
) -> float | None:
    control_sequences = treatment_sequences if control_sequences is None else control_sequences
    treatment_value = _task_metric_value(
        _selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=treatment,
            sequences=treatment_sequences,
        ),
        metric,
    )
    control_value = _task_metric_value(
        _selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=control,
            sequences=control_sequences,
        ),
        metric,
    )
    if treatment_value is None or control_value is None:
        return None
    return treatment_value - control_value


def _task_metric_bootstrap(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    horizon: int,
    treatment: str,
    control: str,
    seed_offset: int,
) -> tuple[list[float] | None, int]:
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    rng = random.Random(int(protocol["statistics"]["bootstrap_seed"]) + seed_offset)
    replicates: list[float] = []
    for _ in range(int(protocol["statistics"]["bootstrap_iterations"])):
        draw = rng.choices(sequences, k=8)
        differences = [
            _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=horizon,
                treatment=treatment,
                control=control,
                metric=metric,
                treatment_sequences=draw,
            )
            for seed in seeds
        ]
        if all(value is not None for value in differences):
            replicates.append(statistics.fmean(value for value in differences if value is not None))
    interval = (
        [_percentile(replicates, 0.025), _percentile(replicates, 0.975)]
        if replicates
        else None
    )
    return interval, len(replicates)


def _task_metric_exact_swap(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    horizon: int,
    treatment: str,
    control: str,
    observed: float | None,
) -> tuple[float | None, int]:
    if observed is None:
        return None, 0
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    permuted: list[float] = []
    for mask in range(256):
        treatment_sequences = [
            sequence_id
            for index, sequence_id in enumerate(sequences)
            if mask & (1 << index)
        ]
        control_sequences = [
            sequence_id
            for index, sequence_id in enumerate(sequences)
            if not mask & (1 << index)
        ]
        seed_differences: list[float] = []
        valid = True
        for seed in seeds:
            treatment_records = [
                *(_selected_task_records(
                    records_by_key,
                    seed=seed,
                    horizon=horizon,
                    cell=treatment,
                    sequences=treatment_sequences,
                )),
                *(_selected_task_records(
                    records_by_key,
                    seed=seed,
                    horizon=horizon,
                    cell=control,
                    sequences=control_sequences,
                )),
            ]
            control_records = [
                *(_selected_task_records(
                    records_by_key,
                    seed=seed,
                    horizon=horizon,
                    cell=control,
                    sequences=treatment_sequences,
                )),
                *(_selected_task_records(
                    records_by_key,
                    seed=seed,
                    horizon=horizon,
                    cell=treatment,
                    sequences=control_sequences,
                )),
            ]
            treatment_value = _task_metric_value(treatment_records, metric)
            control_value = _task_metric_value(control_records, metric)
            if treatment_value is None or control_value is None:
                valid = False
                break
            seed_differences.append(treatment_value - control_value)
        if valid:
            permuted.append(statistics.fmean(seed_differences))
    if not permuted:
        return None, 0
    exceed = sum(abs(value) >= abs(observed) - 1e-15 for value in permuted)
    return exceed / len(permuted), len(permuted)


def _task_seed_swapped_contrast(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    seed: int,
    horizon: int,
    treatment: str,
    control: str,
    metric: str,
    sequences: Sequence[str],
    mask: int,
) -> float | None:
    treatment_kept = [
        sequence_id
        for index, sequence_id in enumerate(sequences)
        if mask & (1 << index)
    ]
    treatment_swapped = [
        sequence_id
        for index, sequence_id in enumerate(sequences)
        if not mask & (1 << index)
    ]
    treatment_records = [
        *_selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=treatment,
            sequences=treatment_kept,
        ),
        *_selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=control,
            sequences=treatment_swapped,
        ),
    ]
    control_records = [
        *_selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=control,
            sequences=treatment_kept,
        ),
        *_selected_task_records(
            records_by_key,
            seed=seed,
            horizon=horizon,
            cell=treatment,
            sequences=treatment_swapped,
        ),
    ]
    treatment_value = _task_metric_value(treatment_records, metric)
    control_value = _task_metric_value(control_records, metric)
    if treatment_value is None or control_value is None:
        return None
    return treatment_value - control_value


def _task_interaction_bootstrap(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    seed_offset: int,
) -> tuple[list[float] | None, int]:
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    rng = random.Random(int(protocol["statistics"]["bootstrap_seed"]) + seed_offset)
    replicates: list[float] = []
    for _ in range(int(protocol["statistics"]["bootstrap_iterations"])):
        draw = rng.choices(sequences, k=8)
        seed_values: list[float] = []
        for seed in seeds:
            high = _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=12,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                treatment_sequences=draw,
            )
            low = _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=3,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                treatment_sequences=draw,
            )
            if high is None or low is None:
                seed_values = []
                break
            seed_values.append(high - low)
        if len(seed_values) == len(seeds):
            replicates.append(statistics.fmean(seed_values))
    interval = (
        [_percentile(replicates, 0.025), _percentile(replicates, 0.975)]
        if replicates
        else None
    )
    return interval, len(replicates)


def _task_interaction_exact_swap(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    observed: float | None,
) -> tuple[float | None, int]:
    if observed is None:
        return None, 0
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    permutations: list[float] = []
    for mask in range(256):
        seed_values: list[float] = []
        for seed in seeds:
            high = _task_seed_swapped_contrast(
                records_by_key,
                seed=seed,
                horizon=12,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                sequences=sequences,
                mask=mask,
            )
            low = _task_seed_swapped_contrast(
                records_by_key,
                seed=seed,
                horizon=3,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                sequences=sequences,
                mask=mask,
            )
            if high is None or low is None:
                seed_values = []
                break
            seed_values.append(high - low)
        if len(seed_values) == len(seeds):
            permutations.append(statistics.fmean(seed_values))
    if not permutations:
        return None, 0
    exceed = sum(abs(value) >= abs(observed) - 1e-15 for value in permutations)
    return exceed / len(permutations), len(permutations)


def _registered_metrics(protocol: Mapping[str, Any]) -> list[str]:
    metrics = protocol["metrics"]
    names = [
        metrics["primary"]["name"],
        *metrics["task_outcomes"],
        *metrics["dynamic_behavior"],
        *metrics["general_rollout"],
    ]
    result: list[str] = []
    for name in names:
        if name not in result:
            result.append(str(name))
    return result


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise GraphDynamicFormalError("cannot take percentile of no values")
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _bootstrap_interval(
    cluster_values: Sequence[float], *, iterations: int, seed: int
) -> list[float] | None:
    if len(cluster_values) != 8:
        return None
    rng = random.Random(seed)
    values = list(cluster_values)
    draws = [
        statistics.fmean(rng.choices(values, k=8))
        for _ in range(iterations)
    ]
    return [_percentile(draws, 0.025), _percentile(draws, 0.975)]


def _exact_sign_p(cluster_values: Sequence[float]) -> tuple[float | None, int]:
    if len(cluster_values) != 8:
        return None, 0
    observed = abs(statistics.fmean(cluster_values))
    exceed = 0
    for mask in range(256):
        permuted = [
            value if mask & (1 << index) else -value
            for index, value in enumerate(cluster_values)
        ]
        if abs(statistics.fmean(permuted)) >= observed - 1e-15:
            exceed += 1
    return exceed / 256.0, 256


def _holm(pvalues: Mapping[str, float | None]) -> dict[str, float | None]:
    available = sorted(
        ((name, value) for name, value in pvalues.items() if value is not None),
        key=lambda item: (float(item[1]), item[0]),
    )
    adjusted: dict[str, float | None] = {name: None for name in pvalues}
    running = 0.0
    # The registered family size does not shrink when a hypothesis is
    # undefined; missing hypotheses are effectively ordered after available
    # p-values and remain null in the output.
    count = len(pvalues)
    for rank, (name, value) in enumerate(available):
        running = max(running, min(1.0, (count - rank) * float(value)))
        adjusted[name] = running
    return adjusted


def _report_pvalue(report: Mapping[str, Any]) -> float | None:
    value = report.get(
        "exact_two_sided_cluster_swap_p",
        report.get("exact_two_sided_sign_permutation_p"),
    )
    return None if value is None else _finite(value, "registered contrast p-value")


def _cell_report(records: Sequence[Mapping[str, Any]], metric: str) -> dict[str, Any]:
    if metric in TASK_COHORT_METRICS:
        return _task_cell_report(records, metric)
    seed_sequence_values: dict[str, dict[str, float | None]] = {}
    values: list[float | None] = []
    for record in sorted(
        records,
        key=lambda item: (int(item["seed"]), str(item["public_sequence_id"])),
    ):
        seed = str(int(record["seed"]))
        sequence_id = str(record["public_sequence_id"])
        value = _metric_value(record, metric)
        seed_sequence_values.setdefault(seed, {})[sequence_id] = value
        values.append(value)
    defined = [value for value in values if value is not None]
    return {
        "estimate": statistics.fmean(defined) if defined else None,
        "seed_sequence_values": seed_sequence_values,
        "defined_episode_numerator": len(defined),
        "assigned_episode_denominator": len(records),
        "undefined_values_imputed_as_zero": False,
    }


def _contrast_report(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    horizon: int,
    treatment: str,
    control: str,
    seed_offset: int,
) -> dict[str, Any]:
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    if metric in TASK_COHORT_METRICS:
        seed_differences = [
            _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=horizon,
                treatment=treatment,
                control=control,
                metric=metric,
                treatment_sequences=sequences,
            )
            for seed in seeds
        ]
        defined_differences = [
            value for value in seed_differences if value is not None
        ]
        observed = (
            statistics.fmean(defined_differences)
            if len(defined_differences) == len(seeds)
            else None
        )
        interval, valid_replicates = _task_metric_bootstrap(
            records_by_key,
            protocol=protocol,
            metric=metric,
            horizon=horizon,
            treatment=treatment,
            control=control,
            seed_offset=seed_offset,
        )
        pvalue, assignments = _task_metric_exact_swap(
            records_by_key,
            protocol=protocol,
            metric=metric,
            horizon=horizon,
            treatment=treatment,
            control=control,
            observed=observed,
        )
        treatment_records = [
            records_by_key[(seed, sequence_id, horizon, treatment)]
            for seed in seeds
            for sequence_id in sequences
        ]
        control_records = [
            records_by_key[(seed, sequence_id, horizon, control)]
            for seed in seeds
            for sequence_id in sequences
        ]
        treatment_summary = _replay_task_summary(treatment_records)
        control_summary = _replay_task_summary(control_records)
        return {
            "direction": f"{treatment}_minus_{control}",
            "horizon": horizon,
            "estimate": observed,
            "seed_level_differences": {
                str(seed): value
                for seed, value in zip(seeds, seed_differences, strict=True)
            },
            "paired_cluster_bootstrap_95ci": interval,
            "paired_cluster_bootstrap_valid_replicates": valid_replicates,
            "exact_two_sided_cluster_swap_p": pvalue,
            "exact_cluster_swap_assignments": assignments,
            "defined_seed_pair_numerator": len(defined_differences),
            "assigned_seed_pair_denominator": len(seeds),
            "matched_bearing_sequence_clusters": 8,
            "treatment_assigned_episode_denominator": len(treatment_records),
            "control_assigned_episode_denominator": len(control_records),
            "treatment_assigned_windows": treatment_summary["assigned_windows"],
            "control_assigned_windows": control_summary["assigned_windows"],
            "treatment_missing_assigned_scores": treatment_summary[
                "missing_assigned_scores"
            ],
            "control_missing_assigned_scores": control_summary[
                "missing_assigned_scores"
            ],
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "metric_recomputed_after_each_cluster_draw_or_swap": True,
            "per_bearing_metric_averaging_performed": False,
            "undefined_values_imputed_as_zero": False,
        }
    seed_level_differences_by_public_sequence: dict[
        str, dict[str, float | None]
    ] = {}
    public_sequence_cluster_differences: dict[str, float | None] = {}
    defined_pairs = 0
    for sequence_id in sequences:
        seed_differences: dict[str, float | None] = {}
        for seed in seeds:
            treatment_record = records_by_key[(seed, sequence_id, horizon, treatment)]
            control_record = records_by_key[(seed, sequence_id, horizon, control)]
            treatment_value = _metric_value(treatment_record, metric)
            control_value = _metric_value(control_record, metric)
            if treatment_value is not None and control_value is not None:
                seed_differences[str(seed)] = treatment_value - control_value
                defined_pairs += 1
            else:
                seed_differences[str(seed)] = None
        seed_level_differences_by_public_sequence[sequence_id] = seed_differences
        complete = [
            value for value in seed_differences.values() if value is not None
        ]
        public_sequence_cluster_differences[sequence_id] = (
            statistics.fmean(complete) if len(complete) == len(seeds) else None
        )
    cluster_values = [
        value
        for value in public_sequence_cluster_differences.values()
        if value is not None
    ]
    iterations = int(protocol["statistics"]["bootstrap_iterations"])
    bootstrap_seed = int(protocol["statistics"]["bootstrap_seed"]) + seed_offset
    pvalue, assignments = _exact_sign_p(cluster_values)
    return {
        "direction": f"{treatment}_minus_{control}",
        "horizon": horizon,
        "estimate": statistics.fmean(cluster_values) if cluster_values else None,
        "seed_level_differences_by_public_sequence": (
            seed_level_differences_by_public_sequence
        ),
        "public_sequence_cluster_differences": (
            public_sequence_cluster_differences
        ),
        "paired_cluster_bootstrap_95ci": _bootstrap_interval(
            cluster_values, iterations=iterations, seed=bootstrap_seed
        ),
        "paired_cluster_bootstrap_iterations": iterations,
        "paired_cluster_bootstrap_seed": bootstrap_seed,
        "paired_cluster_bootstrap_valid_replicates": (
            iterations if len(cluster_values) == len(sequences) else 0
        ),
        "exact_two_sided_sign_permutation_p": pvalue,
        "exact_sign_assignments": assignments,
        "defined_seed_pair_numerator": defined_pairs,
        "assigned_seed_pair_denominator": 24,
        "defined_public_sequence_cluster_numerator": len(cluster_values),
        "registered_public_sequence_cluster_denominator": 8,
        "seeds_averaged_within_cluster_before_inference": True,
        "undefined_values_imputed_as_zero": False,
    }


def _interaction_report(
    records_by_key: Mapping[tuple[int, str, int, str], Mapping[str, Any]],
    *,
    protocol: Mapping[str, Any],
    metric: str,
    seed_offset: int,
) -> dict[str, Any]:
    seeds = [int(value) for value in protocol["experiment_design"]["seeds"]]
    sequences = [f"sequence-{index:04d}" for index in range(1, 9)]
    if metric in TASK_COHORT_METRICS:
        seed_interactions: list[float | None] = []
        for seed in seeds:
            high = _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=12,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                treatment_sequences=sequences,
            )
            low = _task_seed_contrast(
                records_by_key,
                seed=seed,
                horizon=3,
                treatment="graph_full",
                control="reactive",
                metric=metric,
                treatment_sequences=sequences,
            )
            seed_interactions.append(
                None if high is None or low is None else high - low
            )
        defined = [value for value in seed_interactions if value is not None]
        observed = (
            statistics.fmean(defined) if len(defined) == len(seeds) else None
        )
        interval, valid_replicates = _task_interaction_bootstrap(
            records_by_key,
            protocol=protocol,
            metric=metric,
            seed_offset=seed_offset,
        )
        pvalue, assignments = _task_interaction_exact_swap(
            records_by_key,
            protocol=protocol,
            metric=metric,
            observed=observed,
        )
        return {
            "direction": "(graph_full_minus_reactive)_h12_minus_h3",
            "estimate": observed,
            "seed_level_interactions": {
                str(seed): value
                for seed, value in zip(seeds, seed_interactions, strict=True)
            },
            "paired_cluster_bootstrap_95ci": interval,
            "paired_cluster_bootstrap_valid_replicates": valid_replicates,
            "exact_two_sided_cluster_swap_p": pvalue,
            "exact_cluster_swap_assignments": assignments,
            "defined_seed_interaction_numerator": len(defined),
            "assigned_seed_interaction_denominator": len(seeds),
            "matched_bearing_sequence_clusters": 8,
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "metric_recomputed_after_each_cluster_draw_or_swap": True,
            "per_bearing_metric_averaging_performed": False,
            "nested_horizons_treated_as_independent": False,
            "undefined_values_imputed_as_zero": False,
        }
    clusters: list[float] = []
    defined = 0
    for sequence_id in sequences:
        seed_values: list[float] = []
        for seed in seeds:
            values = {
                (horizon, cell): _metric_value(
                    records_by_key[(seed, sequence_id, horizon, cell)], metric
                )
                for horizon in (3, 12)
                for cell in ("reactive", "graph_full")
            }
            if all(value is not None for value in values.values()):
                seed_values.append(
                    (values[(12, "graph_full")] - values[(12, "reactive")])
                    - (values[(3, "graph_full")] - values[(3, "reactive")])
                )
                defined += 1
        if len(seed_values) == len(seeds):
            clusters.append(statistics.fmean(seed_values))
    iterations = int(protocol["statistics"]["bootstrap_iterations"])
    pvalue, assignments = _exact_sign_p(clusters)
    return {
        "direction": "(graph_full_minus_reactive)_h12_minus_h3",
        "estimate": statistics.fmean(clusters) if clusters else None,
        "paired_cluster_bootstrap_95ci": _bootstrap_interval(
            clusters,
            iterations=iterations,
            seed=int(protocol["statistics"]["bootstrap_seed"]) + seed_offset,
        ),
        "exact_two_sided_sign_permutation_p": pvalue,
        "exact_sign_assignments": assignments,
        "defined_seed_interaction_numerator": defined,
        "assigned_seed_interaction_denominator": 24,
        "defined_public_sequence_cluster_numerator": len(clusters),
        "registered_public_sequence_cluster_denominator": 8,
        "nested_horizons_treated_as_independent": False,
        "undefined_values_imputed_as_zero": False,
    }


def analyze_formal_cohort(
    output_root: str | Path,
    protocol_value: Mapping[str, Any],
    acceptance_value: Mapping[str, Any],
    *,
    private_dynamic_assignments: Mapping[str, Any],
) -> dict[str, Any]:
    """Analyze a complete accepted formal cohort without provider access."""

    protocol = validate_protocol(protocol_value)
    acceptance = validate_acceptance(output_root, protocol, acceptance_value)
    records, inclusion = collect_formal_records(
        output_root,
        protocol,
        private_dynamic_assignments=private_dynamic_assignments,
    )
    if acceptance.get("canonical_inclusion") != inclusion:
        raise GraphDynamicFormalError(
            "canonical cohort changed after acceptance or inclusion report drifted"
        )
    metrics = _registered_metrics(protocol)
    records_by_key = {
        (
            int(record["seed"]),
            str(record["public_sequence_id"]),
            int(record["horizon"]),
            str(record["cell"]),
        ): record
        for record in records
    }
    by_cell: dict[str, Any] = {}
    for cell in registered_cells(protocol):
        selected = [record for record in records if record["horizon"] == cell.horizon and record["cell"] == cell.name]
        by_cell[cell.key] = {
            "horizon": cell.horizon,
            "cell": cell.name,
            "agent_profile_id": cell.agent_profile_id,
            "assigned_episode_denominator": len(selected),
            "terminal_status_counts": dict(sorted(Counter(str(row["terminal_status"]) for row in selected).items())),
            "failure_kind_counts": dict(sorted(Counter(str(row["failure_kind"]) for row in selected if row["failure_kind"] is not None).items())),
            "metrics": {metric: _cell_report(selected, metric) for metric in metrics},
        }

    p2e2_by_horizon: dict[str, Any] = {}
    for horizon_index, horizon in enumerate((3, 6, 12)):
        p2e2_by_horizon[str(horizon)] = {
            metric: _contrast_report(
                records_by_key,
                protocol=protocol,
                metric=metric,
                horizon=horizon,
                treatment="graph_full",
                control="reactive",
                seed_offset=1000 * horizon_index + metric_index,
            )
            for metric_index, metric in enumerate(metrics)
        }
    interactions = {
        metric: _interaction_report(
            records_by_key,
            protocol=protocol,
            metric=metric,
            seed_offset=5000 + metric_index,
        )
        for metric_index, metric in enumerate(metrics)
    }
    for metric in metrics:
        adjusted = _holm(
            {"h12_minus_h3": _report_pvalue(interactions[metric])}
        )
        interactions[metric]["holm_adjusted_p"] = adjusted["h12_minus_h3"]

    ablation_cells = {
        "P2-E3": "graph_no_recovery_revision_edge",
        "P2-E4": "graph_no_observation_conditioned_branching",
        "P2-E5": "graph_no_persistent_graph_state",
        "P2-E6": "graph_no_replanning",
    }
    ablations: dict[str, Any] = {
        experiment_id: {
            metric: _contrast_report(
                records_by_key,
                protocol=protocol,
                metric=metric,
                horizon=12,
                treatment="graph_full",
                control=control,
                seed_offset=10000 + experiment_index * 1000 + metric_index,
            )
            for metric_index, metric in enumerate(metrics)
        }
        for experiment_index, (experiment_id, control) in enumerate(ablation_cells.items())
    }
    for metric in metrics:
        adjusted = _holm(
            {
                experiment_id: reports[metric]["exact_two_sided_sign_permutation_p"]
                if "exact_two_sided_sign_permutation_p" in reports[metric]
                else _report_pvalue(reports[metric])
                for experiment_id, reports in ablations.items()
            }
        )
        for experiment_id, value in adjusted.items():
            ablations[experiment_id][metric]["holm_adjusted_p"] = value

    return {
        "schema_version": RESULT_SCHEMA,
        "status": "accepted_complete_formal_cohort_analysis",
        "protocol_id": protocol["protocol_id"],
        "provider_profile_id": protocol["runtime_and_provider_profile"]["formal_provider_profile_id"],
        "output_root": str(Path(output_root).resolve()),
        "provider_calls_performed_by_analyzer": False,
        "primary_endpoint_authority": {
            "target_source": "registered_private_data_port_assignment",
            "prediction_source": "canonical_rollout_successful_submit_prefix",
            "derived_evaluation_jsonl_ingested": False,
            "private_paths_serialized": False,
        },
        "canonical_inclusion": inclusion,
        "grouping_invariants": {
            "absolute_summaries_keyed_by_horizon_and_agent_profile": True,
            "task_primary_recomputed_over_all_assigned_windows_within_seed_cell": True,
            "per_bearing_average_precision_performed": False,
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "pooled_headline_graph_effect_across_horizons": False,
            "pool_across_provider_model_or_runtime_profiles": False,
            "nested_horizons_treated_as_independent": False,
            "failed_non_provider_terminals_retained": True,
        },
        "by_cell": by_cell,
        "registered_contrasts": {
            "P2-E2": {
                "graph_full_minus_reactive_by_horizon": p2e2_by_horizon,
                "registered_h12_minus_h3_interaction": interactions,
            },
            "P2-E3_to_P2-E6": ablations,
            "P2-E7": {
                "new_episode_bundles_added": 0,
                "reused_horizon_12_cells": [
                    "reactive",
                    "graph_full",
                    "graph_no_observation_conditioned_branching",
                ],
                "dynamic_metrics": list(protocol["metrics"]["dynamic_behavior"]),
                "registered_report_sources": {
                    "graph_full_minus_reactive": (
                        "P2-E2.graph_full_minus_reactive_by_horizon.12"
                    ),
                    "graph_full_minus_graph_no_observation_conditioned_branching": (
                        "P2-E3_to_P2-E6.P2-E4"
                    ),
                },
                "claim_boundary": (
                    "Operating-condition identifier changes only; no fault onset, "
                    "event-F1, detection-delay, or physical-time claim."
                ),
            },
        },
        "claim_boundary": (
            "One frozen Paderborn/openrouter-free/North dynamic profile only. "
            "Observed directions and uncertainty must be reported without pooling "
            "horizons, profiles, providers, models, runtimes, or duplicate P2-E7 rows."
        ),
    }


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Provider-free acceptance/analysis for Generic-base Graph dynamic formal v3."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    catalog_parser = subparsers.add_parser("catalog")
    catalog_parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    catalog_parser.add_argument("--output", type=Path)
    for command in ("accept", "analyze"):
        child = subparsers.add_parser(command)
        child.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
        child.add_argument(
            "--dataset-protocol", type=Path, default=DEFAULT_DATASET_PROTOCOL
        )
        child.add_argument("--output-root", type=Path, required=True)
        child.add_argument(
            "--private-metadata-env", required=True, metavar="ENV_NAME"
        )
        child.add_argument(
            "--private-signal-env", required=True, metavar="ENV_NAME"
        )
        child.add_argument("--output", type=Path)
        if command == "analyze":
            child.add_argument("--acceptance", type=Path, required=True)
    args = parser.parse_args(argv)
    protocol = load_protocol(args.protocol)
    if args.command == "catalog":
        catalog = build_public_event_catalog(protocol)
        if args.output is not None:
            _write_json(args.output, catalog)
        print(json.dumps(catalog, indent=2, sort_keys=True, allow_nan=False))
        return 0
    assignments = build_private_dynamic_assignments(
        protocol,
        dataset_protocol_path=args.dataset_protocol,
        metadata_path=_private_path(
            args.private_metadata_env, label="private metadata"
        ),
        signal_path=_private_path(args.private_signal_env, label="private signal"),
    )
    if args.command == "accept":
        report = accept_formal_cohort(
            args.output_root,
            protocol,
            private_dynamic_assignments=assignments,
        )
        if args.output is not None:
            _write_json(args.output, report)
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
        return 0 if report["accepted"] else 2
    acceptance = _read_json(args.acceptance, "formal acceptance")
    result = analyze_formal_cohort(
        args.output_root,
        protocol,
        acceptance,
        private_dynamic_assignments=assignments,
    )
    if args.output is not None:
        _write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
