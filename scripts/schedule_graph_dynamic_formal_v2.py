#!/usr/bin/env python3
"""Emit the complete provider-free P2-E2--P2-E7 dynamic-v3 schedule.

The scheduler is intentionally dry-run only.  It materializes every registered
unit and its inert command projection, but never reads provider credentials,
invokes the runner, writes a schedule file, or makes a provider call.  Runnable
command fields remain suppressed until the protocol and cross-file runner proof
jointly establish formal-runtime readiness.
"""

from __future__ import annotations

import argparse
import ast
import json
import shlex
import sys
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
PROTOCOL_SCHEMA = "graph_dynamic_ablation_protocol_v3"
SCHEDULE_SCHEMA = "graph_dynamic_formal_schedule_v3"

EXPECTED_CELLS = {
    3: ["reactive", "graph_full"],
    6: ["reactive", "graph_full"],
    12: [
        "reactive",
        "graph_full",
        "graph_no_recovery_revision_edge",
        "graph_no_observation_conditioned_branching",
        "graph_no_persistent_graph_state",
        "graph_no_replanning",
    ],
}


class ScheduleContractError(ValueError):
    """Raised when a schedule would diverge from dynamic-v3 authority."""


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ScheduleContractError(f"{label} must be a mapping")
    return dict(value)


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise ScheduleContractError(f"{label} must be a list")
    return value


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


def _load_protocol_chain(
    path: Path, *, stack: tuple[Path, ...] = ()
) -> dict[str, Any]:
    if not path.is_file():
        raise ScheduleContractError(f"missing dynamic protocol: {path}")
    resolved = path.resolve()
    if resolved in stack:
        raise ScheduleContractError("dynamic protocol extension cycle detected")
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    protocol = _mapping(value, "dynamic protocol")
    base_name = protocol.pop("extends_protocol", None)
    if base_name is not None:
        if not isinstance(base_name, str) or Path(base_name).name != base_name:
            raise ScheduleContractError(
                "dynamic protocol extension must be one sibling filename"
            )
        base_path = path.parent / base_name
        if not base_path.is_file():
            raise ScheduleContractError(f"missing extended protocol: {base_path}")
        protocol = _deep_merge(
            _load_protocol_chain(base_path, stack=(*stack, resolved)),
            protocol,
        )
    return protocol


def load_protocol(path: Path = DEFAULT_PROTOCOL) -> dict[str, Any]:
    protocol = _load_protocol_chain(path)
    validate_protocol(protocol)
    return protocol


