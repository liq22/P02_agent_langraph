#!/usr/bin/env python3
"""Validate or execute one registered Generic-base dynamic-v3 formal unit.

``--validate-only`` is strictly provider-free: it does not read provider
environment values or probe evidence, invoke inference, acquire the execution
lock, or write results.  Normal execution is provider-bound and is allowed only
after exact unit, output-root, attempt-prefix, provider-profile, fresh two-turn
probe, and single-process lock checks pass.  The shared dynamic engine remains
``run_graph_experiment.py``; this wrapper owns the formal cohort boundary.
"""

from __future__ import annotations

import argparse
import asyncio
import fcntl
import json
import math
import os
import sys
import time
from collections.abc import Mapping, Sequence
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import yaml

try:
    from analyze_graph_dynamic_formal import (
        FORMAL_EVIDENCE_CLASS,
        GraphDynamicFormalError,
        Unit,
        _read_attempt,
        _validate_attempt_prefixes,
        _validate_manifest,
        _validate_private_evaluation,
        expected_units,
        load_protocol,
        unit_root,
    )
except ModuleNotFoundError:  # Imported as scripts.run_graph_dynamic_formal_v2.
    from scripts.analyze_graph_dynamic_formal import (
        FORMAL_EVIDENCE_CLASS,
        GraphDynamicFormalError,
        Unit,
        _read_attempt,
        _validate_attempt_prefixes,
        _validate_manifest,
        _validate_private_evaluation,
        expected_units,
        load_protocol,
        unit_root,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DYNAMIC_PROTOCOL = (
    ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
)
DEFAULT_DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
)
DEFAULT_PROBE_EVIDENCE = Path(
    "/tmp/openrouter_north_graph_dynamic_v3_two_turn_probe.json"
)
DEFAULT_LOCK_FILE = Path("/tmp/p2_graph_dynamic_v3_formal.lock")

FORMAL_EXECUTION_CONTRACT = "phase1_graph_dynamic_formal_generic_v3"
DYNAMIC_RUNTIME_CONTRACT = "phase1_graph_dynamic_generic_ablation_v3"
DYNAMIC_PROTOCOL_ID = "paderborn_graph_dynamic_ablation_v3"
P2_EXPERIMENT_ID = "p2_graph_vs_generic_llm_v1"
MATCHED_CONTROL_ID = "benchmark_generic_llm_tool_agent_v1"
GRAPH_CONTROL_ID = "graph_decision_control_v1"
REACTIVE_IMPLEMENTATION_ID = "reactive_sequential_agent_v1"
GRAPH_IMPLEMENTATION_ID = "graph_decision_agent_v1"
REACTIVE_AGENT_ID = "reactive-sequential-agent"
GRAPH_AGENT_ID = "graph-decision-agent"
PROVIDER_FAILURE_KIND = "provider_error"
REQUIRED_ROOT_AUXILIARY_FILES = frozenset(
    {"evaluation.jsonl", "run_manifest.json"}
)
ALLOWED_ROOT_AUXILIARY_FILES = REQUIRED_ROOT_AUXILIARY_FILES | {"summary.json"}


class GraphDynamicFormalRunnerError(ValueError):
    """Raised before provider execution when the formal contract drifts."""


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise GraphDynamicFormalRunnerError(f"{label} must be a mapping")
    return dict(value)


def _repo_path(value: str | Path) -> Path:
    path = Path(value)
    return (path if path.is_absolute() else ROOT / path).resolve()


def _same_number(observed: object, expected: object) -> bool:
    return (
        not isinstance(observed, bool)
        and isinstance(observed, (int, float))
        and isinstance(expected, (int, float))
        and math.isfinite(float(observed))
        and float(observed) == float(expected)
    )


def _read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        return _mapping(json.loads(path.read_text(encoding="utf-8")), label)
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphDynamicFormalRunnerError(f"cannot read {label} {path}: {exc}") from exc


def _registered_unit(
    protocol: Mapping[str, Any], args: argparse.Namespace
) -> tuple[int, Unit]:
    requested_cell = (
        "reactive"
        if args.arm == "reactive"
        else f"graph_{args.graph_profile}"
    )
    matches = [
        (ordinal, unit)
        for ordinal, unit in enumerate(expected_units(protocol), 1)
        if unit.seed == args.seed
        and unit.rotation == args.rotation
        and unit.public_sequence_id == args.public_sequence_id
        and unit.cell.horizon == args.horizon
        and unit.cell.name == requested_cell
    ]
    if len(matches) != 1:
        raise GraphDynamicFormalRunnerError(
            "arm/profile/seed/rotation/sequence/horizon is not one registered unit"
        )
    ordinal, unit = matches[0]
    expected_graph_profile = "full" if unit.cell.graph_profile is None else unit.cell.graph_profile
    if args.graph_profile != expected_graph_profile:
        raise GraphDynamicFormalRunnerError("graph profile does not match registered cell")
    return ordinal, unit


