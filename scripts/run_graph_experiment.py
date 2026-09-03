#!/usr/bin/env python3
"""Run one matched reactive-vs-graph PHM policy arm."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from phm_agent_benchmark import EvaluatorResult, write_episode_bundle, write_run_bundle
from phm_agent_benchmark.protocol import (
    PROTOCOL_VERSION,
    USAGE_ACCOUNTING_CONTRACT,
    DataAccessScope,
    EpisodeSpec,
)
from phm_agent_benchmark.rollout_io import (
    RunBundleView,
    read_cohort_rollout_views,
    read_run_bundle,
)
from phm_agent_benchmark.phase1 import (
    Budget,
    DeterministicMockLLM,
    LocalCSVPhase1DataPort,
    LocalPaderbornDataPort,
    LocalCLIJSONLLM,
    ModelProfile,
    OpenAICompatibleLLM,
    RUNTIME_PROTOCOLS,
)
from phm_agent_benchmark.phase1.experiment import (
    EVALUATOR_ASSIGNMENT_CONTRACT,
    aggregate_results,
    attach_model_cost,
    build_evaluator_assignments,
    load_dataset_protocol,
    require_formal_replay_metric_lock,
    run_rotation,
    validate_evaluator_records,
)
from phm_agent_benchmark.phase1.cohort import (
    COHORT_RESUME_IDENTITY_CONTRACT,
    episode_attempt_directory,
    read_cohort_index,
    registered_data_provider_contract,
    validate_cohort_index,
    write_cohort_index,
)
from phm_agent_benchmark.phase1.environment import PHASE1_BASE_RUNTIME_CONTRACT
from phm_agent_benchmark.phase1.resume import (
    ProviderResumePlan,
    ResumeProfile,
    load_provider_partial,
)
from phm_graph_agent import GraphDecisionAgent, ReactiveSequentialAgent
from phm_graph_agent.dynamic_runtime import (
    build_master_sequences,
    fit_dynamic_model_pool,
    run_dynamic_episode,
)
from phm_graph_agent.state import (
    GRAPH_DYNAMIC_RUNTIME_CONTRACT,
    GRAPH_DYNAMIC_RUNTIME_CONTRACTS,
    GRAPH_POLICY_PROFILES,
    GraphPolicyConfig,
    transition_validity_from_states as profile_transition_validity,
)


P2_EXPERIMENT_ID = "p2_graph_vs_generic_llm_v1"
P2_MATCHED_CONTROL_ID = "benchmark_generic_llm_tool_agent_v1"
P2_GRAPH_CONTROL_ID = "graph_decision_control_v1"
P2_REACTIVE_IMPLEMENTATION_ID = "reactive_sequential_agent_v1"
P2_GRAPH_IMPLEMENTATION_ID = "graph_decision_agent_v1"
P2_E8_PROTOCOL_SCHEMA = "graph_cross_dataset_replay_protocol_v3"
P2_E8_PROTOCOL_ID = "phm_graph_cross_dataset_replay_ottawa_generic_base_p2e8_v3"
P2_E8_PROFILE_ID = "paper2-cross-dataset-ottawa-generic-v1"
P2_E8_DATASET_ID = "university-of-ottawa-uored-vafcls-v5"
P2_E8_DATASET_PROTOCOL_ID = "ottawa_uored_v5_ordered_state_replay_v1"
P2_E8_DATA_BACKEND = "csv_directory"
P2_E8_RUNTIME_CONTRACT = "phase1_opaque_sample_vibration_feature_schema_v6"
_SAFE_ENVIRONMENT_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
BENCHMARK_CONTROL_SOURCE_CONTRACT = "benchmark_active_v0_2_control_source_v1"
ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID = (
    "benchmark_v0_2_0--paderborn_phase1_v1--runtime_v6--window_v3"
)
ACTIVE_BENCHMARK_CONTROL_PROFILE_ID = "paper0-paderborn-primary-v1"
FORMAL_RUN_STAMP_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
ACTIVE_GRAPH_DYNAMIC_RUNTIME_CONTRACT = (
    "phase1_graph_dynamic_generic_ablation_v3"
)
LEGACY_GRAPH_DYNAMIC_RUNTIME_CONTRACT = (
    "phase1_graph_dynamic_generic_ablation_v2"
)
if GRAPH_DYNAMIC_RUNTIME_CONTRACT != ACTIVE_GRAPH_DYNAMIC_RUNTIME_CONTRACT:
    raise RuntimeError("active Graph dynamic runtime identity drifted")
if LEGACY_GRAPH_DYNAMIC_RUNTIME_CONTRACT not in GRAPH_DYNAMIC_RUNTIME_CONTRACTS:
    raise RuntimeError("retained Graph dynamic-v2 runtime compatibility drifted")


def _benchmark_control_source(
    args: argparse.Namespace,
    *,
    required: bool,
) -> dict[str, str] | None:
    """Return the public-safe identity of the matched Benchmark control run."""

    raw = {
        "formal_run_stamp": getattr(args, "benchmark_formal_run_stamp", None),
        "protocol_id": getattr(args, "benchmark_control_protocol_id", None),
        "profile_id": getattr(args, "benchmark_control_profile_id", None),
    }
    supplied = {name for name, value in raw.items() if value is not None}
    if not supplied:
        if required:
            raise ValueError(
                "formal Graph execution requires --benchmark-formal-run-stamp, "
                "--benchmark-control-protocol-id, and "
                "--benchmark-control-profile-id"
            )
        return None
    missing = sorted(set(raw) - supplied)
    if missing:
        raise ValueError(
            "Benchmark control provenance must be supplied as one complete identity; "
            f"missing {missing}"
        )

    source = {name: str(value) for name, value in raw.items()}
    if not FORMAL_RUN_STAMP_PATTERN.fullmatch(source["formal_run_stamp"]):
        raise ValueError("benchmark formal run stamp must match YYYYMMDDTHHMMSSZ")
    if source["protocol_id"] != ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID:
        raise ValueError(
            "Benchmark control protocol is not the active P2-E1 control: "
            f"{source['protocol_id']!r}"
        )
    if source["profile_id"] != ACTIVE_BENCHMARK_CONTROL_PROFILE_ID:
        raise ValueError(
            "Benchmark control profile is not the active P2-E1 control: "
            f"{source['profile_id']!r}"
        )

    output = Path(args.output).resolve()
    run_root = output.parent.parent
    expected_run_name = f"run_{source['formal_run_stamp']}"
    if output.name != str(args.rotation) or output.parent.name != f"seed_{args.seed}":
        raise ValueError(
            "formal Graph output must end in "
            f"seed_{args.seed}/{args.rotation}"
        )
    if run_root.name != expected_run_name:
        raise ValueError(
            "formal Graph output belongs to a different Benchmark run stamp: "
            f"expected {expected_run_name!r}, observed {run_root.name!r}"
        )
    if run_root.parent.name != source["profile_id"]:
        raise ValueError(
            "formal Graph output is outside the matched Benchmark control profile"
        )
    if len(run_root.parents) < 3 or run_root.parents[2].name != source["protocol_id"]:
        raise ValueError(
            "formal Graph output is outside the matched Benchmark control protocol"
        )
    return {
        "contract": BENCHMARK_CONTROL_SOURCE_CONTRACT,
        **source,
    }


def _load_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuntimeError(f"cannot load {label}: {exc}") from exc
    if not isinstance(value, dict):
        raise RuntimeError(f"{label} root must be a mapping")
    return value


def _cross_dataset_contract(
    args: argparse.Namespace,
    dataset_protocol: Mapping[str, Any],
) -> dict[str, Any] | None:
    requested = getattr(args, "cross_dataset_protocol", None)
    optional_values = {
        "--dataset-id": getattr(args, "dataset_id", None),
        "--metadata-env": getattr(args, "metadata_env", None),
        "--signal-env": getattr(args, "signal_env", None),
        "--data-readiness-env": getattr(args, "data_readiness_env", None),
        "--experiment-profile-id": getattr(args, "experiment_profile_id", None),
    }
    if requested is None:
        supplied = [name for name, value in optional_values.items() if value is not None]
        if supplied:
            raise RuntimeError(
                "cross-dataset runner flags require --cross-dataset-protocol: "
                + ", ".join(supplied)
            )
        if getattr(args, "data_backend", "local_hdf5") != "local_hdf5":
            raise RuntimeError("external data backends require --cross-dataset-protocol")
        return None

    path = Path(requested).expanduser().resolve()
    cached = getattr(args, "_cross_dataset_contract_cache", None)
    if cached is not None and cached[0] == str(path):
        return dict(cached[1])
    contract = _load_mapping(path, "P2-E8 cross-dataset protocol")
    if contract.get("extends_protocol") != "graph_cross_dataset_replay_protocol_v2.yaml":
        raise RuntimeError("P2-E8 v3 must explicitly extend the frozen v2 record")
    if contract.get("schema_version") != P2_E8_PROTOCOL_SCHEMA:
        raise RuntimeError("P2-E8 cross-dataset protocol schema drifted")
    if contract.get("protocol_id") != P2_E8_PROTOCOL_ID:
        raise RuntimeError("P2-E8 cross-dataset protocol identity drifted")
    if contract.get("supersedes_protocol") != (
        "paper/experiments/graph_cross_dataset_replay_protocol_v2.yaml"
    ):
        raise RuntimeError("P2-E8 v3 supersession identity drifted")

    registration = contract.get("dataset_registration")
    formal = contract.get("formal_execution")
    if not isinstance(registration, Mapping) or not isinstance(formal, Mapping):
        raise RuntimeError("P2-E8 dataset and formal registrations are required")
    observed_dataset = dataset_protocol.get("dataset")
    if not isinstance(observed_dataset, Mapping):
        raise RuntimeError("dataset protocol has no dataset registration")
    if registration.get("dataset_id") != P2_E8_DATASET_ID:
        raise RuntimeError("P2-E8 dataset registration drifted")
    if registration.get("dataset_protocol_id") != P2_E8_DATASET_PROTOCOL_ID:
        raise RuntimeError("P2-E8 dataset protocol registration drifted")
    if dataset_protocol.get("protocol_id") != P2_E8_DATASET_PROTOCOL_ID:
        raise RuntimeError("P2-E8 command dataset protocol identity drifted")
    if observed_dataset.get("dataset_id") != P2_E8_DATASET_ID:
        raise RuntimeError("P2-E8 command dataset identity drifted")
    if observed_dataset.get("data_backend") != P2_E8_DATA_BACKEND:
        raise RuntimeError("P2-E8 command dataset backend drifted")
    if getattr(args, "dataset_id", None) != P2_E8_DATASET_ID:
        raise RuntimeError("P2-E8 requires the registered explicit --dataset-id")
    if getattr(args, "data_backend", None) != P2_E8_DATA_BACKEND:
        raise RuntimeError("P2-E8 requires --data-backend csv_directory")
    if list(getattr(args, "tasks", ())) != ["online_replay_monitoring"]:
        raise RuntimeError("P2-E8 supports only online_replay_monitoring")
    if getattr(args, "dynamic_protocol", None) is not None:
        raise RuntimeError("P2-E8 Ottawa uses the v6 replay runtime, not a dynamic event protocol")
    if getattr(args, "runtime_contract", None) != P2_E8_RUNTIME_CONTRACT:
        raise RuntimeError("P2-E8 requires the active v6 runtime contract")
    if formal.get("experiment_profile_id") != P2_E8_PROFILE_ID:
        raise RuntimeError("P2-E8 formal experiment profile drifted")
    if getattr(args, "experiment_profile_id", None) != P2_E8_PROFILE_ID:
        raise RuntimeError(f"P2-E8 requires --experiment-profile-id {P2_E8_PROFILE_ID}")
    for argument_name, key in (
        ("metadata_env", "metadata_environment"),
        ("signal_env", "signal_environment"),
        ("data_readiness_env", "readiness_environment"),
    ):
        if getattr(args, argument_name, None) != registration.get(key):
            raise RuntimeError(f"P2-E8 {argument_name} identity drifted")
    if getattr(args, "rotation", None) not in registration.get("rotations", ()):
        raise RuntimeError("P2-E8 rotation is not registered")
    if getattr(args, "seed", None) not in contract["current_schedule"]["seeds"]:
        raise RuntimeError("P2-E8 seed is not registered")
    for argument_name, key in (
        ("train_samples_per_bearing", "train_samples_per_bearing"),
        ("validation_samples_per_bearing", "validation_samples_per_bearing"),
        ("test_samples_per_bearing", "test_samples_per_bearing"),
    ):
        if getattr(args, argument_name, None) != registration.get(key):
            raise RuntimeError(f"P2-E8 {argument_name} drifted")
    args._cross_dataset_contract_cache = (str(path), dict(contract))
    return dict(contract)


def _environment_path(environment_name: str, label: str) -> Path:
    if not _SAFE_ENVIRONMENT_NAME.fullmatch(environment_name):
        raise RuntimeError(f"{label} must be a safe environment-variable name")
    value = os.environ.get(environment_name)
    if not value:
        raise RuntimeError(f"missing configured data environment variable: {environment_name}")
    path = Path(value).expanduser().resolve()
    if path.is_relative_to(Path(__file__).resolve().parents[1]):
        raise RuntimeError(f"P2-E8 private {label} must remain outside the repository")
    return path


def _validate_cross_dataset_inference(
    args: argparse.Namespace,
    contract: Mapping[str, Any] | None,
    inference: Mapping[str, Any],
) -> None:
    if contract is None or args.runtime != "openai":
        return
    analysis = contract.get("analysis_gate")
    if (
        not isinstance(analysis, Mapping)
        or analysis.get("accepted_only_cross_dataset_analyzer_implemented") is not True
    ):
        raise RuntimeError(
            "formal P2-E8 launch is blocked until the accepted-only paired analyzer is implemented"
        )
    activation = contract.get("activation_gate")
    current_blockers = (
        activation.get("current_blockers")
        if isinstance(activation, Mapping)
        else None
    )
    if not isinstance(current_blockers, list):
        raise RuntimeError("formal P2-E8 activation blockers are not registered")
    if current_blockers:
        raise RuntimeError(
            "formal P2-E8 launch is blocked: "
            + ", ".join(str(value) for value in current_blockers)
        )
    formal = contract["formal_execution"]
    expected_args = {
        "provider_label": formal["provider_label"],
        "runtime_contract": formal["runtime_contract"],
        "temperature": formal["temperature"],
        "max_output_tokens_per_turn": formal["max_output_tokens_per_turn"],
        "input_usd_per_million": formal["input_usd_per_million"],
        "output_usd_per_million": formal["output_usd_per_million"],
        "base_url_env": formal["base_url_environment"],
        "api_key_env": formal["api_key_environment"],
        "model_env": formal["model_environment"],
    }
    observed_args = {name: getattr(args, name, None) for name in expected_args}
    if observed_args != expected_args:
        raise RuntimeError("formal P2-E8 inference arguments drifted")
    expected_identity = {
        "model": formal["model_id"],
        "provider": formal["provider_label"],
        "inference_protocol": formal["inference_protocol"],
        "thinking_mode": formal["thinking_mode"],
    }
    if dict(inference) != expected_identity:
        raise RuntimeError("formal P2-E8 inference identity drifted")
    if os.environ.get(args.base_url_env) != formal["base_url"]:
        raise RuntimeError("formal P2-E8 base URL drifted")


def _open_data_port(
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
):
    contract = _cross_dataset_contract(args, protocol)
    seed = int(protocol["agent_visibility"]["sample_handle"]["seed"])
    if contract is None:
        return LocalPaderbornDataPort(args.metadata, args.signal, public_id_seed=seed)

    registration = contract["dataset_registration"]
    metadata_path = _environment_path(registration["metadata_environment"], "metadata")
    signal_root = _environment_path(registration["signal_environment"], "signal root")
    readiness_path = _environment_path(
        registration["readiness_environment"], "readiness report"
    )
    try:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("cannot read the P2-E8 CSV readiness report") from exc
    if not isinstance(readiness, Mapping):
        raise RuntimeError("P2-E8 CSV readiness report must be a mapping")

    dataset = protocol["dataset"]
    window = protocol["window_protocol"]
    value_columns = window.get("value_columns")
    source_columns = window.get("source_columns")
    if (
        not isinstance(value_columns, list)
        or not value_columns
        or any(not isinstance(value, str) or not value for value in value_columns)
        or len(set(value_columns)) != len(value_columns)
    ):
        raise RuntimeError("P2-E8 value columns are not registered")
    if (
        not isinstance(source_columns, list)
        or not source_columns
        or any(not isinstance(value, str) or not value for value in source_columns)
        or len(set(source_columns)) != len(source_columns)
        or any(value not in source_columns for value in value_columns)
    ):
        raise RuntimeError("P2-E8 source columns are not registered")
    segment_start_field = window.get("segment_start_field")
    activation = protocol.get("activation_gate")
    if not isinstance(activation, Mapping):
        raise RuntimeError("P2-E8 dataset activation gate is missing")
    expected_records = int(dataset["records"])
    required_readiness: dict[str, Any] = {
        "schema_version": activation["readiness_report_schema"],
        "dataset_id": dataset["dataset_id"],
        "records": expected_records,
        "value_columns": list(value_columns),
        "source_columns": list(source_columns),
        "sample_rate_hz": int(dataset["sample_rate_hz"]),
        "sample_length": int(dataset["sample_length"]),
        "channels": int(dataset["channels_per_record"]),
        "signals_validated": expected_records,
        "data_port_ready": True,
    }
    if segment_start_field is not None:
        required_readiness["segment_start_field"] = segment_start_field
    observed_readiness = {
        key: readiness.get(key) for key in required_readiness
    }
    if observed_readiness != required_readiness:
        raise RuntimeError("P2-E8 readiness report does not prove the complete CSV inventory")
    registered_values = activation.get("required_report_values")
    if not isinstance(registered_values, Mapping) or not registered_values:
        raise RuntimeError("P2-E8 activation report values are not registered")
    if {
        str(key): readiness.get(str(key)) for key in registered_values
    } != dict(registered_values):
        raise RuntimeError("P2-E8 readiness report differs from the activation contract")

    port = LocalCSVPhase1DataPort(
        metadata_path,
        signal_root,
        value_columns=value_columns,
        source_columns=source_columns,
        segment_start_field=segment_start_field,
        dataset_name=str(dataset["provider_name"]),
        default_max_points=int(window["max_returned_points"]),
        public_id_seed=seed,
    )
    try:
        public_rows = port.search_samples({}, expected_records + 1)
        if len(public_rows) != expected_records:
            raise RuntimeError("P2-E8 CSV metadata does not contain the complete inventory")
        expected_shape = [int(dataset["sample_length"]), int(dataset["channels_per_record"])]
        for row in public_rows:
            description = port.describe_sample(str(row["sample_id"]))
            if (
                description.get("dataset_id") != P2_E8_DATASET_ID
                or description.get("sample_length") != int(dataset["sample_length"])
                or description.get("channels") != int(dataset["channels_per_record"])
                or description.get("signal_available") is not True
                or description.get("stored_shape") != expected_shape
            ):
                raise RuntimeError("P2-E8 CSV metadata or signal shape drifted")
    except Exception:
        port.close()
        raise
    return port


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"{path} must contain JSON objects")
                rows.append(value)
    return rows


def _factory(args: argparse.Namespace):
    agent_class = (
        ReactiveSequentialAgent if args.arm == "reactive" else GraphDecisionAgent
    )

    def build(client, model: str):
        if args.arm == "graph":
            return agent_class(
                client,
                model=model,
                policy_config=GraphPolicyConfig.for_profile(
                    args.graph_profile,
                    runtime_contract=args.runtime_contract,
                ),
            )
        return agent_class(client, model=model)

    if args.runtime == "mock":
        return lambda model_id: build(
            DeterministicMockLLM(
                diagnosis_model_id=model_id,
                inject_recoverable_error=args.inject_recoverable_error,
            ),
            "mock-phase1",
        )
    if args.runtime in {"codex", "claude"}:
        model = os.environ.get(args.model_env)
        if not model:
            raise RuntimeError(f"missing configured LLM environment variable: {args.model_env}")
        return lambda model_id: build(
            LocalCLIJSONLLM(args.runtime, timeout=args.local_cli_timeout),
            str(model),
        )
    names = (args.base_url_env, args.api_key_env, args.model_env)
    values = {name: os.environ.get(name) for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError("missing configured LLM environment variables: " + ", ".join(missing))
    return lambda model_id: build(
        OpenAICompatibleLLM(
            base_url=str(values[args.base_url_env]),
            api_key=str(values[args.api_key_env]),
            temperature=args.temperature,
            seed=args.seed,
            max_output_tokens=args.max_output_tokens_per_turn,
        ),
        str(values[args.model_env]),
    )


def _runtime_identity(
    args: argparse.Namespace,
) -> tuple[dict[str, str], ResumeProfile, ModelProfile | None]:
    if args.runtime == "mock":
        identity = {
            "model": "deterministic-mock-llm",
            "provider": "benchmark-local",
            "inference_protocol": "mock-tools",
            "thinking_mode": "not_applicable",
        }
        return (
            identity,
            ResumeProfile(
                runtime_contract=args.runtime_contract,
                model=identity["model"],
                provider=identity["provider"],
                inference_protocol=identity["inference_protocol"],
            ),
            None,
        )
    model = os.environ.get(args.model_env)
    if not model:
        raise RuntimeError(
            f"missing configured LLM environment variable: {args.model_env}"
        )
    if args.runtime == "openai" and (
        args.input_usd_per_million is None
        or args.output_usd_per_million is None
    ):
        raise RuntimeError(
            "formal LLM runs require explicit input/output USD per million tokens"
        )
    identity = {
        "model": str(model),
        "provider": args.provider_label,
        "inference_protocol": RUNTIME_PROTOCOLS[args.runtime],
        "thinking_mode": (
            "not_requested" if args.runtime == "openai" else "provider_managed"
        ),
    }
    resume_profile = ResumeProfile(
        runtime_contract=args.runtime_contract,
        model=identity["model"],
        provider=identity["provider"],
        inference_protocol=identity["inference_protocol"],
    )
    return (
        identity,
        resume_profile,
        ModelProfile(
            args.provider_label,
            str(model),
            RUNTIME_PROTOCOLS[args.runtime],
            args.input_usd_per_million,
            args.output_usd_per_million,
        ),
    )


def _public_bundle_evaluation(
    evaluation: EvaluatorResult,
    model_profile: ModelProfile | None,
) -> EvaluatorResult:
    rollout_metrics = dict(evaluation.rollout_metrics)
    rollout_metrics["estimated_model_cost_usd"] = (
        0.0
        if model_profile is None
        else model_profile.estimate_cost(
            float(rollout_metrics.get("input_tokens", 0.0)),
            float(rollout_metrics.get("output_tokens", 0.0)),
        )
    )
    return EvaluatorResult(
        task_spec_id=evaluation.task_spec_id,
        task_type=evaluation.task_type,
        episode_id=evaluation.episode_id,
        task_metrics={
            key: value
            for key, value in evaluation.task_metrics.items()
            if key != "private_target"
        },
        rollout_metrics=rollout_metrics,
        terminal_status=evaluation.terminal_status,
        evaluator_id=evaluation.evaluator_id,
        evaluator_method=evaluation.evaluator_method,
    )


def _bundle_views(output: Path) -> list[RunBundleView]:
    if not output.exists():
        return []
    return [read_run_bundle(path.parent) for path in sorted(output.rglob("run.json"))]


def _attempt_index(bundle: RunBundleView) -> int:
    value = bundle.run["metadata"].get("attempt_index", 0)
    if type(value) is not int or value < 0:
        raise ValueError(f"invalid attempt_index in {bundle.root}")
    return value


def _state_rows(
    output: Path,
    *,
    graph_profile: str = "full",
    runtime_contract: str = "phase1_opaque_sample_vibration_feature_schema_v6",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for public_row in read_cohort_rollout_views(output):
        trajectory = public_row["trajectory"]
        states = [
            str(step["decision_state"])
            for step in trajectory["steps"]
            if isinstance(step.get("decision_state"), str)
            and step["decision_state"].strip()
        ]
        transitions = list(zip(states, states[1:]))
        valid = transition_validity_from_states(
            states,
            graph_profile=graph_profile,
            runtime_contract=runtime_contract,
        )
        rows.append(
            {
                "rotation": public_row["rotation"],
                "sample_id": public_row["sample_id"],
                "task_id": public_row["task_id"],
                "episode_key": [
                    public_row["rotation"],
                    public_row["sample_id"],
                    public_row["task_id"],
                ],
                "terminal_status": trajectory["terminal_status"],
                "states": states,
                "transitions": transitions,
                "transition_validity": valid,
                "recover_state_count": states.count("Recover"),
            }
        )
    return rows


def _episode_bundle_directory(
    output: Path,
    episode_key: tuple[str, str, str],
    attempt_index: int,
) -> Path:
    return episode_attempt_directory(output, episode_key, attempt_index)


def _episode_sink(
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
    profile: ResumeProfile,
    inference: Mapping[str, str],
    resume_plan: ProviderResumePlan,
    model_profile: ModelProfile | None = None,
    cohort_resume_identity: Mapping[str, Any] | None = None,
):
    def write_episode(
        episode_key,
        task,
        rollout,
        evaluation,
        artifacts,
        episode_metadata,
    ) -> None:
        key = tuple(str(value) for value in episode_key)
        attempt = 0
        if key == resume_plan.retry_episode_key:
            if resume_plan.retry_bundle_dir is None:
                raise RuntimeError("resume retry is missing its previous run bundle")
            attempt = _attempt_index(read_run_bundle(resume_plan.retry_bundle_dir)) + 1
        attempt_id = (
            f"{args.arm}-{key[0]}-{key[2]}-{key[1]}-attempt-{attempt:03d}"
        )
        episode = EpisodeSpec(
            episode_id=rollout.episode_id,
            task=task,
            scope=DataAccessScope(),
            sample_handle=key[1],
        )
        write_episode_bundle(
            _episode_bundle_directory(args.output, key, attempt),
            attempt_id=attempt_id,
            episode=episode,
            rollout=rollout,
            evaluation=_public_bundle_evaluation(evaluation, model_profile),
            artifacts=artifacts,
            run_metadata={
                **dict(episode_metadata),
                **dict(inference),
                **_p2_experiment_identity(args),
                "dataset_protocol": protocol["schema_version"],
                "benchmark_protocol_version": PROTOCOL_VERSION,
                "dataset_protocol_id": protocol.get(
                    "protocol_id", protocol["schema_version"]
                ),
                "dataset_protocol_schema": protocol["schema_version"],
                "window_contract": protocol.get("window_protocol", {}).get(
                    "contract", "not_recorded"
                ),
                "runtime_contract": profile.runtime_contract,
                "seed": args.seed,
                "attempt_index": attempt,
                "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
                "arm": args.arm,
                "runtime": args.runtime,
                "graph_policy_profile": _graph_policy_profile(args),
                **(
                    {
                        **dict(cohort_resume_identity),
                        "cohort_resume_identity_contract": (
                            COHORT_RESUME_IDENTITY_CONTRACT
                        ),
                        "cohort_resume_identity": dict(cohort_resume_identity),
                        "evaluator_assignment_contract": (
                            EVALUATOR_ASSIGNMENT_CONTRACT
                        ),
                    }
                    if cohort_resume_identity is not None
                    else {}
                ),
            },
        )

    return write_episode


def _evaluation_key(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return str(row["rotation"]), str(row["sample_id"]), str(row["task_id"])


def _graph_policy_profile(args: argparse.Namespace) -> str:
    if args.arm == "reactive":
        if args.graph_profile != "full":
            raise ValueError("graph ablation profiles apply only to --arm graph")
        return "reactive"
    return str(args.graph_profile)


def _p2_experiment_identity(args: argparse.Namespace) -> dict[str, str]:
    """Return the versioned causal-control identity saved in every P2 bundle."""

    return {
        "p2_experiment_id": P2_EXPERIMENT_ID,
        "matched_control_id": P2_MATCHED_CONTROL_ID,
        "agent_control_id": (
            P2_MATCHED_CONTROL_ID
            if args.arm == "reactive"
            else P2_GRAPH_CONTROL_ID
        ),
        "agent_implementation_id": (
            P2_REACTIVE_IMPLEMENTATION_ID
            if args.arm == "reactive"
            else P2_GRAPH_IMPLEMENTATION_ID
        ),
    }


def _active_cohort_contract(
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
    inference: Mapping[str, Any],
    *,
    core_budget: Budget,
    monitoring_budget: Budget,
    test_samples_per_bearing: int,
    matches_formal_sampling: bool,
    model_profile: ModelProfile | None,
) -> tuple[dict[str, Any], dict[str, Any], ResumeProfile]:
    """Build the active-v0.2 index profile and immutable resume identity."""

    cross_dataset = _cross_dataset_contract(args, protocol)
    monitoring = args.tasks == ["online_replay_monitoring"]
    registered_evidence_class = (
        "formal"
        if args.runtime == "openai" and matches_formal_sampling
        else "mechanics"
        if args.runtime == "mock"
        else "pilot"
    )
    result_role = "confirmatory" if registered_evidence_class == "formal" else "none"
    benchmark_control_source = _benchmark_control_source(
        args,
        required=(
            cross_dataset is None
            and registered_evidence_class == "formal"
            and args.arm == "graph"
        ),
    )
    scope = "replay" if monitoring else "core"
    budget = monitoring_budget if monitoring else core_budget
    sampling = protocol["episode_sampling"]
    test_sample_selection = (
        sampling["agent_selection"]
        if test_samples_per_bearing == 1
        else sampling["numerical_selection"]
    )
    replay_missing_score_policy_id = (
        require_formal_replay_metric_lock(protocol)
        if monitoring and registered_evidence_class == "formal"
        else None
    )
    data_provider_contract = registered_data_provider_contract(protocol)
    dataset_protocol_id = protocol.get("protocol_id", protocol["schema_version"])
    window_contract = protocol["window_protocol"]["contract"]
    experiment_profile_id = (
        str(cross_dataset["formal_execution"]["experiment_profile_id"])
        if cross_dataset is not None
        else f"p2-e1-{args.arm}-{scope}-active-v0.2"
    )
    requested_profile = getattr(args, "experiment_profile_id", None)
    if requested_profile is not None and requested_profile != experiment_profile_id:
        raise ValueError("experiment profile identity drifted")
    agent_id = (
        GraphDecisionAgent.agent_id
        if args.arm == "graph"
        else ReactiveSequentialAgent.agent_id
    )
    model_view = None if model_profile is None else model_profile.to_dict()
    inference_route = protocol.get("inference", {}).get("inference_route")
    temperature = args.temperature if args.runtime == "openai" else None
    max_output_tokens = (
        args.max_output_tokens_per_turn if args.runtime == "openai" else None
    )
    identity: dict[str, Any] = {
        "cohort_resume_identity_contract": COHORT_RESUME_IDENTITY_CONTRACT,
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "dataset_protocol_id": dataset_protocol_id,
        "dataset_protocol_schema": protocol["schema_version"],
        "window_contract": window_contract,
        "runtime_contract": args.runtime_contract,
        "model": inference["model"],
        "provider": inference["provider"],
        "inference_protocol": inference["inference_protocol"],
        "thinking_mode": inference["thinking_mode"],
        "seed": args.seed,
        "rotation": args.rotation,
        "tasks": sorted(args.tasks),
        "agent": args.arm,
        "agent_id": agent_id,
        "registered_evidence_class": registered_evidence_class,
        "result_role": result_role,
        "experiment_profile_id": experiment_profile_id,
        "budget_profile_id": None,
        "catalog_disclosure": "progressive_catalog",
        "data_backend": (
            P2_E8_DATA_BACKEND if cross_dataset is not None else "local_hdf5"
        ),
        "data_provider_contract": data_provider_contract,
        "evaluator_assignment_contract": EVALUATOR_ASSIGNMENT_CONTRACT,
        "replay_missing_score_policy_id": replay_missing_score_policy_id,
        "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
        "train_samples_per_bearing": args.train_samples_per_bearing,
        "validation_samples_per_bearing": args.validation_samples_per_bearing,
        "test_samples_per_bearing": test_samples_per_bearing,
        "test_sample_selection": test_sample_selection,
        "max_test_bearings": args.max_test_bearings,
        "core_budget": core_budget.to_protocol_dict(),
        "monitoring_budget": monitoring_budget.to_protocol_dict(),
        "temperature": temperature,
        "max_output_tokens_per_turn": max_output_tokens,
        "input_usd_per_million": (
            None if model_view is None else model_view["input_usd_per_million"]
        ),
        "output_usd_per_million": (
            None if model_view is None else model_view["output_usd_per_million"]
        ),
    }
    if inference_route is not None:
        identity["inference_route"] = inference_route
    if benchmark_control_source is not None:
        identity["benchmark_control_source"] = dict(benchmark_control_source)
    if cross_dataset is not None:
        identity.update(
            {
                "cross_dataset_protocol_schema": cross_dataset["schema_version"],
                "cross_dataset_protocol_id": cross_dataset["protocol_id"],
                "data_binding": {
                    "metadata_environment": getattr(args, "metadata_env"),
                    "signal_environment": getattr(args, "signal_env"),
                    "readiness_environment": getattr(args, "data_readiness_env"),
                },
                "agent_profile_id": _dynamic_agent_profile(args),
            }
        )
    profile: dict[str, Any] = {
        "protocol": protocol["schema_version"],
        "benchmark_protocol_version": PROTOCOL_VERSION,
        "dataset_protocol_id": dataset_protocol_id,
        "dataset_protocol_schema": protocol["schema_version"],
        "window_contract": window_contract,
        "rotation": args.rotation,
        "agent": args.arm,
        "agent_id": agent_id,
        "runtime": args.runtime,
        "model": inference["model"],
        "provider": inference["provider"],
        "inference_protocol": inference["inference_protocol"],
        "thinking_mode": inference["thinking_mode"],
        "tasks": list(args.tasks),
        "temperature": temperature,
        "max_output_tokens_per_turn": max_output_tokens,
        "runtime_contract": args.runtime_contract,
        "data_backend": (
            P2_E8_DATA_BACKEND if cross_dataset is not None else "local_hdf5"
        ),
        "data_provider_contract": data_provider_contract,
        "evaluator_assignment_contract": EVALUATOR_ASSIGNMENT_CONTRACT,
        "replay_missing_score_policy_id": replay_missing_score_policy_id,
        "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
        "cohort_resume_identity_contract": COHORT_RESUME_IDENTITY_CONTRACT,
        "dataset_status": protocol.get("status"),
        "experiment_profile_id": experiment_profile_id,
        "budget_profile": None,
        "budget_profile_id": None,
        "catalog_disclosure": "progressive_catalog",
        "sample_handle": protocol["agent_visibility"]["sample_handle"],
        "seed": args.seed,
        "model_profile": model_view,
        "model_cost_basis": "per_token_usd" if model_view is not None else None,
        "train_samples_per_bearing": args.train_samples_per_bearing,
        "validation_samples_per_bearing": args.validation_samples_per_bearing,
        "test_samples_per_bearing": test_samples_per_bearing,
        "test_sample_selection": test_sample_selection,
        "max_test_bearings": args.max_test_bearings,
        "window_protocol": protocol["window_protocol"],
        "budget": budget.to_dict(),
        "budget_protocol": budget.to_protocol_dict(),
        "registered_evidence_class": registered_evidence_class,
        "result_role": result_role,
        "arm": args.arm,
        "graph_policy_profile": _graph_policy_profile(args),
        **_p2_experiment_identity(args),
    }
    if inference_route is not None:
        profile["inference_route"] = inference_route
    if benchmark_control_source is not None:
        profile["benchmark_control_source"] = dict(benchmark_control_source)
    if cross_dataset is not None:
        profile.update(
            {
                "cross_dataset_protocol_schema": cross_dataset["schema_version"],
                "cross_dataset_protocol_id": cross_dataset["protocol_id"],
                "data_binding": dict(identity["data_binding"]),
                "agent_profile_id": _dynamic_agent_profile(args),
            }
        )
    resume_profile = ResumeProfile(
        benchmark_protocol_version=PROTOCOL_VERSION,
        dataset_protocol_id=str(dataset_protocol_id),
        dataset_protocol_schema=str(protocol["schema_version"]),
        window_contract=str(window_contract),
        runtime_contract=args.runtime_contract,
        model=str(inference["model"]),
        provider=str(inference["provider"]),
        inference_protocol=str(inference["inference_protocol"]),
        cohort_identity=identity,
    )
    return profile, identity, resume_profile


def _validate_saved_experiment_identity(
    output: Path,
    args: argparse.Namespace,
) -> None:
    """Reject legacy PHMskills-derived or mixed P2 leaves on resume."""

    expected = _p2_experiment_identity(args)
    run_paths = tuple(sorted(output.rglob("run.json"))) if output.exists() else ()
    if not run_paths:
        return
    for run_path in run_paths:
        metadata = read_run_bundle(run_path.parent).run["metadata"]
        for name, value in expected.items():
            if metadata.get(name) != value:
                raise ValueError(
                    "resume P2 experiment/control identity mismatch for "
                    f"{name} at {run_path.parent}; expected {value!r}, "
                    f"observed {metadata.get(name)!r}. Use a new output directory."
                )


def _validate_saved_graph_profile(output: Path, expected: str) -> None:
    observed = {
        read_run_bundle(run_path.parent).run["metadata"].get(
            "graph_policy_profile"
        )
        for run_path in output.rglob("run.json")
    }
    if observed and observed != {expected}:
        raise ValueError(
            "resume graph policy profile mismatch: "
            f"expected {expected}, observed {sorted(str(item) for item in observed)}"
        )


def _completed_evaluations(
    output: Path,
    plan: ProviderResumePlan,
) -> list[dict[str, Any]]:
    path = output / "cohort_index.json"
    if not path.exists():
        if plan.completed_episode_keys:
            raise ValueError("completed bundles exist without a canonical cohort index")
        return []
    document = validate_cohort_index(path)
    rows = [row for row in document["records"] if _evaluation_key(row) in plan.completed_episode_keys]
    observed = {_evaluation_key(row) for row in rows}
    if observed != set(plan.completed_episode_keys) or len(observed) != len(rows):
        raise ValueError("cohort index records disagree with completed bundles")
    return rows


def _completed_dynamic_evaluations(
    output: Path,
    plan: ProviderResumePlan,
) -> list[dict[str, Any]]:
    """Keep one isolated dynamic unit's existing auxiliary resume view."""

    path = output / "evaluation.jsonl"
    if not path.exists():
        if plan.completed_episode_keys:
            raise ValueError("completed dynamic bundle lacks its evaluation row")
        return []
    rows = [
        row
        for row in _read_jsonl(path)
        if _evaluation_key(row) in plan.completed_episode_keys
    ]
    observed = {_evaluation_key(row) for row in rows}
    if observed != set(plan.completed_episode_keys) or len(observed) != len(rows):
        raise ValueError("dynamic evaluation rows disagree with completed bundles")
    return rows


