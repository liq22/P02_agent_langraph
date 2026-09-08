#!/usr/bin/env python3
"""Insert accepted Paper 2 core/replay results and figures into the manuscript."""

from __future__ import annotations

import argparse
import html
import json
import math
import os
from pathlib import Path
import re
import tempfile
from collections.abc import Mapping
from typing import Any, Iterable

import yaml

from phm_graph_agent import STATES as EXECUTABLE_STATES


class ResultsPending(RuntimeError):
    """Raised when the registered formal inputs are absent or ineligible."""


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROTOCOL = ROOT / "paper/experiments/p2_e1_generic_base_formal_v2.yaml"
DEFAULT_TABLE = ROOT / "paper/assets/tables/graph_monitor_manuscript_results.md"
DEFAULT_CORE_FIGURE = ROOT / "paper/assets/figures/p2_e1_core_primary.svg"
DEFAULT_STATE_JSON = (
    ROOT / "paper/experiments/results/p2_e1_graph_state_summary_v2.json"
)
DEFAULT_STATE_TABLE = ROOT / "paper/assets/tables/p2_e1_graph_state_summary.md"
DEFAULT_MANUSCRIPT = ROOT / "paper/draft/main.md"
FORMAL_RUN_STAMP_PATTERN = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")
REVISION_PATTERN = re.compile(r"^[0-9a-f]{40}$")


DIAGNOSIS_TASK = "cold_start_fault_diagnosis"
ANOMALY_TASK = "unsupervised_anomaly_detection"
REPLAY_TASK = "online_replay_monitoring"
TASK = REPLAY_TASK  # Backward-compatible import for downstream utilities.
CORE_TASKS = (DIAGNOSIS_TASK, ANOMALY_TASK)
RUNTIME_CONTRACT = "phase1_opaque_sample_vibration_feature_schema_v6"
EVIDENCE_CLASS = "real_data_formal_candidate"
BOOTSTRAP_ITERATIONS = 2000
REPLAY_MISSING_SCORE_POLICY_ID = "phase1_replay_target_adverse_missing_score_v1"
CORE_EPISODES = 192
CORE_EPISODES_PER_TASK = 96
REPLAY_EPISODES = 24
SEEDS = [20260808, 20260809, 20260810]
CORE_ROTATIONS = [f"rotation_{index}" for index in range(4)]
STATES = (
    "Inspect",
    "Hypothesize",
    "Analyze",
    "Check",
    "Monitor",
    "Revise",
    "Recover",
    "Submit",
)
DYNAMIC_PROTOCOL = "graph_dynamic_ablation_protocol_v3"
CONTROL_DISPLAY = "Benchmark Generic (Reactive-equivalent)"
PRIMARY_V6_STATE_NOTE = (
    "The registered v6 primary defines no `public_condition_event`; zero Monitor/Revise "
    "occupancy or visitation is therefore valid and supports no dynamic-revision "
    f"claim. `{DYNAMIC_PROTOCOL}` is a separate preregistered profile with accepted "
    "provider-free mechanics and 0/240 formal coverage; its dynamic/ablation claims "
    "must not be inferred from or pooled with the primary cohort."
)

CORE_TABLE_BEGIN = "<!-- GRAPH_CORE_PRIMARY_COMPACT:BEGIN -->"
CORE_TABLE_END = "<!-- GRAPH_CORE_PRIMARY_COMPACT:END -->"
REPLAY_TABLE_BEGIN = "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:BEGIN -->"
REPLAY_TABLE_END = "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:END -->"
FIGURES_BEGIN = "<!-- GRAPH_FORMAL_FIGURES:BEGIN -->"
FIGURES_END = "<!-- GRAPH_FORMAL_FIGURES:END -->"
CORE_MANUSCRIPT_HEADING = "#### Core comparison"
REPLAY_MANUSCRIPT_HEADING = "#### Replay task-primary comparison"
FIGURES_MANUSCRIPT_HEADING = "#### Formal figures"

REGISTERED_ROLLOUT_ENDPOINTS = (
    "rollout.grounded_completion",
    "rollout.submission_rate",
    "rollout.budget_exhaustion",
    "rollout.valid_tool_call_rate",
    "rollout.repeated_action_ratio",
    "rollout.grounded_recovery_success",
    "rollout.recovery_coverage",
    "rollout.steps_to_recovery",
    "rollout.steps",
    "rollout.p95_step_latency_seconds",
    "rollout.llm_turns",
    "rollout.input_tokens",
    "rollout.output_tokens",
    "rollout.wall_clock_seconds",
    "rollout.estimated_model_cost_usd",
)
REGISTERED_ENDPOINTS = {
    DIAGNOSIS_TASK: ("task.macro_f1", *REGISTERED_ROLLOUT_ENDPOINTS),
    ANOMALY_TASK: (
        "task.completion_adjusted_average_precision",
        *REGISTERED_ROLLOUT_ENDPOINTS,
    ),
    REPLAY_TASK: ("task.average_precision", *REGISTERED_ROLLOUT_ENDPOINTS),
}
PRIMARY_ENDPOINT = {
    "cohort": "replay",
    "task": REPLAY_TASK,
    "metric": "task.average_precision",
}
BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = (
    "benchmark_formal_gitlink_topology_v1"
)
P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT = "p2_e1_formal_execution_topology_v1"
BENCHMARK_REPOSITORY = "https://github.com/liq22/phm-agent-benchmark.git"
DATA_FACTORY_REPOSITORY = "https://github.com/PHMbench/phm-data-factory.git"
P2_REPOSITORY = "https://github.com/liq22/P02_agent_langraph.git"
P2_FORMAL_REPRODUCIBILITY_PATHS = (
    "CORE.md",
    "scripts/run_graph_experiment.py",
    "src/phm_graph_agent",
)

EXPECTED_PROTOCOL_IDENTITY = {
    "schema_version": "p2_e1_generic_base_formal_v2",
    "experiment_id": "P2-E1",
}
EXPECTED_BENCHMARK_CONTROL_SOURCE = {
    "contract": "benchmark_active_v0_2_control_source_v1",
    "protocol_id": "benchmark_v0_2_0--paderborn_phase1_v1--runtime_v6--window_v3",
    "profile_id": "paper0-paderborn-primary-v1",
}
EXPECTED_FROZEN_PROFILE = {
    "runtime": "openai",
    "runtime_contract": RUNTIME_CONTRACT,
    "provider": "openrouter-free",
    "model": "cohere/north-mini-code:free",
    "inference_protocol": "openai_chat_completions",
    "thinking_mode": "not_requested",
    "temperature": 0.2,
    "max_output_tokens_per_turn": 2048,
    "input_usd_per_million": 0.0,
    "output_usd_per_million": 0.0,
}
EXPECTED_REGISTERED_DESIGN = {
    "seeds": SEEDS,
    "core": {
        "rotations": CORE_ROTATIONS,
        "tasks": list(CORE_TASKS),
        "expected_statistical_outcomes_per_arm": CORE_EPISODES,
    },
    "replay": {
        "rotations": ["rotation_0"],
        "tasks": [REPLAY_TASK],
        "expected_statistical_outcomes_per_arm": REPLAY_EPISODES,
    },
}
EXPECTED_ANALYSIS = {
    "direction": "treatment_minus_control",
    "bootstrap": {
        "method": "paired_bearing_cluster_percentile_bootstrap",
        "cluster_unit": "physical_bearing",
        "iterations": BOOTSTRAP_ITERATIONS,
        "seed": 20260820,
    },
    "task_endpoints": {
        DIAGNOSIS_TASK: ["task.macro_f1"],
        ANOMALY_TASK: ["task.completion_adjusted_average_precision"],
        REPLAY_TASK: ["task.average_precision"],
    },
    "rollout_endpoints": list(REGISTERED_ROLLOUT_ENDPOINTS),
    "replay_missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
    "primary_endpoint": PRIMARY_ENDPOINT,
}
EXPECTED_RESULT_CLAIM_BOUNDARY = (
    "Accepted absolute and paired estimates are available only when accepted=true. "
    "When false, arm_summaries and paired_bearing_bootstrap are null and no "
    "partial-prefix estimate exists."
)
RESULT_TOP_LEVEL_FIELDS = frozenset(
    {
        "schema_version",
        "gate_id",
        "accepted",
        "status",
        "provider_calls",
        "frozen_profile",
        "benchmark_control_source",
        "formal_execution_topology",
        "protocol_identity",
        "registered_design",
        "analysis",
        "evaluator_private_views_read",
        "effect_estimates_emitted",
        "registered_denominators",
        "registered_endpoints",
        "replay_missing_score_policy_id",
        "direction",
        "arm_summaries",
        "graph_state_summaries",
        "paired_bearing_bootstrap",
        "primary_endpoint",
        "gates",
        "blockers",
        "claim_boundary",
    }
)