def _expected_manifest(
    protocol: Mapping[str, Any], unit: Unit, *, attempt_count: int, complete: bool
) -> dict[str, Any]:
    runtime = protocol["runtime_and_provider_profile"]
    shared = protocol["shared_agent_contract"]["shared"]
    return {
        "study": "graph_dynamic_ablation_v3",
        "dynamic_protocol": protocol["schema_version"],
        "dataset_protocol": protocol["dataset"]["dataset_protocol_schema"],
        "runtime_contract": runtime["effective_runtime_contract"],
        "runtime": "openai",
        "provider_profile_id": runtime["formal_provider_profile_id"],
        "provider": runtime["provider"],
        "model": runtime["model"],
        "inference_protocol": runtime["protocol"],
        "thinking_mode": "not_requested",
        "temperature": shared["temperature"],
        "max_output_tokens_per_turn": shared["max_output_tokens_per_turn"],
        "input_usd_per_million": runtime["input_usd_per_million"],
        "output_usd_per_million": runtime["output_usd_per_million"],
        "arm": unit.cell.arm,
        "graph_policy_profile": (
            "reactive" if unit.cell.graph_profile is None else unit.cell.graph_profile
        ),
        "agent_profile_id": unit.cell.agent_profile_id,
        "seed": unit.seed,
        "rotation": unit.rotation,
        "public_sequence_id": unit.public_sequence_id,
        "horizon": unit.cell.horizon,
        "budget": protocol["budgets"]["by_horizon"][unit.cell.horizon],
        "canonical_episode_count": attempt_count,
        "evidence_class": (
            FORMAL_EVIDENCE_CLASS
            if complete
            else "real_data_provider_failure_not_performance_evidence"
        ),
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": MATCHED_CONTROL_ID,
        "agent_control_id": (
            MATCHED_CONTROL_ID if unit.cell.arm == "reactive" else GRAPH_CONTROL_ID
        ),
        "agent_implementation_id": (
            REACTIVE_IMPLEMENTATION_ID
            if unit.cell.arm == "reactive"
            else GRAPH_IMPLEMENTATION_ID
        ),
    }


