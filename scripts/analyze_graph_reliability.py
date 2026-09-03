#!/usr/bin/env python3
"""Fail-closed analysis for the isolated Paper-2 P2-E9 reliability cohort.

This module has no provider client and no experiment-runner import.  It reads
the preregistered exact-six canonical episode bundles after a separate
acceptance report proves the complete n=10 Reactive-vs-Graph replay cohort,
then independently rebuilds evaluator-only targets through the private
DataPort.  Derived ``evaluation.jsonl`` rows are never target authority.
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
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
_BENCHMARK_SRC = ROOT.parent / "p01-phm-agent-benchmark" / "src"
if _BENCHMARK_SRC.is_dir() and str(_BENCHMARK_SRC) not in sys.path:
    sys.path.insert(0, str(_BENCHMARK_SRC))

from phm_agent_benchmark.phase1 import LocalPaderbornDataPort, anomaly_target
from phm_agent_benchmark.phase1.experiment import aggregate_results, load_dataset_protocol
from phm_graph_agent.dynamic_runtime import build_master_sequences


PROTOCOL_SCHEMA_VERSION = "graph_reliability_protocol_v2"
SCHEDULE_SCHEMA_VERSION = "graph_reliability_schedule_v2"
ACCEPTANCE_SCHEMA_VERSION = "graph_reliability_acceptance_v2"
RESULT_SCHEMA_VERSION = "graph_reliability_result_v2"
REQUIRED_REPEAT_COUNT = 10
REQUIRED_SEQUENCE_COUNT = 8
ARMS = ("reactive", "graph")
PROVIDER_FAILURE_KIND = "provider_error"
REPLAY_MISSING_SCORE_POLICY_ID = "phase1_replay_target_adverse_missing_score_v1"
EVALUATOR_ASSIGNMENT_CONTRACT = "phase1_registered_data_port_assignment_v1"
PRIMARY_METRIC = "task.average_precision"
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_reliability_protocol_v2.yaml"
DEFAULT_DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
)
DEFAULT_DYNAMIC_PROTOCOL = (
    ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml"
)
_ENVIRONMENT_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


class GraphReliabilityContractError(ValueError):
    """Raised when data do not satisfy the frozen P2-E9 contract."""


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GraphReliabilityContractError(f"{label} must be a mapping")
    return dict(value)


def _unique_strings(value: Any, label: str, *, count: int | None = None) -> list[str]:
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes, bytearray))
        or any(not isinstance(item, str) or not item.strip() for item in value)
    ):
        raise GraphReliabilityContractError(f"{label} must be a string list")
    result = [str(item) for item in value]
    if len(result) != len(set(result)):
        raise GraphReliabilityContractError(f"{label} must contain unique values")
    if count is not None and len(result) != count:
        raise GraphReliabilityContractError(
            f"{label} must contain exactly {count} values"
        )
    return result


def _finite_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise GraphReliabilityContractError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise GraphReliabilityContractError(f"{label} must be finite")
    return result


def validate_graph_reliability_protocol(value: Mapping[str, Any]) -> dict[str, Any]:
    """Return a plain mapping only if the P2-E9 preregistration is coherent."""

    protocol = _mapping(value, "protocol")
    if protocol.get("schema_version") != PROTOCOL_SCHEMA_VERSION:
        raise GraphReliabilityContractError("unsupported reliability protocol schema")
    if protocol.get("status") != (
        "preregistered_generic_base_runner_ready_formal_launch_gated"
    ):
        raise GraphReliabilityContractError("reliability protocol status has drifted")
    if protocol.get("supersedes") != "graph_reliability_protocol_v1.yaml":
        raise GraphReliabilityContractError("v2 must supersede the PHMskills-base v1")
    if protocol.get("formal_launch") != "gated":
        raise GraphReliabilityContractError("formal reliability launch must remain gated")
    if protocol.get("experiment_id") != "P2-E9":
        raise GraphReliabilityContractError("Graph reliability must register P2-E9")

    cohort = _mapping(protocol.get("cohort"), "cohort")
    if cohort.get("role") != "separate_reliability_extension":
        raise GraphReliabilityContractError("P2-E9 must be a separate extension")
    if cohort.get("repeat_count") != REQUIRED_REPEAT_COUNT:
        raise GraphReliabilityContractError("P2-E9 requires exactly 10 repeats")
    if cohort.get("relationship_to_primary") != (
        "report_alongside_never_replace_append_or_pool"
    ):
        raise GraphReliabilityContractError("relationship to primary has drifted")
    if cohort.get("pooling_with_three_seed_primary") != "forbidden":
        raise GraphReliabilityContractError("pooling with the primary is forbidden")
    repeats_value = cohort.get("repeats")
    if not isinstance(repeats_value, list):
        raise GraphReliabilityContractError("cohort.repeats must be a list")
    repeats = [_mapping(item, "cohort repeat") for item in repeats_value]
    if len(repeats) != REQUIRED_REPEAT_COUNT:
        raise GraphReliabilityContractError("exactly 10 repeat rows are required")
    repeat_ids = [item.get("repeat_id") for item in repeats]
    seeds = [item.get("seed") for item in repeats]
    if any(not isinstance(item, str) or not item for item in repeat_ids):
        raise GraphReliabilityContractError("repeat IDs must be non-empty strings")
    if len(set(repeat_ids)) != REQUIRED_REPEAT_COUNT:
        raise GraphReliabilityContractError("repeat IDs must be unique")
    if any(type(seed) is not int for seed in seeds):
        raise GraphReliabilityContractError("repeat seeds must be integers")
    if len(set(seeds)) != REQUIRED_REPEAT_COUNT:
        raise GraphReliabilityContractError("repeat seeds must be independent/unique")
    primary_seeds = cohort.get("primary_cohort_seeds")
    if not isinstance(primary_seeds, list) or any(
        type(seed) is not int for seed in primary_seeds
    ):
        raise GraphReliabilityContractError("primary seeds must be an integer list")
    if set(seeds) & set(primary_seeds):
        raise GraphReliabilityContractError("reliability seeds overlap primary seeds")

    scope = _mapping(protocol.get("scope"), "scope")
    if scope.get("task_id") != "online_replay_monitoring":
        raise GraphReliabilityContractError("P2-E9 reliability is replay-only")
    if scope.get("rotation") != "rotation_0":
        raise GraphReliabilityContractError("P2-E9 freezes rotation_0")
    if scope.get("windows_per_episode") != 3:
        raise GraphReliabilityContractError("P2-E9 freezes three replay windows")
    sequences = _unique_strings(
        scope.get("public_sequence_ids"),
        "scope.public_sequence_ids",
        count=REQUIRED_SEQUENCE_COUNT,
    )
    arms = _unique_strings(scope.get("arms"), "scope.arms", count=2)
    if arms != list(ARMS):
        raise GraphReliabilityContractError("arms must be ordered reactive, graph")
    expected_pairs = REQUIRED_REPEAT_COUNT * REQUIRED_SEQUENCE_COUNT
    if scope.get("expected_pairs_per_repeat") != REQUIRED_SEQUENCE_COUNT:
        raise GraphReliabilityContractError("pairs-per-repeat count drifted")
    if scope.get("expected_pairs_total") != expected_pairs:
        raise GraphReliabilityContractError("total paired-unit count drifted")
    if scope.get("expected_episode_bundles_total") != expected_pairs * len(ARMS):
        raise GraphReliabilityContractError("total episode count drifted")

    matched = _mapping(protocol.get("matched_contract"), "matched_contract")
    if matched.get("paired_unit") != [
        "repeat_id",
        "seed",
        "rotation",
        "public_sequence_id",
    ]:
        raise GraphReliabilityContractError("paired unit has drifted")
    if matched.get("arm_order_rule") != "alternate_by_repeat_plus_sequence_parity":
        raise GraphReliabilityContractError("arm counterbalancing rule has drifted")

    profile = _mapping(protocol.get("profile"), "profile")
    profile_id = profile.get("reliability_profile_id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise GraphReliabilityContractError("reliability profile ID is required")
    if profile.get("effective_runtime_contract") == profile.get(
        "base_runtime_contract"
    ):
        raise GraphReliabilityContractError("reliability runtime must be isolated")
    if profile.get("separate_from_active_v6_primary_profile") is not True:
        raise GraphReliabilityContractError("active v6 primary isolation is required")
    if profile.get("separate_from_dynamic_ablation_profile") is not True:
        raise GraphReliabilityContractError("dynamic-profile isolation is required")
    profile_arms = _mapping(profile.get("arms"), "profile.arms")
    if list(profile_arms) != list(ARMS):
        raise GraphReliabilityContractError("profile arm order has drifted")
    expected_arm_profiles = {
        "reactive": (
            "reactive-sequential-agent",
            "benchmark_generic_llm_tool_agent_v1",
            "reactive_sequential_agent_v1",
            "reactive",
        ),
        "graph": (
            "graph-decision-agent",
            "graph_decision_control_v1",
            "graph_decision_agent_v1",
            "full",
        ),
    }
    for arm, (agent_id, control_id, implementation_id, graph_profile) in expected_arm_profiles.items():
        arm_profile = _mapping(profile_arms.get(arm), f"profile.arms.{arm}")
        if (
            arm_profile.get("agent_id") != agent_id
            or arm_profile.get("agent_control_id") != control_id
            or arm_profile.get("agent_implementation_id") != implementation_id
            or arm_profile.get("graph_policy_profile") != graph_profile
        ):
            raise GraphReliabilityContractError(f"{arm} profile has drifted")
    identity = _mapping(protocol.get("identity_contract"), "identity_contract")
    expected_identity = {
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "control_agent_id": "reactive-sequential-agent",
        "treatment_agent_id": "graph-decision-agent",
        "control_implementation_id": "reactive_sequential_agent_v1",
        "treatment_implementation_id": "graph_decision_agent_v1",
        "phmskills_runtime_or_catalog_allowed": False,
    }
    identity_drift = _profile_drift(identity, expected_identity)
    if identity_drift:
        raise GraphReliabilityContractError(
            f"Generic-base identity contract drift: {identity_drift}"
        )
    if profile.get("p2_experiment_id") != identity["p2_experiment_id"]:
        raise GraphReliabilityContractError("profile P2 experiment identity drifted")
    if profile.get("matched_control_id") != identity["matched_control_id"]:
        raise GraphReliabilityContractError("profile matched-control identity drifted")
    for price_name in ("input_usd_per_million", "output_usd_per_million"):
        if _finite_number(profile.get(price_name), f"profile.{price_name}") < 0.0:
            raise GraphReliabilityContractError(f"profile.{price_name} must be nonnegative")
    shared = _mapping(matched.get("shared"), "matched_contract.shared")
    shared_profile_projection = {
        "dataset_protocol": "phm_agent_dataset_protocol_v1",
        "dataset_protocol_id": "paderborn_phase1_v1",
        "dataset_protocol_schema": "phm_agent_dataset_protocol_v1",
        "dataset_id": "paderborn-bearing-datacenter",
        "evaluator_assignment_contract": EVALUATOR_ASSIGNMENT_CONTRACT,
        "base_runtime_contract": profile["base_runtime_contract"],
        "backbone_model": profile["model"],
        "provider": profile["provider"],
        "inference_protocol": profile["inference_protocol"],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "p2_experiment_id": profile["p2_experiment_id"],
        "matched_control_id": profile["matched_control_id"],
    }
    shared_drift = _profile_drift(shared, shared_profile_projection)
    if shared_drift:
        raise GraphReliabilityContractError(
            f"matched shared profile drift: {shared_drift}"
        )
    if profile.get("route_switch_within_profile") != "forbidden":
        raise GraphReliabilityContractError("route switching must remain forbidden")
    if profile.get("model_switch_within_profile") != "forbidden":
        raise GraphReliabilityContractError("model switching must remain forbidden")
    budget = _mapping(profile.get("budget"), "profile.budget")
    for name in (
        "max_tool_calls",
        "max_window_reads",
        "max_operator_calls",
        "max_model_calls",
        "max_llm_turns",
        "max_data_points",
        "max_data_bytes",
    ):
        if type(budget.get(name)) is not int or budget[name] <= 0:
            raise GraphReliabilityContractError(f"invalid budget field {name}")
    if budget.get("max_wall_clock_seconds") is not None:
        raise GraphReliabilityContractError(
            "P2-E9 max_wall_clock_seconds must remain explicitly null"
        )

    attempt = _mapping(protocol.get("attempt_policy"), "attempt_policy")
    canonical_files = _unique_strings(
        attempt.get("canonical_episode_files"),
        "attempt_policy.canonical_episode_files",
        count=6,
    )
    if set(canonical_files) != {
        "run.json",
        "rollout.jsonl",
        "submission.json",
        "metrics.json",
        "failures.jsonl",
        "artifacts.json",
    }:
        raise GraphReliabilityContractError("canonical exact-six file set drifted")
    if attempt.get("provider_failure_kind") != PROVIDER_FAILURE_KIND:
        raise GraphReliabilityContractError("provider failure kind has drifted")
    if attempt.get("non_provider_failure_policy") != "retain_in_denominator":
        raise GraphReliabilityContractError("non-provider failures must be retained")

    metrics = _mapping(protocol.get("metrics"), "metrics")
    task_metric_names = _unique_strings(metrics.get("task"), "metrics.task")
    rollout_metric_names = _unique_strings(metrics.get("rollout"), "metrics.rollout")
    metric_names = _unique_strings(
        [*task_metric_names, *rollout_metric_names], "registered metrics"
    )
    if metrics.get("primary") != PRIMARY_METRIC:
        raise GraphReliabilityContractError(
            "P2-E9 primary endpoint must be replay task.average_precision"
        )
    if metrics["primary"] not in metric_names:
        raise GraphReliabilityContractError("primary metric is not registered")
    primary_contract = _mapping(
        metrics.get("primary_contract"), "metrics.primary_contract"
    )
    expected_primary_contract = {
        "population": "all_protocol_assigned_replay_windows",
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "repeat_aggregation": (
            "recompute_over_all_24_assigned_windows_then_equal_weight_10_repeats"
        ),
        "private_target_authority": "registered_private_data_port_assignment",
        "prediction_authority": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_allowed": False,
        "per_sequence_average_precision_averaging": "forbidden",
    }
    primary_drift = _profile_drift(primary_contract, expected_primary_contract)
    if primary_drift:
        raise GraphReliabilityContractError(
            f"P2-E9 task-primary contract drifted: {primary_drift}"
        )
    if metrics.get("missing_metric_policy") != (
        "report_null_with_defined_numerator_never_impute_zero"
    ):
        raise GraphReliabilityContractError("N/A policy has drifted")
    pass_rule = _mapping(protocol.get("pass_rule"), "pass_rule")
    if pass_rule.get("role") != "explanatory_rollout_reliability_not_task_primary":
        raise GraphReliabilityContractError("grounded pass rule role drifted")
    if (
        pass_rule.get("source")
        != "canonical_metrics.rollout_metrics.grounded_completion"
    ):
        raise GraphReliabilityContractError("grounded pass-rule source drifted")

    statistics_value = _mapping(protocol.get("statistics"), "statistics")
    bootstrap = _mapping(statistics_value.get("bootstrap"), "statistics.bootstrap")
    if type(bootstrap.get("iterations")) is not int or bootstrap["iterations"] <= 0:
        raise GraphReliabilityContractError("bootstrap iterations must be positive")
    if type(bootstrap.get("seed")) is not int:
        raise GraphReliabilityContractError("bootstrap seed must be an integer")
    if statistics_value.get("paired_direction") != "graph_minus_reactive":
        raise GraphReliabilityContractError("paired direction has drifted")
    if statistics_value.get("repeat_estimand") != (
        "equal_weight_mean_of_10_repeat_level_target_adverse_average_precision"
    ):
        raise GraphReliabilityContractError("repeat-level AP estimand drifted")

    execution = _mapping(protocol.get("execution"), "execution")
    if execution.get("schedule_schema_version") != SCHEDULE_SCHEMA_VERSION:
        raise GraphReliabilityContractError("schedule schema has drifted")
    if execution.get("acceptance_schema_version") != ACCEPTANCE_SCHEMA_VERSION:
        raise GraphReliabilityContractError("acceptance schema has drifted")
    if execution.get("result_schema_version") != RESULT_SCHEMA_VERSION:
        raise GraphReliabilityContractError("result schema has drifted")
    if execution.get("provider_execution_authorized_by_schedule") is not False:
        raise GraphReliabilityContractError("the schedule cannot authorize a provider")
    if execution.get("primary_run_directories_ingested") is not False:
        raise GraphReliabilityContractError("primary run ingestion must be false")
    if execution.get("dedicated_runner_contract") != (
        "phase1_graph_reliability_generic_n10_v2"
    ):
        raise GraphReliabilityContractError("dedicated runner contract has drifted")
    if execution.get("dedicated_runner_contract_implemented") is not True:
        raise GraphReliabilityContractError(
            "the dedicated reliability runner contract must be implemented"
        )
    if execution.get("runner_commands_emitted_by_schedule") is not True:
        raise GraphReliabilityContractError(
            "the provider-free schedule must emit, but never invoke, runner commands"
        )
    expected_execution = {
        "runner": "scripts/run_graph_reliability_v2.py",
        "underlying_dynamic_runner": "scripts/run_graph_experiment.py",
        "dynamic_protocol": "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml",
        "dynamic_protocol_id": "paderborn_graph_dynamic_ablation_v2",
        "runner_runtime_contract": "phase1_graph_dynamic_generic_ablation_v2",
        "formal_parent_root": "paper/experiments/runs/formal/graph_reliability_v2",
    }
    execution_drift = _profile_drift(execution, expected_execution)
    if execution_drift:
        raise GraphReliabilityContractError(
            f"reliability execution identity drift: {execution_drift}"
        )
    if profile.get("effective_runtime_contract") != execution[
        "runner_runtime_contract"
    ]:
        raise GraphReliabilityContractError(
            "profile/runtime implementation identity drifted"
        )
    required_flags = _unique_strings(
        execution.get("required_runner_flags"), "execution.required_runner_flags"
    )
    for flag in (
        "--reliability-protocol",
        "--reliability-profile-id",
        "--repeat-id",
        "--arm",
        "--runtime",
        "--dynamic-protocol",
        "--public-sequence-id",
        "--horizon",
        "--rotation",
        "--input-usd-per-million",
        "--output-usd-per-million",
        "--output-root",
    ):
        if flag not in required_flags:
            raise GraphReliabilityContractError(
                f"dedicated runner contract lacks required flag {flag}"
            )
    _unique_strings(
        execution.get("required_runner_identity_literals"),
        "execution.required_runner_identity_literals",
    )
    profile_id = profile["reliability_profile_id"]
    expected_roots = {
        "formal_root": (
            "paper/experiments/runs/formal/graph_reliability_v2/" + profile_id
        ),
        "results_root": (
            "paper/experiments/results/graph_reliability_v2/" + profile_id
        ),
    }
    root_drift = _profile_drift(execution, expected_roots)
    if root_drift:
        raise GraphReliabilityContractError(
            f"reliability root identity drift: {root_drift}"
        )
    return protocol


def load_graph_reliability_protocol(path: str | Path = DEFAULT_PROTOCOL) -> dict[str, Any]:
    try:
        value = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphReliabilityContractError(f"cannot load protocol {path}: {exc}") from exc
    return validate_graph_reliability_protocol(_mapping(value, "protocol file"))


def _private_path(environment_name: str, *, label: str) -> Path:
    if _ENVIRONMENT_NAME.fullmatch(environment_name) is None:
        raise GraphReliabilityContractError(
            f"{label} environment-variable name is invalid"
        )
    raw = os.environ.get(environment_name)
    if not isinstance(raw, str) or not raw.strip():
        raise GraphReliabilityContractError(
            f"{label} environment variable {environment_name} is unset or empty"
        )
    path = Path(raw).expanduser()
    if not path.is_absolute():
        raise GraphReliabilityContractError(f"{label} environment value must be absolute")
    return path


def _merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_dynamic_protocol(path: Path) -> dict[str, Any]:
    try:
        overlay_value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphReliabilityContractError(
            f"cannot load registered dynamic protocol: {type(exc).__name__}"
        ) from exc
    overlay = _mapping(overlay_value, "dynamic protocol")
    base_name = overlay.pop("extends_protocol", None)
    if base_name is None:
        protocol = overlay
    else:
        if not isinstance(base_name, str) or Path(base_name).name != base_name:
            raise GraphReliabilityContractError(
                "dynamic protocol extension must name one sibling file"
            )
        try:
            base_value = yaml.safe_load(
                (path.parent / base_name).read_text(encoding="utf-8")
            )
        except (OSError, yaml.YAMLError) as exc:
            raise GraphReliabilityContractError(
                f"cannot load extended dynamic protocol: {type(exc).__name__}"
            ) from exc
        protocol = _merge(_mapping(base_value, "extended dynamic protocol"), overlay)
    return protocol


def build_private_replay_assignments(
    protocol_value: Mapping[str, Any],
    *,
    dataset_protocol_path: str | Path,
    dynamic_protocol_path: str | Path,
    metadata_path: str | Path,
    signal_path: str | Path,
) -> dict[str, dict[str, Any]]:
    """Rebuild evaluator-only horizon-3 assignments through the DataPort."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    shared = protocol["matched_contract"]["shared"]
    try:
        dataset = load_dataset_protocol(Path(dataset_protocol_path))
    except (OSError, TypeError, ValueError, yaml.YAMLError) as exc:
        raise GraphReliabilityContractError(
            f"cannot load registered dataset protocol: {type(exc).__name__}"
        ) from exc
    dataset_identity = _mapping(dataset.get("dataset"), "dataset protocol identity")
    observed_dataset = {
        "dataset_protocol_id": dataset.get("protocol_id"),
        "dataset_protocol_schema": dataset.get("schema_version"),
        "dataset_id": dataset_identity.get("dataset_id"),
        "evaluator_assignment_contract": dataset_identity.get(
            "evaluator_assignment_contract"
        ),
    }
    dataset_drift = _profile_drift(observed_dataset, {
        name: shared[name] for name in observed_dataset
    })
    if dataset_drift:
        raise GraphReliabilityContractError(
            f"private dataset/DataPort authority drifted: {dataset_drift}"
        )

    dynamic = _load_dynamic_protocol(Path(dynamic_protocol_path))
    expected_dynamic = {
        "schema_version": "graph_dynamic_ablation_protocol_v2",
        "protocol_id": protocol["execution"]["dynamic_protocol_id"],
    }
    dynamic_drift = _profile_drift(dynamic, expected_dynamic)
    if dynamic_drift:
        raise GraphReliabilityContractError(
            f"registered dynamic protocol drifted: {dynamic_drift}"
        )
    if dynamic.get("dataset", {}).get("dataset_id") != shared["dataset_id"]:
        raise GraphReliabilityContractError("dynamic/dataset physical identity drifted")

    try:
        with LocalPaderbornDataPort(
            metadata_path,
            signal_path,
            public_id_seed=int(dataset["agent_visibility"]["sample_handle"]["seed"]),
        ) as data:
            sequences = build_master_sequences(
                data,
                dataset,
                dynamic,
                protocol["scope"]["rotation"],
            )
            assignments = {
                sequence_id: {
                    "sample_ids": list(sequence.sample_ids[: protocol["scope"]["windows_per_episode"]]),
                    "private_target": {
                        sample_id: anomaly_target(data.private_record(sample_id))
                        for sample_id in sequence.sample_ids[
                            : protocol["scope"]["windows_per_episode"]
                        ]
                    },
                }
                for sequence_id, sequence in sequences.items()
            }
    except (KeyError, OSError, RuntimeError, TypeError, ValueError) as exc:
        raise GraphReliabilityContractError(
            f"cannot rebuild private replay assignments: {type(exc).__name__}"
        ) from exc
    return _validate_private_replay_assignments(assignments, protocol)


