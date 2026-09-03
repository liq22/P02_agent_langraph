from __future__ import annotations

import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from scripts.analyze_graph_reliability import (
    ACCEPTANCE_SCHEMA_VERSION,
    PRIMARY_METRIC,
    REPLAY_MISSING_SCORE_POLICY_ID,
    RESULT_SCHEMA_VERSION,
    analyze_graph_reliability,
    load_graph_reliability_protocol,
)
from scripts.render_graph_reliability_manuscript import (
    MANUSCRIPT_BEGIN,
    MANUSCRIPT_END,
    ReliabilityResultsPending,
    validate_reliability_inputs,
    write_reliability_manuscript,
)
from scripts.schedule_graph_reliability import (
    _shared_contract,
    accept_graph_reliability_cohort,
    expected_run_directories,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "paper/experiments/graph_reliability_protocol_v2.yaml"


class ReliabilityManuscriptRendererTest(unittest.TestCase):
    def _json(self, path: Path, value: object) -> Path:
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        return path

    def _fixture(
        self, output_root: Path, *, undefined_primary: bool = False
    ) -> tuple[dict, dict, dict]:
        protocol = load_graph_reliability_protocol(PROTOCOL)
        repeat_ids = [item["repeat_id"] for item in protocol["cohort"]["repeats"]]
        iterations = protocol["statistics"]["bootstrap"]["iterations"]
        metrics = [*protocol["metrics"]["task"], *protocol["metrics"]["rollout"]]

        arm_values = {
            "reactive": {
                PRIMARY_METRIC: 0.65,
                "task.completion_adjusted_average_precision": 0.63,
                "task.auroc": 0.70,
                "task.false_alarm_rate": 0.20,
                "task.true_positive_rate": 0.80,
                "rollout.grounded_completion": 0.75,
                "rollout.submission_rate": 0.75,
                "rollout.grounded_recovery_success": 0.50,
                "rollout.repeated_action_ratio": 0.20,
                "rollout.budget_exhaustion": 0.10,
                "rollout.steps": 6.0,
                "rollout.llm_turns": 4.0,
                "rollout.tool_calls": 6.0,
                "rollout.input_tokens": 100.0,
                "rollout.output_tokens": 10.0,
                "rollout.total_tokens": 110.0,
                "rollout.estimated_model_cost_usd": 0.0,
            },
            "graph": {
                PRIMARY_METRIC: None if undefined_primary else 0.70,
                "task.completion_adjusted_average_precision": 0.68,
                "task.auroc": 0.75,
                "task.false_alarm_rate": 0.10,
                "task.true_positive_rate": 0.85,
                "rollout.grounded_completion": 0.875,
                "rollout.submission_rate": 0.875,
                "rollout.grounded_recovery_success": 0.60,
                "rollout.repeated_action_ratio": 0.10,
                "rollout.budget_exhaustion": 0.05,
                "rollout.steps": 7.0,
                "rollout.llm_turns": 5.0,
                "rollout.tool_calls": 6.0,
                "rollout.input_tokens": 120.0,
                "rollout.output_tokens": 12.0,
                "rollout.total_tokens": 132.0,
                "rollout.estimated_model_cost_usd": 0.0,
            },
        }

        def generic_report(value: float | None) -> dict:
            defined = value is not None
            return {
                "status": "defined" if defined else "not_applicable",
                "mean_across_registered_repeats": value,
                "between_repeat_variance": 0.0 if defined else None,
                "crossed_repeat_sequence_bootstrap_95ci": (
                    [value, value] if defined else None
                ),
                "repeat_estimates": {
                    repeat_id: value for repeat_id in repeat_ids
                },
                "defined_repeat_numerator": 10 if defined else 0,
                "registered_repeat_denominator": 10,
                "defined_episode_numerator": 80 if defined else 0,
                "assigned_episode_denominator": 80,
                "bootstrap_valid_replicates": iterations if defined else 0,
                "bootstrap_replicate_denominator": iterations,
                "missing_values_imputed_as_zero": False,
            }

        def primary_report(value: float | None, *, arm: bool) -> dict:
            report = generic_report(value)
            report.pop("defined_episode_numerator")
            report.update(
                {
                    "role": "primary_task_outcome",
                    "assigned_window_denominator_per_arm": 240,
                    "aggregation": (
                        "recompute_target_adverse_AP_over_all_24_assigned_windows_within_"
                        "each_repeat_then_equal_weight_repeats"
                    ),
                    "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                    "per_sequence_average_precision_averaging_performed": False,
                    "derived_evaluation_jsonl_ingested": False,
                }
            )
            if arm:
                report.update(
                    {
                        "submitted_window_numerator": 240,
                        "missing_assigned_scores": 0,
                        "score_coverage": 1.0,
                    }
                )
            return report

        inclusion = {
            "canonical_non_provider_terminal_count": 160,
            "matched_pair_count": 80,
            "retained_provider_failure_attempt_count": 0,
            "non_provider_failures_retained": 0,
            "terminal_status_counts": {"submitted": 160},
            "failure_kind_counts": {},
        }
        root = output_root.resolve()
        acceptance = {
            "schema_version": ACCEPTANCE_SCHEMA_VERSION,
            "accepted": True,
            "experiment_id": "P2-E9",
            "protocol_id": protocol["protocol_id"],
            "cohort_id": protocol["cohort"]["cohort_id"],
            "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
            "output_root": str(root),
            "repeat_ids": repeat_ids,
            "seeds": [item["seed"] for item in protocol["cohort"]["repeats"]],
            "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
            "arms": ["reactive", "graph"],
            "rotation": protocol["scope"]["rotation"],
            "public_sequence_ids": protocol["scope"]["public_sequence_ids"],
            "expected_episode_bundles": 160,
            "observed_non_provider_terminals": 160,
            "expected_pairs": 80,
            "observed_pairs": 80,
            "registered_run_directories": [
                str(path) for path in expected_run_directories(root, protocol).values()
            ],
            "contract": _shared_contract(protocol),
            "pooling_with_three_seed_primary": "forbidden",
            "primary_results_ingested": False,
            "non_provider_failure_policy": "retain_in_denominator",
            "provider_calls_performed_by_gate": False,
            "errors": [],
            "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
            "matched_control_id": protocol["profile"]["matched_control_id"],
            "canonical_inclusion": inclusion,
        }

        arms = {}
        for arm in ("reactive", "graph"):
            reports = {
                metric: (
                    primary_report(arm_values[arm][metric], arm=True)
                    if metric == PRIMARY_METRIC
                    else generic_report(arm_values[arm][metric])
                )
                for metric in metrics
            }
            numerator = 60 if arm == "reactive" else 70
            pass_all_numerator = 4 if arm == "reactive" else 6
            grounded = reports["rollout.grounded_completion"]
            pass_all_estimate = pass_all_numerator / 8
            arms[arm] = {
                "assigned_episode_denominator": 80,
                "registered_repeat_denominator": 10,
                "base_sequence_denominator": 8,
                "terminal_status_counts": {"submitted": 80},
                "failure_kind_counts": {},
                "metrics": reports,
                "reliability": {
                    "pass_definition": protocol["pass_rule"],
                    "pass_at_1": {
                        "numerator": numerator,
                        "denominator": 80,
                        "estimate": numerator / 80,
                        "mean_across_registered_repeats": grounded[
                            "mean_across_registered_repeats"
                        ],
                        "between_repeat_variance": grounded[
                            "between_repeat_variance"
                        ],
                        "crossed_repeat_sequence_bootstrap_95ci": grounded[
                            "crossed_repeat_sequence_bootstrap_95ci"
                        ],
                        "bootstrap_valid_replicates": iterations,
                        "bootstrap_replicate_denominator": iterations,
                    },
                    "pass_all_10": {
                        "numerator": pass_all_numerator,
                        "denominator": 8,
                        "estimate": pass_all_estimate,
                        "required_repeats_per_base_sequence": 10,
                        "assigned_repeat_episode_denominator": 80,
                        "sequence_cluster_bootstrap_95ci": [
                            pass_all_estimate,
                            pass_all_estimate,
                        ],
                        "bootstrap_valid_replicates": iterations,
                        "bootstrap_replicate_denominator": iterations,
                        "between_repeat_variance": None,
                        "between_repeat_variance_reason": (
                            "not_applicable_to_joint_all_10_endpoint"
                        ),
                    },
                },
                "cost": {
                    metric: reports[metric]
                    for metric in protocol["metrics"]["cost_metrics"]
                },
            }

        paired_metrics = {}
        for metric in metrics:
            graph_value = arm_values["graph"][metric]
            reactive_value = arm_values["reactive"][metric]
            delta = (
                None
                if graph_value is None or reactive_value is None
                else graph_value - reactive_value
            )
            paired_metrics[metric] = (
                primary_report(delta, arm=False)
                if metric == PRIMARY_METRIC
                else generic_report(delta)
            )
        primary = paired_metrics[PRIMARY_METRIC]
        grounded_delta = paired_metrics["rollout.grounded_completion"]
        pass_all_delta = 0.25
        paired = {
            "paired_unit": protocol["matched_contract"]["paired_unit"],
            "metrics": paired_metrics,
            "primary_task_outcome": {
                "metric": PRIMARY_METRIC,
                "estimate": primary["mean_across_registered_repeats"],
                "between_repeat_variance": primary["between_repeat_variance"],
                "crossed_repeat_sequence_bootstrap_95ci": primary[
                    "crossed_repeat_sequence_bootstrap_95ci"
                ],
                "defined_repeat_numerator": primary["defined_repeat_numerator"],
                "registered_repeat_denominator": 10,
                "assigned_pair_denominator": 80,
                "assigned_window_denominator_per_arm": 240,
                "bootstrap_valid_replicates": primary[
                    "bootstrap_valid_replicates"
                ],
                "bootstrap_replicate_denominator": iterations,
            },
            "pass_at_1_delta": {
                "role": "explanatory_rollout_reliability",
                "estimate": grounded_delta["mean_across_registered_repeats"],
                "between_repeat_variance": grounded_delta[
                    "between_repeat_variance"
                ],
                "crossed_repeat_sequence_bootstrap_95ci": grounded_delta[
                    "crossed_repeat_sequence_bootstrap_95ci"
                ],
                "defined_pair_numerator": grounded_delta[
                    "defined_episode_numerator"
                ],
                "assigned_pair_denominator": 80,
                "bootstrap_valid_replicates": iterations,
                "bootstrap_replicate_denominator": iterations,
            },
            "pass_all_10_delta": {
                "estimate": pass_all_delta,
                "sequence_cluster_bootstrap_95ci": [pass_all_delta, pass_all_delta],
                "sequence_denominator": 8,
                "bootstrap_valid_replicates": iterations,
                "bootstrap_replicate_denominator": iterations,
            },
        }
        result = {
            "schema_version": RESULT_SCHEMA_VERSION,
            "status": "accepted_complete_cohort_analysis",
            "experiment_id": "P2-E9",
            "protocol_id": protocol["protocol_id"],
            "cohort_id": protocol["cohort"]["cohort_id"],
            "reliability_profile_id": protocol["profile"]["reliability_profile_id"],
            "p2_experiment_id": protocol["profile"]["p2_experiment_id"],
            "matched_control_id": protocol["profile"]["matched_control_id"],
            "output_root": str(root),
            "provider_calls_performed_by_analyzer": False,
            "primary_endpoint": {
                "metric": PRIMARY_METRIC,
                "role": "task_primary",
                "missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                "private_target_authority": "registered_private_data_port_assignment",
                "prediction_authority": "canonical_rollout_successful_submit_prefix",
                "derived_evaluation_jsonl_ingested": False,
            },
            "cohort": {
                "repeat_ids": repeat_ids,
                "seeds": [item["seed"] for item in protocol["cohort"]["repeats"]],
                "primary_cohort_seeds": protocol["cohort"]["primary_cohort_seeds"],
                "primary_results_ingested": False,
                "pooling_with_three_seed_primary": "forbidden",
                "assigned_episode_denominator": 160,
                "matched_pair_denominator": 80,
            },
            "canonical_inclusion": inclusion,
            "arms": arms,
            "paired_graph_minus_reactive": paired,
            "claim_boundary": protocol["claim_boundary"],
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
        protocol = load_graph_reliability_protocol(PROTOCOL)
        consumer = protocol["execution"]["accepted_manuscript_consumer"]
        self.assertEqual(
            consumer["entrypoint"], "scripts/render_graph_reliability_manuscript.py"
        )
        self.assertIs(consumer["acceptance_required"], True)
        self.assertEqual(consumer["complete_episode_bundles_required"], 160)
        self.assertEqual(consumer["matched_pairs_required"], 80)
        self.assertIs(consumer["raw_run_or_private_data_reads"], False)
        self.assertIs(consumer["provider_calls"], False)
        self.assertIs(consumer["displayed_repeat_arithmetic_recomputed"], True)
        self.assertIs(consumer["atomic_outputs"], True)

    def test_accepted_result_writes_table_svg_and_unique_manuscript_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            summary = write_reliability_manuscript(**paths)
            self.assertEqual(summary["registered_rows"], 8)
            self.assertEqual(summary["formal_episode_bundles"], 160)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("Target-adverse Average Precision", table)
            self.assertIn("+0.0500", table)
            self.assertIn("accepted all 160 registered episode bundles", manuscript)
            self.assertEqual(manuscript.count(MANUSCRIPT_BEGIN), 1)
            self.assertEqual(manuscript.count(MANUSCRIPT_END), 1)
            self.assertNotIn(str(root / "formal"), table + manuscript)
            self.assertNotIn("private_target", table + manuscript)
            ET.parse(paths["figure_path"])

    def test_real_analyzer_fixture_is_consumed_without_raw_run_reads(self) -> None:
        from test_graph_reliability_v1 import _build_fixture, _private_assignments

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = _build_fixture(root)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            result = analyze_graph_reliability(
                root,
                protocol,
                acceptance,
                private_replay_assignments=_private_assignments(protocol),
            )
            rows = validate_reliability_inputs(
                protocol=protocol, acceptance=acceptance, result=result
            )
            self.assertEqual(len(rows), 8)
            self.assertEqual(rows[0]["label"], "Target-adverse Average Precision")

    def test_rejected_acceptance_leaves_outputs_unchanged(self) -> None:
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
            with self.assertRaises(ReliabilityResultsPending):
                write_reliability_manuscript(**paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)

    def test_primary_delta_is_recomputed_from_repeat_estimates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            paired = result["paired_graph_minus_reactive"]["metrics"][PRIMARY_METRIC]
            repeat_id = protocol["cohort"]["repeats"][0]["repeat_id"]
            paired["repeat_estimates"][repeat_id] += 0.01
            with self.assertRaisesRegex(ReliabilityResultsPending, "arithmetic drifted"):
                validate_reliability_inputs(
                    protocol=protocol, acceptance=acceptance, result=result
                )

    def test_pass_and_denominator_tamper_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            cases = []
            wrong_pass = copy.deepcopy(result)
            wrong_pass["arms"]["graph"]["reliability"]["pass_at_1"]["numerator"] = 69
            cases.append(wrong_pass)
            wrong_windows = copy.deepcopy(result)
            wrong_windows["arms"]["reactive"]["metrics"][PRIMARY_METRIC][
                "assigned_window_denominator_per_arm"
            ] = 239
            cases.append(wrong_windows)
            wrong_pool = copy.deepcopy(result)
            wrong_pool["cohort"]["pooling_with_three_seed_primary"] = "allowed"
            cases.append(wrong_pool)
            for index, candidate in enumerate(cases):
                with self.subTest(case=index):
                    with self.assertRaises(ReliabilityResultsPending):
                        validate_reliability_inputs(
                            protocol=protocol,
                            acceptance=acceptance,
                            result=candidate,
                        )

    def test_provider_or_profile_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            acceptance["contract"]["model"] = "replacement-model"
            with self.assertRaises(ReliabilityResultsPending):
                validate_reliability_inputs(
                    protocol=protocol, acceptance=acceptance, result=result
                )

    def test_undefined_primary_renders_na_without_directional_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(
                root / "formal", undefined_primary=True
            )
            paths = self._paths(root, acceptance, result)
            write_reliability_manuscript(**paths)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("N/A [N/A, N/A]", table)
            lowered = manuscript.lower()
            self.assertNotIn("improved", lowered)
            self.assertNotIn("worsened", lowered)
            self.assertNotIn("outperformed", lowered)

    def test_duplicate_markers_fail_before_output_writes(self) -> None:
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
            with self.assertRaises(ReliabilityResultsPending):
                write_reliability_manuscript(**paths)
            self.assertEqual(paths["table_path"].read_text(encoding="utf-8"), "old table")
            self.assertEqual(paths["figure_path"].read_text(encoding="utf-8"), "old figure")


if __name__ == "__main__":
    unittest.main()
