#!/usr/bin/env python3
"""Audit and dry-schedule the registered Paper-2 P2-E8 Ottawa cohort.

The command reads versioned protocols and runner source only. It never opens
private data, reads environment values, invokes a runner, or calls a provider.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
RESEARCH_ROOT = ROOT.parent.resolve()
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_cross_dataset_replay_protocol_v3.yaml"
SUPERSEDED_PROTOCOL = ROOT / "paper/experiments/graph_cross_dataset_replay_protocol_v2.yaml"
LEGACY_PROTOCOL = ROOT / "paper/experiments/graph_cross_dataset_replay_protocol_v1.yaml"
PROTOCOL_SCHEMA = "graph_cross_dataset_replay_protocol_v3"
SCHEDULE_SCHEMA = "graph_cross_dataset_replay_schedule_v3"
PROTOCOL_ID = "phm_graph_cross_dataset_replay_ottawa_generic_base_p2e8_v3"
DATASET_ID = "university-of-ottawa-uored-vafcls-v5"
DATASET_PROTOCOL_ID = "ottawa_uored_v5_ordered_state_replay_v1"
PROFILE_ID = "paper2-cross-dataset-ottawa-generic-v1"
RUNTIME_CONTRACT = "phase1_opaque_sample_vibration_feature_schema_v6"
SAFE_RUN_STAMP = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_MISSING = object()


class ContractError(ValueError):
    """Raised when the audit would diverge from the frozen protocol."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{name} must be a mapping")
    return value