def inspect_attempt_prefix(
    output: Path, unit: Unit, protocol: Mapping[str, Any]
) -> dict[str, Any]:
    """Validate an absent, provider-interrupted, or completed unit prefix."""

    if not output.exists():
        return {
            "state": "pending",
            "attempt_count": 0,
            "provider_failure_attempt_count": 0,
            "effective_non_provider_terminal_count": 0,
            "next_attempt_index": 0,
            "complete": False,
        }
    if not output.is_dir():
        raise GraphDynamicFormalRunnerError("registered unit output is not a directory")
    children = list(output.iterdir())
    files = {path.name for path in children if path.is_file()}
    directories = [path for path in children if path.is_dir()]
    attempt_dirs = sorted(
        path for path in directories if path.name.startswith("attempt_")
    )
    unexpected_dirs = sorted(path.name for path in directories if path not in attempt_dirs)
    if unexpected_dirs:
        raise GraphDynamicFormalRunnerError(
            f"unexpected directories in registered unit root: {unexpected_dirs}"
        )
    if not attempt_dirs:
        raise GraphDynamicFormalRunnerError("existing formal unit has no attempt prefix")
    if not REQUIRED_ROOT_AUXILIARY_FILES.issubset(files) or not files.issubset(
        ALLOWED_ROOT_AUXILIARY_FILES
    ):
        raise GraphDynamicFormalRunnerError(
            f"formal unit auxiliary files drifted: {sorted(files)}"
        )
    expected_names = [f"attempt_{index:03d}" for index in range(len(attempt_dirs))]
    if [path.name for path in attempt_dirs] != expected_names:
        raise GraphDynamicFormalRunnerError("attempt directories are not contiguous zero-based")

    try:
        attempts = [
            _read_attempt(path, unit=unit, protocol=protocol) for path in attempt_dirs
        ]
    except GraphDynamicFormalError as exc:
        raise GraphDynamicFormalRunnerError(str(exc)) from exc
    indexes = [item["attempt_index"] for item in attempts]
    if indexes != list(range(len(attempts))):
        raise GraphDynamicFormalRunnerError("attempt metadata is not contiguous zero-based")
    effective = [item for item in attempts if not item["provider_failure"]]
    if len(effective) > 1:
        raise GraphDynamicFormalRunnerError("unit has multiple non-provider terminals")
    if effective and effective[0] is not attempts[-1]:
        raise GraphDynamicFormalRunnerError("attempt exists after effective terminal")
    if any(not item["provider_failure"] for item in attempts[:-1]):
        raise GraphDynamicFormalRunnerError("non-provider terminal was retried")

    complete = len(effective) == 1
    manifest_path = output / "run_manifest.json"
    if complete:
        try:
            _validate_manifest(
                manifest_path,
                unit=unit,
                protocol=protocol,
                attempt_count=len(attempts),
            )
            master = _validate_private_evaluation(
                output / "evaluation.jsonl",
                record=effective[0],
                unit=unit,
            )
            _validate_attempt_prefixes(attempts, master, directory=output)
        except GraphDynamicFormalError as exc:
            raise GraphDynamicFormalRunnerError(str(exc)) from exc
    else:
        manifest = _read_json(manifest_path, "provider-interrupted manifest")
        expected_manifest = _expected_manifest(
            protocol, unit, attempt_count=len(attempts), complete=False
        )
        drift = {
            name: {"observed": manifest.get(name), "expected": expected}
            for name, expected in expected_manifest.items()
            if manifest.get(name) != expected
        }
        if drift:
            raise GraphDynamicFormalRunnerError(
                f"provider-interrupted manifest drifted: {drift}"
            )

    provider_count = sum(item["provider_failure"] for item in attempts)
    return {
        "state": "complete" if complete else "provider_retry_pending",
        "attempt_count": len(attempts),
        "provider_failure_attempt_count": provider_count,
        "effective_non_provider_terminal_count": len(effective),
        "next_attempt_index": None if complete else len(attempts),
        "complete": complete,
    }


def _validate_underlying_runner(protocol: Mapping[str, Any]) -> Path:
    runner = protocol["formal_scheduler"]["runner"]
    path = _repo_path(runner["underlying_path"])
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise GraphDynamicFormalRunnerError(
            f"cannot read registered underlying dynamic runner: {exc}"
        ) from exc
    required = (
        "async def _run_dynamic",
        "--dynamic-protocol",
        "--public-sequence-id",
        "--horizon",
        DYNAMIC_RUNTIME_CONTRACT,
        P2_EXPERIMENT_ID,
        MATCHED_CONTROL_ID,
    )
    missing = [literal for literal in required if literal not in text]
    if missing:
        raise GraphDynamicFormalRunnerError(
            f"underlying dynamic runner proof missing: {missing}"
        )
    return path


