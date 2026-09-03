#!/usr/bin/env python3
"""Render an accepted Ottawa P2-E8 result into Paper 2.

The consumer is provider-free and reads only the frozen cross-dataset
protocol, the accepted analyzer result, and the active manuscript.  It
revalidates the complete Ottawa cohort, target-adverse window accounting,
displayed Graph-minus-Reactive arithmetic, and registered bootstrap metadata
before updating the table, SVG, and manuscript marker as one write group.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import re
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for _source in (ROOT, ROOT / "src"):
    if str(_source) not in sys.path:
        sys.path.insert(0, str(_source))

from scripts.analyze_graph_cross_dataset_replay import (  # noqa: E402
    REPLAY_POLICY_ID,
    RESULT_SCHEMA,
    TASK_ID,
)
from scripts.schedule_graph_cross_dataset_replay import (  # noqa: E402
    ContractError,
    DATASET_ID,
    DEFAULT_PROTOCOL,
    PROFILE_ID,
    PROTOCOL_ID,
    load_protocol,
    validate_protocol,
)


DEFAULT_RESULT = (
    ROOT
    / "paper/experiments/results/graph_cross_dataset_replay_v3"
    / "paper2-cross-dataset-ottawa-generic-v1/formal_result.json"
)
DEFAULT_TABLE = ROOT / "paper/assets/tables/p2_e8_ottawa_results.md"
DEFAULT_FIGURE = ROOT / "paper/assets/figures/p2_e8_ottawa_primary.svg"
DEFAULT_MANUSCRIPT = ROOT / "paper/draft/main.md"

MANUSCRIPT_BEGIN = "<!-- P2_E8_OTTAWA:BEGIN -->"
MANUSCRIPT_END = "<!-- P2_E8_OTTAWA:END -->"
FORMAL_STAMP = re.compile(r"^[0-9]{8}T[0-9]{6}Z$")

EXPECTED_RUNS_PER_ARM = 9
EXPECTED_EPISODES_PER_ARM = 36
EXPECTED_EPISODES = 72
EXPECTED_PAIRS = 36
EXPECTED_WINDOWS_PER_ARM = 108
EXPECTED_BEARINGS = 12

DISPLAY_METRICS = (
    ("task.average_precision", "Target-adverse Average Precision", "Task primary"),
    ("task.auroc", "AUROC", "Task secondary"),
    ("task.false_alarm_rate", "False-alarm rate", "Task secondary"),
    ("task.true_positive_rate", "True-positive rate", "Task secondary"),
    ("task.score_coverage", "Score coverage", "Task secondary"),
)


class CrossDatasetResultsPending(RuntimeError):
    """Raised before output when P2-E8 evidence is absent or inconsistent."""


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise CrossDatasetResultsPending(f"missing {label}: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise CrossDatasetResultsPending(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise CrossDatasetResultsPending(f"{label} must be a JSON object")
    return value


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CrossDatasetResultsPending(f"{label} must be an object")
    return dict(value)


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise CrossDatasetResultsPending(
            f"{label} keys drifted: missing={sorted(expected - observed)}, "
            f"extra={sorted(observed - expected)}"
        )


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise CrossDatasetResultsPending(f"{label} must be an integer >= {minimum}")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CrossDatasetResultsPending(f"{label} must be finite numeric")
    number = float(value)
    if not math.isfinite(number):
        raise CrossDatasetResultsPending(f"{label} must be finite numeric")
    return number


def _bounded(value: Any, label: str, *, low: float, high: float) -> float:
    number = _finite(value, label)
    if number < low - 1e-12 or number > high + 1e-12:
        raise CrossDatasetResultsPending(
            f"{label} must be within [{low}, {high}]"
        )
    return number


def _same_number(observed: Any, expected: float, label: str) -> None:
    number = _finite(observed, label)
    if not math.isclose(number, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise CrossDatasetResultsPending(
            f"{label} arithmetic drifted: observed={number}, expected={expected}"
        )


def _interval(
    value: Any,
    label: str,
    *,
    low: float,
    high: float,
) -> list[float]:
    if not isinstance(value, list) or len(value) != 2:
        raise CrossDatasetResultsPending(f"{label} must contain two bounds")
    lower = _bounded(value[0], f"{label}.lower", low=low, high=high)
    upper = _bounded(value[1], f"{label}.upper", low=low, high=high)
    if lower > upper:
        raise CrossDatasetResultsPending(f"{label} bounds are reversed")
    return [lower, upper]


def _validate_consumer_registration(protocol: Mapping[str, Any]) -> None:
    try:
        validate_protocol(protocol)
    except ContractError as exc:
        raise CrossDatasetResultsPending("P2-E8 protocol validation failed") from exc
    analysis_gate = _mapping(protocol.get("analysis_gate"), "analysis_gate")
    consumer = _mapping(
        analysis_gate.get("accepted_manuscript_consumer"),
        "analysis_gate.accepted_manuscript_consumer",
    )
    expected = {
        "entrypoint": "scripts/render_graph_cross_dataset_manuscript.py",
        "accepted_result": (
            "paper/experiments/results/graph_cross_dataset_replay_v3/"
            "paper2-cross-dataset-ottawa-generic-v1/formal_result.json"
        ),
        "complete_episode_bundles_required": EXPECTED_EPISODES,
        "matched_pairs_required": EXPECTED_PAIRS,
        "assigned_windows_per_arm_required": EXPECTED_WINDOWS_PER_ARM,
        "raw_run_or_private_data_reads": False,
        "provider_calls": False,
        "displayed_paired_arithmetic_recomputed": True,
        "bootstrap_metadata_rechecked": True,
        "write_contract": "grouped_replace_with_exception_rollback",
        "focused_tests": "tests/test_render_graph_cross_dataset_manuscript.py",
    }
    if consumer != expected:
        raise CrossDatasetResultsPending(
            "P2-E8 accepted-result consumer registration drifted"
        )


def _validate_acceptance(value: Any) -> None:
    acceptance = _mapping(value, "P2-E8 embedded acceptance")
    _exact_keys(
        acceptance,
        {
            "reactive",
            "graph",
            "matched_world_contract",
            "exact_episode_pairing",
        },
        "P2-E8 embedded acceptance",
    )
    for arm in ("reactive", "graph"):
        report = _mapping(acceptance[arm], f"P2-E8 {arm} acceptance")
        _exact_keys(report, {"accepted", "runs", "episodes", "errors"}, f"P2-E8 {arm} acceptance")
        if report["accepted"] is not True:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} gate is not accepted")
        if _integer(report["runs"], f"P2-E8 {arm} accepted runs") != EXPECTED_RUNS_PER_ARM:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} run denominator drifted")
        if _integer(report["episodes"], f"P2-E8 {arm} accepted episodes") != EXPECTED_EPISODES_PER_ARM:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} episode denominator drifted")
        if report["errors"] != []:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} acceptance contains errors")
    if acceptance["matched_world_contract"] != "accepted":
        raise CrossDatasetResultsPending("P2-E8 matched-world gate is not accepted")
    if acceptance["exact_episode_pairing"] != "accepted":
        raise CrossDatasetResultsPending("P2-E8 exact-pairing gate is not accepted")


def _validate_denominators(value: Any) -> dict[str, dict[str, int]]:
    denominators = _mapping(value, "P2-E8 denominators")
    _exact_keys(
        denominators,
        {"reactive", "graph", "matched_episode_pairs"},
        "P2-E8 denominators",
    )
    if _integer(denominators["matched_episode_pairs"], "P2-E8 matched pairs") != EXPECTED_PAIRS:
        raise CrossDatasetResultsPending("P2-E8 matched-pair denominator drifted")
    result: dict[str, dict[str, int]] = {}
    for arm in ("reactive", "graph"):
        report = _mapping(denominators[arm], f"P2-E8 {arm} denominators")
        _exact_keys(
            report,
            {
                "runs",
                "episode_bundles",
                "assigned_windows",
                "physical_bearing_clusters",
                "nonprovider_terminal_failures_retained",
            },
            f"P2-E8 {arm} denominators",
        )
        parsed = {key: _integer(item, f"P2-E8 {arm}.{key}") for key, item in report.items()}
        expected = {
            "runs": EXPECTED_RUNS_PER_ARM,
            "episode_bundles": EXPECTED_EPISODES_PER_ARM,
            "assigned_windows": EXPECTED_WINDOWS_PER_ARM,
            "physical_bearing_clusters": EXPECTED_BEARINGS,
        }
        for key, expected_value in expected.items():
            if parsed[key] != expected_value:
                raise CrossDatasetResultsPending(f"P2-E8 {arm} {key} denominator drifted")
        if parsed["nonprovider_terminal_failures_retained"] > EXPECTED_EPISODES_PER_ARM:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} retained-failure count drifted")
        result[arm] = parsed
    return result


def _validate_arm_summary(value: Any, *, arm: str) -> dict[str, float]:
    arm_summary = _mapping(value, f"P2-E8 {arm} arm summary")
    _exact_keys(arm_summary, {TASK_ID}, f"P2-E8 {arm} task set")
    task_summary = _mapping(arm_summary[TASK_ID], f"P2-E8 {arm} monitoring summary")
    _exact_keys(
        task_summary,
        {"episodes", "bearings", "rollout", "evaluation_contract", "task"},
        f"P2-E8 {arm} monitoring summary",
    )
    if _integer(task_summary["episodes"], f"P2-E8 {arm} episodes") != EXPECTED_EPISODES_PER_ARM:
        raise CrossDatasetResultsPending(f"P2-E8 {arm} summary episode denominator drifted")
    if _integer(task_summary["bearings"], f"P2-E8 {arm} bearings") != EXPECTED_BEARINGS:
        raise CrossDatasetResultsPending(f"P2-E8 {arm} bearing denominator drifted")
    _mapping(task_summary["rollout"], f"P2-E8 {arm} rollout summary")
    expected_contract = {
        "missing_assigned_score_policy_id": REPLAY_POLICY_ID,
        "population": "all_protocol_assigned_replay_windows",
        "partial_decision_source": "canonical_successful_submit_prefix",
        "missing_positive": "zero_ap_contribution_and_normal_miss",
        "missing_negative": "above_submitted_ranks_and_anomaly_false_alarm",
        "target_visibility": "evaluator_only",
    }
    if _mapping(task_summary["evaluation_contract"], f"P2-E8 {arm} evaluation contract") != expected_contract:
        raise CrossDatasetResultsPending(f"P2-E8 {arm} target-adverse contract drifted")
    task = _mapping(task_summary["task"], f"P2-E8 {arm} task metrics")
    _exact_keys(
        task,
        {
            "submission",
            "average_precision",
            "auroc",
            "cohort_prevalence",
            "submitted_prevalence",
            "false_alarm_rate",
            "true_positive_rate",
            "assigned_windows",
            "submitted_windows",
            "missing_assigned_scores",
            "score_coverage",
        },
        f"P2-E8 {arm} task metrics",
    )
    assigned = _integer(task["assigned_windows"], f"P2-E8 {arm} assigned windows")
    submitted = _integer(task["submitted_windows"], f"P2-E8 {arm} submitted windows")
    missing = _integer(task["missing_assigned_scores"], f"P2-E8 {arm} missing windows")
    if assigned != EXPECTED_WINDOWS_PER_ARM or submitted > assigned or missing != assigned - submitted:
        raise CrossDatasetResultsPending(f"P2-E8 {arm} assigned-window accounting drifted")
    _same_number(task["score_coverage"], submitted / assigned, f"P2-E8 {arm} score coverage")
    _same_number(task["cohort_prevalence"], 2.0 / 3.0, f"P2-E8 {arm} cohort prevalence")
    if task["submitted_prevalence"] is not None:
        _bounded(task["submitted_prevalence"], f"P2-E8 {arm} submitted prevalence", low=0.0, high=1.0)
    _bounded(task["submission"], f"P2-E8 {arm} submission rate", low=0.0, high=1.0)
    return {
        metric: _bounded(
            task[metric.removeprefix("task.")],
            f"P2-E8 {arm} {metric}",
            low=0.0,
            high=1.0,
        )
        for metric, _label, _role in DISPLAY_METRICS
    }


def _validate_arm_bootstrap(
    value: Any,
    *,
    arm: str,
    iterations: int,
) -> None:
    report = _mapping(value, f"P2-E8 {arm} bootstrap")
    _exact_keys(report, {"interval_95ci", "valid_replicates"}, f"P2-E8 {arm} bootstrap")
    intervals = _mapping(report["interval_95ci"], f"P2-E8 {arm} intervals")
    valid = _mapping(report["valid_replicates"], f"P2-E8 {arm} valid replicates")
    _exact_keys(intervals, {TASK_ID}, f"P2-E8 {arm} interval task set")
    _exact_keys(valid, {TASK_ID}, f"P2-E8 {arm} replicate task set")
    task_intervals = _mapping(intervals[TASK_ID], f"P2-E8 {arm} task intervals")
    task_valid = _mapping(valid[TASK_ID], f"P2-E8 {arm} task valid replicates")
    for metric, _label, _role in DISPLAY_METRICS:
        if metric not in task_intervals or metric not in task_valid:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} bootstrap lacks {metric}")
        if _integer(task_valid[metric], f"P2-E8 {arm} {metric} valid replicates") != iterations:
            raise CrossDatasetResultsPending(f"P2-E8 {arm} {metric} bootstrap is incomplete")
        _interval(task_intervals[metric], f"P2-E8 {arm} {metric} interval", low=0.0, high=1.0)


def _validate_paired(
    value: Any,
    *,
    arms: Mapping[str, Mapping[str, float]],
    iterations: int,
) -> dict[str, dict[str, Any]]:
    paired = _mapping(value, "P2-E8 paired result")
    _exact_keys(
        paired,
        {
            "estimate",
            "bearing_bootstrap_95ci",
            "bearing_bootstrap_valid_replicates",
            "bootstrap_iterations",
            "seed",
            "direction",
        },
        "P2-E8 paired result",
    )
    if _integer(paired["bootstrap_iterations"], "P2-E8 bootstrap iterations") != iterations:
        raise CrossDatasetResultsPending("P2-E8 paired bootstrap iteration drifted")
    if _integer(paired["seed"], "P2-E8 bootstrap seed") != 20260902:
        raise CrossDatasetResultsPending("P2-E8 paired bootstrap seed drifted")
    if paired["direction"] != "treatment_minus_control":
        raise CrossDatasetResultsPending("P2-E8 paired direction drifted")
    estimates = _mapping(paired["estimate"], "P2-E8 paired estimates")
    intervals = _mapping(paired["bearing_bootstrap_95ci"], "P2-E8 paired intervals")
    valid = _mapping(
        paired["bearing_bootstrap_valid_replicates"],
        "P2-E8 paired valid replicates",
    )
    for report, label in (
        (estimates, "estimate"),
        (intervals, "interval"),
        (valid, "replicate"),
    ):
        _exact_keys(report, {TASK_ID}, f"P2-E8 paired {label} task set")
    task_estimates = _mapping(estimates[TASK_ID], "P2-E8 task paired estimates")
    task_intervals = _mapping(intervals[TASK_ID], "P2-E8 task paired intervals")
    task_valid = _mapping(valid[TASK_ID], "P2-E8 task paired valid replicates")
    rows: dict[str, dict[str, Any]] = {}
    for metric, _label, _role in DISPLAY_METRICS:
        if metric not in task_estimates or metric not in task_intervals or metric not in task_valid:
            raise CrossDatasetResultsPending(f"P2-E8 paired output lacks {metric}")
        expected = arms["graph"][metric] - arms["reactive"][metric]
        _same_number(task_estimates[metric], expected, f"P2-E8 paired {metric}")
        if _integer(task_valid[metric], f"P2-E8 paired {metric} valid replicates") != iterations:
            raise CrossDatasetResultsPending(f"P2-E8 paired {metric} bootstrap is incomplete")
        rows[metric] = {
            "delta": expected,
            "interval": _interval(
                task_intervals[metric],
                f"P2-E8 paired {metric} interval",
                low=-1.0,
                high=1.0,
            ),
            "valid_replicates": iterations,
        }
    if "task.assigned_windows" not in task_estimates:
        raise CrossDatasetResultsPending("P2-E8 paired output lacks assigned-window delta")
    _same_number(task_estimates["task.assigned_windows"], 0.0, "P2-E8 assigned-window delta")
    return rows


def validate_cross_dataset_inputs(
    *,
    protocol: Mapping[str, Any],
    result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Validate accepted P2-E8 artifacts and return five display rows."""

    try:
        _validate_consumer_registration(protocol)
        _exact_keys(
            result,
            {
                "schema_version",
                "status",
                "evidence_class",
                "result_role",
                "protocol_id",
                "dataset_id",
                "dataset_protocol_id",
                "experiment_profile_id",
                "formal_run_stamp",
                "provider_calls_made_by_analyzer",
                "private_assignment_validation",
                "acceptance",
                "analysis",
                "reporting_boundary",
            },
            "P2-E8 result",
        )
        expected_identity = {
            "schema_version": RESULT_SCHEMA,
            "status": "accepted",
            "evidence_class": "formal",
            "result_role": "confirmatory",
            "protocol_id": PROTOCOL_ID,
            "dataset_id": DATASET_ID,
            "dataset_protocol_id": protocol["dataset_registration"]["dataset_protocol_id"],
            "experiment_profile_id": PROFILE_ID,
            "private_assignment_validation": "phase1_registered_data_port_assignment_v1",
        }
        for key, expected in expected_identity.items():
            if result.get(key) != expected:
                raise CrossDatasetResultsPending(f"P2-E8 result identity drifted at {key}")
        stamp = result.get("formal_run_stamp")
        if not isinstance(stamp, str) or FORMAL_STAMP.fullmatch(stamp) is None:
            raise CrossDatasetResultsPending("P2-E8 formal run stamp drifted")
        if type(result.get("provider_calls_made_by_analyzer")) is not int or result["provider_calls_made_by_analyzer"] != 0:
            raise CrossDatasetResultsPending("P2-E8 analyzer provider-call boundary drifted")
        _validate_acceptance(result["acceptance"])
        expected_reporting = {
            "dataset_pooling": "Ottawa_only",
            "public_condition_event": "absent",
            "event_f1": "N/A",
            "detection_delay": "N/A",
            "monitor_or_revise_event_branch_transfer": "not_an_estimand",
        }
        if _mapping(result["reporting_boundary"], "P2-E8 reporting boundary") != expected_reporting:
            raise CrossDatasetResultsPending("P2-E8 reporting boundary drifted")

        analysis = _mapping(result["analysis"], "P2-E8 analysis")
        _exact_keys(
            analysis,
            {
                "denominators",
                "target_adverse_metric_policy_id",
                "arm_summaries",
                "arm_bearing_bootstrap",
                "paired_graph_minus_reactive",
                "primary_endpoint",
            },
            "P2-E8 analysis",
        )
        _validate_denominators(analysis["denominators"])
        if analysis["target_adverse_metric_policy_id"] != REPLAY_POLICY_ID:
            raise CrossDatasetResultsPending("P2-E8 missing-score policy drifted")
        summaries = _mapping(analysis["arm_summaries"], "P2-E8 arm summaries")
        bootstraps = _mapping(analysis["arm_bearing_bootstrap"], "P2-E8 arm bootstraps")
        _exact_keys(summaries, {"reactive", "graph"}, "P2-E8 arm summaries")
        _exact_keys(bootstraps, {"reactive", "graph"}, "P2-E8 arm bootstraps")
        arms = {
            arm: _validate_arm_summary(summaries[arm], arm=arm)
            for arm in ("reactive", "graph")
        }
        iterations = int(protocol["analysis_gate"]["statistics"]["iterations"])
        for arm in ("reactive", "graph"):
            _validate_arm_bootstrap(bootstraps[arm], arm=arm, iterations=iterations)
        paired = _validate_paired(
            analysis["paired_graph_minus_reactive"],
            arms=arms,
            iterations=iterations,
        )
        primary = _mapping(analysis["primary_endpoint"], "P2-E8 primary endpoint")
        _exact_keys(
            primary,
            {"name", "estimate", "bearing_cluster_bootstrap_95ci", "valid_replicates"},
            "P2-E8 primary endpoint",
        )
        primary_metric = DISPLAY_METRICS[0][0]
        if primary["name"] != protocol["analysis_gate"]["statistics"]["primary_endpoint"]:
            raise CrossDatasetResultsPending("P2-E8 primary endpoint name drifted")
        _same_number(primary["estimate"], paired[primary_metric]["delta"], "P2-E8 primary estimate")
        if primary["bearing_cluster_bootstrap_95ci"] != paired[primary_metric]["interval"]:
            raise CrossDatasetResultsPending("P2-E8 primary interval drifted")
        if _integer(primary["valid_replicates"], "P2-E8 primary valid replicates") != iterations:
            raise CrossDatasetResultsPending("P2-E8 primary bootstrap is incomplete")
    except CrossDatasetResultsPending:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise CrossDatasetResultsPending("P2-E8 artifact structure drifted") from exc

    return [
        {
            "metric": metric,
            "label": label,
            "role": role,
            "reactive": arms["reactive"][metric],
            "graph": arms["graph"][metric],
            **paired[metric],
        }
        for metric, label, role in DISPLAY_METRICS
    ]


