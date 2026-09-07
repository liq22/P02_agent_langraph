#!/usr/bin/env python3
"""Validate the P2-E0 real-data Graph adapter/world-equivalence gate.

The gate reads already-persisted canonical RunBundle leaves.  It makes no
provider call, does not aggregate performance, and does not inspect the
evaluator-private unit-root ``evaluation.jsonl`` files.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


P02_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = P02_ROOT.parent / "p01-phm-agent-benchmark"
DEFAULT_GENERIC_ROOT = (
    BENCHMARK_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/generic_primary"
    / "seed_20260808/rotation_0"
)
DEFAULT_GRAPH_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/formal/canonical_runbundle_v1/graph_core_primary"
    / "seed_20260808/rotation_0"
)
DEFAULT_PROTOCOL = BENCHMARK_ROOT / "paper/experiments/datasets/dataset_protocol.yaml"
DEFAULT_OUTPUT = P02_ROOT / "paper/experiments/results/p2_e0_adapter_equivalence_acceptance.json"
LEGACY_SUPERSEDED_MESSAGE = (
    "superseded PHMskills-derived P2-E0 CLI; active use is refused. "
    "Use scripts/analyze_p2_e0_generic_base_adapter_equivalence_v2.py."
)

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
PRIVATE_FIELD_NAMES = frozenset(
    {"bearing_id", "private_target", "diagnosis_target", "anomaly_target"}
)
CORE_TASKS = ("cold_start_fault_diagnosis", "unsupervised_anomaly_detection")
GRAPH_STATES = frozenset(
    {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Revise", "Recover", "Submit"}
)
FULL_BUDGET_KEYS = (
    "max_data_bytes",
    "max_data_points",
    "max_llm_turns",
    "max_model_calls",
    "max_operator_calls",
    "max_tool_calls",
    "max_wall_clock_seconds",
    "max_window_reads",
)


class GateError(RuntimeError):
    """Raised when a P2-E0 acceptance invariant is not satisfied."""


@dataclass(frozen=True)
class AttemptLeaf:
    path: Path
    episode_key: tuple[str, str, str]
    run: Mapping[str, Any]
    metrics: Mapping[str, Any]
    rollout: tuple[Mapping[str, Any], ...]

    @property
    def statistical(self) -> bool:
        terminal = self.run.get("terminal_status")
        is_provider_failure = bool(
            terminal == "failed" and self.run.get("failure_kind") == "provider_error"
        )
        return bool(terminal not in {None, "running"} and not is_provider_failure)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def _load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read valid JSON from {path}: {exc}") from exc


def _load_jsonl(path: Path) -> list[Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    values: list[Any] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            values.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise GateError(f"invalid JSONL at {path}:{line_number}: {exc}") from exc
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
    bearings: set[str] = set()
    for values in folds.values():
        _require(isinstance(values, list), "protocol fold must be a list")
        bearings.update(str(value) for value in values)
    return frozenset(bearings)


def _assert_public(documents: Iterable[Any], bearings: frozenset[str], label: str) -> None:
    for document in documents:
        for key, value in _walk(document):
            if key is not None and key.lower() in PRIVATE_FIELD_NAMES:
                raise GateError(f"{label} exposes private field {key!r}")
            if isinstance(value, str) and value in bearings:
                raise GateError(f"{label} exposes private bearing value {value!r}")


def _load_attempts(
    root: Path, protocol: Mapping[str, Any], *, arm_label: str
) -> list[AttemptLeaf]:
    episodes = root / "episodes"
    _require(episodes.is_dir(), f"{arm_label} episodes root missing: {episodes}")
    paths = sorted(path for path in episodes.glob("*/*/*/attempt-*") if path.is_dir())
    _require(paths, f"{arm_label} has no attempt leaves")
    bearings = _known_bearings(protocol)
    attempts: list[AttemptLeaf] = []
    for path in paths:
        filenames = {item.name for item in path.iterdir() if item.is_file()}
        _require(
            filenames == RUN_BUNDLE_FILES,
            f"{arm_label} non-exact-six leaf {path}: {sorted(filenames)}",
        )
        run = _load_json(path / "run.json")
        submission = _load_json(path / "submission.json")
        metrics = _load_json(path / "metrics.json")
        artifacts = _load_json(path / "artifacts.json")
        rollout = _load_jsonl(path / "rollout.jsonl")
        failures = _load_jsonl(path / "failures.jsonl")
        _assert_public((run, submission, metrics, artifacts, rollout, failures), bearings, str(path))
        relative = path.relative_to(episodes)
        _require(len(relative.parts) == 4, f"unexpected attempt path: {path}")
        directory_key = tuple(str(part) for part in relative.parts[:3])
        metadata_key = tuple(str(part) for part in run.get("metadata", {}).get("episode_key", []))
        _require(
            len(metadata_key) == 3 and metadata_key == directory_key,
            f"{arm_label} episode key/path mismatch at {path}",
        )
        _require(
            run.get("metadata", {}).get("attempt_index")
            == int(relative.parts[3].removeprefix("attempt-")),
            f"{arm_label} attempt index/path mismatch at {path}",
        )
        attempts.append(
            AttemptLeaf(
                path=path,
                episode_key=metadata_key,
                run=run,
                metrics=metrics,
                rollout=tuple(row for row in rollout if isinstance(row, Mapping)),
            )
        )
    return attempts


def _statistical_by_key(
    attempts: Sequence[AttemptLeaf], *, arm_label: str
) -> dict[tuple[str, str, str], AttemptLeaf]:
    grouped: dict[tuple[str, str, str], list[AttemptLeaf]] = {}
    for attempt in attempts:
        grouped.setdefault(attempt.episode_key, []).append(attempt)
    result: dict[tuple[str, str, str], AttemptLeaf] = {}
    for key, key_attempts in grouped.items():
        statistical = [attempt for attempt in key_attempts if attempt.statistical]
        _require(
            len(statistical) == 1,
            f"{arm_label} key {key} has {len(statistical)} statistical attempts",
        )
        result[key] = statistical[0]
    return result


def _normal_budget(manifest: Mapping[str, Any]) -> dict[str, Any]:
    raw = manifest.get("budget_protocol", manifest.get("budget", {}))
    _require(isinstance(raw, Mapping), "manifest budget missing")
    return {key: raw.get(key) for key in FULL_BUDGET_KEYS}


def _normal_sampling(manifest: Mapping[str, Any]) -> dict[str, Any]:
    sampling = manifest.get("sampling_identity", {})
    return {
        "seed": manifest.get("seed"),
        "rotation": manifest.get("rotation"),
        "sample_handle": manifest.get("sample_handle"),
        "train_samples_per_bearing": manifest.get("train_samples_per_bearing"),
        "validation_samples_per_bearing": manifest.get("validation_samples_per_bearing"),
        "test_samples_per_bearing": manifest.get("test_samples_per_bearing"),
        "test_sample_selection": manifest.get("test_sample_selection"),
        "resolved_test_samples_per_bearing": sampling.get(
            "resolved_test_samples_per_bearing", manifest.get("test_samples_per_bearing")
        ),
        "sampling_task_family": sampling.get("task_family", "core"),
    }


def _expected_count(protocol: Mapping[str, Any]) -> int:
    split = protocol.get("split", {})
    rotation = next(
        (row for row in split.get("rotations", []) if row.get("run") == "rotation_0"),
        None,
    )
    _require(rotation is not None, "rotation_0 absent from protocol")
    test_bearings = split.get("folds", {}).get(rotation.get("test"))
    samples = protocol.get("episode_sampling", {}).get("agent_test_samples_per_bearing")
    _require(isinstance(test_bearings, list), "rotation_0 test fold missing")
    _require(isinstance(samples, int) and samples > 0, "invalid agent sampling count")
    return len(test_bearings) * samples * len(CORE_TASKS)


def _protocol_sampling(protocol: Mapping[str, Any]) -> dict[str, Any]:
    sampling = protocol.get("episode_sampling", {})
    return {
        "sample_handle": protocol.get("agent_visibility", {}).get("sample_handle"),
        "train_samples_per_bearing": sampling.get("train_samples_per_bearing"),
        "validation_samples_per_bearing": sampling.get("healthy_validation_samples_per_bearing"),
        "test_samples_per_bearing": sampling.get("agent_test_samples_per_bearing"),
        "test_sample_selection": sampling.get("agent_selection"),
    }


def _display_path(path: Path) -> str:
    try:
        return path.relative_to(P02_ROOT).as_posix()
    except ValueError:
        try:
            return "../" + path.relative_to(P02_ROOT.parent).as_posix()
        except ValueError:
            return path.as_posix()


def _terminal_counts(leaves: Iterable[AttemptLeaf]) -> dict[str, int]:
    counts = Counter()
    for leaf in leaves:
        status = str(leaf.run.get("terminal_status"))
        failure = leaf.run.get("failure_kind")
        key = status if failure in {None, status} else f"{status}:{failure}"
        counts[key] += 1
    return dict(sorted(counts.items()))


def _action_contract(
    leaves: Iterable[AttemptLeaf], *, graph: bool, allowed_actions: set[str]
) -> tuple[int, set[str], set[str]]:
    count = 0
    tools: set[str] = set()
    states: set[str] = set()
    for leaf in leaves:
        for row in leaf.rollout:
            if row.get("event_type") != "action":
                continue
            action = row.get("action", {})
            _require(isinstance(action, Mapping), f"invalid action row in {leaf.path}")
            tool = action.get("name")
            _require(isinstance(tool, str) and tool in allowed_actions, f"out-of-surface action in {leaf.path}")
            state = action.get("decision_state")
            if graph:
                _require(isinstance(state, str) and state in GRAPH_STATES, f"Graph action lacks registered decision_state in {leaf.path}")
                states.add(state)
            else:
                _require(state is None, f"Generic action unexpectedly carries decision_state in {leaf.path}")
            tools.add(tool)
            count += 1
    _require(count > 0, "arm has no canonical action rows")
    return count, tools, states


def analyze_gate(generic_root: Path, graph_root: Path, protocol_path: Path) -> dict[str, Any]:
    """Return the accepted P2-E0 report or raise :class:`GateError`."""

    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    _require(isinstance(protocol, Mapping), "dataset protocol must be a mapping")
    generic_manifest = _load_json(generic_root / "run_manifest.json")
    graph_manifest = _load_json(graph_root / "run_manifest.json")
    protocol_id = protocol.get("schema_version")
    _require(
        generic_manifest.get("protocol") == graph_manifest.get("protocol") == protocol_id,
        "dataset protocol identity differs",
    )
    _require(
        generic_manifest.get("seed") == graph_manifest.get("seed") == 20260808,
        "P2-E0 requires seed 20260808",
    )
    _require(
        generic_manifest.get("rotation") == graph_manifest.get("rotation") == "rotation_0",
        "P2-E0 requires rotation_0",
    )
    runtime_contract = "phase1_opaque_sample_vibration_feature_schema_v6"
    _require(
        generic_manifest.get("runtime_contract")
        == graph_manifest.get("runtime_contract")
        == runtime_contract,
        "runtime contract mismatch",
    )
    _require(
        graph_manifest.get("arm") == "graph" and graph_manifest.get("graph_policy_profile") == "full",
        "Graph manifest is not the registered full policy",
    )

    generic_attempts = _load_attempts(generic_root, protocol, arm_label="Generic")
    graph_attempts = _load_attempts(graph_root, protocol, arm_label="Graph")
    generic_units = _statistical_by_key(generic_attempts, arm_label="Generic")
    graph_units = _statistical_by_key(graph_attempts, arm_label="Graph")
    expected = _expected_count(protocol)
    _require(
        len(generic_units) == len(graph_units) == expected == 16,
        "both arms must have 16/16 statistical rotation-0 episode keys",
    )
    _require(set(generic_units) == set(graph_units), "statistical episode keys differ")

    generic_budget = _normal_budget(generic_manifest)
    graph_budget = _normal_budget(graph_manifest)
    _require(generic_budget == graph_budget, "manifest budgets differ")
    for key, value in protocol.get("budgets", {}).get("core", {}).items():
        _require(generic_budget.get(key) == value, f"budget {key} differs from protocol")
    window = generic_manifest.get("window_protocol")
    _require(window == graph_manifest.get("window_protocol") == json.loads(json.dumps(protocol.get("window_protocol"))), "window protocol differs")
    generic_sampling = _normal_sampling(generic_manifest)
    graph_sampling = _normal_sampling(graph_manifest)
    _require(generic_sampling == graph_sampling, "sampling identities differ")
    for key, value in _protocol_sampling(protocol).items():
        _require(generic_sampling.get(key) == value, f"sampling field {key} differs")

    model_profile = generic_manifest.get("model_profile")
    _require(model_profile == graph_manifest.get("model_profile") == protocol.get("inference", {}).get("model_profile"), "model/provider profiles differ")
    _require(generic_manifest.get("temperature") == graph_manifest.get("temperature") == protocol.get("inference", {}).get("temperature"), "temperature differs")
    _require(generic_manifest.get("max_output_tokens_per_turn") == graph_manifest.get("max_output_tokens_per_turn") == protocol.get("inference", {}).get("max_output_tokens_per_turn"), "output cap differs")
    selected_model = generic_manifest.get("selected_diagnosis_model_id")
    _require(selected_model == graph_manifest.get("selected_diagnosis_model_id"), "selected numerical model differs")
    validation_scores = generic_manifest.get("validation_model_macro_f1")
    _require(validation_scores == graph_manifest.get("validation_model_macro_f1"), "validation scores differ")

    evaluator_ids: dict[str, str] = {}
    global_actions: list[str] | None = None
    for key in sorted(generic_units):
        generic = generic_units[key]
        graph = graph_units[key]
        _require(generic.run.get("task") == graph.run.get("task"), f"TaskSpec differs for {key}")
        task = generic.run.get("task", {})
        _require(generic.run.get("budget") == graph.run.get("budget") == generic_budget, f"episode budget differs for {key}")
        _require(task.get("budget") == generic_budget, f"TaskSpec budget differs for {key}")
        _require(key[2] in CORE_TASKS, f"unexpected task {key[2]}")
        _require(generic.metrics.get("evaluator_id") == graph.metrics.get("evaluator_id"), f"executed evaluator differs for {key}")
        evaluator_ids[key[2]] = str(task.get("evaluator_id"))
        actions = list(task.get("allowed_actions", []))
        if global_actions is None:
            global_actions = actions
        else:
            _require(actions == global_actions, "TaskSpec action surface is unstable")
        for leaf, manifest, label in ((generic, generic_manifest, "Generic"), (graph, graph_manifest, "Graph")):
            metadata = leaf.run.get("metadata", {})
            _require(metadata.get("model") == model_profile.get("model_id") and metadata.get("provider") == model_profile.get("provider") and metadata.get("inference_protocol") == model_profile.get("protocol"), f"{label} inference identity differs for {key}")
            _require(metadata.get("selected_diagnosis_model_id") == selected_model, f"{label} numerical model differs for {key}")
            _require(metadata.get("dataset_protocol") == manifest.get("protocol"), f"{label} dataset protocol differs for {key}")
        _require(graph.run.get("metadata", {}).get("graph_policy_profile") == "full", f"Graph profile differs for {key}")

    allowed = set(global_actions or [])
    generic_action_count, generic_tools, _ = _action_contract(generic_units.values(), graph=False, allowed_actions=allowed)
    graph_action_count, graph_tools, graph_states = _action_contract(graph_units.values(), graph=True, allowed_actions=allowed)
    treatment_only_tools = sorted(graph_tools - allowed)
    _require(treatment_only_tools == [], "Graph adds treatment-only tools")
    generic_outcomes = _terminal_counts(generic_units.values())
    graph_outcomes = _terminal_counts(graph_units.values())
    generic_non_submitted = sum(leaf.run.get("terminal_status") != "submitted" for leaf in generic_units.values())
    graph_agent_failures = sum(leaf.run.get("failure_kind") == "agent_decision_error" for leaf in graph_units.values())
    _require(generic_non_submitted > 0, "fixed Generic natural failures are not retained")
    _require(graph_agent_failures > 0, "fixed Graph agent failure is not retained")

    keys = [list(key) for key in sorted(generic_units)]
    return {
        "schema_version": "p2_e0_adapter_equivalence_acceptance_v1",
        "gate_id": "P2-E0",
        "status": "accepted",
        "accepted": True,
        "evidence_class": "real_data_graph_adapter_world_equivalence_mechanics",
        "provider_calls": 0,
        "inputs": {
            "generic_root": _display_path(generic_root),
            "graph_root": _display_path(graph_root),
            "dataset_protocol": _display_path(protocol_path),
            "seed": 20260808,
            "rotation": "rotation_0",
        },
        "counts": {
            "expected_episode_keys_per_arm": expected,
            "matched_statistical_episode_keys": len(keys),
            "generic": {
                "attempt_leaves": len(generic_attempts),
                "exact_six_attempt_leaves": len(generic_attempts),
                "statistical_episode_keys": len(generic_units),
                "terminal_outcomes": generic_outcomes,
                "non_submitted_statistical_outcomes_retained": generic_non_submitted,
            },
            "graph": {
                "attempt_leaves": len(graph_attempts),
                "exact_six_attempt_leaves": len(graph_attempts),
                "statistical_episode_keys": len(graph_units),
                "terminal_outcomes": graph_outcomes,
                "agent_decision_error_outcomes_retained": graph_agent_failures,
            },
            "canonical_action_rows": {"generic": generic_action_count, "graph": graph_action_count},
        },
        "checks": {
            "both_arms_16_of_16_statistical": True,
            "statistical_episode_keys_identical": True,
            "all_attempt_leaves_exact_six": True,
            "taskspecs_identical": True,
            "budgets_windows_sampling_evaluators_identical": True,
            "model_provider_and_numerical_profiles_identical": True,
            "validation_scores_identical": True,
            "public_bundles_exclude_private_targets_and_bearings": True,
            "global_tool_surface_unchanged": True,
            "treatment_only_tools_empty": True,
            "generic_natural_failures_retained_in_denominator": True,
            "graph_agent_failure_retained_in_denominator": True,
            "graph_actions_carry_registered_decision_state": True,
            "generic_actions_do_not_carry_decision_state": True,
        },
        "shared_contract": {
            "dataset_protocol_id": protocol_id,
            "runtime_contract": runtime_contract,
            "tasks": list(CORE_TASKS),
            "budget": generic_budget,
            "window_protocol": window,
            "sampling": generic_sampling,
            "evaluator_ids": dict(sorted(evaluator_ids.items())),
            "model_profile": model_profile,
            "selected_diagnosis_model_id": selected_model,
            "validation_model_macro_f1": validation_scores,
            "global_allowed_actions": global_actions,
        },
        "intervention_boundary": {
            "only_varied_benchmark_interface_factor": "agent_side_decision_state_prompt_and_policy",
            "graph_policy_profile": "full",
            "observed_graph_states": sorted(graph_states),
            "treatment_only_tools": treatment_only_tools,
            "global_tool_surface": "benchmark_phase1_task_allowed_actions_unchanged",
        },
        "matched_episode_keys": keys,
        "claim_boundary": (
            "Closes P2-E0 Graph adapter/world-equivalence mechanics for the fixed "
            "real-data seed-20260808 rotation-0 slice only. Generic is a world "
            "reference, not the Paper-2 Reactive control. This gate does not "
            "estimate P2-E1, Graph performance, reliability, dynamic behavior, or transfer."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generic-root", type=Path, default=DEFAULT_GENERIC_ROOT)
    parser.add_argument("--graph-root", type=Path, default=DEFAULT_GRAPH_ROOT)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    parser.error(LEGACY_SUPERSEDED_MESSAGE)
    report = analyze_gate(args.generic_root, args.graph_root, args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"accepted": True, "gate_id": "P2-E0", "matched_episode_keys": len(report["matched_episode_keys"]), "output": _display_path(args.output), "provider_calls": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