def _normalized_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ResultsPending(f"{label} must be a mapping")
    try:
        normalized = json.loads(json.dumps(value, sort_keys=True))
    except (TypeError, ValueError) as exc:
        raise ResultsPending(f"{label} must be JSON-serializable") from exc
    if not isinstance(normalized, dict):
        raise ResultsPending(f"{label} must be a mapping")
    return normalized


def _require_benchmark_execution_topology(value: Any, label: str) -> dict[str, Any]:
    topology = _normalized_mapping(value, label)
    base_fields = {
        "contract",
        "benchmark_repository",
        "benchmark_revision",
        "data_factory_repository",
        "data_factory_revision",
        "data_factory_distribution_version",
        "data_factory_lock_version",
    }
    if set(topology) not in (base_fields, base_fields | {"formal_reproducibility_paths"}):
        raise ResultsPending(f"{label} fields drifted")
    if topology.get("contract") != BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT:
        raise ResultsPending(f"{label} contract drifted")
    if topology.get("benchmark_repository") != BENCHMARK_REPOSITORY:
        raise ResultsPending(f"{label} Benchmark repository drifted")
    if topology.get("data_factory_repository") != DATA_FACTORY_REPOSITORY:
        raise ResultsPending(f"{label} Data Factory repository drifted")
    for field in ("benchmark_revision", "data_factory_revision"):
        revision = topology.get(field)
        if not isinstance(revision, str) or REVISION_PATTERN.fullmatch(revision) is None:
            raise ResultsPending(f"{label} has invalid {field}")
    distribution = topology.get("data_factory_distribution_version")
    if (
        not isinstance(distribution, str)
        or not distribution
        or topology.get("data_factory_lock_version") != distribution
    ):
        raise ResultsPending(f"{label} Data Factory distribution/lock versions drifted")
    if "formal_reproducibility_paths" in topology:
        paths = topology["formal_reproducibility_paths"]
        if (
            not isinstance(paths, list)
            or any(not isinstance(path, str) or not path for path in paths)
            or len(paths) != len(set(paths))
        ):
            raise ResultsPending(f"{label} formal reproducibility paths drifted")
    return topology


def _require_graph_execution_topology(value: Any, label: str) -> dict[str, Any]:
    topology = _normalized_mapping(value, label)
    expected_fields = {
        "contract",
        "benchmark_formal_execution_topology",
        "source_repositories",
        "source_revisions",
        "formal_sources_clean",
        "canonical_origins_verified",
        "p2_formal_reproducibility_paths",
    }
    if set(topology) != expected_fields:
        raise ResultsPending(f"{label} fields drifted")
    if topology.get("contract") != P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT:
        raise ResultsPending(f"{label} contract drifted")
    benchmark = _require_benchmark_execution_topology(
        topology.get("benchmark_formal_execution_topology"),
        f"{label}.benchmark_formal_execution_topology",
    )
    expected_repositories = {
        "benchmark": BENCHMARK_REPOSITORY,
        "data_factory": DATA_FACTORY_REPOSITORY,
        "p2": P2_REPOSITORY,
    }
    if topology.get("source_repositories") != expected_repositories:
        raise ResultsPending(f"{label} source repositories drifted")
    revisions = topology.get("source_revisions")
    if not isinstance(revisions, dict) or set(revisions) != set(expected_repositories):
        raise ResultsPending(f"{label} source revisions are incomplete")
    for source, revision in revisions.items():
        if not isinstance(revision, str) or REVISION_PATTERN.fullmatch(revision) is None:
            raise ResultsPending(f"{label} has invalid {source} revision")
    if (
        revisions["benchmark"] != benchmark["benchmark_revision"]
        or revisions["data_factory"] != benchmark["data_factory_revision"]
    ):
        raise ResultsPending(f"{label} source revisions differ from Benchmark topology")
    verified = {source: True for source in expected_repositories}
    if topology.get("formal_sources_clean") != verified:
        raise ResultsPending(f"{label} does not prove clean formal sources")
    if topology.get("canonical_origins_verified") != verified:
        raise ResultsPending(f"{label} does not prove canonical origins")
    if topology.get("p2_formal_reproducibility_paths") != list(
        P2_FORMAL_REPRODUCIBILITY_PATHS
    ):
        raise ResultsPending(f"{label} P02 formal reproducibility paths drifted")
    return topology


def _require_formal_execution_topology(value: Any) -> dict[str, Any]:
    topology = _normalized_mapping(value, "combined P2-E1 formal_execution_topology")
    if set(topology) != {
        "benchmark_control",
        "graph_treatment",
        "shared_benchmark_data_factory",
    }:
        raise ResultsPending("combined P2-E1 formal_execution_topology fields drifted")
    benchmark = _require_benchmark_execution_topology(
        topology.get("benchmark_control"),
        "combined P2-E1 Benchmark control topology",
    )
    graph = _require_graph_execution_topology(
        topology.get("graph_treatment"),
        "combined P2-E1 Graph treatment topology",
    )
    shared = _require_benchmark_execution_topology(
        topology.get("shared_benchmark_data_factory"),
        "combined P2-E1 shared Benchmark/Data Factory topology",
    )
    if shared != benchmark or graph["benchmark_formal_execution_topology"] != benchmark:
        raise ResultsPending(
            "combined P2-E1 shared Benchmark/Data Factory topology drifted across arms"
        )
    return topology


STATE_SUMMARY_FIELDS = frozenset(
    {
        "episodes",
        "mean_transition_validity",
        "all_transitions_valid_rate",
        "recover_episode_rate",
        "mean_recover_visits",
        "state_coverage",
        "state_step_occupancy_proportion",
        "state_episode_visitation_rate",
    }
)

RATE_ENDPOINTS = frozenset(
    {
        "task.macro_f1",
        "task.completion_adjusted_average_precision",
        "task.average_precision",
        "rollout.grounded_completion",
        "rollout.submission_rate",
        "rollout.budget_exhaustion",
        "rollout.valid_tool_call_rate",
        "rollout.repeated_action_ratio",
        "rollout.grounded_recovery_success",
        "rollout.recovery_coverage",
    }
)

CORE_OUTCOME_ROWS = {
    DIAGNOSIS_TASK: ("Diagnosis Macro-F1", "task.macro_f1", 4),
    ANOMALY_TASK: (
        "Anomaly completion-adjusted AP",
        "task.completion_adjusted_average_precision",
        4,
    ),
}
CORE_ROLLOUT_ROWS = (
    ("Rollout", "Grounded completion", "rollout.grounded_completion", 4),
    ("Tool", "Valid tool-call rate", "rollout.valid_tool_call_rate", 4),
    ("Recovery", "Grounded recovery", "rollout.grounded_recovery_success", 4),
    ("Efficiency", "Steps", "rollout.steps", 2),
    ("Cost", "Model cost (USD)", "rollout.estimated_model_cost_usd", 6),
)
REPLAY_ROWS = (
    ("Primary", "Monitoring Average Precision", "task.average_precision", 4),
    ("Rollout", "Grounded completion", "rollout.grounded_completion", 4),
    ("Recovery", "Grounded recovery", "rollout.grounded_recovery_success", 4),
    ("Recovery", "Recovery coverage", "rollout.recovery_coverage", 4),
    ("Recovery", "Steps to recovery", "rollout.steps_to_recovery", 2),
    ("Stability", "Repeated-action ratio", "rollout.repeated_action_ratio", 4),
    ("Stability", "Budget-exhaustion rate", "rollout.budget_exhaustion", 4),
    ("Latency", "p95 step latency (seconds)", "rollout.p95_step_latency_seconds", 4),
    ("Cost", "LLM turns", "rollout.llm_turns", 2),
    ("Cost", "Model cost (USD)", "rollout.estimated_model_cost_usd", 6),
)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ResultsPending(f"missing {label}: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_constant,
            object_pairs_hook=_reject_duplicate_pairs,
        )
    except (json.JSONDecodeError, OSError, ValueError) as error:
        raise ResultsPending(f"invalid {label}: {path}") from error
    if not isinstance(value, dict):
        raise ResultsPending(f"{label} is not a JSON object")
    return value


