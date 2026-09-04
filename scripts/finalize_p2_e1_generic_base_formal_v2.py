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
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any, Iterable, Mapping, Sequence

import yaml


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT.parent / "p01-phm-agent-benchmark"
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
REPLAY_MECHANISM_ENDPOINTS = (
    "rollout.grounded_completion",
    "rollout.submission_rate",
    "rollout.budget_exhaustion",
    "rollout.valid_tool_call_rate",
    "rollout.repeated_action_ratio",
    "rollout.grounded_recovery_success",
    "rollout.recovery_coverage",
    "rollout.steps_to_recovery",
    "rollout.steps",
)
PRIMARY_ENDPOINT = {
    "cohort": "replay",
    "task": "online_replay_monitoring",
    "metric": "task.average_precision",
}
EVIDENCE_CLASS = "real_data_formal_candidate"
EXPECTED_SCHEMA = "p2_e1_generic_base_formal_v2"
BENCHMARK_CONTROL_SOURCE_CONTRACT = "p1_p2_joint_generic_control_source_v1"
BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = (
    "benchmark_formal_gitlink_topology_v1"
)
P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = "p2_e1_formal_execution_topology_v1"
BENCHMARK_REPOSITORY = "https://github.com/liq22/phm-agent-benchmark.git"
DATA_FACTORY_REPOSITORY = "https://github.com/PHMbench/phm-data-factory.git"
P2_REPOSITORY = "https://github.com/liq22/P02_agent_langraph.git"
P2_FORMAL_REPRODUCIBILITY_PATHS = (
    "CORE.md",
    "paper/experiments/p2_e1_generic_base_formal_v2.yaml",
    "scripts/run_graph_experiment.py",
    "src/phm_graph_agent",
)
ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID = (
    "benchmark_v0_2_0--paderborn_phase1_v1--runtime_v6--window_v3"
)
P0_ONLY_BENCHMARK_PROFILE_ID = "paper0-paderborn-primary-v1"
ACTIVE_BENCHMARK_CONTROL_PROFILE_ID = "p1-p2-joint-primary-v1"
JOINT_SCHEDULE_ID = "p1_p2_joint_primary_counterbalance_v1"
JOINT_RESUME_IDENTITY_CONTRACT = "joint_primary_schedule_resume_identity_v1"
JOINT_SCHEDULE_ACCEPTANCE_SCHEMA = "joint_primary_schedule_acceptance_v1"
JOINT_RESUME_IDENTITY_FIELDS = (
    "contract", "schedule_id", "joint_profile_id", "joint_formal_run_stamp",
    "ordinal", "scope", "unit_index", "position", "arm", "seed", "rotation",
    "predecessor_job_id", "output",
)
PAIRING_KEY_FIELDS = ("seed", "rotation", "bearing_id", "sample_id", "task_id")
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
    actions: tuple[Mapping[str, Any], ...]
    failures: tuple[Mapping[str, Any], ...]


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
        "schedule_id": JOINT_SCHEDULE_ID,
        "protocol_id": ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
        "profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
        "formal_run_stamp": "from_joint_schedule_acceptance",
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
    _require(control.get("reuse_mode") == "one_joint_generic_execution_shared_by_p1_and_p2", "Generic joint reuse policy drift")
    _require(control.get("duplicate_provider_execution") == "forbidden_within_joint_cohort", "duplicate Generic execution must be forbidden")
    _require(control.get("p0_b3_reuse") == "forbidden", "P0 B3 must not be reused as P2 control")
    expected_root_contract = {
        "schema": "p1_p2_joint_external_timestamped_root_v1",
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "root_layout": (
            "protocol_id/arm_scope/profile_id/run_{formal_run_stamp}/"
            "seed_{seed}/{rotation}/cohort_index.json"
        ),
        "root_resolution": "explicit_cli_root_and_joint_acceptance_required",
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
    _require(
        (control["external_root_contract"].get("core_scope"), control["external_root_contract"].get("replay_scope"))
        == ("joint_generic_core", "joint_generic_replay"),
        "joint Generic root scopes drift",
    )
    _require(
        (treatment["external_root_contract"].get("core_scope"), treatment["external_root_contract"].get("replay_scope"))
        == ("joint_graph_core", "joint_graph_replay"),
        "joint Graph root scopes drift",
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
            "bootstrap_seed_status": "aligned_before_any_accepted_p2_e1_result",
            "bootstrap_seed_basis": "benchmark_statistics_shared_analysis_rules",
            "superseded_bootstrap_seed": 20260820,
            "corrected_bootstrap_seed": 20260808,
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
    _require(
        protocol.get("pairing")
        == {
            "key": list(PAIRING_KEY_FIELDS),
            "require_exact_key_equality": True,
            "require_identical_task_spec": True,
            "require_identical_budget": True,
            "require_identical_world_and_inference_contract": True,
        },
        "joint bearing-level pairing contract drift",
    )
    joint = protocol.get("joint_schedule", {})
    _require(
        joint.get("schedule_id") == JOINT_SCHEDULE_ID
        and joint.get("profile_id") == ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
        and joint.get("resume_identity_contract") == JOINT_RESUME_IDENTITY_CONTRACT
        and joint.get("resume_identity_fields") == list(JOINT_RESUME_IDENTITY_FIELDS),
        "joint schedule identity registration drift",
    )
    _require(
        joint.get("scheduler_scopes") == ["core", "monitoring"]
        and joint.get("graph_execution_scopes") == ["joint_graph_core", "joint_graph_replay"]
        and joint.get("generic_control_scopes") == ["joint_generic_core", "joint_generic_replay"]
        and joint.get("p0_b3_profile_id") == P0_ONLY_BENCHMARK_PROFILE_ID
        and joint.get("p0_b3_eligible_as_control") is False,
        "joint/P0 authority boundary drift",
    )
    analysis = protocol.get("analysis", {})
    bootstrap = analysis.get("bootstrap", {})
    _require(bootstrap.get("method") == "paired_bearing_cluster_percentile_bootstrap", "bootstrap method drift")
    _require(bootstrap.get("cluster_unit") == "physical_bearing", "bootstrap cluster must be physical bearing")
    _require(bootstrap.get("iterations") == 2000, "P2-E1 requires exactly 2,000 bootstrap resamples")
    _require(bootstrap.get("seed") == 20260808, "P2-E1 bootstrap seed must match the shared Benchmark seed 20260808")
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
        analysis.get("replay_mechanism")
        == {
            "role": "secondary_explanatory_not_task_performance",
            "task": REPLAY_TASKS[0],
            "source": "accepted_exact_six_public_rollout_and_evaluator_views",
            "pairing_key": list(PAIRING_KEY_FIELDS),
            "expected_pairs": 24,
            "endpoints": list(REPLAY_MECHANISM_ENDPOINTS),
            "graph_projection": {
                "states": list(GRAPH_STATE_ORDER),
                "transition_relation": "base_v6_51_edge",
                "monitor_and_revise_reachable": False,
            },
            "case_selection": "none_full_cohort_only",
            "evaluator_private_targets_used": False,
            "reasoning_traces_used": False,
        },
        "registered replay mechanism projection drift",
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


def _joint_schedule_acceptance(path: Path | None) -> dict[str, Any]:
    _require(
        path is not None,
        "P2-E1 result is blocked without --joint-schedule-acceptance",
    )
    value = _load_json(Path(path))
    _require(isinstance(value, Mapping), "joint schedule acceptance must be a mapping")
    acceptance = dict(value)
    expected_fields = {
        "schema_version", "accepted", "schedule_id", "joint_profile_id",
        "joint_formal_run_stamp", "resume_identity_contract", "job_count",
        "completed_prefix_length", "order_validated", "runner_contracts_accepted",
        "duplicate_provider_execution", "p0_b3_control_reuse", "pair_key_fields",
        "resume_identities",
    }
    _require(set(acceptance) == expected_fields, "joint schedule acceptance fields drift")
    _require(
        acceptance.get("schema_version") == JOINT_SCHEDULE_ACCEPTANCE_SCHEMA
        and acceptance.get("accepted") is True
        and acceptance.get("schedule_id") == JOINT_SCHEDULE_ID
        and acceptance.get("joint_profile_id") == ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
        and acceptance.get("resume_identity_contract") == JOINT_RESUME_IDENTITY_CONTRACT,
        "joint schedule acceptance identity drift",
    )
    stamp = acceptance.get("joint_formal_run_stamp")
    _require(
        isinstance(stamp, str) and FORMAL_RUN_STAMP_PATTERN.fullmatch(stamp) is not None,
        "joint schedule acceptance run stamp must match YYYYMMDDTHHMMSSZ",
    )
    _require(
        acceptance.get("job_count") == 45
        and acceptance.get("completed_prefix_length") == 45
        and acceptance.get("order_validated") is True
        and acceptance.get("runner_contracts_accepted") is True
        and acceptance.get("duplicate_provider_execution") is False
        and acceptance.get("p0_b3_control_reuse") is False
        and acceptance.get("pair_key_fields") == list(PAIRING_KEY_FIELDS),
        "joint schedule acceptance did not close all pre-result gates",
    )
    identities = acceptance.get("resume_identities")
    _require(isinstance(identities, list) and len(identities) == 45, "joint schedule acceptance must contain 45 resume identities")
    arms = ("Generic", "PHMskills", "Graph")
    outputs: set[str] = set()
    previous_id: str | None = None
    for ordinal, raw in enumerate(identities):
        _require(isinstance(raw, Mapping) and set(raw) == set(JOINT_RESUME_IDENTITY_FIELDS), f"joint resume identity {ordinal} fields drift")
        identity = dict(raw)
        if ordinal < 36:
            scope = "core"
            unit_index, position = divmod(ordinal, 3)
        else:
            scope = "monitoring"
            unit_index, position = divmod(ordinal - 36, 3)
        order = arms[unit_index % 3 :] + arms[: unit_index % 3]
        arm = order[position]
        expected_job_id = f"{scope}-{unit_index:02d}-position-{position}-{arm.lower()}"
        seed = (20260808, 20260809, 20260810)[unit_index // 4] if scope == "core" else (20260808, 20260809, 20260810)[unit_index]
        rotation = f"rotation_{unit_index % 4}" if scope == "core" else "rotation_0"
        expected = {
            "contract": JOINT_RESUME_IDENTITY_CONTRACT,
            "schedule_id": JOINT_SCHEDULE_ID,
            "joint_profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
            "joint_formal_run_stamp": stamp,
            "ordinal": ordinal,
            "scope": scope,
            "unit_index": unit_index,
            "position": position,
            "arm": arm,
            "seed": seed,
            "rotation": rotation,
            "predecessor_job_id": previous_id,
        }
        _require(
            all(identity.get(field) == expected_value for field, expected_value in expected.items()),
            f"joint resume identity {ordinal} schedule semantics drift",
        )
        output = identity.get("output")
        _require(type(output) is str and Path(output).is_absolute() and str(Path(output).resolve()) == output, f"joint resume identity {ordinal} output is not absolute and normalized")
        _require(output not in outputs, f"joint resume identity {ordinal} duplicates an output")
        if arm in {"Generic", "Graph"}:
            arm_scope = (
                f"joint_generic_{'core' if scope == 'core' else 'replay'}"
                if arm == "Generic"
                else f"joint_graph_{'core' if scope == 'core' else 'replay'}"
            )
            expected_tail = (
                ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
                arm_scope,
                ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
                f"run_{stamp}",
                f"seed_{seed}",
                rotation,
            )
            _require(
                Path(output).parts[-len(expected_tail) :] == expected_tail,
                f"joint resume identity {ordinal} output scope/root drift",
            )
        _require(
            P0_ONLY_BENCHMARK_PROFILE_ID not in Path(output).parts
            and not any(part.startswith("b3_generic_") for part in Path(output).parts),
            f"joint resume identity {ordinal} attempts P0 B3 reuse",
        )
        outputs.add(output)
        previous_id = expected_job_id
    return _json_view(acceptance)


def _benchmark_control_source(
    protocol: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> dict[str, str]:
    stamp = str(acceptance["joint_formal_run_stamp"])
    registered = protocol["benchmark_control_source"]
    return {
        "contract": str(registered["contract"]),
        "schedule_id": str(registered["schedule_id"]),
        "formal_run_stamp": stamp,
        "protocol_id": str(registered["protocol_id"]),
        "profile_id": str(registered["profile_id"]),
    }


def _validate_external_root_identity(
    name: str,
    root: Path,
    source: Mapping[str, str],
) -> None:
    expected_scopes = {
        "generic_core": "joint_generic_core",
        "generic_replay": "joint_generic_replay",
        "graph_core": "joint_graph_core",
        "graph_replay": "joint_graph_replay",
    }
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
        root.parents[1].name == expected_scopes[name],
        f"{name} root is outside its registered joint arm scope",
    )
    _require(
        len(root.parents) >= 3 and root.parents[2].name == source["protocol_id"],
        f"{name} root is outside the registered Benchmark control protocol",
    )
    _require(
        P0_ONLY_BENCHMARK_PROFILE_ID not in root.parts
        and not any(part.startswith("b3_generic_") for part in root.parts),
        f"{name} root attempts to reuse a P0-only B3 cohort",
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


def _accepted_resume_identity(
    acceptance: Mapping[str, Any],
    spec: ArmSpec,
    unit: tuple[int, str],
) -> dict[str, Any]:
    scope = "monitoring" if spec.scope == "replay" else "core"
    arm = "Generic" if spec.control else "Graph"
    matches = [
        dict(value)
        for value in acceptance["resume_identities"]
        if value.get("scope") == scope
        and value.get("arm") == arm
        and value.get("seed") == unit[0]
        and value.get("rotation") == unit[1]
    ]
    _require(len(matches) == 1, f"joint acceptance lacks one {arm} identity for {unit}")
    return matches[0]


def _validate_manifest(
    manifest: Mapping[str, Any],
    spec: ArmSpec,
    unit: tuple[int, str],
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    control_source: Mapping[str, str],
    schedule_acceptance: Mapping[str, Any],
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
    expected_joint_identity = _accepted_resume_identity(
        schedule_acceptance, spec, unit
    )
    _require(
        expected_joint_identity["output"]
        == str((spec.root / f"seed_{seed}" / rotation).resolve()),
        f"{spec.name} joint acceptance output differs from supplied root at {unit}",
    )
    _require(
        manifest.get("joint_resume_identity") == expected_joint_identity,
        f"{spec.name} manifest joint resume identity drift at {unit}",
    )
    expected_joint_scope = {
        (True, "core"): "joint_generic_core",
        (True, "replay"): "joint_generic_replay",
        (False, "core"): "joint_graph_core",
        (False, "replay"): "joint_graph_replay",
    }[(spec.control, spec.scope)]
    _require(
        manifest.get("joint_execution_scope") == expected_joint_scope,
        f"{spec.name} manifest joint execution scope drift at {unit}",
    )
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
    schedule_acceptance: Mapping[str, Any],
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
    expected_joint_identity = _accepted_resume_identity(
        schedule_acceptance, spec, unit
    )
    expected_joint_scope = {
        (True, "core"): "joint_generic_core",
        (True, "replay"): "joint_generic_replay",
        (False, "core"): "joint_graph_core",
        (False, "replay"): "joint_graph_replay",
    }[(spec.control, spec.scope)]
    _require(
        metadata.get("joint_resume_identity") == expected_joint_identity
        and metadata.get("joint_execution_scope") == expected_joint_scope
        and isinstance(resume_identity, Mapping)
        and resume_identity.get("joint_resume_identity") == expected_joint_identity
        and resume_identity.get("joint_execution_scope") == expected_joint_scope,
        f"{spec.name} attempt joint schedule identity drift at {path}",
    )
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
    public_actions: list[dict[str, Any]] = []
    for position, row in enumerate(bundle.rollout_records[:-1]):
        if not isinstance(row, Mapping) or row.get("event_type") != "action":
            raise FinalizationError(f"malformed canonical action row: {path}")
        _require(
            row.get("index") == position,
            f"canonical action indices are not contiguous at {path}",
        )
        action = row.get("action", {})
        _require(isinstance(action, Mapping), f"malformed action row: {path}")
        action_name = action.get("name")
        arguments = action.get("arguments")
        result = row.get("result")
        usage_delta = row.get("usage_delta")
        _require(
            isinstance(action_name, str) and action_name,
            f"canonical action name is missing: {path}",
        )
        _require(
            isinstance(arguments, Mapping),
            f"canonical action arguments are not a mapping: {path}",
        )
        _require(
            isinstance(result, Mapping) and result.get("status") in {"ok", "error"},
            f"canonical action result is invalid: {path}",
        )
        _require(
            isinstance(usage_delta, Mapping),
            f"canonical action usage_delta is invalid: {path}",
        )
        state = action.get("decision_state")
        if spec.control:
            _require(state is None, f"Generic control carries Graph state {state!r}: {path}")
        else:
            _require(state in GRAPH_STATES, f"Graph action lacks a registered decision state: {path}")
            _require(
                state not in {"Monitor", "Revise"},
                f"base-v6 Graph action entered unreachable state {state!r}: {path}",
            )
            states.append(str(state))
        public_actions.append(
            {
                "index": position,
                "name": action_name,
                "arguments": _json_view(arguments),
                "status": result.get("status"),
                "failure_kind": result.get("failure_kind"),
                "decision_state": state,
                "usage_delta": _json_view(usage_delta),
            }
        )
    terminal = run.get("terminal_status")
    failure_kind = run.get("failure_kind")
    if failure_kind == "provider_error":
        _require(terminal == "failed", f"provider_error is not terminal failed: {path}")
        outcome = "provider_error"
    else:
        _require(terminal not in {None, "running"}, f"nonterminal attempt is not admissible: {path}")
        outcome = "statistical"
    return Attempt(
        path,
        key,
        attempt_index,
        outcome,
        run,
        metrics,
        tuple(states),
        tuple(public_actions),
        tuple(_json_view(bundle.failures)),
    )


def _audit_arm(
    spec: ArmSpec,
    protocol: Mapping[str, Any],
    dataset: Mapping[str, Any],
    control_source: Mapping[str, str],
    schedule_acceptance: Mapping[str, Any],
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
            schedule_acceptance,
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
                schedule_acceptance,
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
    matched_pairing_keys = len(matched)
    control_only_pairing_keys = len(control_keys - treatment_keys)
    treatment_only_pairing_keys = len(treatment_keys - control_keys)
    if control.accepted and treatment.accepted and exact_keys:
        def bearing_keys(audit: ArmAudit) -> set[tuple[Any, ...]]:
            rows = _private_records(audit, dataset)
            return {
                (
                    int(str(row["pair_run"]).split(":", 1)[0].removeprefix("seed_")),
                    str(row["rotation"]),
                    str(row["bearing_id"]),
                    str(row["sample_id"]),
                    str(row["task_id"]),
                )
                for row in rows
            }

        control_pairing = bearing_keys(control)
        treatment_pairing = bearing_keys(treatment)
        matched_pairing = control_pairing & treatment_pairing
        exact_keys = (
            control_pairing == treatment_pairing
            and len(control_pairing) == control.spec.expected
        )
        matched_pairing_keys = len(matched_pairing)
        control_only_pairing_keys = len(control_pairing - treatment_pairing)
        treatment_only_pairing_keys = len(treatment_pairing - control_pairing)
    accepted = control.accepted and treatment.accepted and exact_keys
    blockers: list[str] = []
    if not control.accepted:
        blockers.append(f"{control.spec.name} arm gate unaccepted")
    if not treatment.accepted:
        blockers.append(f"{treatment.spec.name} arm gate unaccepted")
    if not exact_keys:
        blockers.append(
            f"exact matched bearing-level statistical keys "
            f"{matched_pairing_keys}/{control.spec.expected}"
        )
    return {
        "accepted": accepted,
        "pairing_key": list(PAIRING_KEY_FIELDS),
        "expected_pairs": control.spec.expected,
        "matched_statistical_keys": matched_pairing_keys,
        "control_only_keys": control_only_pairing_keys,
        "treatment_only_keys": treatment_only_pairing_keys,
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


def _finite_metric(value: Any, label: str, *, nullable: bool = False) -> float | None:
    if value is None and nullable:
        return None
    _require(
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value)),
        f"{label} must be a finite number" + (" or null" if nullable else ""),
    )
    return float(value)


def _same_metric(
    observed: float | None, expected: float | None, label: str
) -> None:
    if observed is None or expected is None:
        _require(observed is expected, f"{label} nullability differs from canonical rollout")
        return
    _require(
        math.isclose(observed, expected, rel_tol=1e-12, abs_tol=1e-12),
        f"{label} differs from canonical rollout: expected {expected}, observed {observed}",
    )


def _canonical_replay_mechanism_episode(attempt: Attempt) -> dict[str, Any]:
    """Rebuild public replay diagnostics without targets or reasoning traces."""

    _require(
        attempt.key.task_id == REPLAY_TASKS[0],
        "replay mechanism projection received a non-replay attempt",
    )
    raw_metrics = attempt.metrics.get("rollout_metrics")
    _require(
        isinstance(raw_metrics, Mapping),
        f"replay attempt lacks evaluator rollout_metrics: {attempt.path}",
    )
    metrics = dict(raw_metrics)
    _require(
        "steps_to_next_success_after_failure" in metrics,
        f"replay attempt lacks the active recovery metric schema: {attempt.path}",
    )

    signatures: set[str] = set()
    repeated = 0
    executed_actions: list[Mapping[str, Any]] = []
    for action in attempt.actions:
        try:
            signature = json.dumps(
                [action["name"], action["arguments"]],
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise FinalizationError(
                f"cannot build a canonical public action signature at {attempt.path}: {exc}"
            ) from exc
        repeated += signature in signatures
        signatures.add(signature)
        usage_delta = action["usage_delta"]
        tool_calls = usage_delta.get("tool_calls")
        if tool_calls is None or _finite_metric(
            tool_calls, f"tool_calls usage at {attempt.path}"
        ) > 0.0:
            executed_actions.append(action)

    action_count = len(attempt.actions)
    valid_tool_calls = sum(action["status"] == "ok" for action in executed_actions)
    terminal_status = str(attempt.run.get("terminal_status"))
    submitted = float(terminal_status == "submitted")
    budget_exhausted = float(terminal_status == "budget_exhausted")
    repeated_ratio = repeated / action_count if action_count else 0.0
    valid_tool_call_rate = (
        valid_tool_calls / len(executed_actions) if executed_actions else 0.0
    )

    failure_count = len(attempt.failures)
    first_failure_step: int | None = None
    if failure_count:
        raw_step = attempt.failures[0].get("step")
        if raw_step is not None:
            _require(
                type(raw_step) is int and raw_step >= 0,
                f"canonical failure has an invalid step at {attempt.path}",
            )
            first_failure_step = int(raw_step)
    next_success = (
        None
        if first_failure_step is None
        else next(
            (
                int(action["index"])
                for action in attempt.actions
                if int(action["index"]) > first_failure_step
                and action["status"] == "ok"
                and action["name"] != "submit"
            ),
            None,
        )
    )
    corrected_after_failure = next_success is not None

    grounding_axes = (
        "submission_grounding",
        "artifact_lineage_completeness",
        "supporting_reference_validity",
    )
    grounded_completion = float(
        submitted == 1.0
        and all(
            _finite_metric(metrics.get(axis), f"{axis} at {attempt.path}") == 1.0
            for axis in grounding_axes
        )
    )
    grounded_recovery = float(
        failure_count > 0 and corrected_after_failure and grounded_completion == 1.0
    )
    recovery_coverage = grounded_recovery if failure_count else None
    steps_to_recovery = (
        float(int(attempt.actions[-1]["index"]) - first_failure_step)
        if grounded_recovery == 1.0
        and first_failure_step is not None
        and attempt.actions
        else None
    )

    canonical = {
        "rollout.grounded_completion": grounded_completion,
        "rollout.submission_rate": submitted,
        "rollout.budget_exhaustion": budget_exhausted,
        "rollout.valid_tool_call_rate": valid_tool_call_rate,
        "rollout.repeated_action_ratio": repeated_ratio,
        "rollout.grounded_recovery_success": grounded_recovery,
        "rollout.recovery_coverage": recovery_coverage,
        "rollout.steps_to_recovery": steps_to_recovery,
        "rollout.steps": float(action_count),
    }
    for endpoint, expected in canonical.items():
        name = endpoint.split(".", 1)[1]
        observed = _finite_metric(
            metrics.get(name),
            f"evaluator {endpoint} at {attempt.path}",
            nullable=expected is None,
        )
        _same_metric(observed, expected, f"evaluator {endpoint} at {attempt.path}")
    observed_failures = _finite_metric(
        metrics.get("failure_count"), f"evaluator failure_count at {attempt.path}"
    )
    _same_metric(
        observed_failures,
        float(failure_count),
        f"evaluator failure_count at {attempt.path}",
    )
    expected_next_success = (
        None
        if first_failure_step is None or next_success is None
        else float(next_success - first_failure_step)
    )
    observed_next_success = _finite_metric(
        metrics.get("steps_to_next_success_after_failure"),
        f"evaluator steps_to_next_success_after_failure at {attempt.path}",
        nullable=expected_next_success is None,
    )
    _same_metric(
        observed_next_success,
        expected_next_success,
        f"evaluator steps_to_next_success_after_failure at {attempt.path}",
    )
    return {
        "metrics": canonical,
        "action_count": action_count,
        "executed_action_count": len(executed_actions),
        "repeated_action_count": repeated,
        "failure_count": failure_count,
        "corrected_after_failure": corrected_after_failure,
        "terminal_status": terminal_status,
    }


def _summary_metric(
    summary: Mapping[str, Any], task: str, endpoint: str, label: str
) -> float | None:
    section, name = endpoint.split(".", 1)
    try:
        value = summary["summary"][task][section][name]
    except (KeyError, TypeError) as exc:
        raise FinalizationError(f"{label} lacks {task}.{endpoint}") from exc
    return _finite_metric(value, f"{label} {task}.{endpoint}", nullable=value is None)


def _paired_metric(
    paired: Mapping[str, Any], task: str, endpoint: str
) -> float | None:
    try:
        value = paired["estimate"][task][endpoint]
    except (KeyError, TypeError) as exc:
        raise FinalizationError(
            f"paired replay result lacks {task}.{endpoint}"
        ) from exc
    return _finite_metric(
        value, f"paired replay {task}.{endpoint}", nullable=value is None
    )


def _graph_replay_transition_projection(
    audit: ArmAudit, state_summary: Mapping[str, Any]
) -> dict[str, Any]:
    _require(audit.accepted and not audit.spec.control, "Graph projection requires an accepted treatment arm")
    attempts = [attempt for _, attempt in sorted(audit.statistical.items())]
    state_counts: Counter[str] = Counter()
    episode_counts: Counter[str] = Counter()
    transition_counts: Counter[str] = Counter()
    valid_transitions = 0
    transition_opportunities = 0
    all_valid_episodes = 0
    recover_after_failure_opportunities = 0
    recover_after_failure_count = 0
    for attempt in attempts:
        states = attempt.states
        _require(
            len(states) == len(attempt.actions),
            f"Graph state/action cardinality differs at {attempt.path}",
        )
        state_counts.update(states)
        episode_counts.update(set(states))
        episode_valid = bool(states)
        for left, right in zip(states, states[1:]):
            transition_counts[f"{left}->{right}"] += 1
            is_valid = right in ALLOWED_TRANSITIONS.get(left, set())
            valid_transitions += is_valid
            transition_opportunities += 1
            episode_valid = episode_valid and is_valid
        all_valid_episodes += episode_valid
        for index, action in enumerate(attempt.actions[:-1]):
            if action["status"] != "error":
                continue
            recover_after_failure_opportunities += 1
            recover_after_failure_count += attempt.actions[index + 1][
                "decision_state"
            ] == "Recover"

    _require(
        state_counts["Monitor"] == 0 and state_counts["Revise"] == 0,
        "base-v6 replay projection cannot contain Monitor or Revise visits",
    )
    task_summary = state_summary.get(REPLAY_TASKS[0])
    _require(
        isinstance(task_summary, Mapping),
        "Graph replay state summary is missing from the accepted result",
    )
    total_steps = sum(state_counts.values())
    expected_occupancy = {
        state: state_counts[state] / total_steps if total_steps else 0.0
        for state in GRAPH_STATE_ORDER
    }
    expected_visitation = {
        state: episode_counts[state] / len(attempts) for state in GRAPH_STATE_ORDER
    }
    for state in GRAPH_STATE_ORDER:
        _same_metric(
            _finite_metric(
                task_summary["state_step_occupancy_proportion"][state],
                f"Graph replay state occupancy {state}",
            ),
            expected_occupancy[state],
            f"Graph replay state occupancy {state}",
        )
        _same_metric(
            _finite_metric(
                task_summary["state_episode_visitation_rate"][state],
                f"Graph replay state visitation {state}",
            ),
            expected_visitation[state],
            f"Graph replay state visitation {state}",
        )
    return {
        "episodes": len(attempts),
        "action_steps": total_steps,
        "state_visit_counts": {
            state: state_counts[state] for state in GRAPH_STATE_ORDER
        },
        "state_episode_counts": {
            state: episode_counts[state] for state in GRAPH_STATE_ORDER
        },
        "transition_opportunities": transition_opportunities,
        "valid_transition_count": valid_transitions,
        "invalid_transition_count": transition_opportunities - valid_transitions,
        "observed_transition_counts": dict(sorted(transition_counts.items())),
        "all_valid_episode_count": all_valid_episodes,
        "recover_after_failed_action_opportunities": recover_after_failure_opportunities,
        "recover_after_failed_action_count": recover_after_failure_count,
        "monitor_and_revise_visits": 0,
    }


def _replay_mechanism_summary(
    *,
    control: ArmAudit,
    treatment: ArmAudit,
    control_summary: Mapping[str, Any],
    treatment_summary: Mapping[str, Any],
    paired: Mapping[str, Any],
    graph_state_summary: Mapping[str, Any],
    protocol: Mapping[str, Any],
    protocol_identity: Mapping[str, Any],
    benchmark_control_source: Mapping[str, Any],
    formal_execution_topology: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the preregistered full-cohort replay mechanism projection."""

    _require(control.accepted and treatment.accepted, "mechanism projection requires two accepted replay arms")
    control_keys = set(control.statistical)
    treatment_keys = set(treatment.statistical)
    _require(
        control_keys == treatment_keys and len(control_keys) == control.spec.expected == 24,
        "mechanism projection requires the exact 24 paired replay keys",
    )
    episode_values: dict[str, dict[EpisodeKey, dict[str, Any]]] = {
        "control": {
            key: _canonical_replay_mechanism_episode(control.statistical[key])
            for key in sorted(control_keys)
        },
        "treatment": {
            key: _canonical_replay_mechanism_episode(treatment.statistical[key])
            for key in sorted(treatment_keys)
        },
    }
    source_summaries = {
        "control": control_summary,
        "treatment": treatment_summary,
    }
    metric_projection: dict[str, Any] = {}
    for endpoint in REPLAY_MECHANISM_ENDPOINTS:
        arms: dict[str, Any] = {}
        for arm in ("control", "treatment"):
            defined = [
                episode["metrics"][endpoint]
                for episode in episode_values[arm].values()
                if episode["metrics"][endpoint] is not None
            ]
            estimate = sum(defined) / len(defined) if defined else None
            reported = _summary_metric(
                source_summaries[arm], REPLAY_TASKS[0], endpoint, arm
            )
            _same_metric(
                reported,
                estimate,
                f"accepted replay {arm} mechanism {endpoint}",
            )
            arms[arm] = {
                "estimate": estimate,
                "defined_episodes": len(defined),
                "registered_episodes": 24,
            }
        expected_delta = (
            None
            if arms["control"]["estimate"] is None
            or arms["treatment"]["estimate"] is None
            else arms["treatment"]["estimate"] - arms["control"]["estimate"]
        )
        observed_delta = _paired_metric(paired, REPLAY_TASKS[0], endpoint)
        _same_metric(
            observed_delta,
            expected_delta,
            f"accepted replay paired mechanism {endpoint}",
        )
        metric_projection[endpoint] = {
            **arms,
            "graph_minus_generic": observed_delta,
        }

    registration = protocol["analysis"]["replay_mechanism"]
    denominator_view = {}
    for arm, audit in (("control", control), ("treatment", treatment)):
        denominator_view[arm] = {
            "statistical_episodes": len(audit.statistical),
            "attempt_leaves": len(audit.attempts),
            "provider_error_history_attempts": audit.provider_errors,
            "nonsubmitted_or_partial_episodes": audit.nonprovider_failures,
            "natural_nonprovider_terminal_failures": sum(
                attempt.run.get("failure_kind") is not None
                for attempt in audit.statistical.values()
            ),
            "terminal_counts": dict(audit.terminal_counts),
        }
    return {
        "schema_version": "p2_e1_replay_mechanism_v1",
        "accepted": True,
        "role": registration["role"],
        "task": registration["task"],
        "source": registration["source"],
        "protocol_identity": _json_view(protocol_identity),
        "benchmark_control_source": _json_view(benchmark_control_source),
        "formal_execution_topology": _json_view(formal_execution_topology),
        "pairing": {
            "key": list(registration["pairing_key"]),
            "expected_pairs": 24,
            "observed_pairs": len(control_keys),
            "control_only_keys": 0,
            "treatment_only_keys": 0,
        },
        "denominators": denominator_view,
        "metric_projection": metric_projection,
        "graph_state_projection": _graph_replay_transition_projection(
            treatment, graph_state_summary
        ),
        "case_selection": "none_full_cohort_only",
        "evaluator_private_targets_used": False,
        "reasoning_traces_used": False,
    }


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
    joint_schedule_acceptance: Path | None = None,
    generic_core_root: Path | None = None,
    generic_replay_root: Path | None = None,
    graph_core_root: Path | None = None,
    graph_replay_root: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    protocol, dataset = _load_protocol(protocol_path)
    authority = protocol["authority"]
    schedule_acceptance = _joint_schedule_acceptance(joint_schedule_acceptance)
    control_source = _benchmark_control_source(
        protocol,
        schedule_acceptance,
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
        name: _audit_arm(
            spec, protocol, dataset, control_source, schedule_acceptance
        )
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
    protocol_identity = _json_view(
        {
            "schema_version": protocol["schema_version"],
            "experiment_id": protocol["experiment_id"],
        }
    )

    paired: dict[str, Any] | None = None
    arm_summaries: dict[str, Any] | None = None
    graph_state_summaries: dict[str, Any] | None = None
    replay_mechanism: dict[str, Any] | None = None
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
        replay_mechanism = _replay_mechanism_summary(
            control=audits["generic_replay"],
            treatment=audits["graph_replay"],
            control_summary=replay_summaries["control"],
            treatment_summary=replay_summaries["treatment"],
            paired=replay_result,
            graph_state_summary=graph_state_summaries["replay"],
            protocol=protocol,
            protocol_identity=protocol_identity,
            benchmark_control_source=control_source,
            formal_execution_topology=execution_topology,
        )
        private_rows = core_rows + replay_rows
        effect_count = sum(
            value is not None
            for cohort in paired.values()
            for metrics in cohort["estimate"].values()
            for value in metrics.values()
        )

    views = {name: _arm_view(audit) for name, audit in audits.items()}
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
        "joint_schedule_acceptance": schedule_acceptance,
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
        "joint_schedule_acceptance": schedule_acceptance,
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
        "replay_mechanism": replay_mechanism,
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
    parser.add_argument("--joint-schedule-acceptance", type=Path, required=True)
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
    protected = {
        args.protocol.resolve(),
        dataset_path.resolve(),
        args.joint_schedule_acceptance.resolve(),
    }
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
        joint_schedule_acceptance=args.joint_schedule_acceptance,
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
