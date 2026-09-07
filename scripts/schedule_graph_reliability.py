#!/usr/bin/env python3
"""Provider-free scheduling and acceptance for Paper-2 P2-E9.

``schedule`` emits the complete deterministic n=10 assignment set. ``accept``
validates the isolated canonical bundle tree. Neither command imports an LLM
client, constructs an Agent, or authorizes provider execution.
"""

from __future__ import annotations

import argparse
import ast
import json
import shlex
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:  # Direct script execution places this directory on sys.path.
    from analyze_graph_reliability import (
        ACCEPTANCE_SCHEMA_VERSION,
        ARMS,
        DEFAULT_PROTOCOL,
        GraphReliabilityContractError,
        SCHEDULE_SCHEMA_VERSION,
        collect_canonical_records,
        expected_run_directories,
        load_graph_reliability_protocol,
        validate_graph_reliability_acceptance,
        validate_graph_reliability_protocol,
    )
except ModuleNotFoundError:  # Imported as scripts.schedule_graph_reliability.
    from scripts.analyze_graph_reliability import (
        ACCEPTANCE_SCHEMA_VERSION,
        ARMS,
        DEFAULT_PROTOCOL,
        GraphReliabilityContractError,
        SCHEDULE_SCHEMA_VERSION,
        collect_canonical_records,
        expected_run_directories,
        load_graph_reliability_protocol,
        validate_graph_reliability_acceptance,
        validate_graph_reliability_protocol,
    )


def _shared_contract(protocol: Mapping[str, Any]) -> dict[str, Any]:
    profile = protocol["profile"]
    shared = protocol["matched_contract"]["shared"]
    return {
        "dataset_protocol": shared["dataset_protocol_schema"],
        "dataset_protocol_id": shared["dataset_protocol_id"],
        "dataset_protocol_schema": shared["dataset_protocol_schema"],
        "dataset_id": shared["dataset_id"],
        "evaluator_assignment_contract": shared[
            "evaluator_assignment_contract"
        ],
        "base_runtime_contract": profile["base_runtime_contract"],
        "effective_runtime_contract": profile["effective_runtime_contract"],
        "reliability_execution_contract": protocol["execution"][
            "dedicated_runner_contract"
        ],
        "dynamic_protocol": protocol["execution"]["dynamic_protocol"],
        "dynamic_protocol_id": protocol["execution"]["dynamic_protocol_id"],
        "horizon": protocol["scope"]["windows_per_episode"],
        "provider": profile["provider"],
        "model": profile["model"],
        "inference_protocol": profile["inference_protocol"],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
        "budget": dict(profile["budget"]),
        "p2_experiment_id": profile["p2_experiment_id"],
        "matched_control_id": profile["matched_control_id"],
    }