def _resume_context(
    args: argparse.Namespace,
    profile: ResumeProfile,
) -> tuple[ProviderResumePlan, list[dict[str, Any]]]:
    if args.resume_provider_partial:
        if (args.output / "rollout.jsonl").exists() or (
            args.output / "provider_failures.jsonl"
        ).exists():
            raise ValueError(
                "legacy root rollout/archive cannot be resumed; use a new output directory"
            )
        _validate_saved_experiment_identity(args.output, args)
        _validate_saved_graph_profile(args.output, _graph_policy_profile(args))
        plan = load_provider_partial(args.output, expected_profile=profile)
        return plan, _completed_evaluations(args.output, plan)
    if _bundle_views(args.output) or any(
        (args.output / name).exists()
        for name in (
            "rollout.jsonl",
            "evaluation.jsonl",
            "cohort_index.json",
            "state_evaluation.jsonl",
            "summary.json",
            "run_manifest.json",
            "provider_failures.jsonl",
        )
    ):
        raise ValueError("output already contains a run; use --resume-provider-partial")
    return ProviderResumePlan(frozenset()), []


def transition_validity_from_states(
    states: list[str],
    *,
    graph_profile: str = "full",
    runtime_contract: str = "phase1_opaque_sample_vibration_feature_schema_v6",
) -> float:
    config = GraphPolicyConfig.for_profile(
        graph_profile,
        runtime_contract=runtime_contract,
    )
    return profile_transition_validity(states, config)