def _expect(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise ScheduleContractError(
            f"{label} mismatch: observed {actual!r}, expected {expected!r}"
        )


def _repo_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ScheduleContractError(f"{label} must be a repository-relative path")
    path = Path(value)
    if path.is_absolute():
        raise ScheduleContractError(f"{label} must be repository-relative")
    resolved = (ROOT / path).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ScheduleContractError(f"{label} escapes the P02 repository") from exc
    return resolved


def _identity_contract(protocol: Mapping[str, Any]) -> dict[str, str]:
    treatment = _mapping(
        protocol.get("treatment_construction"), "treatment_construction"
    )
    values = {
        "base_agent_class": treatment.get("base_agent_class"),
        "p2_experiment_id": treatment.get("p2_experiment_id"),
        "matched_control_id": treatment.get("matched_control_id"),
        "reactive_agent_id": treatment.get("reactive_agent_id"),
        "graph_agent_id": treatment.get("graph_agent_id"),
        "reactive_agent_control_id": treatment.get("reactive_agent_control_id"),
        "graph_agent_control_id": treatment.get("graph_agent_control_id"),
        "reactive_implementation_id": treatment.get("reactive_implementation_id"),
        "graph_implementation_id": treatment.get("graph_implementation_id"),
    }
    if any(not isinstance(value, str) or not value for value in values.values()):
        raise ScheduleContractError("Generic-base identity values must be strings")
    return {key: str(value) for key, value in values.items()}


def validate_protocol(protocol: Mapping[str, Any]) -> None:
    """Validate the exact registered matrix and scheduler projection."""

    _expect(protocol.get("schema_version"), PROTOCOL_SCHEMA, "schema_version")
    _expect(
        protocol.get("protocol_id"),
        "paderborn_graph_dynamic_ablation_v3",
        "protocol_id",
    )
    implementation = _mapping(
        protocol.get("implementation_status"), "implementation_status"
    )
    if implementation.get("formal_matrix_scheduler_implemented") is not True:
        raise ScheduleContractError("formal matrix scheduler is not declared implemented")
    if implementation.get("formal_provider_execution_started") is not False:
        raise ScheduleContractError("scheduler cannot target an already-started profile")

    design = _mapping(protocol.get("experiment_design"), "experiment_design")
    _expect(design.get("seeds"), [20260808, 20260809, 20260810], "seeds")
    _expect(design.get("rotations"), ["rotation_0"], "rotations")
    cells = _mapping(design.get("cells_per_seed_sequence"), "cells")
    for horizon, expected in EXPECTED_CELLS.items():
        _expect(cells.get(f"horizon_{horizon}"), expected, f"horizon_{horizon} cells")
    _expect(design.get("total_cells_per_seed_sequence"), 10, "cell count")
    _expect(design.get("expected_formal_episode_bundles"), 240, "formal units")

    dataset = _mapping(protocol.get("dataset"), "dataset")
    _expect(dataset.get("rotation"), "rotation_0", "dataset rotation")
    _expect(dataset.get("held_out_bearings"), 8, "public sequence count")
    sequence = _mapping(protocol.get("sequence_construction"), "sequence")
    _expect(sequence.get("horizons"), [3, 6, 12], "horizons")
    _expect(
        sequence.get("horizon_sequence"),
        "sequence_h = master_sequence[0:h]",
        "nested horizon construction",
    )
    if sequence.get("independently_resample_each_horizon") is not False:
        raise ScheduleContractError("independent horizon sampling is forbidden")

    identity = _identity_contract(protocol)
    expected_identity = {
        "base_agent_class": "phm_agent_benchmark.phase1.GenericLLMToolAgent",
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "reactive_agent_id": "reactive-sequential-agent",
        "graph_agent_id": "graph-decision-agent",
        "reactive_agent_control_id": "benchmark_generic_llm_tool_agent_v1",
        "graph_agent_control_id": "graph_decision_control_v1",
        "reactive_implementation_id": "reactive_sequential_agent_v1",
        "graph_implementation_id": "graph_decision_agent_v1",
    }
    _expect(identity, expected_identity, "Generic-base identity")
    if protocol["treatment_construction"].get(
        "legacy_phmskills_superclass_allowed"
    ) is not False:
        raise ScheduleContractError("legacy PHMskills base must remain forbidden")

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
    }
    for key, expected in expected_runtime.items():
        _expect(runtime.get(key), expected, f"runtime.{key}")
    shared = _mapping(
        _mapping(protocol.get("shared_agent_contract"), "shared_agent_contract").get(
            "shared"
        ),
        "shared_agent_contract.shared",
    )
    expected_shared = {
        "backbone_model": runtime["model"],
        "provider": runtime["provider"],
        "inference_protocol": runtime["protocol"],
        "temperature": 0.2,
        "max_output_tokens_per_turn": 2048,
    }
    for key, expected in expected_shared.items():
        _expect(shared.get(key), expected, f"shared_agent_contract.shared.{key}")

    scheduler = _mapping(protocol.get("formal_scheduler"), "formal_scheduler")
    _expect(scheduler.get("schema_version"), SCHEDULE_SCHEMA, "scheduler schema")
    _expect(scheduler.get("mode"), "provider_free_dry_run_only", "scheduler mode")
    for field in (
        "provider_calls_allowed",
        "runner_invocation_allowed",
        "environment_value_reads_allowed",
        "filesystem_writes_allowed",
    ):
        if scheduler.get(field) is not False:
            raise ScheduleContractError(f"formal_scheduler.{field} must be false")
    _expect(
        scheduler.get("schedule_order"),
        ["seed", "rotation", "public_sequence_id", "horizon", "cell"],
        "schedule order",
    )
    _expect(scheduler.get("expected_unique_units"), 240, "scheduler unit count")

    assignments = _mapping(scheduler.get("cell_assignments"), "cell_assignments")
    registered_cells = {name for names in EXPECTED_CELLS.values() for name in names}
    _expect(set(assignments), registered_cells, "cell assignment names")
    profiles = _mapping(protocol.get("graph_profiles"), "graph_profiles")
    for cell_name, assignment_value in assignments.items():
        assignment = _mapping(assignment_value, f"assignment {cell_name}")
        if cell_name == "reactive":
            expected = {
                "arm": "reactive",
                "graph_profile": "full",
                "agent_id": identity["reactive_agent_id"],
                "agent_profile_id": protocol["formal_analysis"]["agent_identity"][
                    "reactive_agent_profile_id"
                ],
                "agent_control_id": identity["reactive_agent_control_id"],
                "agent_implementation_id": identity["reactive_implementation_id"],
            }
        else:
            graph_profile = cell_name.removeprefix("graph_")
            expected = {
                "arm": "graph",
                "graph_profile": graph_profile,
                "agent_id": identity["graph_agent_id"],
                "agent_profile_id": profiles[graph_profile]["agent_profile_id"],
                "agent_control_id": identity["graph_agent_control_id"],
                "agent_implementation_id": identity["graph_implementation_id"],
            }
        _expect(assignment, expected, f"assignment {cell_name}")

    output = _mapping(protocol.get("output_contract"), "output_contract")
    formal_root = output.get("formal_root")
    if not isinstance(formal_root, str):
        raise ScheduleContractError("formal output root must be a string")
    if "graph_dynamic_ablation_v3" not in formal_root or "ablation_v1" in formal_root:
        raise ScheduleContractError("formal output root is not isolated dynamic-v3")
    expected_count = (
        len(design["seeds"])
        * len(design["rotations"])
        * int(dataset["held_out_bearings"])
        * sum(len(value) for value in EXPECTED_CELLS.values())
    )
    _expect(expected_count, 240, "derived formal units")