def _validate_private_replay_assignments(
    value: Mapping[str, Any], protocol: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    assignments = _mapping(value, "private replay assignments")
    expected_sequences = list(protocol["scope"]["public_sequence_ids"])
    if set(assignments) != set(expected_sequences):
        raise GraphReliabilityContractError(
            "private replay assignments do not cover the registered sequences"
        )
    expected_windows = int(protocol["scope"]["windows_per_episode"])
    normalized: dict[str, dict[str, Any]] = {}
    seen_samples: set[str] = set()
    for sequence_id in expected_sequences:
        row = _mapping(assignments[sequence_id], f"private assignment {sequence_id}")
        sample_ids = _unique_strings(
            row.get("sample_ids"),
            f"private assignment {sequence_id}.sample_ids",
            count=expected_windows,
        )
        targets = _mapping(
            row.get("private_target"),
            f"private assignment {sequence_id}.private_target",
        )
        if set(targets) != set(sample_ids):
            raise GraphReliabilityContractError(
                f"private targets do not match assigned samples for {sequence_id}"
            )
        normalized_targets: dict[str, int] = {}
        for sample_id in sample_ids:
            target = targets[sample_id]
            if type(target) is not int or target not in {0, 1}:
                raise GraphReliabilityContractError(
                    f"private replay target is not binary for {sequence_id}"
                )
            normalized_targets[sample_id] = target
        overlap = seen_samples & set(sample_ids)
        if overlap:
            raise GraphReliabilityContractError(
                "private replay samples overlap across registered sequences"
            )
        seen_samples.update(sample_ids)
        normalized[sequence_id] = {
            "sample_ids": sample_ids,
            "private_target": normalized_targets,
        }
    return normalized


def expected_run_directories(
    output_root: str | Path, protocol: Mapping[str, Any]
) -> dict[tuple[str, str], Path]:
    protocol = validate_graph_reliability_protocol(protocol)
    root = Path(output_root).resolve()
    profile_id = protocol["profile"]["reliability_profile_id"]
    rotation = protocol["scope"]["rotation"]
    return {
        (str(repeat["repeat_id"]), arm): (
            root / profile_id / str(repeat["repeat_id"]) / arm / rotation
        )
        for repeat in protocol["cohort"]["repeats"]
        for arm in ARMS
    }


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphReliabilityContractError(f"cannot read {label} {path}: {exc}") from exc
    return _mapping(value, f"{label} {path}")


def _read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise GraphReliabilityContractError(f"cannot read {label} {path}: {exc}") from exc
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise GraphReliabilityContractError(
                f"invalid {label} line {line_number} in {path}: {exc}"
            ) from exc
        rows.append(_mapping(value, f"{label} line {line_number}"))
    return rows


def _expected_model_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "provider": profile["provider"],
        "model_id": profile["model"],
        "protocol": profile["inference_protocol"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
    }


def _profile_drift(observed: Mapping[str, Any], expected: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: {"observed": observed.get(key), "expected": expected_value}
        for key, expected_value in expected.items()
        if observed.get(key) != expected_value
    }


def _validate_manifest(
    path: Path,
    protocol: Mapping[str, Any],
    *,
    repeat_id: str,
    seed: int,
    arm: str,
) -> None:
    manifest = _read_json(path, "run manifest")
    profile = protocol["profile"]
    scope = protocol["scope"]
    shared = protocol["matched_contract"]["shared"]
    expected = {
        "reliability_profile_id": profile["reliability_profile_id"],
        "reliability_execution_contract": protocol["execution"][
            "dedicated_runner_contract"
        ],
        "protocol": shared["dataset_protocol_schema"],
        "dataset_protocol_id": shared["dataset_protocol_id"],
        "dataset_protocol_schema": shared["dataset_protocol_schema"],
        "dataset_id": shared["dataset_id"],
        "evaluator_assignment_contract": shared[
            "evaluator_assignment_contract"
        ],
        "runtime_contract": profile["effective_runtime_contract"],
        "dynamic_protocol_id": protocol["execution"]["dynamic_protocol_id"],
        "seed": seed,
        "repeat_id": repeat_id,
        "rotation": scope["rotation"],
        "horizon": scope["windows_per_episode"],
        "arm": arm,
        "agent_id": profile["arms"][arm]["agent_id"],
        "agent_control_id": profile["arms"][arm]["agent_control_id"],
        "agent_implementation_id": profile["arms"][arm]["agent_implementation_id"],
        "p2_experiment_id": profile["p2_experiment_id"],
        "matched_control_id": profile["matched_control_id"],
        "graph_policy_profile": profile["arms"][arm]["graph_policy_profile"],
        "tasks": [scope["task_id"]],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
        "model_profile": _expected_model_profile(profile),
        "budget": profile["budget"],
        "evidence_class": scope["evidence_class"],
    }
    drift = _profile_drift(manifest, expected)
    if drift:
        raise GraphReliabilityContractError(f"manifest profile drift at {path}: {drift}")


def _validate_exact_six(leaf: Path, protocol: Mapping[str, Any]) -> None:
    expected = set(protocol["attempt_policy"]["canonical_episode_files"])
    try:
        children = list(leaf.iterdir())
    except OSError as exc:
        raise GraphReliabilityContractError(f"cannot inspect bundle {leaf}: {exc}") from exc
    observed = {item.name for item in children if item.is_file()}
    directories = [item.name for item in children if item.is_dir()]
    if observed != expected or directories:
        raise GraphReliabilityContractError(
            f"bundle is not exact-six at {leaf}: files={sorted(observed)}, "
            f"directories={sorted(directories)}"
        )


def _read_attempt(
    leaf: Path,
    protocol: Mapping[str, Any],
    *,
    repeat_id: str,
    seed: int,
    arm: str,
) -> dict[str, Any]:
    _validate_exact_six(leaf, protocol)
    run = _read_json(leaf / "run.json", "canonical run")
    metrics = _read_json(leaf / "metrics.json", "canonical metrics")
    submission = _read_json(leaf / "submission.json", "canonical submission")
    _read_json(leaf / "artifacts.json", "canonical artifacts")
    rollout_records = _read_jsonl(leaf / "rollout.jsonl", "canonical rollout")
    _read_jsonl(leaf / "failures.jsonl", "canonical failures")

    profile = protocol["profile"]
    scope = protocol["scope"]
    shared = protocol["matched_contract"]["shared"]
    metadata = _mapping(run.get("metadata"), f"run metadata {leaf}")
    expected_metadata = {
        "reliability_profile_id": profile["reliability_profile_id"],
        "reliability_execution_contract": protocol["execution"][
            "dedicated_runner_contract"
        ],
        "dataset_protocol": shared["dataset_protocol_schema"],
        "dataset_protocol_id": shared["dataset_protocol_id"],
        "dataset_protocol_schema": shared["dataset_protocol_schema"],
        "dataset_id": shared["dataset_id"],
        "evaluator_assignment_contract": shared[
            "evaluator_assignment_contract"
        ],
        "runtime_contract": profile["effective_runtime_contract"],
        "dynamic_protocol_id": protocol["execution"]["dynamic_protocol_id"],
        "model": profile["model"],
        "provider": profile["provider"],
        "inference_protocol": profile["inference_protocol"],
        "thinking_mode": profile["thinking_mode"],
        "seed": seed,
        "repeat_id": repeat_id,
        "rotation": scope["rotation"],
        "horizon": scope["windows_per_episode"],
        "arm": arm,
        "agent_control_id": profile["arms"][arm]["agent_control_id"],
        "agent_implementation_id": profile["arms"][arm]["agent_implementation_id"],
        "p2_experiment_id": profile["p2_experiment_id"],
        "matched_control_id": profile["matched_control_id"],
        "graph_policy_profile": profile["arms"][arm]["graph_policy_profile"],
        "task_id": scope["task_id"],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
    }
    drift = _profile_drift(metadata, expected_metadata)
    if drift:
        raise GraphReliabilityContractError(f"episode profile drift at {leaf}: {drift}")
    if run.get("agent_id") != profile["arms"][arm]["agent_id"]:
        raise GraphReliabilityContractError(f"agent identity drift at {leaf}")
    run_budget = _mapping(run.get("budget"), f"run budget {leaf}")
    budget_drift = {
        key: (run_budget.get(key), value)
        for key, value in profile["budget"].items()
        if run_budget.get(key) != value
    }
    if budget_drift:
        raise GraphReliabilityContractError(f"episode budget drift at {leaf}: {budget_drift}")

    sequence_id = metadata.get("public_sequence_id")
    if sequence_id not in scope["public_sequence_ids"]:
        raise GraphReliabilityContractError(
            f"unregistered public sequence at {leaf}: {sequence_id!r}"
        )
    episode_key = metadata.get("episode_key")
    if episode_key != [scope["rotation"], sequence_id, scope["task_id"]]:
        raise GraphReliabilityContractError(f"episode key drift at {leaf}")
    attempt_index = metadata.get("attempt_index")
    if type(attempt_index) is not int or attempt_index < 0:
        raise GraphReliabilityContractError(f"invalid attempt index at {leaf}")
    expected_leaf_names = (
        f"attempt_{attempt_index:03d}",
        scope["task_id"],
        str(sequence_id),
        scope["rotation"],
        "episodes",
    )
    observed_leaf_names = (
        leaf.name,
        leaf.parent.name,
        leaf.parent.parent.name,
        leaf.parent.parent.parent.name,
        leaf.parent.parent.parent.parent.name,
    )
    if observed_leaf_names != expected_leaf_names:
        raise GraphReliabilityContractError(f"canonical attempt layout drift at {leaf}")
    if metrics.get("task_id") != scope["task_id"]:
        raise GraphReliabilityContractError(f"metric task drift at {leaf}")
    if metrics.get("terminal_status") != run.get("terminal_status"):
        raise GraphReliabilityContractError(f"terminal status mismatch at {leaf}")
    rollout_metrics = _mapping(metrics.get("rollout_metrics"), f"rollout metrics {leaf}")
    task_metrics = _mapping(metrics.get("task_metrics"), f"task metrics {leaf}")
    usage = _mapping(run.get("usage", {}), f"run usage {leaf}")
    failure_kind = run.get("failure_kind")
    provider_failure = failure_kind == PROVIDER_FAILURE_KIND
    if not provider_failure:
        grounded = rollout_metrics.get("grounded_completion")
        if isinstance(grounded, bool) or grounded not in (0, 0.0, 1, 1.0):
            raise GraphReliabilityContractError(
                f"non-provider terminal lacks binary grounded completion at {leaf}"
            )
    return {
        "leaf": str(leaf),
        "repeat_id": repeat_id,
        "seed": seed,
        "rotation": scope["rotation"],
        "public_sequence_id": str(sequence_id),
        "task_id": scope["task_id"],
        "arm": arm,
        "attempt_index": attempt_index,
        "terminal_status": str(run.get("terminal_status")),
        "failure_kind": failure_kind,
        "provider_failure": provider_failure,
        "task_metrics": task_metrics,
        "rollout_metrics": rollout_metrics,
        "usage": usage,
        "submission_document": submission,
        "rollout_records": rollout_records,
    }


def collect_canonical_records(
    output_root: str | Path, protocol: Mapping[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Validate and select one non-provider terminal for every assigned unit."""

    protocol = validate_graph_reliability_protocol(protocol)
    root = Path(output_root).resolve()
    run_dirs = expected_run_directories(root, protocol)
    repeat_seed = {
        str(item["repeat_id"]): int(item["seed"])
        for item in protocol["cohort"]["repeats"]
    }
    expected_sequences = set(protocol["scope"]["public_sequence_ids"])
    records: list[dict[str, Any]] = []
    provider_attempt_count = 0
    terminal_counts: Counter[str] = Counter()
    failure_counts: Counter[str] = Counter()
    accepted_leafs: set[Path] = set()

    for (repeat_id, arm), run_dir in run_dirs.items():
        if not run_dir.is_dir():
            raise GraphReliabilityContractError(f"missing registered run directory: {run_dir}")
        _validate_manifest(
            run_dir / "run_manifest.json",
            protocol,
            repeat_id=repeat_id,
            seed=repeat_seed[repeat_id],
            arm=arm,
        )
        run_paths = sorted((run_dir / "episodes").rglob("run.json"))
        if not run_paths:
            raise GraphReliabilityContractError(f"no canonical episode bundles: {run_dir}")
        attempts_by_sequence: dict[str, list[dict[str, Any]]] = defaultdict(list)
        attempt_indexes: dict[str, set[int]] = defaultdict(set)
        for run_path in run_paths:
            attempt = _read_attempt(
                run_path.parent,
                protocol,
                repeat_id=repeat_id,
                seed=repeat_seed[repeat_id],
                arm=arm,
            )
            sequence_id = attempt["public_sequence_id"]
            if attempt["attempt_index"] in attempt_indexes[sequence_id]:
                raise GraphReliabilityContractError(
                    f"duplicate attempt index for {repeat_id}/{arm}/{sequence_id}"
                )
            attempt_indexes[sequence_id].add(attempt["attempt_index"])
            attempts_by_sequence[sequence_id].append(attempt)
            accepted_leafs.add(run_path.parent.resolve())
        if set(attempts_by_sequence) != expected_sequences:
            missing = sorted(expected_sequences - set(attempts_by_sequence))
            extra = sorted(set(attempts_by_sequence) - expected_sequences)
            raise GraphReliabilityContractError(
                f"sequence coverage mismatch at {run_dir}; missing={missing}, extra={extra}"
            )
        for sequence_id in protocol["scope"]["public_sequence_ids"]:
            attempts = attempts_by_sequence[sequence_id]
            provider_attempt_count += sum(item["provider_failure"] for item in attempts)
            selected = [item for item in attempts if not item["provider_failure"]]
            if len(selected) != 1:
                raise GraphReliabilityContractError(
                    f"{repeat_id}/{arm}/{sequence_id} has {len(selected)} non-provider "
                    "terminals; expected exactly one"
                )
            indexes = sorted(item["attempt_index"] for item in attempts)
            if indexes != list(range(len(indexes))):
                raise GraphReliabilityContractError(
                    f"{repeat_id}/{arm}/{sequence_id} attempt history is not contiguous"
                )
            record = selected[0]
            if any(
                item["provider_failure"]
                and item["attempt_index"] > record["attempt_index"]
                for item in attempts
            ):
                raise GraphReliabilityContractError(
                    f"{repeat_id}/{arm}/{sequence_id} has a provider retry after its "
                    "non-provider terminal"
                )
            records.append(record)
            terminal_counts[record["terminal_status"]] += 1
            if record["failure_kind"] is not None:
                failure_counts[str(record["failure_kind"])] += 1

    all_run_paths = sorted(root.rglob("run.json")) if root.exists() else []
    unexpected = [
        str(path.parent)
        for path in all_run_paths
        if path.parent.resolve() not in accepted_leafs
    ]
    if unexpected:
        raise GraphReliabilityContractError(
            f"unregistered run bundles under reliability root: {unexpected[:5]}"
        )

    expected_episode_count = protocol["scope"]["expected_episode_bundles_total"]
    if len(records) != expected_episode_count:
        raise GraphReliabilityContractError(
            f"selected {len(records)} episodes; expected {expected_episode_count}"
        )
    pair_keys: dict[tuple[str, int, str, str], set[str]] = defaultdict(set)
    for record in records:
        pair_keys[
            (
                record["repeat_id"],
                record["seed"],
                record["rotation"],
                record["public_sequence_id"],
            )
        ].add(record["arm"])
    if len(pair_keys) != protocol["scope"]["expected_pairs_total"] or any(
        arms != set(ARMS) for arms in pair_keys.values()
    ):
        raise GraphReliabilityContractError("Reactive-vs-Graph pairing is incomplete")

    inclusion = {
        "canonical_non_provider_terminal_count": len(records),
        "matched_pair_count": len(pair_keys),
        "retained_provider_failure_attempt_count": provider_attempt_count,
        "non_provider_failures_retained": sum(failure_counts.values()),
        "terminal_status_counts": dict(sorted(terminal_counts.items())),
        "failure_kind_counts": dict(sorted(failure_counts.items())),
    }
    return records, inclusion


def validate_graph_reliability_acceptance(
    protocol_value: Mapping[str, Any],
    acceptance_value: Mapping[str, Any],
    *,
    output_root: str | Path | None = None,
) -> dict[str, Any]:
    """Fail closed unless the report accepts this exact complete cohort."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    report = _mapping(acceptance_value, "acceptance")
    repeats = protocol["cohort"]["repeats"]
    shared = protocol["matched_contract"]["shared"]
    expected = {
        "schema_version": ACCEPTANCE_SCHEMA_VERSION,
        "accepted": True,
        "experiment_id": "P2-E9",
        "protocol_id": protocol["protocol_id"],
        "cohort_id": protocol["cohort"]["cohort_id"],
        "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
        "repeat_ids": [item["repeat_id"] for item in repeats],
        "seeds": [item["seed"] for item in repeats],
        "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
        "arms": list(ARMS),
        "rotation": protocol["scope"]["rotation"],
        "public_sequence_ids": protocol["scope"]["public_sequence_ids"],
        "expected_episode_bundles": protocol["scope"]["expected_episode_bundles_total"],
        "observed_non_provider_terminals": protocol["scope"]["expected_episode_bundles_total"],
        "expected_pairs": protocol["scope"]["expected_pairs_total"],
        "observed_pairs": protocol["scope"]["expected_pairs_total"],
        "pooling_with_three_seed_primary": "forbidden",
        "primary_results_ingested": False,
        "non_provider_failure_policy": "retain_in_denominator",
        "provider_calls_performed_by_gate": False,
        "errors": [],
        "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
        "matched_control_id": protocol["profile"]["matched_control_id"],
    }
    if output_root is not None:
        expected["output_root"] = str(Path(output_root).resolve())
    drift = _profile_drift(report, expected)
    if drift:
        raise GraphReliabilityContractError(f"acceptance report drift: {drift}")
    contract = _mapping(report.get("contract"), "acceptance.contract")
    expected_contract = {
        "dataset_protocol": shared["dataset_protocol_schema"],
        "dataset_protocol_id": shared["dataset_protocol_id"],
        "dataset_protocol_schema": shared["dataset_protocol_schema"],
        "dataset_id": shared["dataset_id"],
        "evaluator_assignment_contract": shared[
            "evaluator_assignment_contract"
        ],
        "base_runtime_contract": protocol["profile"]["base_runtime_contract"],
        "effective_runtime_contract": protocol["profile"]["effective_runtime_contract"],
        "reliability_execution_contract": protocol["execution"][
            "dedicated_runner_contract"
        ],
        "dynamic_protocol": protocol["execution"]["dynamic_protocol"],
        "dynamic_protocol_id": protocol["execution"]["dynamic_protocol_id"],
        "horizon": protocol["scope"]["windows_per_episode"],
        "provider": protocol["profile"]["provider"],
        "model": protocol["profile"]["model"],
        "inference_protocol": protocol["profile"]["inference_protocol"],
        "temperature": protocol["profile"]["temperature"],
        "max_output_tokens_per_turn": protocol["profile"]["max_output_tokens_per_turn"],
        "input_usd_per_million": float(
            protocol["profile"]["input_usd_per_million"]
        ),
        "output_usd_per_million": float(
            protocol["profile"]["output_usd_per_million"]
        ),
        "budget": protocol["profile"]["budget"],
        "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
        "matched_control_id": protocol["profile"]["matched_control_id"],
    }
    contract_drift = _profile_drift(contract, expected_contract)
    if contract_drift:
        raise GraphReliabilityContractError(
            f"accepted shared contract drift: {contract_drift}"
        )
    return report


def _payload_decisions(value: Any, *, label: str) -> list[dict[str, Any]]:
    payload = _mapping(value, label)
    decisions_value = payload.get("decisions")
    alarms_value = payload.get("alarms")
    if decisions_value is not None and alarms_value is not None:
        if decisions_value != alarms_value:
            raise GraphReliabilityContractError(
                f"{label} has conflicting decisions and alarms"
            )
        raw = decisions_value
    else:
        raw = decisions_value if decisions_value is not None else alarms_value
    if not isinstance(raw, list) or any(not isinstance(item, Mapping) for item in raw):
        raise GraphReliabilityContractError(f"{label} lacks a decision list")
    return [dict(item) for item in raw]


def _canonical_replay_decisions(record: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Project the last immutable successful submit prefix from rollout truth."""

    prefix: list[dict[str, Any]] = []
    rows = record["rollout_records"]
    if not rows or rows[-1].get("event_type") != "terminal":
        raise GraphReliabilityContractError(
            f"canonical rollout lacks its terminal event: {record['leaf']}"
        )
    terminal = rows[-1]
    if terminal.get("terminal_status") != record["terminal_status"]:
        raise GraphReliabilityContractError(
            f"canonical rollout terminal status drift: {record['leaf']}"
        )
    for row in rows[:-1]:
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
            result.get("output"), label=f"successful submit output at {record['leaf']}"
        )
        if len(observed) <= len(prefix) or observed[: len(prefix)] != prefix:
            raise GraphReliabilityContractError(
                f"canonical successful submissions rewrite their prefix: {record['leaf']}"
            )
        prefix = observed

    submission = record["submission_document"]
    submission_status = submission.get("terminal_status", submission.get("status"))
    if submission_status != record["terminal_status"]:
        raise GraphReliabilityContractError(
            f"canonical submission status drift: {record['leaf']}"
        )
    payload = submission.get("payload")
    if record["terminal_status"] == "submitted":
        final = _payload_decisions(
            payload, label=f"canonical terminal submission at {record['leaf']}"
        )
        if final != prefix:
            raise GraphReliabilityContractError(
                f"terminal submission differs from rollout submit truth: {record['leaf']}"
            )
    elif payload is not None:
        raise GraphReliabilityContractError(
            f"failed terminal unexpectedly has a submission payload: {record['leaf']}"
        )
    return prefix


def _analysis_replay_record(
    record: Mapping[str, Any], assignment: Mapping[str, Any]
) -> dict[str, Any]:
    return {
        "task_id": record["task_id"],
        "bearing_id": record["public_sequence_id"],
        "sample_ids": list(assignment["sample_ids"]),
        "private_target": dict(assignment["private_target"]),
        "replay_decisions": _canonical_replay_decisions(record),
        "submission": record["submission_document"].get("payload"),
        "evaluation": {
            "task_metrics": dict(record["task_metrics"]),
            "rollout_metrics": dict(record["rollout_metrics"]),
        },
    }


def _replay_task_summary(
    records: Sequence[Mapping[str, Any]],
    assignments: Mapping[str, Mapping[str, Any]],
) -> dict[str, float | int | None]:
    if not records:
        raise GraphReliabilityContractError("cannot summarize an empty replay cohort")
    analysis_records = [
        _analysis_replay_record(
            record, assignments[str(record["public_sequence_id"])]
        )
        for record in records
    ]
    return _replay_task_summary_from_analysis(analysis_records)


def _replay_task_summary_from_analysis(
    analysis_records: Sequence[Mapping[str, Any]],
) -> dict[str, float | int | None]:
    if not analysis_records:
        raise GraphReliabilityContractError("cannot summarize an empty replay cohort")
    expected_windows = sum(len(item["sample_ids"]) for item in analysis_records)
    try:
        summary = aggregate_results(
            analysis_records,
            replay_missing_score_policy_id=REPLAY_MISSING_SCORE_POLICY_ID,
        )["online_replay_monitoring"]
    except (KeyError, TypeError, ValueError) as exc:
        raise GraphReliabilityContractError(
            f"canonical target-adverse replay aggregation failed: {exc}"
        ) from exc
    contract = _mapping(summary.get("evaluation_contract"), "replay evaluation contract")
    if contract.get("missing_assigned_score_policy_id") != REPLAY_MISSING_SCORE_POLICY_ID:
        raise GraphReliabilityContractError("replay missing-score policy drifted")
    task = _mapping(summary.get("task"), "target-adverse replay task summary")
    if task.get("assigned_windows") != expected_windows:
        raise GraphReliabilityContractError("assigned-window denominator drifted")
    submitted = task.get("submitted_windows")
    missing = task.get("missing_assigned_scores")
    if (
        type(submitted) is not int
        or type(missing) is not int
        or submitted + missing != expected_windows
    ):
        raise GraphReliabilityContractError("replay score coverage drifted")
    return task


def _metric_value(record: Mapping[str, Any], metric: str, profile: Mapping[str, Any]) -> float | None:
    section, name = metric.split(".", 1)
    values = record["task_metrics"] if section == "task" else record["rollout_metrics"]
    usage = record["usage"]
    value: Any
    if section == "rollout" and name == "total_tokens":
        input_value = values.get("input_tokens", usage.get("input_tokens"))
        output_value = values.get("output_tokens", usage.get("output_tokens"))
        if input_value is None or output_value is None:
            return None
        value = _finite_number(input_value, f"{metric} input") + _finite_number(
            output_value, f"{metric} output"
        )
    elif section == "rollout" and name == "estimated_model_cost_usd":
        value = values.get(name)
        input_value = values.get("input_tokens", usage.get("input_tokens"))
        output_value = values.get("output_tokens", usage.get("output_tokens"))
        derived: float | None = None
        if input_value is not None and output_value is not None:
            derived = (
                _finite_number(input_value, "cost input tokens")
                * float(profile["input_usd_per_million"])
                + _finite_number(output_value, "cost output tokens")
                * float(profile["output_usd_per_million"])
            ) / 1_000_000.0
        if value is None:
            return derived
        observed = _finite_number(value, metric)
        if derived is not None and not math.isclose(
            observed, derived, rel_tol=0.0, abs_tol=1e-12
        ):
            raise GraphReliabilityContractError(
                f"canonical cost disagrees with frozen price profile: {record['leaf']}"
            )
        return observed
    else:
        value = values.get(name)
        if value is None and section == "rollout" and name in usage:
            value = usage[name]
    if value is None:
        return None
    observed = _finite_number(value, f"{metric} at {record['leaf']}")
    if section == "rollout" and name in usage and usage[name] is not None:
        usage_value = _finite_number(usage[name], f"usage.{name} at {record['leaf']}")
        if not math.isclose(observed, usage_value, rel_tol=0.0, abs_tol=1e-12):
            raise GraphReliabilityContractError(
                f"canonical metric and run usage disagree for {name}: {record['leaf']}"
            )
    return observed


def _percentile(values: Sequence[float], quantile: float) -> float:
    ordered = sorted(float(item) for item in values)
    if not ordered:
        raise GraphReliabilityContractError("cannot take percentile of no values")
    position = (len(ordered) - 1) * quantile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _interval(values: Sequence[float]) -> list[float] | None:
    if not values:
        return None
    return [_percentile(values, 0.025), _percentile(values, 0.975)]


def _variance(values: Sequence[float]) -> float | None:
    return statistics.variance(values) if len(values) >= 2 else None


def _bootstrap_metric(
    value_by_key: Mapping[tuple[str, str, str], float | None],
    *,
    repeat_ids: Sequence[str],
    sequence_ids: Sequence[str],
    arm: str | None,
    iterations: int,
    seed: int,
) -> list[float]:
    randomizer = random.Random(seed)
    draws: list[float] = []
    for _ in range(iterations):
        repeat_draw = randomizer.choices(list(repeat_ids), k=len(repeat_ids))
        sequence_draw = randomizer.choices(list(sequence_ids), k=len(sequence_ids))
        repeat_values: list[float] = []
        for repeat_id in repeat_draw:
            values: list[float] = []
            for sequence_id in sequence_draw:
                if arm is None:
                    graph = value_by_key[(repeat_id, sequence_id, "graph")]
                    reactive = value_by_key[(repeat_id, sequence_id, "reactive")]
                    if graph is not None and reactive is not None:
                        values.append(graph - reactive)
                else:
                    value = value_by_key[(repeat_id, sequence_id, arm)]
                    if value is not None:
                        values.append(value)
            if values:
                repeat_values.append(statistics.fmean(values))
        if repeat_values:
            draws.append(statistics.fmean(repeat_values))
    return draws


def _metric_report(
    value_by_key: Mapping[tuple[str, str, str], float | None],
    *,
    repeat_ids: Sequence[str],
    sequence_ids: Sequence[str],
    arm: str | None,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    repeat_estimates: dict[str, float | None] = {}
    defined_episode_count = 0
    assigned_episode_count = len(repeat_ids) * len(sequence_ids)
    for repeat_id in repeat_ids:
        values: list[float] = []
        for sequence_id in sequence_ids:
            if arm is None:
                graph = value_by_key[(repeat_id, sequence_id, "graph")]
                reactive = value_by_key[(repeat_id, sequence_id, "reactive")]
                if graph is not None and reactive is not None:
                    values.append(graph - reactive)
            else:
                value = value_by_key[(repeat_id, sequence_id, arm)]
                if value is not None:
                    values.append(value)
        defined_episode_count += len(values)
        repeat_estimates[repeat_id] = statistics.fmean(values) if values else None
    defined_repeats = [value for value in repeat_estimates.values() if value is not None]
    draws = _bootstrap_metric(
        value_by_key,
        repeat_ids=repeat_ids,
        sequence_ids=sequence_ids,
        arm=arm,
        iterations=iterations,
        seed=seed,
    )
    return {
        "status": "defined" if defined_repeats else "not_applicable",
        "mean_across_registered_repeats": (
            statistics.fmean(defined_repeats) if defined_repeats else None
        ),
        "between_repeat_variance": _variance(defined_repeats),
        "crossed_repeat_sequence_bootstrap_95ci": _interval(draws),
        "repeat_estimates": repeat_estimates,
        "defined_repeat_numerator": len(defined_repeats),
        "registered_repeat_denominator": len(repeat_ids),
        "defined_episode_numerator": defined_episode_count,
        "assigned_episode_denominator": assigned_episode_count,
        "bootstrap_valid_replicates": len(draws),
        "bootstrap_replicate_denominator": iterations,
        "missing_values_imputed_as_zero": False,
    }


def _task_ap_value(rows: Sequence[Mapping[str, Any]]) -> float | None:
    value = _replay_task_summary_from_analysis(rows).get("average_precision")
    return None if value is None else _finite_number(value, PRIMARY_METRIC)


def _selected_analysis_rows(
    analysis_by_key: Mapping[tuple[str, str, str], Mapping[str, Any]],
    *,
    repeat_id: str,
    arm: str,
    sequence_ids: Sequence[str],
) -> list[Mapping[str, Any]]:
    return [
        analysis_by_key[(repeat_id, sequence_id, arm)]
        for sequence_id in sequence_ids
    ]


def _task_primary_report(
    analysis_by_key: Mapping[tuple[str, str, str], Mapping[str, Any]],
    *,
    repeat_ids: Sequence[str],
    sequence_ids: Sequence[str],
    arm: str | None,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    first_row = next(iter(analysis_by_key.values()), None)
    if first_row is None:
        raise GraphReliabilityContractError("primary analysis has no registered rows")
    windows_per_episode = len(first_row["sample_ids"])
    repeat_estimates: dict[str, float | None] = {}
    for repeat_id in repeat_ids:
        if arm is None:
            graph = _task_ap_value(
                _selected_analysis_rows(
                    analysis_by_key,
                    repeat_id=repeat_id,
                    arm="graph",
                    sequence_ids=sequence_ids,
                )
            )
            reactive = _task_ap_value(
                _selected_analysis_rows(
                    analysis_by_key,
                    repeat_id=repeat_id,
                    arm="reactive",
                    sequence_ids=sequence_ids,
                )
            )
            repeat_estimates[repeat_id] = (
                None if graph is None or reactive is None else graph - reactive
            )
        else:
            repeat_estimates[repeat_id] = _task_ap_value(
                _selected_analysis_rows(
                    analysis_by_key,
                    repeat_id=repeat_id,
                    arm=arm,
                    sequence_ids=sequence_ids,
                )
            )

    rng = random.Random(seed)
    draws: list[float] = []
    for _ in range(iterations):
        repeat_draw = rng.choices(list(repeat_ids), k=len(repeat_ids))
        sequence_draw = rng.choices(list(sequence_ids), k=len(sequence_ids))
        repeat_values: list[float] = []
        for repeat_id in repeat_draw:
            if arm is None:
                graph = _task_ap_value(
                    _selected_analysis_rows(
                        analysis_by_key,
                        repeat_id=repeat_id,
                        arm="graph",
                        sequence_ids=sequence_draw,
                    )
                )
                reactive = _task_ap_value(
                    _selected_analysis_rows(
                        analysis_by_key,
                        repeat_id=repeat_id,
                        arm="reactive",
                        sequence_ids=sequence_draw,
                    )
                )
                if graph is not None and reactive is not None:
                    repeat_values.append(graph - reactive)
            else:
                value = _task_ap_value(
                    _selected_analysis_rows(
                        analysis_by_key,
                        repeat_id=repeat_id,
                        arm=arm,
                        sequence_ids=sequence_draw,
                    )
                )
                if value is not None:
                    repeat_values.append(value)
        if repeat_values:
            draws.append(statistics.fmean(repeat_values))

    defined = [value for value in repeat_estimates.values() if value is not None]
    report: dict[str, Any] = {
        "status": "defined" if defined else "not_applicable",
        "role": "primary_task_outcome",
        "mean_across_registered_repeats": (
            statistics.fmean(defined) if defined else None
        ),
        "between_repeat_variance": _variance(defined),
        "crossed_repeat_sequence_bootstrap_95ci": _interval(draws),
        "repeat_estimates": repeat_estimates,
        "defined_repeat_numerator": len(defined),
        "registered_repeat_denominator": len(repeat_ids),
        "assigned_episode_denominator": len(repeat_ids) * len(sequence_ids),
        "assigned_window_denominator_per_arm": (
            len(repeat_ids)
            * len(sequence_ids)
            * windows_per_episode
        ),
        "bootstrap_valid_replicates": len(draws),
        "bootstrap_replicate_denominator": iterations,
        "aggregation": (
            "recompute_target_adverse_AP_over_all_24_assigned_windows_within_"
            "each_repeat_then_equal_weight_repeats"
        ),
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "per_sequence_average_precision_averaging_performed": False,
        "derived_evaluation_jsonl_ingested": False,
        "missing_values_imputed_as_zero": False,
    }
    if arm is not None:
        all_rows = [
            analysis_by_key[(repeat_id, sequence_id, arm)]
            for repeat_id in repeat_ids
            for sequence_id in sequence_ids
        ]
        coverage = _replay_task_summary_from_analysis(all_rows)
        report.update(
            {
                "submitted_window_numerator": coverage["submitted_windows"],
                "missing_assigned_scores": coverage["missing_assigned_scores"],
                "score_coverage": coverage["score_coverage"],
            }
        )
    return report


def _pass_all_report(
    pass_by_key: Mapping[tuple[str, str, str], int],
    *,
    repeat_ids: Sequence[str],
    sequence_ids: Sequence[str],
    arm: str,
    iterations: int,
    seed: int,
) -> dict[str, Any]:
    outcomes = {
        sequence_id: int(
            all(pass_by_key[(repeat_id, sequence_id, arm)] for repeat_id in repeat_ids)
        )
        for sequence_id in sequence_ids
    }
    randomizer = random.Random(seed)
    draws = [
        statistics.fmean(
            outcomes[item]
            for item in randomizer.choices(list(sequence_ids), k=len(sequence_ids))
        )
        for _ in range(iterations)
    ]
    numerator = sum(outcomes.values())
    return {
        "numerator": numerator,
        "denominator": len(sequence_ids),
        "estimate": numerator / len(sequence_ids),
        "required_repeats_per_base_sequence": len(repeat_ids),
        "assigned_repeat_episode_denominator": len(repeat_ids) * len(sequence_ids),
        "sequence_cluster_bootstrap_95ci": _interval(draws),
        "bootstrap_valid_replicates": len(draws),
        "bootstrap_replicate_denominator": iterations,
        "between_repeat_variance": None,
        "between_repeat_variance_reason": "not_applicable_to_joint_all_10_endpoint",
    }


def analyze_graph_reliability(
    output_root: str | Path,
    protocol_value: Mapping[str, Any],
    acceptance_value: Mapping[str, Any],
    *,
    private_replay_assignments: Mapping[str, Any],
) -> dict[str, Any]:
    """Analyze the complete accepted P2-E9 cohort without calling a provider."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    acceptance = validate_graph_reliability_acceptance(
        protocol, acceptance_value, output_root=output_root
    )
    records, inclusion = collect_canonical_records(output_root, protocol)
    if acceptance.get("canonical_inclusion") != inclusion:
        raise GraphReliabilityContractError(
            "canonical cohort changed after acceptance or inclusion report drifted"
        )
    assignments = _validate_private_replay_assignments(
        private_replay_assignments, protocol
    )

    repeat_ids = [str(item["repeat_id"]) for item in protocol["cohort"]["repeats"]]
    sequence_ids = list(protocol["scope"]["public_sequence_ids"])
    metrics = [*protocol["metrics"]["task"], *protocol["metrics"]["rollout"]]
    profile = protocol["profile"]
    iterations = int(protocol["statistics"]["bootstrap"]["iterations"])
    bootstrap_seed = int(protocol["statistics"]["bootstrap"]["seed"])
    record_by_key = {
        (record["repeat_id"], record["public_sequence_id"], record["arm"]): record
        for record in records
    }
    analysis_by_key = {
        key: _analysis_replay_record(
            record, assignments[str(record["public_sequence_id"])]
        )
        for key, record in record_by_key.items()
    }
    value_by_metric: dict[str, dict[tuple[str, str, str], float | None]] = {}
    for metric in metrics:
        value_by_metric[metric] = (
            {key: None for key in record_by_key}
            if metric == PRIMARY_METRIC
            else {
                key: _metric_value(record, metric, profile)
                for key, record in record_by_key.items()
            }
        )
    pass_by_key = {
        key: int(value_by_metric["rollout.grounded_completion"][key] == 1.0)
        for key in record_by_key
    }

    arm_results: dict[str, Any] = {}
    for arm_index, arm in enumerate(ARMS):
        arm_records = [record for record in records if record["arm"] == arm]
        metric_reports = {
            metric: _metric_report(
                values,
                repeat_ids=repeat_ids,
                sequence_ids=sequence_ids,
                arm=arm,
                iterations=iterations,
                seed=bootstrap_seed + metric_index * 17 + arm_index,
            )
            for metric_index, (metric, values) in enumerate(value_by_metric.items())
        }
        metric_reports[PRIMARY_METRIC] = _task_primary_report(
            analysis_by_key,
            repeat_ids=repeat_ids,
            sequence_ids=sequence_ids,
            arm=arm,
            iterations=iterations,
            seed=bootstrap_seed + 700 + arm_index,
        )
        pass_values = [pass_by_key[key] for key in pass_by_key if key[2] == arm]
        pass_at_1_report = metric_reports["rollout.grounded_completion"]
        pass_all_report = _pass_all_report(
            pass_by_key,
            repeat_ids=repeat_ids,
            sequence_ids=sequence_ids,
            arm=arm,
            iterations=iterations,
            seed=bootstrap_seed + 1000 + arm_index,
        )
        failures = Counter(
            str(record["failure_kind"])
            for record in arm_records
            if record["failure_kind"] is not None
        )
        terminals = Counter(str(record["terminal_status"]) for record in arm_records)
        arm_results[arm] = {
            "assigned_episode_denominator": len(arm_records),
            "registered_repeat_denominator": len(repeat_ids),
            "base_sequence_denominator": len(sequence_ids),
            "terminal_status_counts": dict(sorted(terminals.items())),
            "failure_kind_counts": dict(sorted(failures.items())),
            "metrics": metric_reports,
            "reliability": {
                "pass_definition": protocol["pass_rule"],
                "pass_at_1": {
                    "numerator": sum(pass_values),
                    "denominator": len(pass_values),
                    "estimate": sum(pass_values) / len(pass_values),
                    "mean_across_registered_repeats": pass_at_1_report[
                        "mean_across_registered_repeats"
                    ],
                    "between_repeat_variance": pass_at_1_report[
                        "between_repeat_variance"
                    ],
                    "crossed_repeat_sequence_bootstrap_95ci": pass_at_1_report[
                        "crossed_repeat_sequence_bootstrap_95ci"
                    ],
                    "bootstrap_valid_replicates": pass_at_1_report[
                        "bootstrap_valid_replicates"
                    ],
                    "bootstrap_replicate_denominator": iterations,
                },
                "pass_all_10": pass_all_report,
            },
            "cost": {
                metric: metric_reports[metric]
                for metric in protocol["metrics"]["cost_metrics"]
            },
        }

    paired_metrics = {
        metric: _metric_report(
            values,
            repeat_ids=repeat_ids,
            sequence_ids=sequence_ids,
            arm=None,
            iterations=iterations,
            seed=bootstrap_seed + metric_index * 17 + 2,
        )
        for metric_index, (metric, values) in enumerate(value_by_metric.items())
    }
    paired_metrics[PRIMARY_METRIC] = _task_primary_report(
        analysis_by_key,
        repeat_ids=repeat_ids,
        sequence_ids=sequence_ids,
        arm=None,
        iterations=iterations,
        seed=bootstrap_seed + 702,
    )
    graph_all = arm_results["graph"]["reliability"]["pass_all_10"]
    reactive_all = arm_results["reactive"]["reliability"]["pass_all_10"]
    graph_all_by_sequence = {
        sequence_id: int(
            all(pass_by_key[(repeat_id, sequence_id, "graph")] for repeat_id in repeat_ids)
        )
        for sequence_id in sequence_ids
    }
    reactive_all_by_sequence = {
        sequence_id: int(
            all(
                pass_by_key[(repeat_id, sequence_id, "reactive")]
                for repeat_id in repeat_ids
            )
        )
        for sequence_id in sequence_ids
    }
    all_differences = {
        sequence_id: graph_all_by_sequence[sequence_id]
        - reactive_all_by_sequence[sequence_id]
        for sequence_id in sequence_ids
    }
    all_randomizer = random.Random(bootstrap_seed + 2000)
    all_delta_draws = [
        statistics.fmean(
            all_differences[item]
            for item in all_randomizer.choices(sequence_ids, k=len(sequence_ids))
        )
        for _ in range(iterations)
    ]
    grounded_paired = paired_metrics["rollout.grounded_completion"]
    primary_paired = paired_metrics[PRIMARY_METRIC]
    result = {
        "schema_version": RESULT_SCHEMA_VERSION,
        "status": "accepted_complete_cohort_analysis",
        "experiment_id": "P2-E9",
        "protocol_id": protocol["protocol_id"],
        "cohort_id": protocol["cohort"]["cohort_id"],
        "reliability_profile_id": profile["reliability_profile_id"],
        "p2_experiment_id": profile["p2_experiment_id"],
        "matched_control_id": profile["matched_control_id"],
        "output_root": str(Path(output_root).resolve()),
        "provider_calls_performed_by_analyzer": False,
        "primary_endpoint": {
            "metric": PRIMARY_METRIC,
            "role": "task_primary",
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "private_target_authority": "registered_private_data_port_assignment",
            "prediction_authority": "canonical_rollout_successful_submit_prefix",
            "derived_evaluation_jsonl_ingested": False,
        },
        "cohort": {
            "repeat_ids": repeat_ids,
            "seeds": [item["seed"] for item in protocol["cohort"]["repeats"]],
            "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
            "primary_results_ingested": False,
            "pooling_with_three_seed_primary": "forbidden",
            "assigned_episode_denominator": len(records),
            "matched_pair_denominator": protocol["scope"]["expected_pairs_total"],
        },
        "canonical_inclusion": inclusion,
        "arms": arm_results,
        "paired_graph_minus_reactive": {
            "paired_unit": protocol["matched_contract"]["paired_unit"],
            "metrics": paired_metrics,
            "primary_task_outcome": {
                "metric": PRIMARY_METRIC,
                "estimate": primary_paired["mean_across_registered_repeats"],
                "between_repeat_variance": primary_paired[
                    "between_repeat_variance"
                ],
                "crossed_repeat_sequence_bootstrap_95ci": primary_paired[
                    "crossed_repeat_sequence_bootstrap_95ci"
                ],
                "defined_repeat_numerator": primary_paired[
                    "defined_repeat_numerator"
                ],
                "registered_repeat_denominator": len(repeat_ids),
                "assigned_pair_denominator": protocol["scope"][
                    "expected_pairs_total"
                ],
                "assigned_window_denominator_per_arm": primary_paired[
                    "assigned_window_denominator_per_arm"
                ],
                "bootstrap_valid_replicates": primary_paired[
                    "bootstrap_valid_replicates"
                ],
                "bootstrap_replicate_denominator": iterations,
            },
            "pass_at_1_delta": {
                "role": "explanatory_rollout_reliability",
                "estimate": grounded_paired["mean_across_registered_repeats"],
                "between_repeat_variance": grounded_paired["between_repeat_variance"],
                "crossed_repeat_sequence_bootstrap_95ci": grounded_paired[
                    "crossed_repeat_sequence_bootstrap_95ci"
                ],
                "defined_pair_numerator": grounded_paired["defined_episode_numerator"],
                "assigned_pair_denominator": protocol["scope"]["expected_pairs_total"],
                "bootstrap_valid_replicates": grounded_paired[
                    "bootstrap_valid_replicates"
                ],
                "bootstrap_replicate_denominator": iterations,
            },
            "pass_all_10_delta": {
                "estimate": graph_all["estimate"] - reactive_all["estimate"],
                "sequence_cluster_bootstrap_95ci": _interval(all_delta_draws),
                "sequence_denominator": len(sequence_ids),
                "bootstrap_valid_replicates": len(all_delta_draws),
                "bootstrap_replicate_denominator": iterations,
            },
        },
        "claim_boundary": protocol["claim_boundary"],
    }
    return result


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze an accepted complete P2-E9 Graph reliability cohort; "
            "this command never calls a provider."
        )
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument(
        "--dataset-protocol", type=Path, default=DEFAULT_DATASET_PROTOCOL
    )
    parser.add_argument(
        "--dynamic-protocol", type=Path, default=DEFAULT_DYNAMIC_PROTOCOL
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--acceptance", type=Path, required=True)
    parser.add_argument("--private-metadata-env", required=True, metavar="ENV_NAME")
    parser.add_argument("--private-signal-env", required=True, metavar="ENV_NAME")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    protocol = load_graph_reliability_protocol(args.protocol)
    acceptance = _read_json(args.acceptance, "acceptance report")
    assignments = build_private_replay_assignments(
        protocol,
        dataset_protocol_path=args.dataset_protocol,
        dynamic_protocol_path=args.dynamic_protocol,
        metadata_path=_private_path(
            args.private_metadata_env, label="private metadata"
        ),
        signal_path=_private_path(args.private_signal_env, label="private signal"),
    )
    result = analyze_graph_reliability(
        args.output_root,
        protocol,
        acceptance,
        private_replay_assignments=assignments,
    )
    if args.output is not None:
        _write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