def build_dynamic_formal_unit_contract(args: argparse.Namespace) -> dict[str, Any]:
    """Return one exact registered unit contract without reading provider env."""

    dynamic_path = _repo_path(args.dynamic_protocol)
    if dynamic_path != DEFAULT_DYNAMIC_PROTOCOL.resolve():
        raise GraphDynamicFormalRunnerError(
            "only graph_dynamic_ablation_protocol_v3.yaml is launchable; v1/v2 are forbidden"
        )
    try:
        protocol = load_protocol(dynamic_path)
    except GraphDynamicFormalError as exc:
        raise GraphDynamicFormalRunnerError(str(exc)) from exc
    if protocol.get("protocol_id") != DYNAMIC_PROTOCOL_ID:
        raise GraphDynamicFormalRunnerError("dynamic-v3 protocol identity drifted")
    scheduler = _mapping(protocol.get("formal_scheduler"), "formal_scheduler")
    runner = _mapping(scheduler.get("runner"), "formal_scheduler.runner")
    if runner.get("execution_contract") != FORMAL_EXECUTION_CONTRACT:
        raise GraphDynamicFormalRunnerError("formal execution contract drifted")
    if _repo_path(runner.get("path", "")) != Path(__file__).resolve():
        raise GraphDynamicFormalRunnerError("formal runner entrypoint drifted")
    _validate_underlying_runner(protocol)

    if args.runtime != "openai":
        raise GraphDynamicFormalRunnerError("formal dynamic runtime must be openai")
    if args.runtime_contract != DYNAMIC_RUNTIME_CONTRACT:
        raise GraphDynamicFormalRunnerError("dynamic runtime contract drifted")
    if args.tasks != ["online_replay_monitoring"]:
        raise GraphDynamicFormalRunnerError(
            "formal dynamic runner accepts only online_replay_monitoring"
        )
    if args.resume_provider_partial is not True:
        raise GraphDynamicFormalRunnerError(
            "formal units require exact provider-partial resume semantics"
        )
    if (
        args.train_samples_per_bearing != runner["train_samples_per_bearing"]
        or args.validation_samples_per_bearing
        != runner["validation_samples_per_bearing"]
    ):
        raise GraphDynamicFormalRunnerError(
            "training/reference sample-count identity drifted"
        )
    if Path(args.lock_file).resolve() != Path(runner["lock_file_default"]).resolve():
        raise GraphDynamicFormalRunnerError("formal profile lock-file identity drifted")

    runtime = protocol["runtime_and_provider_profile"]
    shared = protocol["shared_agent_contract"]["shared"]
    exact_values = {
        "provider_label": runtime["provider"],
        "temperature": shared["temperature"],
        "max_output_tokens_per_turn": shared["max_output_tokens_per_turn"],
        "input_usd_per_million": runtime["input_usd_per_million"],
        "output_usd_per_million": runtime["output_usd_per_million"],
    }
    for name, expected in exact_values.items():
        observed = getattr(args, name)
        if isinstance(expected, (int, float)):
            matches = _same_number(observed, expected)
        else:
            matches = observed == expected
        if not matches:
            raise GraphDynamicFormalRunnerError(f"explicit {name} drifted")
    expected_env_names = runner["environment_variable_names"]
    for argument, key in (
        ("base_url_env", "base_url"),
        ("api_key_env", "api_key"),
        ("model_env", "model"),
    ):
        if getattr(args, argument) != expected_env_names[key]:
            raise GraphDynamicFormalRunnerError(f"{argument} identity drifted")

    dataset_path = _repo_path(args.protocol)
    expected_dataset_path = _repo_path(runner["dataset_protocol_argument"])
    try:
        same_dataset_file = dataset_path.samefile(expected_dataset_path)
    except OSError:
        same_dataset_file = False
    if not same_dataset_file:
        raise GraphDynamicFormalRunnerError("dataset protocol path drifted")
    try:
        dataset = _mapping(
            yaml.safe_load(dataset_path.read_text(encoding="utf-8")),
            "dataset protocol",
        )
    except (OSError, yaml.YAMLError) as exc:
        raise GraphDynamicFormalRunnerError(
            f"cannot read registered dataset protocol: {exc}"
        ) from exc
    if dataset.get("schema_version") != protocol["dataset"]["dataset_protocol_schema"]:
        raise GraphDynamicFormalRunnerError("dataset protocol schema drifted")

    ordinal, unit = _registered_unit(protocol, args)
    expected_output = (
        ROOT
        / unit_root(
            Path(protocol["output_contract"]["formal_root"]), unit
        )
    ).resolve()
    observed_output = _repo_path(args.output)
    if observed_output != expected_output:
        raise GraphDynamicFormalRunnerError(
            "output must equal the isolated registered dynamic-v3 unit root"
        )
    assignment = scheduler["cell_assignments"][unit.cell.name]
    expected_agent = REACTIVE_AGENT_ID if unit.cell.arm == "reactive" else GRAPH_AGENT_ID
    if assignment["agent_id"] != expected_agent:
        raise GraphDynamicFormalRunnerError("scheduled agent identity drifted")
    attempt_state = inspect_attempt_prefix(observed_output, unit, protocol)
    manifest_fields = list(protocol["formal_analysis"]["manifest_proof_fields"])
    missing_proof_fields = [
        field for field in manifest_fields if field not in _expected_manifest(
            protocol, unit, attempt_count=max(1, attempt_state["attempt_count"]), complete=True
        )
    ]
    if missing_proof_fields:
        raise GraphDynamicFormalRunnerError(
            f"analyzer manifest proof fields are not produced: {missing_proof_fields}"
        )
    return {
        "schema_version": "graph_dynamic_formal_unit_contract_v3",
        "formal_execution_contract": FORMAL_EXECUTION_CONTRACT,
        "protocol_id": DYNAMIC_PROTOCOL_ID,
        "dynamic_protocol": str(dynamic_path),
        "dataset_protocol": str(dataset_path),
        "unit_id": scheduler["unit_id_format"] % ordinal,
        "registered_unit_count": len(expected_units(protocol)),
        "seed": unit.seed,
        "rotation": unit.rotation,
        "public_sequence_id": unit.public_sequence_id,
        "horizon": unit.cell.horizon,
        "cell": unit.cell.name,
        "arm": unit.cell.arm,
        "graph_profile": args.graph_profile,
        "agent_id": assignment["agent_id"],
        "agent_profile_id": assignment["agent_profile_id"],
        "agent_control_id": assignment["agent_control_id"],
        "agent_implementation_id": assignment["agent_implementation_id"],
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": MATCHED_CONTROL_ID,
        "runtime_contract": runtime["effective_runtime_contract"],
        "provider_profile_id": runtime["formal_provider_profile_id"],
        "provider": runtime["provider"],
        "model": runtime["model"],
        "inference_protocol": runtime["protocol"],
        "thinking_mode": "not_requested",
        "temperature": float(shared["temperature"]),
        "max_output_tokens_per_turn": int(shared["max_output_tokens_per_turn"]),
        "input_usd_per_million": float(runtime["input_usd_per_million"]),
        "output_usd_per_million": float(runtime["output_usd_per_million"]),
        "base_url_expected": runner["base_url_expected"],
        "budget": dict(protocol["budgets"]["by_horizon"][unit.cell.horizon]),
        "output": str(observed_output),
        "attempt_state": attempt_state,
        "analyzer_manifest_proof_fields": manifest_fields,
        "provider_calls_performed": False,
        "environment_values_read": False,
        "probe_evidence_read": False,
        "filesystem_writes_performed": False,
    }


