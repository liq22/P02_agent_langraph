#!/usr/bin/env python3
"""Render accepted dynamic-v3 estimates into Paper 2 without raw-run access.

The renderer consumes only the accepted cohort report, the analyzer result, and
the frozen protocol.  It validates displayed task-primary and mechanism
arithmetic before updating the standalone table, SVG, and marked manuscript
block as one group.
"""

from __future__ import annotations

import argparse
import html
import json
import math
import os
import stat
import statistics
import sys
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
if str(_REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPOSITORY_ROOT))

from scripts.analyze_graph_dynamic_formal import (
    ACCEPTANCE_SCHEMA,
    MECHANISM_ABLATION_METRICS,
    P2_E7_DYNAMIC_METRICS,
    RESULT_SCHEMA,
    REPLAY_MISSING_SCORE_POLICY_ID,
    TASK_COHORT_METRICS,
    _bootstrap_interval,
    _exact_sign_p,
    _holm,
    _registered_metrics,
    load_protocol,
    registered_cells,
    validate_acceptance,
)


ROOT = _REPOSITORY_ROOT
DEFAULT_PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
DEFAULT_RESULT_ROOT = (
    ROOT
    / "paper/experiments/results/graph_dynamic_ablation_v3"
    / "openrouter_north_graph_dynamic_generic_ablation_v3"
)
DEFAULT_RESULT = DEFAULT_RESULT_ROOT / "formal_result.json"
DEFAULT_ACCEPTANCE = DEFAULT_RESULT_ROOT / "formal_acceptance.json"
DEFAULT_TABLE = ROOT / "paper/assets/tables/p2_dynamic_formal_results.md"
DEFAULT_FIGURE = ROOT / "paper/assets/figures/p2_dynamic_formal_primary.svg"
DEFAULT_MANUSCRIPT = ROOT / "paper/draft/main.md"

PRIMARY_METRIC = "target_adverse_window_average_precision"
EXPECTED_SEEDS = (20260808, 20260809, 20260810)
EXPECTED_PUBLIC_SEQUENCES = tuple(
    f"sequence-{index:04d}" for index in range(1, 9)
)
BOOTSTRAP_ITERATIONS = 10000
EXPECTED_EPISODES_PER_CELL = 24
EXPECTED_FORMAL_UNITS = 240
PUBLICATION_WRITE_CONTRACT = (
    "fully_staged_mode_preserving_grouped_replace_with_reverse_rollback"
)

MANUSCRIPT_BEGIN = "<!-- P2_DYNAMIC_FORMAL:BEGIN -->"
MANUSCRIPT_END = "<!-- P2_DYNAMIC_FORMAL:END -->"
MANUSCRIPT_HEADING = "#### Dynamic-v3 horizon and ablation results"

ABLATION_CONTROLS = {
    "P2-E3": "graph_no_recovery_revision_edge",
    "P2-E4": "graph_no_observation_conditioned_branching",
    "P2-E5": "graph_no_persistent_graph_state",
    "P2-E6": "graph_no_replanning",
}

CELL_DISPLAY = {
    "reactive": "Benchmark Generic (Reactive-equivalent)",
    "graph_full": "Graph full",
    "graph_no_recovery_revision_edge": "Graph without recovery/revision edge",
    "graph_no_observation_conditioned_branching": "Graph without observation-conditioned branching",
    "graph_no_persistent_graph_state": "Graph without persistent state",
    "graph_no_replanning": "Graph without replanning",
}


