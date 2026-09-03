#!/usr/bin/env python3
"""Render an accepted P2-E9 reliability result into Paper 2.

This provider-free consumer reads only the frozen protocol, acceptance report,
analysis result, and active manuscript.  It validates the displayed n=10 task,
reliability, and cost arithmetic before updating the table, SVG, and manuscript
block as one write group.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import statistics
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
for _source in (ROOT, ROOT / "src"):
    if str(_source) not in sys.path:
        sys.path.insert(0, str(_source))

from scripts.analyze_graph_reliability import (
    ACCEPTANCE_SCHEMA_VERSION,
    ARMS,
    PRIMARY_METRIC,
    REPLAY_MISSING_SCORE_POLICY_ID,
    RESULT_SCHEMA_VERSION,
    load_graph_reliability_protocol,
    validate_graph_reliability_acceptance,
)
from scripts.schedule_graph_reliability import expected_run_directories


DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_reliability_protocol_v2.yaml"
DEFAULT_RESULT_ROOT = (
    ROOT
    / "paper/experiments/results/graph_reliability_v2"
    / "graph_reliability_generic_n10_v2"
)
DEFAULT_RESULT = DEFAULT_RESULT_ROOT / "formal_result.json"
DEFAULT_ACCEPTANCE = DEFAULT_RESULT_ROOT / "formal_acceptance.json"
DEFAULT_TABLE = ROOT / "paper/assets/tables/p2_e9_reliability_results.md"
DEFAULT_FIGURE = ROOT / "paper/assets/figures/p2_e9_reliability_primary.svg"
DEFAULT_MANUSCRIPT = ROOT / "paper/draft/main.md"

MANUSCRIPT_BEGIN = "<!-- P2_E9_RELIABILITY:BEGIN -->"
MANUSCRIPT_END = "<!-- P2_E9_RELIABILITY:END -->"

EXPECTED_REPEATS = 10
EXPECTED_SEQUENCES = 8
EXPECTED_EPISODES_PER_ARM = 80
EXPECTED_EPISODES = 160
EXPECTED_PAIRS = 80
EXPECTED_WINDOWS_PER_ARM = 240

SELECTED_METRICS = (
    "rollout.repeated_action_ratio",
    "rollout.budget_exhaustion",
    "rollout.llm_turns",
    "rollout.total_tokens",
    "rollout.estimated_model_cost_usd",
)


class ReliabilityResultsPending(RuntimeError):
    """Raised when P2-E9 inputs are absent, rejected, or inconsistent."""


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
        raise ReliabilityResultsPending(f"missing {label}: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ReliabilityResultsPending(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ReliabilityResultsPending(f"{label} must be a JSON object")
    return value


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise ReliabilityResultsPending(f"{label} must be an object")
    return dict(value)


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise ReliabilityResultsPending(
            f"{label} keys drifted: missing={sorted(expected - observed)}, "
            f"extra={sorted(observed - expected)}"
        )


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise ReliabilityResultsPending(f"{label} must be an integer >= {minimum}")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReliabilityResultsPending(f"{label} must be finite numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ReliabilityResultsPending(f"{label} must be finite numeric")
    return number


def _optional_number(
    value: Any,
    label: str,
    *,
    lower: float | None = None,
    upper: float | None = None,
) -> float | None:
    if value is None:
        return None
    number = _finite(value, label)
    if lower is not None and number < lower - 1e-12:
        raise ReliabilityResultsPending(f"{label} is below {lower}")
    if upper is not None and number > upper + 1e-12:
        raise ReliabilityResultsPending(f"{label} is above {upper}")
    return number


def _same_number(observed: Any, expected: float | None, label: str) -> None:
    if expected is None:
        if observed is not None:
            raise ReliabilityResultsPending(f"{label} must be N/A")
        return
    number = _finite(observed, label)
    if not math.isclose(number, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise ReliabilityResultsPending(
            f"{label} arithmetic drifted: observed={number}, expected={expected}"
        )


def _validate_count_map(
    value: Any, label: str, *, expected_total: int | None = None
) -> dict[str, int]:
    counts = _mapping(value, label)
    if any(not isinstance(key, str) or not key for key in counts):
        raise ReliabilityResultsPending(f"{label} has an invalid key")
    result = {
        key: _integer(item, f"{label}.{key}") for key, item in counts.items()
    }
    if expected_total is not None and sum(result.values()) != expected_total:
        raise ReliabilityResultsPending(
            f"{label} totals {sum(result.values())}; expected {expected_total}"
        )
    return result


def _expected_repeat_ids(protocol: Mapping[str, Any]) -> list[str]:
    return [str(item["repeat_id"]) for item in protocol["cohort"]["repeats"]]


def _validate_interval(
    value: Any,
    *,
    label: str,
    valid_replicates: int,
    lower: float | None = None,
    upper: float | None = None,
) -> list[float] | None:
    if valid_replicates == 0:
        if value is not None:
            raise ReliabilityResultsPending(f"{label} must be N/A with zero replicates")
        return None
    if not isinstance(value, list) or len(value) != 2:
        raise ReliabilityResultsPending(f"{label} must have two bounds")
    low = _finite(value[0], f"{label}.lower")
    high = _finite(value[1], f"{label}.upper")
    if low > high:
        raise ReliabilityResultsPending(f"{label} bounds are reversed")
    if lower is not None and low < lower - 1e-12:
        raise ReliabilityResultsPending(f"{label} is below {lower}")
    if upper is not None and high > upper + 1e-12:
        raise ReliabilityResultsPending(f"{label} is above {upper}")
    return [low, high]


def _validate_inclusion(value: Any) -> dict[str, Any]:
    inclusion = _mapping(value, "canonical inclusion")
    _exact_keys(
        inclusion,
        {
            "canonical_non_provider_terminal_count",
            "matched_pair_count",
            "retained_provider_failure_attempt_count",
            "non_provider_failures_retained",
            "terminal_status_counts",
            "failure_kind_counts",
        },
        "canonical inclusion",
    )
    if inclusion.get("canonical_non_provider_terminal_count") != EXPECTED_EPISODES:
        raise ReliabilityResultsPending("P2-E9 inclusion is not 160/160")
    if inclusion.get("matched_pair_count") != EXPECTED_PAIRS:
        raise ReliabilityResultsPending("P2-E9 inclusion is not 80/80 paired")
    _integer(
        inclusion.get("retained_provider_failure_attempt_count"),
        "retained provider failures",
    )
    retained = _integer(
        inclusion.get("non_provider_failures_retained"),
        "retained non-provider failures",
    )
    if retained > EXPECTED_EPISODES:
        raise ReliabilityResultsPending("retained failures exceed the cohort")
    _validate_count_map(
        inclusion.get("terminal_status_counts"),
        "terminal status counts",
        expected_total=EXPECTED_EPISODES,
    )
    failures = _validate_count_map(
        inclusion.get("failure_kind_counts"), "failure kind counts"
    )
    if sum(failures.values()) != retained:
        raise ReliabilityResultsPending("failure-kind counts disagree with inclusion")
    return inclusion


def _validate_acceptance(
    acceptance: Mapping[str, Any],
    *,
    protocol: Mapping[str, Any],
    output_root: str,
) -> None:
    try:
        validate_graph_reliability_acceptance(
            protocol, acceptance, output_root=output_root
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ReliabilityResultsPending("P2-E9 acceptance did not validate") from exc
    _exact_keys(
        acceptance,
        {
            "schema_version",
            "accepted",
            "experiment_id",
            "protocol_id",
            "cohort_id",
            "reliability_profile_id",
            "output_root",
            "repeat_ids",
            "seeds",
            "primary_cohort_seeds",
            "arms",
            "rotation",
            "public_sequence_ids",
            "expected_episode_bundles",
            "observed_non_provider_terminals",
            "expected_pairs",
            "observed_pairs",
            "registered_run_directories",
            "contract",
            "pooling_with_three_seed_primary",
            "primary_results_ingested",
            "non_provider_failure_policy",
            "provider_calls_performed_by_gate",
            "errors",
            "p2_experiment_id",
            "matched_control_id",
            "canonical_inclusion",
        },
        "P2-E9 acceptance",
    )
    if acceptance.get("schema_version") != ACCEPTANCE_SCHEMA_VERSION:
        raise ReliabilityResultsPending("P2-E9 acceptance schema drifted")
    expected_directories = [
        str(path)
        for path in expected_run_directories(Path(output_root), protocol).values()
    ]
    if acceptance.get("registered_run_directories") != expected_directories:
        raise ReliabilityResultsPending("P2-E9 registered run directories drifted")


def _validate_report_core(
    report: Mapping[str, Any],
    *,
    label: str,
    repeat_ids: Sequence[str],
    bootstrap_iterations: int,
    lower: float | None = None,
    upper: float | None = None,
) -> tuple[dict[str, float | None], float | None]:
    repeat_estimates = _mapping(
        report.get("repeat_estimates"), f"{label}.repeat_estimates"
    )
    if set(repeat_estimates) != set(repeat_ids):
        raise ReliabilityResultsPending(f"{label} repeat set drifted")
    normalized = {
        repeat_id: _optional_number(
            repeat_estimates[repeat_id],
            f"{label}.repeat_estimates.{repeat_id}",
            lower=lower,
            upper=upper,
        )
        for repeat_id in repeat_ids
    }
    defined = [value for value in normalized.values() if value is not None]
    expected_status = "defined" if defined else "not_applicable"
    if report.get("status") != expected_status:
        raise ReliabilityResultsPending(f"{label} status disagrees with repeats")
    if report.get("defined_repeat_numerator") != len(defined):
        raise ReliabilityResultsPending(f"{label} defined-repeat count drifted")
    if report.get("registered_repeat_denominator") != EXPECTED_REPEATS:
        raise ReliabilityResultsPending(f"{label} repeat denominator drifted")
    expected_mean = statistics.fmean(defined) if defined else None
    expected_variance = statistics.variance(defined) if len(defined) > 1 else None
    _same_number(
        report.get("mean_across_registered_repeats"),
        expected_mean,
        f"{label}.mean",
    )
    _same_number(
        report.get("between_repeat_variance"),
        expected_variance,
        f"{label}.variance",
    )
    valid = _integer(
        report.get("bootstrap_valid_replicates"), f"{label}.bootstrap valid"
    )
    if valid > bootstrap_iterations:
        raise ReliabilityResultsPending(f"{label} has too many bootstrap replicates")
    if report.get("bootstrap_replicate_denominator") != bootstrap_iterations:
        raise ReliabilityResultsPending(f"{label} bootstrap denominator drifted")
    _validate_interval(
        report.get("crossed_repeat_sequence_bootstrap_95ci"),
        label=f"{label}.bootstrap CI",
        valid_replicates=valid,
        lower=lower,
        upper=upper,
    )
    return normalized, expected_mean


def _validate_primary_report(
    value: Any,
    *,
    label: str,
    repeat_ids: Sequence[str],
    bootstrap_iterations: int,
    arm: str | None,
) -> dict[str, Any]:
    report = _mapping(value, label)
    expected_keys = {
        "status",
        "role",
        "mean_across_registered_repeats",
        "between_repeat_variance",
        "crossed_repeat_sequence_bootstrap_95ci",
        "repeat_estimates",
        "defined_repeat_numerator",
        "registered_repeat_denominator",
        "assigned_episode_denominator",
        "assigned_window_denominator_per_arm",
        "bootstrap_valid_replicates",
        "bootstrap_replicate_denominator",
        "aggregation",
        "missing_score_policy_id",
        "per_sequence_average_precision_averaging_performed",
        "derived_evaluation_jsonl_ingested",
        "missing_values_imputed_as_zero",
    }
    if arm is not None:
        expected_keys.update(
            {
                "submitted_window_numerator",
                "missing_assigned_scores",
                "score_coverage",
            }
        )
    _exact_keys(report, expected_keys, label)
    expected_static = {
        "role": "primary_task_outcome",
        "assigned_episode_denominator": EXPECTED_EPISODES_PER_ARM,
        "assigned_window_denominator_per_arm": EXPECTED_WINDOWS_PER_ARM,
        "aggregation": (
            "recompute_target_adverse_AP_over_all_24_assigned_windows_within_"
            "each_repeat_then_equal_weight_repeats"
        ),
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "per_sequence_average_precision_averaging_performed": False,
        "derived_evaluation_jsonl_ingested": False,
        "missing_values_imputed_as_zero": False,
    }
    for key, expected in expected_static.items():
        if report.get(key) != expected:
            raise ReliabilityResultsPending(f"{label}.{key} drifted")
    _validate_report_core(
        report,
        label=label,
        repeat_ids=repeat_ids,
        bootstrap_iterations=bootstrap_iterations,
        lower=-1.0 if arm is None else 0.0,
        upper=1.0,
    )
    if arm is not None:
        submitted = _integer(
            report.get("submitted_window_numerator"), f"{label}.submitted windows"
        )
        missing = _integer(
            report.get("missing_assigned_scores"), f"{label}.missing windows"
        )
        if submitted + missing != EXPECTED_WINDOWS_PER_ARM:
            raise ReliabilityResultsPending(f"{label} loses assigned windows")
        _same_number(
            report.get("score_coverage"),
            submitted / EXPECTED_WINDOWS_PER_ARM,
            f"{label}.score coverage",
        )
    return report


def _validate_metric_report(
    value: Any,
    *,
    label: str,
    repeat_ids: Sequence[str],
    bootstrap_iterations: int,
    bounds: tuple[float, float] | None = None,
) -> dict[str, Any]:
    report = _mapping(value, label)
    _exact_keys(
        report,
        {
            "status",
            "mean_across_registered_repeats",
            "between_repeat_variance",
            "crossed_repeat_sequence_bootstrap_95ci",
            "repeat_estimates",
            "defined_repeat_numerator",
            "registered_repeat_denominator",
            "defined_episode_numerator",
            "assigned_episode_denominator",
            "bootstrap_valid_replicates",
            "bootstrap_replicate_denominator",
            "missing_values_imputed_as_zero",
        },
        label,
    )
    if report.get("assigned_episode_denominator") != EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"{label} episode denominator drifted")
    defined_episodes = _integer(
        report.get("defined_episode_numerator"), f"{label}.defined episodes"
    )
    if defined_episodes > EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"{label} defines too many episodes")
    if report.get("missing_values_imputed_as_zero") is not False:
        raise ReliabilityResultsPending(f"{label} permits missing-value imputation")
    lower, upper = bounds if bounds is not None else (None, None)
    _validate_report_core(
        report,
        label=label,
        repeat_ids=repeat_ids,
        bootstrap_iterations=bootstrap_iterations,
        lower=lower,
        upper=upper,
    )
    return report


def _validate_complete_grounded_report(
    report: Mapping[str, Any], *, label: str
) -> None:
    """Require grounded completion to cover every registered episode and repeat."""

    if report.get("defined_episode_numerator") != EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(
            f"{label} must define all {EXPECTED_EPISODES_PER_ARM} assigned episodes"
        )
    if report.get("defined_repeat_numerator") != EXPECTED_REPEATS:
        raise ReliabilityResultsPending(
            f"{label} must define all {EXPECTED_REPEATS} registered repeats"
        )


def _validate_display_delta(
    *, reactive: Any, graph: Any, delta: Any, label: str
) -> None:
    """Bind a displayed paired contrast to its two displayed arm estimates."""

    if reactive is None or graph is None:
        expected = None
    else:
        expected = _finite(graph, f"{label}.graph") - _finite(
            reactive, f"{label}.reactive"
        )
    _same_number(delta, expected, f"{label}.Graph-minus-Reactive")


def _validate_pass_all(
    value: Any, *, label: str, bootstrap_iterations: int
) -> dict[str, Any]:
    report = _mapping(value, label)
    _exact_keys(
        report,
        {
            "numerator",
            "denominator",
            "estimate",
            "required_repeats_per_base_sequence",
            "assigned_repeat_episode_denominator",
            "sequence_cluster_bootstrap_95ci",
            "bootstrap_valid_replicates",
            "bootstrap_replicate_denominator",
            "between_repeat_variance",
            "between_repeat_variance_reason",
        },
        label,
    )
    numerator = _integer(report.get("numerator"), f"{label}.numerator")
    if numerator > EXPECTED_SEQUENCES or report.get("denominator") != EXPECTED_SEQUENCES:
        raise ReliabilityResultsPending(f"{label} sequence denominator drifted")
    if report.get("required_repeats_per_base_sequence") != EXPECTED_REPEATS:
        raise ReliabilityResultsPending(f"{label} repeat requirement drifted")
    if report.get("assigned_repeat_episode_denominator") != EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"{label} episode denominator drifted")
    _same_number(
        report.get("estimate"), numerator / EXPECTED_SEQUENCES, f"{label}.estimate"
    )
    valid = _integer(
        report.get("bootstrap_valid_replicates"), f"{label}.bootstrap valid"
    )
    if valid > bootstrap_iterations or report.get(
        "bootstrap_replicate_denominator"
    ) != bootstrap_iterations:
        raise ReliabilityResultsPending(f"{label} bootstrap metadata drifted")
    _validate_interval(
        report.get("sequence_cluster_bootstrap_95ci"),
        label=f"{label}.bootstrap CI",
        valid_replicates=valid,
        lower=0.0,
        upper=1.0,
    )
    if report.get("between_repeat_variance") is not None or report.get(
        "between_repeat_variance_reason"
    ) != "not_applicable_to_joint_all_10_endpoint":
        raise ReliabilityResultsPending(f"{label} variance semantics drifted")
    return report


def _validate_arm(
    value: Any,
    *,
    arm: str,
    protocol: Mapping[str, Any],
    repeat_ids: Sequence[str],
    metrics: Sequence[str],
    bootstrap_iterations: int,
) -> dict[str, Any]:
    report = _mapping(value, f"arms.{arm}")
    _exact_keys(
        report,
        {
            "assigned_episode_denominator",
            "registered_repeat_denominator",
            "base_sequence_denominator",
            "terminal_status_counts",
            "failure_kind_counts",
            "metrics",
            "reliability",
            "cost",
        },
        f"arms.{arm}",
    )
    if report.get("assigned_episode_denominator") != EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"arms.{arm} denominator drifted")
    if report.get("registered_repeat_denominator") != EXPECTED_REPEATS:
        raise ReliabilityResultsPending(f"arms.{arm} repeat denominator drifted")
    if report.get("base_sequence_denominator") != EXPECTED_SEQUENCES:
        raise ReliabilityResultsPending(f"arms.{arm} sequence denominator drifted")
    _validate_count_map(
        report.get("terminal_status_counts"),
        f"arms.{arm}.terminal counts",
        expected_total=EXPECTED_EPISODES_PER_ARM,
    )
    failures = _validate_count_map(
        report.get("failure_kind_counts"), f"arms.{arm}.failure counts"
    )
    if sum(failures.values()) > EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"arms.{arm} has too many failures")

    metric_reports = _mapping(report.get("metrics"), f"arms.{arm}.metrics")
    if set(metric_reports) != set(metrics):
        raise ReliabilityResultsPending(f"arms.{arm} metric registry drifted")
    for metric in metrics:
        label = f"arms.{arm}.metrics.{metric}"
        if metric == PRIMARY_METRIC:
            _validate_primary_report(
                metric_reports[metric],
                label=label,
                repeat_ids=repeat_ids,
                bootstrap_iterations=bootstrap_iterations,
                arm=arm,
            )
        else:
            bounds = (0.0, 1.0) if metric in {
                "task.completion_adjusted_average_precision",
                "task.auroc",
                "task.false_alarm_rate",
                "task.true_positive_rate",
                "rollout.grounded_completion",
                "rollout.submission_rate",
                "rollout.grounded_recovery_success",
                "rollout.repeated_action_ratio",
                "rollout.budget_exhaustion",
            } else None
            _validate_metric_report(
                metric_reports[metric],
                label=label,
                repeat_ids=repeat_ids,
                bootstrap_iterations=bootstrap_iterations,
                bounds=bounds,
            )
    cost = _mapping(report.get("cost"), f"arms.{arm}.cost")
    cost_metrics = list(protocol["metrics"]["cost_metrics"])
    if set(cost) != set(cost_metrics) or any(
        cost[metric] != metric_reports[metric] for metric in cost_metrics
    ):
        raise ReliabilityResultsPending(f"arms.{arm} cost projection drifted")

    reliability = _mapping(report.get("reliability"), f"arms.{arm}.reliability")
    _exact_keys(
        reliability,
        {"pass_definition", "pass_at_1", "pass_all_10"},
        f"arms.{arm}.reliability",
    )
    if reliability.get("pass_definition") != protocol["pass_rule"]:
        raise ReliabilityResultsPending(f"arms.{arm} pass definition drifted")
    pass_at_1 = _mapping(
        reliability.get("pass_at_1"), f"arms.{arm}.pass_at_1"
    )
    _exact_keys(
        pass_at_1,
        {
            "numerator",
            "denominator",
            "estimate",
            "mean_across_registered_repeats",
            "between_repeat_variance",
            "crossed_repeat_sequence_bootstrap_95ci",
            "bootstrap_valid_replicates",
            "bootstrap_replicate_denominator",
        },
        f"arms.{arm}.pass_at_1",
    )
    numerator = _integer(pass_at_1.get("numerator"), f"arms.{arm}.pass numerator")
    if numerator > EXPECTED_EPISODES_PER_ARM or pass_at_1.get(
        "denominator"
    ) != EXPECTED_EPISODES_PER_ARM:
        raise ReliabilityResultsPending(f"arms.{arm} pass@1 denominator drifted")
    _same_number(
        pass_at_1.get("estimate"),
        numerator / EXPECTED_EPISODES_PER_ARM,
        f"arms.{arm}.pass@1 estimate",
    )
    grounded = metric_reports["rollout.grounded_completion"]
    _validate_complete_grounded_report(
        grounded, label=f"arms.{arm}.metrics.rollout.grounded_completion"
    )
    _same_number(
        pass_at_1.get("estimate"),
        grounded.get("mean_across_registered_repeats"),
        f"arms.{arm}.pass@1 estimate versus grounded repeat mean",
    )
    for key in (
        "mean_across_registered_repeats",
        "between_repeat_variance",
        "crossed_repeat_sequence_bootstrap_95ci",
        "bootstrap_valid_replicates",
        "bootstrap_replicate_denominator",
    ):
        if pass_at_1.get(key) != grounded.get(key):
            raise ReliabilityResultsPending(f"arms.{arm} pass@1 projection drifted")
    _validate_pass_all(
        reliability.get("pass_all_10"),
        label=f"arms.{arm}.pass_all_10",
        bootstrap_iterations=bootstrap_iterations,
    )
    return report


def _validate_paired(
    value: Any,
    *,
    protocol: Mapping[str, Any],
    repeat_ids: Sequence[str],
    metrics: Sequence[str],
    bootstrap_iterations: int,
    arms: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    paired = _mapping(value, "paired_graph_minus_reactive")
    _exact_keys(
        paired,
        {"paired_unit", "metrics", "primary_task_outcome", "pass_at_1_delta", "pass_all_10_delta"},
        "paired_graph_minus_reactive",
    )
    if paired.get("paired_unit") != protocol["matched_contract"]["paired_unit"]:
        raise ReliabilityResultsPending("P2-E9 paired unit drifted")
    reports = _mapping(paired.get("metrics"), "paired metrics")
    if set(reports) != set(metrics):
        raise ReliabilityResultsPending("paired metric registry drifted")
    for metric in metrics:
        label = f"paired.metrics.{metric}"
        if metric == PRIMARY_METRIC:
            _validate_primary_report(
                reports[metric],
                label=label,
                repeat_ids=repeat_ids,
                bootstrap_iterations=bootstrap_iterations,
                arm=None,
            )
        else:
            bounds = (-1.0, 1.0) if metric in {
                "task.completion_adjusted_average_precision",
                "task.auroc",
                "task.false_alarm_rate",
                "task.true_positive_rate",
                "rollout.grounded_completion",
                "rollout.submission_rate",
                "rollout.grounded_recovery_success",
                "rollout.repeated_action_ratio",
                "rollout.budget_exhaustion",
            } else None
            _validate_metric_report(
                reports[metric],
                label=label,
                repeat_ids=repeat_ids,
                bootstrap_iterations=bootstrap_iterations,
                bounds=bounds,
            )

    _validate_complete_grounded_report(
        reports["rollout.grounded_completion"],
        label="paired.metrics.rollout.grounded_completion",
    )

    for metric in (PRIMARY_METRIC, *SELECTED_METRICS, "rollout.grounded_completion"):
        graph_report = arms["graph"]["metrics"][metric]
        reactive_report = arms["reactive"]["metrics"][metric]
        paired_report = reports[metric]
        graph_repeats = graph_report["repeat_estimates"]
        reactive_repeats = reactive_report["repeat_estimates"]
        paired_repeats = paired_report["repeat_estimates"]
        for repeat_id in repeat_ids:
            graph_value = graph_repeats[repeat_id]
            reactive_value = reactive_repeats[repeat_id]
            expected = (
                None
                if graph_value is None or reactive_value is None
                else float(graph_value) - float(reactive_value)
            )
            _same_number(
                paired_repeats[repeat_id],
                expected,
                f"paired {metric} repeat {repeat_id}",
            )

    primary = _mapping(paired.get("primary_task_outcome"), "primary task outcome")
    _exact_keys(
        primary,
        {
            "metric",
            "estimate",
            "between_repeat_variance",
            "crossed_repeat_sequence_bootstrap_95ci",
            "defined_repeat_numerator",
            "registered_repeat_denominator",
            "assigned_pair_denominator",
            "assigned_window_denominator_per_arm",
            "bootstrap_valid_replicates",
            "bootstrap_replicate_denominator",
        },
        "primary task outcome",
    )
    primary_report = reports[PRIMARY_METRIC]
    expected_primary = {
        "metric": PRIMARY_METRIC,
        "estimate": primary_report["mean_across_registered_repeats"],
        "between_repeat_variance": primary_report["between_repeat_variance"],
        "crossed_repeat_sequence_bootstrap_95ci": primary_report[
            "crossed_repeat_sequence_bootstrap_95ci"
        ],
        "defined_repeat_numerator": primary_report["defined_repeat_numerator"],
        "registered_repeat_denominator": EXPECTED_REPEATS,
        "assigned_pair_denominator": EXPECTED_PAIRS,
        "assigned_window_denominator_per_arm": EXPECTED_WINDOWS_PER_ARM,
        "bootstrap_valid_replicates": primary_report["bootstrap_valid_replicates"],
        "bootstrap_replicate_denominator": bootstrap_iterations,
    }
    if primary != expected_primary:
        raise ReliabilityResultsPending("primary task outcome projection drifted")

    pass_delta = _mapping(paired.get("pass_at_1_delta"), "pass@1 delta")
    grounded = reports["rollout.grounded_completion"]
    expected_pass_delta = {
        "role": "explanatory_rollout_reliability",
        "estimate": grounded["mean_across_registered_repeats"],
        "between_repeat_variance": grounded["between_repeat_variance"],
        "crossed_repeat_sequence_bootstrap_95ci": grounded[
            "crossed_repeat_sequence_bootstrap_95ci"
        ],
        "defined_pair_numerator": grounded["defined_episode_numerator"],
        "assigned_pair_denominator": EXPECTED_PAIRS,
        "bootstrap_valid_replicates": grounded["bootstrap_valid_replicates"],
        "bootstrap_replicate_denominator": bootstrap_iterations,
    }
    if pass_delta != expected_pass_delta:
        raise ReliabilityResultsPending("pass@1 delta projection drifted")

    pass_all_delta = _mapping(paired.get("pass_all_10_delta"), "pass-all-10 delta")
    _exact_keys(
        pass_all_delta,
        {
            "estimate",
            "sequence_cluster_bootstrap_95ci",
            "sequence_denominator",
            "bootstrap_valid_replicates",
            "bootstrap_replicate_denominator",
        },
        "pass-all-10 delta",
    )
    graph_all = arms["graph"]["reliability"]["pass_all_10"]
    reactive_all = arms["reactive"]["reliability"]["pass_all_10"]
    _same_number(
        pass_all_delta.get("estimate"),
        float(graph_all["estimate"]) - float(reactive_all["estimate"]),
        "pass-all-10 delta estimate",
    )
    if pass_all_delta.get("sequence_denominator") != EXPECTED_SEQUENCES:
        raise ReliabilityResultsPending("pass-all-10 delta sequence denominator drifted")
    valid = _integer(
        pass_all_delta.get("bootstrap_valid_replicates"),
        "pass-all-10 delta bootstrap valid",
    )
    if valid > bootstrap_iterations or pass_all_delta.get(
        "bootstrap_replicate_denominator"
    ) != bootstrap_iterations:
        raise ReliabilityResultsPending("pass-all-10 delta bootstrap drifted")
    _validate_interval(
        pass_all_delta.get("sequence_cluster_bootstrap_95ci"),
        label="pass-all-10 delta CI",
        valid_replicates=valid,
        lower=-1.0,
        upper=1.0,
    )
    return paired


def validate_reliability_inputs(
    *,
    protocol: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    result: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Validate accepted P2-E9 artifacts and return the display rows."""

    try:
        consumer = _mapping(
            protocol.get("execution", {}).get("accepted_manuscript_consumer"),
            "P2-E9 accepted manuscript consumer",
        )
        if (
            consumer.get("write_contract")
            != "grouped_replace_with_exception_rollback"
        ):
            raise ReliabilityResultsPending("P2-E9 manuscript write contract drifted")
        _exact_keys(
            result,
            {
                "schema_version",
                "status",
                "experiment_id",
                "protocol_id",
                "cohort_id",
                "reliability_profile_id",
                "p2_experiment_id",
                "matched_control_id",
                "output_root",
                "provider_calls_performed_by_analyzer",
                "primary_endpoint",
                "cohort",
                "canonical_inclusion",
                "arms",
                "paired_graph_minus_reactive",
                "claim_boundary",
            },
            "P2-E9 result",
        )
        expected_identity = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "accepted_complete_cohort_analysis",
            "experiment_id": "P2-E9",
            "protocol_id": protocol["protocol_id"],
            "cohort_id": protocol["cohort"]["cohort_id"],
            "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
            "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
            "matched_control_id": protocol["profile"]["matched_control_id"],
            "provider_calls_performed_by_analyzer": False,
        }
        for key, expected in expected_identity.items():
            if result.get(key) != expected:
                raise ReliabilityResultsPending(f"P2-E9 result identity drifted at {key}")
        output_root = result.get("output_root")
        if not isinstance(output_root, str) or not output_root or not Path(output_root).is_absolute():
            raise ReliabilityResultsPending("P2-E9 output_root must be absolute")
        _validate_acceptance(acceptance, protocol=protocol, output_root=output_root)
        if result.get("canonical_inclusion") != acceptance.get("canonical_inclusion"):
            raise ReliabilityResultsPending("P2-E9 result and acceptance inclusion differ")
        _validate_inclusion(result.get("canonical_inclusion"))
        if result.get("primary_endpoint") != {
            "metric": PRIMARY_METRIC,
            "role": "task_primary",
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "private_target_authority": "registered_private_data_port_assignment",
            "prediction_authority": "canonical_rollout_successful_submit_prefix",
            "derived_evaluation_jsonl_ingested": False,
        }:
            raise ReliabilityResultsPending("P2-E9 primary endpoint authority drifted")
        repeat_ids = _expected_repeat_ids(protocol)
        cohort = _mapping(result.get("cohort"), "P2-E9 cohort")
        if cohort != {
            "repeat_ids": repeat_ids,
            "seeds": [item["seed"] for item in protocol["cohort"]["repeats"]],
            "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
            "primary_results_ingested": False,
            "pooling_with_three_seed_primary": "forbidden",
            "assigned_episode_denominator": EXPECTED_EPISODES,
            "matched_pair_denominator": EXPECTED_PAIRS,
        }:
            raise ReliabilityResultsPending("P2-E9 cohort identity or isolation drifted")
        if result.get("claim_boundary") != protocol["claim_boundary"]:
            raise ReliabilityResultsPending("P2-E9 claim boundary drifted")

        metrics = [*protocol["metrics"]["task"], *protocol["metrics"]["rollout"]]
        iterations = int(protocol["statistics"]["bootstrap"]["iterations"])
        arms_value = _mapping(result.get("arms"), "P2-E9 arms")
        if set(arms_value) != set(ARMS):
            raise ReliabilityResultsPending("P2-E9 arm set drifted")
        arms = {
            arm: _validate_arm(
                arms_value[arm],
                arm=arm,
                protocol=protocol,
                repeat_ids=repeat_ids,
                metrics=metrics,
                bootstrap_iterations=iterations,
            )
            for arm in ARMS
        }
        paired = _validate_paired(
            result.get("paired_graph_minus_reactive"),
            protocol=protocol,
            repeat_ids=repeat_ids,
            metrics=metrics,
            bootstrap_iterations=iterations,
            arms=arms,
        )
    except ReliabilityResultsPending:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise ReliabilityResultsPending("P2-E9 artifact structure drifted") from exc

    rows: list[dict[str, Any]] = []

    def metric_row(label: str, role: str, metric: str) -> dict[str, Any]:
        reactive = arms["reactive"]["metrics"][metric]
        graph = arms["graph"]["metrics"][metric]
        delta = paired["metrics"][metric]
        return {
            "label": label,
            "role": role,
            "reactive": reactive["mean_across_registered_repeats"],
            "graph": graph["mean_across_registered_repeats"],
            "delta": delta["mean_across_registered_repeats"],
            "interval": delta["crossed_repeat_sequence_bootstrap_95ci"],
            "variance": delta["between_repeat_variance"],
            "defined": f"{delta['defined_repeat_numerator']}/10 repeats",
        }

    rows.append(metric_row("Target-adverse Average Precision", "Task primary", PRIMARY_METRIC))
    rows.append(
        {
            "label": "Grounded pass@1",
            "role": "Explanatory reliability",
            "reactive": arms["reactive"]["reliability"]["pass_at_1"]["estimate"],
            "graph": arms["graph"]["reliability"]["pass_at_1"]["estimate"],
            "delta": paired["pass_at_1_delta"]["estimate"],
            "interval": paired["pass_at_1_delta"][
                "crossed_repeat_sequence_bootstrap_95ci"
            ],
            "variance": paired["pass_at_1_delta"]["between_repeat_variance"],
            "defined": f"{paired['pass_at_1_delta']['defined_pair_numerator']}/80 pairs",
        }
    )
    rows.append(
        {
            "label": "Grounded pass-all-10",
            "role": "Explanatory reliability",
            "reactive": arms["reactive"]["reliability"]["pass_all_10"]["estimate"],
            "graph": arms["graph"]["reliability"]["pass_all_10"]["estimate"],
            "delta": paired["pass_all_10_delta"]["estimate"],
            "interval": paired["pass_all_10_delta"][
                "sequence_cluster_bootstrap_95ci"
            ],
            "variance": None,
            "defined": "8/8 sequences",
        }
    )
    rows.extend(
        [
            metric_row("Repeated-action ratio", "Rollout", "rollout.repeated_action_ratio"),
            metric_row("Budget-exhaustion rate", "Rollout", "rollout.budget_exhaustion"),
            metric_row("LLM turns", "Cost", "rollout.llm_turns"),
            metric_row("Total tokens", "Cost", "rollout.total_tokens"),
            metric_row("Model cost (USD)", "Cost", "rollout.estimated_model_cost_usd"),
        ]
    )
    for row in rows:
        _validate_display_delta(
            reactive=row["reactive"],
            graph=row["graph"],
            delta=row["delta"],
            label=str(row["label"]),
        )
    return rows