def _check_execution_environment(
    args: argparse.Namespace, contract: Mapping[str, Any]
) -> None:
    values = {
        name: os.environ.get(name)
        for name in (args.base_url_env, args.api_key_env, args.model_env)
    }
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise GraphDynamicFormalRunnerError(
            "missing configured provider environment variable names: "
            + ", ".join(missing)
        )
    if values[args.model_env] != contract["model"]:
        raise GraphDynamicFormalRunnerError("configured model identity drifted")
    if str(values[args.base_url_env]).rstrip("/") != str(
        contract["base_url_expected"]
    ).rstrip("/"):
        raise GraphDynamicFormalRunnerError("configured provider base URL drifted")


def _check_probe_evidence(
    path: Path, *, model: str, max_age_hours: float
) -> None:
    probe = _read_json(path, "two-turn probe evidence")
    models = probe.get("models")
    if not isinstance(models, list) or len(models) != 1:
        raise GraphDynamicFormalRunnerError("probe must contain exactly one model result")
    result = _mapping(models[0], "probe model result")
    if (
        result.get("model_id") != model
        or result.get("status") != "passed"
        or result.get("completed_turns") != 2
        or result.get("error") is not None
    ):
        raise GraphDynamicFormalRunnerError(
            "fresh exact-profile two-turn probe has not passed"
        )
    try:
        age_seconds = time.time() - path.stat().st_mtime
    except OSError as exc:
        raise GraphDynamicFormalRunnerError(f"cannot stat probe evidence: {exc}") from exc
    if age_seconds < -300 or age_seconds > max_age_hours * 3600:
        raise GraphDynamicFormalRunnerError("two-turn probe evidence is not fresh")


