#!/usr/bin/env python3
"""Insert accepted Paper 2 core/replay results and figures into the manuscript."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

from phm_graph_agent import STATES as EXECUTABLE_STATES


class ResultsPending(RuntimeError):
    """Raised when the registered formal inputs are absent or ineligible."""


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


def _load(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise ResultsPending(f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise ResultsPending(f"invalid {label}: {path}") from error
    if not isinstance(value, dict):
        raise ResultsPending(f"{label} is not a JSON object")
    return value


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
    if result.get("registered_evidence_class") not in {None, "formal"}:
        raise ResultsPending(f"{label} has the wrong registered evidence class")
    if result.get("result_role") not in {None, "confirmatory"}:
        raise ResultsPending(f"{label} has the wrong result role")
    if result.get("bootstrap_iterations") != BOOTSTRAP_ITERATIONS:
        raise ResultsPending(f"{label} does not use 2,000 bootstrap resamples")
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
    if value is not None and not isinstance(value, (int, float)):
        raise ResultsPending(f"invalid estimate for {task}.{metric}")
    if interval is not None and (
        not isinstance(interval, list)
        or len(interval) != 2
        or not all(isinstance(bound, (int, float)) for bound in interval)
    ):
        raise ResultsPending(f"invalid interval for {task}.{metric}")
    if not isinstance(valid, int) or not 0 <= valid <= BOOTSTRAP_ITERATIONS:
        raise ResultsPending(f"invalid bootstrap count for {task}.{metric}")
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
            if not isinstance(occupancy[state], (int, float)) or not isinstance(
                visitation[state], (int, float)
            ):
                raise ResultsPending(f"Graph state diagnostics are invalid for {task}.{state}")
        for metric in (
            "mean_transition_validity",
            "all_transitions_valid_rate",
            "recover_episode_rate",
            "mean_recover_visits",
        ):
            if not isinstance(values.get(metric), (int, float)):
                raise ResultsPending(f"Graph state summary is missing {task}.{metric}")
        coverage = values.get("state_coverage")
        if not isinstance(coverage, list) or not set(coverage).issubset(set(STATES)):
            raise ResultsPending(f"Graph state coverage is invalid for {task}")
        validated[task] = values
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
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
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
        "blockers": [],
    }
    for key, expected in expected_top_level.items():
        if result.get(key) != expected:
            raise ResultsPending(
                f"combined P2-E1 result does not satisfy {key}={expected!r}"
            )

    gates = result.get("gates")
    if not isinstance(gates, dict):
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
                    or not isinstance(submitted, (int, float))
                    or not isinstance(missing, (int, float))
                    or submitted + missing != assigned
                    or coverage != submitted / assigned
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
    return arm_summaries, paired, graph_states


def render_tables_from_combined_result(
    *,
    result: dict[str, Any],
    core_state_summary: dict[str, Any] | None = None,
    replay_state_summary: dict[str, Any] | None = None,
) -> tuple[str, str]:
    """Render both registered tables directly from the accepted P2-E1 finalizer."""

    arm_summaries, paired, embedded_states = _require_combined_result(result)
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
    source = _replace_block(
        source, CORE_TABLE_BEGIN, CORE_TABLE_END, core_table, "Paper 2 core-result"
    )
    source = _replace_block(
        source,
        REPLAY_TABLE_BEGIN,
        REPLAY_TABLE_END,
        replay_table,
        "Paper 2 replay-result",
    )
    if figures is None:
        return source
    return _replace_block(source, FIGURES_BEGIN, FIGURES_END, figures, "Paper 2 formal-figure")


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


def write_table(args: argparse.Namespace) -> None:
    combined_result_path = getattr(args, "combined_result", None)
    if combined_result_path is not None:
        core_state_path = getattr(args, "core_state_summary", None)
        replay_state_path = getattr(args, "state_summary", None)
        core_table, replay_table = render_tables_from_combined_result(
            result=_load(combined_result_path, "combined P2-E1 finalizer result"),
            core_state_summary=(
                None
                if core_state_path is None
                else _load(core_state_path, "Graph core state summary")
            ),
            replay_state_summary=(
                None
                if replay_state_path is None
                else _load(replay_state_path, "Graph monitoring state summary")
            ),
        )
    else:
        legacy_names = (
            "core_control_summary",
            "core_graph_summary",
            "core_paired_delta",
            "core_control_acceptance",
            "core_graph_acceptance",
        )
        if any(getattr(args, name, None) is None for name in legacy_names):
            raise ResultsPending(
                "use --combined-result or supply every legacy core result/gate input"
            )
        if args.core_state_summary is None or args.state_summary is None:
            raise ResultsPending(
                "legacy result mode requires both Graph state summary inputs"
            )
        core_state_summary = _load(
            args.core_state_summary, "Graph core state summary"
        )
        replay_state_summary = _load(
            args.state_summary, "Graph monitoring state summary"
        )
        core_control_gate = _load(
            args.core_control_acceptance, "Benchmark Generic core acceptance"
        )
        core_graph_gate = _load(args.core_graph_acceptance, "Graph core acceptance")
        _require_matched_gates(
            core_control_gate,
            core_graph_gate,
            scope="core",
            mode="core",
            tasks=CORE_TASKS,
            episodes=CORE_EPISODES,
            runs=12,
            rotations=CORE_ROTATIONS,
        )
        replay_control_gate = _load(
            args.reactive_acceptance, "Benchmark Generic monitoring acceptance"
        )
        replay_graph_gate = _load(args.graph_acceptance, "Graph monitoring acceptance")
        _require_matched_gates(
            replay_control_gate,
            replay_graph_gate,
            scope="monitoring",
            mode="monitoring",
            tasks=(REPLAY_TASK,),
            episodes=REPLAY_EPISODES,
            runs=3,
            rotations=["rotation_0"],
        )

        core_control_summary = _load(
            args.core_control_summary, "Benchmark Generic core summary"
        )
        core_graph_summary = _load(args.core_graph_summary, "Graph core summary")
        core_paired_delta = _load(
            args.core_paired_delta, "Graph-minus-Generic core result"
        )
        _require_result_sources(
            control_summary=core_control_summary,
            graph_summary=core_graph_summary,
            paired_delta=core_paired_delta,
            control_acceptance=args.core_control_acceptance,
            graph_acceptance=args.core_graph_acceptance,
            scope="core",
        )
        reactive_summary = _load(
            args.reactive_summary, "Benchmark Generic monitoring summary"
        )
        graph_summary = _load(args.graph_summary, "Graph monitoring summary")
        paired_delta = _load(args.paired_delta, "Graph-minus-Generic replay result")
        _require_result_sources(
            control_summary=reactive_summary,
            graph_summary=graph_summary,
            paired_delta=paired_delta,
            control_acceptance=args.reactive_acceptance,
            graph_acceptance=args.graph_acceptance,
            scope="monitoring",
        )

        core_table = render_core_table(
            control_summary=core_control_summary,
            graph_summary=core_graph_summary,
            paired_delta=core_paired_delta,
            state_summary=core_state_summary,
        )
        replay_table = render_replay_table(
            reactive_summary=reactive_summary,
            graph_summary=graph_summary,
            paired_delta=paired_delta,
            state_summary=replay_state_summary,
        )
    figure_inputs = (
        args.core_comparison_figure,
        args.monitor_mechanism_json,
        args.monitor_mechanism_figure,
    )
    if all(value is None for value in figure_inputs):
        figures = None
    elif any(value is None for value in figure_inputs):
        raise ResultsPending(
            "formal figures are optional as a group; provide all three figure inputs or none"
        )
    else:
        figures = render_figures(
            core_comparison_figure=args.core_comparison_figure,
            monitor_mechanism_json=args.monitor_mechanism_json,
            monitor_mechanism_figure=args.monitor_mechanism_figure,
        )
    manuscript = insert_results(
        args.manuscript,
        core_table=core_table,
        replay_table=replay_table,
        figures=figures,
    )
    combined = "# Accepted replay task-primary comparison\n\n" + replay_table
    combined += "\n# Accepted core comparison\n\n" + core_table
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(combined, encoding="utf-8")
    args.manuscript.write_text(manuscript, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--combined-result", type=Path)
    parser.add_argument("--core-control-summary", type=Path)
    parser.add_argument("--core-graph-summary", type=Path)
    parser.add_argument("--core-paired-delta", type=Path)
    parser.add_argument("--core-state-summary", type=Path)
    parser.add_argument("--core-control-acceptance", type=Path)
    parser.add_argument("--core-graph-acceptance", type=Path)
    parser.add_argument("--core-comparison-figure", type=Path)
    parser.add_argument("--monitor-mechanism-json", type=Path)
    parser.add_argument("--monitor-mechanism-figure", type=Path)
    parser.add_argument(
        "--reactive-summary",
        type=Path,
        default=Path("paper/experiments/results/reactive_monitor_primary.json"),
    )
    parser.add_argument(
        "--graph-summary",
        type=Path,
        default=Path("paper/experiments/results/graph_monitor_primary.json"),
    )
    parser.add_argument(
        "--paired-delta",
        type=Path,
        default=Path("paper/experiments/results/reactive_vs_graph_monitor_delta.json"),
    )
    parser.add_argument(
        "--state-summary",
        type=Path,
    )
    parser.add_argument(
        "--reactive-acceptance",
        type=Path,
        default=Path(
            "paper/experiments/results/reactive_monitor_primary_cohort_acceptance.json"
        ),
    )
    parser.add_argument(
        "--graph-acceptance",
        type=Path,
        default=Path(
            "paper/experiments/results/graph_monitor_primary_cohort_acceptance.json"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("paper/assets/tables/graph_monitor_manuscript_results.md"),
    )
    parser.add_argument("--manuscript", type=Path, default=Path("paper/draft/main.md"))
    args = parser.parse_args()
    try:
        write_table(args)
    except ResultsPending as error:
        parser.exit(2, f"pending: {error}\n")


if __name__ == "__main__":
    main()