def _registered_contrasts(horizon: int, cell: str) -> list[str]:
    contrasts: list[str] = []
    if cell in {"reactive", "graph_full"}:
        contrasts.append("P2-E2")
    if horizon == 12:
        specific = {
            "graph_no_recovery_revision_edge": "P2-E3",
            "graph_no_observation_conditioned_branching": "P2-E4",
            "graph_no_persistent_graph_state": "P2-E5",
            "graph_no_replanning": "P2-E6",
        }
        if cell == "graph_full":
            contrasts.extend(["P2-E3", "P2-E4", "P2-E5", "P2-E6"])
        elif cell in specific:
            contrasts.append(specific[cell])
        if cell in {
            "reactive",
            "graph_full",
            "graph_no_observation_conditioned_branching",
        }:
            contrasts.append("P2-E7")
    return contrasts


def _unit_argv(
    protocol: Mapping[str, Any],
    assignment: Mapping[str, Any],
    *,
    seed: int,
    rotation: str,
    public_sequence_id: str,
    horizon: int,
    output_root: str,
) -> list[str]:
    scheduler = _mapping(protocol["formal_scheduler"], "formal_scheduler")
    runner = _mapping(scheduler["runner"], "formal_scheduler.runner")
    runtime = _mapping(
        protocol["runtime_and_provider_profile"], "runtime_and_provider_profile"
    )
    shared = _mapping(
        protocol["shared_agent_contract"]["shared"], "shared_agent_contract.shared"
    )
    env_names = _mapping(runner["environment_variable_names"], "environment names")
    return [
        str(runner["python_command"]),
        str(runner["path"]),
        "--arm",
        str(assignment["arm"]),
        "--runtime",
        str(runner["runtime"]),
        "--graph-profile",
        str(assignment["graph_profile"]),
        "--runtime-contract",
        str(runtime["effective_runtime_contract"]),
        "--dynamic-protocol",
        str(runner["dynamic_protocol_argument"]),
        "--protocol",
        str(runner["dataset_protocol_argument"]),
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
        str(runtime["provider"]),
        "--input-usd-per-million",
        str(runtime["input_usd_per_million"]),
        "--output-usd-per-million",
        str(runtime["output_usd_per_million"]),
        "--base-url-env",
        str(env_names["base_url"]),
        "--api-key-env",
        str(env_names["api_key"]),
        "--model-env",
        str(env_names["model"]),
        "--resume-provider-partial",
        "--train-samples-per-bearing",
        str(runner["train_samples_per_bearing"]),
        "--validation-samples-per-bearing",
        str(runner["validation_samples_per_bearing"]),
        "--probe-evidence",
        str(runner["probe_evidence_default"]),
        "--output",
        output_root,
    ]


