#!/usr/bin/env python3
"""Run one frozen P2-E9 reliability unit through the shared dynamic engine.

The dedicated wrapper owns only the reliability cohort projection: repeat
identity, isolated output layout, exact provider profile, and canonical
provenance fields.  The underlying Generic-base Reactive/Graph implementation
remains ``run_graph_experiment.py``.  ``--validate-only`` is provider-free and
performs no filesystem writes; normal execution is provider-bound.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import math
import os
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

try:
    from analyze_graph_reliability import (
        GraphReliabilityContractError,
        load_graph_reliability_protocol,
    )
except ModuleNotFoundError:  # Imported as scripts.run_graph_reliability_v2.
    from scripts.analyze_graph_reliability import (
        GraphReliabilityContractError,
        load_graph_reliability_protocol,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RELIABILITY_PROTOCOL = (
    ROOT / "paper/experiments/graph_reliability_protocol_v2.yaml"
)
DEFAULT_DYNAMIC_PROTOCOL = (
    ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml"
)
DEFAULT_DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
)
RELIABILITY_EXECUTION_CONTRACT = "phase1_graph_reliability_generic_n10_v2"
DYNAMIC_RUNTIME_CONTRACT = "phase1_graph_dynamic_generic_ablation_v2"
P2_EXPERIMENT_ID = "p2_graph_vs_generic_llm_v1"
MATCHED_CONTROL_ID = "benchmark_generic_llm_tool_agent_v1"
RELIABILITY_PROFILE_ID = "graph_reliability_generic_n10_v2"
DYNAMIC_PROTOCOL_ID = "paderborn_graph_dynamic_ablation_v2"


class GraphReliabilityRunnerError(ValueError):
    """Raised before inference when a dedicated-unit identity has drifted."""


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GraphReliabilityRunnerError(f"{label} must be a mapping")
    return dict(value)


def _repo_path(value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise GraphReliabilityRunnerError(f"cannot load {label} {path}: {exc}") from exc
    return _mapping(value, label)


def _merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_dynamic_protocol(path: Path) -> dict[str, Any]:
    overlay = _load_yaml(path, "dynamic protocol")
    base_name = overlay.pop("extends_protocol", None)
    if base_name is None:
        merged = overlay
    else:
        if not isinstance(base_name, str) or Path(base_name).name != base_name:
            raise GraphReliabilityRunnerError(
                "dynamic protocol extension must name one sibling file"
            )
        merged = _merge(
            _load_yaml(path.parent / base_name, "extended dynamic protocol"),
            overlay,
        )
    if merged.get("schema_version") != "graph_dynamic_ablation_protocol_v2":
        raise GraphReliabilityRunnerError("unsupported dynamic protocol schema")
    return merged


def _same_number(observed: Any, expected: Any) -> bool:
    return (
        not isinstance(observed, bool)
        and isinstance(observed, (int, float))
        and math.isfinite(float(observed))
        and float(observed) == float(expected)
    )


def _validate_output_root(root: Path, protocol: Mapping[str, Any]) -> None:
    execution = protocol["execution"]
    formal_parent = _repo_path(execution["formal_parent_root"])
    if root.is_relative_to(ROOT) and root != formal_parent:
        raise GraphReliabilityRunnerError(
            "repository-local execution must use the exact registered formal parent root"
        )
    for value in [
        *execution["forbidden_primary_roots"],
        *execution["forbidden_legacy_roots"],
    ]:
        forbidden = _repo_path(value)
        if root == forbidden or root.is_relative_to(forbidden) or forbidden.is_relative_to(root):
            raise GraphReliabilityRunnerError(
                f"reliability output root overlaps forbidden root {value}"
            )


def build_reliability_unit_contract(args: argparse.Namespace) -> dict[str, Any]:
    """Validate and return one unit projection without reading provider env values."""

    reliability_path = _repo_path(args.reliability_protocol)
    try:
        protocol = load_graph_reliability_protocol(reliability_path)
    except GraphReliabilityContractError as exc:
        raise GraphReliabilityRunnerError(str(exc)) from exc
    profile = protocol["profile"]
    execution = protocol["execution"]
    scope = protocol["scope"]

    if args.reliability_profile_id != RELIABILITY_PROFILE_ID or (
        args.reliability_profile_id != profile["reliability_profile_id"]
    ):
        raise GraphReliabilityRunnerError("reliability profile ID drifted")
    if execution["dedicated_runner_contract"] != RELIABILITY_EXECUTION_CONTRACT:
        raise GraphReliabilityRunnerError("reliability execution contract drifted")
    if execution["runner_runtime_contract"] != DYNAMIC_RUNTIME_CONTRACT:
        raise GraphReliabilityRunnerError("dynamic runner runtime contract drifted")
    if (
        profile["p2_experiment_id"] != P2_EXPERIMENT_ID
        or profile["matched_control_id"] != MATCHED_CONTROL_ID
    ):
        raise GraphReliabilityRunnerError("P2 Generic-base identity drifted")

    repeats = {
        str(item["repeat_id"]): int(item["seed"])
        for item in protocol["cohort"]["repeats"]
    }
    if args.repeat_id not in repeats:
        raise GraphReliabilityRunnerError("repeat ID is not registered")
    if args.arm not in scope["arms"]:
        raise GraphReliabilityRunnerError("arm is not registered")
    if args.public_sequence_id not in scope["public_sequence_ids"]:
        raise GraphReliabilityRunnerError("public sequence ID is not registered")
    if args.rotation != scope["rotation"]:
        raise GraphReliabilityRunnerError("rotation identity drifted")
    if args.horizon != scope["windows_per_episode"]:
        raise GraphReliabilityRunnerError("reliability horizon identity drifted")
    if args.runtime != "openai":
        raise GraphReliabilityRunnerError("formal reliability runtime must be openai")
    for name in ("input_usd_per_million", "output_usd_per_million"):
        if not _same_number(getattr(args, name), profile[name]):
            raise GraphReliabilityRunnerError(f"explicit {name} drifted")

    dynamic_path = _repo_path(args.dynamic_protocol)
    expected_dynamic_path = _repo_path(execution["dynamic_protocol"])
    if dynamic_path != expected_dynamic_path:
        raise GraphReliabilityRunnerError("dynamic protocol path identity drifted")
    dynamic = _load_dynamic_protocol(dynamic_path)
    if dynamic.get("protocol_id") != DYNAMIC_PROTOCOL_ID or (
        dynamic.get("protocol_id") != execution["dynamic_protocol_id"]
    ):
        raise GraphReliabilityRunnerError("dynamic protocol ID drifted")
    dataset = _mapping(dynamic.get("dataset"), "dynamic.dataset")
    sequence = _mapping(
        dynamic.get("sequence_construction"), "dynamic.sequence_construction"
    )
    runtime = _mapping(
        dynamic.get("runtime_and_provider_profile"), "dynamic runtime profile"
    )
    if dataset.get("rotation") != scope["rotation"]:
        raise GraphReliabilityRunnerError("dynamic/reliability rotation mismatch")
    if dataset.get("held_out_bearings") != len(scope["public_sequence_ids"]):
        raise GraphReliabilityRunnerError("dynamic/reliability sequence count mismatch")
    if args.horizon not in sequence.get("horizons", []):
        raise GraphReliabilityRunnerError("horizon is not registered dynamically")
    expected_runtime = {
        "effective_runtime_contract": DYNAMIC_RUNTIME_CONTRACT,
        "provider": profile["provider"],
        "model": profile["model"],
        "protocol": profile["inference_protocol"],
        "input_usd_per_million": profile["input_usd_per_million"],
        "output_usd_per_million": profile["output_usd_per_million"],
    }
    for name, expected in expected_runtime.items():
        if runtime.get(name) != expected:
            raise GraphReliabilityRunnerError(
                f"dynamic/reliability runtime mismatch for {name}"
            )
    horizon_budget = _mapping(
        _mapping(dynamic.get("budgets"), "dynamic.budgets")
        .get("by_horizon"),
        "dynamic.budgets.by_horizon",
    ).get(args.horizon)
    if horizon_budget != profile["budget"]:
        raise GraphReliabilityRunnerError("dynamic/reliability horizon budget mismatch")
    underlying_runner = _repo_path(execution["underlying_dynamic_runner"])
    try:
        underlying_text = underlying_runner.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise GraphReliabilityRunnerError(
            f"cannot read the registered dynamic runner: {exc}"
        ) from exc
    for literal in (
        "async def _run_dynamic",
        "--dynamic-protocol",
        "--public-sequence-id",
        "--horizon",
        DYNAMIC_RUNTIME_CONTRACT,
        P2_EXPERIMENT_ID,
        MATCHED_CONTROL_ID,
    ):
        if literal not in underlying_text:
            raise GraphReliabilityRunnerError(
                f"underlying dynamic runner identity missing {literal}"
            )

    output_root = Path(args.output_root).resolve()
    _validate_output_root(output_root, protocol)
    run_directory = (
        output_root
        / profile["reliability_profile_id"]
        / args.repeat_id
        / args.arm
        / scope["rotation"]
    )
    formal_parent = _repo_path(execution["formal_parent_root"])
    if output_root == formal_parent and run_directory.parents[2] != _repo_path(
        execution["formal_root"]
    ):
        raise GraphReliabilityRunnerError("formal profile root identity drifted")
    episode_root = (
        run_directory
        / "episodes"
        / scope["rotation"]
        / args.public_sequence_id
        / scope["task_id"]
    )
    return {
        "schema_version": "graph_reliability_unit_contract_v2",
        "experiment_id": "P2-E9",
        "protocol_id": protocol["protocol_id"],
        "reliability_profile_id": profile["reliability_profile_id"],
        "reliability_execution_contract": RELIABILITY_EXECUTION_CONTRACT,
        "dynamic_protocol": str(dynamic_path),
        "dynamic_protocol_id": DYNAMIC_PROTOCOL_ID,
        "runtime_contract": DYNAMIC_RUNTIME_CONTRACT,
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": MATCHED_CONTROL_ID,
        "repeat_id": args.repeat_id,
        "seed": repeats[args.repeat_id],
        "arm": args.arm,
        "agent_id": profile["arms"][args.arm]["agent_id"],
        "agent_control_id": profile["arms"][args.arm]["agent_control_id"],
        "agent_implementation_id": profile["arms"][args.arm][
            "agent_implementation_id"
        ],
        "graph_policy_profile": profile["arms"][args.arm][
            "graph_policy_profile"
        ],
        "rotation": scope["rotation"],
        "public_sequence_id": args.public_sequence_id,
        "horizon": args.horizon,
        "task_id": scope["task_id"],
        "provider": profile["provider"],
        "model": profile["model"],
        "inference_protocol": profile["inference_protocol"],
        "thinking_mode": profile["thinking_mode"],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
        "budget": dict(profile["budget"]),
        "output_root": str(output_root),
        "run_directory": str(run_directory),
        "episode_root": str(episode_root),
        "provider_calls_performed": False,
        "filesystem_writes_performed": False,
        "seed_authority": "registered_reliability_repeat_not_dynamic_primary_seed",
    }


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _stamp_attempts(
    contract: Mapping[str, Any], protocol: Mapping[str, Any]
) -> None:
    episode_root = Path(contract["episode_root"])
    run_directory = Path(contract["run_directory"])
    run_paths = sorted(episode_root.glob("attempt_*/run.json"))
    if not run_paths:
        return
    profile = protocol["profile"]
    shared = protocol["matched_contract"]["shared"]
    expected_existing = {
        "dataset_protocol": shared["dataset_protocol_schema"],
        "runtime_contract": DYNAMIC_RUNTIME_CONTRACT,
        "model": profile["model"],
        "provider": profile["provider"],
        "inference_protocol": profile["inference_protocol"],
        "thinking_mode": profile["thinking_mode"],
        "seed": contract["seed"],
        "rotation": contract["rotation"],
        "horizon": contract["horizon"],
        "public_sequence_id": contract["public_sequence_id"],
        "arm": contract["arm"],
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": MATCHED_CONTROL_ID,
        "agent_control_id": contract["agent_control_id"],
        "agent_implementation_id": contract["agent_implementation_id"],
        "graph_policy_profile": contract["graph_policy_profile"],
        "task_id": contract["task_id"],
    }
    for run_path in run_paths:
        run = json.loads(run_path.read_text(encoding="utf-8"))
        metadata = _mapping(run.get("metadata"), f"run metadata {run_path}")
        drift = {
            name: (metadata.get(name), expected)
            for name, expected in expected_existing.items()
            if metadata.get(name) != expected
        }
        if drift or run.get("agent_id") != contract["agent_id"]:
            raise GraphReliabilityRunnerError(
                f"underlying dynamic unit identity drift: {drift}"
            )
        if run.get("budget") != profile["budget"]:
            raise GraphReliabilityRunnerError("underlying dynamic unit budget drift")
        metadata.update(
            {
                "reliability_profile_id": contract["reliability_profile_id"],
                "reliability_execution_contract": RELIABILITY_EXECUTION_CONTRACT,
                "dataset_protocol_id": shared["dataset_protocol_id"],
                "dataset_protocol_schema": shared["dataset_protocol_schema"],
                "dataset_id": shared["dataset_id"],
                "evaluator_assignment_contract": shared[
                    "evaluator_assignment_contract"
                ],
                "dynamic_protocol_id": DYNAMIC_PROTOCOL_ID,
                "repeat_id": contract["repeat_id"],
                "temperature": profile["temperature"],
                "max_output_tokens_per_turn": profile[
                    "max_output_tokens_per_turn"
                ],
                "input_usd_per_million": float(
                    profile["input_usd_per_million"]
                ),
                "output_usd_per_million": float(
                    profile["output_usd_per_million"]
                ),
            }
        )
        run["metadata"] = metadata
        _write_json(run_path, run)

    all_runs = sorted((run_directory / "episodes").rglob("run.json"))
    non_provider_terminals = 0
    for run_path in all_runs:
        value = json.loads(run_path.read_text(encoding="utf-8"))
        if value.get("failure_kind") != "provider_error":
            non_provider_terminals += 1
    manifest = {
        "study": "graph_reliability_v2",
        "reliability_profile_id": contract["reliability_profile_id"],
        "reliability_execution_contract": RELIABILITY_EXECUTION_CONTRACT,
        "protocol": shared["dataset_protocol_schema"],
        "dataset_protocol_id": shared["dataset_protocol_id"],
        "dataset_protocol_schema": shared["dataset_protocol_schema"],
        "dataset_id": shared["dataset_id"],
        "evaluator_assignment_contract": shared[
            "evaluator_assignment_contract"
        ],
        "runtime_contract": DYNAMIC_RUNTIME_CONTRACT,
        "dynamic_protocol": protocol["execution"]["dynamic_protocol"],
        "dynamic_protocol_id": DYNAMIC_PROTOCOL_ID,
        "seed": contract["seed"],
        "repeat_id": contract["repeat_id"],
        "rotation": contract["rotation"],
        "horizon": contract["horizon"],
        "arm": contract["arm"],
        "agent_id": contract["agent_id"],
        "agent_control_id": contract["agent_control_id"],
        "agent_implementation_id": contract["agent_implementation_id"],
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": MATCHED_CONTROL_ID,
        "graph_policy_profile": contract["graph_policy_profile"],
        "tasks": [contract["task_id"]],
        "temperature": profile["temperature"],
        "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
        "input_usd_per_million": float(profile["input_usd_per_million"]),
        "output_usd_per_million": float(profile["output_usd_per_million"]),
        "model_profile": {
            "provider": profile["provider"],
            "model_id": profile["model"],
            "protocol": profile["inference_protocol"],
            "input_usd_per_million": float(profile["input_usd_per_million"]),
            "output_usd_per_million": float(profile["output_usd_per_million"]),
        },
        "budget": dict(profile["budget"]),
        "evidence_class": protocol["scope"]["evidence_class"],
        "canonical_attempt_count": len(all_runs),
        "canonical_non_provider_terminal_count": non_provider_terminals,
    }
    run_directory.mkdir(parents=True, exist_ok=True)
    _write_json(run_directory / "run_manifest.json", manifest)


def _check_execution_environment(args: argparse.Namespace, profile: Mapping[str, Any]) -> None:
    missing = [
        name
        for name in (args.base_url_env, args.api_key_env, args.model_env)
        if not os.environ.get(name)
    ]
    if missing:
        raise GraphReliabilityRunnerError(
            "missing configured provider environment variable names: "
            + ", ".join(missing)
        )
    if os.environ.get(args.model_env) != profile["model"]:
        raise GraphReliabilityRunnerError("configured model identity drifted")


def execute_reliability_unit(
    args: argparse.Namespace, contract: Mapping[str, Any]
) -> None:
    """Execute one already-validated provider unit and stamp reliability provenance."""

    protocol = load_graph_reliability_protocol(_repo_path(args.reliability_protocol))
    _check_execution_environment(args, protocol["profile"])
    dynamic = _load_dynamic_protocol(_repo_path(args.dynamic_protocol))
    try:
        from run_graph_experiment import _run_dynamic, _validate_dynamic_arguments
    except ModuleNotFoundError:
        from scripts.run_graph_experiment import (
            _run_dynamic,
            _validate_dynamic_arguments,
        )
    from phm_agent_benchmark.phase1.experiment import load_dataset_protocol

    dynamic_args = argparse.Namespace(
        arm=args.arm,
        runtime=args.runtime,
        inject_recoverable_error=False,
        graph_profile="full",
        metadata=args.metadata,
        signal=args.signal,
        protocol=_repo_path(args.dataset_protocol),
        dynamic_protocol=_repo_path(args.dynamic_protocol),
        public_sequence_id=args.public_sequence_id,
        horizon=args.horizon,
        rotation=args.rotation,
        tasks=["online_replay_monitoring"],
        train_samples_per_bearing=args.train_samples_per_bearing,
        validation_samples_per_bearing=args.validation_samples_per_bearing,
        test_samples_per_bearing=None,
        max_test_bearings=None,
        temperature=protocol["profile"]["temperature"],
        max_output_tokens_per_turn=protocol["profile"][
            "max_output_tokens_per_turn"
        ],
        local_cli_timeout=300.0,
        runtime_contract=DYNAMIC_RUNTIME_CONTRACT,
        resume_provider_partial=args.resume_provider_partial,
        seed=contract["seed"],
        provider_label=protocol["profile"]["provider"],
        input_usd_per_million=float(
            protocol["profile"]["input_usd_per_million"]
        ),
        output_usd_per_million=float(
            protocol["profile"]["output_usd_per_million"]
        ),
        base_url_env=args.base_url_env,
        api_key_env=args.api_key_env,
        model_env=args.model_env,
        output=Path(contract["episode_root"]),
    )
    dataset_protocol = load_dataset_protocol(dynamic_args.protocol)
    shared = protocol["matched_contract"]["shared"]
    dataset_identity = _mapping(
        dataset_protocol.get("dataset"), "dataset protocol identity"
    )
    observed_dataset = {
        "dataset_protocol_id": dataset_protocol.get("protocol_id"),
        "dataset_protocol_schema": dataset_protocol.get("schema_version"),
        "dataset_id": dataset_identity.get("dataset_id"),
        "evaluator_assignment_contract": dataset_identity.get(
            "evaluator_assignment_contract"
        ),
    }
    dataset_drift = {
        name: (observed, shared[name])
        for name, observed in observed_dataset.items()
        if observed != shared[name]
    }
    if dataset_drift:
        raise GraphReliabilityRunnerError(
            f"dataset/DataPort authority drift: {dataset_drift}"
        )
    dynamic_projection = copy.deepcopy(dynamic)
    dynamic_projection["experiment_design"]["seeds"] = [
        int(item["seed"]) for item in protocol["cohort"]["repeats"]
    ]
    _validate_dynamic_arguments(dynamic_args, dynamic_projection)
    provider_terminal: SystemExit | None = None
    try:
        asyncio.run(_run_dynamic(dynamic_args, dataset_protocol, dynamic_projection))
    except SystemExit as exc:
        provider_terminal = exc
    _stamp_attempts(contract, protocol)
    if provider_terminal is not None:
        raise provider_terminal


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or run one frozen Generic-base P2-E9 reliability unit."
    )
    parser.add_argument(
        "--reliability-protocol", type=Path, default=DEFAULT_RELIABILITY_PROTOCOL
    )
    parser.add_argument("--reliability-profile-id", required=True)
    parser.add_argument("--repeat-id", required=True)
    parser.add_argument("--arm", choices=("reactive", "graph"), required=True)
    parser.add_argument("--runtime", choices=("openai",), required=True)
    parser.add_argument("--dynamic-protocol", type=Path, required=True)
    parser.add_argument("--public-sequence-id", required=True)
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--rotation", required=True)
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--metadata", default="/mnt/e/D01_vibench/metadata.xlsx")
    parser.add_argument("--signal", default="/mnt/e/D01_vibench/RM_027_PU.h5")
    parser.add_argument(
        "--dataset-protocol", type=Path, default=DEFAULT_DATASET_PROTOCOL
    )
    parser.add_argument("--train-samples-per-bearing", type=int, default=8)
    parser.add_argument("--validation-samples-per-bearing", type=int, default=8)
    parser.add_argument("--base-url-env", default="LLM_BASE_URL")
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--model-env", default="LLM_MODEL")
    parser.add_argument("--resume-provider-partial", action="store_true")
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate and print the unit contract without env reads or filesystem writes.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        contract = build_reliability_unit_contract(args)
        if args.validate_only:
            print(json.dumps(contract, indent=2, sort_keys=True, allow_nan=False))
            return 0
        execute_reliability_unit(args, contract)
        return 0
    except (GraphReliabilityRunnerError, GraphReliabilityContractError) as exc:
        print(f"reliability runner contract error: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