def _load_dynamic_protocol(path: Path) -> dict[str, Any]:
    def merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
        merged = dict(left)
        for key, item in right.items():
            if isinstance(item, Mapping) and isinstance(merged.get(key), Mapping):
                merged[key] = merge(merged[key], item)
            else:
                merged[key] = item
        return merged

    def load(current: Path, stack: tuple[Path, ...]) -> dict[str, Any]:
        resolved = current.resolve()
        if resolved in stack:
            raise ValueError("dynamic protocol extension cycle detected")
        value = yaml.safe_load(current.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("dynamic protocol must be a YAML mapping")
        value = dict(value)
        base_name = value.pop("extends_protocol", None)
        if base_name is None:
            return value
        if not isinstance(base_name, str) or Path(base_name).name != base_name:
            raise ValueError("dynamic protocol extension must be one sibling filename")
        return merge(load(current.parent / base_name, (*stack, resolved)), value)

    protocol = load(path, ())
    if protocol.get("schema_version") not in {
        "graph_dynamic_ablation_protocol_v2",
        "graph_dynamic_ablation_protocol_v3",
    }:
        raise ValueError("unsupported graph dynamic protocol")
    return protocol


def _validate_dynamic_arguments(
    args: argparse.Namespace,
    dynamic_protocol: Mapping[str, Any] | None,
) -> None:
    if args.runtime_contract not in {
        PHASE1_BASE_RUNTIME_CONTRACT,
        *GRAPH_DYNAMIC_RUNTIME_CONTRACTS,
    }:
        raise ValueError(f"unsupported runtime contract: {args.runtime_contract}")
    dynamic = args.runtime_contract in GRAPH_DYNAMIC_RUNTIME_CONTRACTS
    supplied = any(
        value is not None
        for value in (args.dynamic_protocol, args.public_sequence_id, args.horizon)
    )
    if dynamic != (dynamic_protocol is not None):
        raise ValueError(
            "a registered graph dynamic runtime requires --dynamic-protocol"
        )
    if not dynamic:
        if supplied:
            raise ValueError("dynamic sequence flags require the dynamic runtime contract")
        return
    if args.tasks != ["online_replay_monitoring"]:
        raise ValueError("the dynamic runtime supports only online_replay_monitoring")
    if args.public_sequence_id is None or args.horizon is None:
        raise ValueError("dynamic runtime requires --public-sequence-id and --horizon")
    assert dynamic_protocol is not None
    if (
        dynamic_protocol["runtime_and_provider_profile"]["effective_runtime_contract"]
        != args.runtime_contract
    ):
        raise ValueError("dynamic protocol/runtime identity mismatch")
    if args.seed not in {int(value) for value in dynamic_protocol["experiment_design"]["seeds"]}:
        raise ValueError("seed is not registered by the dynamic protocol")
    if args.rotation != str(dynamic_protocol["dataset"]["rotation"]):
        raise ValueError("rotation is not registered by the dynamic protocol")
    expected_sequence_ids = {
        f"sequence-{index:04d}"
        for index in range(
            1, int(dynamic_protocol["dataset"]["held_out_bearings"]) + 1
        )
    }
    if args.public_sequence_id not in expected_sequence_ids:
        raise ValueError("public sequence ID is not registered by the dynamic protocol")
    if args.horizon not in {
        int(value)
        for value in dynamic_protocol["sequence_construction"]["horizons"]
    }:
        raise ValueError("horizon is not registered by the dynamic protocol")


def _dynamic_agent_profile(args: argparse.Namespace) -> str:
    if args.arm == "reactive":
        return "reactive_sequential_generic_v2"
    return f"graph_dynamic_{args.graph_profile}_generic_v2"


def _validate_saved_dynamic_unit(args: argparse.Namespace) -> None:
    expected = {
        **_p2_experiment_identity(args),
        "runtime_contract": args.runtime_contract,
        "seed": args.seed,
        "rotation": args.rotation,
        "sample_id": args.public_sequence_id,
        "task_id": "online_replay_monitoring",
        "horizon": args.horizon,
        "graph_policy_profile": _graph_policy_profile(args),
        "agent_profile_id": _dynamic_agent_profile(args),
    }
    for run_path in args.output.rglob("run.json") if args.output.exists() else ():
        metadata = read_run_bundle(run_path.parent).run["metadata"]
        for name, value in expected.items():
            if metadata.get(name) != value:
                raise ValueError(
                    f"resume dynamic unit mismatch for {name}: "
                    f"expected {value!r}, observed {metadata.get(name)!r}"
                )


def _dynamic_resume_context(
    args: argparse.Namespace,
    profile: ResumeProfile,
) -> tuple[ProviderResumePlan, list[dict[str, Any]]]:
    _validate_saved_dynamic_unit(args)
    has_bundles = args.output.exists() and any(args.output.rglob("run.json"))
    has_auxiliary = args.output.exists() and any(
        (args.output / name).exists()
        for name in ("evaluation.jsonl", "summary.json", "run_manifest.json")
    )
    if not args.resume_provider_partial:
        if has_bundles or has_auxiliary:
            raise ValueError("dynamic output already contains a run; use resume")
        return ProviderResumePlan(frozenset()), []
    plan = load_provider_partial(args.output, expected_profile=profile)
    return plan, _completed_dynamic_evaluations(args.output, plan)


def _write_dynamic_bundle(
    args: argparse.Namespace,
    dataset_protocol: Mapping[str, Any],
    profile: ResumeProfile,
    inference: Mapping[str, str],
    resume_plan: ProviderResumePlan,
    result: Any,
    model_profile: ModelProfile | None,
    selected_model_id: str,
    started_at: str,
    ended_at: str,
) -> Path:
    episode_key = (
        str(args.rotation),
        str(args.public_sequence_id),
        "online_replay_monitoring",
    )
    attempt = 0
    if resume_plan.retry_episode_key == episode_key:
        if resume_plan.retry_bundle_dir is None:
            raise RuntimeError("dynamic retry is missing its previous bundle")
        attempt = _attempt_index(read_run_bundle(resume_plan.retry_bundle_dir)) + 1
    attempt_root = args.output / f"attempt_{attempt:03d}"
    write_run_bundle(
        attempt_root,
        run_id=(
            f"{_dynamic_agent_profile(args)}-{args.seed}-{args.rotation}-"
            f"h{args.horizon}-{args.public_sequence_id}-attempt-{attempt:03d}"
        ),
        task=result.task_spec,
        rollout=result.trajectory,
        evaluation=_public_bundle_evaluation(result.evaluation, model_profile),
        artifacts=result.artifact_descriptors,
        run_metadata={
            **dict(inference),
            **_p2_experiment_identity(args),
            "dataset_protocol": dataset_protocol["schema_version"],
            "runtime_contract": profile.runtime_contract,
            "seed": args.seed,
            "rotation": args.rotation,
            "horizon": args.horizon,
            "public_sequence_id": args.public_sequence_id,
            "sample_id": args.public_sequence_id,
            "task_id": "online_replay_monitoring",
            "episode_key": list(episode_key),
            "attempt_index": attempt,
            "arm": args.arm,
            "runtime": args.runtime,
            "graph_policy_profile": _graph_policy_profile(args),
            "agent_profile_id": _dynamic_agent_profile(args),
            "selected_diagnosis_model_id": selected_model_id,
            "started_at": started_at,
            "ended_at": ended_at,
            "evidence_class": (
                "mechanics_only_not_performance_evidence"
                if args.runtime == "mock"
                else "real_data_provider_failure_not_performance_evidence"
                if result.trajectory.terminal_failure_kind == "provider_error"
                else "real_data_formal_candidate"
            ),
        },
    )
    return attempt_root


async def _run_dynamic(
    args: argparse.Namespace,
    dataset_protocol: Mapping[str, Any],
    dynamic_protocol: Mapping[str, Any],
) -> None:
    inference, resume_profile, model_profile = _runtime_identity(args)
    resume_plan, previous_records = _dynamic_resume_context(args, resume_profile)
    episode_key = (
        str(args.rotation),
        str(args.public_sequence_id),
        "online_replay_monitoring",
    )
    if episode_key in resume_plan.completed_episode_keys:
        print(json.dumps(aggregate_results(previous_records), indent=2, sort_keys=True))
        return
    args.output.mkdir(parents=True, exist_ok=True)
    with LocalPaderbornDataPort(
        args.metadata,
        args.signal,
        public_id_seed=int(
            dataset_protocol["agent_visibility"]["sample_handle"]["seed"]
        ),
    ) as data:
        sequences = build_master_sequences(
            data,
            dataset_protocol,
            dynamic_protocol,
            args.rotation,
        )
        sequence = sequences[str(args.public_sequence_id)]
        models, selected_model_id = fit_dynamic_model_pool(
            data,
            dataset_protocol,
            args.rotation,
            train_samples_per_bearing=args.train_samples_per_bearing,
            validation_samples_per_bearing=args.validation_samples_per_bearing,
        )
        policy = _factory(args)(selected_model_id)
        started_at = datetime.now(timezone.utc).isoformat()
        result = await run_dynamic_episode(
            data,
            models,
            policy,
            dataset_protocol,
            dynamic_protocol,
            sequence,
            seed=args.seed,
            rotation=args.rotation,
            horizon=args.horizon,
            strip_historical_decision_state=(
                args.arm == "graph"
                and args.graph_profile == "no_persistent_graph_state"
            ),
        )
        ended_at = datetime.now(timezone.utc).isoformat()
    _write_dynamic_bundle(
        args,
        dataset_protocol,
        resume_profile,
        inference,
        resume_plan,
        result,
        model_profile,
        selected_model_id,
        started_at,
        ended_at,
    )
    record = {
        "rotation": args.rotation,
        "bearing_id": args.public_sequence_id,
        "sample_id": args.public_sequence_id,
        "sample_ids": list(result.task.public_context["replay_sample_ids"]),
        "task_id": "online_replay_monitoring",
        "private_target": dict(result.task.private_target),
        "submission": result.trajectory.submission,
        "evaluation": result.evaluation.to_dict(),
    }
    records = previous_records + [record]
    if model_profile is not None:
        attach_model_cost(records[-1:], model_profile)
    _write_jsonl(args.output / "evaluation.jsonl", records)
    summary = aggregate_results(records)
    if args.arm == "graph":
        state_rows = _state_rows(
            args.output,
            graph_profile=args.graph_profile,
            runtime_contract=args.runtime_contract,
        )
        summary["graph"] = {
            "transition_validity": sum(
                row["transition_validity"] for row in state_rows
            )
            / len(state_rows),
            "recover_state_count": sum(
                row["recover_state_count"] for row in state_rows
            ),
            "state_coverage": sorted(
                {state for row in state_rows for state in row["states"]}
            ),
        }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest = {
        "study": str(dynamic_protocol["schema_version"]).replace("_protocol", ""),
        **_p2_experiment_identity(args),
        "dynamic_protocol": dynamic_protocol["schema_version"],
        "dataset_protocol": dataset_protocol["schema_version"],
        "runtime_contract": args.runtime_contract,
        "runtime": args.runtime,
        "provider_profile_id": (
            dynamic_protocol["runtime_and_provider_profile"]["formal_provider_profile_id"]
            if args.runtime == "openai"
            else "benchmark_local_mock"
        ),
        "provider": inference["provider"],
        "model": inference["model"],
        "inference_protocol": inference["inference_protocol"],
        "thinking_mode": inference["thinking_mode"],
        "temperature": args.temperature if args.runtime == "openai" else None,
        "max_output_tokens_per_turn": (
            args.max_output_tokens_per_turn if args.runtime == "openai" else None
        ),
        "input_usd_per_million": (
            args.input_usd_per_million if args.runtime == "openai" else None
        ),
        "output_usd_per_million": (
            args.output_usd_per_million if args.runtime == "openai" else None
        ),
        "arm": args.arm,
        "graph_policy_profile": _graph_policy_profile(args),
        "agent_profile_id": _dynamic_agent_profile(args),
        "seed": args.seed,
        "rotation": args.rotation,
        "public_sequence_id": args.public_sequence_id,
        "horizon": args.horizon,
        "budget": result.task_spec.budget.to_protocol_dict(),
        "canonical_episode_count": len(list(args.output.rglob("run.json"))),
        "evidence_class": (
            "real_data_provider_failure_not_performance_evidence"
            if result.trajectory.terminal_status == "provider_error"
            else "mechanics_only_not_performance_evidence"
            if args.runtime == "mock"
            else "real_data_formal_candidate"
        ),
    }
    (args.output / "run_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if result.trajectory.terminal_status == "provider_error":
        raise SystemExit("provider failure stopped this dynamic cohort unit")


async def _run(args: argparse.Namespace) -> None:
    protocol = load_dataset_protocol(args.protocol)
    cross_dataset = _cross_dataset_contract(args, protocol)
    dynamic_protocol = (
        None
        if args.dynamic_protocol is None
        else _load_dynamic_protocol(args.dynamic_protocol)
    )
    _validate_dynamic_arguments(args, dynamic_protocol)
    if cross_dataset is not None and dynamic_protocol is not None:
        raise RuntimeError("P2-E8 cross-dataset replay cannot use a dynamic event protocol")
    if dynamic_protocol is not None:
        await _run_dynamic(args, protocol, dynamic_protocol)
        return
    _graph_policy_profile(args)
    inference, _base_resume_profile, model_profile = _runtime_identity(args)
    _validate_cross_dataset_inference(args, cross_dataset, inference)
    test_samples_per_bearing = args.test_samples_per_bearing
    if test_samples_per_bearing is None:
        test_samples_per_bearing = (
            protocol["episode_sampling"]["monitoring_windows_per_episode"]
            if args.tasks == ["online_replay_monitoring"]
            else protocol["episode_sampling"]["agent_test_samples_per_bearing"]
        )
    core_budget = Budget()
    monitoring_budget = Budget(
        max_tool_calls=72,
        max_window_reads=test_samples_per_bearing,
        max_operator_calls=50,
        max_model_calls=test_samples_per_bearing,
        max_llm_turns=72,
    )
    frozen = protocol["episode_sampling"]
    expected_test_samples = (
        frozen["monitoring_windows_per_episode"]
        if args.tasks == ["online_replay_monitoring"]
        else frozen["agent_test_samples_per_bearing"]
    )
    matches_formal_sampling = (
        args.train_samples_per_bearing == frozen["train_samples_per_bearing"]
        and args.validation_samples_per_bearing
        == frozen["healthy_validation_samples_per_bearing"]
        and test_samples_per_bearing == expected_test_samples
        and args.max_test_bearings is None
    )
    manifest, cohort_identity, resume_profile = _active_cohort_contract(
        args,
        protocol,
        inference,
        core_budget=core_budget,
        monitoring_budget=monitoring_budget,
        test_samples_per_bearing=test_samples_per_bearing,
        matches_formal_sampling=matches_formal_sampling,
        model_profile=model_profile,
    )
    resume_plan, previous_records = _resume_context(args, resume_profile)
    args.output.mkdir(parents=True, exist_ok=True)
    with _open_data_port(args, protocol) as data:
        private_assignments = build_evaluator_assignments(
            data,
            protocol,
            args.rotation,
            tasks=args.tasks,
            test_samples_per_bearing=test_samples_per_bearing,
            max_test_bearings=args.max_test_bearings,
        )
        validate_evaluator_records(
            previous_records,
            private_assignments,
            require_complete=False,
        )
        _trajectories, records, run_info = await run_rotation(
            data,
            protocol,
            args.rotation,
            _factory(args),
            tasks=args.tasks,
            train_samples_per_bearing=args.train_samples_per_bearing,
            validation_samples_per_bearing=args.validation_samples_per_bearing,
            test_samples_per_bearing=test_samples_per_bearing,
            max_test_bearings=args.max_test_bearings,
            budget=core_budget,
            monitoring_budget=monitoring_budget,
            completed_episode_keys=set(resume_plan.completed_episode_keys),
            runtime_contract=args.runtime_contract,
            episode_sink=_episode_sink(
                args,
                protocol,
                resume_profile,
                inference,
                resume_plan,
                model_profile,
                cohort_identity,
            ),
        )
    records = previous_records + records
    provider_failed = run_info.get("early_termination_reason") == "provider_error"
    records = validate_evaluator_records(
        records,
        private_assignments,
        require_complete=not provider_failed,
    )
    if provider_failed:
        run_info["completed_episode_count"] = len(records)
    if model_profile is not None:
        attach_model_cost(records, model_profile)
    manifest.update(
        {
            "resumed_episode_count": len(resume_plan.completed_episode_keys),
            "retry_episode_key": (
                None
                if resume_plan.retry_episode_key is None
                else list(resume_plan.retry_episode_key)
            ),
            **run_info,
        }
    )
    write_cohort_index(
        args.output / "cohort_index.json",
        profile=manifest,
        records=records,
        status=("provider_failure_incomplete_cohort" if provider_failed else "complete"),
        private_assignments=private_assignments,
    )
    validate_cohort_index(
        args.output / "cohort_index.json",
        private_assignments=private_assignments,
    )
    state_rows = (
        _state_rows(
            args.output,
            graph_profile=args.graph_profile,
            runtime_contract=args.runtime_contract,
        )
        if args.arm == "graph"
        else []
    )
    summary = aggregate_results(records)
    if state_rows:
        summary["graph"] = {
            "transition_validity": sum(row["transition_validity"] for row in state_rows) / len(state_rows),
            "recover_state_count": sum(row["recover_state_count"] for row in state_rows),
            "state_coverage": sorted({state for row in state_rows for state in row["states"]}),
        }
    (args.output / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    if provider_failed:
        raise SystemExit("provider failure stopped this cohort unit")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=("reactive", "graph"), required=True)
    parser.add_argument(
        "--runtime",
        choices=("mock", "openai", "codex", "claude", "local-cli-bridge"),
        default="mock",
    )
    parser.add_argument("--inject-recoverable-error", action="store_true")
    parser.add_argument(
        "--graph-profile",
        choices=GRAPH_POLICY_PROFILES,
        default="full",
        help="Preregistered Graph treatment profile; reactive runs use full/default.",
    )
    parser.add_argument("--metadata", default="/mnt/e/D01_vibench/metadata.xlsx")
    parser.add_argument("--signal", default="/mnt/e/D01_vibench/RM_027_PU.h5")
    parser.add_argument(
        "--protocol",
        default="../p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml",
    )
    parser.add_argument(
        "--cross-dataset-protocol",
        type=Path,
        help=(
            "Explicit P2-E8 v3 registration. Required for external datasets; "
            "the zero-eligible v2 record is never executable."
        ),
    )
    parser.add_argument(
        "--dataset-id",
        help="Explicit external dataset identity registered by P2-E8 v3.",
    )
    parser.add_argument(
        "--data-backend",
        choices=("local_hdf5", "csv_directory"),
        default="local_hdf5",
    )
    parser.add_argument(
        "--metadata-env",
        help="Environment-variable name containing private external metadata path.",
    )
    parser.add_argument(
        "--signal-env",
        help="Environment-variable name containing private external signal root.",
    )
    parser.add_argument(
        "--data-readiness-env",
        help="Environment-variable name containing the private readiness report path.",
    )
    parser.add_argument(
        "--experiment-profile-id",
        help="Explicit profile identity for a registered cross-dataset run.",
    )
    parser.add_argument(
        "--dynamic-protocol",
        type=Path,
        help="Opt in to the active Generic-base graph_dynamic_ablation_protocol_v3; omitted for active v6.",
    )
    parser.add_argument(
        "--public-sequence-id",
        help="Frozen opaque sequence-0001 through sequence-0008 dynamic unit.",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        choices=(3, 6, 12),
        help="Nested dynamic replay horizon; its budget is read from the protocol.",
    )
    parser.add_argument("--rotation", default="rotation_0")
    parser.add_argument(
        "--tasks",
        nargs="+",
        choices=(
            "cold_start_fault_diagnosis",
            "unsupervised_anomaly_detection",
            "online_replay_monitoring",
        ),
        default=(
            "cold_start_fault_diagnosis",
            "unsupervised_anomaly_detection",
        ),
    )
    parser.add_argument("--train-samples-per-bearing", type=int, default=8)
    parser.add_argument("--validation-samples-per-bearing", type=int, default=8)
    parser.add_argument("--test-samples-per-bearing", type=int)
    parser.add_argument(
        "--max-test-bearings",
        type=int,
        help="Pilot-only cap; omitted for registered full-fold runs.",
    )
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-output-tokens-per-turn", type=int, default=2048)
    parser.add_argument("--local-cli-timeout", type=float, default=300.0)
    parser.add_argument("--runtime-contract", default=PHASE1_BASE_RUNTIME_CONTRACT)
    parser.add_argument("--resume-provider-partial", action="store_true")
    parser.add_argument(
        "--benchmark-formal-run-stamp",
        help="Matched Benchmark control run stamp (YYYYMMDDTHHMMSSZ).",
    )
    parser.add_argument(
        "--benchmark-control-protocol-id",
        help="Active Benchmark control protocol identity paired with this Graph run.",
    )
    parser.add_argument(
        "--benchmark-control-profile-id",
        help="Active Benchmark control experiment profile paired with this Graph run.",
    )
    parser.add_argument("--seed", type=int, default=20260808)
    parser.add_argument("--provider-label", default="configured_gateway")
    parser.add_argument("--input-usd-per-million", type=float)
    parser.add_argument("--output-usd-per-million", type=float)
    parser.add_argument("--base-url-env", default="LLM_BASE_URL")
    parser.add_argument("--api-key-env", default="LLM_API_KEY")
    parser.add_argument("--model-env", default="LLM_MODEL")
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main() -> None:
    asyncio.run(_run(build_parser().parse_args()))


if __name__ == "__main__":
    main()