def _unit_root(
    protocol: Mapping[str, Any],
    *,
    agent_profile_id: str,
    seed: int,
    rotation: str,
    horizon: int,
    public_sequence_id: str,
) -> str:
    scheduler = _mapping(protocol["formal_scheduler"], "formal_scheduler")
    output = _mapping(protocol["output_contract"], "output_contract")
    pattern = scheduler.get("output_pattern")
    if not isinstance(pattern, str):
        raise ScheduleContractError("formal scheduler output pattern must be a string")
    try:
        return pattern.format(
            formal_root=output["formal_root"],
            agent_profile_id=agent_profile_id,
            seed=seed,
            rotation=rotation,
            horizon=horizon,
            public_sequence_id=public_sequence_id,
        )
    except (KeyError, ValueError) as exc:
        raise ScheduleContractError("invalid scheduler output pattern") from exc


def build_units(
    protocol: Mapping[str, Any], *, expose_runnable_commands: bool = False
) -> list[dict[str, Any]]:
    validate_protocol(protocol)
    design = _mapping(protocol["experiment_design"], "experiment_design")
    dataset = _mapping(protocol["dataset"], "dataset")
    scheduler = _mapping(protocol["formal_scheduler"], "formal_scheduler")
    assignments = _mapping(scheduler["cell_assignments"], "cell_assignments")
    budgets = _mapping(protocol["budgets"]["by_horizon"], "budgets.by_horizon")
    runtime = _mapping(
        protocol["runtime_and_provider_profile"], "runtime_and_provider_profile"
    )
    shared = _mapping(
        protocol["shared_agent_contract"]["shared"], "shared_agent_contract.shared"
    )
    treatment = _identity_contract(protocol)

    sequence_format = scheduler.get("public_sequence_id_format")
    unit_format = scheduler.get("unit_id_format")
    if not isinstance(sequence_format, str) or not isinstance(unit_format, str):
        raise ScheduleContractError("unit and public-sequence formats must be strings")
    sequence_ids = [
        sequence_format % index
        for index in range(1, int(dataset["held_out_bearings"]) + 1)
    ]
    cells_by_horizon = _mapping(design["cells_per_seed_sequence"], "cells")
    units: list[dict[str, Any]] = []
    keys: set[tuple[object, ...]] = set()
    roots: set[str] = set()

    for seed_value in design["seeds"]:
        seed = int(seed_value)
        for rotation_value in design["rotations"]:
            rotation = str(rotation_value)
            for public_sequence_id in sequence_ids:
                for horizon in (3, 6, 12):
                    for cell in cells_by_horizon[f"horizon_{horizon}"]:
                        assignment = _mapping(assignments[cell], f"assignment {cell}")
                        key = (seed, rotation, public_sequence_id, horizon, cell)
                        if key in keys:
                            raise ScheduleContractError(f"duplicate formal unit key: {key}")
                        keys.add(key)
                        output_root = _unit_root(
                            protocol,
                            agent_profile_id=str(assignment["agent_profile_id"]),
                            seed=seed,
                            rotation=rotation,
                            horizon=horizon,
                            public_sequence_id=public_sequence_id,
                        )
                        if output_root in roots:
                            raise ScheduleContractError(
                                f"duplicate formal unit output root: {output_root}"
                            )
                        roots.add(output_root)
                        planned_argv = _unit_argv(
                            protocol,
                            assignment,
                            seed=seed,
                            rotation=rotation,
                            public_sequence_id=public_sequence_id,
                            horizon=horizon,
                            output_root=output_root,
                        )
                        ordinal = len(units) + 1
                        units.append(
                            {
                                "unit_id": unit_format % ordinal,
                                "key": {
                                    "seed": seed,
                                    "rotation": rotation,
                                    "public_sequence_id": public_sequence_id,
                                    "horizon": horizon,
                                    "cell": cell,
                                },
                                "assignment": {
                                    "arm": assignment["arm"],
                                    "graph_profile": assignment["graph_profile"],
                                    "horizon": horizon,
                                    "agent_id": assignment["agent_id"],
                                    "agent_profile_id": assignment["agent_profile_id"],
                                    "agent_control_id": assignment["agent_control_id"],
                                    "agent_implementation_id": assignment[
                                        "agent_implementation_id"
                                    ],
                                },
                                "generic_base_identity": {
                                    "base_agent_class": treatment["base_agent_class"],
                                    "p2_experiment_id": treatment["p2_experiment_id"],
                                    "matched_control_id": treatment["matched_control_id"],
                                    "legacy_phmskills_superclass_allowed": False,
                                },
                                "runtime_identity": {
                                    "runtime_contract": runtime[
                                        "effective_runtime_contract"
                                    ],
                                    "provider_profile_id": runtime[
                                        "formal_provider_profile_id"
                                    ],
                                    "provider": runtime["provider"],
                                    "model": runtime["model"],
                                    "inference_protocol": runtime["protocol"],
                                    "temperature": shared["temperature"],
                                    "max_output_tokens_per_turn": shared[
                                        "max_output_tokens_per_turn"
                                    ],
                                    "input_usd_per_million": runtime[
                                        "input_usd_per_million"
                                    ],
                                    "output_usd_per_million": runtime[
                                        "output_usd_per_million"
                                    ],
                                },
                                "registered_contrasts": _registered_contrasts(
                                    horizon, cell
                                ),
                                "budget": dict(
                                    _mapping(budgets[horizon], f"budget {horizon}")
                                ),
                                "output_root": output_root,
                                "planned_argv": planned_argv,
                                "planned_command": shlex.join(planned_argv),
                                "argv": planned_argv if expose_runnable_commands else None,
                                "command": (
                                    shlex.join(planned_argv)
                                    if expose_runnable_commands
                                    else None
                                ),
                            }
                        )

    expected = int(scheduler["expected_unique_units"])
    _expect(len(units), expected, "emitted unit count")
    _expect(len(keys), expected, "unique unit keys")
    _expect(len(roots), expected, "isolated output roots")
    return units


