#!/usr/bin/env python3
"""Build the provider-free task-primary P2-E2 horizon-v3 schedule.

This module deliberately has no runner-execution path.  It validates that the
schedule is a projection of the registered dynamic protocol, emits commands as
data, and reports whether the future runtime integration is statically ready.
"""

from __future__ import annotations

import argparse
import ast
import json
import shlex
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_horizon_scaling_protocol_v3.yaml"
LEGACY_PROTOCOL = ROOT / "paper/experiments/graph_horizon_scaling_protocol_v1.yaml"
SUPERSEDED_PROTOCOL = ROOT / "paper/experiments/graph_horizon_scaling_protocol_v2.yaml"


class ContractError(ValueError):
    """Raised when the scheduler would diverge from its scientific contract."""


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ContractError(f"{name} must be a mapping")
    return value


def _list(value: object, name: str) -> list[Any]:
    if not isinstance(value, list):
        raise ContractError(f"{name} must be a list")
    return value


def _load_yaml(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        raise ContractError(f"missing protocol: {path}")
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _mapping(payload, str(path))


def _deep_merge(
    base: Mapping[str, Any], override: Mapping[str, Any]
) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(_mapping(merged[key], key), value)
        else:
            merged[key] = value
    return merged


def _load_extended_yaml(
    path: Path, *, stack: tuple[Path, ...] = ()
) -> Mapping[str, Any]:
    """Recursively load a sibling-only versioned protocol extension chain."""

    resolved = path.resolve()
    if resolved in stack:
        raise ContractError("protocol extension cycle detected")
    source = dict(_load_yaml(path))
    base_name = source.pop("extends_protocol", None)
    if base_name is None:
        return source
    if not isinstance(base_name, str) or Path(base_name).name != base_name:
        raise ContractError("protocol extension must be one sibling filename")
    return _deep_merge(
        _load_extended_yaml(path.parent / base_name, stack=(*stack, resolved)),
        source,
    )


def _load_source_yaml(path: Path) -> Mapping[str, Any]:
    return _load_extended_yaml(path)


def _load_protocol_yaml(path: Path) -> Mapping[str, Any]:
    return _load_extended_yaml(path)


def _resolve_repo_path(value: object, name: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ContractError(f"{name} must be a non-empty repository-relative path")
    path = Path(value)
    if path.is_absolute():
        raise ContractError(f"{name} must be repository-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ContractError(f"{name} escapes the P02 repository") from exc
    return resolved


def _expect_equal(actual: object, expected: object, name: str) -> None:
    if actual != expected:
        raise ContractError(f"{name} mismatch: {actual!r} != {expected!r}")


def validate_projection(
    protocol: Mapping[str, Any], source: Mapping[str, Any]
) -> None:
    """Fail if the schedule projection changes a source-protocol variable."""

    _expect_equal(
        protocol.get("schema_version"),
        "graph_horizon_scaling_protocol_v3",
        "schema_version",
    )
    _expect_equal(
        protocol.get("status"),
        "preregistered_task_primary_metric_amendment_scheduler_ready_formal_not_run",
        "status",
    )
    _expect_equal(
        protocol.get("supersedes"),
        "graph_horizon_scaling_protocol_v2.yaml",
        "supersedes",
    )
    _expect_equal(
        source.get("schema_version"),
        "graph_dynamic_ablation_protocol_v3",
        "source.schema_version",
    )
    scope = _mapping(protocol.get("scope"), "scope")
    _expect_equal(scope.get("matrix_id"), "P2-E2", "scope.matrix_id")
    _expect_equal(
        scope.get("task_id"), "online_replay_monitoring", "scope.task_id"
    )

    sequence = _mapping(protocol.get("sequence_contract"), "sequence_contract")
    source_sequence = _mapping(
        source.get("sequence_construction"), "source.sequence_construction"
    )
    for key in (
        "master_horizon",
        "horizons",
        "independently_resample_each_horizon",
        "expected_public_domain_schedule",
        "expected_change_release_indices_zero_based",
    ):
        _expect_equal(sequence.get(key), source_sequence.get(key), f"sequence.{key}")
    horizons = _list(sequence.get("horizons"), "sequence.horizons")
    _expect_equal(horizons, [3, 6, 12], "sequence.horizons")
    _expect_equal(
        sequence.get("master_horizon"), max(horizons), "sequence.master_horizon"
    )
    if sequence.get("one_master_sequence_per_public_sequence") is not True:
        raise ContractError("every public sequence must use one master sequence")
    if sequence.get("independently_resample_each_seed_or_cell") is not False:
        raise ContractError("seed/cell-specific sequence resampling is forbidden")

    schedule = _mapping(protocol.get("schedule"), "schedule")
    source_design = _mapping(source.get("experiment_design"), "source.experiment_design")
    _expect_equal(schedule.get("seeds"), source_design.get("seeds"), "schedule.seeds")
    _expect_equal(
        schedule.get("rotations"), source_design.get("rotations"), "schedule.rotations"
    )
    cells_by_horizon = _mapping(
        source_design.get("cells_per_seed_sequence"),
        "source.experiment_design.cells_per_seed_sequence",
    )
    for horizon in horizons:
        source_cells = _list(
            cells_by_horizon.get(f"horizon_{horizon}"),
            f"source.cells.horizon_{horizon}",
        )
        if not {"reactive", "graph_full"}.issubset(source_cells):
            raise ContractError(
                f"source horizon {horizon} lacks the matched P2-E2 cells"
            )

    budgets = _mapping(protocol.get("budgets"), "budgets")
    source_budgets = _mapping(source.get("budgets"), "source.budgets")
    _expect_equal(
        budgets.get("by_horizon"),
        source_budgets.get("by_horizon"),
        "budgets.by_horizon",
    )

    runtime = _mapping(protocol.get("runtime_projection"), "runtime_projection")
    source_runtime = _mapping(
        source.get("runtime_and_provider_profile"),
        "source.runtime_and_provider_profile",
    )
    shared = _mapping(
        _mapping(protocol.get("matched_cells"), "matched_cells").get("shared"),
        "matched_cells.shared",
    )
    for projection_key, source_key in (
        ("runtime_contract", "effective_runtime_contract"),
        ("provider_profile_id", "formal_provider_profile_id"),
        ("provider", "provider"),
        ("backbone_model", "model"),
        ("inference_protocol", "protocol"),
    ):
        _expect_equal(
            shared.get(projection_key),
            source_runtime.get(source_key),
            f"matched_cells.shared.{projection_key}",
        )
    source_treatment = _mapping(
        source.get("treatment_construction"), "source.treatment_construction"
    )
    identity = _mapping(protocol.get("identity_contract"), "identity_contract")
    for key, source_key in (
        ("p2_experiment_id", "p2_experiment_id"),
        ("matched_control_id", "matched_control_id"),
        ("control_agent_id", "reactive_agent_id"),
        ("treatment_agent_id", "graph_agent_id"),
    ):
        _expect_equal(identity.get(key), source_treatment.get(source_key), f"identity.{key}")
    _expect_equal(
        shared.get("p2_experiment_id"), identity.get("p2_experiment_id"),
        "matched_cells.shared.p2_experiment_id",
    )
    _expect_equal(
        shared.get("matched_control_id"), identity.get("matched_control_id"),
        "matched_cells.shared.matched_control_id",
    )
    matched = _mapping(protocol.get("matched_cells"), "matched_cells")
    _expect_equal(
        _mapping(matched.get("reactive"), "matched_cells.reactive").get("agent_id"),
        identity.get("control_agent_id"), "matched_cells.reactive.agent_id",
    )
    _expect_equal(
        _mapping(matched.get("graph_full"), "matched_cells.graph_full").get("agent_id"),
        identity.get("treatment_agent_id"), "matched_cells.graph_full.agent_id",
    )
    _expect_equal(
        runtime.get("dynamic_protocol_argument"),
        protocol["authority"]["source_dynamic_protocol"],
        "runtime_projection.dynamic_protocol_argument",
    )
    output = _mapping(protocol.get("output_contract"), "output_contract")
    source_output = _mapping(source.get("output_contract"), "source.output_contract")
    for key in ("formal_root", "results_root"):
        _expect_equal(output.get(key), source_output.get(key), f"output_contract.{key}")

    metrics = _mapping(protocol.get("metrics"), "metrics")
    primary = _mapping(metrics.get("primary"), "metrics.primary")
    source_metrics = _mapping(source.get("metrics"), "source.metrics")
    source_primary = _mapping(source_metrics.get("primary"), "source.metrics.primary")
    for key in ("name", "unit", "missing_score_policy_id"):
        _expect_equal(primary.get(key), source_primary.get(key), f"metrics.primary.{key}")
    _expect_equal(
        primary.get("name"),
        "target_adverse_window_average_precision",
        "task-primary endpoint",
    )
    if primary.get("name") == "grounded_completion_rate":
        raise ContractError("grounded completion cannot be the primary task endpoint")
    _expect_equal(
        metrics.get("general_rollout_role"),
        "secondary",
        "metrics.general_rollout_role",
    )
    denominator = _mapping(
        protocol.get("failure_and_denominator_contract"),
        "failure_and_denominator_contract",
    )
    _expect_equal(
        denominator.get("missing_score_policy_id"),
        source_primary.get("missing_score_policy_id"),
        "failure_and_denominator_contract.missing_score_policy_id",
    )
    if "assigned_window" not in str(denominator.get("task_window_denominator")):
        raise ContractError("task metric denominator must retain every assigned window")

    statistics = _mapping(protocol.get("statistics"), "statistics")
    source_statistics = _mapping(source.get("statistics"), "source.statistics")
    for key in ("exact_paired_permutation", "interval_method"):
        _expect_equal(
            statistics.get(key), source_statistics.get(key), f"statistics.{key}"
        )
    _expect_equal(
        statistics.get("per_bearing_average_precision"),
        "forbidden",
        "statistics.per_bearing_average_precision",
    )

    sequence_count = len(_list(sequence.get("public_sequence_ids"), "public_sequence_ids"))
    pair_count = (
        len(_list(schedule.get("seeds"), "schedule.seeds"))
        * len(_list(schedule.get("rotations"), "schedule.rotations"))
        * sequence_count
        * len(horizons)
    )
    _expect_equal(pair_count, schedule.get("expected_matched_pairs"), "matched pair count")
    _expect_equal(2 * pair_count, schedule.get("expected_episode_bundles"), "bundle count")
    _expect_equal(
        2
        * len(_list(schedule.get("seeds"), "schedule.seeds"))
        * len(_list(schedule.get("rotations"), "schedule.rotations"))
        * sequence_count,
        schedule.get("expected_bundles_per_horizon"),
        "bundles per horizon",
    )
    _expect_equal(pair_count, schedule.get("expected_bundles_per_cell"), "bundles per cell")


def _agent_profile_id(cell_name: str, cell: Mapping[str, Any]) -> str:
    value = cell.get("agent_profile_id")
    if not isinstance(value, str) or not value:
        raise ContractError(f"{cell_name} lacks agent_profile_id")
    return value


def _format_unit_root(
    protocol: Mapping[str, Any],
    *,
    agent_profile_id: str,
    seed: int,
    rotation: str,
    horizon: int,
    public_sequence_id: str,
) -> str:
    output = _mapping(protocol.get("output_contract"), "output_contract")
    pattern = output.get("unit_output_pattern")
    formal_root = output.get("formal_root")
    if not isinstance(pattern, str) or not isinstance(formal_root, str):
        raise ContractError("output paths must be strings")
    return pattern.format(
        formal_root=formal_root,
        agent_profile_id=agent_profile_id,
        seed=seed,
        rotation=rotation,
        horizon=horizon,
        public_sequence_id=public_sequence_id,
    )


def _command_for_unit(
    protocol: Mapping[str, Any],
    *,
    cell_name: str,
    cell: Mapping[str, Any],
    seed: int,
    rotation: str,
    horizon: int,
    public_sequence_id: str,
    output_root: str,
) -> list[str]:
    runtime = _mapping(protocol.get("runtime_projection"), "runtime_projection")
    shared = _mapping(
        _mapping(protocol.get("matched_cells"), "matched_cells").get("shared"),
        "matched_cells.shared",
    )
    env_names = _mapping(
        runtime.get("environment_variable_names"),
        "runtime_projection.environment_variable_names",
    )
    values = {
        "runner_arm": cell.get("runner_arm"),
        "runner_graph_profile": cell.get("runner_graph_profile"),
        "python_command": runtime.get("python_command"),
        "runner": runtime.get("runner"),
        "runtime": runtime.get("runtime"),
        "runtime_contract": shared.get("runtime_contract"),
        "dynamic_protocol": runtime.get("dynamic_protocol_argument"),
        "provider": shared.get("provider"),
        "base_url_env": env_names.get("base_url"),
        "api_key_env": env_names.get("api_key"),
        "model_env": env_names.get("model"),
    }
    if any(not isinstance(value, str) or not value for value in values.values()):
        raise ContractError(f"invalid command contract for cell {cell_name}")
    return [
        values["python_command"],
        values["runner"],
        "--arm",
        values["runner_arm"],
        "--runtime",
        values["runtime"],
        "--graph-profile",
        values["runner_graph_profile"],
        "--runtime-contract",
        values["runtime_contract"],
        "--dynamic-protocol",
        values["dynamic_protocol"],
        "--public-sequence-id",
        public_sequence_id,
        "--horizon",
        str(horizon),
        "--tasks",
        "online_replay_monitoring",
        "--seed",
        str(seed),
        "--rotation",
        rotation,
        "--temperature",
        str(shared["temperature"]),
        "--max-output-tokens-per-turn",
        str(shared["max_output_tokens_per_turn"]),
        "--provider-label",
        values["provider"],
        "--input-usd-per-million",
        str(shared["input_usd_per_million"]),
        "--output-usd-per-million",
        str(shared["output_usd_per_million"]),
        "--base-url-env",
        values["base_url_env"],
        "--api-key-env",
        values["api_key_env"],
        "--model-env",
        values["model_env"],
        "--resume-provider-partial",
        "--output",
        output_root,
    ]


def build_units(
    protocol: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    emit_commands: bool = False,
) -> list[dict[str, Any]]:
    validate_projection(protocol, source)
    sequence = _mapping(protocol["sequence_contract"], "sequence_contract")
    schedule = _mapping(protocol["schedule"], "schedule")
    matched = _mapping(protocol["matched_cells"], "matched_cells")
    budgets = _mapping(_mapping(protocol["budgets"], "budgets")["by_horizon"], "budgets.by_horizon")
    cell_order = _list(matched.get("order"), "matched_cells.order")
    units: list[dict[str, Any]] = []
    output_roots: set[str] = set()
    unit_keys: set[tuple[object, ...]] = set()

    for seed in _list(schedule.get("seeds"), "schedule.seeds"):
        for rotation in _list(schedule.get("rotations"), "schedule.rotations"):
            for public_sequence_id in _list(
                sequence.get("public_sequence_ids"), "sequence.public_sequence_ids"
            ):
                for horizon in _list(sequence.get("horizons"), "sequence.horizons"):
                    for cell_name in cell_order:
                        cell = _mapping(matched.get(cell_name), f"matched_cells.{cell_name}")
                        key = (seed, rotation, public_sequence_id, horizon, cell_name)
                        if key in unit_keys:
                            raise ContractError(f"duplicate unit key: {key}")
                        unit_keys.add(key)
                        agent_profile_id = _agent_profile_id(cell_name, cell)
                        output_root = _format_unit_root(
                            protocol,
                            agent_profile_id=agent_profile_id,
                            seed=seed,
                            rotation=rotation,
                            horizon=horizon,
                            public_sequence_id=public_sequence_id,
                        )
                        if output_root in output_roots:
                            raise ContractError(f"duplicate output root: {output_root}")
                        output_roots.add(output_root)
                        argv = (
                            _command_for_unit(
                                protocol,
                                cell_name=cell_name,
                                cell=cell,
                                seed=seed,
                                rotation=rotation,
                                horizon=horizon,
                                public_sequence_id=public_sequence_id,
                                output_root=output_root,
                            )
                            if emit_commands
                            else None
                        )
                        ordinal = len(units) + 1
                        units.append(
                            {
                                "unit_id": schedule["unit_id_format"] % ordinal,
                                "key": {
                                    "seed": seed,
                                    "rotation": rotation,
                                    "public_sequence_id": public_sequence_id,
                                    "horizon": horizon,
                                    "cell": cell_name,
                                },
                                "agent_profile_id": agent_profile_id,
                                "budget": dict(_mapping(budgets[horizon], f"budget.{horizon}")),
                                "output_root": output_root,
                                "argv": argv,
                                "command": None if argv is None else shlex.join(argv),
                            }
                        )

    _expect_equal(
        len(units), schedule.get("expected_episode_bundles"), "scheduled unit count"
    )
    _expect_equal(len(unit_keys), len(units), "unique unit key count")
    _expect_equal(len(output_roots), len(units), "unique output root count")
    return units


def _declared_runner_flags(runner: Path) -> set[str]:
    if not runner.is_file():
        return set()
    try:
        tree = ast.parse(runner.read_text(encoding="utf-8"), filename=str(runner))
    except (OSError, SyntaxError, UnicodeError):
        return set()
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
    return flags


def runtime_readiness(
    protocol: Mapping[str, Any], source: Mapping[str, Any], runner: Path
) -> dict[str, Any]:
    runtime = _mapping(protocol["runtime_projection"], "runtime_projection")
    gates = _mapping(protocol["gates"], "gates")
    runtime_gate = _mapping(gates["runtime_integration"], "gates.runtime_integration")
    required_flags = [
        str(value)
        for value in _list(runtime["required_runner_flags"], "required_runner_flags")
    ]
    declared_flags = _declared_runner_flags(runner)
    missing_runner_flags = [flag for flag in required_flags if flag not in declared_flags]

    runner_text = ""
    if runner.is_file():
        try:
            runner_text = runner.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            runner_text = ""
    required_identities = [
        str(value)
        for value in _list(
            runtime.get("required_runner_identity_literals"),
            "required_runner_identity_literals",
        )
    ]
    missing_runner_identities = [
        value for value in required_identities if value not in runner_text
    ]

    implementation = _mapping(source.get("implementation_status"), "source.implementation_status")
    required_implementation = [
        str(value)
        for value in _list(
            runtime_gate["required_source_implementation_flags"],
            "required_source_implementation_flags",
        )
    ]
    missing_implementation = [
        name for name in required_implementation if implementation.get(name) is not True
    ]
    blocked_reasons = [
        *(f"runner_missing_flag:{flag}" for flag in missing_runner_flags),
        *(f"runner_missing_identity:{value}" for value in missing_runner_identities),
        *(f"source_not_implemented:{name}" for name in missing_implementation),
    ]
    return {
        "ready": not blocked_reasons,
        "runner": runner.relative_to(ROOT).as_posix()
        if runner.is_relative_to(ROOT)
        else str(runner),
        "missing_runner_flags": missing_runner_flags,
        "missing_runner_identity_literals": missing_runner_identities,
        "missing_source_implementation_flags": missing_implementation,
        "blocked_reasons": blocked_reasons,
    }


def build_manifest(protocol_path: Path, runner_override: Path | None = None) -> dict[str, Any]:
    protocol = _load_protocol_yaml(protocol_path)
    _expect_equal(
        protocol.get("schema_version"),
        "graph_horizon_scaling_protocol_v3",
        "schema_version",
    )
    authority = _mapping(protocol.get("authority"), "authority")
    source_path = _resolve_repo_path(
        authority.get("source_dynamic_protocol"), "authority.source_dynamic_protocol"
    )
    source = _load_source_yaml(source_path)
    runtime = _mapping(protocol["runtime_projection"], "runtime_projection")
    runner = runner_override or _resolve_repo_path(runtime.get("runner"), "runtime.runner")
    readiness = runtime_readiness(protocol, source, runner)
    units = build_units(protocol, source, emit_commands=readiness["ready"])
    command_count = sum(unit["argv"] is not None for unit in units)
    return {
        "schema_version": "graph_horizon_scaling_schedule_v3",
        "protocol_id": protocol["protocol_id"],
        "mode": "dry_run",
        "evidence_class": "schedule_only_not_performance_evidence",
        "provider_calls_made": 0,
        "runner_invoked": False,
        "environment_values_read": False,
        "filesystem_writes_made": 0,
        "runtime_integration": readiness,
        "commands_emitted": command_count,
        "commands_suppressed": len(units) - command_count,
        "formal_launch_allowed_by_this_scheduler": False,
        "unit_count": len(units),
        "units": units,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Emit the provider-free deterministic P2-E2 horizon schedule."
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument(
        "--runner",
        type=Path,
        help="Override the runner path for a static integration check only.",
    )
    parser.add_argument(
        "--require-runtime-ready",
        action="store_true",
        help="Exit 3 after emitting the manifest if runtime prerequisites are absent.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    if not args.dry_run:
        parser.error(
            "--dry-run is required; this provider-free scheduler never launches inference"
        )
    try:
        manifest = build_manifest(args.protocol.resolve(), args.runner.resolve() if args.runner else None)
    except (ContractError, KeyError, TypeError, ValueError) as exc:
        print(f"schedule contract error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    if args.require_runtime_ready and not manifest["runtime_integration"]["ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