def _format_number(value: Any, *, signed: bool = False) -> str:
    number = _finite(value, "display value")
    return f"{number:+.4f}" if signed else f"{number:.4f}"


def render_table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# Accepted P2-E8 Ottawa replay results",
        "",
        "| Endpoint | Role | Reactive | Graph | Graph - Reactive [95% bearing-bootstrap CI] | Valid replicates |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        interval = row["interval"]
        effect = (
            f"{_format_number(row['delta'], signed=True)} "
            f"[{_format_number(interval[0], signed=True)}, "
            f"{_format_number(interval[1], signed=True)}]"
        )
        lines.append(
            f"| {row['label']} | {row['role']} | "
            f"{_format_number(row['reactive'])} | {_format_number(row['graph'])} | "
            f"{effect} | {row['valid_replicates']}/2000 |"
        )
    lines.extend(
        [
            "",
            "Ottawa is reported alone: 36 exact matched episode pairs, 108 assigned windows per arm, and 12 physical-bearing clusters. Missing decisions remain in the target-adverse denominator. The source states are evaluator-private window targets, not a public condition event; event-F1, detection delay, and Monitor/Revise event-branch transfer remain N/A or outside this estimand.",
            "",
        ]
    )
    return "\n".join(lines)


def render_svg(rows: Sequence[Mapping[str, Any]]) -> str:
    width = 1020
    left = 315
    right = 65
    top = 76
    row_height = 54
    height = top + row_height * len(rows) + 76
    plot_width = width - left - right

    def x(value: float) -> float:
        return left + ((value + 1.0) / 2.0) * plot_width

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Accepted P2-E8 Ottawa Graph-minus-Reactive contrasts</title>',
        '<desc id="desc">Five task-primary and secondary Ottawa replay contrasts with registered physical-bearing bootstrap intervals.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Inter,Arial,sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.label{font-size:14px}.tick{font-size:12px;fill:#596579}.ci{stroke:#5b4bb7;stroke-width:3}.point{fill:#0b7a75;stroke:#fff;stroke-width:1.5}.zero{stroke:#8591a3;stroke-width:1.5;stroke-dasharray:5 4}.grid{stroke:#e1e6ee;stroke-width:1}</style>',
        '<text class="title" x="24" y="34">P2-E8 Ottawa Graph - Reactive task contrasts</text>',
        '<text class="tick" x="24" y="56">Ottawa-only task endpoints; 95% physical-bearing bootstrap CI</text>',
    ]
    for tick in (-1.0, -0.5, 0.0, 0.5, 1.0):
        tick_x = x(tick)
        css = "zero" if tick == 0.0 else "grid"
        parts.append(
            f'<line class="{css}" x1="{tick_x:.2f}" y1="{top - 18}" x2="{tick_x:.2f}" y2="{height - 46}"/>'
        )
        parts.append(
            f'<text class="tick" x="{tick_x:.2f}" y="{height - 23}" text-anchor="middle">{tick:+.1f}</text>'
        )
    for index, row in enumerate(rows):
        y = top + index * row_height
        interval = row["interval"]
        parts.append(
            f'<text class="label" x="24" y="{y + 5}">{html.escape(str(row["label"]))}</text>'
        )
        parts.append(
            f'<line class="ci" x1="{x(float(interval[0])):.2f}" y1="{y}" x2="{x(float(interval[1])):.2f}" y2="{y}"/>'
        )
        parts.append(
            f'<circle class="point" cx="{x(float(row["delta"])):.2f}" cy="{y}" r="5.5"/>'
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def _replace_block(source: str, content: str) -> str:
    if source.count(MANUSCRIPT_BEGIN) != 1 or source.count(MANUSCRIPT_END) != 1:
        raise CrossDatasetResultsPending(
            "active manuscript needs one unique P2-E8 Ottawa marker pair"
        )
    prefix, remainder = source.split(MANUSCRIPT_BEGIN, 1)
    _old, suffix = remainder.split(MANUSCRIPT_END, 1)
    return (
        f"{prefix}{MANUSCRIPT_BEGIN}\n\n{content.rstrip()}\n\n"
        f"{MANUSCRIPT_END}{suffix}"
    )


def render_manuscript_block(
    rows: Sequence[Mapping[str, Any]], *, figure_name: str
) -> str:
    table_body = render_table(rows).split("\n", 2)[2]
    return "\n".join(
        [
            "The P2-E8 gate accepted all 72 registered Ottawa episode bundles and 36 exact Graph--Reactive pairs, retaining 108 assigned windows per arm across 12 physical-bearing clusters. The table reports the registered task-primary and secondary window-level outcomes without pooling Ottawa with Paderborn or interpreting evaluator-private source states as a public condition event. All estimates are retained regardless of direction.",
            "",
            table_body.rstrip(),
            "",
            f"![Accepted P2-E8 Ottawa task contrasts](../assets/figures/{figure_name})",
        ]
    ) + "\n"


def _restore(path: Path, original: bytes | None) -> None:
    if original is None:
        if path.exists():
            path.unlink()
        return
    path.write_bytes(original)


def _write_group_with_exception_rollback(contents: Mapping[Path, str]) -> None:
    originals = {path: path.read_bytes() if path.exists() else None for path in contents}
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
            os.replace(temporary_path, path)
            replaced.append(path)
    except Exception:
        for path in reversed(replaced):
            _restore(path, originals[path])
        raise
    finally:
        for temporary_path in temporary.values():
            if temporary_path.exists():
                temporary_path.unlink()


def write_cross_dataset_manuscript(
    *,
    protocol_path: Path,
    result_path: Path,
    table_path: Path,
    figure_path: Path,
    manuscript_path: Path,
) -> dict[str, Any]:
    try:
        protocol = load_protocol(protocol_path)
    except ContractError as exc:
        raise CrossDatasetResultsPending("cannot load P2-E8 protocol") from exc
    result = _load_json(result_path, "P2-E8 result")
    rows = validate_cross_dataset_inputs(protocol=protocol, result=result)
    if not manuscript_path.is_file():
        raise CrossDatasetResultsPending(f"missing active manuscript: {manuscript_path}")
    source = manuscript_path.read_text(encoding="utf-8")
    table = render_table(rows)
    figure = render_svg(rows)
    manuscript = _replace_block(
        source,
        render_manuscript_block(rows, figure_name=figure_path.name),
    )
    _write_group_with_exception_rollback(
        {table_path: table, figure_path: figure, manuscript_path: manuscript}
    )
    return {
        "schema_version": "p2_e8_ottawa_manuscript_render_v1",
        "status": "accepted_p2_e8_inserted",
        "registered_rows": len(rows),
        "formal_episode_bundles": EXPECTED_EPISODES,
        "matched_pairs": EXPECTED_PAIRS,
        "assigned_windows_per_arm": EXPECTED_WINDOWS_PER_ARM,
        "provider_calls_performed_by_renderer": False,
        "raw_run_or_private_data_reads_performed_by_renderer": False,
        "table": str(table_path),
        "figure": str(figure_path),
        "manuscript": str(manuscript_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an accepted P2-E8 Ottawa result into Paper 2."
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    args = parser.parse_args(argv)
    summary = write_cross_dataset_manuscript(
        protocol_path=args.protocol,
        result_path=args.result,
        table_path=args.table,
        figure_path=args.figure,
        manuscript_path=args.manuscript,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