def _format_number(value: Any, *, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    number = _finite(value, "display value")
    if abs(number) >= 1000:
        return f"{number:+,.1f}" if signed else f"{number:,.1f}"
    if 0 < abs(number) < 0.0001:
        return f"{number:+.3e}" if signed else f"{number:.3e}"
    return f"{number:+.4f}" if signed else f"{number:.4f}"


def _format_effect(row: Mapping[str, Any]) -> str:
    if row["delta"] is None:
        return "N/A [N/A, N/A]"
    interval = row["interval"]
    if not isinstance(interval, list) or len(interval) != 2:
        raise ReliabilityResultsPending("defined display delta lacks its interval")
    return (
        f"{_format_number(row['delta'], signed=True)} "
        f"[{_format_number(interval[0], signed=True)}, "
        f"{_format_number(interval[1], signed=True)}]"
    )


def render_table(rows: Sequence[Mapping[str, Any]]) -> str:
    lines = [
        "# Accepted P2-E9 reliability results",
        "",
        "| Endpoint | Role | Reactive | Graph | Graph - Reactive [95% bootstrap CI] | Between-repeat variance of delta | Defined population |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {label} | {role} | {reactive} | {graph} | {effect} | {variance} | {defined} |".format(
                label=row["label"],
                role=row["role"],
                reactive=_format_number(row["reactive"]),
                graph=_format_number(row["graph"]),
                effect=_format_effect(row),
                variance=_format_number(row["variance"]),
                defined=row["defined"],
            )
        )
    lines.extend(
        [
            "",
            "P2-E9 is a separate ten-repeat extension and is never appended to or pooled with the three-seed primary cohort. Task Average Precision is recomputed within each repeat over all 24 assigned windows under `phase1_replay_target_adverse_missing_score_v1`. Grounded pass@1 and pass-all-10 are explanatory. Intervals use 2,000 crossed repeat/sequence or sequence-cluster resamples; undefined values remain N/A.",
            "",
        ]
    )
    return "\n".join(lines)


def render_svg(rows: Sequence[Mapping[str, Any]]) -> str:
    plotted = list(rows[:5])
    width = 1050
    left = 330
    right = 70
    top = 76
    row_height = 52
    plot_width = width - left - right
    height = top + row_height * len(plotted) + 78

    def x(value: float) -> float:
        return left + ((value + 1.0) / 2.0) * plot_width

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Accepted P2-E9 bounded reliability contrasts</title>',
        '<desc id="desc">Graph-minus-Reactive estimates and bootstrap intervals for target-adverse Average Precision and bounded reliability outcomes.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Inter,Arial,sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.label{font-size:14px}.tick{font-size:12px;fill:#596579}.na{font-size:12px;fill:#7b8494}.ci{stroke:#5b4bb7;stroke-width:3}.point{fill:#0b7a75;stroke:#ffffff;stroke-width:1.5}.zero{stroke:#8591a3;stroke-width:1.5;stroke-dasharray:5 4}.grid{stroke:#e1e6ee;stroke-width:1}</style>',
        '<text class="title" x="24" y="34">P2-E9 Graph - Reactive reliability contrasts</text>',
        '<text class="tick" x="24" y="56">Task primary and bounded explanatory outcomes; 95% registered bootstrap CI</text>',
    ]
    for tick in (-1.0, -0.5, 0.0, 0.5, 1.0):
        tick_x = x(tick)
        css = "zero" if tick == 0.0 else "grid"
        parts.append(
            f'<line class="{css}" x1="{tick_x:.2f}" y1="{top - 18}" x2="{tick_x:.2f}" y2="{height - 48}"/>'
        )
        parts.append(
            f'<text class="tick" x="{tick_x:.2f}" y="{height - 25}" text-anchor="middle">{tick:+.1f}</text>'
        )
    for index, row in enumerate(plotted):
        y = top + index * row_height
        parts.append(
            f'<text class="label" x="24" y="{y + 5}">{html.escape(str(row["label"]))}</text>'
        )
        if row["delta"] is None:
            parts.append(f'<text class="na" x="{left + 8}" y="{y + 5}">N/A</text>')
            continue
        interval = row["interval"]
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
        raise ReliabilityResultsPending(
            "active manuscript needs one unique P2-E9 reliability marker pair"
        )
    prefix, remainder = source.split(MANUSCRIPT_BEGIN, 1)
    _, suffix = remainder.split(MANUSCRIPT_END, 1)
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
            "The P2-E9 gate accepted all 160 registered episode bundles and 80 matched Graph--Reactive pairs across ten independent repeats. The table reports the target-adverse task-primary endpoint alongside the preregistered explanatory reliability, rollout, and cost outcomes. P2-E9 remains separate from the three-seed primary cohort, and all estimates are retained regardless of direction.",
            "",
            table_body.rstrip(),
            "",
            f"![Accepted P2-E9 bounded reliability contrasts](../assets/figures/{figure_name})",
        ]
    ) + "\n"