class DynamicResultsPending(RuntimeError):
    """Raised when a dynamic-v3 artifact is absent, rejected, or inconsistent."""


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise DynamicResultsPending(f"missing {label}: {path}")
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise DynamicResultsPending(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise DynamicResultsPending(f"{label} must be a JSON object")
    return value


def _mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise DynamicResultsPending(f"{label} must be an object")
    return dict(value)


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    observed = set(value)
    if observed != expected:
        raise DynamicResultsPending(
            f"{label} keys drifted: missing={sorted(expected - observed)}, "
            f"extra={sorted(observed - expected)}"
        )


def _integer(value: Any, label: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise DynamicResultsPending(f"{label} must be an integer >= {minimum}")
    return value


def _finite(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DynamicResultsPending(f"{label} must be finite numeric")
    number = float(value)
    if not math.isfinite(number):
        raise DynamicResultsPending(f"{label} must be finite numeric")
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
        raise DynamicResultsPending(f"{label} is below {lower}")
    if upper is not None and number > upper + 1e-12:
        raise DynamicResultsPending(f"{label} is above {upper}")
    return number


def _same_number(observed: Any, expected: float | None, label: str) -> None:
    if expected is None:
        if observed is not None:
            raise DynamicResultsPending(f"{label} must be N/A")
        return
    number = _finite(observed, label)
    if not math.isclose(number, expected, rel_tol=1e-12, abs_tol=1e-12):
        raise DynamicResultsPending(
            f"{label} arithmetic drifted: observed={number}, expected={expected}"
        )


def _validate_count_map(
    value: Any, label: str, *, expected_total: int | None = None
) -> dict[str, int]:
    counts = _mapping(value, label)
    if any(not isinstance(key, str) or not key for key in counts):
        raise DynamicResultsPending(f"{label} has an invalid key")
    result = {
        key: _integer(item, f"{label}.{key}") for key, item in counts.items()
    }
    if expected_total is not None and sum(result.values()) != expected_total:
        raise DynamicResultsPending(
            f"{label} totals {sum(result.values())}; expected {expected_total}"
        )
    return result


def _validate_inclusion(
    value: Any, *, cell_keys: set[str]
) -> dict[str, Any]:
    inclusion = _mapping(value, "canonical inclusion")
    _exact_keys(
        inclusion,
        {
            "scheduled_unit_denominator",
            "effective_non_provider_terminal_count",
            "retained_provider_failure_attempt_count",
            "retained_non_provider_failure_count",
            "terminal_status_counts",
            "failure_kind_counts",
            "cell_denominators",
            "p2e2_matched_pair_count",
            "public_sequence_cluster_count",
            "failures_retained_in_denominator",
            "cross_horizon_pooling_performed",
            "cross_profile_pooling_performed",
            "private_assignment_sequence_count",
            "private_target_authority",
            "prediction_authority",
            "derived_evaluation_jsonl_ingested",
        },
        "canonical inclusion",
    )
    expected_scalars = {
        "scheduled_unit_denominator": EXPECTED_FORMAL_UNITS,
        "effective_non_provider_terminal_count": EXPECTED_FORMAL_UNITS,
        "p2e2_matched_pair_count": 72,
        "public_sequence_cluster_count": 8,
        "failures_retained_in_denominator": True,
        "cross_horizon_pooling_performed": False,
        "cross_profile_pooling_performed": False,
        "private_assignment_sequence_count": 8,
        "private_target_authority": "registered_private_data_port_assignment",
        "prediction_authority": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_ingested": False,
    }
    for key, expected in expected_scalars.items():
        if inclusion.get(key) != expected:
            raise DynamicResultsPending(
                f"canonical inclusion drifted at {key}: {inclusion.get(key)!r}"
            )
    _integer(
        inclusion.get("retained_provider_failure_attempt_count"),
        "retained provider failures",
    )
    retained_failures = _integer(
        inclusion.get("retained_non_provider_failure_count"),
        "retained non-provider failures",
    )
    if retained_failures > EXPECTED_FORMAL_UNITS:
        raise DynamicResultsPending("retained non-provider failures exceed the cohort")
    _validate_count_map(
        inclusion.get("terminal_status_counts"),
        "terminal status counts",
        expected_total=EXPECTED_FORMAL_UNITS,
    )
    failure_counts = _validate_count_map(
        inclusion.get("failure_kind_counts"), "failure kind counts"
    )
    if sum(failure_counts.values()) != retained_failures:
        raise DynamicResultsPending("failure-kind counts disagree with retained failures")
    denominators = _validate_count_map(
        inclusion.get("cell_denominators"), "cell denominators"
    )
    if set(denominators) != cell_keys or any(
        count != EXPECTED_EPISODES_PER_CELL for count in denominators.values()
    ):
        raise DynamicResultsPending("canonical cell denominators are not exact 24s")
    return inclusion


def _validate_task_cell(
    value: Any, *, label: str, horizon: int
) -> dict[str, Any]:
    report = _mapping(value, label)
    _exact_keys(
        report,
        {
            "estimate",
            "aggregation",
            "seed_estimates",
            "defined_seed_numerator",
            "registered_seed_denominator",
            "assigned_episode_denominator",
            "assigned_window_denominator",
            "submitted_window_numerator",
            "missing_assigned_scores",
            "score_coverage",
            "missing_score_policy_id",
            "per_bearing_metric_averaging_performed",
            "undefined_values_imputed_as_zero",
        },
        label,
    )
    expected_static = {
        "aggregation": "mean_of_seed_level_metrics_each_recomputed_over_all_eight_bearing_sequences",
        "registered_seed_denominator": 3,
        "assigned_episode_denominator": EXPECTED_EPISODES_PER_CELL,
        "assigned_window_denominator": EXPECTED_EPISODES_PER_CELL * horizon,
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "per_bearing_metric_averaging_performed": False,
        "undefined_values_imputed_as_zero": False,
    }
    for key, expected in expected_static.items():
        if report.get(key) != expected:
            raise DynamicResultsPending(f"{label}.{key} drifted")

    seed_values = _mapping(report.get("seed_estimates"), f"{label}.seed_estimates")
    if set(seed_values) != {str(seed) for seed in EXPECTED_SEEDS}:
        raise DynamicResultsPending(f"{label} has the wrong seed set")
    normalized = [
        _optional_number(
            seed_values[str(seed)],
            f"{label}.seed_estimates.{seed}",
            lower=0.0,
            upper=1.0,
        )
        for seed in EXPECTED_SEEDS
    ]
    defined = [item for item in normalized if item is not None]
    if report.get("defined_seed_numerator") != len(defined):
        raise DynamicResultsPending(f"{label} has a wrong defined-seed numerator")
    expected_estimate = statistics.fmean(defined) if defined else None
    _same_number(report.get("estimate"), expected_estimate, f"{label}.estimate")

    assigned = EXPECTED_EPISODES_PER_CELL * horizon
    submitted = _integer(
        report.get("submitted_window_numerator"), f"{label}.submitted windows"
    )
    missing = _integer(
        report.get("missing_assigned_scores"), f"{label}.missing windows"
    )
    if submitted + missing != assigned:
        raise DynamicResultsPending(f"{label} loses assigned-window denominator rows")
    _same_number(
        report.get("score_coverage"),
        submitted / assigned,
        f"{label}.score_coverage",
    )
    return report


def _validate_episode_cell(value: Any, *, label: str) -> dict[str, Any]:
    report = _mapping(value, label)
    _exact_keys(
        report,
        {
            "estimate",
            "seed_sequence_values",
            "defined_episode_numerator",
            "assigned_episode_denominator",
            "undefined_values_imputed_as_zero",
        },
        label,
    )
    seed_values = _mapping(
        report.get("seed_sequence_values"), f"{label}.seed_sequence_values"
    )
    if set(seed_values) != {str(seed) for seed in EXPECTED_SEEDS}:
        raise DynamicResultsPending(f"{label} has the wrong seed set")
    normalized: list[float] = []
    for seed in EXPECTED_SEEDS:
        sequences = _mapping(
            seed_values[str(seed)], f"{label}.seed_sequence_values.{seed}"
        )
        if set(sequences) != set(EXPECTED_PUBLIC_SEQUENCES):
            raise DynamicResultsPending(
                f"{label}.seed_sequence_values.{seed} has the wrong sequence set"
            )
        for sequence_id in EXPECTED_PUBLIC_SEQUENCES:
            item = _optional_number(
                sequences[sequence_id],
                f"{label}.seed_sequence_values.{seed}.{sequence_id}",
            )
            if item is not None:
                normalized.append(item)
    defined = _integer(
        report.get("defined_episode_numerator"), f"{label}.defined episodes"
    )
    if defined != len(normalized):
        raise DynamicResultsPending(f"{label} defined-episode numerator drifted")
    if report.get("assigned_episode_denominator") != EXPECTED_EPISODES_PER_CELL:
        raise DynamicResultsPending(f"{label} has a wrong episode denominator")
    _same_number(
        report.get("estimate"),
        statistics.fmean(normalized) if normalized else None,
        f"{label}.estimate",
    )
    if report.get("undefined_values_imputed_as_zero") is not False:
        raise DynamicResultsPending(f"{label} permits undefined-value imputation")
    return report


def _validate_cells(
    result: Mapping[str, Any], protocol: Mapping[str, Any]
) -> dict[str, dict[str, Any]]:
    expected_cells = {cell.key: cell for cell in registered_cells(protocol)}
    metrics = _registered_metrics(protocol)
    by_cell = _mapping(result.get("by_cell"), "result.by_cell")
    if set(by_cell) != set(expected_cells):
        raise DynamicResultsPending("result cell topology drifted")
    validated: dict[str, dict[str, Any]] = {}
    for key, cell in expected_cells.items():
        report = _mapping(by_cell[key], f"by_cell.{key}")
        _exact_keys(
            report,
            {
                "horizon",
                "cell",
                "agent_profile_id",
                "assigned_episode_denominator",
                "terminal_status_counts",
                "failure_kind_counts",
                "metrics",
            },
            f"by_cell.{key}",
        )
        expected_identity = {
            "horizon": cell.horizon,
            "cell": cell.name,
            "agent_profile_id": cell.agent_profile_id,
            "assigned_episode_denominator": EXPECTED_EPISODES_PER_CELL,
        }
        for identity_key, expected in expected_identity.items():
            if report.get(identity_key) != expected:
                raise DynamicResultsPending(
                    f"by_cell.{key}.{identity_key} identity drifted"
                )
        _validate_count_map(
            report.get("terminal_status_counts"),
            f"by_cell.{key}.terminal_status_counts",
            expected_total=EXPECTED_EPISODES_PER_CELL,
        )
        failure_counts = _validate_count_map(
            report.get("failure_kind_counts"),
            f"by_cell.{key}.failure_kind_counts",
        )
        if sum(failure_counts.values()) > EXPECTED_EPISODES_PER_CELL:
            raise DynamicResultsPending(f"by_cell.{key} has too many failures")
        cell_metrics = _mapping(report.get("metrics"), f"by_cell.{key}.metrics")
        if set(cell_metrics) != set(metrics):
            raise DynamicResultsPending(f"by_cell.{key} metric registry drifted")
        for metric in metrics:
            label = f"by_cell.{key}.metrics.{metric}"
            if metric in TASK_COHORT_METRICS:
                _validate_task_cell(cell_metrics[metric], label=label, horizon=cell.horizon)
            else:
                _validate_episode_cell(cell_metrics[metric], label=label)
        validated[key] = report
    return validated


def _primary_cell(
    by_cell: Mapping[str, Mapping[str, Any]], horizon: int, cell: str
) -> dict[str, Any]:
    return _mapping(
        by_cell[f"h{horizon}:{cell}"]["metrics"][PRIMARY_METRIC],
        f"primary cell h{horizon}:{cell}",
    )


def _episode_cell(
    by_cell: Mapping[str, Mapping[str, Any]],
    *,
    horizon: int,
    cell: str,
    metric: str,
) -> dict[str, Any]:
    return _mapping(
        by_cell[f"h{horizon}:{cell}"]["metrics"][metric],
        f"episode cell h{horizon}:{cell}.{metric}",
    )


def _validate_mechanism_reporting_contract(
    protocol: Mapping[str, Any],
) -> None:
    consumer = _mapping(
        protocol.get("formal_analysis", {}).get("accepted_manuscript_consumer"),
        "accepted manuscript consumer",
    )
    if consumer.get("displayed_mechanism_arithmetic_recomputed") is not True:
        raise DynamicResultsPending("mechanism arithmetic consumer flag drifted")
    if consumer.get("task_primary_and_mechanism_sections_separate") is not True:
        raise DynamicResultsPending("task/mechanism section boundary drifted")
    expected_scalars = {
        "render_schema": "p2_dynamic_formal_manuscript_render_v2",
        "task_primary_rows_after_acceptance": 8,
        "secondary_mechanism_rows_after_acceptance": 26,
        "valid_bootstrap_replicates_reported": True,
        "existing_output_contract": "absent_or_ordinary_single_link_regular_file",
        "production_cli_protocol": "graph_dynamic_ablation_protocol_v3.yaml",
        "write_contract": PUBLICATION_WRITE_CONTRACT,
    }
    for key, expected in expected_scalars.items():
        if consumer.get(key) != expected:
            raise DynamicResultsPending(f"accepted consumer contract drifted at {key}")
    mechanism = _mapping(
        consumer.get("mechanism_reporting"), "mechanism reporting"
    )
    if (
        mechanism.get("role") != "secondary_explanatory_not_task_performance"
        or mechanism.get("horizon") != 12
        or mechanism.get("direction") != "graph_full_minus_control"
    ):
        raise DynamicResultsPending("mechanism reporting role or estimand drifted")
    ablations = _mapping(
        mechanism.get("ablation_rows"), "mechanism reporting ablation rows"
    )
    if set(ablations) != set(ABLATION_CONTROLS):
        raise DynamicResultsPending("mechanism reporting ablation set drifted")
    for experiment_id, control in ABLATION_CONTROLS.items():
        report = _mapping(ablations[experiment_id], f"{experiment_id} reporting")
        expected_keys = {"control", "metrics"}
        if experiment_id == "P2-E4":
            expected_keys.add("also_serves_p2_e7_no_branching_comparison")
        _exact_keys(report, expected_keys, f"{experiment_id} reporting")
        if (
            report.get("control") != control
            or report.get("metrics")
            != list(MECHANISM_ABLATION_METRICS[experiment_id])
        ):
            raise DynamicResultsPending(
                f"{experiment_id} mechanism reporting contract drifted"
            )
        if experiment_id == "P2-E4" and report.get(
            "also_serves_p2_e7_no_branching_comparison"
        ) is not True:
            raise DynamicResultsPending("P2-E4/P2-E7 row reuse drifted")
    e7 = _mapping(
        mechanism.get("operating_condition_change_rows"),
        "P2-E7 reporting",
    )
    if e7 != {
        "experiment_id": "P2-E7",
        "control": "reactive",
        "metrics": list(P2_E7_DYNAMIC_METRICS),
        "no_branching_source_reused_from": "P2-E4",
        "duplicate_no_branching_rows": False,
        "forbidden_interpretations": [
            "fault_onset",
            "event_f1",
            "detection_delay",
            "physical_time",
        ],
    }:
        raise DynamicResultsPending("P2-E7 reporting contract drifted")


def _validate_episode_contrast(
    value: Any,
    *,
    label: str,
    metric: str,
    horizon: int,
    treatment: str,
    control: str,
    by_cell: Mapping[str, Mapping[str, Any]],
    expected_bootstrap_seed: int,
    holm: bool,
) -> dict[str, Any]:
    report = _mapping(value, label)
    expected_keys = {
        "direction",
        "horizon",
        "estimate",
        "seed_level_differences_by_public_sequence",
        "public_sequence_cluster_differences",
        "paired_cluster_bootstrap_95ci",
        "paired_cluster_bootstrap_iterations",
        "paired_cluster_bootstrap_seed",
        "paired_cluster_bootstrap_valid_replicates",
        "exact_two_sided_sign_permutation_p",
        "exact_sign_assignments",
        "defined_seed_pair_numerator",
        "assigned_seed_pair_denominator",
        "defined_public_sequence_cluster_numerator",
        "registered_public_sequence_cluster_denominator",
        "seeds_averaged_within_cluster_before_inference",
        "undefined_values_imputed_as_zero",
    }
    if holm:
        expected_keys.add("holm_adjusted_p")
    _exact_keys(report, expected_keys, label)
    if report.get("direction") != f"{treatment}_minus_{control}":
        raise DynamicResultsPending(f"{label} direction drifted")
    if report.get("horizon") != horizon:
        raise DynamicResultsPending(f"{label} horizon drifted")
    expected_static = {
        "assigned_seed_pair_denominator": 24,
        "registered_public_sequence_cluster_denominator": 8,
        "seeds_averaged_within_cluster_before_inference": True,
        "undefined_values_imputed_as_zero": False,
        "paired_cluster_bootstrap_iterations": BOOTSTRAP_ITERATIONS,
        "paired_cluster_bootstrap_seed": expected_bootstrap_seed,
    }
    for key, expected in expected_static.items():
        if report.get(key) != expected:
            raise DynamicResultsPending(f"{label}.{key} drifted")

    treatment_values = _mapping(
        _episode_cell(
            by_cell,
            horizon=horizon,
            cell=treatment,
            metric=metric,
        ).get("seed_sequence_values"),
        f"{label}.treatment values",
    )
    control_values = _mapping(
        _episode_cell(
            by_cell,
            horizon=horizon,
            cell=control,
            metric=metric,
        ).get("seed_sequence_values"),
        f"{label}.control values",
    )
    observed_seeds = _mapping(
        report.get("seed_level_differences_by_public_sequence"),
        f"{label}.seed differences",
    )
    observed_clusters = _mapping(
        report.get("public_sequence_cluster_differences"),
        f"{label}.cluster differences",
    )
    if set(observed_seeds) != set(EXPECTED_PUBLIC_SEQUENCES) or set(
        observed_clusters
    ) != set(EXPECTED_PUBLIC_SEQUENCES):
        raise DynamicResultsPending(f"{label} has the wrong public sequence set")

    defined_pairs = 0
    cluster_values: list[float] = []
    for sequence_id in EXPECTED_PUBLIC_SEQUENCES:
        seed_differences = _mapping(
            observed_seeds[sequence_id],
            f"{label}.seed differences.{sequence_id}",
        )
        if set(seed_differences) != {str(seed) for seed in EXPECTED_SEEDS}:
            raise DynamicResultsPending(
                f"{label}.{sequence_id} has the wrong paired seed set"
            )
        complete: list[float] = []
        for seed in EXPECTED_SEEDS:
            key = str(seed)
            treatment_seed = _mapping(
                treatment_values[key], f"{label}.treatment.{key}"
            )
            control_seed = _mapping(
                control_values[key], f"{label}.control.{key}"
            )
            treatment_value = _optional_number(
                treatment_seed[sequence_id],
                f"{label}.treatment.{key}.{sequence_id}",
            )
            control_value = _optional_number(
                control_seed[sequence_id],
                f"{label}.control.{key}.{sequence_id}",
            )
            expected = (
                None
                if treatment_value is None or control_value is None
                else treatment_value - control_value
            )
            _same_number(
                seed_differences[key],
                expected,
                f"{label}.{sequence_id}.{key}",
            )
            if expected is not None:
                defined_pairs += 1
                complete.append(expected)
        expected_cluster = (
            statistics.fmean(complete)
            if len(complete) == len(EXPECTED_SEEDS)
            else None
        )
        _same_number(
            observed_clusters[sequence_id],
            expected_cluster,
            f"{label}.cluster.{sequence_id}",
        )
        if expected_cluster is not None:
            cluster_values.append(expected_cluster)

    if report.get("defined_seed_pair_numerator") != defined_pairs:
        raise DynamicResultsPending(f"{label} defined-pair numerator drifted")
    if report.get("defined_public_sequence_cluster_numerator") != len(
        cluster_values
    ):
        raise DynamicResultsPending(f"{label} defined-cluster numerator drifted")
    expected_estimate = (
        statistics.fmean(cluster_values) if cluster_values else None
    )
    _same_number(report.get("estimate"), expected_estimate, f"{label}.estimate")

    expected_interval = _bootstrap_interval(
        cluster_values,
        iterations=BOOTSTRAP_ITERATIONS,
        seed=expected_bootstrap_seed,
    )
    interval = report.get("paired_cluster_bootstrap_95ci")
    if expected_interval is None:
        if interval is not None:
            raise DynamicResultsPending(f"{label} incomplete clusters need N/A CI")
    else:
        if not isinstance(interval, list) or len(interval) != 2:
            raise DynamicResultsPending(f"{label} lacks a two-bound CI")
        _same_number(interval[0], expected_interval[0], f"{label}.CI lower")
        _same_number(interval[1], expected_interval[1], f"{label}.CI upper")
    expected_valid = (
        BOOTSTRAP_ITERATIONS
        if len(cluster_values) == len(EXPECTED_PUBLIC_SEQUENCES)
        else 0
    )
    if report.get("paired_cluster_bootstrap_valid_replicates") != expected_valid:
        raise DynamicResultsPending(f"{label} bootstrap replicate count drifted")
    expected_p, expected_assignments = _exact_sign_p(cluster_values)
    _same_number(
        report.get("exact_two_sided_sign_permutation_p"),
        expected_p,
        f"{label}.exact p",
    )
    if report.get("exact_sign_assignments") != expected_assignments:
        raise DynamicResultsPending(f"{label} exact assignment count drifted")
    return report


def _validate_inference_fields(
    report: Mapping[str, Any], *, label: str, estimate: float | None, limit: float
) -> None:
    interval = report.get("paired_cluster_bootstrap_95ci")
    valid = _integer(
        report.get("paired_cluster_bootstrap_valid_replicates"),
        f"{label}.valid bootstrap replicates",
    )
    assignments = _integer(
        report.get("exact_cluster_swap_assignments"),
        f"{label}.exact assignments",
    )
    pvalue = _optional_number(
        report.get("exact_two_sided_cluster_swap_p"),
        f"{label}.exact p",
        lower=0.0,
        upper=1.0,
    )
    if estimate is None:
        if interval is not None or valid != 0 or assignments != 0 or pvalue is not None:
            raise DynamicResultsPending(
                f"{label} must keep undefined inference as N/A with zero replicates"
            )
        return
    if not isinstance(interval, list) or len(interval) != 2:
        raise DynamicResultsPending(f"{label} lacks a two-bound bootstrap interval")
    low = _finite(interval[0], f"{label}.CI lower")
    high = _finite(interval[1], f"{label}.CI upper")
    if low > high or low < -limit - 1e-12 or high > limit + 1e-12:
        raise DynamicResultsPending(f"{label} has an invalid bootstrap interval")
    if not 1 <= valid <= BOOTSTRAP_ITERATIONS:
        raise DynamicResultsPending(f"{label} has an invalid bootstrap count")
    if assignments != 256 or pvalue is None:
        raise DynamicResultsPending(f"{label} lacks the exact 256-way cluster test")


def _validate_task_contrast(
    value: Any,
    *,
    label: str,
    horizon: int,
    treatment: str,
    control: str,
    by_cell: Mapping[str, Mapping[str, Any]],
    holm: bool,
) -> dict[str, Any]:
    report = _mapping(value, label)
    expected_keys = {
        "direction",
        "horizon",
        "estimate",
        "seed_level_differences",
        "paired_cluster_bootstrap_95ci",
        "paired_cluster_bootstrap_valid_replicates",
        "exact_two_sided_cluster_swap_p",
        "exact_cluster_swap_assignments",
        "defined_seed_pair_numerator",
        "assigned_seed_pair_denominator",
        "matched_bearing_sequence_clusters",
        "treatment_assigned_episode_denominator",
        "control_assigned_episode_denominator",
        "treatment_assigned_windows",
        "control_assigned_windows",
        "treatment_missing_assigned_scores",
        "control_missing_assigned_scores",
        "missing_score_policy_id",
        "metric_recomputed_after_each_cluster_draw_or_swap",
        "per_bearing_metric_averaging_performed",
        "undefined_values_imputed_as_zero",
    }
    if holm:
        expected_keys.add("holm_adjusted_p")
    _exact_keys(report, expected_keys, label)
    if report.get("direction") != f"{treatment}_minus_{control}":
        raise DynamicResultsPending(f"{label} direction drifted")
    if report.get("horizon") != horizon:
        raise DynamicResultsPending(f"{label} horizon drifted")
    expected_static = {
        "assigned_seed_pair_denominator": 3,
        "matched_bearing_sequence_clusters": 8,
        "treatment_assigned_episode_denominator": EXPECTED_EPISODES_PER_CELL,
        "control_assigned_episode_denominator": EXPECTED_EPISODES_PER_CELL,
        "treatment_assigned_windows": EXPECTED_EPISODES_PER_CELL * horizon,
        "control_assigned_windows": EXPECTED_EPISODES_PER_CELL * horizon,
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "metric_recomputed_after_each_cluster_draw_or_swap": True,
        "per_bearing_metric_averaging_performed": False,
        "undefined_values_imputed_as_zero": False,
    }
    for key, expected in expected_static.items():
        if report.get(key) != expected:
            raise DynamicResultsPending(f"{label}.{key} drifted")

    treatment_cell = _primary_cell(by_cell, horizon, treatment)
    control_cell = _primary_cell(by_cell, horizon, control)
    treatment_seeds = _mapping(
        treatment_cell["seed_estimates"], f"{label}.treatment seeds"
    )
    control_seeds = _mapping(control_cell["seed_estimates"], f"{label}.control seeds")
    differences = _mapping(
        report.get("seed_level_differences"), f"{label}.seed differences"
    )
    if set(differences) != {str(seed) for seed in EXPECTED_SEEDS}:
        raise DynamicResultsPending(f"{label} has the wrong paired seed set")
    normalized: list[float | None] = []
    for seed in EXPECTED_SEEDS:
        key = str(seed)
        treatment_value = _optional_number(
            treatment_seeds[key], f"{label}.treatment seed {seed}", lower=0.0, upper=1.0
        )
        control_value = _optional_number(
            control_seeds[key], f"{label}.control seed {seed}", lower=0.0, upper=1.0
        )
        expected = (
            None
            if treatment_value is None or control_value is None
            else treatment_value - control_value
        )
        _same_number(differences[key], expected, f"{label}.seed difference {seed}")
        normalized.append(expected)
    defined = [item for item in normalized if item is not None]
    if report.get("defined_seed_pair_numerator") != len(defined):
        raise DynamicResultsPending(f"{label} has a wrong defined-pair numerator")
    expected_estimate = (
        statistics.fmean(defined) if len(defined) == len(EXPECTED_SEEDS) else None
    )
    _same_number(report.get("estimate"), expected_estimate, f"{label}.estimate")

    if report.get("treatment_missing_assigned_scores") != treatment_cell.get(
        "missing_assigned_scores"
    ):
        raise DynamicResultsPending(f"{label} treatment missing-window count drifted")
    if report.get("control_missing_assigned_scores") != control_cell.get(
        "missing_assigned_scores"
    ):
        raise DynamicResultsPending(f"{label} control missing-window count drifted")
    _validate_inference_fields(
        report, label=label, estimate=expected_estimate, limit=1.0
    )
    return report


def _validate_task_interaction(
    value: Any,
    *,
    label: str,
    horizon_reports: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    report = _mapping(value, label)
    _exact_keys(
        report,
        {
            "direction",
            "estimate",
            "seed_level_interactions",
            "paired_cluster_bootstrap_95ci",
            "paired_cluster_bootstrap_valid_replicates",
            "exact_two_sided_cluster_swap_p",
            "exact_cluster_swap_assignments",
            "defined_seed_interaction_numerator",
            "assigned_seed_interaction_denominator",
            "matched_bearing_sequence_clusters",
            "missing_score_policy_id",
            "metric_recomputed_after_each_cluster_draw_or_swap",
            "per_bearing_metric_averaging_performed",
            "nested_horizons_treated_as_independent",
            "undefined_values_imputed_as_zero",
            "holm_adjusted_p",
        },
        label,
    )
    expected_static = {
        "direction": "(graph_full_minus_reactive)_h12_minus_h3",
        "assigned_seed_interaction_denominator": 3,
        "matched_bearing_sequence_clusters": 8,
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "metric_recomputed_after_each_cluster_draw_or_swap": True,
        "per_bearing_metric_averaging_performed": False,
        "nested_horizons_treated_as_independent": False,
        "undefined_values_imputed_as_zero": False,
    }
    for key, expected in expected_static.items():
        if report.get(key) != expected:
            raise DynamicResultsPending(f"{label}.{key} drifted")
    seed_values = _mapping(
        report.get("seed_level_interactions"), f"{label}.seed interactions"
    )
    if set(seed_values) != {str(seed) for seed in EXPECTED_SEEDS}:
        raise DynamicResultsPending(f"{label} has the wrong seed set")
    high = _mapping(
        horizon_reports["12"]["seed_level_differences"], f"{label}.h12 seeds"
    )
    low = _mapping(
        horizon_reports["3"]["seed_level_differences"], f"{label}.h3 seeds"
    )
    normalized: list[float | None] = []
    for seed in EXPECTED_SEEDS:
        key = str(seed)
        high_value = _optional_number(high[key], f"{label}.h12 seed {seed}")
        low_value = _optional_number(low[key], f"{label}.h3 seed {seed}")
        expected = (
            None
            if high_value is None or low_value is None
            else high_value - low_value
        )
        _same_number(seed_values[key], expected, f"{label}.seed interaction {seed}")
        normalized.append(expected)
    defined = [item for item in normalized if item is not None]
    if report.get("defined_seed_interaction_numerator") != len(defined):
        raise DynamicResultsPending(f"{label} has a wrong defined-seed numerator")
    expected_estimate = (
        statistics.fmean(defined) if len(defined) == len(EXPECTED_SEEDS) else None
    )
    _same_number(report.get("estimate"), expected_estimate, f"{label}.estimate")
    _validate_inference_fields(
        report, label=label, estimate=expected_estimate, limit=2.0
    )
    expected_holm = _holm(
        {"h12_minus_h3": report.get("exact_two_sided_cluster_swap_p")}
    )["h12_minus_h3"]
    _same_number(report.get("holm_adjusted_p"), expected_holm, f"{label}.Holm p")
    return report


def _validate_result(
    result: Mapping[str, Any],
    acceptance: Mapping[str, Any],
    protocol: Mapping[str, Any],
) -> list[dict[str, Any]]:
    _exact_keys(
        result,
        {
            "schema_version",
            "status",
            "protocol_id",
            "provider_profile_id",
            "output_root",
            "provider_calls_performed_by_analyzer",
            "primary_endpoint_authority",
            "canonical_inclusion",
            "grouping_invariants",
            "by_cell",
            "registered_contrasts",
            "claim_boundary",
        },
        "dynamic formal result",
    )
    expected_identity = {
        "schema_version": RESULT_SCHEMA,
        "status": "accepted_complete_formal_cohort_analysis",
        "protocol_id": protocol["protocol_id"],
        "provider_profile_id": protocol["runtime_and_provider_profile"][
            "formal_provider_profile_id"
        ],
        "provider_calls_performed_by_analyzer": False,
    }
    for key, expected in expected_identity.items():
        if result.get(key) != expected:
            raise DynamicResultsPending(f"dynamic formal result identity drifted at {key}")
    output_root = result.get("output_root")
    if not isinstance(output_root, str) or not output_root or not Path(output_root).is_absolute():
        raise DynamicResultsPending("dynamic result output_root must be absolute")
    declared_formal_root = _declared_protocol_path(
        protocol.get("output_contract", {}).get("formal_root"),
        "output_contract.formal_root",
    ).resolve(strict=False)
    if output_root != str(Path(output_root).resolve(strict=False)) or Path(
        output_root
    ) != declared_formal_root:
        raise DynamicResultsPending(
            "dynamic result output_root differs from the protocol formal_root"
        )
    try:
        validate_acceptance(output_root, protocol, acceptance)
    except (TypeError, ValueError, KeyError) as exc:
        raise DynamicResultsPending("dynamic formal acceptance did not validate") from exc
    _exact_keys(
        acceptance,
        {
            "schema_version",
            "accepted",
            "protocol_id",
            "provider_profile_id",
            "output_root",
            "expected_episode_bundles",
            "observed_effective_non_provider_terminals",
            "provider_calls_performed_by_gate",
            "grouping_contract",
            "evaluator_authority",
            "canonical_inclusion",
            "errors",
        },
        "dynamic formal acceptance",
    )
    if acceptance.get("schema_version") != ACCEPTANCE_SCHEMA:
        raise DynamicResultsPending("dynamic acceptance schema drifted")

    authority = {
        "target_source": "registered_private_data_port_assignment",
        "prediction_source": "canonical_rollout_successful_submit_prefix",
        "derived_evaluation_jsonl_ingested": False,
        "private_paths_serialized": False,
    }
    if result.get("primary_endpoint_authority") != authority:
        raise DynamicResultsPending("dynamic result primary authority drifted")
    if acceptance.get("evaluator_authority") != authority:
        raise DynamicResultsPending("dynamic acceptance evaluator authority drifted")
    if result.get("canonical_inclusion") != acceptance.get("canonical_inclusion"):
        raise DynamicResultsPending("result and acceptance inclusion reports differ")

    cell_keys = {cell.key for cell in registered_cells(protocol)}
    _validate_inclusion(result.get("canonical_inclusion"), cell_keys=cell_keys)
    if result.get("grouping_invariants") != {
        "absolute_summaries_keyed_by_horizon_and_agent_profile": True,
        "task_primary_recomputed_over_all_assigned_windows_within_seed_cell": True,
        "per_bearing_average_precision_performed": False,
        "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
        "pooled_headline_graph_effect_across_horizons": False,
        "pool_across_provider_model_or_runtime_profiles": False,
        "nested_horizons_treated_as_independent": False,
        "failed_non_provider_terminals_retained": True,
    }:
        raise DynamicResultsPending("dynamic result grouping invariants drifted")
    grouping = _mapping(acceptance.get("grouping_contract"), "acceptance grouping")
    if grouping.get("paired_unit") != protocol["statistics"]["paired_unit"]:
        raise DynamicResultsPending("acceptance paired unit drifted")

    _validate_mechanism_reporting_contract(protocol)
    by_cell = _validate_cells(result, protocol)
    metrics = _registered_metrics(protocol)
    contrasts = _mapping(result.get("registered_contrasts"), "registered contrasts")
    _exact_keys(contrasts, {"P2-E2", "P2-E3_to_P2-E6", "P2-E7"}, "registered contrasts")
    p2e2 = _mapping(contrasts["P2-E2"], "P2-E2")
    _exact_keys(
        p2e2,
        {"graph_full_minus_reactive_by_horizon", "registered_h12_minus_h3_interaction"},
        "P2-E2",
    )
    by_horizon = _mapping(
        p2e2["graph_full_minus_reactive_by_horizon"], "P2-E2 horizons"
    )
    if set(by_horizon) != {"3", "6", "12"}:
        raise DynamicResultsPending("P2-E2 horizon set drifted")
    horizon_primary: dict[str, dict[str, Any]] = {}
    for horizon in (3, 6, 12):
        reports = _mapping(by_horizon[str(horizon)], f"P2-E2 h{horizon}")
        if set(reports) != set(metrics):
            raise DynamicResultsPending(f"P2-E2 h{horizon} metric registry drifted")
        for metric, report in reports.items():
            if not isinstance(report, Mapping):
                raise DynamicResultsPending(f"P2-E2 h{horizon}.{metric} is invalid")
            if report.get("direction") != "graph_full_minus_reactive" or report.get(
                "horizon"
            ) != horizon:
                raise DynamicResultsPending(f"P2-E2 h{horizon}.{metric} identity drifted")
        horizon_primary[str(horizon)] = _validate_task_contrast(
            reports[PRIMARY_METRIC],
            label=f"P2-E2 h{horizon}.{PRIMARY_METRIC}",
            horizon=horizon,
            treatment="graph_full",
            control="reactive",
            by_cell=by_cell,
            holm=False,
        )

    interaction_reports = _mapping(
        p2e2["registered_h12_minus_h3_interaction"], "P2-E2 interaction"
    )
    if set(interaction_reports) != set(metrics):
        raise DynamicResultsPending("P2-E2 interaction metric registry drifted")
    for metric, report in interaction_reports.items():
        if not isinstance(report, Mapping) or report.get("direction") != (
            "(graph_full_minus_reactive)_h12_minus_h3"
        ):
            raise DynamicResultsPending(f"P2-E2 interaction.{metric} identity drifted")
    interaction = _validate_task_interaction(
        interaction_reports[PRIMARY_METRIC],
        label=f"P2-E2 interaction.{PRIMARY_METRIC}",
        horizon_reports=horizon_primary,
    )

    ablations = _mapping(contrasts["P2-E3_to_P2-E6"], "P2-E3 to P2-E6")
    if set(ablations) != set(ABLATION_CONTROLS):
        raise DynamicResultsPending("ablation experiment set drifted")
    ablation_primary: dict[str, dict[str, Any]] = {}
    for experiment_id, control in ABLATION_CONTROLS.items():
        reports = _mapping(ablations[experiment_id], experiment_id)
        if set(reports) != set(metrics):
            raise DynamicResultsPending(f"{experiment_id} metric registry drifted")
        for metric, report in reports.items():
            if not isinstance(report, Mapping):
                raise DynamicResultsPending(f"{experiment_id}.{metric} is invalid")
            if report.get("direction") != f"graph_full_minus_{control}" or report.get(
                "horizon"
            ) != 12:
                raise DynamicResultsPending(f"{experiment_id}.{metric} identity drifted")
        ablation_primary[experiment_id] = _validate_task_contrast(
            reports[PRIMARY_METRIC],
            label=f"{experiment_id}.{PRIMARY_METRIC}",
            horizon=12,
            treatment="graph_full",
            control=control,
            by_cell=by_cell,
            holm=True,
        )
    adjusted = _holm(
        {
            experiment_id: report.get("exact_two_sided_cluster_swap_p")
            for experiment_id, report in ablation_primary.items()
        }
    )
    for experiment_id, expected in adjusted.items():
        _same_number(
            ablation_primary[experiment_id].get("holm_adjusted_p"),
            expected,
            f"{experiment_id}.Holm p",
        )

    metric_index = {metric: index for index, metric in enumerate(metrics)}
    mechanism_metric_union = set(P2_E7_DYNAMIC_METRICS)
    for registered in MECHANISM_ABLATION_METRICS.values():
        mechanism_metric_union.update(registered)
    if mechanism_metric_union & set(TASK_COHORT_METRICS):
        raise DynamicResultsPending("mechanism registry contains a task metric")
    if not mechanism_metric_union.issubset(set(metrics)):
        raise DynamicResultsPending("mechanism registry contains an unknown metric")

    bootstrap_base = int(protocol["statistics"]["bootstrap_seed"])
    validated_mechanisms: dict[str, dict[str, dict[str, Any]]] = {
        experiment_id: {} for experiment_id in ABLATION_CONTROLS
    }
    for metric in sorted(mechanism_metric_union, key=metric_index.__getitem__):
        family: dict[str, dict[str, Any]] = {}
        for experiment_index, (experiment_id, control) in enumerate(
            ABLATION_CONTROLS.items()
        ):
            report = _validate_episode_contrast(
                ablations[experiment_id][metric],
                label=f"{experiment_id}.{metric}",
                metric=metric,
                horizon=12,
                treatment="graph_full",
                control=control,
                by_cell=by_cell,
                expected_bootstrap_seed=(
                    bootstrap_base
                    + 10000
                    + experiment_index * 1000
                    + metric_index[metric]
                ),
                holm=True,
            )
            family[experiment_id] = report
            validated_mechanisms[experiment_id][metric] = report
        expected_adjusted = _holm(
            {
                experiment_id: report.get(
                    "exact_two_sided_sign_permutation_p"
                )
                for experiment_id, report in family.items()
            }
        )
        for experiment_id, expected in expected_adjusted.items():
            _same_number(
                family[experiment_id].get("holm_adjusted_p"),
                expected,
                f"{experiment_id}.{metric}.Holm p",
            )

    e7_reactive: dict[str, dict[str, Any]] = {}
    for metric in P2_E7_DYNAMIC_METRICS:
        e7_reactive[metric] = _validate_episode_contrast(
            by_horizon["12"][metric],
            label=f"P2-E7.graph_full_minus_reactive.{metric}",
            metric=metric,
            horizon=12,
            treatment="graph_full",
            control="reactive",
            by_cell=by_cell,
            expected_bootstrap_seed=(
                bootstrap_base + 2000 + metric_index[metric]
            ),
            holm=False,
        )

    p2e7 = _mapping(contrasts["P2-E7"], "P2-E7")
    if p2e7 != {
        "new_episode_bundles_added": 0,
        "reused_horizon_12_cells": [
            "reactive",
            "graph_full",
            "graph_no_observation_conditioned_branching",
        ],
        "dynamic_metrics": list(protocol["metrics"]["dynamic_behavior"]),
        "registered_report_sources": {
            "graph_full_minus_reactive": (
                "P2-E2.graph_full_minus_reactive_by_horizon.12"
            ),
            "graph_full_minus_graph_no_observation_conditioned_branching": (
                "P2-E3_to_P2-E6.P2-E4"
            ),
        },
        "claim_boundary": (
            "Operating-condition identifier changes only; no fault onset, "
            "event-F1, detection-delay, or physical-time claim."
        ),
    }:
        raise DynamicResultsPending("P2-E7 reuse or claim boundary drifted")
    if not isinstance(result.get("claim_boundary"), str) or not result["claim_boundary"]:
        raise DynamicResultsPending("dynamic result claim boundary is missing")

    rows: list[dict[str, Any]] = []
    for horizon in (3, 6, 12):
        report = horizon_primary[str(horizon)]
        rows.append(
            {
                "kind": "task_primary",
                "id": "P2-E2",
                "metric": PRIMARY_METRIC,
                "label": f"Graph full - Reactive, h={horizon}",
                "horizon": str(horizon),
                "treatment": _primary_cell(by_cell, horizon, "graph_full")["estimate"],
                "control": _primary_cell(by_cell, horizon, "reactive")["estimate"],
                "estimate": report["estimate"],
                "interval": report["paired_cluster_bootstrap_95ci"],
                "valid_replicates": report[
                    "paired_cluster_bootstrap_valid_replicates"
                ],
                "bootstrap_replicates": BOOTSTRAP_ITERATIONS,
                "p": report["exact_two_sided_cluster_swap_p"],
                "holm": None,
                "holm_registered": False,
                "windows": f"{24 * horizon}/{24 * horizon}",
            }
        )
    rows.append(
        {
            "kind": "task_primary",
            "id": "P2-E2",
            "metric": PRIMARY_METRIC,
            "label": "(Graph full - Reactive), h=12 minus h=3",
            "horizon": "12-3",
            "treatment": None,
            "control": None,
            "estimate": interaction["estimate"],
            "interval": interaction["paired_cluster_bootstrap_95ci"],
            "valid_replicates": interaction[
                "paired_cluster_bootstrap_valid_replicates"
            ],
            "bootstrap_replicates": BOOTSTRAP_ITERATIONS,
            "p": interaction["exact_two_sided_cluster_swap_p"],
            "holm": interaction["holm_adjusted_p"],
            "holm_registered": True,
            "windows": "288/288; 72/72",
        }
    )
    for experiment_id, control in ABLATION_CONTROLS.items():
        report = ablation_primary[experiment_id]
        rows.append(
            {
                "kind": "task_primary",
                "id": experiment_id,
                "metric": PRIMARY_METRIC,
                "label": f"Graph full - {CELL_DISPLAY[control]}",
                "horizon": "12",
                "treatment": _primary_cell(by_cell, 12, "graph_full")["estimate"],
                "control": _primary_cell(by_cell, 12, control)["estimate"],
                "estimate": report["estimate"],
                "interval": report["paired_cluster_bootstrap_95ci"],
                "valid_replicates": report[
                    "paired_cluster_bootstrap_valid_replicates"
                ],
                "bootstrap_replicates": BOOTSTRAP_ITERATIONS,
                "p": report["exact_two_sided_cluster_swap_p"],
                "holm": report["holm_adjusted_p"],
                "holm_registered": True,
                "windows": "288/288",
            }
        )

    for experiment_id, control in ABLATION_CONTROLS.items():
        display_id = (
            "P2-E4 / P2-E7" if experiment_id == "P2-E4" else experiment_id
        )
        for metric in MECHANISM_ABLATION_METRICS[experiment_id]:
            report = validated_mechanisms[experiment_id][metric]
            treatment_cell = _episode_cell(
                by_cell, horizon=12, cell="graph_full", metric=metric
            )
            control_cell = _episode_cell(
                by_cell, horizon=12, cell=control, metric=metric
            )
            rows.append(
                {
                    "kind": "mechanism",
                    "id": display_id,
                    "metric": metric,
                    "label": f"Graph full - {CELL_DISPLAY[control]}",
                    "horizon": "12",
                    "treatment": treatment_cell["estimate"],
                    "control": control_cell["estimate"],
                    "estimate": report["estimate"],
                    "interval": report["paired_cluster_bootstrap_95ci"],
                    "valid_replicates": report[
                        "paired_cluster_bootstrap_valid_replicates"
                    ],
                    "bootstrap_replicates": report[
                        "paired_cluster_bootstrap_iterations"
                    ],
                    "p": report["exact_two_sided_sign_permutation_p"],
                    "holm": report["holm_adjusted_p"],
                    "holm_registered": True,
                    "defined": (
                        f"{report['defined_seed_pair_numerator']}/24 pairs; "
                        f"{report['defined_public_sequence_cluster_numerator']}/8 clusters"
                    ),
                }
            )
    for metric in P2_E7_DYNAMIC_METRICS:
        report = e7_reactive[metric]
        treatment_cell = _episode_cell(
            by_cell, horizon=12, cell="graph_full", metric=metric
        )
        control_cell = _episode_cell(
            by_cell, horizon=12, cell="reactive", metric=metric
        )
        rows.append(
            {
                "kind": "mechanism",
                "id": "P2-E7",
                "metric": metric,
                "label": "Graph full - Benchmark Generic (Reactive-equivalent)",
                "horizon": "12",
                "treatment": treatment_cell["estimate"],
                "control": control_cell["estimate"],
                "estimate": report["estimate"],
                "interval": report["paired_cluster_bootstrap_95ci"],
                "valid_replicates": report[
                    "paired_cluster_bootstrap_valid_replicates"
                ],
                "bootstrap_replicates": report[
                    "paired_cluster_bootstrap_iterations"
                ],
                "p": report["exact_two_sided_sign_permutation_p"],
                "holm": None,
                "holm_registered": False,
                "defined": (
                    f"{report['defined_seed_pair_numerator']}/24 pairs; "
                    f"{report['defined_public_sequence_cluster_numerator']}/8 clusters"
                ),
            }
        )
    return rows


def validate_dynamic_inputs(
    *,
    protocol: Mapping[str, Any],
    result: Mapping[str, Any],
    acceptance: Mapping[str, Any],
) -> list[dict[str, Any]]:
    """Validate accepted artifacts and return separate task/mechanism rows."""

    try:
        return _validate_result(result, acceptance, protocol)
    except DynamicResultsPending:
        raise
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise DynamicResultsPending("dynamic formal artifact structure drifted") from exc


def _format_number(value: Any, *, signed: bool = False) -> str:
    if value is None:
        return "N/A"
    number = _finite(value, "display value")
    return f"{number:+.4f}" if signed else f"{number:.4f}"


def _format_effect(row: Mapping[str, Any]) -> str:
    estimate = row["estimate"]
    interval = row["interval"]
    if estimate is None:
        return "N/A [N/A, N/A]"
    if interval is None:
        return f"{_format_number(estimate, signed=True)} [N/A, N/A]"
    if not isinstance(interval, list) or len(interval) != 2:
        raise DynamicResultsPending("defined display effect has an invalid interval")
    return (
        f"{_format_number(estimate, signed=True)} "
        f"[{_format_number(interval[0], signed=True)}, "
        f"{_format_number(interval[1], signed=True)}]"
    )


def render_table(rows: Sequence[Mapping[str, Any]]) -> str:
    task_rows = [row for row in rows if row.get("kind") == "task_primary"]
    mechanism_rows = [row for row in rows if row.get("kind") == "mechanism"]
    if len(task_rows) != 8 or len(mechanism_rows) != 26:
        raise DynamicResultsPending("dynamic display row topology drifted")
    lines = [
        "# Accepted dynamic-v3 task-primary results",
        "",
        "| ID | Registered contrast | Horizon | Treatment AP | Control AP | Delta AP [95% paired cluster bootstrap CI] | Valid bootstrap replicates | Exact p | Holm p | Assigned windows T/C |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in task_rows:
        holm = (
            _format_number(row["holm"])
            if row["holm_registered"]
            else "—"
        )
        lines.append(
            "| {id} | {label} | {horizon} | {treatment} | {control} | "
            "{effect} | {valid}/{total} | {p} | {holm} | {windows} |".format(
                id=row["id"],
                label=row["label"],
                horizon=row["horizon"],
                treatment=_format_number(row["treatment"]),
                control=_format_number(row["control"]),
                effect=_format_effect(row),
                valid=row["valid_replicates"],
                total=row["bootstrap_replicates"],
                p=_format_number(row["p"]),
                holm=holm,
                windows=row["windows"],
            )
        )
    lines.extend(
        [
            "",
            "AP is recomputed within each seed over all eight assigned bearing sequences; each absolute cell contains 24 episodes. Delta is treatment minus control. The 10,000-resample interval and exact 256-way test use matched bearing clusters and retain failed or partial windows under `phase1_replay_target_adverse_missing_score_v1`. Holm adjustment applies to the four ablations and the separately registered horizon interaction; undefined values remain N/A.",
            "",
            "## Registered secondary mechanism outcomes",
            "",
            "| ID | Registered contrast | Metric | Horizon | Treatment | Control | Delta [95% paired cluster bootstrap CI] | Valid bootstrap replicates | Exact p | Holm p | Defined evidence |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in mechanism_rows:
        holm = (
            _format_number(row["holm"])
            if row["holm_registered"]
            else "—"
        )
        lines.append(
            "| {id} | {label} | `{metric}` | {horizon} | {treatment} | "
            "{control} | {effect} | {valid}/{total} | {p} | {holm} | {defined} |".format(
                id=row["id"],
                label=row["label"],
                metric=row["metric"],
                horizon=row["horizon"],
                treatment=_format_number(row["treatment"]),
                control=_format_number(row["control"]),
                effect=_format_effect(row),
                valid=row["valid_replicates"],
                total=row["bootstrap_replicates"],
                p=_format_number(row["p"]),
                holm=holm,
                defined=row["defined"],
            )
        )
    lines.extend(
        [
            "",
            "Mechanism rows are secondary explanatory outcomes and are never pooled with task-primary AP. Each delta is Graph full minus the named control at horizon 12. The four-ablation Holm family is recomputed separately for each displayed metric. `P2-E4 / P2-E7` is one reused full-versus-no-branching report, not a duplicated episode denominator; the additional P2-E7 rows compare Graph full with Reactive on the same registered operating-condition deliveries. P2-E7 supports no fault-onset, event-F1, detection-delay, or physical-time interpretation. Incomplete paired clusters retain a point estimate over complete clusters but show N/A inference; undefined episode values are never imputed as zero.",
            "",
        ]
    )
    return "\n".join(lines)


def render_svg(rows: Sequence[Mapping[str, Any]]) -> str:
    rows = [row for row in rows if row.get("kind") == "task_primary"]
    if len(rows) != 8:
        raise DynamicResultsPending("task-primary SVG row topology drifted")
    width = 1120
    left = 390
    right = 70
    top = 74
    row_height = 45
    plot_width = width - left - right
    height = top + row_height * len(rows) + 78

    def x(value: float) -> float:
        return left + ((value + 2.0) / 4.0) * plot_width

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Accepted dynamic-v3 task-primary contrasts</title>',
        '<desc id="desc">Point estimates and paired bearing-cluster bootstrap intervals for registered target-adverse Average Precision contrasts.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Inter,Arial,sans-serif;fill:#172033}.title{font-size:22px;font-weight:700}.label{font-size:13px}.tick{font-size:12px;fill:#596579}.na{font-size:12px;fill:#7b8494}.ci{stroke:#2962a3;stroke-width:3}.point{fill:#0b7a75;stroke:#ffffff;stroke-width:1.5}.zero{stroke:#8591a3;stroke-width:1.5;stroke-dasharray:5 4}.grid{stroke:#e1e6ee;stroke-width:1}</style>',
        '<text class="title" x="24" y="34">Dynamic-v3 target-adverse AP contrasts</text>',
        '<text class="tick" x="24" y="56">Delta = treatment - control; 95% paired bearing-cluster bootstrap CI</text>',
    ]
    for tick in (-2.0, -1.0, 0.0, 1.0, 2.0):
        tick_x = x(tick)
        css = "zero" if tick == 0.0 else "grid"
        parts.append(
            f'<line class="{css}" x1="{tick_x:.2f}" y1="{top - 18}" x2="{tick_x:.2f}" y2="{height - 48}"/>'
        )
        parts.append(
            f'<text class="tick" x="{tick_x:.2f}" y="{height - 25}" text-anchor="middle">{tick:+.1f}</text>'
        )
    for index, row in enumerate(rows):
        y = top + index * row_height
        label = html.escape(f"{row['id']}  {row['label']}")
        parts.append(f'<text class="label" x="24" y="{y + 5}">{label}</text>')
        estimate = row["estimate"]
        interval = row["interval"]
        if estimate is None:
            parts.append(
                f'<text class="na" x="{left + 8}" y="{y + 5}">N/A</text>'
            )
            continue
        low, high = interval
        parts.append(
            f'<line class="ci" x1="{x(float(low)):.2f}" y1="{y}" x2="{x(float(high)):.2f}" y2="{y}"/>'
        )
        parts.append(
            f'<circle class="point" cx="{x(float(estimate)):.2f}" cy="{y}" r="5.5"/>'
        )
    parts.append("</svg>\n")
    return "\n".join(parts)


def _replace_block(source: str, content: str) -> str:
    if source.count(MANUSCRIPT_BEGIN) != 1 or source.count(MANUSCRIPT_END) != 1:
        raise DynamicResultsPending(
            "active manuscript needs one unique dynamic-v3 result marker pair"
        )
    prefix, remainder = source.split(MANUSCRIPT_BEGIN, 1)
    _, suffix = remainder.split(MANUSCRIPT_END, 1)
    return (
        f"{prefix}{MANUSCRIPT_BEGIN}\n\n{content.rstrip()}\n\n"
        f"{MANUSCRIPT_END}{suffix}"
    )


def render_manuscript_block(
    rows: Sequence[Mapping[str, Any]], *, figure_reference: str
) -> str:
    table = render_table(rows)
    table_body = table.split("\n", 2)[2]
    return "\n".join(
        [
            MANUSCRIPT_HEADING,
            "",
            "The dynamic-v3 gate accepted all 240 registered episode bundles: 24 episodes in each of ten horizon/profile cells across three seeds and eight held-out bearing sequences. The first table section reports eight preregistered target-adverse assigned-window Average Precision rows, including the horizon interaction and four ablation task effects. The second section reports 26 prespecified secondary mechanism rows for P2-E3--P2-E7 without pooling them with task performance. P2-E4 also supplies the single reused full-versus-no-observation-branching P2-E7 comparison; no episode denominator is duplicated. All estimates are retained regardless of direction, and P2-E7 is limited to public operating-condition identifier changes rather than fault onset, event-F1, detection delay, or physical time.",
            "",
            table_body.rstrip(),
            "",
            f"![Accepted dynamic-v3 task-primary contrasts]({figure_reference})",
        ]
    ) + "\n"


_replace_path = os.replace
_NEW_FILE_MODE = 0o644


def _lexical_path(path: Path) -> Path:
    """Normalize a path without following its final symlink identity."""

    return Path(os.path.abspath(os.fspath(path)))


def _declared_protocol_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value:
        raise DynamicResultsPending(f"dynamic protocol lacks {label}")
    path = Path(value)
    return _lexical_path(path if path.is_absolute() else ROOT / path)


def _paths_alias(left: Path, right: Path) -> bool:
    if _lexical_path(left) == _lexical_path(right):
        return True
    if left.exists() and right.exists():
        try:
            return os.path.samefile(left, right)
        except OSError:
            return False
    return False


def _protocol_source_paths(protocol_path: Path) -> list[Path]:
    sources: list[Path] = []
    current = _lexical_path(protocol_path)
    seen: set[Path] = set()
    while True:
        if current in seen:
            raise DynamicResultsPending(
                "dynamic protocol authority chain contains a cycle"
            )
        seen.add(current)
        _require_ordinary_single_link(
            current,
            label="dynamic protocol authority source",
            required=True,
        )
        sources.append(current)
        try:
            payload = yaml.safe_load(current.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise DynamicResultsPending(
                f"cannot inspect dynamic protocol authority chain: {current}"
            ) from exc
        if not isinstance(payload, Mapping):
            return sources
        extension = payload.get("extends_protocol")
        if extension is None:
            return sources
        if (
            not isinstance(extension, str)
            or not extension
            or Path(extension).name != extension
        ):
            raise DynamicResultsPending(
                "dynamic protocol extension must name one sibling authority"
            )
        current = _lexical_path(current.parent / extension)


def _path_is_within(path: Path, root: Path) -> bool:
    variants: list[tuple[Path, Path]] = [
        (_lexical_path(path), _lexical_path(root))
    ]
    try:
        variants.append((path.resolve(strict=False), root.resolve(strict=False)))
    except (OSError, RuntimeError) as exc:
        raise DynamicResultsPending(
            f"cannot resolve publication path boundary for {path}"
        ) from exc
    for candidate, boundary in variants:
        try:
            candidate.relative_to(boundary)
        except ValueError:
            continue
        return True
    return False


def _path_is_strictly_within(path: Path, root: Path) -> bool:
    """Require both lexical and resolved containment for trusted sources."""

    try:
        lexical = _lexical_path(path).relative_to(_lexical_path(root))
        resolved = path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    except (OSError, RuntimeError) as exc:
        raise DynamicResultsPending(
            f"cannot resolve trusted path boundary for {path}"
        ) from exc
    return lexical is not None and resolved is not None


def _require_ordinary_single_link(path: Path, *, label: str, required: bool) -> None:
    """Reject file identities that byte backups cannot faithfully restore."""

    try:
        metadata = path.lstat()
    except FileNotFoundError:
        if required:
            raise DynamicResultsPending(f"missing {label}: {path}")
        return
    except OSError as exc:
        raise DynamicResultsPending(f"cannot inspect {label}: {path}") from exc
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
        raise DynamicResultsPending(
            f"{label} must be an ordinary single-link regular file: {path}"
        )


def _require_publication_boundary(
    *,
    protocol_path: Path,
    sources: Sequence[Path],
    targets: Sequence[Path],
    protected_roots: Sequence[Path],
) -> None:
    lexical_paths = [
        _lexical_path(path)
        for path in [protocol_path, *sources, *targets, *protected_roots]
    ]
    try:
        boundary = Path(os.path.commonpath([os.fspath(path) for path in lexical_paths]))
    except ValueError as exc:
        raise DynamicResultsPending("publication paths do not share one authority root") from exc
    for path in [*targets, *protected_roots]:
        if not _path_is_strictly_within(path, boundary):
            raise DynamicResultsPending(
                f"publication path resolves outside its authority root: {path}"
            )


def _require_production_cli_paths(
    *,
    protocol_path: Path,
    sources: Sequence[Path],
    targets: Sequence[Path],
) -> None:
    if _lexical_path(protocol_path) != _lexical_path(DEFAULT_PROTOCOL):
        raise DynamicResultsPending(
            "production CLI requires the registered dynamic-v3 protocol"
        )
    for source in [protocol_path, *sources]:
        if not _path_is_strictly_within(source, ROOT):
            raise DynamicResultsPending(
                f"production publication input resolves outside the repository: {source}"
            )
    for target in targets:
        if not _path_is_strictly_within(target, ROOT):
            raise DynamicResultsPending(
                f"production publication output resolves outside the repository: {target}"
            )


def _require_declared_publication_paths(
    *,
    protocol: Mapping[str, Any],
    result_path: Path,
    acceptance_path: Path,
    table_path: Path,
    figure_path: Path,
    manuscript_path: Path,
) -> tuple[list[Path], list[Path]]:
    outputs = _mapping(protocol.get("output_contract"), "output_contract")
    supplied = {
        "output_contract.formal_result": result_path,
        "output_contract.formal_acceptance": acceptance_path,
        "output_contract.accepted_manuscript_table": table_path,
        "output_contract.accepted_manuscript_figure": figure_path,
        "output_contract.accepted_manuscript": manuscript_path,
    }
    for label, path in supplied.items():
        key = label.rsplit(".", 1)[1]
        if _lexical_path(path) != _declared_protocol_path(outputs.get(key), label):
            raise DynamicResultsPending(
                f"publication path differs from dynamic protocol {label}"
            )
    formal_root = _declared_protocol_path(
        outputs.get("formal_root"), "output_contract.formal_root"
    )
    results_root = _declared_protocol_path(
        outputs.get("results_root"), "output_contract.results_root"
    )
    for key in ("formal_result", "formal_acceptance"):
        if not _path_is_strictly_within(
            _declared_protocol_path(outputs.get(key), f"output_contract.{key}"),
            results_root,
        ):
            raise DynamicResultsPending(
                f"dynamic protocol {key} must be inside output_contract.results_root"
            )
    protected_roots = [formal_root, results_root]
    return [table_path, figure_path, manuscript_path], protected_roots


def _require_safe_publication_paths(
    targets: Sequence[Path],
    *,
    sources: Sequence[Path],
    protected_roots: Sequence[Path],
) -> None:
    for index, target in enumerate(targets):
        for other in targets[index + 1 :]:
            if _paths_alias(target, other):
                raise DynamicResultsPending(
                    f"publication outputs must be distinct: {target} aliases {other}"
                )
        for source in sources:
            if _paths_alias(target, source):
                raise DynamicResultsPending(
                    f"publication output must not overwrite an input authority: {target}"
                )
    for source in sources:
        _require_ordinary_single_link(
            source, label="publication input authority", required=True
        )
    for target in targets:
        for root in protected_roots:
            if _path_is_within(target, root):
                raise DynamicResultsPending(
                    f"publication output must not be inside an input root: {target}"
                )
        _require_ordinary_single_link(
            target, label="existing publication output", required=False
        )


def _manuscript_reference(target: Path, manuscript: Path) -> str:
    return Path(
        os.path.relpath(_lexical_path(target), start=_lexical_path(manuscript).parent)
    ).as_posix()


def _stage_bytes(path: Path, payload: bytes, mode: int) -> Path:
    handle = tempfile.NamedTemporaryFile(
        mode="wb",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    )
    temporary_path = Path(handle.name)
    try:
        handle.write(payload)
        handle.flush()
        os.fchmod(handle.fileno(), mode)
        os.fsync(handle.fileno())
    except Exception:
        handle.close()
        if temporary_path.exists():
            temporary_path.unlink()
        raise
    handle.close()
    return temporary_path


def _write_group_with_exception_rollback(contents: Mapping[Path, str]) -> None:
    for path in contents:
        if not path.parent.is_dir():
            raise DynamicResultsPending(
                f"publication parent directory does not exist: {path.parent}"
            )
    originals: dict[Path, tuple[bytes | None, int]] = {}
    for path in contents:
        _require_ordinary_single_link(
            path, label="existing publication output", required=False
        )
        if path.exists():
            originals[path] = (
                path.read_bytes(),
                stat.S_IMODE(path.stat().st_mode),
            )
        else:
            originals[path] = (None, _NEW_FILE_MODE)

    staged: dict[Path, Path] = {}
    backups: dict[Path, Path] = {}
    replaced: list[Path] = []
    try:
        for path, content in contents.items():
            staged[path] = _stage_bytes(
                path,
                content.encode("utf-8"),
                originals[path][1],
            )
        for path, (payload, mode) in originals.items():
            if payload is not None:
                backups[path] = _stage_bytes(path, payload, mode)
        for path in contents:
            _replace_path(staged[path], path)
            replaced.append(path)
    except Exception as exc:
        rollback_errors: list[Exception] = []
        for path in reversed(replaced):
            try:
                backup = backups.get(path)
                if backup is None:
                    if path.exists():
                        path.unlink()
                else:
                    _replace_path(backup, path)
            except Exception as rollback_exc:  # pragma: no cover - catastrophic I/O
                rollback_errors.append(rollback_exc)
        if rollback_errors:
            raise RuntimeError(
                "dynamic publication replacement failed and rollback was incomplete"
            ) from exc
        raise
    finally:
        for temporary_path in [*staged.values(), *backups.values()]:
            if temporary_path.exists():
                temporary_path.unlink()


def write_dynamic_manuscript(
    *,
    protocol_path: Path,
    result_path: Path,
    acceptance_path: Path,
    table_path: Path,
    figure_path: Path,
    manuscript_path: Path,
) -> dict[str, Any]:
    """Validate all inputs, then update all three manuscript products."""

    protocol_sources = _protocol_source_paths(protocol_path)
    protocol = load_protocol(protocol_path)
    targets, protected_roots = _require_declared_publication_paths(
        protocol=protocol,
        result_path=result_path,
        acceptance_path=acceptance_path,
        table_path=table_path,
        figure_path=figure_path,
        manuscript_path=manuscript_path,
    )
    sources = [
        *protocol_sources,
        result_path,
        acceptance_path,
    ]
    _require_publication_boundary(
        protocol_path=protocol_path,
        sources=sources,
        targets=targets,
        protected_roots=protected_roots,
    )
    _require_safe_publication_paths(
        targets,
        sources=sources,
        protected_roots=protected_roots,
    )
    result = _load_json(result_path, "dynamic formal result")
    acceptance = _load_json(acceptance_path, "dynamic formal acceptance")
    rows = validate_dynamic_inputs(
        protocol=protocol, result=result, acceptance=acceptance
    )
    if not manuscript_path.is_file():
        raise DynamicResultsPending(f"missing active manuscript: {manuscript_path}")
    source = manuscript_path.read_text(encoding="utf-8")
    table = render_table(rows)
    figure = render_svg(rows)
    manuscript = _replace_block(
        source,
        render_manuscript_block(
            rows,
            figure_reference=_manuscript_reference(figure_path, manuscript_path),
        ),
    )
    _write_group_with_exception_rollback(
        {
            table_path: table,
            figure_path: figure,
            manuscript_path: manuscript,
        }
    )
    return {
        "schema_version": "p2_dynamic_formal_manuscript_render_v2",
        "status": "accepted_dynamic_v3_inserted",
        "registered_rows": len(rows),
        "task_primary_rows": sum(
            row.get("kind") == "task_primary" for row in rows
        ),
        "secondary_mechanism_rows": sum(
            row.get("kind") == "mechanism" for row in rows
        ),
        "formal_episode_bundles": EXPECTED_FORMAL_UNITS,
        "provider_calls_performed_by_renderer": False,
        "raw_run_or_private_data_reads_performed_by_renderer": False,
        "table": str(table_path),
        "figure": str(figure_path),
        "manuscript": str(manuscript_path),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Render an accepted dynamic-v3 result into Paper 2."
    )
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--result", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--acceptance", type=Path, default=DEFAULT_ACCEPTANCE)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    args = parser.parse_args(argv)
    _require_production_cli_paths(
        protocol_path=args.protocol,
        sources=[],
        targets=[],
    )
    production_sources = [
        *_protocol_source_paths(args.protocol),
        args.result,
        args.acceptance,
    ]
    _require_production_cli_paths(
        protocol_path=args.protocol,
        sources=production_sources,
        targets=[args.table, args.figure, args.manuscript],
    )
    summary = write_dynamic_manuscript(
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