def _json_view(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True))


def _load_active_protocol(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ResultsPending(f"missing active P2-E1 protocol: {path}")
    try:
        protocol = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise ResultsPending(f"invalid active P2-E1 protocol: {path}") from error
    if not isinstance(protocol, dict):
        raise ResultsPending("active P2-E1 protocol is not a mapping")
    expected = {
        "schema_version": EXPECTED_PROTOCOL_IDENTITY["schema_version"],
        "status": "active",
        "experiment_id": EXPECTED_PROTOCOL_IDENTITY["experiment_id"],
        "frozen_profile": EXPECTED_FROZEN_PROFILE,
        "registered_design": EXPECTED_REGISTERED_DESIGN,
        "analysis": EXPECTED_ANALYSIS,
    }
    for key, value in expected.items():
        if _json_view(protocol.get(key)) != _json_view(value):
            raise ResultsPending(f"active P2-E1 protocol has drifted {key}")
    source = protocol.get("benchmark_control_source")
    expected_source = {
        **EXPECTED_BENCHMARK_CONTROL_SOURCE,
        "formal_run_stamp": "explicit_cli_required",
        "public_leaf_root_path": "forbidden",
    }
    if _json_view(source) != _json_view(expected_source):
        raise ResultsPending("active P2-E1 protocol has drifted benchmark_control_source")
    outputs = protocol.get("outputs")
    if not isinstance(outputs, dict) or set(outputs) != {
        "readiness",
        "result",
        "accepted_publication",
    }:
        raise ResultsPending("active P2-E1 protocol has drifted outputs")
    for name in ("readiness", "result"):
        if not isinstance(outputs.get(name), str) or not outputs[name]:
            raise ResultsPending(f"active P2-E1 protocol lacks outputs.{name}")
    publication = outputs.get("accepted_publication")
    expected_publication = {
        "consumer": "scripts/render_graph_manuscript_table.py",
        "expected_formal_run_stamp_cli_flag": "--expected-benchmark-formal-run-stamp",
        "source": "accepted_combined_result_only",
        "external_state_override": "forbidden",
        "core_figure_generation": "deterministic_from_accepted_result",
        "mechanism_case": "omitted_until_bound_extractor",
        "write_contract": "grouped_replace_with_exception_rollback",
    }
    if not isinstance(publication, dict) or set(publication) != {
        *expected_publication,
        "table",
        "core_figure",
        "state_json",
        "state_table",
        "manuscript",
    }:
        raise ResultsPending("active P2-E1 protocol has drifted publication outputs")
    for key, expected_value in expected_publication.items():
        if publication.get(key) != expected_value:
            raise ResultsPending(
                f"active P2-E1 protocol has drifted accepted_publication.{key}"
            )
    for name in ("table", "core_figure", "state_json", "state_table", "manuscript"):
        if not isinstance(publication.get(name), str) or not publication[name]:
            raise ResultsPending(
                f"active P2-E1 protocol lacks accepted_publication.{name}"
            )
    return protocol


def _require_protocol_binding(
    result: Mapping[str, Any],
    protocol: Mapping[str, Any],
    *,
    expected_formal_run_stamp: str,
) -> None:
    if FORMAL_RUN_STAMP_PATTERN.fullmatch(expected_formal_run_stamp) is None:
        raise ResultsPending(
            "expected Benchmark formal run stamp must match YYYYMMDDTHHMMSSZ"
        )
    expected_fields = {
        "protocol_identity": EXPECTED_PROTOCOL_IDENTITY,
        "frozen_profile": protocol["frozen_profile"],
        "registered_design": protocol["registered_design"],
        "analysis": protocol["analysis"],
    }
    for key, expected in expected_fields.items():
        if _json_view(result.get(key)) != _json_view(expected):
            raise ResultsPending(f"combined P2-E1 result has a protocol-binding mismatch in {key}")
    source = result.get("benchmark_control_source")
    expected_source = {
        **EXPECTED_BENCHMARK_CONTROL_SOURCE,
        "formal_run_stamp": expected_formal_run_stamp,
    }
    if _json_view(source) != _json_view(expected_source):
        raise ResultsPending(
            "combined P2-E1 result has a Benchmark control-source or formal-stamp mismatch"
        )


def _require_gate(
    report: dict[str, Any],
    label: str,
    *,
    graph: bool,
    mode: str,
    tasks: Iterable[str],
    episodes: int,
    runs: int,
    rotations: list[str],
) -> None:
    task_list = list(tasks)
    expected = {
        "accepted": True,
        "mode": mode,
        "expected_episodes": episodes,
        "observed_unique_episodes": episodes,
        "expected_runs": runs,
        "observed_runs": runs,
        "seeds": SEEDS,
        "rotations": rotations,
        "tasks": task_list,
        "inference_contract_required": True,
        "state_evaluation_required": graph,
        "expected_runtime_contract": RUNTIME_CONTRACT,
        "expected_evidence_classes": [EVIDENCE_CLASS],
        "errors": [],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise ResultsPending(f"{label} does not satisfy {key}={value!r}")
    contract = report.get("contract")
    if not isinstance(contract, dict):
        raise ResultsPending(f"{label} is missing its frozen contract")
    if contract.get("runtime_contract") != RUNTIME_CONTRACT:
        raise ResultsPending(f"{label} has the wrong runtime contract")
    if contract.get("tasks") != task_list:
        raise ResultsPending(f"{label} has the wrong task contract")


def _require_matched_gates(
    control: dict[str, Any],
    graph: dict[str, Any],
    *,
    scope: str,
    mode: str,
    tasks: Iterable[str],
    episodes: int,
    runs: int,
    rotations: list[str],
) -> None:
    _require_gate(
        control,
        f"{CONTROL_DISPLAY} {scope} cohort",
        graph=False,
        mode=mode,
        tasks=tasks,
        episodes=episodes,
        runs=runs,
        rotations=rotations,
    )
    _require_gate(
        graph,
        f"Graph {scope} cohort",
        graph=True,
        mode=mode,
        tasks=tasks,
        episodes=episodes,
        runs=runs,
        rotations=rotations,
    )
    if control.get("contract") != graph.get("contract"):
        raise ResultsPending(f"Benchmark Generic and Graph {scope} contracts do not match")
    if control.get("run_contracts") != graph.get("run_contracts"):
        raise ResultsPending(
            f"Benchmark Generic and Graph {scope} numerical run contracts do not match"
        )


def _require_acceptance_source(value: Any, expected: Path, label: str) -> None:
    if not isinstance(value, str) or Path(value).resolve() != expected.resolve():
        raise ResultsPending(f"{label} does not reference its accepted cohort gate")


def _require_formal_result(
    result: dict[str, Any], label: str, root: str, tasks: Iterable[str]
) -> None:
    task_set = set(tasks)
    if result.get("evidence_class") != EVIDENCE_CLASS:
        raise ResultsPending(f"{label} is not a formal-candidate result")
    if result.get("registered_evidence_class") != "formal":
        raise ResultsPending(f"{label} has the wrong registered evidence class")
    if result.get("result_role") != "confirmatory":
        raise ResultsPending(f"{label} has the wrong result role")
    if result.get("bootstrap_iterations") != BOOTSTRAP_ITERATIONS:
        raise ResultsPending(f"{label} does not use 2,000 bootstrap resamples")
    if result.get("seed") != EXPECTED_ANALYSIS["bootstrap"]["seed"]:
        raise ResultsPending(f"{label} has the wrong bootstrap seed")
    if root == "estimate" and result.get("direction") != "treatment_minus_control":
        raise ResultsPending(f"{label} has the wrong contrast direction")
    values = result.get(root)
    if not isinstance(values, dict) or set(values) != task_set:
        raise ResultsPending(f"{label} has the wrong registered task set")
    intervals = result.get("bearing_bootstrap_95ci")
    valid = result.get("bearing_bootstrap_valid_replicates")
    if not isinstance(intervals, dict) or not isinstance(valid, dict):
        raise ResultsPending(f"{label} lacks registered bootstrap results")
    for task in task_set:
        expected_endpoints = set(REGISTERED_ENDPOINTS[task])
        if (
            not isinstance(intervals.get(task), dict)
            or set(intervals[task]) != expected_endpoints
            or not isinstance(valid.get(task), dict)
            or set(valid[task]) != expected_endpoints
        ):
            raise ResultsPending(f"{label} has endpoint drift for {task}")
        task_values = values[task]
        if not isinstance(task_values, dict):
            raise ResultsPending(f"{label} has invalid values for {task}")
        for endpoint in expected_endpoints:
            if root == "estimate":
                present = endpoint in task_values
            else:
                section, name = endpoint.split(".", 1)
                present = isinstance(task_values.get(section), dict) and name in task_values[section]
            if not present:
                raise ResultsPending(f"{label} is missing {task}.{endpoint}")
            _extract(result, task, endpoint, delta=root == "estimate")


def _extract(
    result: dict[str, Any], task: str, metric: str, *, delta: bool
) -> tuple[float | None, list[float] | None, int, int]:
    root = "estimate" if delta else "summary"
    section, name = metric.split(".", 1)
    try:
        task_values = result[root][task]
        value = task_values[metric] if delta else task_values[section][name]
        interval = result["bearing_bootstrap_95ci"][task][metric]
        valid = result["bearing_bootstrap_valid_replicates"][task][metric]
    except (KeyError, TypeError) as error:
        raise ResultsPending(f"missing registered result {task}.{metric}") from error
    if value is not None and (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(float(value))
    ):
        raise ResultsPending(f"invalid estimate for {task}.{metric}")
    if interval is not None and (
        not isinstance(interval, list)
        or len(interval) != 2
        or not all(
            not isinstance(bound, bool)
            and isinstance(bound, (int, float))
            and math.isfinite(float(bound))
            for bound in interval
        )
        or float(interval[0]) > float(interval[1])
    ):
        raise ResultsPending(f"invalid interval for {task}.{metric}")
    if (
        isinstance(valid, bool)
        or not isinstance(valid, int)
        or not 0 <= valid <= BOOTSTRAP_ITERATIONS
    ):
        raise ResultsPending(f"invalid bootstrap count for {task}.{metric}")
    if value is None and (interval is not None or valid != 0):
        raise ResultsPending(
            f"undefined estimate has non-null bootstrap evidence for {task}.{metric}"
        )
    if value is not None and ((interval is None) != (valid == 0)):
        raise ResultsPending(
            f"bootstrap interval/count availability differs for {task}.{metric}"
        )
    domain_low: float | None = None
    domain_high: float | None = None
    if metric in RATE_ENDPOINTS:
        domain_low, domain_high = (-1.0, 1.0) if delta else (0.0, 1.0)
    elif not delta:
        domain_low = 0.0
    if value is not None and (
        (domain_low is not None and float(value) < domain_low)
        or (domain_high is not None and float(value) > domain_high)
    ):
        raise ResultsPending(f"out-of-domain estimate for {task}.{metric}")
    if interval is not None and any(
        (domain_low is not None and float(bound) < domain_low)
        or (domain_high is not None and float(bound) > domain_high)
        for bound in interval
    ):
        raise ResultsPending(f"out-of-domain interval for {task}.{metric}")
    return (
        None if value is None else float(value),
        None if interval is None else [float(bound) for bound in interval],
        valid,
        BOOTSTRAP_ITERATIONS,
    )


def _cell(
    item: tuple[float | None, list[float] | None, int, int],
    precision: int,
    *,
    signed: bool,
) -> str:
    value, interval, valid, total = item
    if value is None:
        return f"N/A [CI N/A]; {valid}/{total}"
    sign = "+" if signed else ""
    estimate = f"{value:{sign}.{precision}f}"
    if interval is None:
        return f"{estimate} [CI N/A]; {valid}/{total}"
    low, high = interval
    return (
        f"{estimate} [{low:{sign}.{precision}f}, {high:{sign}.{precision}f}]; "
        f"{valid}/{total}"
    )


def _require_state_summary(
    state_summary: dict[str, Any], tasks: Iterable[str], *, episodes_per_task: int
) -> dict[str, dict[str, Any]]:
    if tuple(EXECUTABLE_STATES) != STATES:
        raise ResultsPending(
            "executable Graph topology does not match the frozen eight-state reporting contract"
        )
    task_list = list(tasks)
    if set(state_summary) != set(task_list):
        raise ResultsPending("Graph state summary has the wrong registered task set")
    validated: dict[str, dict[str, Any]] = {}
    for task in task_list:
        values = state_summary.get(task)
        if not isinstance(values, dict):
            raise ResultsPending(f"Graph state summary is invalid for {task}")
        if set(values) != STATE_SUMMARY_FIELDS:
            raise ResultsPending(
                f"Graph state summary has unexpected or missing fields for {task}"
            )
        if values.get("episodes") != episodes_per_task:
            raise ResultsPending(
                f"Graph state summary has the wrong episode count for {task}"
            )
        occupancy = values.get("state_step_occupancy_proportion")
        visitation = values.get("state_episode_visitation_rate")
        if not isinstance(occupancy, dict) or set(occupancy) != set(STATES):
            raise ResultsPending(
                f"Graph state occupancy lacks the exact eight executable states for {task}"
            )
        if not isinstance(visitation, dict) or set(visitation) != set(STATES):
            raise ResultsPending(
                f"Graph state visitation lacks the exact eight executable states for {task}"
            )
        for state in STATES:
            if (
                isinstance(occupancy[state], bool)
                or not isinstance(occupancy[state], (int, float))
                or not math.isfinite(float(occupancy[state]))
                or not 0.0 <= float(occupancy[state]) <= 1.0
                or isinstance(visitation[state], bool)
                or not isinstance(visitation[state], (int, float))
                or not math.isfinite(float(visitation[state]))
                or not 0.0 <= float(visitation[state]) <= 1.0
            ):
                raise ResultsPending(f"Graph state diagnostics are invalid for {task}.{state}")
        occupancy_total = sum(float(occupancy[state]) for state in STATES)
        if not (
            math.isclose(occupancy_total, 1.0, rel_tol=1e-9, abs_tol=1e-9)
            or (
                math.isclose(occupancy_total, 0.0, rel_tol=0.0, abs_tol=1e-12)
                and all(float(visitation[state]) == 0.0 for state in STATES)
            )
        ):
            raise ResultsPending(
                f"Graph state occupancy is neither normalized nor an all-empty trajectory for {task}"
            )
        for metric in (
            "mean_transition_validity",
            "all_transitions_valid_rate",
            "recover_episode_rate",
            "mean_recover_visits",
        ):
            metric_value = values.get(metric)
            if (
                isinstance(metric_value, bool)
                or not isinstance(metric_value, (int, float))
                or not math.isfinite(float(metric_value))
                or float(metric_value) < 0.0
            ):
                raise ResultsPending(f"Graph state summary is missing {task}.{metric}")
        for metric in (
            "mean_transition_validity",
            "all_transitions_valid_rate",
            "recover_episode_rate",
        ):
            if float(values[metric]) > 1.0:
                raise ResultsPending(f"Graph state rate is out of domain for {task}.{metric}")
        coverage = values.get("state_coverage")
        expected_coverage = [
            state for state in STATES if float(visitation[state]) > 0.0
        ]
        if (
            not isinstance(coverage, list)
            or len(coverage) != len(set(coverage))
            or coverage != expected_coverage
        ):
            raise ResultsPending(f"Graph state coverage is invalid for {task}")
        validated[task] = {field: values[field] for field in STATE_SUMMARY_FIELDS}
    return validated


def _comparison_table(
    *,
    tasks: Iterable[str],
    rows: dict[str, tuple[tuple[str, str, str, int], ...]],
    control_summary: dict[str, Any],
    graph_summary: dict[str, Any],
    paired_delta: dict[str, Any],
) -> list[str]:
    lines = [
        f"| Task | Role | Registered endpoint | {CONTROL_DISPLAY} estimate [95% CI]; valid/2000 | Graph estimate [95% CI]; valid/2000 | Graph - Generic [95% CI]; valid/2000 |",
        "|---|---|---|---:|---:|---:|",
    ]
    for task in tasks:
        for role, endpoint, metric, precision in rows[task]:
            control = _extract(control_summary, task, metric, delta=False)
            graph = _extract(graph_summary, task, metric, delta=False)
            delta = _extract(paired_delta, task, metric, delta=True)
            lines.append(
                f"| {task} | {role} | {endpoint} | "
                f"{_cell(control, precision, signed=False)} | "
                f"{_cell(graph, precision, signed=False)} | "
                f"{_cell(delta, precision, signed=True)} |"
            )
    return lines


def _state_table(
    state_values: dict[str, dict[str, Any]], tasks: Iterable[str]
) -> list[str]:
    lines = [
        "Graph-only state diagnostics (no Benchmark Generic analogue):",
        "",
        "| Task | State | Step occupancy proportion | Episode visitation rate |",
        "|---|---|---:|---:|",
    ]
    for task in tasks:
        occupancy = state_values[task]["state_step_occupancy_proportion"]
        visitation = state_values[task]["state_episode_visitation_rate"]
        for state in STATES:
            lines.append(
                f"| {task} | {state} | {float(occupancy[state]):.4f} | "
                f"{float(visitation[state]):.4f} |"
            )
        values = state_values[task]
        lines.extend(
            [
                "",
                f"{task} transition validity: "
                f"{float(values['mean_transition_validity']):.4f}; "
                f"all-valid episode rate: {float(values['all_transitions_valid_rate']):.4f}; "
                f"Recover episode rate: {float(values['recover_episode_rate']):.4f}; "
                f"mean Recover visits: {float(values['mean_recover_visits']):.4f}.",
                "",
            ]
        )
    lines.append(
        "N/A denotes an undefined accepted estimate and is never replaced with zero. "
        "State values are Graph-only treatment-integrity diagnostics, not paired effects."
    )
    lines.extend(["", PRIMARY_V6_STATE_NOTE])
    return lines


def render_core_table(
    *,
    control_summary: dict[str, Any],
    graph_summary: dict[str, Any],
    paired_delta: dict[str, Any],
    state_summary: dict[str, Any],
) -> str:
    _require_formal_result(control_summary, "Benchmark Generic core summary", "summary", CORE_TASKS)
    _require_formal_result(graph_summary, "Graph core summary", "summary", CORE_TASKS)
    _require_formal_result(
        paired_delta, "Graph-minus-Generic core paired result", "estimate", CORE_TASKS
    )
    if paired_delta.get("direction") != "treatment_minus_control":
        raise ResultsPending("core paired result direction is not Graph minus Generic")
    state_values = _require_state_summary(
        state_summary, CORE_TASKS, episodes_per_task=CORE_EPISODES_PER_TASK
    )
    rows = {
        task: (("Task primary", *CORE_OUTCOME_ROWS[task]), *CORE_ROLLOUT_ROWS)
        for task in CORE_TASKS
    }
    lines = _comparison_table(
        tasks=CORE_TASKS,
        rows=rows,
        control_summary=control_summary,
        graph_summary=graph_summary,
        paired_delta=paired_delta,
    )
    lines.extend(["", *_state_table(state_values, CORE_TASKS)])
    return "\n".join(lines) + "\n"


def render_replay_table(
    *,
    reactive_summary: dict[str, Any],
    graph_summary: dict[str, Any],
    paired_delta: dict[str, Any],
    state_summary: dict[str, Any],
) -> str:
    tasks = (REPLAY_TASK,)
    _require_formal_result(
        reactive_summary, "Benchmark Generic monitoring summary", "summary", tasks
    )
    _require_formal_result(graph_summary, "Graph monitoring summary", "summary", tasks)
    _require_formal_result(
        paired_delta, "Graph-minus-Generic replay paired result", "estimate", tasks
    )
    if paired_delta.get("direction") != "treatment_minus_control":
        raise ResultsPending("replay paired result direction is not Graph minus Generic")
    state_values = _require_state_summary(
        state_summary, tasks, episodes_per_task=REPLAY_EPISODES
    )
    lines = _comparison_table(
        tasks=tasks,
        rows={REPLAY_TASK: REPLAY_ROWS},
        control_summary=reactive_summary,
        graph_summary=graph_summary,
        paired_delta=paired_delta,
    )
    lines.extend(["", *_state_table(state_values, tasks)])
    return "\n".join(lines) + "\n"


def _require_combined_result(
    result: dict[str, Any],
    *,
    protocol: Mapping[str, Any] | None = None,
    expected_formal_run_stamp: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if set(result) != RESULT_TOP_LEVEL_FIELDS:
        raise ResultsPending(
            "combined P2-E1 result does not match the finalizer output schema"
        )
    expected_top_level = {
        "schema_version": "p2_e1_generic_base_formal_v2_result",
        "gate_id": "P2-E1",
        "accepted": True,
        "status": "accepted_paired_result",
        "provider_calls": 0,
        "registered_denominators": {
            "core_per_arm": CORE_EPISODES,
            "replay_per_arm": REPLAY_EPISODES,
        },
        "registered_endpoints": {
            task: list(endpoints) for task, endpoints in REGISTERED_ENDPOINTS.items()
        },
        "replay_missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "direction": "GraphDecisionAgent_minus_Benchmark_GenericLLMToolAgent",
        "primary_endpoint": PRIMARY_ENDPOINT,
        "evaluator_private_views_read": 2 * (CORE_EPISODES + REPLAY_EPISODES),
        "blockers": [],
        "claim_boundary": EXPECTED_RESULT_CLAIM_BOUNDARY,
    }
    for key, expected in expected_top_level.items():
        if result.get(key) != expected:
            raise ResultsPending(
                f"combined P2-E1 result does not satisfy {key}={expected!r}"
            )
    _require_formal_execution_topology(result.get("formal_execution_topology"))
    if protocol is not None:
        if expected_formal_run_stamp is None:
            raise ResultsPending(
                "active combined-result publication requires an explicit Benchmark formal run stamp"
            )
        _require_protocol_binding(
            result,
            protocol,
            expected_formal_run_stamp=expected_formal_run_stamp,
        )

    gates = result.get("gates")
    if not isinstance(gates, dict) or set(gates) != {
        "arms",
        "paired_cohorts",
        "all_four_arm_gates_accepted",
        "both_exact_pairing_gates_accepted",
    }:
        raise ResultsPending("combined P2-E1 result is missing embedded gates")
    if gates.get("all_four_arm_gates_accepted") is not True:
        raise ResultsPending("combined P2-E1 result lacks four accepted arm gates")
    if gates.get("both_exact_pairing_gates_accepted") is not True:
        raise ResultsPending("combined P2-E1 result lacks two accepted pairing gates")
    arms = gates.get("arms")
    expected_arms = {
        "generic_core": CORE_EPISODES,
        "graph_core": CORE_EPISODES,
        "generic_replay": REPLAY_EPISODES,
        "graph_replay": REPLAY_EPISODES,
    }
    if not isinstance(arms, dict) or set(arms) != set(expected_arms):
        raise ResultsPending("combined P2-E1 result has the wrong arm gate set")
    for name, expected in expected_arms.items():
        gate = arms[name]
        if not isinstance(gate, dict) or gate != {
            "accepted": True,
            "statistical_outcomes": expected,
            "expected_statistical_outcomes": expected,
            "blockers": [],
        }:
            raise ResultsPending(f"combined P2-E1 result has an invalid {name} gate")
    paired_gates = gates.get("paired_cohorts")
    if not isinstance(paired_gates, dict) or set(paired_gates) != {"core", "replay"}:
        raise ResultsPending("combined P2-E1 result has the wrong pairing gate set")
    for scope, expected in (("core", CORE_EPISODES), ("replay", REPLAY_EPISODES)):
        gate = paired_gates[scope]
        if (
            not isinstance(gate, dict)
            or set(gate)
            != {
                "accepted",
                "expected_pairs",
                "matched_statistical_keys",
                "control_only_keys",
                "treatment_only_keys",
                "blockers",
            }
            or gate.get("accepted") is not True
            or gate.get("expected_pairs") != expected
            or gate.get("matched_statistical_keys") != expected
            or gate.get("control_only_keys") != 0
            or gate.get("treatment_only_keys") != 0
            or gate.get("blockers") != []
        ):
            raise ResultsPending(
                f"combined P2-E1 result has an invalid {scope} pairing gate"
            )

    arm_summaries = result.get("arm_summaries")
    paired = result.get("paired_bearing_bootstrap")
    graph_states = result.get("graph_state_summaries")
    if not isinstance(arm_summaries, dict) or set(arm_summaries) != {"core", "replay"}:
        raise ResultsPending("combined P2-E1 result lacks complete arm summaries")
    if not isinstance(paired, dict) or set(paired) != {"core", "replay"}:
        raise ResultsPending("combined P2-E1 result lacks complete paired estimates")
    if not isinstance(graph_states, dict) or set(graph_states) != {"core", "replay"}:
        raise ResultsPending("combined P2-E1 result lacks complete Graph state summaries")
    for scope, expected_policy in (
        ("core", None),
        ("replay", REPLAY_MISSING_SCORE_POLICY_ID),
    ):
        tasks = CORE_TASKS if scope == "core" else (REPLAY_TASK,)
        summaries = arm_summaries[scope]
        if not isinstance(summaries, dict) or set(summaries) != {
            "control",
            "treatment",
        }:
            raise ResultsPending(f"combined P2-E1 result has invalid {scope} summaries")
        for arm in ("control", "treatment"):
            summary = summaries[arm]
            if not isinstance(summary, dict):
                raise ResultsPending(
                    f"combined P2-E1 result has an invalid {scope}.{arm} summary"
                )
            if (
                summary.get("registered_evidence_class") != "formal"
                or summary.get("result_role") != "confirmatory"
            ):
                raise ResultsPending(
                    f"combined P2-E1 result has informal {scope}.{arm} evidence"
                )
            if summary.get("replay_missing_score_policy_id") != expected_policy:
                raise ResultsPending(
                    f"combined P2-E1 result has a replay-policy mismatch in {scope}.{arm}"
                )
            _require_formal_result(
                summary,
                f"combined P2-E1 {scope}.{arm} summary",
                "summary",
                tasks,
            )
            expected_episodes = (
                CORE_EPISODES_PER_TASK if scope == "core" else REPLAY_EPISODES
            )
            expected_bearings = 32 if scope == "core" else 8
            for task in tasks:
                task_summary = summary.get("summary", {}).get(task, {})
                if (
                    task_summary.get("episodes") != expected_episodes
                    or task_summary.get("bearings") != expected_bearings
                ):
                    raise ResultsPending(
                        f"combined P2-E1 result has invalid episode/bearing counts in "
                        f"{scope}.{arm}.{task}"
                    )
            if scope == "replay":
                replay_summary = summary.get("summary", {}).get(REPLAY_TASK, {})
                task_values = replay_summary.get("task", {})
                evaluation_contract = replay_summary.get("evaluation_contract", {})
                assigned = task_values.get("assigned_windows")
                submitted = task_values.get("submitted_windows")
                missing = task_values.get("missing_assigned_scores")
                coverage = task_values.get("score_coverage")
                if (
                    replay_summary.get("episodes") != REPLAY_EPISODES
                    or evaluation_contract.get("missing_assigned_score_policy_id")
                    != REPLAY_MISSING_SCORE_POLICY_ID
                    or assigned != 3 * REPLAY_EPISODES
                    or isinstance(submitted, bool)
                    or not isinstance(submitted, int)
                    or isinstance(missing, bool)
                    or not isinstance(missing, int)
                    or submitted < 0
                    or missing < 0
                    or submitted + missing != assigned
                    or isinstance(coverage, bool)
                    or not isinstance(coverage, (int, float))
                    or not math.isfinite(float(coverage))
                    or not math.isclose(
                        float(coverage), submitted / assigned, rel_tol=0.0, abs_tol=1e-12
                    )
                ):
                    raise ResultsPending(
                        f"combined P2-E1 result lacks valid replay score accounting in {arm}"
                    )
        paired_scope = paired[scope]
        if not isinstance(paired_scope, dict):
            raise ResultsPending(
                f"combined P2-E1 result has invalid {scope} paired estimates"
            )
        if (
            paired_scope.get("registered_evidence_class") != "formal"
            or paired_scope.get("result_role") != "confirmatory"
        ):
            raise ResultsPending(
                f"combined P2-E1 result has informal {scope} paired evidence"
            )
        if paired_scope.get("replay_missing_score_policy_id") != expected_policy:
            raise ResultsPending(
                f"combined P2-E1 result has a replay-policy mismatch in {scope} paired estimates"
            )
        _require_formal_result(
            paired_scope,
            f"combined P2-E1 {scope} paired estimates",
            "estimate",
            tasks,
        )
    observed_effect_count = sum(
        value is not None
        for scope in ("core", "replay")
        for metrics in paired[scope]["estimate"].values()
        for value in metrics.values()
    )
    if result.get("effect_estimates_emitted") != observed_effect_count:
        raise ResultsPending(
            "combined P2-E1 effect-estimate count does not match emitted estimates"
        )
    validated_states = {
        "core": _require_state_summary(
            graph_states["core"], CORE_TASKS, episodes_per_task=CORE_EPISODES_PER_TASK
        ),
        "replay": _require_state_summary(
            graph_states["replay"], (REPLAY_TASK,), episodes_per_task=REPLAY_EPISODES
        ),
    }
    return arm_summaries, paired, validated_states


def _summary_point(
    summary: Mapping[str, Any], task: str, endpoint: str
) -> float | None:
    section, name = endpoint.split(".", 1)
    try:
        value = summary["summary"][task][section][name]
    except (KeyError, TypeError) as error:
        raise ResultsPending(f"missing arm-summary point {task}.{endpoint}") from error
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResultsPending(f"non-numeric arm-summary point {task}.{endpoint}")
    point = float(value)
    if not math.isfinite(point):
        raise ResultsPending(f"non-finite arm-summary point {task}.{endpoint}")
    if endpoint in RATE_ENDPOINTS and not 0.0 <= point <= 1.0:
        raise ResultsPending(f"out-of-domain arm-summary rate {task}.{endpoint}")
    if endpoint not in RATE_ENDPOINTS and point < 0.0:
        raise ResultsPending(f"negative arm-summary magnitude {task}.{endpoint}")
    return point


def _paired_point(
    paired: Mapping[str, Any], task: str, endpoint: str
) -> float | None:
    try:
        value = paired["estimate"][task][endpoint]
    except (KeyError, TypeError) as error:
        raise ResultsPending(f"missing paired point {task}.{endpoint}") from error
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResultsPending(f"non-numeric paired point {task}.{endpoint}")
    point = float(value)
    if not math.isfinite(point):
        raise ResultsPending(f"non-finite paired point {task}.{endpoint}")
    if endpoint in RATE_ENDPOINTS and not -1.0 <= point <= 1.0:
        raise ResultsPending(f"out-of-domain paired rate {task}.{endpoint}")
    return point


def _require_combined_arithmetic(
    arm_summaries: Mapping[str, Any], paired: Mapping[str, Any]
) -> None:
    """Recompute every published Graph-minus-Generic point estimate."""

    for scope, tasks in (("core", CORE_TASKS), ("replay", (REPLAY_TASK,))):
        summaries = arm_summaries[scope]
        paired_scope = paired[scope]
        for task in tasks:
            for endpoint in REGISTERED_ENDPOINTS[task]:
                control = _summary_point(summaries["control"], task, endpoint)
                treatment = _summary_point(summaries["treatment"], task, endpoint)
                observed = _paired_point(paired_scope, task, endpoint)
                if control is None or treatment is None:
                    if observed is not None:
                        raise ResultsPending(
                            f"paired point must be null when an arm is undefined for {task}.{endpoint}"
                        )
                    continue
                expected = treatment - control
                if observed is None or not math.isclose(
                    observed, expected, rel_tol=1e-12, abs_tol=1e-12
                ):
                    raise ResultsPending(
                        f"paired point arithmetic drift for {task}.{endpoint}: "
                        f"expected {expected!r}, observed {observed!r}"
                    )


def render_tables_from_combined_result(
    *,
    result: dict[str, Any],
    core_state_summary: dict[str, Any] | None = None,
    replay_state_summary: dict[str, Any] | None = None,
    protocol: Mapping[str, Any] | None = None,
    expected_formal_run_stamp: str | None = None,
) -> tuple[str, str]:
    """Render both registered tables directly from the accepted P2-E1 finalizer."""

    arm_summaries, paired, embedded_states = _require_combined_result(
        result,
        protocol=protocol,
        expected_formal_run_stamp=expected_formal_run_stamp,
    )
    core_states = (
        embedded_states["core"] if core_state_summary is None else core_state_summary
    )
    replay_states = (
        embedded_states["replay"]
        if replay_state_summary is None
        else replay_state_summary
    )
    core_table = render_core_table(
        control_summary=arm_summaries["core"]["control"],
        graph_summary=arm_summaries["core"]["treatment"],
        paired_delta=paired["core"],
        state_summary=core_states,
    )
    replay_table = render_replay_table(
        reactive_summary=arm_summaries["replay"]["control"],
        graph_summary=arm_summaries["replay"]["treatment"],
        paired_delta=paired["replay"],
        state_summary=replay_states,
    )
    return core_table, replay_table


def render_core_figure(result: Mapping[str, Any]) -> str:
    """Render the three registered task-primary arm estimates deterministically."""

    arms = result["arm_summaries"]
    rows = (
        ("Diagnosis Macro-F1", "core", DIAGNOSIS_TASK, "task.macro_f1"),
        (
            "Anomaly completion-adjusted AP",
            "core",
            ANOMALY_TASK,
            "task.completion_adjusted_average_precision",
        ),
        ("Replay Average Precision", "replay", REPLAY_TASK, "task.average_precision"),
    )
    width = 960
    height = 122 + 112 * len(rows)
    plot_x = 330
    plot_width = 500
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Accepted P2-E1 task-primary arm estimates</title>',
        '<desc id="desc">Benchmark Generic and Graph task-primary point estimates on matched accepted cohorts. Error bars remain in the accompanying table.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="30" y="38" font-family="sans-serif" font-size="22" font-weight="700" fill="#172033">P2-E1 accepted task-primary estimates</text>',
        '<text x="30" y="64" font-family="sans-serif" font-size="13" fill="#4b5563">Matched formal cohorts; task performance only</text>',
        f'<line x1="{plot_x}" y1="82" x2="{plot_x + plot_width}" y2="82" stroke="#9ca3af"/>',
    ]
    for tick in range(6):
        value = tick / 5
        x = plot_x + value * plot_width
        parts.extend(
            [
                f'<line x1="{x:.1f}" y1="78" x2="{x:.1f}" y2="86" stroke="#6b7280"/>',
                f'<text x="{x:.1f}" y="102" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#4b5563">{value:.1f}</text>',
            ]
        )
    for index, (label, scope, task, endpoint) in enumerate(rows):
        top = 118 + index * 112
        control = _summary_point(arms[scope]["control"], task, endpoint)
        treatment = _summary_point(arms[scope]["treatment"], task, endpoint)
        paired = _paired_point(result["paired_bearing_bootstrap"][scope], task, endpoint)
        parts.append(
            f'<g data-task="{html.escape(task)}" data-endpoint="{html.escape(endpoint)}">'
        )
        parts.append(
            f'<text x="30" y="{top + 22}" font-family="sans-serif" font-size="14" font-weight="600" fill="#172033">{html.escape(label)}</text>'
        )
        for arm_index, (arm_label, point, color) in enumerate(
            (
                ("Benchmark Generic", control, "#64748b"),
                ("Graph", treatment, "#2563eb"),
            )
        ):
            y = top + 4 + arm_index * 34
            parts.append(
                f'<text x="190" y="{y + 15}" font-family="sans-serif" font-size="12" fill="#374151">{arm_label}</text>'
            )
            if point is None:
                parts.append(
                    f'<text x="{plot_x}" y="{y + 15}" font-family="sans-serif" font-size="12" fill="#6b7280">N/A</text>'
                )
            else:
                bar_width = point * plot_width
                parts.extend(
                    [
                        f'<rect x="{plot_x}" y="{y}" width="{bar_width:.3f}" height="20" rx="3" fill="{color}" data-arm="{arm_label}" data-point="{point:.12g}"/>',
                        f'<text x="{plot_x + bar_width + 8:.3f}" y="{y + 15}" font-family="sans-serif" font-size="12" fill="#111827">{point:.4f}</text>',
                    ]
                )
        delta_text = "N/A" if paired is None else f"{paired:+.4f}"
        parts.append(
            f'<text x="{plot_x}" y="{top + 94}" font-family="sans-serif" font-size="12" fill="#111827" data-delta="{delta_text}">Graph - Generic: {delta_text}</text>'
        )
        parts.append("</g>")
    parts.extend(
        [
            f'<text x="30" y="{height - 18}" font-family="sans-serif" font-size="11" fill="#6b7280">Point estimates only; clustered 95% intervals and valid bootstrap counts are reported in the canonical table.</text>',
            "</svg>",
        ]
    )
    return "\n".join(parts) + "\n"


def render_state_json(result: Mapping[str, Any]) -> str:
    document = {
        "schema_version": "p2_e1_graph_state_summary_v2",
        "gate_id": "P2-E1",
        "accepted": True,
        "benchmark_control_source": result["benchmark_control_source"],
        "protocol_identity": result["protocol_identity"],
        "graph_state_summaries": result["graph_state_summaries"],
        "claim_boundary": (
            "Graph-only treatment-integrity diagnostics; no Benchmark Generic analogue "
            "and no paired treatment-effect interpretation."
        ),
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"


def render_state_table(result: Mapping[str, Any]) -> str:
    states = result["graph_state_summaries"]
    core = _state_table(states["core"], CORE_TASKS)
    replay = _state_table(states["replay"], (REPLAY_TASK,))
    return "\n".join(
        [
            "# Accepted P2-E1 Graph state diagnostics",
            "",
            "## Core cohort",
            "",
            *core,
            "",
            "## Replay cohort",
            "",
            *replay,
            "",
        ]
    )


def render_active_figures(
    *,
    core_figure: Path,
    state_table: Path,
    manuscript: Path,
    monitor_mechanism_json: Path | None,
    monitor_mechanism_figure: Path | None,
) -> str:
    core_reference = _manuscript_reference(core_figure, manuscript)
    state_reference = _manuscript_reference(state_table, manuscript)
    lines = [
        f"![Accepted matched task-primary comparison]({core_reference})",
        "",
        "The deterministic core figure reports only registered task-primary arm point "
        "estimates from the accepted combined result; clustered intervals remain in "
        "the canonical table.",
        "",
        "Graph-only state diagnostics are synchronized in "
        f"`{state_reference}` and are treatment-integrity "
        "descriptions rather than paired effects.",
    ]
    if monitor_mechanism_json is not None or monitor_mechanism_figure is not None:
        raise ResultsPending(
            "active P2-E1 publication omits mechanism inputs until a bound extractor exists"
        )
    lines.extend(
        [
            "",
            "No descriptive replay mechanism case is admitted by the active publication "
            "contract; this does not block the accepted task-primary figure.",
        ]
    )
    return "\n".join(lines) + "\n"


def _require_nonempty(path: Path, label: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ResultsPending(f"missing {label}: {path}")


def _require_monitor_case(path: Path) -> dict[str, Any]:
    case = _load(path, "monitor mechanism case")
    if case.get("case_kind") != "semantic-divergence":
        raise ResultsPending("monitor mechanism case is not semantic-divergence")
    if case.get("task_id") != REPLAY_TASK:
        raise ResultsPending("monitor mechanism case has the wrong task")
    for arm in ("control", "treatment"):
        values = case.get(arm)
        if not isinstance(values, dict) or not isinstance(
            values.get("semantic_sequence"), list
        ):
            raise ResultsPending(f"monitor mechanism case lacks the {arm} sequence")
    treatment_states = case["treatment"].get("decision_states")
    if not isinstance(treatment_states, list) or not any(
        state in STATES for state in treatment_states
    ):
        raise ResultsPending("monitor mechanism case lacks Graph state observations")
    return case


def render_figures(
    *,
    core_comparison_figure: Path,
    monitor_mechanism_json: Path,
    monitor_mechanism_figure: Path,
) -> str:
    _require_nonempty(core_comparison_figure, "accepted core comparison figure")
    _require_monitor_case(monitor_mechanism_json)
    _require_nonempty(monitor_mechanism_figure, "accepted monitor mechanism figure")
    return "\n".join(
        [
            f"![Accepted matched core comparison](../assets/figures/{core_comparison_figure.name})",
            "",
            "The accepted matched core comparison visualizes registered task and rollout "
            "endpoints only.",
            "",
            f"![Accepted long-horizon semantic/state case](../assets/figures/{monitor_mechanism_figure.name})",
            "",
            "The long-horizon figure is a descriptive semantic/state divergence, not an "
            "evaluator-gated recovery claim. Its structured source is "
            f"`paper/experiments/results/{monitor_mechanism_json.name}`.",
        ]
    ) + "\n"


def _replace_block(source: str, begin: str, end: str, content: str, label: str) -> str:
    if source.count(begin) != 1 or source.count(end) != 1:
        raise ResultsPending(f"active manuscript is missing its unique {label} markers")
    prefix, remainder = source.split(begin, 1)
    _, suffix = remainder.split(end, 1)
    return f"{prefix}{begin}\n\n{content.rstrip()}\n\n{end}{suffix}"


def insert_results(
    manuscript: Path, *, core_table: str, replay_table: str, figures: str | None
) -> str:
    if not manuscript.is_file():
        raise ResultsPending(f"missing active manuscript: {manuscript}")
    source = manuscript.read_text(encoding="utf-8")
    core_block = f"{CORE_MANUSCRIPT_HEADING}\n\n{core_table.rstrip()}"
    replay_block = f"{REPLAY_MANUSCRIPT_HEADING}\n\n{replay_table.rstrip()}"
    source = _replace_block(
        source, CORE_TABLE_BEGIN, CORE_TABLE_END, core_block, "Paper 2 core-result"
    )
    source = _replace_block(
        source,
        REPLAY_TABLE_BEGIN,
        REPLAY_TABLE_END,
        replay_block,
        "Paper 2 replay-result",
    )
    if figures is None:
        return source
    figure_block = f"{FIGURES_MANUSCRIPT_HEADING}\n\n{figures.rstrip()}"
    return _replace_block(
        source,
        FIGURES_BEGIN,
        FIGURES_END,
        figure_block,
        "Paper 2 formal-figure",
    )


def _require_result_sources(
    *,
    control_summary: dict[str, Any],
    graph_summary: dict[str, Any],
    paired_delta: dict[str, Any],
    control_acceptance: Path,
    graph_acceptance: Path,
    scope: str,
) -> None:
    _require_acceptance_source(
        control_summary.get("cohort_acceptance"),
        control_acceptance,
        f"Benchmark Generic {scope} summary",
    )
    _require_acceptance_source(
        graph_summary.get("cohort_acceptance"),
        graph_acceptance,
        f"Graph {scope} summary",
    )
    paired_sources = paired_delta.get("cohort_acceptance")
    if not isinstance(paired_sources, dict):
        raise ResultsPending(f"{scope} paired result is missing its cohort gate references")
    _require_acceptance_source(
        paired_sources.get("control"), control_acceptance, f"{scope} paired control"
    )
    _require_acceptance_source(
        paired_sources.get("treatment"), graph_acceptance, f"{scope} paired treatment"
    )


_replace_path = os.replace


def _paths_alias(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    if left.exists() and right.exists():
        try:
            return os.path.samefile(left, right)
        except OSError:
            return False
    return False


def _declared_protocol_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ResultsPending(f"active P2-E1 protocol lacks {label}")
    path = Path(value)
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def _require_declared_publication_paths(
    args: argparse.Namespace,
    protocol: Mapping[str, Any],
    *,
    combined_result: Path,
) -> None:
    outputs = protocol["outputs"]
    publication = outputs["accepted_publication"]
    supplied = {
        "outputs.result": combined_result,
        "accepted_publication.table": args.output,
        "accepted_publication.core_figure": args.core_figure_output,
        "accepted_publication.state_json": args.state_json_output,
        "accepted_publication.state_table": args.state_table_output,
        "accepted_publication.manuscript": args.manuscript,
    }
    declared = {
        "outputs.result": outputs["result"],
        "accepted_publication.table": publication["table"],
        "accepted_publication.core_figure": publication["core_figure"],
        "accepted_publication.state_json": publication["state_json"],
        "accepted_publication.state_table": publication["state_table"],
        "accepted_publication.manuscript": publication["manuscript"],
    }
    for label, supplied_path in supplied.items():
        expected = _declared_protocol_path(declared[label], label)
        if not _paths_alias(supplied_path, expected):
            raise ResultsPending(f"publication path differs from protocol {label}")


def _require_safe_publication_paths(
    targets: list[Path], *, sources: Iterable[Path]
) -> None:
    for index, target in enumerate(targets):
        for other in targets[index + 1 :]:
            if _paths_alias(target, other):
                raise ResultsPending(
                    f"publication outputs must be distinct: {target} aliases {other}"
                )
        for source in sources:
            if _paths_alias(target, source):
                raise ResultsPending(
                    f"publication output must not overwrite an input: {target}"
                )


def _restore(path: Path, original: bytes | None) -> None:
    if original is None:
        if path.exists():
            path.unlink()
        return
    path.write_bytes(original)


def _atomic_write_group(contents: Mapping[Path, str]) -> None:
    originals = {
        path: path.read_bytes() if path.exists() else None for path in contents
    }
    temporary: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in contents.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=path.parent,
                prefix=f".{path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                temporary[path] = Path(handle.name)
        for path, temporary_path in temporary.items():
            _replace_path(temporary_path, path)
            replaced.append(path)
    except Exception:
        for path in reversed(replaced):
            _restore(path, originals[path])
        raise
    finally:
        for temporary_path in temporary.values():
            if temporary_path.exists():
                temporary_path.unlink()


def _manuscript_reference(target: Path, manuscript: Path) -> str:
    return Path(
        os.path.relpath(target.resolve(), start=manuscript.parent.resolve())
    ).as_posix()


def write_table(args: argparse.Namespace) -> None:
    combined_result_path = getattr(args, "combined_result", None)
    if combined_result_path is None:
        raise ResultsPending(
            "active P2-E1 publication requires --combined-result; legacy publication is forbidden"
        )
    if (
        getattr(args, "core_state_summary", None) is not None
        or getattr(args, "state_summary", None) is not None
    ):
        raise ResultsPending(
            "active combined-result publication forbids external Graph state overrides"
        )
    if getattr(args, "core_comparison_figure", None) is not None:
        raise ResultsPending(
            "active combined-result publication generates its core figure directly"
        )
    protocol_path = getattr(args, "protocol", DEFAULT_PROTOCOL)
    expected_stamp = getattr(args, "expected_benchmark_formal_run_stamp", None)
    protocol = _load_active_protocol(protocol_path)
    _require_declared_publication_paths(
        args, protocol, combined_result=combined_result_path
    )
    result = _load(combined_result_path, "combined P2-E1 finalizer result")
    core_table, replay_table = render_tables_from_combined_result(
        result=result,
        protocol=protocol,
        expected_formal_run_stamp=expected_stamp,
    )
    arm_summaries, paired, _ = _require_combined_result(
        result,
        protocol=protocol,
        expected_formal_run_stamp=expected_stamp,
    )
    _require_combined_arithmetic(arm_summaries, paired)
    monitor_json = getattr(args, "monitor_mechanism_json", None)
    monitor_figure = getattr(args, "monitor_mechanism_figure", None)
    figures = render_active_figures(
        core_figure=args.core_figure_output,
        state_table=args.state_table_output,
        manuscript=args.manuscript,
        monitor_mechanism_json=monitor_json,
        monitor_mechanism_figure=monitor_figure,
    )
    manuscript = insert_results(
        args.manuscript,
        core_table=core_table,
        replay_table=replay_table,
        figures=figures,
    )
    combined = "# Accepted replay task-primary comparison\n\n" + replay_table
    combined += "\n# Accepted core comparison\n\n" + core_table
    targets = [
        args.output,
        args.core_figure_output,
        args.state_json_output,
        args.state_table_output,
        args.manuscript,
    ]
    _require_safe_publication_paths(targets, sources=[protocol_path, combined_result_path])
    _atomic_write_group(
        {
            args.output: combined,
            args.core_figure_output: render_core_figure(result),
            args.state_json_output: render_state_json(result),
            args.state_table_output: render_state_table(result),
            args.manuscript: manuscript,
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--combined-result", type=Path, required=True)
    parser.add_argument("--expected-benchmark-formal-run-stamp", required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_TABLE,
    )
    parser.add_argument(
        "--core-figure-output", type=Path, default=DEFAULT_CORE_FIGURE
    )
    parser.add_argument("--state-json-output", type=Path, default=DEFAULT_STATE_JSON)
    parser.add_argument("--state-table-output", type=Path, default=DEFAULT_STATE_TABLE)
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    args = parser.parse_args()
    try:
        write_table(args)
    except ResultsPending as error:
        parser.exit(2, f"pending: {error}\n")


if __name__ == "__main__":
    main()
