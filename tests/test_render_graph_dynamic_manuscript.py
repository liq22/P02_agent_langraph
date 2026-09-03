from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

from scripts.analyze_graph_dynamic_formal import (
    ACCEPTANCE_SCHEMA,
    MECHANISM_ABLATION_METRICS,
    P2_E7_DYNAMIC_METRICS,
    RESULT_SCHEMA,
    REPLAY_MISSING_SCORE_POLICY_ID,
    _holm,
    _registered_metrics,
    load_protocol,
    registered_cells,
)
from scripts.render_graph_dynamic_manuscript import (
    MANUSCRIPT_BEGIN,
    MANUSCRIPT_END,
    PRIMARY_METRIC,
    DynamicResultsPending,
    validate_dynamic_inputs,
    write_dynamic_manuscript,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
SEEDS = (20260808, 20260809, 20260810)


class DynamicManuscriptRendererTest(unittest.TestCase):
    def _json(self, path: Path, value: object) -> Path:
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        return path

    def _fixture(
        self, output_root: Path, *, undefined_h3: bool = False
    ) -> tuple[dict, dict, dict]:
        protocol = load_protocol(PROTOCOL)
        metrics = _registered_metrics(protocol)
        values: dict[tuple[int, str], list[float | None]] = {
            (3, "reactive"): [0.40, 0.45, 0.50],
            (3, "graph_full"): [0.50, 0.55, None if undefined_h3 else 0.60],
            (6, "reactive"): [0.45, 0.50, 0.55],
            (6, "graph_full"): [0.57, 0.62, 0.67],
            (12, "reactive"): [0.50, 0.55, 0.60],
            (12, "graph_full"): [0.68, 0.73, 0.78],
            (12, "graph_no_recovery_revision_edge"): [0.63, 0.68, 0.73],
            (12, "graph_no_observation_conditioned_branching"): [0.60, 0.65, 0.70],
            (12, "graph_no_persistent_graph_state"): [0.58, 0.63, 0.68],
            (12, "graph_no_replanning"): [0.61, 0.66, 0.71],
        }

        def task_cell(horizon: int, cell: str) -> dict:
            seed_values = values[(horizon, cell)]
            defined = [value for value in seed_values if value is not None]
            assigned = 24 * horizon
            return {
                "estimate": sum(defined) / len(defined) if defined else None,
                "aggregation": "mean_of_seed_level_metrics_each_recomputed_over_all_eight_bearing_sequences",
                "seed_estimates": {
                    str(seed): value for seed, value in zip(SEEDS, seed_values, strict=True)
                },
                "defined_seed_numerator": len(defined),
                "registered_seed_denominator": 3,
                "assigned_episode_denominator": 24,
                "assigned_window_denominator": assigned,
                "submitted_window_numerator": assigned,
                "missing_assigned_scores": 0,
                "score_coverage": 1.0,
                "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                "per_bearing_metric_averaging_performed": False,
                "undefined_values_imputed_as_zero": False,
            }

        dynamic_values = {
            "steps_from_event_to_next_successful_action": {
                "reactive": 2.0,
                "graph_full": 0.0,
                "graph_no_recovery_revision_edge": 1.0,
                "graph_no_observation_conditioned_branching": 1.5,
                "graph_no_persistent_graph_state": 1.0,
                "graph_no_replanning": 1.25,
            },
            "steps_from_event_to_next_model_prediction": {
                "reactive": 4.0,
                "graph_full": 2.0,
                "graph_no_recovery_revision_edge": 3.0,
                "graph_no_observation_conditioned_branching": 3.5,
                "graph_no_persistent_graph_state": 3.0,
                "graph_no_replanning": 3.25,
            },
            "post_event_repeated_action_ratio": {
                "reactive": 0.40,
                "graph_full": 0.10,
                "graph_no_recovery_revision_edge": 0.20,
                "graph_no_observation_conditioned_branching": 0.30,
                "graph_no_persistent_graph_state": 0.25,
                "graph_no_replanning": 0.35,
            },
            "post_event_budget_exhaustion_rate": {
                "reactive": 0.20,
                "graph_full": 0.00,
                "graph_no_recovery_revision_edge": 0.05,
                "graph_no_observation_conditioned_branching": 0.10,
                "graph_no_persistent_graph_state": 0.05,
                "graph_no_replanning": 0.15,
            },
        }

        def episode_value(horizon: int, cell: str, metric: str) -> float | None:
            if metric == "operating_condition_event_delivery_count":
                return {3: 0.0, 6: 1.0, 12: 3.0}[horizon]
            if metric == "event_to_Monitor_transition_rate":
                if horizon == 3 or cell == "reactive":
                    return None
                return (
                    0.0
                    if cell == "graph_no_observation_conditioned_branching"
                    else 1.0
                )
            if metric == "event_to_Revise_transition_rate":
                if horizon == 3 or cell == "reactive":
                    return None
                return 1.0 if cell == "graph_full" else 0.0
            if metric in dynamic_values:
                return None if horizon == 3 else dynamic_values[metric][cell]
            if metric == "grounded_recovery_success":
                return {
                    "reactive": 0.50,
                    "graph_full": 0.90,
                    "graph_no_recovery_revision_edge": 0.20,
                    "graph_no_observation_conditioned_branching": 0.70,
                    "graph_no_persistent_graph_state": 0.60,
                    "graph_no_replanning": 0.65,
                }[cell]
            if metric == "steps_to_next_success_after_failure":
                return {
                    "reactive": 4.0,
                    "graph_full": 2.0,
                    "graph_no_recovery_revision_edge": 5.0,
                    "graph_no_observation_conditioned_branching": 3.0,
                    "graph_no_persistent_graph_state": 3.5,
                    "graph_no_replanning": 3.0,
                }[cell]
            if metric == "repeated_action_ratio":
                return {
                    "reactive": 0.40,
                    "graph_full": 0.10,
                    "graph_no_recovery_revision_edge": 0.20,
                    "graph_no_observation_conditioned_branching": 0.30,
                    "graph_no_persistent_graph_state": 0.35,
                    "graph_no_replanning": 0.30,
                }[cell]
            if metric == "loop_incidence":
                return {
                    "reactive": 0.50,
                    "graph_full": 0.10,
                    "graph_no_recovery_revision_edge": 0.20,
                    "graph_no_observation_conditioned_branching": 0.30,
                    "graph_no_persistent_graph_state": 0.40,
                    "graph_no_replanning": 0.30,
                }[cell]
            return 1.0

        def episode_cell(horizon: int, cell: str, metric: str) -> dict:
            value = episode_value(horizon, cell, metric)
            seed_sequence_values = {
                str(seed): {
                    f"sequence-{index:04d}": value for index in range(1, 9)
                }
                for seed in SEEDS
            }
            return {
                "estimate": value,
                "seed_sequence_values": seed_sequence_values,
                "defined_episode_numerator": 0 if value is None else 24,
                "assigned_episode_denominator": 24,
                "undefined_values_imputed_as_zero": False,
            }

        by_cell: dict[str, dict] = {}
        for cell in registered_cells(protocol):
            cell_metrics = {}
            for metric in metrics:
                if metric in {
                    "target_adverse_window_average_precision",
                    "target_adverse_window_auroc",
                    "target_adverse_false_alarm_rate",
                    "target_adverse_true_positive_rate",
                    "replay_score_coverage",
                }:
                    cell_metrics[metric] = task_cell(cell.horizon, cell.name)
                else:
                    cell_metrics[metric] = episode_cell(
                        cell.horizon, cell.name, metric
                    )
            by_cell[cell.key] = {
                "horizon": cell.horizon,
                "cell": cell.name,
                "agent_profile_id": cell.agent_profile_id,
                "assigned_episode_denominator": 24,
                "terminal_status_counts": {"submitted": 24},
                "failure_kind_counts": {},
                "metrics": cell_metrics,
            }

        def contrast(
            horizon: int,
            treatment: str,
            control: str,
            *,
            pvalue: float,
            holm: bool,
        ) -> dict:
            differences = []
            for high, low in zip(
                values[(horizon, treatment)], values[(horizon, control)], strict=True
            ):
                differences.append(None if high is None or low is None else high - low)
            defined = [value for value in differences if value is not None]
            estimate = sum(defined) / 3 if len(defined) == 3 else None
            report = {
                "direction": f"{treatment}_minus_{control}",
                "horizon": horizon,
                "estimate": estimate,
                "seed_level_differences": {
                    str(seed): value
                    for seed, value in zip(SEEDS, differences, strict=True)
                },
                "paired_cluster_bootstrap_95ci": (
                    None if estimate is None else [estimate - 0.02, estimate + 0.02]
                ),
                "paired_cluster_bootstrap_valid_replicates": (
                    0 if estimate is None else 10000
                ),
                "exact_two_sided_cluster_swap_p": (
                    None if estimate is None else pvalue
                ),
                "exact_cluster_swap_assignments": 0 if estimate is None else 256,
                "defined_seed_pair_numerator": len(defined),
                "assigned_seed_pair_denominator": 3,
                "matched_bearing_sequence_clusters": 8,
                "treatment_assigned_episode_denominator": 24,
                "control_assigned_episode_denominator": 24,
                "treatment_assigned_windows": 24 * horizon,
                "control_assigned_windows": 24 * horizon,
                "treatment_missing_assigned_scores": 0,
                "control_missing_assigned_scores": 0,
                "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                "metric_recomputed_after_each_cluster_draw_or_swap": True,
                "per_bearing_metric_averaging_performed": False,
                "undefined_values_imputed_as_zero": False,
            }
            if holm:
                report["holm_adjusted_p"] = None
            return report

        horizon_primary = {
            "3": contrast(3, "graph_full", "reactive", pvalue=0.125, holm=False),
            "6": contrast(6, "graph_full", "reactive", pvalue=0.0625, holm=False),
            "12": contrast(12, "graph_full", "reactive", pvalue=0.03125, holm=False),
        }

        h12 = horizon_primary["12"]["seed_level_differences"]
        h3 = horizon_primary["3"]["seed_level_differences"]
        interaction_values = {
            str(seed): (
                None
                if h12[str(seed)] is None or h3[str(seed)] is None
                else h12[str(seed)] - h3[str(seed)]
            )
            for seed in SEEDS
        }
        defined_interactions = [
            value for value in interaction_values.values() if value is not None
        ]
        interaction_estimate = (
            sum(defined_interactions) / 3
            if len(defined_interactions) == 3
            else None
        )
        interaction_p = None if interaction_estimate is None else 0.25
        interaction = {
            "direction": "(graph_full_minus_reactive)_h12_minus_h3",
            "estimate": interaction_estimate,
            "seed_level_interactions": interaction_values,
            "paired_cluster_bootstrap_95ci": (
                None
                if interaction_estimate is None
                else [interaction_estimate - 0.03, interaction_estimate + 0.03]
            ),
            "paired_cluster_bootstrap_valid_replicates": (
                0 if interaction_estimate is None else 10000
            ),
            "exact_two_sided_cluster_swap_p": interaction_p,
            "exact_cluster_swap_assignments": (
                0 if interaction_estimate is None else 256
            ),
            "defined_seed_interaction_numerator": len(defined_interactions),
            "assigned_seed_interaction_denominator": 3,
            "matched_bearing_sequence_clusters": 8,
            "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "metric_recomputed_after_each_cluster_draw_or_swap": True,
            "per_bearing_metric_averaging_performed": False,
            "nested_horizons_treated_as_independent": False,
            "undefined_values_imputed_as_zero": False,
            "holm_adjusted_p": interaction_p,
        }

        def other_contrast(horizon: int, treatment: str, control: str) -> dict:
            return {
                "direction": f"{treatment}_minus_{control}",
                "horizon": horizon,
            }

        def episode_contrast(
            horizon: int,
            treatment: str,
            control: str,
            metric: str,
            *,
            seed_offset: int,
            holm: bool,
        ) -> dict:
            treatment_values = by_cell[f"h{horizon}:{treatment}"]["metrics"][
                metric
            ]["seed_sequence_values"]
            control_values = by_cell[f"h{horizon}:{control}"]["metrics"][metric][
                "seed_sequence_values"
            ]
            seed_differences = {}
            clusters = {}
            defined_pairs = 0
            for sequence_index in range(1, 9):
                sequence_id = f"sequence-{sequence_index:04d}"
                paired = {}
                complete = []
                for seed in SEEDS:
                    key = str(seed)
                    treatment_value = treatment_values[key][sequence_id]
                    control_value = control_values[key][sequence_id]
                    difference = (
                        None
                        if treatment_value is None or control_value is None
                        else treatment_value - control_value
                    )
                    paired[key] = difference
                    if difference is not None:
                        complete.append(difference)
                        defined_pairs += 1
                seed_differences[sequence_id] = paired
                clusters[sequence_id] = (
                    sum(complete) / len(SEEDS)
                    if len(complete) == len(SEEDS)
                    else None
                )
            defined_clusters = [value for value in clusters.values() if value is not None]
            estimate = (
                sum(defined_clusters) / len(defined_clusters)
                if defined_clusters
                else None
            )
            if len(defined_clusters) == 8:
                interval = [estimate, estimate]
                observed = abs(estimate)
                exceed = 0
                for mask in range(256):
                    permuted = [
                        value if mask & (1 << index) else -value
                        for index, value in enumerate(defined_clusters)
                    ]
                    if abs(sum(permuted) / 8) >= observed - 1e-15:
                        exceed += 1
                pvalue = exceed / 256
                assignments = 256
                valid_replicates = 10000
            else:
                interval = None
                pvalue = None
                assignments = 0
                valid_replicates = 0
            report = {
                "direction": f"{treatment}_minus_{control}",
                "horizon": horizon,
                "estimate": estimate,
                "seed_level_differences_by_public_sequence": seed_differences,
                "public_sequence_cluster_differences": clusters,
                "paired_cluster_bootstrap_95ci": interval,
                "paired_cluster_bootstrap_iterations": 10000,
                "paired_cluster_bootstrap_seed": (
                    protocol["statistics"]["bootstrap_seed"] + seed_offset
                ),
                "paired_cluster_bootstrap_valid_replicates": valid_replicates,
                "exact_two_sided_sign_permutation_p": pvalue,
                "exact_sign_assignments": assignments,
                "defined_seed_pair_numerator": defined_pairs,
                "assigned_seed_pair_denominator": 24,
                "defined_public_sequence_cluster_numerator": len(defined_clusters),
                "registered_public_sequence_cluster_denominator": 8,
                "seeds_averaged_within_cluster_before_inference": True,
                "undefined_values_imputed_as_zero": False,
            }
            if holm:
                report["holm_adjusted_p"] = None
            return report

        mechanism_metric_union = set(P2_E7_DYNAMIC_METRICS)
        for registered in MECHANISM_ABLATION_METRICS.values():
            mechanism_metric_union.update(registered)
        metric_index = {metric: index for index, metric in enumerate(metrics)}

        by_horizon = {}
        for horizon in (3, 6, 12):
            by_horizon[str(horizon)] = {
                metric: (
                    horizon_primary[str(horizon)]
                    if metric == PRIMARY_METRIC
                    else episode_contrast(
                        horizon,
                        "graph_full",
                        "reactive",
                        metric,
                        seed_offset=2000 + metric_index[metric],
                        holm=False,
                    )
                    if horizon == 12 and metric in P2_E7_DYNAMIC_METRICS
                    else other_contrast(horizon, "graph_full", "reactive")
                )
                for metric in metrics
            }
        interactions = {
            metric: (
                interaction
                if metric == PRIMARY_METRIC
                else {"direction": "(graph_full_minus_reactive)_h12_minus_h3"}
            )
            for metric in metrics
        }

        controls = {
            "P2-E3": "graph_no_recovery_revision_edge",
            "P2-E4": "graph_no_observation_conditioned_branching",
            "P2-E5": "graph_no_persistent_graph_state",
            "P2-E6": "graph_no_replanning",
        }
        pvalues = {"P2-E3": 0.04, "P2-E4": 0.02, "P2-E5": 0.01, "P2-E6": 0.03}
        ablations = {}
        for experiment_id, control in controls.items():
            primary = contrast(
                12,
                "graph_full",
                control,
                pvalue=pvalues[experiment_id],
                holm=True,
            )
            ablations[experiment_id] = {
                metric: (
                    primary
                    if metric == PRIMARY_METRIC
                    else episode_contrast(
                        12,
                        "graph_full",
                        control,
                        metric,
                        seed_offset=(
                            10000
                            + list(controls).index(experiment_id) * 1000
                            + metric_index[metric]
                        ),
                        holm=True,
                    )
                    if metric in mechanism_metric_union
                    else other_contrast(12, "graph_full", control)
                )
                for metric in metrics
            }
        adjusted = _holm(pvalues)
        for experiment_id, value in adjusted.items():
            ablations[experiment_id][PRIMARY_METRIC]["holm_adjusted_p"] = value
        for metric in mechanism_metric_union:
            metric_adjusted = _holm(
                {
                    experiment_id: ablations[experiment_id][metric][
                        "exact_two_sided_sign_permutation_p"
                    ]
                    for experiment_id in controls
                }
            )
            for experiment_id, value in metric_adjusted.items():
                ablations[experiment_id][metric]["holm_adjusted_p"] = value

        cell_denominators = {cell.key: 24 for cell in registered_cells(protocol)}
        inclusion = {
            "scheduled_unit_denominator": 240,
            "effective_non_provider_terminal_count": 240,
            "retained_provider_failure_attempt_count": 0,
            "retained_non_provider_failure_count": 0,
            "terminal_status_counts": {"submitted": 240},
            "failure_kind_counts": {},
            "cell_denominators": cell_denominators,
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
        authority = {
            "target_source": "registered_private_data_port_assignment",
            "prediction_source": "canonical_rollout_successful_submit_prefix",
            "derived_evaluation_jsonl_ingested": False,
            "private_paths_serialized": False,
        }
        acceptance = {
            "schema_version": ACCEPTANCE_SCHEMA,
            "accepted": True,
            "protocol_id": protocol["protocol_id"],
            "provider_profile_id": protocol["runtime_and_provider_profile"][
                "formal_provider_profile_id"
            ],
            "output_root": str(output_root.resolve()),
            "expected_episode_bundles": 240,
            "observed_effective_non_provider_terminals": 240,
            "provider_calls_performed_by_gate": False,
            "grouping_contract": {
                "absolute_cell_key": ["horizon", "agent_profile_id"],
                "paired_unit": protocol["statistics"]["paired_unit"],
                "pool_episode_rows_across_horizons": False,
                "pool_across_provider_model_or_runtime_profiles": False,
            },
            "evaluator_authority": authority,
            "canonical_inclusion": inclusion,
            "errors": [],
        }
        result = {
            "schema_version": RESULT_SCHEMA,
            "status": "accepted_complete_formal_cohort_analysis",
            "protocol_id": protocol["protocol_id"],
            "provider_profile_id": protocol["runtime_and_provider_profile"][
                "formal_provider_profile_id"
            ],
            "output_root": str(output_root.resolve()),
            "provider_calls_performed_by_analyzer": False,
            "primary_endpoint_authority": authority,
            "canonical_inclusion": inclusion,
            "grouping_invariants": {
                "absolute_summaries_keyed_by_horizon_and_agent_profile": True,
                "task_primary_recomputed_over_all_assigned_windows_within_seed_cell": True,
                "per_bearing_average_precision_performed": False,
                "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                "pooled_headline_graph_effect_across_horizons": False,
                "pool_across_provider_model_or_runtime_profiles": False,
                "nested_horizons_treated_as_independent": False,
                "failed_non_provider_terminals_retained": True,
            },
            "by_cell": by_cell,
            "registered_contrasts": {
                "P2-E2": {
                    "graph_full_minus_reactive_by_horizon": by_horizon,
                    "registered_h12_minus_h3_interaction": interactions,
                },
                "P2-E3_to_P2-E6": ablations,
                "P2-E7": {
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
                },
            },
            "claim_boundary": "One frozen dynamic-v3 profile.",
        }
        return protocol, acceptance, result

    def _paths(self, root: Path, acceptance: dict, result: dict) -> dict[str, Path]:
        manuscript = root / "main.md"
        manuscript.write_text(
            "Before\n"
            f"{MANUSCRIPT_BEGIN}\n\npending\n\n{MANUSCRIPT_END}\n"
            "After\n",
            encoding="utf-8",
        )
        return {
            "protocol_path": PROTOCOL,
            "result_path": self._json(root / "result.json", result),
            "acceptance_path": self._json(root / "acceptance.json", acceptance),
            "table_path": root / "table.md",
            "figure_path": root / "figure.svg",
            "manuscript_path": manuscript,
        }

    def test_protocol_registers_the_accepted_only_consumer(self) -> None:
        protocol = load_protocol(PROTOCOL)
        consumer = protocol["formal_analysis"]["accepted_manuscript_consumer"]
        self.assertEqual(
            consumer["entrypoint"], "scripts/render_graph_dynamic_manuscript.py"
        )
        self.assertEqual(
            consumer["render_schema"],
            "p2_dynamic_formal_manuscript_render_v2",
        )
        self.assertIs(consumer["acceptance_required"], True)
        self.assertEqual(consumer["complete_episode_bundles_required"], 240)
        self.assertIs(consumer["raw_run_or_private_data_reads"], False)
        self.assertIs(consumer["provider_calls"], False)
        self.assertIs(consumer["displayed_primary_arithmetic_recomputed"], True)
        self.assertIs(consumer["displayed_mechanism_arithmetic_recomputed"], True)
        self.assertIs(consumer["displayed_holm_adjustment_recomputed"], True)
        self.assertIs(consumer["task_primary_and_mechanism_sections_separate"], True)
        self.assertIs(consumer["atomic_outputs"], True)
        self.assertEqual(consumer["task_primary_rows_after_acceptance"], 8)
        self.assertEqual(consumer["secondary_mechanism_rows_after_acceptance"], 26)
        mechanism = consumer["mechanism_reporting"]
        self.assertEqual(set(mechanism["ablation_rows"]), set(MECHANISM_ABLATION_METRICS))
        self.assertEqual(
            mechanism["operating_condition_change_rows"]["metrics"],
            list(P2_E7_DYNAMIC_METRICS),
        )
        self.assertIs(
            mechanism["operating_condition_change_rows"][
                "duplicate_no_branching_rows"
            ],
            False,
        )

    def test_accepted_result_writes_table_svg_and_unique_manuscript_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            summary = write_dynamic_manuscript(**paths)
            self.assertEqual(
                summary["schema_version"],
                "p2_dynamic_formal_manuscript_render_v2",
            )
            self.assertEqual(summary["registered_rows"], 34)
            self.assertEqual(summary["task_primary_rows"], 8)
            self.assertEqual(summary["secondary_mechanism_rows"], 26)
            self.assertFalse(summary["provider_calls_performed_by_renderer"])
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("P2-E6", table)
            self.assertIn("P2-E4 / P2-E7", table)
            self.assertIn("Registered secondary mechanism outcomes", table)
            self.assertIn("`event_to_Monitor_transition_rate`", table)
            self.assertIn("+0.1800", table)
            self.assertIn("accepted all 240 registered episode bundles", manuscript)
            self.assertIn("26 prespecified secondary mechanism rows", manuscript)
            self.assertEqual(manuscript.count(MANUSCRIPT_BEGIN), 1)
            self.assertEqual(manuscript.count(MANUSCRIPT_END), 1)
            self.assertNotIn(str(root / "formal"), table + manuscript)
            self.assertNotIn("private_target", table + manuscript)
            ET.parse(paths["figure_path"])

    def test_rejected_acceptance_leaves_all_outputs_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            acceptance["accepted"] = False
            paths = self._paths(root, acceptance, result)
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            originals = {
                key: paths[key].read_bytes()
                for key in ("table_path", "figure_path", "manuscript_path")
            }
            with self.assertRaises(DynamicResultsPending):
                write_dynamic_manuscript(**paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)

    def test_denominator_policy_and_bootstrap_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            cases = []
            wrong_denominator = copy.deepcopy(result)
            wrong_denominator["by_cell"]["h12:graph_full"]["metrics"][PRIMARY_METRIC][
                "assigned_window_denominator"
            ] = 287
            cases.append(wrong_denominator)
            wrong_policy = copy.deepcopy(result)
            wrong_policy["registered_contrasts"]["P2-E2"][
                "graph_full_minus_reactive_by_horizon"
            ]["12"][PRIMARY_METRIC]["missing_score_policy_id"] = "drop_failed"
            cases.append(wrong_policy)
            wrong_bootstrap = copy.deepcopy(result)
            wrong_bootstrap["registered_contrasts"]["P2-E2"][
                "graph_full_minus_reactive_by_horizon"
            ]["12"][PRIMARY_METRIC][
                "paired_cluster_bootstrap_valid_replicates"
            ] = 10001
            cases.append(wrong_bootstrap)
            for candidate in cases:
                with self.subTest(candidate=cases.index(candidate)):
                    with self.assertRaises(DynamicResultsPending):
                        validate_dynamic_inputs(
                            protocol=protocol,
                            result=candidate,
                            acceptance=acceptance,
                        )

    def test_displayed_delta_is_recomputed_from_seed_level_cells(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            report = result["registered_contrasts"]["P2-E2"][
                "graph_full_minus_reactive_by_horizon"
            ]["12"][PRIMARY_METRIC]
            report["seed_level_differences"]["20260809"] += 0.01
            with self.assertRaisesRegex(DynamicResultsPending, "arithmetic drifted"):
                validate_dynamic_inputs(
                    protocol=protocol, result=result, acceptance=acceptance
                )

    def test_holm_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            result["registered_contrasts"]["P2-E3_to_P2-E6"]["P2-E4"][
                PRIMARY_METRIC
            ]["holm_adjusted_p"] = 0.99
            with self.assertRaisesRegex(DynamicResultsPending, "Holm p"):
                validate_dynamic_inputs(
                    protocol=protocol, result=result, acceptance=acceptance
                )

    def test_mechanism_arithmetic_interval_and_holm_tamper_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, baseline = self._fixture(root / "formal")
            cases = []

            wrong_pair = copy.deepcopy(baseline)
            report = wrong_pair["registered_contrasts"]["P2-E3_to_P2-E6"][
                "P2-E6"
            ]["post_event_repeated_action_ratio"]
            report["seed_level_differences_by_public_sequence"][
                "sequence-0001"
            ]["20260809"] += 0.01
            cases.append(wrong_pair)

            wrong_interval = copy.deepcopy(baseline)
            wrong_interval["registered_contrasts"]["P2-E3_to_P2-E6"][
                "P2-E5"
            ]["loop_incidence"]["paired_cluster_bootstrap_95ci"][0] += 0.01
            cases.append(wrong_interval)

            wrong_holm = copy.deepcopy(baseline)
            wrong_holm["registered_contrasts"]["P2-E3_to_P2-E6"][
                "P2-E4"
            ]["event_to_Monitor_transition_rate"]["holm_adjusted_p"] = 0.99
            cases.append(wrong_holm)

            for index, candidate in enumerate(cases):
                with self.subTest(index=index):
                    with self.assertRaises(DynamicResultsPending):
                        validate_dynamic_inputs(
                            protocol=protocol,
                            result=candidate,
                            acceptance=acceptance,
                        )

    def test_p2e7_source_and_reporting_registry_drift_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            wrong_result = copy.deepcopy(result)
            wrong_result["registered_contrasts"]["P2-E7"][
                "registered_report_sources"
            ]["graph_full_minus_reactive"] = "unregistered"
            with self.assertRaisesRegex(DynamicResultsPending, "P2-E7 reuse"):
                validate_dynamic_inputs(
                    protocol=protocol,
                    result=wrong_result,
                    acceptance=acceptance,
                )

            wrong_protocol = copy.deepcopy(protocol)
            wrong_protocol["formal_analysis"]["accepted_manuscript_consumer"][
                "mechanism_reporting"
            ]["ablation_rows"]["P2-E6"]["metrics"].append("steps")
            with self.assertRaisesRegex(
                DynamicResultsPending, "P2-E6 mechanism reporting"
            ):
                validate_dynamic_inputs(
                    protocol=wrong_protocol,
                    result=result,
                    acceptance=acceptance,
                )

    def test_undefined_primary_effect_renders_na_without_directional_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(
                root / "formal", undefined_h3=True
            )
            paths = self._paths(root, acceptance, result)
            write_dynamic_manuscript(**paths)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("N/A [N/A, N/A]", table)
            self.assertIn("0/24 pairs; 0/8 clusters", table)
            lowered = manuscript.lower()
            self.assertNotIn("improved", lowered)
            self.assertNotIn("worsened", lowered)
            self.assertNotIn("outperformed", lowered)

    def test_duplicate_manuscript_markers_fail_before_output_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            paths["manuscript_path"].write_text(
                paths["manuscript_path"].read_text(encoding="utf-8")
                + f"{MANUSCRIPT_BEGIN}\n{MANUSCRIPT_END}\n",
                encoding="utf-8",
            )
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            with self.assertRaises(DynamicResultsPending):
                write_dynamic_manuscript(**paths)
            self.assertEqual(paths["table_path"].read_text(encoding="utf-8"), "old table")
            self.assertEqual(paths["figure_path"].read_text(encoding="utf-8"), "old figure")

    def test_second_replace_failure_rolls_back_all_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            originals = {
                key: paths[key].read_bytes()
                for key in ("table_path", "figure_path", "manuscript_path")
            }
            real_replace = os.replace
            replacement_count = 0

            def fail_second_replace(source: object, destination: object) -> None:
                nonlocal replacement_count
                replacement_count += 1
                if replacement_count == 2:
                    raise OSError("simulated second replace failure")
                real_replace(source, destination)

            with mock.patch(
                "scripts.render_graph_dynamic_manuscript.os.replace",
                side_effect=fail_second_replace,
            ):
                with self.assertRaisesRegex(OSError, "simulated second"):
                    write_dynamic_manuscript(**paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