@contextmanager
def _exclusive_profile_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise GraphDynamicFormalRunnerError(
                "another dynamic-v3 formal provider runner holds the profile lock"
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def execute_dynamic_formal_unit(
    args: argparse.Namespace, contract: Mapping[str, Any]
) -> dict[str, Any]:
    """Execute one pending/retry unit through the shared provider-bound engine."""

    _check_execution_environment(args, contract)
    protocol = load_protocol(_repo_path(args.dynamic_protocol))
    runner = protocol["formal_scheduler"]["runner"]
    _check_probe_evidence(
        Path(args.probe_evidence),
        model=str(contract["model"]),
        max_age_hours=float(runner["probe_max_age_hours"]),
    )
    with _exclusive_profile_lock(Path(args.lock_file)):
        refreshed = build_dynamic_formal_unit_contract(args)
        before = refreshed["attempt_state"]
        if before["complete"]:
            return refreshed
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
            graph_profile=args.graph_profile,
            metadata=args.metadata,
            signal=args.signal,
            protocol=_repo_path(args.protocol),
            dynamic_protocol=_repo_path(args.dynamic_protocol),
            public_sequence_id=args.public_sequence_id,
            horizon=args.horizon,
            rotation=args.rotation,
            tasks=list(args.tasks),
            train_samples_per_bearing=args.train_samples_per_bearing,
            validation_samples_per_bearing=args.validation_samples_per_bearing,
            test_samples_per_bearing=None,
            max_test_bearings=None,
            temperature=args.temperature,
            max_output_tokens_per_turn=args.max_output_tokens_per_turn,
            local_cli_timeout=300.0,
            runtime_contract=args.runtime_contract,
            resume_provider_partial=True,
            seed=args.seed,
            provider_label=args.provider_label,
            input_usd_per_million=args.input_usd_per_million,
            output_usd_per_million=args.output_usd_per_million,
            base_url_env=args.base_url_env,
            api_key_env=args.api_key_env,
            model_env=args.model_env,
            output=_repo_path(args.output),
        )
        dataset = load_dataset_protocol(dynamic_args.protocol)
        _validate_dynamic_arguments(dynamic_args, protocol)
        provider_terminal: SystemExit | None = None
        try:
            asyncio.run(_run_dynamic(dynamic_args, dataset, protocol))
        except SystemExit as exc:
            provider_terminal = exc
        after = build_dynamic_formal_unit_contract(args)
        if after["attempt_state"]["attempt_count"] != before["attempt_count"] + 1:
            raise GraphDynamicFormalRunnerError(
                "provider execution did not append exactly one immutable attempt"
            )
        if provider_terminal is not None:
            if after["attempt_state"]["state"] != "provider_retry_pending":
                raise GraphDynamicFormalRunnerError(
                    "provider terminal did not retain one exact-six retry prefix"
                )
            raise provider_terminal
        if not after["attempt_state"]["complete"]:
            raise GraphDynamicFormalRunnerError(
                "normal execution did not produce one effective terminal"
            )
        return after


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate or run one registered Generic-base dynamic-v3 formal unit."
    )
    parser.add_argument("--arm", choices=("reactive", "graph"), required=True)
    parser.add_argument("--runtime", choices=("openai",), required=True)
    parser.add_argument(
        "--graph-profile",
        choices=(
            "full",
            "no_recovery_revision_edge",
            "no_observation_conditioned_branching",
            "no_persistent_graph_state",
            "no_replanning",
        ),
        required=True,
    )
    parser.add_argument("--runtime-contract", required=True)
    parser.add_argument(
        "--dynamic-protocol", type=Path, default=DEFAULT_DYNAMIC_PROTOCOL
    )
    parser.add_argument("--public-sequence-id", required=True)
    parser.add_argument("--horizon", type=int, required=True)
    parser.add_argument("--tasks", nargs="+", required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--rotation", required=True)
    parser.add_argument("--temperature", type=float, required=True)
    parser.add_argument("--max-output-tokens-per-turn", type=int, required=True)
    parser.add_argument("--provider-label", required=True)
    parser.add_argument("--input-usd-per-million", type=float, required=True)
    parser.add_argument("--output-usd-per-million", type=float, required=True)
    parser.add_argument("--base-url-env", required=True)
    parser.add_argument("--api-key-env", required=True)
    parser.add_argument("--model-env", required=True)
    parser.add_argument("--resume-provider-partial", action="store_true")
    parser.add_argument("--probe-evidence", type=Path, default=DEFAULT_PROBE_EVIDENCE)
    parser.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK_FILE)
    parser.add_argument("--metadata", default="/mnt/e/D01_vibench/metadata.xlsx")
    parser.add_argument("--signal", default="/mnt/e/D01_vibench/RM_027_PU.h5")
    parser.add_argument("--protocol", type=Path, default=DEFAULT_DATASET_PROTOCOL)
    parser.add_argument("--train-samples-per-bearing", type=int, default=8)
    parser.add_argument("--validation-samples-per-bearing", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help=(
            "Validate and print the unit contract without env/probe reads, "
            "provider calls, locks, or filesystem writes."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        contract = build_dynamic_formal_unit_contract(args)
        if args.validate_only or contract["attempt_state"]["complete"]:
            print(json.dumps(contract, indent=2, sort_keys=True, allow_nan=False))
            return 0
        result = execute_dynamic_formal_unit(args, contract)
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0
    except (GraphDynamicFormalRunnerError, GraphDynamicFormalError) as exc:
        print(f"dynamic formal runner contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
