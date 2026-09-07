#!/usr/bin/env python3
"""Audit P2-E1 Reactive-versus-Graph primary-cohort readiness offline.

This command reads existing canonical RunBundle leaves and the four formal
cohort-acceptance artifacts.  It never calls a model provider and deliberately
does not read evaluator-private ``evaluation.jsonl`` files or aggregate task
metrics.  An incomplete prefix can be structurally valid, but it can never be
accepted as a P2-E1 result.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


P02_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = P02_ROOT.parent
BENCHMARK_ROOT = WORKSPACE_ROOT / "p01-phm-agent-benchmark"
P01_ROOT = WORKSPACE_ROOT / "P01-PHMskills"

DEFAULT_PROTOCOL = BENCHMARK_ROOT / "paper/experiments/datasets/dataset_protocol.yaml"
DEFAULT_REACTIVE_CORE_ROOT = (
    P01_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/phm_skills_primary"
)
DEFAULT_GRAPH_CORE_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/graph_core_primary"
)
DEFAULT_REACTIVE_REPLAY_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/reactive_monitor_primary"
)
DEFAULT_GRAPH_REPLAY_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/graph_monitor_primary"
)
DEFAULT_ACCEPTANCE_PATHS = {
    "reactive_core": P01_ROOT
    / "paper/experiments/results/phm_skills_primary_cohort_acceptance.json",
    "graph_core": P02_ROOT
    / "paper/experiments/results/graph_core_primary_cohort_acceptance.json",
    "reactive_replay": P02_ROOT
    / "paper/experiments/results/reactive_monitor_primary_cohort_acceptance.json",
    "graph_replay": P02_ROOT
    / "paper/experiments/results/graph_monitor_primary_cohort_acceptance.json",
}
DEFAULT_OUTPUT = (
    P02_ROOT / "paper/experiments/results/p2_e1_primary_readiness.json"
)
LEGACY_SUPERSEDED_MESSAGE = (
    "superseded PHMskills-derived P2-E1 CLI; active use is refused. "
    "Use scripts/finalize_p2_e1_generic_base_formal_v2.py."
)

REGISTERED_SEEDS = (20260808, 20260809, 20260810)
REGISTERED_RUNTIME_CONTRACT = "phase1_opaque_sample_vibration_feature_schema_v6"
CORE_TASKS = ("cold_start_fault_diagnosis", "unsupervised_anomaly_detection")
REPLAY_TASKS = ("online_replay_monitoring",)
RUN_BUNDLE_FILES = frozenset(
    {
        "run.json",
        "rollout.jsonl",
        "submission.json",
        "metrics.json",
        "failures.jsonl",
        "artifacts.json",
    }
)
GRAPH_STATES = frozenset(
    {
        "Inspect",
        "Hypothesize",
        "Analyze",
        "Check",
        "Monitor",
        "Revise",
        "Recover",
        "Submit",
    }
)
PRIVATE_FIELD_NAMES = frozenset(
    {"bearing_id", "private_target", "diagnosis_target", "anomaly_target"}
)
UNIT_PATTERN = re.compile(r"^seed_(\d+)$")


class ReadinessError(RuntimeError):
    """Raised when an existing prefix violates the registered contract."""


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
    run: Mapping[str, Any]
    rollout: tuple[Mapping[str, Any], ...]

    @property
    def outcome_class(self) -> str:
        terminal = self.run.get("terminal_status")
        failure_kind = self.run.get("failure_kind")
        if terminal == "failed" and failure_kind == "provider_error":
            return "provider_error"
        if terminal in {None, "running"}:
            return "incomplete"
        return "statistical"


@dataclass(frozen=True)
class ArmSpec:
    report_key: str
    display_name: str
    root: Path
    expected_arm: str
    graph_guided: bool
    tasks: tuple[str, ...]
    rotations: tuple[str, ...]


@dataclass(frozen=True)
class ArmAudit:
    spec: ArmSpec
    attempts: tuple[Attempt, ...]
    statistical_by_key: Mapping[EpisodeKey, Attempt]
    unit_manifests: Mapping[tuple[int, str], Mapping[str, Any]]
    action_rows: int


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReadinessError(message)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReadinessError(f"cannot read valid JSON from {path}: {exc}") from exc


def _load_jsonl(path: Path) -> list[Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ReadinessError(f"cannot read {path}: {exc}") from exc
    values: list[Any] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ReadinessError(
                f"invalid JSONL at {path}:{line_number}: {exc}"
            ) from exc
    return values


def _walk(value: Any) -> Iterable[tuple[str | None, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key), child
            yield from _walk(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield None, child
            yield from _walk(child)


def _known_bearings(protocol: Mapping[str, Any]) -> frozenset[str]:
    folds = protocol.get("split", {}).get("folds", {})
    _require(isinstance(folds, Mapping) and folds, "protocol split.folds missing")
    result: set[str] = set()
    for values in folds.values():
        _require(isinstance(values, list), "protocol fold must be a list")
        result.update(str(value) for value in values)
    return frozenset(result)


def _assert_public(
    documents: Iterable[Any], bearings: frozenset[str], *, label: str
) -> None:
    for document in documents:
        for key, value in _walk(document):
            if key is not None and key.lower() in PRIVATE_FIELD_NAMES:
                raise ReadinessError(f"{label} exposes private field {key!r}")
            if isinstance(value, str) and value in bearings:
                raise ReadinessError(
                    f"{label} exposes evaluator-private bearing value {value!r}"
                )


def _display_path(path: Path) -> str:
    logical = Path(os.path.abspath(path))
    p02_root = Path(os.path.abspath(P02_ROOT))
    workspace_root = Path(os.path.abspath(WORKSPACE_ROOT))
    try:
        return logical.relative_to(p02_root).as_posix()
    except ValueError:
        try:
            return "../" + logical.relative_to(workspace_root).as_posix()
        except ValueError:
            return logical.as_posix()


def _reject_generic_control(spec: ArmSpec) -> None:
    if spec.report_key.startswith("reactive"):
        lowered = [part.lower() for part in spec.root.parts]
        _require(
            not any("generic" in part for part in lowered),
            f"{spec.display_name} cannot use a Generic root: {spec.root}",
        )
        _require(
            spec.expected_arm in {"phm-skills", "reactive"},
            f"{spec.display_name} must be PHMskills/Reactive, not {spec.expected_arm!r}",
        )


def _unit_contract(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "budget": manifest.get("budget"),
        "max_output_tokens_per_turn": manifest.get("max_output_tokens_per_turn"),
        "model_profile": manifest.get("model_profile"),
        "protocol": manifest.get("protocol"),
        "replay_windows_per_episode": manifest.get("replay_windows_per_episode"),
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
    }


def _attempt_contract(attempt: Attempt) -> dict[str, Any]:
    metadata = attempt.run.get("metadata", {})
    return {
        "budget": attempt.run.get("budget"),
        "dataset_protocol": metadata.get("dataset_protocol"),
        "inference_protocol": metadata.get("inference_protocol"),
        "model": metadata.get("model"),
        "provider": metadata.get("provider"),
        "rotation": metadata.get("rotation"),
        "runtime_contract": metadata.get("runtime_contract"),
        "sample_id": metadata.get("sample_id"),
        "seed": metadata.get("seed"),
        "selected_diagnosis_model_id": metadata.get("selected_diagnosis_model_id"),
        "task": attempt.run.get("task"),
        "thinking_mode": metadata.get("thinking_mode"),
    }


def _load_arm(
    spec: ArmSpec,
    protocol: Mapping[str, Any],
    registered_seeds: tuple[int, ...],
) -> ArmAudit:
    _reject_generic_control(spec)
    if not spec.root.exists():
        return ArmAudit(spec, (), {}, {}, 0)
    _require(spec.root.is_dir(), f"arm root is not a directory: {spec.root}")

    bearings = _known_bearings(protocol)
    attempts: list[Attempt] = []
    manifests: dict[tuple[int, str], Mapping[str, Any]] = {}
    action_rows = 0
    for seed_dir in sorted(path for path in spec.root.glob("seed_*") if path.is_dir()):
        match = UNIT_PATTERN.fullmatch(seed_dir.name)
        _require(match is not None, f"invalid seed directory: {seed_dir}")
        seed = int(match.group(1))
        _require(seed in registered_seeds, f"unregistered seed in {seed_dir}")
        for unit_dir in sorted(path for path in seed_dir.iterdir() if path.is_dir()):
            rotation = unit_dir.name
            _require(rotation in spec.rotations, f"unregistered rotation in {unit_dir}")
            manifest_path = unit_dir / "run_manifest.json"
            _require(manifest_path.is_file(), f"run manifest missing: {manifest_path}")
            manifest = _load_json(manifest_path)
            _require(isinstance(manifest, Mapping), f"manifest is not an object: {manifest_path}")
            _require(
                manifest.get("arm") == spec.expected_arm,
                f"{spec.display_name} manifest arm is {manifest.get('arm')!r}, expected {spec.expected_arm!r}",
            )
            _require(manifest.get("seed") == seed, f"manifest seed mismatch: {manifest_path}")
            _require(
                manifest.get("rotation") == rotation,
                f"manifest rotation mismatch: {manifest_path}",
            )
            _require(
                tuple(manifest.get("tasks", ())) == spec.tasks,
                f"manifest task set/order mismatch: {manifest_path}",
            )
            if spec.graph_guided:
                _require(
                    manifest.get("graph_policy_profile") == "full",
                    f"Graph primary must use graph_policy_profile=full: {manifest_path}",
                )
            manifests[(seed, rotation)] = manifest

            episodes = unit_dir / "episodes"
            _require(episodes.is_dir(), f"episodes root missing: {episodes}")
            leaf_paths = sorted(
                path for path in episodes.glob("*/*/*/attempt-*") if path.is_dir()
            )
            for path in leaf_paths:
                names = {item.name for item in path.iterdir()}
                _require(
                    names == RUN_BUNDLE_FILES,
                    f"non-exact-six attempt leaf {path}: {sorted(names)}",
                )
                run = _load_json(path / "run.json")
                submission = _load_json(path / "submission.json")
                metrics = _load_json(path / "metrics.json")
                artifacts = _load_json(path / "artifacts.json")
                rollout_raw = _load_jsonl(path / "rollout.jsonl")
                failures = _load_jsonl(path / "failures.jsonl")
                _require(isinstance(run, Mapping), f"run.json is not an object: {path}")
                rollout = tuple(row for row in rollout_raw if isinstance(row, Mapping))
                _assert_public(
                    (run, submission, metrics, artifacts, rollout, failures),
                    bearings,
                    label=str(path),
                )

                relative = path.relative_to(episodes)
                _require(len(relative.parts) == 4, f"invalid attempt path: {path}")
                path_rotation, sample_id, task_id, attempt_name = relative.parts
                _require(path_rotation == rotation, f"rotation/path mismatch: {path}")
                _require(task_id in spec.tasks, f"unexpected task in {path}")
                _require(
                    attempt_name.startswith("attempt-")
                    and attempt_name.removeprefix("attempt-").isdigit(),
                    f"invalid attempt directory name: {path}",
                )
                metadata = run.get("metadata", {})
                _require(isinstance(metadata, Mapping), f"run metadata missing: {path}")
                key = EpisodeKey(seed, rotation, sample_id, task_id)
                _require(
                    tuple(metadata.get("episode_key", ()))
                    == (rotation, sample_id, task_id),
                    f"episode key/path mismatch: {path}",
                )
                _require(metadata.get("seed") == seed, f"run seed mismatch: {path}")
                _require(
                    metadata.get("arm") == spec.expected_arm,
                    f"run arm mismatch in {path}: {metadata.get('arm')!r}",
                )
                _require(
                    metadata.get("attempt_index")
                    == int(attempt_name.removeprefix("attempt-")),
                    f"attempt index/path mismatch: {path}",
                )
                model_profile = manifest.get("model_profile", {})
                _require(
                    isinstance(model_profile, Mapping),
                    f"manifest model_profile missing: {manifest_path}",
                )
                expected_metadata = {
                    "dataset_protocol": manifest.get("protocol"),
                    "inference_protocol": model_profile.get("protocol"),
                    "model": model_profile.get("model_id"),
                    "provider": model_profile.get("provider"),
                    "rotation": rotation,
                    "runtime_contract": manifest.get("runtime_contract"),
                    "sample_id": sample_id,
                    "seed": seed,
                    "selected_diagnosis_model_id": manifest.get(
                        "selected_diagnosis_model_id"
                    ),
                    "task_id": task_id,
                }
                for field, expected_value in expected_metadata.items():
                    _require(
                        metadata.get(field) == expected_value,
                        f"run/manifest {field} mismatch in {path}",
                    )
                run_budget = run.get("budget", {})
                manifest_budget = manifest.get("budget", {})
                _require(
                    isinstance(run_budget, Mapping)
                    and isinstance(manifest_budget, Mapping),
                    f"run or manifest budget missing: {path}",
                )
                for field, expected_value in manifest_budget.items():
                    _require(
                        run_budget.get(field) == expected_value,
                        f"run/manifest budget {field} mismatch in {path}",
                    )
                task_spec = run.get("task", {})
                _require(
                    isinstance(task_spec, Mapping)
                    and task_spec.get("task_id") == task_id
                    and task_spec.get("task_type") == task_id,
                    f"run TaskSpec/path mismatch: {path}",
                )
                if spec.graph_guided:
                    _require(
                        metadata.get("graph_policy_profile") == "full",
                        f"Graph run is not full-profile: {path}",
                    )
                for row in rollout:
                    if row.get("event_type") != "action":
                        continue
                    action_rows += 1
                    action = row.get("action", {})
                    _require(isinstance(action, Mapping), f"malformed action row: {path}")
                    state = action.get("decision_state")
                    if spec.graph_guided:
                        _require(
                            state in GRAPH_STATES,
                            f"Graph action lacks a registered decision state: {path}",
                        )
                    else:
                        _require(
                            state is None,
                            f"Reactive control unexpectedly carries Graph state {state!r}: {path}",
                        )
                attempts.append(Attempt(path, key, run, rollout))

    grouped: dict[EpisodeKey, list[Attempt]] = {}
    for attempt in attempts:
        grouped.setdefault(attempt.key, []).append(attempt)
    statistical_by_key: dict[EpisodeKey, Attempt] = {}
    for key, key_attempts in grouped.items():
        statistical = [
            attempt for attempt in key_attempts if attempt.outcome_class == "statistical"
        ]
        _require(
            len(statistical) <= 1,
            f"{spec.display_name} key {key.as_list()} has multiple statistical attempts",
        )
        if statistical:
            statistical_by_key[key] = statistical[0]

    if statistical_by_key and spec.graph_guided:
        _require(action_rows > 0, f"{spec.display_name} has no observable Graph actions")
    return ArmAudit(
        spec=spec,
        attempts=tuple(attempts),
        statistical_by_key=statistical_by_key,
        unit_manifests=manifests,
        action_rows=action_rows,
    )


def _registered_counts(
    protocol: Mapping[str, Any], seeds: tuple[int, ...]
) -> dict[str, Any]:
    split = protocol.get("split", {})
    folds = split.get("folds", {})
    rotations = split.get("rotations", [])
    sampling = protocol.get("episode_sampling", {})
    samples_per_bearing = sampling.get("agent_test_samples_per_bearing")
    _require(
        isinstance(samples_per_bearing, int) and samples_per_bearing > 0,
        "invalid agent_test_samples_per_bearing",
    )
    rotation_rows = {
        str(row.get("run")): row for row in rotations if isinstance(row, Mapping)
    }
    core_rotations = tuple(rotation_rows)
    replay_rotations = tuple(str(value) for value in sampling.get("monitoring_rotations", ()))
    _require(core_rotations, "no registered core rotations")
    _require(replay_rotations, "no registered monitoring rotations")

    def per_seed_count(selected: tuple[str, ...], tasks: tuple[str, ...]) -> int:
        count = 0
        for rotation in selected:
            _require(rotation in rotation_rows, f"unknown protocol rotation {rotation}")
            fold_id = rotation_rows[rotation].get("test")
            bearings = folds.get(fold_id)
            _require(isinstance(bearings, list), f"test fold missing for {rotation}")
            count += len(bearings) * samples_per_bearing * len(tasks)
        return count

    return {
        "seeds": list(seeds),
        "core_rotations": list(core_rotations),
        "replay_rotations": list(replay_rotations),
        "core_tasks": list(CORE_TASKS),
        "replay_tasks": list(REPLAY_TASKS),
        "expected_core_statistical_outcomes_per_arm": len(seeds)
        * per_seed_count(core_rotations, CORE_TASKS),
        "expected_replay_statistical_outcomes_per_arm": len(seeds)
        * per_seed_count(replay_rotations, REPLAY_TASKS),
    }


def _compare_pair_contracts(
    reactive: ArmAudit, graph: ArmAudit, matched_keys: set[EpisodeKey]
) -> None:
    for key in sorted(matched_keys):
        _require(
            _attempt_contract(reactive.statistical_by_key[key])
            == _attempt_contract(graph.statistical_by_key[key]),
            f"matched run contracts differ for {key.as_list()}",
        )
    matched_units = set(reactive.unit_manifests) & set(graph.unit_manifests)
    for unit in sorted(matched_units):
        _require(
            _unit_contract(reactive.unit_manifests[unit])
            == _unit_contract(graph.unit_manifests[unit]),
            f"matched unit manifests differ for seed/rotation {unit}",
        )


def _arm_counts(audit: ArmAudit, expected: int) -> dict[str, Any]:
    outcome_counts = Counter(attempt.outcome_class for attempt in audit.attempts)
    statistical = len(audit.statistical_by_key)
    return {
        "root": _display_path(audit.spec.root),
        "root_present": audit.spec.root.is_dir(),
        "attempt_leaves": len(audit.attempts),
        "exact_six_attempt_leaves": len(audit.attempts),
        "statistical_outcomes": statistical,
        "provider_error_attempts": outcome_counts["provider_error"],
        "incomplete_attempts": outcome_counts["incomplete"],
        "registered_statistical_outcomes": expected,
        "missing_registered_statistical_outcomes": expected - statistical,
        "completed_fraction": statistical / expected if expected else None,
        "unit_manifests": len(audit.unit_manifests),
        "canonical_action_rows": audit.action_rows,
    }


def _acceptance_state(
    paths: Mapping[str, Path],
    *,
    expected_core: int,
    expected_replay: int,
    registered_seeds: tuple[int, ...],
    core_rotations: tuple[str, ...],
    replay_rotations: tuple[str, ...],
    expected_runtime_contract: str,
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    documents: dict[str, Mapping[str, Any]] = {}
    for key, path in paths.items():
        present = path.is_file()
        declared_accepted = False
        errors: list[str] = []
        if present:
            document = _load_json(path)
            _require(isinstance(document, Mapping), f"acceptance gate is not an object: {path}")
            documents[key] = document
            declared_accepted = document.get("accepted") is True
            scope = "core" if key.endswith("core") else "replay"
            expected_episodes = expected_core if scope == "core" else expected_replay
            rotations = core_rotations if scope == "core" else replay_rotations
            tasks = CORE_TASKS if scope == "core" else REPLAY_TASKS
            expected_runs = len(registered_seeds) * len(rotations)
            expected_mode = "core" if scope == "core" else "monitoring"
            expected_state_evaluation = key.startswith("graph")
            checks = {
                "declared accepted=true": declared_accepted,
                "errors is empty": document.get("errors") == [],
                "expected episode count matches": document.get("expected_episodes")
                == expected_episodes,
                "observed episode count matches": document.get("observed_unique_episodes")
                == expected_episodes,
                "expected run count matches": document.get("expected_runs") == expected_runs,
                "observed run count matches": document.get("observed_runs") == expected_runs,
                "registered seeds match": document.get("seeds") == list(registered_seeds),
                "registered rotations match": document.get("rotations") == list(rotations),
                "registered tasks match": document.get("tasks") == list(tasks),
                "mode matches": document.get("mode") == expected_mode,
                "inference contract required": document.get("inference_contract_required")
                is True,
                "runtime contract matches": document.get("expected_runtime_contract")
                == expected_runtime_contract,
                "state-evaluation requirement matches": document.get(
                    "state_evaluation_required"
                )
                is expected_state_evaluation,
                "acceptance contract present": isinstance(document.get("contract"), Mapping),
                "per-run contracts complete": isinstance(document.get("run_contracts"), Mapping)
                and len(document.get("run_contracts", {})) == expected_runs,
            }
            errors.extend(label for label, passed in checks.items() if not passed)
        else:
            errors.append("acceptance artifact missing")
        result[key] = {
            "path": _display_path(path),
            "present": present,
            "declared_accepted": declared_accepted,
            "contract_valid": not errors,
            "accepted": declared_accepted and not errors,
            "validation_errors": errors,
        }

    for reactive_key, graph_key in (
        ("reactive_core", "graph_core"),
        ("reactive_replay", "graph_replay"),
    ):
        reactive = documents.get(reactive_key)
        graph = documents.get(graph_key)
        if reactive is None or graph is None:
            continue
        if reactive.get("contract") != graph.get("contract"):
            for key in (reactive_key, graph_key):
                result[key]["validation_errors"].append(
                    "Reactive and Graph acceptance contracts differ"
                )
                result[key]["contract_valid"] = False
                result[key]["accepted"] = False
    return result


def build_report(
    *,
    protocol_path: Path = DEFAULT_PROTOCOL,
    reactive_core_root: Path = DEFAULT_REACTIVE_CORE_ROOT,
    graph_core_root: Path = DEFAULT_GRAPH_CORE_ROOT,
    reactive_replay_root: Path = DEFAULT_REACTIVE_REPLAY_ROOT,
    graph_replay_root: Path = DEFAULT_GRAPH_REPLAY_ROOT,
    acceptance_paths: Mapping[str, Path] = DEFAULT_ACCEPTANCE_PATHS,
    registered_seeds: tuple[int, ...] = REGISTERED_SEEDS,
    expected_runtime_contract: str = REGISTERED_RUNTIME_CONTRACT,
) -> dict[str, Any]:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    _require(isinstance(protocol, Mapping), "dataset protocol is not a mapping")
    registered = _registered_counts(protocol, registered_seeds)
    registered["runtime_contract"] = expected_runtime_contract
    core_rotations = tuple(registered["core_rotations"])
    replay_rotations = tuple(registered["replay_rotations"])
    specs = {
        "reactive_core": ArmSpec(
            "reactive_core",
            "Reactive core control (PHMskills sequential policy)",
            reactive_core_root,
            "phm-skills",
            False,
            CORE_TASKS,
            core_rotations,
        ),
        "graph_core": ArmSpec(
            "graph_core",
            "Graph core treatment",
            graph_core_root,
            "graph",
            True,
            CORE_TASKS,
            core_rotations,
        ),
        "reactive_replay": ArmSpec(
            "reactive_replay",
            "Reactive replay control",
            reactive_replay_root,
            "reactive",
            False,
            REPLAY_TASKS,
            replay_rotations,
        ),
        "graph_replay": ArmSpec(
            "graph_replay",
            "Graph replay treatment",
            graph_replay_root,
            "graph",
            True,
            REPLAY_TASKS,
            replay_rotations,
        ),
    }
    audits = {
        key: _load_arm(spec, protocol, registered_seeds) for key, spec in specs.items()
    }

    reactive_core_keys = set(audits["reactive_core"].statistical_by_key)
    graph_core_keys = set(audits["graph_core"].statistical_by_key)
    reactive_replay_keys = set(audits["reactive_replay"].statistical_by_key)
    graph_replay_keys = set(audits["graph_replay"].statistical_by_key)
    core_matched = reactive_core_keys & graph_core_keys
    replay_matched = reactive_replay_keys & graph_replay_keys
    _compare_pair_contracts(audits["reactive_core"], audits["graph_core"], core_matched)
    _compare_pair_contracts(
        audits["reactive_replay"], audits["graph_replay"], replay_matched
    )

    expected_core = registered["expected_core_statistical_outcomes_per_arm"]
    expected_replay = registered["expected_replay_statistical_outcomes_per_arm"]
    core_complete = (
        len(reactive_core_keys) == expected_core
        and len(graph_core_keys) == expected_core
        and reactive_core_keys == graph_core_keys
    )
    replay_complete = (
        len(reactive_replay_keys) == expected_replay
        and len(graph_replay_keys) == expected_replay
        and reactive_replay_keys == graph_replay_keys
    )
    acceptance = _acceptance_state(
        acceptance_paths,
        expected_core=expected_core,
        expected_replay=expected_replay,
        registered_seeds=registered_seeds,
        core_rotations=core_rotations,
        replay_rotations=replay_rotations,
        expected_runtime_contract=expected_runtime_contract,
    )
    all_gates_accepted = all(item["accepted"] for item in acceptance.values())
    accepted = core_complete and replay_complete and all_gates_accepted

    blockers: list[str] = []
    if not core_complete:
        blockers.append(
            f"core cohort incomplete: {len(core_matched)}/{expected_core} exact matched statistical keys"
        )
    if not replay_complete:
        blockers.append(
            f"replay cohort incomplete: {len(replay_matched)}/{expected_replay} exact matched statistical keys"
        )
    missing_gates = [key for key, item in acceptance.items() if not item["accepted"]]
    if missing_gates:
        blockers.append("formal cohort gates not accepted: " + ", ".join(missing_gates))

    arm_counts = {
        "reactive_core": _arm_counts(audits["reactive_core"], expected_core),
        "graph_core": _arm_counts(audits["graph_core"], expected_core),
        "reactive_replay": _arm_counts(audits["reactive_replay"], expected_replay),
        "graph_replay": _arm_counts(audits["graph_replay"], expected_replay),
    }
    return {
        "schema_version": "p2_e1_primary_readiness_v1",
        "gate_id": "P2-E1",
        "accepted": accepted,
        "status": "accepted_complete_cohort" if accepted else "incomplete_prefix",
        "evidence_class": "provider_free_primary_readiness_audit_not_performance_result",
        "provider_calls": 0,
        "claim_boundary": (
            "This artifact audits canonical prefix structure and formal acceptance readiness only. "
            "It contains no task-effect estimate and cannot support a Reactive-versus-Graph "
            "performance, completion, recovery, reliability, or dynamic-behavior claim while "
            "accepted=false. Generic is prohibited as a Reactive control; provider-error and "
            "other partial attempts remain retained but are never converted into results."
        ),
        "control_identity": {
            "core": "PHMskills sequential policy (arm=phm-skills)",
            "replay": "PHMskills Reactive policy (arm=reactive)",
            "treatment": "PHMskills plus full explicit decision graph (arm=graph)",
            "generic_is_control": False,
        },
        "registered_plan": registered,
        "counts": {
            **arm_counts,
            "matched_statistical_keys": {
                "core": len(core_matched),
                "replay": len(replay_matched),
            },
            "unmatched_current_statistical_keys": {
                "reactive_core_only": len(reactive_core_keys - graph_core_keys),
                "graph_core_only": len(graph_core_keys - reactive_core_keys),
                "reactive_replay_only": len(reactive_replay_keys - graph_replay_keys),
                "graph_replay_only": len(graph_replay_keys - reactive_replay_keys),
            },
        },
        "checks": {
            "control_identity_is_reactive_not_generic": True,
            "all_existing_attempt_leaves_exact_six": True,
            "all_existing_public_bundles_exclude_private_targets_and_bearings": True,
            "at_most_one_statistical_attempt_per_episode_key": True,
            "provider_errors_retained_as_nonstatistical_attempts": True,
            "current_matched_core_contracts_identical": True,
            "current_matched_replay_contracts_identical": True,
            "reactive_actions_exclude_graph_state": True,
            "graph_actions_use_registered_full_profile_states": True,
            "core_registered_coverage_complete": core_complete,
            "replay_registered_coverage_complete": replay_complete,
            "all_four_formal_cohort_gates_accepted": all_gates_accepted,
            "formal_p2_e1_result_eligible": accepted,
        },
        "acceptance_artifacts": acceptance,
        "blockers": blockers,
        "partial_prefix_policy": {
            "aggregate_performance": False,
            "emit_effect_estimate": False,
            "provider_error_is_statistical_outcome": False,
            "natural_nonprovider_terminal_is_retained_statistical_outcome": True,
        },
    }


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--reactive-core-root", type=Path, default=DEFAULT_REACTIVE_CORE_ROOT)
    parser.add_argument("--graph-core-root", type=Path, default=DEFAULT_GRAPH_CORE_ROOT)
    parser.add_argument("--reactive-replay-root", type=Path, default=DEFAULT_REACTIVE_REPLAY_ROOT)
    parser.add_argument("--graph-replay-root", type=Path, default=DEFAULT_GRAPH_REPLAY_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    parser.error(LEGACY_SUPERSEDED_MESSAGE)
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    report = build_report(
        protocol_path=args.protocol,
        reactive_core_root=args.reactive_core_root,
        graph_core_root=args.graph_core_root,
        reactive_replay_root=args.reactive_replay_root,
        graph_replay_root=args.graph_replay_root,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
