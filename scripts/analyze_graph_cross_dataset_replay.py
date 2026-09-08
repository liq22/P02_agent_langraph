#!/usr/bin/env python3
"""Accept and analyze the matched Ottawa Paper-2 P2-E8 cohort.

The analyzer is provider-free. It accepts only complete canonical cohorts,
reconstructs evaluator-private assignments from the registered CSV DataPort,
recomputes target-adverse metrics, verifies exact Reactive/Graph episode
pairing, and then performs the preregistered bearing-clustered bootstrap.
"""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
import json
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


def _benchmark_root() -> Path:
    for name in ("p01-phm-agent-benchmark", "P01-phm-agent-benchmark"):
        candidate = ROOT.parent / name
        if candidate.is_dir():
            return candidate
    return ROOT.parent / "p01-phm-agent-benchmark"


BENCHMARK_ROOT = _benchmark_root()
for source_root in (
    BENCHMARK_ROOT / "src",
    BENCHMARK_ROOT / "src/phm_data_factory/src",
):
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

from phm_agent_benchmark.phase1 import LocalCSVPhase1DataPort  # noqa: E402
from phm_agent_benchmark.phase1.cohort import (  # noqa: E402
    validate_cohort_index,
    validate_formal_cohort,
)
from phm_agent_benchmark.phase1.experiment import (  # noqa: E402
    aggregate_results,
    bearing_bootstrap_intervals,
    build_evaluator_assignments,
    paired_bearing_bootstrap_deltas,
    require_formal_replay_metric_lock,
)

try:  # Executed as a script or imported as scripts.* in tests.
    from schedule_graph_cross_dataset_replay import (
        DATASET_ID,
        DEFAULT_PROTOCOL,
        PROFILE_ID,
        PROTOCOL_ID,
        PROTOCOL_SCHEMA,
        RUNTIME_CONTRACT,
        load_protocol,
        validate_protocol,
    )
except ModuleNotFoundError:  # pragma: no cover - import route only
    from scripts.schedule_graph_cross_dataset_replay import (
        DATASET_ID,
        DEFAULT_PROTOCOL,
        PROFILE_ID,
        PROTOCOL_ID,
        PROTOCOL_SCHEMA,
        RUNTIME_CONTRACT,
        load_protocol,
        validate_protocol,
    )


RESULT_SCHEMA = "p2_e8_ottawa_generic_base_result_v2"
TASK_ID = "online_replay_monitoring"
REPLAY_POLICY_ID = "phase1_replay_target_adverse_missing_score_v1"
FORMAL_STAMP = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
SAFE_ENVIRONMENT_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
ARM_IDENTITIES = {
    "reactive": {
        "agent": "reactive",
        "agent_id": "reactive-sequential-agent",
        "agent_profile_id": "reactive_sequential_generic_v2",
        "agent_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_implementation_id": "reactive_sequential_agent_v1",
        "graph_policy_profile": "reactive",
    },
    "graph": {
        "agent": "graph",
        "agent_id": "graph-decision-agent",
        "agent_profile_id": "graph_dynamic_full_generic_v2",
        "agent_control_id": "graph_decision_control_v1",
        "agent_implementation_id": "graph_decision_agent_v1",
        "graph_policy_profile": "full",
    },
}