def _declared_runner_flags(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
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


def graph_reliability_runner_readiness(
    protocol_value: Mapping[str, Any], runner_override: str | Path | None = None
) -> dict[str, Any]:
    """Report the real dedicated-runner gap without constructing commands."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    execution = protocol["execution"]
    root = Path(__file__).resolve().parents[1]
    runner = Path(runner_override) if runner_override is not None else root / execution["runner"]
    if not runner.is_absolute():
        runner = root / runner
    runner = runner.resolve()
    required = [str(value) for value in execution["required_runner_flags"]]
    declared = _declared_runner_flags(runner)
    missing = [flag for flag in required if flag not in declared]
    try:
        runner_text = runner.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        runner_text = ""
    required_identities = [
        str(value) for value in execution["required_runner_identity_literals"]
    ]
    missing_identities = [
        value for value in required_identities if value not in runner_text
    ]
    dedicated = execution["dedicated_runner_contract_implemented"] is True
    blocked = [
        *(f"runner_missing_flag:{flag}" for flag in missing),
        *(f"runner_missing_identity:{value}" for value in missing_identities),
    ]
    if not dedicated:
        blocked.append("dedicated_runner_contract_not_implemented")
    return {
        "ready": not blocked,
        "runner": str(runner),
        "dedicated_runner_contract": execution["dedicated_runner_contract"],
        "dedicated_runner_contract_implemented": dedicated,
        "missing_runner_flags": missing,
        "missing_runner_identity_literals": missing_identities,
        "blocked_reasons": blocked,
        "runner_commands_emitted": None,
    }


def _runner_argv(
    protocol: Mapping[str, Any],
    *,
    output_root: Path,
    repeat_id: str,
    arm: str,
    sequence_id: str,
) -> list[str]:
    """Build one frozen command without reading environment values or executing it."""

    execution = protocol["execution"]
    profile = protocol["profile"]
    scope = protocol["scope"]
    return [
        str(execution["python_command"]),
        str(execution["runner"]),
        "--reliability-protocol",
        "paper/experiments/graph_reliability_protocol_v2.yaml",
        "--reliability-profile-id",
        str(profile["reliability_profile_id"]),
        "--repeat-id",
        repeat_id,
        "--arm",
        arm,
        "--runtime",
        "openai",
        "--dynamic-protocol",
        str(execution["dynamic_protocol"]),
        "--public-sequence-id",
        sequence_id,
        "--horizon",
        str(scope["windows_per_episode"]),
        "--rotation",
        str(scope["rotation"]),
        "--input-usd-per-million",
        str(float(profile["input_usd_per_million"])),
        "--output-usd-per-million",
        str(float(profile["output_usd_per_million"])),
        "--output-root",
        str(output_root),
        "--resume-provider-partial",
    ]


def build_graph_reliability_schedule(
    protocol_value: Mapping[str, Any], output_root: str | Path
) -> dict[str, Any]:
    """Return the deterministic assignment set without touching a provider."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    readiness = graph_reliability_runner_readiness(protocol)
    root = Path(output_root).resolve()
    run_dirs = expected_run_directories(root, protocol)
    repeat_rows = protocol["cohort"]["repeats"]
    sequences = protocol["scope"]["public_sequence_ids"]
    rotation = protocol["scope"]["rotation"]
    task_id = protocol["scope"]["task_id"]
    paired_units: list[dict[str, Any]] = []
    episode_assignments: list[dict[str, Any]] = []
    execution_index = 0
    for repeat_index, repeat in enumerate(repeat_rows):
        repeat_id = str(repeat["repeat_id"])
        seed = int(repeat["seed"])
        for sequence_index, sequence_id in enumerate(sequences):
            arm_order = (
                list(ARMS)
                if (repeat_index + sequence_index) % 2 == 0
                else list(reversed(ARMS))
            )
            pair_id = f"{repeat_id}:{rotation}:{sequence_id}"
            unit = {
                "paired_unit_id": pair_id,
                "repeat_id": repeat_id,
                "seed": seed,
                "rotation": rotation,
                "public_sequence_id": sequence_id,
                "task_id": task_id,
                "arm_order": arm_order,
                "matched": True,
            }
            paired_units.append(unit)
            for position, arm in enumerate(arm_order):
                argv = (
                    _runner_argv(
                        protocol,
                        output_root=root,
                        repeat_id=repeat_id,
                        arm=arm,
                        sequence_id=sequence_id,
                    )
                    if readiness["ready"]
                    else None
                )
                episode_assignments.append(
                    {
                        "execution_index": execution_index,
                        "paired_unit_id": pair_id,
                        "within_pair_position": position,
                        "repeat_id": repeat_id,
                        "seed": seed,
                        "rotation": rotation,
                        "public_sequence_id": sequence_id,
                        "task_id": task_id,
                        "arm": arm,
                        "agent_id": protocol["profile"]["arms"][arm]["agent_id"],
                        "agent_control_id": protocol["profile"]["arms"][arm][
                            "agent_control_id"
                        ],
                        "agent_implementation_id": protocol["profile"]["arms"][arm][
                            "agent_implementation_id"
                        ],
                        "graph_policy_profile": protocol["profile"]["arms"][arm][
                            "graph_policy_profile"
                        ],
                        "run_directory": str(run_dirs[(repeat_id, arm)]),
                        "argv": argv,
                        "command": None if argv is None else shlex.join(argv),
                    }
                )
                execution_index += 1

    run_assignments = [
        {
            "assignment_id": f"{repeat['repeat_id']}:{arm}:{rotation}",
            "repeat_id": repeat["repeat_id"],
            "seed": repeat["seed"],
            "arm": arm,
            "rotation": rotation,
            "task_id": task_id,
            "public_sequence_ids": list(sequences),
            "expected_episode_count": len(sequences),
            "run_directory": str(run_dirs[(str(repeat["repeat_id"]), arm)]),
        }
        for repeat in repeat_rows
        for arm in ARMS
    ]
    runner_commands = [
        {
            "execution_index": item["execution_index"],
            "paired_unit_id": item["paired_unit_id"],
            "arm": item["arm"],
            "argv": item["argv"],
            "command": item["command"],
        }
        for item in episode_assignments
        if item["argv"] is not None
    ]
    readiness["runner_commands_emitted"] = len(runner_commands)
    return {
        "schema_version": SCHEDULE_SCHEMA_VERSION,
        "status": "dry_schedule_only",
        "experiment_id": "P2-E9",
        "protocol_id": protocol["protocol_id"],
        "cohort_id": protocol["cohort"]["cohort_id"],
        "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
        "output_root": str(root),
        "output_layout": protocol["execution"]["output_layout"],
        "repeat_ids": [item["repeat_id"] for item in repeat_rows],
        "seeds": [item["seed"] for item in repeat_rows],
        "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
        "arms": list(ARMS),
        "rotation": rotation,
        "public_sequence_ids": list(sequences),
        "run_assignment_count": len(run_assignments),
        "paired_unit_count": len(paired_units),
        "episode_assignment_count": len(episode_assignments),
        "run_assignments": run_assignments,
        "paired_units": paired_units,
        "episode_assignments": episode_assignments,
        "contract": _shared_contract(protocol),
        "runner_readiness": readiness,
        "runner_commands": runner_commands,
        "runner_commands_emitted": len(runner_commands),
        "provider_calls_performed": False,
        "provider_execution_authorized_by_schedule": False,
        "primary_results_ingested": False,
        "pooling_with_three_seed_primary": "forbidden",
        "non_provider_failure_policy": "retain_in_denominator",
        "claim_boundary": "provider_free_schedule_mechanics_only",
    }


def accept_graph_reliability_cohort(
    output_root: str | Path, protocol_value: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate the isolated exact-six cohort and return a retained gate report."""

    protocol = validate_graph_reliability_protocol(protocol_value)
    root = Path(output_root).resolve()
    repeats = protocol["cohort"]["repeats"]
    report: dict[str, Any] = {
        "schema_version": ACCEPTANCE_SCHEMA_VERSION,
        "accepted": False,
        "experiment_id": "P2-E9",
        "protocol_id": protocol["protocol_id"],
        "cohort_id": protocol["cohort"]["cohort_id"],
        "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
        "output_root": str(root),
        "repeat_ids": [item["repeat_id"] for item in repeats],
        "seeds": [item["seed"] for item in repeats],
        "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
        "arms": list(ARMS),
        "rotation": protocol["scope"]["rotation"],
        "public_sequence_ids": protocol["scope"]["public_sequence_ids"],
        "expected_episode_bundles": protocol["scope"][
            "expected_episode_bundles_total"
        ],
        "observed_non_provider_terminals": 0,
        "expected_pairs": protocol["scope"]["expected_pairs_total"],
        "observed_pairs": 0,
        "registered_run_directories": [
            str(path)
            for path in expected_run_directories(root, protocol).values()
        ],
        "contract": _shared_contract(protocol),
        "pooling_with_three_seed_primary": "forbidden",
        "primary_results_ingested": False,
        "non_provider_failure_policy": "retain_in_denominator",
        "provider_calls_performed_by_gate": False,
        "errors": [],
        "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
        "matched_control_id": protocol["profile"]["matched_control_id"],
    }
    try:
        _records, inclusion = collect_canonical_records(root, protocol)
    except GraphReliabilityContractError as exc:
        report["errors"] = [str(exc)]
        return report
    report.update(
        {
            "accepted": True,
            "observed_non_provider_terminals": inclusion[
                "canonical_non_provider_terminal_count"
            ],
            "observed_pairs": inclusion["matched_pair_count"],
            "canonical_inclusion": inclusion,
            "errors": [],
        }
    )
    validate_graph_reliability_acceptance(protocol, report, output_root=root)
    return report


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Dry-schedule or accept the isolated P2-E9 Graph reliability "
            "cohort; this command never calls a provider."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("schedule", "accept"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
        subparser.add_argument("--output-root", type=Path, required=True)
        subparser.add_argument("--output", type=Path)
    args = parser.parse_args()
    protocol = load_graph_reliability_protocol(args.protocol)
    if args.command == "schedule":
        result = build_graph_reliability_schedule(protocol, args.output_root)
    else:
        if args.output is None:
            parser.error("accept requires --output so a rejected gate is retained")
        result = accept_graph_reliability_cohort(args.output_root, protocol)
    if args.output is not None:
        _write_json(args.output, result)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    if args.command == "accept" and not result["accepted"]:
        raise SystemExit("P2-E9 Graph reliability cohort is incomplete")


if __name__ == "__main__":
    main()