def _restore(path: Path, original: bytes | None) -> None:
    if original is None:
        if path.exists():
            path.unlink()
        return
    path.write_bytes(original)


def _write_group_with_exception_rollback(contents: Mapping[Path, str]) -> None:
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


def write_reliability_manuscript(
    *,
    protocol_path: Path,
    result_path: Path,
    acceptance_path: Path,
    table_path: Path,
    figure_path: Path,
    manuscript_path: Path,
) -> dict[str, Any]:
    protocol = load_graph_reliability_protocol(protocol_path)
    result = _load_json(result_path, "P2-E9 result")
    acceptance = _load_json(acceptance_path, "P2-E9 acceptance")
    rows = validate_reliability_inputs(
        protocol=protocol, acceptance=acceptance, result=result
    )
    if not manuscript_path.is_file():
        raise ReliabilityResultsPending(f"missing active manuscript: {manuscript_path}")
    source = manuscript_path.read_text(encoding="utf-8")
    table = render_table(rows)
    figure = render_svg(rows)
    manuscript = _replace_block(
        source, render_manuscript_block(rows, figure_name=figure_path.name)
    )
    _write_group_with_exception_rollback(
        {
            table_path: table,
            figure_path: figure,
            manuscript_path: manuscript,
        }
    )
    return {
        "schema_version": "p2_e9_reliability_manuscript_render_v1",
        "status": "accepted_p2_e9_inserted",
        "registered_rows": len(rows),
        "formal_episode_bundles": EXPECTED_EPISODES,
        "matched_pairs": EXPECTED_PAIRS,
        "provider_calls_performed_by_renderer": False,
        "raw_run_or_private_data_reads_performed_by_renderer": False,
        "table": str(table_path),
        "figure": str(figure_path),
        "manuscript": str(manuscript_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an accepted P2-E9 reliability result into Paper 2."
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    args = parser.parse_args(argv)
    summary = write_reliability_manuscript(
        protocol_path=args.protocol,
        result_path=args.result,
        acceptance_path=args.acceptance,
        table_path=args.table,
        figure_path=args.figure,
        manuscript_path=args.manuscript,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