def _ast_evidence(path: Path) -> tuple[set[str], set[str], str | None]:
    if not path.is_file():
        return set(), set(), "missing"
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError, UnicodeError) as exc:
        return set(), set(), type(exc).__name__
    flags: set[str] = set()
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value)
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
    return flags, literals, None


def runtime_readiness(
    protocol: Mapping[str, Any],
    *,
    runner_override: Path | None = None,
    identity_proof_overrides: Sequence[Path] | None = None,
) -> dict[str, Any]:
    validate_protocol(protocol)
    scheduler = _mapping(protocol["formal_scheduler"], "formal_scheduler")
    runner_contract = _mapping(scheduler["runner"], "formal_scheduler.runner")
    runner = runner_override or _repo_path(runner_contract["path"], "runner.path")
    if identity_proof_overrides is None:
        proof_files = [
            _repo_path(value, "runner.identity_proof_files")
            for value in _list(
                runner_contract["identity_proof_files"], "identity proof files"
            )
        ]
    else:
        proof_files = list(identity_proof_overrides)
    if runner not in proof_files:
        proof_files.insert(0, runner)

    runner_flags, _runner_literals, runner_error = _ast_evidence(runner)
    required_flags = [
        str(value)
        for value in _list(runner_contract["required_flags"], "required flags")
    ]
    missing_flags = [flag for flag in required_flags if flag not in runner_flags]

    all_literals: set[str] = set()
    invalid_proof_files: list[str] = []
    for path in proof_files:
        _flags, literals, error = _ast_evidence(path)
        all_literals.update(literals)
        if error is not None:
            invalid_proof_files.append(f"{path}:{error}")
    required_literals = [
        str(value)
        for value in _list(
            runner_contract["required_identity_literals"],
            "required identity literals",
        )
    ]
    missing_literals = [
        literal for literal in required_literals if literal not in all_literals
    ]

    implementation = _mapping(
        protocol["implementation_status"], "implementation_status"
    )
    gate = _mapping(scheduler["readiness_gate"], "readiness_gate")
    required_implementation = [
        str(value)
        for value in _list(
            gate["required_implementation_flags"],
            "required implementation flags",
        )
    ]
    missing_implementation = [
        name for name in required_implementation if implementation.get(name) is not True
    ]
    blocked_reasons = [
        *(f"runner_ast_unavailable:{runner_error}" for _ in [0] if runner_error),
        *(f"runner_missing_flag:{flag}" for flag in missing_flags),
        *(f"identity_proof_unavailable:{item}" for item in invalid_proof_files),
        *(f"runner_missing_identity:{literal}" for literal in missing_literals),
        *(f"source_not_implemented:{name}" for name in missing_implementation),
    ]
    return {
        "ready": not blocked_reasons,
        "runner": str(runner),
        "identity_proof_files": [str(path) for path in proof_files],
        "missing_runner_flags": missing_flags,
        "missing_identity_literals": missing_literals,
        "invalid_identity_proof_files": invalid_proof_files,
        "missing_implementation_flags": missing_implementation,
        "blocked_reasons": blocked_reasons,
    }