def _list(value: object, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{name} must be a list")
    return value


def _merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_protocol(path: Path, _stack: tuple[Path, ...] = ()) -> dict[str, Any]:
    """Load a YAML protocol and its explicit sibling extension chain."""

    resolved = path.resolve()
    _require(resolved not in _stack, "cross-dataset protocol extension cycle detected")
    try:
        value = yaml.safe_load(resolved.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot load protocol {path}: {exc}") from exc
    payload = dict(_mapping(value, str(path)))
    base_name = payload.get("extends_protocol")
    if base_name is None:
        return payload
    _require(
        isinstance(base_name, str)
        and bool(base_name)
        and Path(base_name).name == base_name,
        "extends_protocol must name one sibling protocol",
    )
    base = load_protocol(resolved.parent / base_name, (*_stack, resolved))
    return _merge(base, payload)


def _load_yaml(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        raise ContractError(f"missing protocol: {path}")
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ContractError(f"cannot load dataset protocol {path}: {exc}") from exc
    return _mapping(value, str(path))


def _resolve_research_path(value: object, name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{name} must be a non-empty repository-relative path")
    path = Path(value)
    if path.is_absolute():
        raise ContractError(f"{name} must be repository-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(RESEARCH_ROOT)
    except ValueError as exc:
        raise ContractError(f"{name} escapes the research workspace") from exc
    return resolved


def _get_dotted(payload: Mapping[str, Any], dotted_path: object) -> object:
    if not isinstance(dotted_path, str) or not dotted_path:
        raise ContractError("source check path must be a non-empty dotted string")
    current: object = payload
    for key in dotted_path.split("."):
        if not isinstance(current, Mapping) or key not in current:
            return _MISSING
        current = current[key]
    return current


def _check(check: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    check_id = check.get("id")
    if not isinstance(check_id, str) or not check_id:
        raise ContractError("every source check requires a non-empty id")
    if check.get("operator") != "equals":
        raise ContractError(f"unsupported operator for {check_id}: {check.get('operator')!r}")
    observed = _get_dotted(source, check.get("path"))
    expected = check.get("expected")
    missing = observed is _MISSING
    return {
        "id": check_id,
        "path": check.get("path"),
        "operator": "equals",
        "expected": expected,
        "observed": None if missing else observed,
        "observed_missing": missing,
        "passed": not missing and observed == expected,
    }


def validate_protocol(protocol: Mapping[str, Any]) -> None:
    """Validate the exact Ottawa source, matched arms, and cohort arithmetic."""

    schema = protocol.get("schema_version")
    if schema == "graph_cross_dataset_replay_protocol_v1":
        raise ContractError("v1 is superseded_phmskills_base and launch forbidden")
    if schema == "graph_cross_dataset_replay_protocol_v2":
        raise ContractError("v2 is superseded zero-eligible authority and launch forbidden")
    _require(schema == PROTOCOL_SCHEMA, f"schema must be {PROTOCOL_SCHEMA}")
    _require(protocol.get("protocol_id") == PROTOCOL_ID, "P2-E8 protocol identity drifted")
    _require(
        protocol.get("extends_protocol") == "graph_cross_dataset_replay_protocol_v2.yaml",
        "v3 must extend the frozen v2 record",
    )
    _require(
        protocol.get("supersedes_protocol")
        == "paper/experiments/graph_cross_dataset_replay_protocol_v2.yaml",
        "v3 must supersede the zero-eligible v2 record",
    )

    scope = _mapping(protocol.get("scope"), "scope")
    _require(scope.get("matrix_id") == "P2-E8", "scope.matrix_id must be P2-E8")
    _require(
        scope.get("primary_task") == "online_replay_monitoring",
        "P2-E8 primary task must remain online_replay_monitoring",
    )
    _require(
        scope.get("targetless_mechanics_is_outcome_evidence") is False,
        "targetless mechanics must never count as outcome evidence",
    )
    _require(scope.get("public_condition_event") == "absent", "Ottawa has no public condition event")
    _require(scope.get("monitor_or_revise_event_branch_estimand") is False, "event-branch transfer is not an estimand")
    _require(scope.get("event_f1_or_detection_delay_estimand") is False, "event metrics are not estimands")
    _require(scope.get("minimum_eligible_external_datasets") == 1, "P2-E8 requires one external dataset")

    identity = _mapping(protocol.get("agent_identity"), "agent_identity")
    expected_scaffold = {
        "class": "phm_agent_benchmark.phase1.GenericLLMToolAgent",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "legacy_phmskills_superclass_allowed": False,
    }
    expected_control = {
        "arm": "reactive",
        "class": "phm_graph_agent.ReactiveSequentialAgent",
        "direct_base_class": "phm_agent_benchmark.phase1.GenericLLMToolAgent",
        "behavior_overrides": [],
        "agent_id": "reactive-sequential-agent",
        "agent_profile_id": "reactive_sequential_generic_v2",
        "agent_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_implementation_id": "reactive_sequential_agent_v1",
        "graph_policy_profile": "reactive",
    }
    expected_treatment = {
        "arm": "graph",
        "class": "phm_graph_agent.GraphDecisionAgent",
        "direct_base_class": "phm_agent_benchmark.phase1.GenericLLMToolAgent",
        "agent_id": "graph-decision-agent",
        "agent_profile_id": "graph_dynamic_full_generic_v2",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": "graph_decision_control_v1",
        "agent_implementation_id": "graph_decision_agent_v1",
        "graph_policy_profile": "full",
    }
    for name, expected in (
        ("scaffold", expected_scaffold),
        ("control", expected_control),
        ("treatment", expected_treatment),
    ):
        observed = _mapping(identity.get(name), f"agent_identity.{name}")
        drift = {
            key: {"expected": value, "observed": observed.get(key)}
            for key, value in expected.items()
            if observed.get(key) != value
        }
        _require(not drift, f"Generic-base {name} identity drift: {drift}")
    matched = _mapping(protocol.get("matched_contract"), "matched_contract")
    _require(
        matched.get("cells")
        == ["reactive_sequential_generic_v2", "graph_dynamic_full_generic_v2"],
        "matched cells must bind the Generic-base v2 identities",
    )
    _require(matched.get("cross_dataset_pooling") == "forbidden", "cross-dataset pooling must remain forbidden")

    candidates = _list(protocol.get("candidate_sources"), "candidate_sources")
    _require(len(candidates) == 1, "v3 must select exactly one Ottawa candidate")
    candidate = _mapping(candidates[0], "candidate")
    _require(candidate.get("expected_dataset_id") == DATASET_ID, "Ottawa candidate identity drifted")
    _require(candidate.get("external_to_reference") is True, "Ottawa must be external to Paderborn")
    _require(bool(_list(candidate.get("required_all"), "candidate.required_all")), "Ottawa source checks are required")
    _require(bool(_list(candidate.get("outcome_target_any"), "candidate.outcome_target_any")), "Ottawa outcome-target check is required")

    registration = _mapping(protocol.get("dataset_registration"), "dataset_registration")
    expected_registration = {
        "dataset_id": DATASET_ID,
        "dataset_protocol_id": DATASET_PROTOCOL_ID,
        "data_backend": "csv_directory",
        "task": "online_replay_monitoring",
        "rotations": ["rotation_0", "rotation_1", "rotation_2"],
        "train_samples_per_bearing": 1,
        "validation_samples_per_bearing": 1,
        "test_samples_per_bearing": 3,
        "episodes_per_rotation": 4,
        "windows_per_episode": 3,
        "heldout_physical_bearings": 12,
    }
    for key, expected in expected_registration.items():
        _require(registration.get(key) == expected, f"dataset_registration.{key} drifted")
    for key in ("metadata_environment", "signal_environment", "readiness_environment"):
        _require(isinstance(registration.get(key), str) and registration[key], f"dataset_registration.{key} is required")

    formal = _mapping(protocol.get("formal_execution"), "formal_execution")
    expected_formal = {
        "runtime": "openai",
        "experiment_profile_id": PROFILE_ID,
        "provider_label": "openrouter-free",
        "model_id": "cohere/north-mini-code:free",
        "inference_protocol": "openai_chat_completions",
        "thinking_mode": "not_requested",
        "runtime_contract": RUNTIME_CONTRACT,
        "temperature": 0.2,
        "max_output_tokens_per_turn": 2048,
        "input_usd_per_million": 0.0,
        "output_usd_per_million": 0.0,
        "registered_evidence_class": "formal",
        "result_role": "confirmatory",
        "same_day_429_retry": "forbidden",
        "launch_state": "not_run",
    }
    for key, expected in expected_formal.items():
        _require(formal.get(key) == expected, f"formal_execution.{key} drifted")

    current = _mapping(protocol.get("current_schedule"), "current_schedule")
    seeds = _list(current.get("seeds"), "current_schedule.seeds")
    arms = _list(current.get("arms"), "current_schedule.arms")
    rotations = registration["rotations"]
    commands = len(seeds) * len(arms) * len(rotations)
    bundles = commands * int(registration["episodes_per_rotation"])
    pairs = len(seeds) * len(rotations) * int(registration["episodes_per_rotation"])
    windows = bundles * int(registration["windows_per_episode"])
    _require(seeds == [20260808, 20260809, 20260810], "P2-E8 seed set drifted")
    _require(arms == ["reactive", "graph"], "P2-E8 arm order drifted")
    _require(current.get("expected_eligible_dataset_ids") == [DATASET_ID], "eligible dataset registration drifted")
    _require(current.get("expected_eligible_external_datasets") == 1, "eligible dataset count drifted")
    _require(current.get("expected_runner_commands") == commands == 18, "runner-command count drifted")
    _require(current.get("expected_episode_bundles") == bundles == 72, "episode-bundle count drifted")
    _require(current.get("expected_matched_episode_pairs") == pairs == 36, "matched-pair count drifted")
    _require(current.get("expected_assigned_windows_across_arms") == windows == 216, "assigned-window count drifted")
    _require(current.get("formal_launch_allowed") is False, "v3 cannot claim formal launch before analysis")
    _require(_list(current.get("units"), "current_schedule.units") == [], "protocol records no executed units")

    runtime = _mapping(protocol.get("runtime_gate"), "runtime_gate")
    _require(runtime.get("dynamic_protocol") is None, "Ottawa must use ordinary v6 replay")
    _require(runtime.get("required_runtime_contract") == RUNTIME_CONTRACT, "runtime gate drifted")
    _require(bool(_list(runtime.get("required_runner_flags"), "runtime_gate.required_runner_flags")), "runner flags are required")
    _require(bool(_list(runtime.get("required_source_fragments"), "runtime_gate.required_source_fragments")), "runner source fragments are required")

    analysis = _mapping(protocol.get("analysis_gate"), "analysis_gate")
    _require(
        analysis.get("current_state") == "implemented_and_tested",
        "analysis implementation state drifted",
    )
    _require(
        analysis.get("accepted_only_cross_dataset_analyzer_implemented") is True,
        "accepted-only analyzer must be implemented",
    )
    _require(bool(_list(analysis.get("required_before_formal_launch"), "analysis_gate.required_before_formal_launch")), "analysis requirements are required")
    _require(analysis.get("current_blocker") is None, "implemented analyzer cannot retain an analysis blocker")
    activation = _mapping(protocol.get("activation_gate"), "activation_gate")
    _require(
        _list(activation.get("current_blockers"), "activation_gate.current_blockers")
        == ["same_day_north_retry_forbidden_after_http_429_20260902"],
        "the current no-same-day-retry blocker drifted",
    )


def audit_candidate(candidate: Mapping[str, Any], source: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate one source without interpreting labels or opening raw data."""

    candidate_id = candidate.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id:
        raise ContractError("candidate_id must be a non-empty string")
    observed_id = _get_dotted(source, candidate.get("dataset_id_path"))
    missing_id = observed_id is _MISSING
    id_matches = not missing_id and observed_id == candidate.get("expected_dataset_id")
    required = [
        _check(_mapping(item, f"{candidate_id}.required_all"), source)
        for item in _list(candidate.get("required_all"), f"{candidate_id}.required_all")
    ]
    outcomes = [
        _check(_mapping(item, f"{candidate_id}.outcome_target_any"), source)
        for item in _list(candidate.get("outcome_target_any"), f"{candidate_id}.outcome_target_any")
    ]
    outcome_ready = any(item["passed"] for item in outcomes)
    eligible = (
        candidate.get("external_to_reference") is True
        and id_matches
        and all(item["passed"] for item in required)
        and outcome_ready
    )
    blockers: list[str] = []
    if not id_matches:
        blockers.append("dataset_identity_mismatch_or_missing")
    blockers.extend(
        f"required_check_failed:{item['id']}" for item in required if not item["passed"]
    )
    if not outcome_ready:
        blockers.append("no_legal_external_outcome_target")
    return {
        "candidate_id": candidate_id,
        "protocol_path": candidate.get("protocol_path"),
        "expected_dataset_id": candidate.get("expected_dataset_id"),
        "observed_dataset_id": None if missing_id else observed_id,
        "dataset_id_matches": id_matches,
        "external_to_reference": candidate.get("external_to_reference") is True,
        "required_checks": required,
        "outcome_target_checks": outcomes,
        "outcome_target_available": outcome_ready,
        "eligible": eligible,
        "blocked_reasons": blockers,
    }


def _runner_surface(runner: Path) -> tuple[set[str], str]:
    if not runner.is_file():
        return set(), ""
    try:
        source = runner.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(runner))
    except (OSError, SyntaxError, UnicodeError):
        return set(), ""
    flags: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        for argument in node.args:
            if (
                isinstance(argument, ast.Constant)
                and isinstance(argument.value, str)
                and argument.value.startswith("--")
            ):
                flags.add(argument.value)
    return flags, source


def runtime_readiness(protocol: Mapping[str, Any], runner: Path) -> dict[str, Any]:
    gate = _mapping(protocol.get("runtime_gate"), "runtime_gate")
    required_flags = [str(value) for value in _list(gate.get("required_runner_flags"), "required_runner_flags")]
    required_fragments = [str(value) for value in _list(gate.get("required_source_fragments"), "required_source_fragments")]
    declared, source = _runner_surface(runner)
    missing_flags = [flag for flag in required_flags if flag not in declared]
    missing_fragments = [fragment for fragment in required_fragments if fragment not in source]
    implementation = _mapping(gate.get("required_implementation_flags"), "required_implementation_flags")
    missing_implementation = [str(name) for name, value in implementation.items() if value is not True]
    blockers = [
        *(f"runner_missing_flag:{flag}" for flag in missing_flags),
        *(f"runner_missing_source_fragment:{fragment}" for fragment in missing_fragments),
        *(f"implementation_not_ready:{name}" for name in missing_implementation),
    ]
    return {
        "ready": not blockers,
        "runner": runner.relative_to(ROOT).as_posix() if runner.is_relative_to(ROOT) else str(runner),
        "missing_runner_flags": missing_flags,
        "missing_source_fragments": missing_fragments,
        "missing_implementation_flags": missing_implementation,
        "blocked_reasons": blockers,
    }


def analysis_readiness(protocol: Mapping[str, Any]) -> dict[str, Any]:
    """Audit the accepted-only analyzer without opening any run or private data."""

    gate = _mapping(protocol.get("analysis_gate"), "analysis_gate")
    analyzer = _resolve_research_path(gate.get("analyzer"), "analysis_gate.analyzer")
    required_fragments = [
        str(value)
        for value in _list(
            gate.get("required_source_fragments"),
            "analysis_gate.required_source_fragments",
        )
    ]
    try:
        source = analyzer.read_text(encoding="utf-8")
        ast.parse(source, filename=str(analyzer))
    except (OSError, SyntaxError, UnicodeError):
        source = ""
    missing_fragments = [
        fragment for fragment in required_fragments if fragment not in source
    ]
    blockers: list[str] = []
    if gate.get("accepted_only_cross_dataset_analyzer_implemented") is not True:
        blockers.append(str(gate.get("current_blocker") or "analyzer_not_declared_ready"))
    blockers.extend(
        f"analyzer_missing_source_fragment:{fragment}"
        for fragment in missing_fragments
    )
    return {
        "ready": not blockers,
        "analyzer": (
            analyzer.relative_to(ROOT).as_posix()
            if analyzer.is_relative_to(ROOT)
            else str(analyzer)
        ),
        "missing_source_fragments": missing_fragments,
        "required_before_formal_launch": list(
            _list(
                gate.get("required_before_formal_launch"),
                "analysis_gate.required_before_formal_launch",
            )
        ),
        "blocked_reasons": blockers,
    }


def _relative_to_root(path: Path) -> str:
    return os.path.relpath(path.resolve(), ROOT.resolve())


def _build_units(
    protocol: Mapping[str, Any],
    *,
    protocol_path: Path,
    runner: Path,
    run_stamp: str,
    python_executable: str,
) -> list[dict[str, Any]]:
    _require(bool(SAFE_RUN_STAMP.fullmatch(run_stamp)), "run_stamp must be a safe path component")
    registration = protocol["dataset_registration"]
    formal = protocol["formal_execution"]
    current = protocol["current_schedule"]
    runner_text = _relative_to_root(runner)
    dataset_protocol = _relative_to_root(
        _resolve_research_path(registration["protocol_path"], "dataset_registration.protocol_path")
    )
    cross_protocol = _relative_to_root(protocol_path)
    output_root = ROOT / str(current["output_root"]) / f"run_{run_stamp}"
    profile_by_arm = {
        "reactive": protocol["agent_identity"]["control"]["agent_profile_id"],
        "graph": protocol["agent_identity"]["treatment"]["agent_profile_id"],
    }
    units: list[dict[str, Any]] = []
    outputs: set[str] = set()
    for arm in current["arms"]:
        for seed in current["seeds"]:
            for rotation in registration["rotations"]:
                output = output_root / arm / f"seed_{seed}" / rotation
                output_text = str(output)
                _require(output_text not in outputs, f"duplicate P2-E8 output: {output_text}")
                outputs.add(output_text)
                command = [
                    python_executable,
                    runner_text,
                    "--arm", str(arm),
                    "--runtime", str(formal["runtime"]),
                    "--graph-profile", "full",
                    "--protocol", dataset_protocol,
                    "--cross-dataset-protocol", cross_protocol,
                    "--dataset-id", str(registration["dataset_id"]),
                    "--data-backend", str(registration["data_backend"]),
                    "--metadata-env", str(registration["metadata_environment"]),
                    "--signal-env", str(registration["signal_environment"]),
                    "--data-readiness-env", str(registration["readiness_environment"]),
                    "--experiment-profile-id", str(formal["experiment_profile_id"]),
                    "--rotation", str(rotation),
                    "--tasks", str(registration["task"]),
                    "--train-samples-per-bearing", str(registration["train_samples_per_bearing"]),
                    "--validation-samples-per-bearing", str(registration["validation_samples_per_bearing"]),
                    "--test-samples-per-bearing", str(registration["test_samples_per_bearing"]),
                    "--runtime-contract", str(formal["runtime_contract"]),
                    "--seed", str(seed),
                    "--provider-label", str(formal["provider_label"]),
                    "--temperature", str(formal["temperature"]),
                    "--max-output-tokens-per-turn", str(formal["max_output_tokens_per_turn"]),
                    "--input-usd-per-million", str(formal["input_usd_per_million"]),
                    "--output-usd-per-million", str(formal["output_usd_per_million"]),
                    "--base-url-env", str(formal["base_url_environment"]),
                    "--api-key-env", str(formal["api_key_environment"]),
                    "--model-env", str(formal["model_environment"]),
                    "--output", output_text,
                ]
                units.append(
                    {
                        "unit_id": f"P2-E8--ottawa--{arm}--seed-{seed}--{rotation}",
                        "dataset_id": DATASET_ID,
                        "task_id": registration["task"],
                        "arm": arm,
                        "agent_profile_id": profile_by_arm[arm],
                        "seed": seed,
                        "rotation": rotation,
                        "matched_pair_partition": f"{DATASET_ID}|seed-{seed}|{rotation}",
                        "expected_episode_bundles": registration["episodes_per_rotation"],
                        "expected_assigned_windows": registration["episodes_per_rotation"] * registration["windows_per_episode"],
                        "output": output_text,
                        "command": command,
                    }
                )
    return units


def build_manifest(
    protocol_path: Path = DEFAULT_PROTOCOL,
    runner_override: Path | None = None,
    *,
    run_stamp: str = "DRYRUN",
    python_executable: str = sys.executable,
) -> dict[str, Any]:
    protocol_path = protocol_path.resolve()
    protocol = load_protocol(protocol_path)
    validate_protocol(protocol)
    audits: list[dict[str, Any]] = []
    for raw in _list(protocol.get("candidate_sources"), "candidate_sources"):
        candidate = _mapping(raw, "candidate")
        source_path = _resolve_research_path(candidate.get("protocol_path"), f"{candidate.get('candidate_id')}.protocol_path")
        audits.append(audit_candidate(candidate, _load_yaml(source_path)))

    eligible_ids = [audit["expected_dataset_id"] for audit in audits if audit["eligible"]]
    current = _mapping(protocol.get("current_schedule"), "current_schedule")
    expected_ids = _list(current.get("expected_eligible_dataset_ids"), "current_schedule.expected_eligible_dataset_ids")
    _require(eligible_ids == expected_ids, "source eligibility changed; freeze a new P2-E8 protocol before scheduling")
    _require(len(eligible_ids) == current.get("expected_eligible_external_datasets"), "eligible external dataset count mismatch")

    gate = _mapping(protocol.get("runtime_gate"), "runtime_gate")
    runner = runner_override or _resolve_research_path(gate.get("runner"), "runtime_gate.runner")
    runtime = runtime_readiness(protocol, runner)
    target_ready = len(eligible_ids) >= int(protocol["scope"]["minimum_eligible_external_datasets"])
    schedule_blockers: list[str] = []
    if not target_ready:
        schedule_blockers.append("no_eligible_external_dataset_with_outcome_target")
    schedule_blockers.extend(runtime["blocked_reasons"])
    schedule_ready = not schedule_blockers
    units = (
        _build_units(
            protocol,
            protocol_path=protocol_path,
            runner=runner,
            run_stamp=run_stamp,
            python_executable=python_executable,
        )
        if schedule_ready
        else []
    )
    _require(len(units) in {0, int(current["expected_runner_commands"])}, "partial P2-E8 schedules are forbidden")

    analysis = analysis_readiness(protocol)
    analysis_ready = analysis["ready"]
    provider_free_preflight_ready = schedule_ready and analysis_ready
    activation_blockers = list(schedule_blockers)
    activation_blockers.extend(analysis["blocked_reasons"])
    activation_blockers.extend(protocol["activation_gate"]["current_blockers"])
    counts = Counter(unit["arm"] for unit in units)
    return {
        "schema_version": SCHEDULE_SCHEMA,
        "protocol_id": protocol["protocol_id"],
        "authority_version": current["authority_version"],
        "matrix_id": "P2-E8",
        "mode": "dry_run",
        "evidence_class": "source_and_runtime_schedule_only_not_performance_evidence",
        "provider_calls_made": 0,
        "runner_invoked": False,
        "raw_signals_read": False,
        "private_targets_read": False,
        "environment_values_read": False,
        "filesystem_writes_made": 0,
        "agent_identity": {
            "scaffold": dict(protocol["agent_identity"]["scaffold"]),
            "control": dict(protocol["agent_identity"]["control"]),
            "treatment": dict(protocol["agent_identity"]["treatment"]),
        },
        "candidate_audits": audits,
        "eligible_external_dataset_ids": eligible_ids,
        "eligible_external_dataset_count": len(eligible_ids),
        "external_outcome_target_ready": target_ready,
        "runtime_readiness": runtime,
        "schedule_ready": schedule_ready,
        "schedule_blocked_reasons": schedule_blockers,
        "analysis_readiness": analysis,
        "provider_free_preflight_ready": provider_free_preflight_ready,
        "activation_ready": not activation_blockers,
        "activation_blocked_reasons": activation_blockers,
        "formal_launch_allowed_by_this_scheduler": False,
        "formal_launch_prerequisites_satisfied": not activation_blockers,
        "run_stamp": run_stamp,
        "expected_episode_bundles": current["expected_episode_bundles"],
        "expected_matched_episode_pairs": current["expected_matched_episode_pairs"],
        "expected_assigned_windows_across_arms": current["expected_assigned_windows_across_arms"],
        "unit_count": len(units),
        "arm_unit_counts": {arm: counts[arm] for arm in current["arms"]},
        "units": units,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Provider-free P2-E8 Ottawa source/runtime audit and dry scheduler."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--runner", type=Path, help="Override runner path for source-surface audit only.")
    parser.add_argument("--run-stamp", default="DRYRUN", help="Safe isolated output namespace; no directory is created.")
    parser.add_argument("--require-eligible", action="store_true", help="Exit 3 when Ottawa lacks its registered outcome target.")
    parser.add_argument("--require-ready", action="store_true", help="Exit 4 while any formal activation prerequisite, including analysis, is closed.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if not args.dry_run:
        parser.error("--dry-run is required; this scheduler never launches inference")
    try:
        manifest = build_manifest(
            args.protocol.resolve(),
            args.runner.resolve() if args.runner else None,
            run_stamp=args.run_stamp,
        )
    except (ContractError, KeyError, OSError, TypeError, ValueError) as exc:
        print(f"schedule contract error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    if args.require_eligible and not manifest["external_outcome_target_ready"]:
        return 3
    if args.require_ready and not manifest["activation_ready"]:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