class CrossDatasetAnalysisError(RuntimeError):
    """Raised before any result is emitted when accepted evidence is absent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CrossDatasetAnalysisError(message)


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be a mapping")
    return value


def _list(value: object, label: str) -> list[Any]:
    _require(isinstance(value, list), f"{label} must be a list")
    return value


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CrossDatasetAnalysisError(f"cannot load {label}: {exc}") from exc
    _require(isinstance(value, dict), f"{label} root must be a mapping")
    return value


def _lexical_path(path: Path) -> Path:
    """Normalize without discarding the final path-component identity."""

    return Path(os.path.abspath(os.fspath(path)))


def _path_is_strictly_within(path: Path, root: Path) -> bool:
    """Require both lexical and resolved containment."""

    try:
        _lexical_path(path).relative_to(_lexical_path(root))
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    except (OSError, RuntimeError) as exc:
        raise CrossDatasetAnalysisError(
            f"cannot resolve production path boundary for {path}"
        ) from exc
    return True


def _require_exact_path(observed: Path, expected: Path, label: str) -> None:
    try:
        resolved_equal = observed.resolve(strict=False) == expected.resolve(
            strict=False
        )
    except (OSError, RuntimeError) as exc:
        raise CrossDatasetAnalysisError(f"cannot resolve {label}: {observed}") from exc
    _require(
        _lexical_path(observed) == _lexical_path(expected) and resolved_equal,
        f"{label} must match the registered path exactly",
    )


def _require_ordinary_single_link(
    path: Path, *, label: str, required: bool
) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        _require(not required, f"missing {label}: {path}")
        return
    except OSError as exc:
        raise CrossDatasetAnalysisError(f"cannot inspect {label}: {path}") from exc
    _require(
        stat.S_ISREG(metadata.st_mode) and metadata.st_nlink == 1,
        f"{label} must be an ordinary single-link regular file: {path}",
    )


def _protocol_source_paths(protocol_path: Path) -> list[Path]:
    """Return every lexical sibling in the protocol extension chain."""

    sources: list[Path] = []
    current = _lexical_path(protocol_path)
    seen: set[Path] = set()
    while True:
        _require(
            current not in seen,
            "P2-E8 protocol authority chain contains a cycle",
        )
        seen.add(current)
        _require_ordinary_single_link(
            current,
            label="P2-E8 protocol authority source",
            required=True,
        )
        sources.append(current)
        try:
            payload = yaml.safe_load(current.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise CrossDatasetAnalysisError(
                f"cannot inspect P2-E8 protocol authority chain: {current}"
            ) from exc
        _require(isinstance(payload, Mapping), f"protocol must be a mapping: {current}")
        extension = payload.get("extends_protocol")
        if extension is None:
            return sources
        _require(
            isinstance(extension, str)
            and bool(extension)
            and Path(extension).name == extension,
            "P2-E8 protocol extension must name one sibling authority",
        )
        current = _lexical_path(current.parent / extension)


def _registered_path(value: object, label: str) -> Path:
    _require(isinstance(value, str) and bool(value), f"{label} is required")
    relative = Path(value)
    _require(not relative.is_absolute(), f"{label} must be repository-relative")
    return _lexical_path(ROOT / relative)


def _validate_production_cli_paths(
    *,
    protocol_path: Path,
    dataset_protocol_path: Path | None,
    output_path: Path,
) -> Path:
    """Bind the production CLI to registered authorities before private reads."""

    _require_exact_path(protocol_path, DEFAULT_PROTOCOL, "P2-E8 protocol")
    protocol_sources = _protocol_source_paths(protocol_path)
    for source in protocol_sources:
        _require(
            _path_is_strictly_within(source, ROOT),
            f"P2-E8 protocol source resolves outside the repository: {source}",
        )

    cross = load_protocol(protocol_path)
    validate_protocol(cross)
    analysis = _validate_analysis_registration(cross)

    registered_dataset = _registered_path(
        _mapping(cross.get("dataset_registration"), "dataset_registration").get(
            "protocol_path"
        ),
        "dataset_registration.protocol_path",
    )
    _require(
        _path_is_strictly_within(registered_dataset, BENCHMARK_ROOT),
        "registered Ottawa dataset protocol must remain inside the Benchmark root",
    )
    supplied_dataset = dataset_protocol_path or registered_dataset
    _require_exact_path(
        supplied_dataset,
        registered_dataset,
        "Ottawa dataset protocol",
    )
    _require_ordinary_single_link(
        registered_dataset,
        label="registered Ottawa dataset protocol",
        required=True,
    )

    results_root = _registered_path(
        analysis.get("results_root"), "analysis_gate.results_root"
    )
    formal_result = _registered_path(
        analysis.get("formal_result"), "analysis_gate.formal_result"
    )
    _require(
        _path_is_strictly_within(results_root, ROOT),
        "registered P2-E8 results root resolves outside the repository",
    )
    _require(
        _path_is_strictly_within(formal_result, results_root),
        "registered P2-E8 formal result must remain inside results_root",
    )
    _require_exact_path(output_path, formal_result, "P2-E8 output")
    _require(
        _path_is_strictly_within(output_path.parent, results_root),
        "P2-E8 output parent resolves outside results_root",
    )
    _require_ordinary_single_link(
        output_path,
        label="existing P2-E8 output",
        required=False,
    )
    return registered_dataset


def _validate_analysis_registration(cross: Mapping[str, Any]) -> Mapping[str, Any]:
    analysis = _mapping(cross.get("analysis_gate"), "analysis_gate")
    _require(
        analysis.get("result_schema") == RESULT_SCHEMA,
        "P2-E8 result schema registration drifted",
    )
    accepted = _mapping(
        analysis.get("accepted_input_contract"),
        "analysis_gate.accepted_input_contract",
    )
    expected_accepted = {
        "runs_per_arm": 9,
        "episode_bundles_per_arm": 36,
        "assigned_windows_per_arm": 108,
        "exact_matched_episode_pairs": 36,
        "canonical_attempt_contract": "exact_six",
        "registered_evidence_class": "formal",
        "result_role": "confirmatory",
        "nonprovider_terminal_failures": "retained_in_denominator",
        "unresolved_provider_errors": "reject_cohort",
        "partial_prefix_aggregation": "forbidden",
    }
    _require(dict(accepted) == expected_accepted, "accepted-input contract drifted")
    statistics = _mapping(analysis.get("statistics"), "analysis_gate.statistics")
    expected_statistics = {
        "direction": "graph_minus_reactive",
        "primary_endpoint": "online_replay_monitoring.task.average_precision",
        "secondary_task_endpoints": [
            "online_replay_monitoring.task.auroc",
            "online_replay_monitoring.task.false_alarm_rate",
            "online_replay_monitoring.task.true_positive_rate",
            "online_replay_monitoring.task.score_coverage",
        ],
        "interval_method": "paired_bearing_cluster_percentile_bootstrap_with_metric_recomputation",
        "cluster_unit": "physical_bearing",
        "iterations": 2000,
        "seed": 20260902,
    }
    _require(dict(statistics) == expected_statistics, "P2-E8 statistics drifted")
    return analysis


def _dataset_protocol_path(cross: Mapping[str, Any]) -> Path:
    registration = _mapping(cross.get("dataset_registration"), "dataset_registration")
    value = registration.get("protocol_path")
    _require(isinstance(value, str) and value, "dataset protocol path is required")
    path = (ROOT / value).resolve()
    _require(path.is_file(), f"dataset protocol is missing: {path}")
    return path


def _environment_path(name: object, label: str) -> Path:
    _require(
        isinstance(name, str) and SAFE_ENVIRONMENT_NAME.fullmatch(name) is not None,
        f"{label} environment name is invalid",
    )
    value = os.environ.get(name)
    _require(bool(value), f"missing configured data environment variable: {name}")
    path = Path(str(value)).expanduser().resolve()
    _require(
        not path.is_relative_to(ROOT),
        f"private {label} must remain outside the Paper-2 repository",
    )
    return path


@contextmanager
def _open_private_data(
    cross: Mapping[str, Any],
    dataset: Mapping[str, Any],
) -> Iterator[LocalCSVPhase1DataPort]:
    registration = _mapping(cross["dataset_registration"], "dataset_registration")
    metadata = _environment_path(registration["metadata_environment"], "metadata")
    signals = _environment_path(registration["signal_environment"], "signal root")
    readiness_path = _environment_path(
        registration["readiness_environment"], "readiness report"
    )
    try:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CrossDatasetAnalysisError("cannot read the Ottawa readiness report") from exc
    _require(isinstance(readiness, Mapping), "Ottawa readiness report must be a mapping")

    dataset_registration = _mapping(dataset.get("dataset"), "dataset.dataset")
    window = _mapping(dataset.get("window_protocol"), "dataset.window_protocol")
    activation = _mapping(dataset.get("activation_gate"), "dataset.activation_gate")
    value_columns = _list(window.get("value_columns"), "window value columns")
    source_columns = _list(window.get("source_columns"), "window source columns")
    expected_records = int(dataset_registration["records"])
    expected_readiness: dict[str, Any] = {
        "schema_version": activation["readiness_report_schema"],
        "dataset_id": DATASET_ID,
        "records": expected_records,
        "value_columns": value_columns,
        "source_columns": source_columns,
        "sample_rate_hz": int(dataset_registration["sample_rate_hz"]),
        "sample_length": int(dataset_registration["sample_length"]),
        "channels": int(dataset_registration["channels_per_record"]),
        "signals_validated": expected_records,
        "data_port_ready": True,
    }
    if window.get("segment_start_field") is not None:
        expected_readiness["segment_start_field"] = window["segment_start_field"]
    _require(
        {key: readiness.get(key) for key in expected_readiness}
        == expected_readiness,
        "Ottawa readiness report does not prove the complete CSV inventory",
    )
    required_values = _mapping(
        activation.get("required_report_values"),
        "activation_gate.required_report_values",
    )
    _require(
        {str(key): readiness.get(str(key)) for key in required_values}
        == dict(required_values),
        "Ottawa readiness report differs from the activation contract",
    )

    port = LocalCSVPhase1DataPort(
        metadata,
        signals,
        value_columns=value_columns,
        source_columns=source_columns,
        segment_start_field=window.get("segment_start_field"),
        dataset_name=str(dataset_registration["provider_name"]),
        default_max_points=int(window["max_returned_points"]),
        public_id_seed=int(dataset["agent_visibility"]["sample_handle"]["seed"]),
    )
    try:
        rows = port.search_samples({}, expected_records + 1)
        _require(len(rows) == expected_records, "Ottawa DataPort inventory is incomplete")
        yield port
    finally:
        port.close()


def _validate_root_layout(reactive_root: Path, graph_root: Path) -> str:
    reactive = reactive_root.resolve()
    graph = graph_root.resolve()
    _require(reactive.name == "reactive", "Reactive root must end in /reactive")
    _require(graph.name == "graph", "Graph root must end in /graph")
    _require(reactive.parent == graph.parent, "Reactive and Graph roots must share one run root")
    run_name = reactive.parent.name
    _require(run_name.startswith("run_"), "P2-E8 run root must start with run_")
    stamp = run_name.removeprefix("run_")
    _require(FORMAL_STAMP.fullmatch(stamp) is not None, "formal run stamp must match YYYYMMDDTHHMMSSZ")
    return stamp


def _validate_registered_root_layout(
    reactive_root: Path,
    graph_root: Path,
    cross: Mapping[str, Any],
) -> tuple[str, Path]:
    """Bind the accepted arm roots to the protocol base and stamped run root."""

    stamp = _validate_root_layout(reactive_root, graph_root)
    current = _mapping(cross.get("current_schedule"), "current_schedule")
    declared_output_root = Path(str(current.get("output_root", "")))
    _require(str(declared_output_root) not in {"", "."}, "P2-E8 output root is required")
    if not declared_output_root.is_absolute():
        declared_output_root = ROOT / declared_output_root
    expected_run_root = (
        declared_output_root / f"run_{stamp}"
    ).resolve(strict=False)
    formal_run_root = reactive_root.resolve().parent
    _require(
        formal_run_root == expected_run_root,
        "P2-E8 accepted cohort root differs from current_schedule.output_root and stamp",
    )
    return stamp, formal_run_root


def _expected_run_dirs(
    arm_root: Path,
    *,
    seeds: Sequence[int],
    rotations: Sequence[str],
) -> list[Path]:
    expected = [
        arm_root / f"seed_{seed}" / rotation
        for seed in seeds
        for rotation in rotations
    ]
    observed = {
        path.parent.resolve()
        for path in arm_root.rglob("cohort_index.json")
        if path.is_file()
    } if arm_root.is_dir() else set()
    expected_set = {path.resolve() for path in expected}
    _require(observed == expected_set, f"{arm_root.name} cohort-index topology is not exact 9/9")
    return expected


def _profile_expected(
    cross: Mapping[str, Any],
    dataset: Mapping[str, Any],
    arm: str,
) -> dict[str, Any]:
    formal = cross["formal_execution"]
    registration = cross["dataset_registration"]
    identity = ARM_IDENTITIES[arm]
    return {
        "protocol": dataset["schema_version"],
        "dataset_protocol_id": dataset["protocol_id"],
        "dataset_protocol_schema": dataset["schema_version"],
        "runtime": formal["runtime"],
        "runtime_contract": formal["runtime_contract"],
        "model": formal["model_id"],
        "provider": formal["provider_label"],
        "inference_protocol": formal["inference_protocol"],
        "thinking_mode": formal["thinking_mode"],
        "temperature": formal["temperature"],
        "max_output_tokens_per_turn": formal["max_output_tokens_per_turn"],
        "model_profile": {
            "provider": formal["provider_label"],
            "model_id": formal["model_id"],
            "protocol": formal["inference_protocol"],
            "input_usd_per_million": formal["input_usd_per_million"],
            "output_usd_per_million": formal["output_usd_per_million"],
        },
        "registered_evidence_class": formal["registered_evidence_class"],
        "result_role": formal["result_role"],
        "experiment_profile_id": formal["experiment_profile_id"],
        "tasks": [registration["task"]],
        "data_backend": registration["data_backend"],
        "cross_dataset_protocol_schema": PROTOCOL_SCHEMA,
        "cross_dataset_protocol_id": PROTOCOL_ID,
        "data_binding": {
            "metadata_environment": registration["metadata_environment"],
            "signal_environment": registration["signal_environment"],
            "readiness_environment": registration["readiness_environment"],
        },
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        **identity,
    }


def _validate_arm_profiles(
    run_dirs: Sequence[Path],
    *,
    cross: Mapping[str, Any],
    dataset: Mapping[str, Any],
    arm: str,
) -> None:
    expected = _profile_expected(cross, dataset, arm)
    for run_dir in run_dirs:
        document = validate_cohort_index(run_dir / "cohort_index.json")
        profile = _mapping(document.get("profile"), f"{run_dir} profile")
        drift = {
            key: {"expected": value, "observed": profile.get(key)}
            for key, value in expected.items()
            if profile.get(key) != value
        }
        _require(not drift, f"{arm} formal profile drift at {run_dir}: {drift}")
        _require("benchmark_control_source" not in profile, "P2-E8 must not bind a Paderborn control root")


def _validate_matched_reports(
    reactive: Mapping[str, Any],
    graph: Mapping[str, Any],
) -> None:
    _require(reactive.get("accepted") is True, "Reactive accepted-cohort gate failed")
    _require(graph.get("accepted") is True, "Graph accepted-cohort gate failed")
    left = dict(_mapping(reactive.get("contract"), "Reactive cohort contract"))
    right = dict(_mapping(graph.get("contract"), "Graph cohort contract"))
    for field in ("agent", "agent_id"):
        left.pop(field, None)
        right.pop(field, None)
    _require(left == right, "Reactive and Graph data/model/runtime worlds differ")
    _require(
        reactive.get("run_contracts") == graph.get("run_contracts"),
        "Reactive and Graph numerical model selections differ",
    )


def _trusted_arm_records(
    run_dirs: Sequence[Path],
    *,
    private_data: LocalCSVPhase1DataPort,
    dataset: Mapping[str, Any],
) -> list[dict[str, Any]]:
    assignments_by_rotation: dict[str, Mapping[tuple[str, str, str], Mapping[str, Any]]] = {}
    records: list[dict[str, Any]] = []
    for run_dir in run_dirs:
        untrusted = validate_cohort_index(run_dir / "cohort_index.json")
        profile = _mapping(untrusted.get("profile"), f"{run_dir} profile")
        seed = profile.get("seed")
        rotation = profile.get("rotation")
        _require(type(seed) is int, f"{run_dir} seed identity is invalid")
        _require(isinstance(rotation, str) and rotation, f"{run_dir} rotation identity is invalid")
        assignments = assignments_by_rotation.get(rotation)
        if assignments is None:
            assignments = build_evaluator_assignments(
                private_data,
                dataset,
                rotation,
                tasks=[TASK_ID],
                test_samples_per_bearing=3,
            )
            assignments_by_rotation[rotation] = assignments
        trusted = validate_cohort_index(
            run_dir / "cohort_index.json",
            private_assignments=assignments,
        )
        rows = _list(trusted.get("records"), f"{run_dir} trusted records")
        _require(len(rows) == 4, f"{run_dir} must contain exactly four Ottawa episodes")
        for raw in rows:
            row = dict(_mapping(raw, f"{run_dir} record"))
            row["pair_run"] = str(seed)
            records.append(row)
    return records


def _pair_key(record: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        str(record.get("pair_run")),
        str(record.get("rotation")),
        str(record.get("bearing_id")),
        str(record.get("sample_id")),
        str(record.get("task_id")),
    )


def _validate_records(
    reactive: Sequence[Mapping[str, Any]],
    graph: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    _require(len(reactive) == 36, f"Reactive accepted denominator is {len(reactive)}/36")
    _require(len(graph) == 36, f"Graph accepted denominator is {len(graph)}/36")
    reactive_keys = [_pair_key(row) for row in reactive]
    graph_keys = [_pair_key(row) for row in graph]
    _require(len(set(reactive_keys)) == 36, "Reactive episode keys are not unique")
    _require(len(set(graph_keys)) == 36, "Graph episode keys are not unique")
    _require(set(reactive_keys) == set(graph_keys), "Reactive and Graph episode keys do not match exactly")

    def arm_counts(rows: Sequence[Mapping[str, Any]], arm: str) -> dict[str, Any]:
        bearings = Counter(str(row.get("bearing_id")) for row in rows)
        seeds = Counter(str(row.get("pair_run")) for row in rows)
        rotations = Counter(str(row.get("rotation")) for row in rows)
        windows = 0
        for row in rows:
            _require(row.get("task_id") == TASK_ID, f"{arm} contains a non-monitoring task")
            sample_ids = _list(row.get("sample_ids"), f"{arm} sample_ids")
            targets = _mapping(row.get("private_target"), f"{arm} private_target")
            _require(len(sample_ids) == 3, f"{arm} episode does not contain three assigned windows")
            _require(set(map(str, sample_ids)) == set(map(str, targets)), f"{arm} private target keys differ from assigned windows")
            _require(sorted(int(value) for value in targets.values()) == [0, 1, 1], f"{arm} Ottawa target pattern drifted")
            windows += len(sample_ids)
        _require(len(bearings) == 12 and set(bearings.values()) == {3}, f"{arm} physical-bearing clusters are not exact 12x3")
        _require(len(seeds) == 3 and set(seeds.values()) == {12}, f"{arm} seed denominator is not exact 3x12")
        _require(len(rotations) == 3 and set(rotations.values()) == {12}, f"{arm} rotation denominator is not exact 3x12")
        _require(windows == 108, f"{arm} assigned-window denominator is {windows}/108")
        return {
            "runs": 9,
            "episode_bundles": len(rows),
            "assigned_windows": windows,
            "physical_bearing_clusters": len(bearings),
            "nonprovider_terminal_failures_retained": sum(
                row.get("failure_kind") not in {None, "provider_error"}
                for row in rows
            ),
        }

    return {
        "reactive": arm_counts(reactive, "Reactive"),
        "graph": arm_counts(graph, "Graph"),
        "matched_episode_pairs": 36,
    }


def analyze_accepted_records(
    reactive: Sequence[Mapping[str, Any]],
    graph: Sequence[Mapping[str, Any]],
    *,
    dataset: Mapping[str, Any],
    cross: Mapping[str, Any],
) -> dict[str, Any]:
    """Analyze only an already accepted, exact, private-target-bound cohort."""

    denominators = _validate_records(reactive, graph)
    analysis = _validate_analysis_registration(cross)
    statistics = analysis["statistics"]
    iterations = int(statistics["iterations"])
    seed = int(statistics["seed"])
    try:
        replay_policy = require_formal_replay_metric_lock(dataset)
    except RuntimeError as exc:
        raise CrossDatasetAnalysisError(str(exc)) from exc
    _require(replay_policy == REPLAY_POLICY_ID, "target-adverse replay policy drifted")

    reactive_summary = aggregate_results(
        reactive,
        replay_missing_score_policy_id=replay_policy,
    )
    graph_summary = aggregate_results(
        graph,
        replay_missing_score_policy_id=replay_policy,
    )
    reactive_interval, reactive_valid = bearing_bootstrap_intervals(
        reactive,
        iterations=iterations,
        seed=seed,
        replay_missing_score_policy_id=replay_policy,
    )
    graph_interval, graph_valid = bearing_bootstrap_intervals(
        graph,
        iterations=iterations,
        seed=seed,
        replay_missing_score_policy_id=replay_policy,
    )
    paired = paired_bearing_bootstrap_deltas(
        reactive,
        graph,
        iterations=iterations,
        seed=seed,
        replay_missing_score_policy_id=replay_policy,
    )
    _require(paired.get("bootstrap_iterations") == iterations, "paired bootstrap iteration count drifted")
    _require(paired.get("seed") == seed, "paired bootstrap seed drifted")
    _require(paired.get("direction") == "treatment_minus_control", "paired contrast direction drifted")
    try:
        primary_estimate = paired["estimate"][TASK_ID]["task.average_precision"]
        primary_interval = paired["bearing_bootstrap_95ci"][TASK_ID]["task.average_precision"]
        primary_valid = paired["bearing_bootstrap_valid_replicates"][TASK_ID]["task.average_precision"]
    except (KeyError, TypeError) as exc:
        raise CrossDatasetAnalysisError("paired result lacks the preregistered primary endpoint") from exc
    _require(primary_estimate is not None, "primary Graph-minus-Reactive AP effect is undefined")
    _require(isinstance(primary_interval, list) and len(primary_interval) == 2, "primary paired interval is undefined")
    _require(primary_valid == iterations, "primary paired interval lacks all bootstrap replicates")
    return {
        "denominators": denominators,
        "target_adverse_metric_policy_id": replay_policy,
        "arm_summaries": {
            "reactive": reactive_summary,
            "graph": graph_summary,
        },
        "arm_bearing_bootstrap": {
            "reactive": {
                "interval_95ci": reactive_interval,
                "valid_replicates": reactive_valid,
            },
            "graph": {
                "interval_95ci": graph_interval,
                "valid_replicates": graph_valid,
            },
        },
        "paired_graph_minus_reactive": paired,
        "primary_endpoint": {
            "name": statistics["primary_endpoint"],
            "estimate": primary_estimate,
            "bearing_cluster_bootstrap_95ci": primary_interval,
            "valid_replicates": primary_valid,
        },
    }


def build_report(
    *,
    reactive_root: Path,
    graph_root: Path,
    protocol_path: Path = DEFAULT_PROTOCOL,
    dataset_protocol_path: Path | None = None,
) -> dict[str, Any]:
    cross = load_protocol(protocol_path.resolve())
    validate_protocol(cross)
    _validate_analysis_registration(cross)
    dataset_path = dataset_protocol_path or _dataset_protocol_path(cross)
    dataset = _load_yaml(dataset_path.resolve(), "Ottawa dataset protocol")
    _require(dataset.get("protocol_id") == cross["dataset_registration"]["dataset_protocol_id"], "Ottawa dataset protocol identity drifted")
    _require(dataset.get("dataset", {}).get("dataset_id") == DATASET_ID, "Ottawa dataset identity drifted")
    run_stamp, formal_run_root = _validate_registered_root_layout(
        reactive_root, graph_root, cross
    )
    seeds = [int(value) for value in cross["current_schedule"]["seeds"]]
    rotations = [str(value) for value in cross["dataset_registration"]["rotations"]]
    reactive_dirs = _expected_run_dirs(reactive_root, seeds=seeds, rotations=rotations)
    graph_dirs = _expected_run_dirs(graph_root, seeds=seeds, rotations=rotations)
    _validate_arm_profiles(reactive_dirs, cross=cross, dataset=dataset, arm="reactive")
    _validate_arm_profiles(graph_dirs, cross=cross, dataset=dataset, arm="graph")

    with _open_private_data(cross, dataset) as private_data:
        reactive_acceptance = validate_formal_cohort(
            reactive_dirs,
            dataset,
            expected_seeds=seeds,
            mode="monitoring",
            expected_rotations=rotations,
            require_state_evaluation=False,
            require_inference_contract=False,
            expected_runtime_contract=RUNTIME_CONTRACT,
            expected_experiment_profile_id=PROFILE_ID,
            expected_agent="reactive",
            expected_agent_id="reactive-sequential-agent",
            expected_registered_evidence_class="formal",
            expected_result_role="confirmatory",
            private_data=private_data,
        )
        graph_acceptance = validate_formal_cohort(
            graph_dirs,
            dataset,
            expected_seeds=seeds,
            mode="monitoring",
            expected_rotations=rotations,
            require_state_evaluation=True,
            require_inference_contract=False,
            expected_runtime_contract=RUNTIME_CONTRACT,
            expected_experiment_profile_id=PROFILE_ID,
            expected_agent="graph",
            expected_agent_id="graph-decision-agent",
            expected_registered_evidence_class="formal",
            expected_result_role="confirmatory",
            private_data=private_data,
        )
        _validate_matched_reports(reactive_acceptance, graph_acceptance)
        reactive_records = _trusted_arm_records(
            reactive_dirs,
            private_data=private_data,
            dataset=dataset,
        )
        graph_records = _trusted_arm_records(
            graph_dirs,
            private_data=private_data,
            dataset=dataset,
        )

    analysis = analyze_accepted_records(
        reactive_records,
        graph_records,
        dataset=dataset,
        cross=cross,
    )
    return {
        "schema_version": RESULT_SCHEMA,
        "status": "accepted",
        "evidence_class": "formal",
        "result_role": "confirmatory",
        "protocol_id": PROTOCOL_ID,
        "dataset_id": DATASET_ID,
        "dataset_protocol_id": dataset["protocol_id"],
        "experiment_profile_id": PROFILE_ID,
        "formal_run_stamp": run_stamp,
        "formal_run_root": str(formal_run_root),
        "provider_calls_made_by_analyzer": 0,
        "private_assignment_validation": dataset["dataset"]["evaluator_assignment_contract"],
        "acceptance": {
            "reactive": {
                "accepted": True,
                "runs": reactive_acceptance["observed_runs"],
                "episodes": reactive_acceptance["observed_unique_episodes"],
                "errors": [],
            },
            "graph": {
                "accepted": True,
                "runs": graph_acceptance["observed_runs"],
                "episodes": graph_acceptance["observed_unique_episodes"],
                "errors": [],
            },
            "matched_world_contract": "accepted",
            "exact_episode_pairing": "accepted",
        },
        "analysis": analysis,
        "reporting_boundary": {
            "dataset_pooling": "Ottawa_only",
            "public_condition_event": "absent",
            "event_f1": "N/A",
            "detection_delay": "N/A",
            "monitor_or_revise_event_branch_transfer": "not_an_estimand",
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Provider-free accepted-only P2-E8 Ottawa paired analyzer."
    )
    parser.add_argument("--reactive-root", type=Path, required=True)
    parser.add_argument("--graph-root", type=Path, required=True)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--dataset-protocol", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        dataset_protocol_path = _validate_production_cli_paths(
            protocol_path=args.protocol,
            dataset_protocol_path=args.dataset_protocol,
            output_path=args.output,
        )
        report = build_report(
            reactive_root=args.reactive_root,
            graph_root=args.graph_root,
            protocol_path=args.protocol,
            dataset_protocol_path=dataset_protocol_path,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _validate_production_cli_paths(
            protocol_path=args.protocol,
            dataset_protocol_path=dataset_protocol_path,
            output_path=args.output,
        )
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    except (CrossDatasetAnalysisError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"P2-E8 analysis blocked: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
