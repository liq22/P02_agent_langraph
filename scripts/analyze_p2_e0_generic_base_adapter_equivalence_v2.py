#!/usr/bin/env python3
"""Validate the corrected P2-E0 Generic-base adapter/world gate.

This provider-free gate reads the isolated real-Paderborn Mock bundles for the
ReactiveSequentialAgent and GraphDecisionAgent.  It never reads evaluator-
private root records, invokes a model/provider, or aggregates performance.
"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

import yaml


P02_ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = P02_ROOT.parent / "p01-phm-agent-benchmark"
DEFAULT_REACTIVE_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/mechanics/p2_generic_graph_base_v1/e0_full"
    / "reactive/rotation_0"
)
DEFAULT_GRAPH_ROOT = (
    P02_ROOT
    / "paper/experiments/runs/mechanics/p2_generic_graph_base_v1/e0_full"
    / "graph/rotation_0"
)
DEFAULT_PROTOCOL = BENCHMARK_ROOT / "paper/experiments/datasets/dataset_protocol.yaml"
DEFAULT_OUTPUT = (
    P02_ROOT
    / "paper/experiments/results/p2_e0_generic_base_adapter_equivalence_v2.json"
)

P2_EXPERIMENT_ID = "p2_graph_vs_generic_llm_v1"
MATCHED_CONTROL_ID = "benchmark_generic_llm_tool_agent_v1"
GRAPH_CONTROL_ID = "graph_decision_control_v1"
REACTIVE_IMPLEMENTATION_ID = "reactive_sequential_agent_v1"
GRAPH_IMPLEMENTATION_ID = "graph_decision_agent_v1"
RUNTIME_CONTRACT = "phase1_opaque_sample_vibration_feature_schema_v6"
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
PRIVATE_FIELDS = frozenset(
    {"bearing_id", "private_target", "diagnosis_target", "anomaly_target"}
)
FORBIDDEN_P1_MARKERS = (
    "phm_skills",
    "phmskills",
    "p01-phmskills",
    "phm-skills-agent",
)
CORE_TASKS = ("cold_start_fault_diagnosis", "unsupervised_anomaly_detection")
GRAPH_STATES = frozenset(
    {"Inspect", "Hypothesize", "Analyze", "Check", "Monitor", "Revise", "Recover", "Submit"}
)
GRAPH_CONTROL_METHODS = frozenset(
    {"__init__", "decision_state", "available_tools", "conversation", "system_prompt"}
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
    """Raised when a corrected P2-E0 invariant fails."""


@dataclass(frozen=True)
class Attempt:
    path: Path
    key: tuple[str, str, str]
    run: Mapping[str, Any]
    metrics: Mapping[str, Any]
    rollout: tuple[Mapping[str, Any], ...]

    @property
    def statistical(self) -> bool:
        terminal = self.run.get("terminal_status")
        provider_error = bool(
            terminal == "failed" and self.run.get("failure_kind") == "provider_error"
        )
        return bool(terminal not in {None, "running"} and not provider_error)


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise GateError(message)


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GateError(f"cannot read valid JSON from {path}: {exc}") from exc


def _jsonl(path: Path) -> list[Any]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise GateError(f"cannot read {path}: {exc}") from exc
    rows: list[Any] = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise GateError(f"invalid JSONL at {path}:{number}: {exc}") from exc
    return rows


def _walk(value: Any) -> Iterable[tuple[str | None, Any]]:
    if isinstance(value, Mapping):
        for key, child in value.items():
            yield str(key), child
            yield from _walk(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        for child in value:
            yield None, child
            yield from _walk(child)


def _bearings(protocol: Mapping[str, Any]) -> frozenset[str]:
    folds = protocol.get("split", {}).get("folds", {})
    _require(isinstance(folds, Mapping) and folds, "protocol split.folds missing")
    values: set[str] = set()
    for fold in folds.values():
        _require(isinstance(fold, list), "protocol fold must be a list")
        values.update(str(item) for item in fold)
    return frozenset(values)


def _assert_public_and_p1_free(
    documents: Iterable[Any], bearings: frozenset[str], label: str
) -> None:
    for document in documents:
        for key, value in _walk(document):
            if key is not None and key.lower() in PRIVATE_FIELDS:
                raise GateError(f"{label} exposes private field {key!r}")
            if isinstance(value, str):
                if value in bearings:
                    raise GateError(f"{label} exposes private bearing value {value!r}")
                lowered = value.lower()
                if any(marker in lowered for marker in FORBIDDEN_P1_MARKERS):
                    raise GateError(f"{label} contains forbidden P1 provenance {value!r}")


def _load_attempts(
    root: Path, protocol: Mapping[str, Any], *, label: str
) -> list[Attempt]:
    episodes = root / "episodes"
    _require(episodes.is_dir(), f"{label} episodes root missing: {episodes}")
    paths = sorted(path for path in episodes.glob("*/*/*/attempt-*") if path.is_dir())
    _require(len(paths) == 16, f"{label} requires exactly 16 attempt leaves, found {len(paths)}")
    known_bearings = _bearings(protocol)
    attempts: list[Attempt] = []
    for path in paths:
        names = {item.name for item in path.iterdir() if item.is_file()}
        _require(names == RUN_BUNDLE_FILES, f"{label} non-exact-six leaf {path}: {sorted(names)}")
        run = _json(path / "run.json")
        submission = _json(path / "submission.json")
        metrics = _json(path / "metrics.json")
        artifacts = _json(path / "artifacts.json")
        rollout = _jsonl(path / "rollout.jsonl")
        failures = _jsonl(path / "failures.jsonl")
        _assert_public_and_p1_free(
            (run, submission, metrics, artifacts, rollout, failures),
            known_bearings,
            str(path),
        )
        relative = path.relative_to(episodes)
        _require(len(relative.parts) == 4, f"unexpected attempt path {path}")
        path_key = tuple(str(part) for part in relative.parts[:3])
        metadata = run.get("metadata", {})
        metadata_key = tuple(str(part) for part in metadata.get("episode_key", []))
        _require(metadata_key == path_key, f"{label} episode key/path mismatch at {path}")
        _require(
            metadata.get("attempt_index")
            == int(relative.parts[3].removeprefix("attempt-")),
            f"{label} attempt index/path mismatch at {path}",
        )
        attempts.append(
            Attempt(
                path=path,
                key=metadata_key,
                run=run,
                metrics=metrics,
                rollout=tuple(row for row in rollout if isinstance(row, Mapping)),
            )
        )
    return attempts


def _by_key(attempts: Sequence[Attempt], *, label: str) -> dict[tuple[str, str, str], Attempt]:
    result: dict[tuple[str, str, str], Attempt] = {}
    for attempt in attempts:
        _require(attempt.statistical, f"{label} has non-statistical attempt at {attempt.path}")
        _require(attempt.key not in result, f"{label} duplicate statistical key {attempt.key}")
        result[attempt.key] = attempt
    _require(len(result) == 16, f"{label} requires 16 statistical keys")
    return result


def _source_control_contract() -> dict[str, Any]:
    agent_path = P02_ROOT / "src/phm_graph_agent/agent.py"
    runner_path = P02_ROOT / "scripts/run_graph_experiment.py"
    sources = {path: path.read_text(encoding="utf-8") for path in (agent_path, runner_path)}
    for path, source in sources.items():
        source_tree = ast.parse(source, filename=str(path))
        imported_names: list[str] = []
        for node in ast.walk(source_tree):
            if isinstance(node, ast.Import):
                imported_names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported_names.append(str(node.module))
                imported_names.extend(alias.name for alias in node.names)
        lowered = "\n".join(imported_names).lower()
        _require(
            not any(marker in lowered for marker in FORBIDDEN_P1_MARKERS),
            f"production source imports forbidden P1 runtime: {path}",
        )
    tree = ast.parse(sources[agent_path], filename=str(agent_path))
    classes = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    reactive = classes.get("ReactiveSequentialAgent")
    graph = classes.get("GraphDecisionAgent")
    _require(reactive is not None and graph is not None, "corrected P2 agent classes missing")

    def base_names(node: ast.ClassDef) -> list[str]:
        return [base.id for base in node.bases if isinstance(base, ast.Name)]

    _require(base_names(reactive) == ["GenericLLMToolAgent"], "Reactive is not a direct Generic base")
    reactive_methods = {
        node.name for node in reactive.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    _require(not reactive_methods, f"Reactive overrides Generic behavior: {sorted(reactive_methods)}")
    _require(base_names(graph) == ["GenericLLMToolAgent"], "Graph is not a direct Generic base")
    graph_methods = {
        node.name for node in graph.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    _require(graph_methods == GRAPH_CONTROL_METHODS, f"Graph control methods drift: {sorted(graph_methods)}")
    return {
        "reactive_direct_base": "GenericLLMToolAgent",
        "reactive_behavior_overrides": [],
        "graph_direct_base": "GenericLLMToolAgent",
        "graph_control_methods": sorted(graph_methods),
        "production_p1_runtime_imports_or_provenance": [],
    }


def _budget(manifest: Mapping[str, Any]) -> dict[str, Any]:
    raw = manifest.get("budget", {})
    _require(isinstance(raw, Mapping), "manifest budget missing")
    return {key: raw.get(key) for key in FULL_BUDGET_KEYS}


def _sampling(manifest: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "seed": manifest.get("seed"),
        "rotation": manifest.get("rotation"),
        "sample_handle": manifest.get("sample_handle"),
        "train_samples_per_bearing": manifest.get("train_samples_per_bearing"),
        "validation_samples_per_bearing": manifest.get("validation_samples_per_bearing"),
        "test_samples_per_bearing": manifest.get("test_samples_per_bearing"),
        "test_sample_selection": manifest.get("test_sample_selection"),
        "max_test_bearings": manifest.get("max_test_bearings"),
    }


def _expected_keys(protocol: Mapping[str, Any]) -> int:
    split = protocol.get("split", {})
    rotation = next(
        (row for row in split.get("rotations", []) if row.get("run") == "rotation_0"),
        None,
    )
    _require(rotation is not None, "rotation_0 absent from protocol")
    held_out = split.get("folds", {}).get(rotation.get("test"))
    samples = protocol.get("episode_sampling", {}).get("agent_test_samples_per_bearing")
    _require(isinstance(held_out, list) and isinstance(samples, int), "invalid protocol sampling")
    return len(held_out) * samples * len(CORE_TASKS)


def _terminal_counts(attempts: Iterable[Attempt]) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for attempt in attempts:
        status = str(attempt.run.get("terminal_status"))
        failure = attempt.run.get("failure_kind")
        counts[status if failure in {None, status} else f"{status}:{failure}"] += 1
    return dict(sorted(counts.items()))


def _actions(
    attempts: Iterable[Attempt], *, graph: bool, allowed: set[str], expected_agent: str
) -> tuple[int, set[str], set[str]]:
    count = 0
    tools: set[str] = set()
    states: set[str] = set()
    for attempt in attempts:
        for row in attempt.rollout:
            if row.get("event_type") != "action":
                continue
            _require(row.get("agent_id") == expected_agent, f"rollout agent identity drift at {attempt.path}")
            action = row.get("action", {})
            _require(isinstance(action, Mapping), f"invalid action at {attempt.path}")
            tool = action.get("name")
            _require(isinstance(tool, str) and tool in allowed, f"out-of-surface action at {attempt.path}")
            state = action.get("decision_state")
            if graph:
                _require(isinstance(state, str) and state in GRAPH_STATES, f"Graph decision state missing at {attempt.path}")
                states.add(state)
            else:
                _require(state is None, f"Reactive action carries Graph state at {attempt.path}")
            tools.add(tool)
            count += 1
    _require(count > 0, "arm has no canonical action rows")
    return count, tools, states


def _display(path: Path) -> str:
    try:
        return path.relative_to(P02_ROOT).as_posix()
    except ValueError:
        try:
            return "../" + path.relative_to(P02_ROOT.parent).as_posix()
        except ValueError:
            return path.as_posix()


def analyze_gate(reactive_root: Path, graph_root: Path, protocol_path: Path) -> dict[str, Any]:
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    _require(isinstance(protocol, Mapping), "dataset protocol must be a mapping")
    source_contract = _source_control_contract()
    reactive_manifest = _json(reactive_root / "run_manifest.json")
    graph_manifest = _json(graph_root / "run_manifest.json")

    shared_manifest_fields = (
        "p2_experiment_id",
        "matched_control_id",
        "protocol",
        "runtime",
        "runtime_contract",
        "rotation",
        "seed",
        "tasks",
        "window_protocol",
        "budget",
        "sample_handle",
        "train_samples_per_bearing",
        "validation_samples_per_bearing",
        "test_samples_per_bearing",
        "test_sample_selection",
        "max_test_bearings",
        "selected_diagnosis_model_id",
        "validation_model_macro_f1",
        "model_profile",
        "temperature",
        "max_output_tokens_per_turn",
    )
    for name in shared_manifest_fields:
        _require(reactive_manifest.get(name) == graph_manifest.get(name), f"manifest field differs: {name}")
    _require(reactive_manifest.get("p2_experiment_id") == P2_EXPERIMENT_ID, "P2 experiment identity differs")
    _require(reactive_manifest.get("matched_control_id") == MATCHED_CONTROL_ID, "matched Generic control identity differs")
    _require(reactive_manifest.get("runtime") == "mock", "P2-E0 v2 requires provider-free Mock runtime")
    _require(reactive_manifest.get("runtime_contract") == RUNTIME_CONTRACT, "runtime contract differs")
    _require(reactive_manifest.get("seed") == 20260808 and reactive_manifest.get("rotation") == "rotation_0", "seed/rotation differs")
    _require(reactive_manifest.get("protocol") == protocol.get("schema_version"), "source protocol differs")
    _require(reactive_manifest.get("max_test_bearings") is None, "E0 full slice cannot truncate bearings")
    _require(reactive_manifest.get("canonical_episode_count") == graph_manifest.get("canonical_episode_count") == 16, "manifest episode count differs")
    _require(reactive_manifest.get("model_profile") is None, "Mock E0 cannot declare provider model profile")
    _require(reactive_manifest.get("evidence_class") == graph_manifest.get("evidence_class") == "mechanics_only_not_performance_evidence", "evidence class differs")

    _require(
        reactive_manifest.get("arm") == "reactive"
        and reactive_manifest.get("agent_control_id") == MATCHED_CONTROL_ID
        and reactive_manifest.get("agent_implementation_id") == REACTIVE_IMPLEMENTATION_ID
        and reactive_manifest.get("graph_policy_profile") == "reactive",
        "Reactive zero-override Generic identity differs",
    )
    _require(
        graph_manifest.get("arm") == "graph"
        and graph_manifest.get("agent_control_id") == GRAPH_CONTROL_ID
        and graph_manifest.get("agent_implementation_id") == GRAPH_IMPLEMENTATION_ID
        and graph_manifest.get("graph_policy_profile") == "full",
        "Graph registered control identity differs",
    )
    normal_budget = _budget(reactive_manifest)
    _require(normal_budget == _budget(graph_manifest), "budget differs")
    for key, value in protocol.get("budgets", {}).get("core", {}).items():
        _require(normal_budget.get(key) == value, f"budget differs from protocol: {key}")
    _require(reactive_manifest.get("window_protocol") == json.loads(json.dumps(protocol.get("window_protocol"))), "window differs from protocol")
    sampling = _sampling(reactive_manifest)
    frozen = protocol.get("episode_sampling", {})
    expected_sampling = {
        "seed": 20260808,
        "rotation": "rotation_0",
        "sample_handle": protocol.get("agent_visibility", {}).get("sample_handle"),
        "train_samples_per_bearing": frozen.get("train_samples_per_bearing"),
        "validation_samples_per_bearing": frozen.get("healthy_validation_samples_per_bearing"),
        "test_samples_per_bearing": frozen.get("agent_test_samples_per_bearing"),
        "test_sample_selection": frozen.get("agent_selection"),
        "max_test_bearings": None,
    }
    _require(sampling == expected_sampling, "sampling differs from source protocol")

    reactive_attempts = _load_attempts(reactive_root, protocol, label="Reactive")
    graph_attempts = _load_attempts(graph_root, protocol, label="Graph")
    reactive = _by_key(reactive_attempts, label="Reactive")
    graph = _by_key(graph_attempts, label="Graph")
    _require(len(reactive) == len(graph) == _expected_keys(protocol) == 16, "16-key requirement differs")
    _require(set(reactive) == set(graph), "matched episode keys differ")

    global_actions: list[str] | None = None
    evaluator_ids: dict[str, str] = {}
    model_identity: tuple[str, str, str] | None = None
    for key in sorted(reactive):
        control = reactive[key]
        treatment = graph[key]
        _require(control.run.get("task") == treatment.run.get("task"), f"TaskSpec differs for {key}")
        task = control.run.get("task", {})
        _require(control.run.get("budget") == treatment.run.get("budget") == normal_budget, f"episode budget differs for {key}")
        _require(control.metrics.get("evaluator_id") == treatment.metrics.get("evaluator_id"), f"evaluator differs for {key}")
        evaluator_ids[key[2]] = str(task.get("evaluator_id"))
        actions = list(task.get("allowed_actions", []))
        if global_actions is None:
            global_actions = actions
        else:
            _require(actions == global_actions, "global tool surface is unstable")
        for attempt, manifest, expected in (
            (control, reactive_manifest, {
                "arm": "reactive", "agent_control_id": MATCHED_CONTROL_ID,
                "agent_implementation_id": REACTIVE_IMPLEMENTATION_ID,
                "graph_policy_profile": "reactive", "agent_id": "reactive-sequential-agent",
            }),
            (treatment, graph_manifest, {
                "arm": "graph", "agent_control_id": GRAPH_CONTROL_ID,
                "agent_implementation_id": GRAPH_IMPLEMENTATION_ID,
                "graph_policy_profile": "full", "agent_id": "graph-decision-agent",
            }),
        ):
            metadata = attempt.run.get("metadata", {})
            _require(attempt.run.get("agent_id") == expected["agent_id"], f"agent_id differs for {key}")
            for name in ("arm", "agent_control_id", "agent_implementation_id", "graph_policy_profile"):
                _require(metadata.get(name) == expected[name], f"{name} differs for {key}")
            _require(metadata.get("p2_experiment_id") == P2_EXPERIMENT_ID and metadata.get("matched_control_id") == MATCHED_CONTROL_ID, f"P2 identity differs for {key}")
            _require(metadata.get("dataset_protocol") == manifest.get("protocol") and metadata.get("runtime_contract") == RUNTIME_CONTRACT, f"world identity differs for {key}")
            current_model = (str(metadata.get("model")), str(metadata.get("provider")), str(metadata.get("inference_protocol")))
            if model_identity is None:
                model_identity = current_model
            _require(current_model == model_identity, f"model identity differs for {key}")
            _require(metadata.get("selected_diagnosis_model_id") == reactive_manifest.get("selected_diagnosis_model_id"), f"selected numerical model differs for {key}")
    _require(model_identity == ("deterministic-mock-llm", "benchmark-local", "mock-tools"), "provider-free model identity differs")

    allowed = set(global_actions or [])
    reactive_action_count, reactive_tools, _ = _actions(
        reactive.values(), graph=False, allowed=allowed, expected_agent="reactive-sequential-agent"
    )
    graph_action_count, graph_tools, states = _actions(
        graph.values(), graph=True, allowed=allowed, expected_agent="graph-decision-agent"
    )
    treatment_only_tools = sorted(graph_tools - allowed)
    _require(not treatment_only_tools, "Graph adds tools beyond the shared global surface")

    reactive_non_submitted = sum(item.run.get("terminal_status") != "submitted" for item in reactive.values())
    graph_non_submitted = sum(item.run.get("terminal_status") != "submitted" for item in graph.values())
    keys = [list(key) for key in sorted(reactive)]
    return {
        "schema_version": "p2_e0_generic_base_adapter_equivalence_v2",
        "gate_id": "P2-E0-v2",
        "status": "accepted",
        "accepted": True,
        "evidence_class": "provider_free_real_data_generic_base_adapter_world_mechanics",
        "provider_calls": 0,
        "inputs": {
            "reactive_root": _display(reactive_root),
            "graph_root": _display(graph_root),
            "dataset_protocol": _display(protocol_path),
            "p2_experiment_id": P2_EXPERIMENT_ID,
            "seed": 20260808,
            "rotation": "rotation_0",
        },
        "counts": {
            "matched_statistical_episode_keys": 16,
            "exact_six_attempt_leaves_total": 32,
            "reactive": {
                "attempt_leaves": 16,
                "statistical_episode_keys": 16,
                "terminal_outcomes": _terminal_counts(reactive.values()),
                "non_submitted_statistical_outcomes_retained": reactive_non_submitted,
                "canonical_action_rows": reactive_action_count,
            },
            "graph": {
                "attempt_leaves": 16,
                "statistical_episode_keys": 16,
                "terminal_outcomes": _terminal_counts(graph.values()),
                "non_submitted_statistical_outcomes_retained": graph_non_submitted,
                "canonical_action_rows": graph_action_count,
            },
        },
        "checks": {
            "both_arms_16_of_16_statistical": True,
            "all_32_attempt_leaves_exact_six": True,
            "matched_episode_keys_identical": True,
            "taskspec_budget_world_evaluator_model_identical": True,
            "global_tool_surface_identical": True,
            "reactive_is_zero_override_generic_control": True,
            "graph_is_generic_base_with_registered_graph_control_only": True,
            "reactive_actions_have_no_graph_state": True,
            "graph_actions_have_registered_state": True,
            "no_p1_runtime_import_or_bundle_provenance": True,
            "all_nonprovider_terminal_failures_retained_in_denominator": True,
            "provider_calls_zero": True,
        },
        "shared_contract": {
            "dataset_protocol_id": protocol.get("schema_version"),
            "runtime_contract": RUNTIME_CONTRACT,
            "tasks": list(CORE_TASKS),
            "budget": normal_budget,
            "window_protocol": reactive_manifest.get("window_protocol"),
            "sampling": sampling,
            "evaluator_ids": dict(sorted(evaluator_ids.items())),
            "model_identity": {
                "model": model_identity[0], "provider": model_identity[1],
                "inference_protocol": model_identity[2],
            },
            "selected_diagnosis_model_id": reactive_manifest.get("selected_diagnosis_model_id"),
            "validation_model_macro_f1": reactive_manifest.get("validation_model_macro_f1"),
            "global_allowed_actions": global_actions,
        },
        "control_boundary": {
            **source_contract,
            "p2_experiment_id": P2_EXPERIMENT_ID,
            "matched_control_id": MATCHED_CONTROL_ID,
            "reactive_implementation_id": REACTIVE_IMPLEMENTATION_ID,
            "graph_control_id": GRAPH_CONTROL_ID,
            "graph_implementation_id": GRAPH_IMPLEMENTATION_ID,
            "treatment_only_tools": treatment_only_tools,
            "observed_graph_states": sorted(states),
        },
        "denominator_policy": {
            "natural_nonprovider_terminal_is_statistical": True,
            "provider_error_is_statistical": False,
            "failed_or_partial_statistical_units_are_not_dropped": True,
        },
        "matched_episode_keys": keys,
        "claim_boundary": (
            "Closes corrected P2-E0 Generic-base adapter/world mechanics for the "
            "isolated real-Paderborn provider-free Mock seed-20260808 rotation-0 "
            "slice only. It does not estimate P2-E1, Graph performance, reliability, "
            "dynamic behavior, or transfer. The legacy PHMskills-derived E0 artifact "
            "is not an input to this gate."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reactive-root", type=Path, default=DEFAULT_REACTIVE_ROOT)
    parser.add_argument("--graph-root", type=Path, default=DEFAULT_GRAPH_ROOT)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = analyze_gate(args.reactive_root, args.graph_root, args.protocol)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "accepted": report["accepted"], "gate_id": report["gate_id"],
        "matched_episode_keys": report["counts"]["matched_statistical_episode_keys"],
        "output": _display(args.output), "provider_calls": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
