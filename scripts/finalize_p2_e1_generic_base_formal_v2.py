#!/usr/bin/env python3
"""Accept and finalize the matched Generic-base P2-E1 formal-v2 cohort.

The command is provider-free. It validates each active-v0.2 cohort index against
its canonical RunBundle history before counting denominators. Evaluator-private
records are projected into paired analysis, and the 2,000-resample bearing
bootstrap runs, only after all four arm gates and both pairing gates accept.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT.parent / "P01-phm-agent-benchmark"
BENCHMARK_SRC = BENCHMARK / "src"
if str(BENCHMARK_SRC) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_SRC))

from phm_agent_benchmark.phase1.experiment import (
    aggregate_results,
    bearing_bootstrap_intervals,
    paired_bearing_bootstrap_deltas,
    require_formal_replay_metric_lock,
)
from phm_agent_benchmark.phase1.cohort import (
    episode_attempt_directory,
    validate_cohort_index,
)
from phm_agent_benchmark.protocol import PROTOCOL_VERSION, USAGE_ACCOUNTING_CONTRACT
from phm_agent_benchmark.rollout_io import read_run_bundle
from phm_graph_agent import ALLOWED_TRANSITIONS, STATES as EXECUTABLE_GRAPH_STATES


DEFAULT_PROTOCOL = ROOT / "paper/experiments/p2_e1_generic_base_formal_v2.yaml"
DEFAULT_READINESS = ROOT / "paper/experiments/results/p2_e1_primary_readiness_v2.json"
DEFAULT_RESULT = ROOT / "paper/experiments/results/p2_e1_generic_base_formal_v2_result.json"
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
GRAPH_STATE_ORDER = (
    "Inspect",
    "Hypothesize",
    "Analyze",
    "Check",
    "Monitor",
    "Revise",
    "Recover",
    "Submit",
)
GRAPH_STATES = frozenset(GRAPH_STATE_ORDER)
PRIVATE_FIELDS = frozenset(
    {"bearing_id", "private_target", "diagnosis_target", "anomaly_target"}
)
CORE_TASKS = ("cold_start_fault_diagnosis", "unsupervised_anomaly_detection")
REPLAY_TASKS = ("online_replay_monitoring",)
TASK_ENDPOINTS = {
    "cold_start_fault_diagnosis": ("task.macro_f1",),
    "unsupervised_anomaly_detection": (
        "task.completion_adjusted_average_precision",
    ),
    "online_replay_monitoring": ("task.average_precision",),
}
ROLLOUT_ENDPOINTS = (
    "rollout.grounded_completion",
    "rollout.submission_rate",
    "rollout.budget_exhaustion",
    "rollout.valid_tool_call_rate",
    "rollout.repeated_action_ratio",
    "rollout.grounded_recovery_success",
    "rollout.recovery_coverage",
    "rollout.steps_to_recovery",
    "rollout.steps",
    "rollout.p95_step_latency_seconds",
    "rollout.llm_turns",
    "rollout.input_tokens",
    "rollout.output_tokens",
    "rollout.wall_clock_seconds",
    "rollout.estimated_model_cost_usd",
)
PRIMARY_ENDPOINT = {
    "cohort": "replay",
    "task": "online_replay_monitoring",
    "metric": "task.average_precision",
}
EVIDENCE_CLASS = "real_data_formal_candidate"
EXPECTED_SCHEMA = "p2_e1_generic_base_formal_v2"
BENCHMARK_CONTROL_SOURCE_CONTRACT = "benchmark_active_v0_2_control_source_v1"
BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = (
    "benchmark_formal_gitlink_topology_v1"
)
P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = "p2_e1_formal_execution_topology_v1"
BENCHMARK_REPOSITORY = "https://github.com/liq22/phm-agent-benchmark.git"
DATA_FACTORY_REPOSITORY = "https://github.com/PHMbench/phm-data-factory.git"
P2_REPOSITORY = "https://github.com/liq22/P02_agent_langraph.git"
P2_FORMAL_REPRODUCIBILITY_PATHS = (
    "CORE.md",
    "scripts/run_graph_experiment.py",
    "src/phm_graph_agent",
)
ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID = (
    "benchmark_v0_2_0--paderborn_phase1_v1--runtime_v6--window_v3"
)
ACTIVE_BENCHMARK_CONTROL_PROFILE_ID = "paper0-paderborn-primary-v1"
FORMAL_RUN_STAMP_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


class FinalizationError(RuntimeError):
    """Raised when persisted P2-E1 evidence violates its frozen contract."""


@dataclass(frozen=True, order=True)
class EpisodeKey:
    seed: int
    rotation: str
    sample_id: str
    task_id: str

    def as_list(self) -> list[Any]:
        return [self.seed, self.rotation, self.sample_id, self.task_id]


@dataclass(frozen=True)
class Attempt:
    path: Path
    key: EpisodeKey
    index: int
    outcome_class: str
    run: Mapping[str, Any]
    metrics: Mapping[str, Any]
    states: tuple[str, ...]


@dataclass(frozen=True)
class ArmSpec:
    name: str
    scope: str
    root: Path
    control: bool
    tasks: tuple[str, ...]
    units: tuple[tuple[int, str], ...]
    expected: int


@dataclass(frozen=True)
class ArmAudit:
    spec: ArmSpec
    attempts: tuple[Attempt, ...]
    statistical: Mapping[EpisodeKey, Attempt]
    manifests: Mapping[tuple[int, str], Mapping[str, Any]]
    evaluation_files: Mapping[tuple[int, str], Path]
    terminal_counts: Mapping[str, int]
    provider_errors: int
    nonprovider_failures: int
    unresolved_provider_keys: tuple[EpisodeKey, ...]
    retry_chains: int
    action_rows: int
    accepted: bool
    blockers: tuple[str, ...]
    execution_topology: Mapping[str, Any] | None = None


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise FinalizationError(message)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise FinalizationError(f"cannot read valid JSON from {path}: {exc}") from exc


def _load_jsonl(path: Path) -> list[Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FinalizationError(f"cannot read {path}: {exc}") from exc
    rows: list[Any] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise FinalizationError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
    return rows


def _json_view(value: Any) -> Any:
    """Normalize YAML/JSON mapping keys before persisted-contract comparison."""

    return json.loads(json.dumps(value, sort_keys=True))


def _benchmark_execution_topology(value: Any, label: str) -> dict[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be a mapping")
    topology = _json_view(value)
    base_fields = {
        "contract",
        "benchmark_repository",
        "benchmark_revision",
        "data_factory_repository",
        "data_factory_revision",
        "data_factory_distribution_version",
        "data_factory_lock_version",
    }
    allowed_fields = base_fields | {"formal_reproducibility_paths"}
    _require(
        set(topology) in (base_fields, allowed_fields),
        f"{label} fields drifted",
    )
    _require(
        topology.get("contract") == BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
        f"{label} contract drifted",
    )
    _require(
        topology.get("benchmark_repository") == BENCHMARK_REPOSITORY,
        f"{label} Benchmark repository drifted",
    )
    _require(
        topology.get("data_factory_repository") == DATA_FACTORY_REPOSITORY,
        f"{label} Data Factory repository drifted",
    )
    for field in ("benchmark_revision", "data_factory_revision"):
        revision = topology.get(field)
        _require(
            isinstance(revision, str)
            and REVISION_PATTERN.fullmatch(revision) is not None,
            f"{label} has invalid {field}",
        )
    distribution = topology.get("data_factory_distribution_version")
    _require(
        isinstance(distribution, str)
        and bool(distribution)
        and topology.get("data_factory_lock_version") == distribution,
        f"{label} Data Factory distribution/lock versions drifted",
    )
    if "formal_reproducibility_paths" in topology:
        paths = topology["formal_reproducibility_paths"]
        _require(
            isinstance(paths, list)
            and all(isinstance(path, str) and path for path in paths)
            and len(paths) == len(set(paths)),
            f"{label} formal reproducibility paths drifted",
        )
    return topology


def _graph_execution_topology(value: Any, label: str) -> dict[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be a mapping")
    topology = _json_view(value)
    expected_fields = {
        "contract",
        "benchmark_formal_execution_topology",
        "source_repositories",
        "source_revisions",
        "formal_sources_clean",
        "canonical_origins_verified",
        "p2_formal_reproducibility_paths",
    }
    _require(set(topology) == expected_fields, f"{label} fields drifted")
    _require(
        topology.get("contract") == P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
        f"{label} contract drifted",
    )
    benchmark = _benchmark_execution_topology(
        topology.get("benchmark_formal_execution_topology"),
        f"{label}.benchmark_formal_execution_topology",
    )
    expected_repositories = {
        "benchmark": BENCHMARK_REPOSITORY,
        "data_factory": DATA_FACTORY_REPOSITORY,
        "p2": P2_REPOSITORY,
    }
    _require(
        topology.get("source_repositories") == expected_repositories,
        f"{label} source repositories drifted",
    )
    revisions = topology.get("source_revisions")
    _require(
        isinstance(revisions, Mapping)
        and set(revisions) == set(expected_repositories),
        f"{label} source revisions are incomplete",
    )
    for source, revision in revisions.items():
        _require(
            isinstance(revision, str)
            and REVISION_PATTERN.fullmatch(revision) is not None,
            f"{label} has invalid {source} revision",
        )
    _require(
        revisions["benchmark"] == benchmark["benchmark_revision"]
        and revisions["data_factory"] == benchmark["data_factory_revision"],
        f"{label} source revisions differ from Benchmark topology",
    )
    expected_verified = {source: True for source in expected_repositories}
    _require(
        topology.get("formal_sources_clean") == expected_verified,
        f"{label} does not prove clean formal sources",
    )
    _require(
        topology.get("canonical_origins_verified") == expected_verified,
        f"{label} does not prove canonical origins",
    )
    _require(
        topology.get("p2_formal_reproducibility_paths")
        == list(P2_FORMAL_REPRODUCIBILITY_PATHS),
        f"{label} P02 formal reproducibility paths drifted",
    )
    return topology


def _walk(value: Any) -> Iterable[tuple[str | None, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key), child
            yield from _walk(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield None, child
            yield from _walk(child)


def _known_bearings(dataset: Mapping[str, Any]) -> frozenset[str]:
    folds = dataset.get("split", {}).get("folds", {})
    _require(isinstance(folds, Mapping) and folds, "dataset protocol split.folds is missing")
    bearings: set[str] = set()
    for values in folds.values():
        _require(isinstance(values, list), "dataset protocol fold is not a list")
        bearings.update(str(value) for value in values)
    return frozenset(bearings)


def _assert_public(documents: Iterable[Any], bearings: frozenset[str], label: str) -> None:
    for document in documents:
        for key, value in _walk(document):
            if key is not None and key.lower() in PRIVATE_FIELDS:
                raise FinalizationError(f"{label} exposes private field {key!r}")
            if isinstance(value, str) and value in bearings:
                raise FinalizationError(f"{label} exposes evaluator-private bearing {value!r}")


def _display(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        try:
            return "../" + path.resolve().relative_to(ROOT.parent.resolve()).as_posix()
        except ValueError:
            return path.as_posix()


def _resolve(raw: str) -> Path:
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def _load_protocol(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol = yaml.safe_load(path.read_text(encoding="utf-8"))
    _require(isinstance(protocol, dict), "P2-E1 formal protocol must be a mapping")
    _require(protocol.get("schema_version") == EXPECTED_SCHEMA, "wrong P2-E1 protocol schema")
    _require(protocol.get("status") == "active", "P2-E1 formal-v2 protocol is not active")
    dataset_path = _resolve(str(protocol.get("dataset_protocol", "")))
    dataset = yaml.safe_load(dataset_path.read_text(encoding="utf-8"))
    _require(isinstance(dataset, dict), "dataset protocol must be a mapping")
    _validate_protocol(protocol, dataset)
    protocol["_dataset_path"] = str(dataset_path)
    return protocol, dataset


def _validate_protocol(protocol: Mapping[str, Any], dataset: Mapping[str, Any]) -> None:
    expected_control_source = {
        "contract": BENCHMARK_CONTROL_SOURCE_CONTRACT,
        "protocol_id": ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
        "profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
        "formal_run_stamp": "explicit_cli_required",
        "public_leaf_root_path": "forbidden",
    }
    _require(
        protocol.get("benchmark_control_source") == expected_control_source,
        "Benchmark control-source registration drift",
    )
    authority = protocol.get("authority", {})
    control = authority.get("control", {})
    treatment = authority.get("treatment", {})
    _require(control.get("repository") == "liq22/phm-agent-benchmark", "control repository drift")
    _require(control.get("policy") == "GenericLLMToolAgent", "control policy drift")
    _require(control.get("agent_id") == "generic-llm-tool-agent", "control agent drift")
    _require(control.get("reuse_mode") == "external_immutable_read_only", "Generic root must be immutable")
    _require(control.get("duplicate_provider_execution") == "forbidden", "duplicate Generic execution must be forbidden")
    expected_root_contract = {
        "schema": "benchmark_active_v0_2_external_timestamped_root_v1",
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "root_layout": (
            "protocol_id/arm_scope/profile_id/run_{formal_run_stamp}/"
            "seed_{seed}/{rotation}/cohort_index.json"
        ),
        "root_resolution": "explicit_cli_root_required",
    }
    for arm, expected_flags in (
        (control, ("--generic-core-root", "--generic-replay-root")),
        (treatment, ("--graph-core-root", "--graph-replay-root")),
    ):
        contract = arm.get("external_root_contract", {})
        for field, expected_value in expected_root_contract.items():
            _require(contract.get(field) == expected_value, f"external root contract {field} drift")
        _require(
            (contract.get("core_cli_flag"), contract.get("replay_cli_flag"))
            == expected_flags,
            "external root CLI binding drift",
        )
        _require(
            arm.get("core_root") is None and arm.get("replay_root") is None,
            "active-v0.2 roots must be supplied explicitly",
        )
    _require(treatment.get("repository") == "liq22/P02_agent_langraph", "treatment repository drift")
    _require(treatment.get("policy") == "GraphDecisionAgent", "treatment policy drift")
    _require(treatment.get("agent_id") == "graph-decision-agent", "treatment agent drift")
    _require(treatment.get("graph_policy_profile") == "full", "primary Graph profile must be full")
    _require(treatment.get("formal_root_version") == "p2_graph_vs_generic_llm_active_v0_2_v1", "Graph root version drift")
    identity = treatment.get("identity", {})
    expected_identity = {
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": "graph_decision_control_v1",
        "agent_implementation_id": "graph_decision_agent_v1",
    }
    _require(identity == expected_identity, "Graph causal identity drift")
    _require(
        tuple(EXECUTABLE_GRAPH_STATES) == GRAPH_STATE_ORDER,
        "executable Graph state topology differs from the registered reporting contract",
    )

    design = protocol.get("registered_design", {})
    seeds = design.get("seeds")
    core = design.get("core", {})
    replay = design.get("replay", {})
    dataset_rotations = [str(row["run"]) for row in dataset.get("split", {}).get("rotations", [])]
    monitoring_rotations = list(dataset.get("episode_sampling", {}).get("monitoring_rotations", []))
    _require(seeds == [20260808, 20260809, 20260810], "registered P2-E1 seeds drift")
    _require(core.get("rotations") == dataset_rotations, "core rotations differ from dataset authority")
    _require(core.get("tasks") == list(CORE_TASKS), "core task registration drift")
    _require(core.get("expected_statistical_outcomes_per_arm") == 192, "core denominator must be 192 per arm")
    _require(replay.get("rotations") == monitoring_rotations == ["rotation_0"], "replay rotations drift")
    _require(replay.get("tasks") == list(REPLAY_TASKS), "replay task registration drift")
    _require(replay.get("expected_statistical_outcomes_per_arm") == 24, "replay denominator must be 24 per arm")
    _require(
        protocol.get("authority_correction")
        == {
            "status": "applied_before_any_accepted_p2_e1_result",
            "basis": "CORE.md_task_performance_primary_rollout_diagnostics_secondary",
            "superseded_primary_endpoint": "rollout.grounded_completion",
            "corrected_primary_endpoint": "task.average_precision",
            "graph_treatment_formal_outcomes_observed_at_correction": 0,
        },
        "P2-E1 pre-result task-primary authority correction drift",
    )
    folds = dataset.get("split", {}).get("folds", {})
    rotation_rows = {str(row["run"]): row for row in dataset.get("split", {}).get("rotations", [])}
    core_per_seed = sum(len(folds[rotation_rows[rotation]["test"]]) * len(CORE_TASKS) for rotation in dataset_rotations)
    replay_per_seed = sum(len(folds[rotation_rows[rotation]["test"]]) for rotation in monitoring_rotations)
    _require(len(seeds) * core_per_seed == 192, "dataset authority does not derive the 192 core denominator")
    _require(len(seeds) * replay_per_seed == 24, "dataset authority does not derive the 24 replay denominator")

    frozen = protocol.get("frozen_profile", {})
    inference = dataset.get("inference", {})
    model = inference.get("model_profile", {})
    expected_frozen = {
        "runtime": "openai",
        "runtime_contract": "phase1_opaque_sample_vibration_feature_schema_v6",
        "provider": model.get("provider"),
        "model": model.get("model_id"),
        "inference_protocol": model.get("protocol"),
        "thinking_mode": "not_requested",
        "temperature": inference.get("temperature"),
        "max_output_tokens_per_turn": inference.get("max_output_tokens_per_turn"),
        "input_usd_per_million": model.get("input_usd_per_million"),
        "output_usd_per_million": model.get("output_usd_per_million"),
    }
    _require(frozen == expected_frozen, "frozen inference/model profile differs from dataset authority")
    failure = protocol.get("failure_and_denominator_policy", {})
    _require(failure.get("canonical_attempt_contract") == "exact_six", "exact-six policy missing")
    _require(failure.get("provider_error") == "retain_attempt_exclude_until_same_profile_retry_terminates", "provider retry policy drift")
    _require(failure.get("non_provider_terminal_failure") == "retain_in_denominator", "failure denominator policy drift")
    _require(failure.get("unresolved_provider_error") == "blocks_arm_acceptance", "unresolved provider policy drift")
    _require(failure.get("partial_prefix_aggregation") == "forbidden", "partial aggregation must be forbidden")
    analysis = protocol.get("analysis", {})
    bootstrap = analysis.get("bootstrap", {})
    _require(bootstrap.get("method") == "paired_bearing_cluster_percentile_bootstrap", "bootstrap method drift")
    _require(bootstrap.get("cluster_unit") == "physical_bearing", "bootstrap cluster must be physical bearing")
    _require(bootstrap.get("iterations") == 2000, "P2-E1 requires exactly 2,000 bootstrap resamples")
    _require(bootstrap.get("seed") == 20260820, "P2-E1 bootstrap seed must be exactly 20260820")
    _require(analysis.get("direction") == "treatment_minus_control", "contrast direction drift")
    _require(
        analysis.get("task_endpoints")
        == {task: list(endpoints) for task, endpoints in TASK_ENDPOINTS.items()},
        "registered task endpoints drift",
    )
    _require(
        analysis.get("rollout_endpoints") == list(ROLLOUT_ENDPOINTS),
        "registered rollout endpoints drift",
    )
    _require(
        analysis.get("primary_endpoint") == PRIMARY_ENDPOINT,
        "P2-E1 primary endpoint must be replay task.average_precision",
    )
    try:
        replay_policy = require_formal_replay_metric_lock(dataset)
    except RuntimeError as exc:
        raise FinalizationError(str(exc)) from exc
    _require(
        analysis.get("replay_missing_score_policy_id") == replay_policy,
        "P2-E1 replay missing-score policy differs from dataset authority",
    )


def _benchmark_control_source(
    protocol: Mapping[str, Any],
    *,
    formal_run_stamp: str | None,
    protocol_id: str | None,
    profile_id: str | None,
) -> dict[str, str]:
    missing = [
        name
        for name, value in (
            ("benchmark_formal_run_stamp", formal_run_stamp),
            ("benchmark_control_protocol_id", protocol_id),
            ("benchmark_control_profile_id", profile_id),
        )
        if value is None
    ]
    _require(
        not missing,
        "active-v0.2 finalization requires explicit Benchmark control identity: "
        + ", ".join(missing),
    )
    stamp = str(formal_run_stamp)
    observed_protocol = str(protocol_id)
    observed_profile = str(profile_id)
    registered = protocol["benchmark_control_source"]
    _require(
        FORMAL_RUN_STAMP_PATTERN.fullmatch(stamp) is not None,
        "Benchmark formal run stamp must match YYYYMMDDTHHMMSSZ",
    )
    _require(
        observed_protocol == registered["protocol_id"],
        "Benchmark control protocol differs from the active P2-E1 registration",
    )
    _require(
        observed_profile == registered["profile_id"],
        "Benchmark control profile differs from the active P2-E1 registration",
    )
    return {
        "contract": str(registered["contract"]),
        "formal_run_stamp": stamp,
        "protocol_id": observed_protocol,
        "profile_id": observed_profile,
    }


def _validate_external_root_identity(
    name: str,
    root: Path,
    source: Mapping[str, str],
) -> None:
    expected_run_name = f"run_{source['formal_run_stamp']}"
    _require(
        root.name == expected_run_name,
        f"{name} root belongs to a different formal run stamp: "
        f"expected {expected_run_name!r}, observed {root.name!r}",
    )
    _require(
        root.parent.name == source["profile_id"],
        f"{name} root is outside the registered Benchmark control profile",
    )
    _require(
        len(root.parents) >= 3 and root.parents[2].name == source["protocol_id"],
        f"{name} root is outside the registered Benchmark control protocol",
    )


def _budget_view(value: Any, expected: Mapping[str, Any]) -> dict[str, Any]:
    _require(isinstance(value, Mapping), "budget is missing")
    view = {key: value.get(key) for key in expected}
    _require(view == dict(expected), f"budget differs: expected {dict(expected)}, observed {view}")
    return view


def _manifest_pair_contract(manifest: Mapping[str, Any], expected_budget: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "benchmark_protocol_version": manifest.get("benchmark_protocol_version"),
        "budget": _budget_view(manifest.get("budget"), expected_budget),
        "budget_protocol": manifest.get("budget_protocol"),
        "dataset_protocol_id": manifest.get("dataset_protocol_id"),
        "dataset_protocol_schema": manifest.get("dataset_protocol_schema"),
        "max_output_tokens_per_turn": manifest.get("max_output_tokens_per_turn"),
        "model_profile": manifest.get("model_profile"),
        "protocol": manifest.get("protocol"),
        "replay_missing_score_policy_id": manifest.get(
            "replay_missing_score_policy_id"
        ),
        "rotation": manifest.get("rotation"),
        "runtime": manifest.get("runtime"),
        "runtime_contract": manifest.get("runtime_contract"),
        "sample_handle": manifest.get("sample_handle"),
        "seed": manifest.get("seed"),
        "selected_diagnosis_model_id": manifest.get("selected_diagnosis_model_id"),
        "tasks": manifest.get("tasks"),
        "temperature": manifest.get("temperature"),
        "test_sample_selection": manifest.get("test_sample_selection"),
        "test_samples_per_bearing": manifest.get("test_samples_per_bearing"),
        "train_samples_per_bearing": manifest.get("train_samples_per_bearing"),
        "validation_model_macro_f1": manifest.get("validation_model_macro_f1"),
        "validation_samples_per_bearing": manifest.get("validation_samples_per_bearing"),
        "window_protocol": manifest.get("window_protocol"),
        "window_contract": manifest.get("window_contract"),
    }


def _validate_manifest(
    manifest: Mapping[str, Any],
    spec: ArmSpec,
    unit: tuple[int, str],
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    control_source: Mapping[str, str],
) -> dict[str, Any]:
    seed, rotation = unit
    frozen = protocol["frozen_profile"]
    sampling = dataset["episode_sampling"]
    expected_budget = dataset["budgets"]["core" if spec.scope == "core" else "monitoring"]
    expected_test_samples = sampling["agent_test_samples_per_bearing"] if spec.scope == "core" else sampling["monitoring_windows_per_episode"]
    expected_selection = sampling["agent_selection"] if spec.scope == "core" else sampling["numerical_selection"]
    expected_model_profile = {
        "input_usd_per_million": frozen["input_usd_per_million"],
        "model_id": frozen["model"],
        "output_usd_per_million": frozen["output_usd_per_million"],
        "protocol": frozen["inference_protocol"],
        "provider": frozen["provider"],
    }
    expected = {
        "protocol": dataset["schema_version"],
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "dataset_protocol_id": dataset.get("protocol_id", dataset["schema_version"]),
        "dataset_protocol_schema": dataset["schema_version"],
        "window_contract": dataset["window_protocol"]["contract"],
        "runtime": frozen["runtime"],
        "runtime_contract": frozen["runtime_contract"],
        "rotation": rotation,
        "seed": seed,
        "tasks": list(spec.tasks),
        "temperature": frozen["temperature"],
        "max_output_tokens_per_turn": frozen["max_output_tokens_per_turn"],
        "model_profile": expected_model_profile,
        "sample_handle": dataset["agent_visibility"]["sample_handle"],
        "window_protocol": dataset["window_protocol"],
        "train_samples_per_bearing": sampling["train_samples_per_bearing"],
        "validation_samples_per_bearing": sampling["healthy_validation_samples_per_bearing"],
        "test_samples_per_bearing": expected_test_samples,
        "test_sample_selection": expected_selection,
        "max_test_bearings": None,
    }
    for field, expected_value in expected.items():
        _require(_json_view(manifest.get(field)) == _json_view(expected_value), f"{spec.name} manifest {field} drift at {unit}")
    expected_replay_policy = (
        protocol["analysis"]["replay_missing_score_policy_id"]
        if spec.scope == "replay"
        else None
    )
    _require(
        "replay_missing_score_policy_id" in manifest
        and manifest.get("replay_missing_score_policy_id") == expected_replay_policy,
        f"{spec.name} manifest replay missing-score policy drift at {unit}",
    )
    _budget_view(manifest.get("budget"), expected_budget)
    budget_protocol = dict(expected_budget)
    budget_protocol.update(
        {
            "max_data_points": None,
            "max_data_bytes": None,
            "max_wall_clock_seconds": None,
        }
    )
    _require(
        _json_view(manifest.get("budget_protocol")) == _json_view(budget_protocol),
        f"{spec.name} manifest budget_protocol drift at {unit}",
    )
    _require(isinstance(manifest.get("selected_diagnosis_model_id"), str), f"{spec.name} selected model missing at {unit}")
    _require(isinstance(manifest.get("validation_model_macro_f1"), Mapping), f"{spec.name} validation scores missing at {unit}")
    _require(manifest.get("registered_evidence_class") == "formal", f"{spec.name} evidence registration is not formal at {unit}")
    _require(manifest.get("result_role") == "confirmatory", f"{spec.name} result role is not confirmatory at {unit}")
    _require(manifest.get("usage_accounting_contract") == USAGE_ACCOUNTING_CONTRACT, f"{spec.name} usage contract drift at {unit}")
    if spec.control:
        _require(manifest.get("agent_id") == protocol["authority"]["control"]["agent_id"], f"Generic control manifest agent drift at {unit}")
        _require(
            manifest.get("experiment_profile_id") == control_source["profile_id"],
            f"Generic control experiment profile drift at {unit}",
        )
        if "benchmark_control_source" in manifest:
            _require(
                manifest.get("benchmark_control_source") == dict(control_source),
                f"Generic control source identity drift at {unit}",
            )
        for field in ("p2_experiment_id", "matched_control_id", "agent_control_id", "agent_implementation_id", "runtime_source"):
            _require(field not in manifest, f"Generic control unexpectedly carries downstream field {field}")
        topology = _benchmark_execution_topology(
            manifest.get("formal_execution_topology"),
            f"{spec.name} manifest formal_execution_topology at {unit}",
        )
    else:
        _require(manifest.get("agent_id") == protocol["authority"]["treatment"]["agent_id"], f"Graph manifest agent drift at {unit}")
        _require(manifest.get("arm") == "graph", f"Graph manifest arm drift at {unit}")
        _require(manifest.get("graph_policy_profile") == "full", f"Graph manifest profile drift at {unit}")
        _require(
            manifest.get("benchmark_control_source") == dict(control_source),
            f"Graph manifest Benchmark control source drift at {unit}",
        )
        for field, expected_value in protocol["authority"]["treatment"]["identity"].items():
            _require(manifest.get(field) == expected_value, f"Graph manifest {field} drift at {unit}")
        topology = _graph_execution_topology(
            manifest.get("formal_execution_topology"),
            f"{spec.name} manifest formal_execution_topology at {unit}",
        )
    return topology


def _attempt_pair_contract(attempt: Attempt, expected_budget: Mapping[str, Any]) -> dict[str, Any]:
    metadata = attempt.run.get("metadata", {})
    return {
        "benchmark_protocol_version": attempt.run.get("protocol_version"),
        "budget": _budget_view(attempt.run.get("budget"), expected_budget),
        "dataset_protocol": metadata.get("dataset_protocol"),
        "dataset_protocol_id": metadata.get("dataset_protocol_id"),
        "dataset_protocol_schema": metadata.get("dataset_protocol_schema"),
        "inference_protocol": metadata.get("inference_protocol"),
        "model": metadata.get("model"),
        "provider": metadata.get("provider"),
        "rotation": metadata.get("rotation"),
        "replay_missing_score_policy_id": metadata.get(
            "replay_missing_score_policy_id"
        ),
        "runtime_contract": metadata.get("runtime_contract"),
        "sample_id": metadata.get("sample_id"),
        "seed": metadata.get("seed"),
        "selected_diagnosis_model_id": metadata.get("selected_diagnosis_model_id"),
        "task": attempt.run.get("task"),
        "thinking_mode": metadata.get("thinking_mode"),
        "window_contract": metadata.get("window_contract"),
    }


def _read_attempt(
    path: Path,
    spec: ArmSpec,
    unit: tuple[int, str],
    manifest: Mapping[str, Any],
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    bearings: frozenset[str],
    control_source: Mapping[str, str],
) -> Attempt:
    try:
        bundle = read_run_bundle(path)
    except (OSError, ValueError) as exc:
        raise FinalizationError(
            f"benchmark canonical bundle validation failed at {path}: {exc}"
        ) from exc
    run = bundle.run
    metrics = bundle.metrics
    _assert_public(
        (run, metrics, bundle.submission, bundle.artifacts, bundle.rollout_records, bundle.failures),
        bearings,
        str(path),
    )
    rotation, sample_id, task_id = bundle.episode_key
    _require(rotation == unit[1] and task_id in spec.tasks, f"attempt outside registered unit: {path}")
    attempt_name = path.name
    _require(attempt_name.startswith("attempt_") and len(attempt_name) == 11 and attempt_name[8:].isdigit(), f"malformed attempt index: {path}")
    attempt_index = int(attempt_name[8:])
    unit_dir = spec.root / f"seed_{unit[0]}" / unit[1]
    _require(
        path == episode_attempt_directory(unit_dir, bundle.episode_key, attempt_index),
        f"malformed active-v0.2 attempt path: {path}",
    )
    metadata = run.get("metadata", {})
    _require(isinstance(metadata, Mapping), f"run metadata missing: {path}")
    key = EpisodeKey(unit[0], unit[1], sample_id, task_id)
    expected_metadata = {
        "episode_key": [unit[1], sample_id, task_id],
        "attempt_index": attempt_index,
        "dataset_protocol": dataset["schema_version"],
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "dataset_protocol_id": dataset.get("protocol_id", dataset["schema_version"]),
        "dataset_protocol_schema": dataset["schema_version"],
        "window_contract": dataset["window_protocol"]["contract"],
        "runtime_contract": protocol["frozen_profile"]["runtime_contract"],
        "provider": protocol["frozen_profile"]["provider"],
        "model": protocol["frozen_profile"]["model"],
        "inference_protocol": protocol["frozen_profile"]["inference_protocol"],
        "thinking_mode": protocol["frozen_profile"]["thinking_mode"],
        "rotation": unit[1],
        "sample_id": sample_id,
        "seed": unit[0],
        "task_id": task_id,
        "selected_diagnosis_model_id": manifest.get("selected_diagnosis_model_id"),
        "replay_missing_score_policy_id": (
            protocol["analysis"]["replay_missing_score_policy_id"]
            if spec.scope == "replay"
            else None
        ),
    }
    for field, expected_value in expected_metadata.items():
        _require(
            field in metadata and metadata.get(field) == expected_value,
            f"{spec.name} attempt {field} drift at {path}",
        )
    resume_identity = metadata.get("cohort_resume_identity")
    _require(
        isinstance(resume_identity, Mapping)
        and "replay_missing_score_policy_id" in resume_identity
        and resume_identity.get("replay_missing_score_policy_id")
        == expected_metadata["replay_missing_score_policy_id"],
        f"{spec.name} attempt resume replay missing-score policy drift at {path}",
    )
    expected_topology = manifest.get("formal_execution_topology")
    _require(
        metadata.get("formal_execution_topology") == expected_topology,
        f"{spec.name} attempt formal_execution_topology drift at {path}",
    )
    _require(
        isinstance(resume_identity, Mapping)
        and resume_identity.get("formal_execution_topology") == expected_topology,
        f"{spec.name} attempt resume formal_execution_topology drift at {path}",
    )
    expected_budget = dataset["budgets"]["core" if spec.scope == "core" else "monitoring"]
    _budget_view(run.get("budget"), expected_budget)
    task = run.get("task", {})
    _require(isinstance(task, Mapping) and task.get("task_type") == task_id, f"TaskSpec/path mismatch: {path}")
    _require(task.get("protocol_version") == PROTOCOL_VERSION, f"TaskSpec protocol drift: {path}")
    _budget_view(task.get("budget"), expected_budget)
    _require(metrics.get("task_type") == task_id and metrics.get("terminal_status") == run.get("terminal_status"), f"public metrics/run mismatch: {path}")
    if spec.control:
        _require(run.get("agent_id") == protocol["authority"]["control"]["agent_id"], f"Generic agent identity drift: {path}")
        _require(
            metadata.get("experiment_profile_id") == control_source["profile_id"],
            f"Generic control experiment profile drift: {path}",
        )
        if "benchmark_control_source" in metadata:
            _require(
                metadata.get("benchmark_control_source") == dict(control_source),
                f"Generic control source identity drift: {path}",
            )
        for field in ("p2_experiment_id", "matched_control_id", "agent_control_id", "agent_implementation_id", "runtime_source"):
            _require(field not in metadata, f"Generic control unexpectedly carries downstream field {field}: {path}")
    else:
        _require(run.get("agent_id") == protocol["authority"]["treatment"]["agent_id"], f"Graph agent identity drift: {path}")
        _require(metadata.get("arm") == "graph" and metadata.get("graph_policy_profile") == "full", f"Graph arm/profile drift: {path}")
        _require(
            metadata.get("benchmark_control_source") == dict(control_source),
            f"Graph attempt Benchmark control source drift: {path}",
        )
        _require(
            isinstance(resume_identity, Mapping)
            and resume_identity.get("benchmark_control_source")
            == dict(control_source),
            f"Graph resume identity Benchmark control source drift: {path}",
        )
        for field, expected_value in protocol["authority"]["treatment"]["identity"].items():
            _require(metadata.get(field) == expected_value, f"Graph attempt {field} drift: {path}")
    states: list[str] = []
    for row in bundle.rollout_records:
        if not isinstance(row, Mapping) or row.get("event_type") != "action":
            continue
        action = row.get("action", {})
        _require(isinstance(action, Mapping), f"malformed action row: {path}")
        state = action.get("decision_state")
        if spec.control:
            _require(state is None, f"Generic control carries Graph state {state!r}: {path}")
        else:
            _require(state in GRAPH_STATES, f"Graph action lacks a registered decision state: {path}")
            states.append(str(state))
    terminal = run.get("terminal_status")
    failure_kind = run.get("failure_kind")
    if failure_kind == "provider_error":
        _require(terminal == "failed", f"provider_error is not terminal failed: {path}")
        outcome = "provider_error"
    else:
        _require(terminal not in {None, "running"}, f"nonterminal attempt is not admissible: {path}")
        outcome = "statistical"
    return Attempt(path, key, attempt_index, outcome, run, metrics, tuple(states))


def _audit_arm(
    spec: ArmSpec,
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    control_source: Mapping[str, str],
) -> ArmAudit:
    if not spec.root.exists():
        blocker = f"root missing: {_display(spec.root)}"
        return ArmAudit(spec, (), {}, {}, {}, {}, 0, 0, (), 0, 0, False, (blocker,))
    _require(spec.root.is_dir(), f"arm root is not a directory: {spec.root}")
    expected_units = set(spec.units)
    discovered_indexes = sorted(spec.root.glob("seed_*/rotation_*/cohort_index.json"))
    if not discovered_indexes:
        try:
            nonempty = next(spec.root.iterdir(), None) is not None
        except OSError as exc:
            raise FinalizationError(f"cannot inspect arm root {spec.root}: {exc}") from exc
        _require(
            not nonempty,
            f"{spec.name} non-empty root contains zero active-v0.2 canonical cohort units: {spec.root}",
        )
    discovered_units: set[tuple[int, str]] = set()
    index_by_unit: dict[tuple[int, str], Path] = {}
    for index_path in discovered_indexes:
        seed_name = index_path.parents[1].name
        _require(seed_name.startswith("seed_") and seed_name[5:].isdigit(), f"malformed seed directory: {index_path}")
        unit = (int(seed_name[5:]), index_path.parent.name)
        _require(unit not in index_by_unit, f"duplicate cohort unit: {unit}")
        discovered_units.add(unit)
        index_by_unit[unit] = index_path
    _require(discovered_units <= expected_units, f"{spec.name} contains unregistered units: {sorted(discovered_units - expected_units)}")

    all_index_paths = set(spec.root.rglob("cohort_index.json"))
    _require(
        all_index_paths == set(discovered_indexes),
        f"{spec.name} contains cohort indexes outside active timestamped unit paths",
    )

    bearings = _known_bearings(dataset)
    attempts: list[Attempt] = []
    manifests: dict[tuple[int, str], Mapping[str, Any]] = {}
    evaluation_files: dict[tuple[int, str], Path] = {}
    action_rows = 0
    for unit in sorted(discovered_units):
        unit_dir = spec.root / f"seed_{unit[0]}" / unit[1]
        index_path = index_by_unit[unit]
        try:
            cohort = validate_cohort_index(index_path)
        except (OSError, ValueError) as exc:
            raise FinalizationError(
                f"invalid active-v0.2 cohort index at {index_path}: {exc}"
            ) from exc
        manifest = cohort.get("profile")
        _require(isinstance(manifest, Mapping), f"manifest is not a mapping: {unit_dir}")
        topology = _validate_manifest(
            manifest,
            spec,
            unit,
            protocol,
            dataset,
            control_source,
        )
        manifests[unit] = manifest
        if manifests and len(manifests) > 1:
            first_unit = next(iter(manifests))
            first_topology = manifests[first_unit].get("formal_execution_topology")
            _require(
                _json_view(first_topology) == _json_view(topology),
                f"{spec.name} formal_execution_topology differs across units",
            )
        evaluation_files[unit] = index_path
        raw_attempts = cohort.get("attempts")
        _require(isinstance(raw_attempts, list), f"cohort attempts are missing: {index_path}")
        attempt_paths = []
        for raw in raw_attempts:
            _require(isinstance(raw, Mapping) and isinstance(raw.get("path"), str), f"malformed cohort attempt row: {index_path}")
            path = unit_dir / str(raw["path"])
            _require(path.is_dir(), f"cohort attempt path is missing: {path}")
            attempt_paths.append(path)
        discovered_run_paths = {path.parent for path in unit_dir.rglob("run.json")}
        _require(set(attempt_paths) == discovered_run_paths, f"{spec.name} has run bundles outside cohort index in {unit_dir}")
        for path in attempt_paths:
            attempt = _read_attempt(
                path,
                spec,
                unit,
                manifest,
                protocol,
                dataset,
                bearings,
                control_source,
            )
            attempts.append(attempt)
            action_rows += sum(
                1
                for row in _load_jsonl(path / "rollout.jsonl")
                if isinstance(row, Mapping) and row.get("event_type") == "action"
            )

    histories: dict[EpisodeKey, list[Attempt]] = defaultdict(list)
    for attempt in attempts:
        histories[attempt.key].append(attempt)
    statistical: dict[EpisodeKey, Attempt] = {}
    retry_chains = 0
    unresolved: list[EpisodeKey] = []
    for key, history in histories.items():
        ordered = sorted(history, key=lambda item: item.index)
        indices = [item.index for item in ordered]
        _require(indices == list(range(len(indices))), f"{spec.name} retry indices are not contiguous from zero for {key.as_list()}: {indices}")
        profile = [_attempt_pair_contract(item, dataset["budgets"]["core" if spec.scope == "core" else "monitoring"]) for item in ordered]
        _require(all(item == profile[0] for item in profile[1:]), f"{spec.name} retry profile drift for {key.as_list()}")
        statistical_attempts = [item for item in ordered if item.outcome_class == "statistical"]
        _require(len(statistical_attempts) <= 1, f"{spec.name} has multiple statistical attempts for {key.as_list()}")
        if statistical_attempts:
            _require(ordered[-1] is statistical_attempts[0], f"{spec.name} statistical attempt is not final for {key.as_list()}")
            _require(all(item.outcome_class == "provider_error" for item in ordered[:-1]), f"{spec.name} preterminal retry is not provider_error for {key.as_list()}")
            statistical[key] = statistical_attempts[0]
        else:
            _require(all(item.outcome_class == "provider_error" for item in ordered), f"{spec.name} unresolved history is not provider-only for {key.as_list()}")
            unresolved.append(key)
        retry_chains += len(ordered) > 1

    terminal_counts = Counter(str(item.run.get("terminal_status")) for item in attempts if item.outcome_class == "statistical")
    provider_errors = sum(item.outcome_class == "provider_error" for item in attempts)
    nonprovider_failures = sum(
        item.outcome_class == "statistical" and item.run.get("terminal_status") != "submitted"
        for item in attempts
    )
    blockers: list[str] = []
    missing_units = sorted(expected_units - set(manifests))
    if missing_units:
        blockers.append(f"missing registered units: {len(missing_units)}/{len(expected_units)}")
    if len(statistical) != spec.expected:
        blockers.append(f"statistical denominator {len(statistical)}/{spec.expected}")
    if unresolved:
        blockers.append(f"unresolved provider-error episode keys: {len(unresolved)}")
    expected_per_unit = spec.expected // len(spec.units)
    expected_per_task = expected_per_unit // len(spec.tasks)
    for unit in spec.units:
        unit_counts = Counter(key.task_id for key in statistical if (key.seed, key.rotation) == unit)
        for task in spec.tasks:
            if unit_counts[task] != expected_per_task:
                blockers.append(f"{unit[0]}/{unit[1]}/{task} denominator {unit_counts[task]}/{expected_per_task}")
    non_candidate = [
        unit
        for unit, manifest in manifests.items()
        if manifest.get("registered_evidence_class") != "formal"
        or manifest.get("result_role") != "confirmatory"
    ]
    if non_candidate:
        blockers.append(f"units not registered as formal confirmatory evidence: {len(non_candidate)}")
    accepted = not blockers
    execution_topology = (
        None
        if not manifests
        else _json_view(next(iter(manifests.values()))["formal_execution_topology"])
    )
    return ArmAudit(
        spec, tuple(attempts), statistical, manifests, evaluation_files,
        dict(sorted(terminal_counts.items())), provider_errors, nonprovider_failures,
        tuple(sorted(unresolved)), retry_chains, action_rows, accepted, tuple(blockers),
        execution_topology=execution_topology,
    )


def _pair_gate(control: ArmAudit, treatment: ArmAudit, dataset: Mapping[str, Any]) -> dict[str, Any]:
    _require(control.spec.scope == treatment.spec.scope, "paired scopes differ")
    expected_budget = dataset["budgets"]["core" if control.spec.scope == "core" else "monitoring"]
    control_keys = set(control.statistical)
    treatment_keys = set(treatment.statistical)
    matched = control_keys & treatment_keys
    for key in sorted(matched):
        left = control.statistical[key]
        right = treatment.statistical[key]
        _require(_attempt_pair_contract(left, expected_budget) == _attempt_pair_contract(right, expected_budget), f"paired episode contract differs for {key.as_list()}")
    common_units = set(control.manifests) & set(treatment.manifests)
    for unit in sorted(common_units):
        _require(_manifest_pair_contract(control.manifests[unit], expected_budget) == _manifest_pair_contract(treatment.manifests[unit], expected_budget), f"paired unit manifest contract differs for {unit}")
        control_topology = _benchmark_execution_topology(
            control.manifests[unit].get("formal_execution_topology"),
            f"control formal_execution_topology at {unit}",
        )
        treatment_topology = _graph_execution_topology(
            treatment.manifests[unit].get("formal_execution_topology"),
            f"treatment formal_execution_topology at {unit}",
        )
        _require(
            treatment_topology["benchmark_formal_execution_topology"]
            == control_topology,
            f"paired Benchmark/Data Factory formal_execution_topology differs for {unit}",
        )
    exact_keys = control_keys == treatment_keys and len(control_keys) == control.spec.expected
    accepted = control.accepted and treatment.accepted and exact_keys
    blockers: list[str] = []
    if not control.accepted:
        blockers.append(f"{control.spec.name} arm gate unaccepted")
    if not treatment.accepted:
        blockers.append(f"{treatment.spec.name} arm gate unaccepted")
    if not exact_keys:
        blockers.append(f"exact matched statistical keys {len(matched)}/{control.spec.expected}")
    return {
        "accepted": accepted,
        "expected_pairs": control.spec.expected,
        "matched_statistical_keys": len(matched),
        "control_only_keys": len(control_keys - treatment_keys),
        "treatment_only_keys": len(treatment_keys - control_keys),
        "blockers": blockers,
    }


def _execution_topology_binding(
    audits: Mapping[str, ArmAudit],
) -> dict[str, Any]:
    generic = [
        audits[name].execution_topology
        for name in ("generic_core", "generic_replay")
        if audits[name].execution_topology is not None
    ]
    graph = [
        audits[name].execution_topology
        for name in ("graph_core", "graph_replay")
        if audits[name].execution_topology is not None
    ]
    if generic:
        _require(
            all(value == generic[0] for value in generic[1:]),
            "Generic formal_execution_topology differs across core/replay arms",
        )
    if graph:
        _require(
            all(value == graph[0] for value in graph[1:]),
            "Graph formal_execution_topology differs across core/replay arms",
        )
    benchmark_topology = None if not generic else generic[0]
    graph_topology = None if not graph else graph[0]
    shared = None
    if benchmark_topology is not None and graph_topology is not None:
        _require(
            graph_topology["benchmark_formal_execution_topology"]
            == benchmark_topology,
            "Generic/Graph shared Benchmark/Data Factory formal_execution_topology differs",
        )
        shared = benchmark_topology
    return {
        "benchmark_control": _json_view(benchmark_topology),
        "graph_treatment": _json_view(graph_topology),
        "shared_benchmark_data_factory": _json_view(shared),
    }


def _arm_view(audit: ArmAudit) -> dict[str, Any]:
    return {
        "root": _display(audit.spec.root),
        "root_present": audit.spec.root.is_dir(),
        "accepted": audit.accepted,
        "expected_statistical_outcomes": audit.spec.expected,
        "statistical_outcomes": len(audit.statistical),
        "failure_denominator": len(audit.statistical),
        "attempt_leaves": len(audit.attempts),
        "exact_six_attempts": len(audit.attempts),
        "provider_error_attempts": audit.provider_errors,
        "unresolved_provider_error_keys": len(audit.unresolved_provider_keys),
        "nonprovider_terminal_failures_retained": audit.nonprovider_failures,
        "retry_chains": audit.retry_chains,
        "unit_manifests": len(audit.manifests),
        "canonical_action_rows": audit.action_rows,
        "terminal_counts": dict(audit.terminal_counts),
        "blockers": list(audit.blockers),
    }


def _transition_validity(states: Sequence[str]) -> float:
    if not states:
        return 0.0
    if len(states) == 1:
        return 1.0
    valid = sum(
        right in ALLOWED_TRANSITIONS.get(left, set())
        for left, right in zip(states, states[1:])
    )
    return valid / (len(states) - 1)


def _graph_state_summary(audit: ArmAudit) -> dict[str, Any]:
    _require(audit.accepted, "Graph state summary requires an accepted arm")
    _require(not audit.spec.control, "Graph state summary cannot consume a control arm")
    expected_per_task = audit.spec.expected // len(audit.spec.tasks)
    result: dict[str, Any] = {}
    for task in audit.spec.tasks:
        attempts = [
            attempt
            for key, attempt in sorted(audit.statistical.items())
            if key.task_id == task
        ]
        _require(
            len(attempts) == expected_per_task,
            f"accepted Graph state denominator drift for {task}",
        )
        validities = [_transition_validity(attempt.states) for attempt in attempts]
        recover_counts = [attempt.states.count("Recover") for attempt in attempts]
        total_steps = sum(len(attempt.states) for attempt in attempts)
        result[task] = {
            "episodes": len(attempts),
            "mean_transition_validity": sum(validities) / len(validities),
            "all_transitions_valid_rate": sum(value == 1.0 for value in validities)
            / len(validities),
            "recover_episode_rate": sum(value > 0 for value in recover_counts)
            / len(recover_counts),
            "mean_recover_visits": sum(recover_counts) / len(recover_counts),
            "state_coverage": [
                state
                for state in GRAPH_STATE_ORDER
                if any(state in attempt.states for attempt in attempts)
            ],
            "state_step_occupancy_proportion": {
                state: (
                    sum(attempt.states.count(state) for attempt in attempts)
                    / total_steps
                    if total_steps
                    else 0.0
                )
                for state in GRAPH_STATE_ORDER
            },
            "state_episode_visitation_rate": {
                state: sum(state in attempt.states for attempt in attempts)
                / len(attempts)
                for state in GRAPH_STATE_ORDER
            },
        }
    return result


def _private_records(audit: ArmAudit, dataset: Mapping[str, Any]) -> list[dict[str, Any]]:
    _require(audit.accepted, f"private evaluator rows cannot be read before {audit.spec.name} accepts")
    records: dict[EpisodeKey, dict[str, Any]] = {}
    rotations = {str(row["run"]): row for row in dataset["split"]["rotations"]}
    for unit, path in sorted(audit.evaluation_files.items()):
        _require(path.is_file(), f"accepted unit lacks canonical cohort index: {path}")
        try:
            cohort = validate_cohort_index(path)
        except (OSError, ValueError) as exc:
            raise FinalizationError(f"accepted cohort index failed validation: {path}: {exc}") from exc
        test_fold = rotations[unit[1]]["test"]
        allowed_bearings = set(str(item) for item in dataset["split"]["folds"][test_fold])
        for value in cohort["records"]:
            _require(isinstance(value, Mapping), f"evaluator row is not a mapping: {path}")
            key = EpisodeKey(unit[0], str(value.get("rotation")), str(value.get("sample_id")), str(value.get("task_id")))
            _require(key in audit.statistical, f"evaluator row is outside accepted denominator: {key.as_list()}")
            _require(key not in records, f"duplicate evaluator row: {key.as_list()}")
            bearing = str(value.get("bearing_id"))
            _require(bearing in allowed_bearings, f"evaluator bearing is outside test fold for {key.as_list()}")
            public_metrics = audit.statistical[key].metrics
            _require(value.get("evaluation") == public_metrics, f"private/public evaluator result mismatch for {key.as_list()}")
            row = dict(value)
            row["pair_run"] = f"seed_{unit[0]}:{unit[1]}"
            records[key] = row
    _require(set(records) == set(audit.statistical), f"accepted {audit.spec.name} denominator is missing evaluator rows")
    return [records[key] for key in sorted(records)]


def _registered_endpoints(
    protocol: Mapping[str, Any], tasks: Sequence[str]
) -> dict[str, tuple[str, ...]]:
    analysis = protocol["analysis"]
    task_endpoints = analysis["task_endpoints"]
    rollout_endpoints = tuple(str(value) for value in analysis["rollout_endpoints"])
    return {
        task: tuple(str(value) for value in task_endpoints[task])
        + rollout_endpoints
        for task in tasks
    }


def _filter_endpoints(
    result: Mapping[str, Any], endpoints: Mapping[str, Sequence[str]]
) -> dict[str, Any]:
    estimates = result["estimate"]
    intervals = result["bearing_bootstrap_95ci"]
    valid = result["bearing_bootstrap_valid_replicates"]
    _require(
        set(estimates) == set(endpoints),
        "accepted analysis has the wrong registered task set",
    )
    filtered_estimates: dict[str, dict[str, Any]] = {}
    filtered_intervals: dict[str, dict[str, Any]] = {}
    filtered_valid: dict[str, dict[str, Any]] = {}
    for task, registered in endpoints.items():
        metrics = estimates[task]
        missing = [metric for metric in registered if metric not in metrics]
        _require(not missing, f"accepted cohort lacks registered endpoints for {task}: {missing}")
        filtered_estimates[task] = {metric: metrics[metric] for metric in registered}
        filtered_intervals[task] = {
            metric: intervals[task][metric] for metric in registered
        }
        filtered_valid[task] = {metric: valid[task][metric] for metric in registered}
    return {
        "estimate": filtered_estimates,
        "bearing_bootstrap_95ci": filtered_intervals,
        "bearing_bootstrap_valid_replicates": filtered_valid,
        "bootstrap_iterations": result["bootstrap_iterations"],
        "seed": result["seed"],
        "direction": result["direction"],
        "evidence_class": EVIDENCE_CLASS,
        "registered_evidence_class": "formal",
        "result_role": "confirmatory",
    }


def _absolute_summary(
    rows: Sequence[Mapping[str, Any]],
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    tasks: Sequence[str],
    *,
    replay_missing_score_policy_id: str | None,
) -> dict[str, Any]:
    config = protocol["analysis"]["bootstrap"]
    diagnosis_classes = tuple(
        str(value) for value in dataset["tasks"]["diagnosis"]["labels"]
    )
    summary = aggregate_results(
        rows,
        diagnosis_classes=diagnosis_classes,
        replay_missing_score_policy_id=replay_missing_score_policy_id,
    )
    intervals, valid = bearing_bootstrap_intervals(
        rows,
        iterations=int(config["iterations"]),
        seed=int(config["seed"]),
        diagnosis_classes=diagnosis_classes,
        replay_missing_score_policy_id=replay_missing_score_policy_id,
    )
    endpoints = _registered_endpoints(protocol, tasks)
    _require(set(summary) == set(tasks), "accepted arm summary has the wrong task set")
    filtered_summary: dict[str, dict[str, Any]] = {}
    filtered_intervals: dict[str, dict[str, Any]] = {}
    filtered_valid: dict[str, dict[str, Any]] = {}
    for task, registered in endpoints.items():
        task_summary = summary[task]
        view: dict[str, Any] = {
            "episodes": task_summary["episodes"],
            "bearings": task_summary["bearings"],
            "task": {},
            "rollout": {},
        }
        if "evaluation_contract" in task_summary:
            view["evaluation_contract"] = task_summary["evaluation_contract"]
        if task == REPLAY_TASKS[0]:
            required_reporting = dataset["tasks"]["monitoring"][
                "missing_assigned_score_policy"
            ]["required_reporting"]
            task_values = task_summary.get("task")
            _require(
                isinstance(task_values, Mapping),
                "accepted replay arm lacks task score accounting",
            )
            missing_reporting = [
                name for name in required_reporting if name not in task_values
            ]
            _require(
                not missing_reporting,
                f"accepted replay arm lacks required score accounting: {missing_reporting}",
            )
            view["task"].update(
                {name: task_values[name] for name in required_reporting}
            )
        filtered_intervals[task] = {}
        filtered_valid[task] = {}
        for metric in registered:
            section, name = metric.split(".", 1)
            values = task_summary.get(section)
            _require(
                isinstance(values, Mapping) and name in values,
                f"accepted arm lacks registered endpoint {task}.{metric}",
            )
            _require(
                metric in intervals.get(task, {}) and metric in valid.get(task, {}),
                f"accepted arm lacks registered bootstrap endpoint {task}.{metric}",
            )
            view[section][name] = values[name]
            filtered_intervals[task][metric] = intervals[task][metric]
            filtered_valid[task][metric] = valid[task][metric]
        filtered_summary[task] = view
    return {
        "summary": filtered_summary,
        "bearing_bootstrap_95ci": filtered_intervals,
        "bearing_bootstrap_valid_replicates": filtered_valid,
        "bootstrap_iterations": int(config["iterations"]),
        "seed": int(config["seed"]),
        "evidence_class": EVIDENCE_CLASS,
        "registered_evidence_class": "formal",
        "result_role": "confirmatory",
        "replay_missing_score_policy_id": replay_missing_score_policy_id,
    }


def _analyze_scope(
    control: ArmAudit, treatment: ArmAudit, protocol: Mapping[str, Any], dataset: Mapping[str, Any]
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], int]:
    config = protocol["analysis"]["bootstrap"]
    control_rows = _private_records(control, dataset)
    treatment_rows = _private_records(treatment, dataset)
    control_bearings = {
        (row["pair_run"], row["rotation"], row["sample_id"], row["task_id"]): row["bearing_id"]
        for row in control_rows
    }
    treatment_bearings = {
        (row["pair_run"], row["rotation"], row["sample_id"], row["task_id"]): row["bearing_id"]
        for row in treatment_rows
    }
    _require(control_bearings == treatment_bearings, "paired physical-bearing identities differ across arms")
    replay_policy = (
        str(protocol["analysis"]["replay_missing_score_policy_id"])
        if control.spec.scope == "replay"
        else None
    )
    result = paired_bearing_bootstrap_deltas(
        control_rows,
        treatment_rows,
        iterations=int(config["iterations"]),
        seed=int(config["seed"]),
        replay_missing_score_policy_id=replay_policy,
    )
    tasks = control.spec.tasks
    paired = _filter_endpoints(result, _registered_endpoints(protocol, tasks))
    summaries = {
        "control": _absolute_summary(
            control_rows,
            protocol,
            dataset,
            tasks,
            replay_missing_score_policy_id=replay_policy,
        ),
        "treatment": _absolute_summary(
            treatment_rows,
            protocol,
            dataset,
            tasks,
            replay_missing_score_policy_id=replay_policy,
        ),
    }
    return paired, summaries, len(control_rows) + len(treatment_rows)


def build_documents(
    *,
    protocol_path: Path = DEFAULT_PROTOCOL,
    benchmark_formal_run_stamp: str | None = None,
    benchmark_control_protocol_id: str | None = None,
    benchmark_control_profile_id: str | None = None,
    generic_core_root: Path | None = None,
    generic_replay_root: Path | None = None,
    graph_core_root: Path | None = None,
    graph_replay_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol, dataset = _load_protocol(protocol_path)
    authority = protocol["authority"]
    control_source = _benchmark_control_source(
        protocol,
        formal_run_stamp=benchmark_formal_run_stamp,
        protocol_id=benchmark_control_protocol_id,
        profile_id=benchmark_control_profile_id,
    )
    supplied = {
        "generic_core": generic_core_root,
        "generic_replay": generic_replay_root,
        "graph_core": graph_core_root,
        "graph_replay": graph_replay_root,
    }
    missing = [name for name, root in supplied.items() if root is None]
    _require(
        not missing,
        "active-v0.2 external timestamped roots require explicit CLI arguments: "
        + ", ".join(missing),
    )
    roots = {
        name: Path(root).resolve()
        for name, root in supplied.items()
        if root is not None
    }
    for name, root in roots.items():
        _validate_external_root_identity(name, root, control_source)
    design = protocol["registered_design"]
    seeds = tuple(int(item) for item in design["seeds"])
    core_units = tuple((seed, rotation) for seed in seeds for rotation in design["core"]["rotations"])
    replay_units = tuple((seed, rotation) for seed in seeds for rotation in design["replay"]["rotations"])
    specs = {
        "generic_core": ArmSpec("generic_core", "core", roots["generic_core"], True, CORE_TASKS, core_units, 192),
        "graph_core": ArmSpec("graph_core", "core", roots["graph_core"], False, CORE_TASKS, core_units, 192),
        "generic_replay": ArmSpec("generic_replay", "replay", roots["generic_replay"], True, REPLAY_TASKS, replay_units, 24),
        "graph_replay": ArmSpec("graph_replay", "replay", roots["graph_replay"], False, REPLAY_TASKS, replay_units, 24),
    }
    audits = {
        name: _audit_arm(spec, protocol, dataset, control_source)
        for name, spec in specs.items()
    }
    execution_topology = _execution_topology_binding(audits)
    pair_gates = {
        "core": _pair_gate(audits["generic_core"], audits["graph_core"], dataset),
        "replay": _pair_gate(audits["generic_replay"], audits["graph_replay"], dataset),
    }
    all_arm_gates = all(audit.accepted for audit in audits.values())
    all_pair_gates = all(gate["accepted"] for gate in pair_gates.values())
    accepted = all_arm_gates and all_pair_gates
    blockers = [f"{name}: {blocker}" for name, audit in audits.items() for blocker in audit.blockers]
    blockers.extend(f"{scope} pairing: {blocker}" for scope, gate in pair_gates.items() for blocker in gate["blockers"])

    paired: dict[str, Any] | None = None
    arm_summaries: dict[str, Any] | None = None
    graph_state_summaries: dict[str, Any] | None = None
    private_rows = 0
    effect_count = 0
    if accepted:
        core_result, core_summaries, core_rows = _analyze_scope(
            audits["generic_core"], audits["graph_core"], protocol, dataset
        )
        replay_result, replay_summaries, replay_rows = _analyze_scope(
            audits["generic_replay"], audits["graph_replay"], protocol, dataset
        )
        core_result["replay_missing_score_policy_id"] = None
        replay_result["replay_missing_score_policy_id"] = protocol["analysis"][
            "replay_missing_score_policy_id"
        ]
        paired = {"core": core_result, "replay": replay_result}
        arm_summaries = {"core": core_summaries, "replay": replay_summaries}
        graph_state_summaries = {
            "core": _graph_state_summary(audits["graph_core"]),
            "replay": _graph_state_summary(audits["graph_replay"]),
        }
        private_rows = core_rows + replay_rows
        effect_count = sum(
            value is not None
            for cohort in paired.values()
            for metrics in cohort["estimate"].values()
            for value in metrics.values()
        )

    views = {name: _arm_view(audit) for name, audit in audits.items()}
    protocol_identity = _json_view(
        {
            "schema_version": protocol["schema_version"],
            "experiment_id": protocol["experiment_id"],
        }
    )
    readiness = {
        "schema_version": "p2_e1_primary_readiness_v2",
        "gate_id": "P2-E1-GENERIC-BASE-FORMAL-V2",
        "accepted": accepted,
        "status": "accepted_complete_cohorts" if accepted else "incomplete_no_effect_estimate",
        "provider_calls": 0,
        "primary_endpoint": protocol["analysis"]["primary_endpoint"],
        "replay_missing_score_policy_id": protocol["analysis"][
            "replay_missing_score_policy_id"
        ],
        "benchmark_control_source": dict(control_source),
        "formal_execution_topology": execution_topology,
        "evaluator_private_views_read": private_rows,
        "effect_estimates_emitted": effect_count,
        "protocol": _display(protocol_path),
        "dataset_protocol": _display(Path(protocol["_dataset_path"])),
        "authority": {
            "control": "Benchmark GenericLLMToolAgent external immutable root",
            "treatment": "P02 GraphDecisionAgent over the same Generic base",
            "legacy_phmskills_graph_roots_included": False,
            "duplicate_reactive_provider_execution_required": False,
            "graph_formal_root_version": authority["treatment"]["formal_root_version"],
        },
        "expected": {"core_per_arm": 192, "replay_per_arm": 24},
        "observed": {
            **views,
            "matched_core_statistical_keys": pair_gates["core"]["matched_statistical_keys"],
            "matched_replay_statistical_keys": pair_gates["replay"]["matched_statistical_keys"],
        },
        "gates": {
            "arms": {name: {"accepted": audit.accepted, "blockers": list(audit.blockers)} for name, audit in audits.items()},
            "paired_cohorts": pair_gates,
            "all_four_arm_gates_accepted": all_arm_gates,
            "both_exact_pairing_gates_accepted": all_pair_gates,
            "bootstrap_permitted": accepted,
        },
        "failure_denominator_policy": {
            "provider_errors_retained_in_retry_history": True,
            "provider_errors_excluded_until_same_profile_retry_terminates": True,
            "natural_nonprovider_terminal_failures_retained": True,
            "accepted_denominators": {"core_per_arm": 192, "replay_per_arm": 24},
        },
        "blockers": blockers,
        "claim_boundary": protocol["claim_boundary"],
    }
    result = {
        "schema_version": "p2_e1_generic_base_formal_v2_result",
        "gate_id": "P2-E1",
        "accepted": accepted,
        "status": "accepted_paired_result" if accepted else "deferred_until_complete_accepted_gates",
        "provider_calls": 0,
        "frozen_profile": _json_view(protocol["frozen_profile"]),
        "benchmark_control_source": _json_view(control_source),
        "formal_execution_topology": execution_topology,
        "protocol_identity": protocol_identity,
        "registered_design": _json_view(protocol["registered_design"]),
        "analysis": _json_view(protocol["analysis"]),
        "evaluator_private_views_read": private_rows,
        "effect_estimates_emitted": effect_count,
        "registered_denominators": {"core_per_arm": 192, "replay_per_arm": 24},
        "registered_endpoints": {
            task: list(_registered_endpoints(protocol, (task,))[task])
            for task in (*CORE_TASKS, *REPLAY_TASKS)
        },
        "replay_missing_score_policy_id": protocol["analysis"][
            "replay_missing_score_policy_id"
        ],
        "direction": "GraphDecisionAgent_minus_Benchmark_GenericLLMToolAgent",
        "arm_summaries": arm_summaries,
        "graph_state_summaries": graph_state_summaries,
        "paired_bearing_bootstrap": paired,
        "primary_endpoint": protocol["analysis"]["primary_endpoint"],
        "gates": {
            "arms": {
                name: {
                    "accepted": audit.accepted,
                    "statistical_outcomes": len(audit.statistical),
                    "expected_statistical_outcomes": audit.spec.expected,
                    "blockers": list(audit.blockers),
                }
                for name, audit in audits.items()
            },
            "paired_cohorts": pair_gates,
            "all_four_arm_gates_accepted": all_arm_gates,
            "both_exact_pairing_gates_accepted": all_pair_gates,
        },
        "blockers": blockers,
        "claim_boundary": (
            "Accepted absolute and paired estimates are available only when accepted=true. "
            "When false, arm_summaries and paired_bearing_bootstrap are null and no "
            "partial-prefix estimate exists."
        ),
    }
    return readiness, result


def audit(**kwargs: Any) -> dict[str, Any]:
    """Compatibility entry point returning the active readiness document."""

    return build_documents(**kwargs)[0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--benchmark-formal-run-stamp", required=True)
    parser.add_argument("--benchmark-control-protocol-id", required=True)
    parser.add_argument("--benchmark-control-profile-id", required=True)
    parser.add_argument("--generic-core-root", type=Path, required=True)
    parser.add_argument("--generic-replay-root", type=Path, required=True)
    parser.add_argument("--graph-core-root", type=Path, required=True)
    parser.add_argument("--graph-replay-root", type=Path, required=True)
    parser.add_argument("--readiness-output", type=Path, default=DEFAULT_READINESS)
    parser.add_argument("--result-output", type=Path, default=DEFAULT_RESULT)
    return parser


def _restore_output(path: Path, original: bytes | None) -> None:
    if original is None:
        if path.exists():
            path.unlink()
        return
    path.write_bytes(original)


def _atomic_write_group(contents: Mapping[Path, str]) -> None:
    originals = {
        path: path.read_bytes() if path.exists() else None for path in contents
    }
    temporary: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in contents.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                temporary[path] = Path(handle.name)
        for path, temporary_path in temporary.items():
            os.replace(temporary_path, path)
            replaced.append(path)
    except Exception:
        for path in reversed(replaced):
            _restore_output(path, originals[path])
        raise
    finally:
        for temporary_path in temporary.values():
            if temporary_path.exists():
                temporary_path.unlink()


def _same_existing_file(left: Path, right: Path) -> bool:
    try:
        return os.path.samefile(left, right)
    except (FileNotFoundError, OSError):
        return False


def _validate_publication_output_paths(
    args: argparse.Namespace,
    *,
    dataset_path: Path,
) -> None:
    outputs = (args.readiness_output, args.result_output)
    resolved_outputs = tuple(path.resolve() for path in outputs)
    _require(
        resolved_outputs[0] != resolved_outputs[1]
        and not _same_existing_file(outputs[0], outputs[1]),
        "readiness and result outputs must be distinct non-hardlinked paths",
    )

    roots = tuple(
        Path(root).resolve()
        for root in (
            args.generic_core_root,
            args.generic_replay_root,
            args.graph_core_root,
            args.graph_replay_root,
        )
    )
    protected = {args.protocol.resolve(), dataset_path.resolve()}
    for root in roots:
        if root.exists():
            protected.update(path.resolve() for path in root.rglob("cohort_index.json"))
    for output, resolved in zip(outputs, resolved_outputs):
        _require(
            not any(resolved.is_relative_to(root) for root in roots),
            "publication outputs must remain outside all four external immutable roots",
        )
        _require(
            resolved not in protected
            and not any(_same_existing_file(output, path) for path in protected),
            "publication outputs must not overwrite protocol, dataset, or cohort_index inputs",
        )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    loaded_protocol, _dataset = _load_protocol(args.protocol)
    _validate_publication_output_paths(
        args,
        dataset_path=Path(loaded_protocol["_dataset_path"]),
    )
    readiness, result = build_documents(
        protocol_path=args.protocol,
        benchmark_formal_run_stamp=args.benchmark_formal_run_stamp,
        benchmark_control_protocol_id=args.benchmark_control_protocol_id,
        benchmark_control_profile_id=args.benchmark_control_profile_id,
        generic_core_root=args.generic_core_root,
        generic_replay_root=args.generic_replay_root,
        graph_core_root=args.graph_core_root,
        graph_replay_root=args.graph_replay_root,
    )
    _atomic_write_group(
        {
            args.readiness_output: json.dumps(readiness, indent=2, sort_keys=True)
            + "\n",
            args.result_output: json.dumps(result, indent=2, sort_keys=True) + "\n",
        }
    )
    print(
        json.dumps(
            {
                "accepted": readiness["accepted"],
                "effect_estimates_emitted": result["effect_estimates_emitted"],
                "provider_calls": 0,
                "readiness": _display(args.readiness_output),
                "result": _display(args.result_output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