def build_manifest(
    protocol_path: Path = DEFAULT_PROTOCOL,
    *,
    runner_override: Path | None = None,
    identity_proof_overrides: Sequence[Path] | None = None,
) -> dict[str, Any]:
    protocol = load_protocol(protocol_path)
    readiness = runtime_readiness(
        protocol,
        runner_override=runner_override,
        identity_proof_overrides=identity_proof_overrides,
    )
    units = build_units(protocol, expose_runnable_commands=readiness["ready"])
    contrast_counts = Counter(
        contrast for unit in units for contrast in unit["registered_contrasts"]
    )
    commands_emitted = sum(unit["argv"] is not None for unit in units)
    return {
        "schema_version": SCHEDULE_SCHEMA,
        "protocol_schema_version": protocol["schema_version"],
        "protocol_id": protocol["protocol_id"],
        "mode": "dry_run",
        "evidence_class": "schedule_only_not_performance_evidence",
        "provider_calls_made": 0,
        "runner_invoked": False,
        "environment_values_read": False,
        "filesystem_writes_made": 0,
        "runtime_readiness": readiness,
        "planned_commands": len(units),
        "commands_emitted": commands_emitted,
        "commands_suppressed": len(units) - commands_emitted,
        "formal_launch_allowed_by_this_scheduler": False,
        "unit_count": len(units),
        "unique_output_root_count": len({unit["output_root"] for unit in units}),
        "registered_contrast_unit_references": dict(sorted(contrast_counts.items())),
        "units": units,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit the provider-free dry-run schedule for all 240 registered "
            "P2-E2--P2-E7 dynamic-v3 units."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Explicitly select the default and only supported mode.",
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument(
        "--runner",
        type=Path,
        help="Override the runner only for a provider-free static readiness audit.",
    )
    parser.add_argument(
        "--identity-proof-file",
        action="append",
        type=Path,
        help="Override cross-file identity proof sources for a static audit.",
    )
    parser.add_argument(
        "--require-runtime-ready",
        action="store_true",
        help="Exit 3 after emission when the formal runner proof is incomplete.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        manifest = build_manifest(
            args.protocol.resolve(),
            runner_override=args.runner.resolve() if args.runner else None,
            identity_proof_overrides=(
                [path.resolve() for path in args.identity_proof_file]
                if args.identity_proof_file
                else None
            ),
        )
    except (OSError, ScheduleContractError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"schedule contract error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    if args.require_runtime_ready and not manifest["runtime_readiness"]["ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
