from __future__ import annotations

import copy
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from scripts import analyze_graph_cross_dataset_replay as analyzer
from scripts.render_graph_cross_dataset_manuscript import (
    DISPLAY_METRICS,
    MANUSCRIPT_BEGIN,
    MANUSCRIPT_END,
    CrossDatasetResultsPending,
    validate_cross_dataset_inputs,
    write_cross_dataset_manuscript,
)
from scripts.schedule_graph_cross_dataset_replay import load_protocol


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = ROOT / "paper/experiments/graph_cross_dataset_replay_protocol_v3.yaml"
DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark"
    / "paper/experiments/datasets/ottawa_uored_v5/phase1_monitoring_protocol_v1.yaml"
)


class CrossDatasetManuscriptRendererTest(unittest.TestCase):
    def _json(self, path: Path, value: object) -> Path:
        path.write_text(
            json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        return path

    def _manual_analysis(self) -> dict:
        values = {
            "reactive": {
                "task.average_precision": 0.60,
                "task.auroc": 0.65,
                "task.false_alarm_rate": 0.25,
                "task.true_positive_rate": 0.75,
                "task.score_coverage": 90 / 108,
            },
            "graph": {
                "task.average_precision": 0.70,
                "task.auroc": 0.72,
                "task.false_alarm_rate": 0.18,
                "task.true_positive_rate": 0.82,
                "task.score_coverage": 99 / 108,
            },
        }

        def arm_summary(arm: str) -> dict:
            submitted = 90 if arm == "reactive" else 99
            task = {
                "submission": 0.80 if arm == "reactive" else 0.90,
                "average_precision": values[arm]["task.average_precision"],
                "auroc": values[arm]["task.auroc"],
                "cohort_prevalence": 2 / 3,
                "submitted_prevalence": 2 / 3,
                "false_alarm_rate": values[arm]["task.false_alarm_rate"],
                "true_positive_rate": values[arm]["task.true_positive_rate"],
                "assigned_windows": 108,
                "submitted_windows": submitted,
                "missing_assigned_scores": 108 - submitted,
                "score_coverage": values[arm]["task.score_coverage"],
            }
            return {
                "online_replay_monitoring": {
                    "episodes": 36,
                    "bearings": 12,
                    "rollout": {"submission_rate": task["submission"]},
                    "evaluation_contract": {
                        "missing_assigned_score_policy_id": analyzer.REPLAY_POLICY_ID,
                        "population": "all_protocol_assigned_replay_windows",
                        "partial_decision_source": "canonical_successful_submit_prefix",
                        "missing_positive": "zero_ap_contribution_and_normal_miss",
                        "missing_negative": "above_submitted_ranks_and_anomaly_false_alarm",
                        "target_visibility": "evaluator_only",
                    },
                    "task": task,
                }
            }

        def arm_bootstrap(arm: str) -> dict:
            intervals = {}
            valid = {}
            for metric, _label, _role in DISPLAY_METRICS:
                point = values[arm][metric]
                intervals[metric] = [max(0.0, point - 0.05), min(1.0, point + 0.05)]
                valid[metric] = 2000
            return {
                "interval_95ci": {"online_replay_monitoring": intervals},
                "valid_replicates": {"online_replay_monitoring": valid},
            }

        estimates = {
            metric: values["graph"][metric] - values["reactive"][metric]
            for metric, _label, _role in DISPLAY_METRICS
        }
        estimates["task.assigned_windows"] = 0.0
        intervals = {
            metric: [max(-1.0, delta - 0.05), min(1.0, delta + 0.05)]
            for metric, delta in estimates.items()
            if metric != "task.assigned_windows"
        }
        valid = {metric: 2000 for metric in intervals}
        return {
            "denominators": {
                "reactive": {
                    "runs": 9,
                    "episode_bundles": 36,
                    "assigned_windows": 108,
                    "physical_bearing_clusters": 12,
                    "nonprovider_terminal_failures_retained": 1,
                },
                "graph": {
                    "runs": 9,
                    "episode_bundles": 36,
                    "assigned_windows": 108,
                    "physical_bearing_clusters": 12,
                    "nonprovider_terminal_failures_retained": 2,
                },
                "matched_episode_pairs": 36,
            },
            "target_adverse_metric_policy_id": analyzer.REPLAY_POLICY_ID,
            "arm_summaries": {
                "reactive": arm_summary("reactive"),
                "graph": arm_summary("graph"),
            },
            "arm_bearing_bootstrap": {
                "reactive": arm_bootstrap("reactive"),
                "graph": arm_bootstrap("graph"),
            },
            "paired_graph_minus_reactive": {
                "estimate": {"online_replay_monitoring": estimates},
                "bearing_bootstrap_95ci": {
                    "online_replay_monitoring": intervals
                },
                "bearing_bootstrap_valid_replicates": {
                    "online_replay_monitoring": valid
                },
                "bootstrap_iterations": 2000,
                "seed": 20260902,
                "direction": "treatment_minus_control",
            },
            "primary_endpoint": {
                "name": "online_replay_monitoring.task.average_precision",
                "estimate": estimates["task.average_precision"],
                "bearing_cluster_bootstrap_95ci": intervals[
                    "task.average_precision"
                ],
                "valid_replicates": 2000,
            },
        }

    def _result(self, protocol: dict, *, analysis: dict | None = None) -> dict:
        return {
            "schema_version": analyzer.RESULT_SCHEMA,
            "status": "accepted",
            "evidence_class": "formal",
            "result_role": "confirmatory",
            "protocol_id": protocol["protocol_id"],
            "dataset_id": protocol["dataset_registration"]["dataset_id"],
            "dataset_protocol_id": protocol["dataset_registration"][
                "dataset_protocol_id"
            ],
            "experiment_profile_id": protocol["formal_execution"][
                "experiment_profile_id"
            ],
            "formal_run_stamp": "20260903T010203Z",
            "provider_calls_made_by_analyzer": 0,
            "private_assignment_validation": (
                "phase1_registered_data_port_assignment_v1"
            ),
            "acceptance": {
                "reactive": {
                    "accepted": True,
                    "runs": 9,
                    "episodes": 36,
                    "errors": [],
                },
                "graph": {
                    "accepted": True,
                    "runs": 9,
                    "episodes": 36,
                    "errors": [],
                },
                "matched_world_contract": "accepted",
                "exact_episode_pairing": "accepted",
            },
            "analysis": analysis or self._manual_analysis(),
            "reporting_boundary": {
                "dataset_pooling": "Ottawa_only",
                "public_condition_event": "absent",
                "event_f1": "N/A",
                "detection_delay": "N/A",
                "monitor_or_revise_event_branch_transfer": "not_an_estimand",
            },
        }

    def _paths(self, root: Path, result: dict) -> dict[str, Path]:
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
            "table_path": root / "table.md",
            "figure_path": root / "figure.svg",
            "manuscript_path": manuscript,
        }

    def test_protocol_registers_the_accepted_only_consumer(self) -> None:
        protocol = load_protocol(PROTOCOL)
        consumer = protocol["analysis_gate"]["accepted_manuscript_consumer"]
        self.assertEqual(
            consumer["entrypoint"],
            "scripts/render_graph_cross_dataset_manuscript.py",
        )
        self.assertEqual(consumer["complete_episode_bundles_required"], 72)
        self.assertEqual(consumer["matched_pairs_required"], 36)
        self.assertEqual(consumer["assigned_windows_per_arm_required"], 108)
        self.assertIs(consumer["raw_run_or_private_data_reads"], False)
        self.assertIs(consumer["provider_calls"], False)
        self.assertIs(consumer["displayed_paired_arithmetic_recomputed"], True)
        self.assertIs(consumer["atomic_outputs"], True)

    def test_accepted_result_writes_table_svg_and_unique_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = load_protocol(PROTOCOL)
            paths = self._paths(root, self._result(protocol))
            summary = write_cross_dataset_manuscript(**paths)
            self.assertEqual(summary["registered_rows"], 5)
            self.assertEqual(summary["formal_episode_bundles"], 72)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("Target-adverse Average Precision", table)
            self.assertIn("+0.1000", table)
            self.assertIn("accepted all 72 registered Ottawa episode bundles", manuscript)
            self.assertEqual(manuscript.count(MANUSCRIPT_BEGIN), 1)
            self.assertEqual(manuscript.count(MANUSCRIPT_END), 1)
            self.assertNotIn(str(root), table + manuscript)
            self.assertNotIn("private_target", table + manuscript)
            ET.parse(paths["figure_path"])

    def test_rejected_acceptance_leaves_all_outputs_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = load_protocol(PROTOCOL)
            result = self._result(protocol)
            result["acceptance"]["graph"]["accepted"] = False
            paths = self._paths(root, result)
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            originals = {
                key: paths[key].read_bytes()
                for key in ("table_path", "figure_path", "manuscript_path")
            }
            with self.assertRaises(CrossDatasetResultsPending):
                write_cross_dataset_manuscript(**paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)

    def test_denominator_and_window_accounting_tamper_fail_closed(self) -> None:
        protocol = load_protocol(PROTOCOL)
        cases = []
        wrong_pairs = self._result(protocol)
        wrong_pairs["analysis"]["denominators"]["matched_episode_pairs"] = 35
        cases.append(wrong_pairs)
        wrong_coverage = self._result(protocol)
        wrong_coverage["analysis"]["arm_summaries"]["graph"][
            "online_replay_monitoring"
        ]["task"]["score_coverage"] = 1.0
        cases.append(wrong_coverage)
        wrong_failure = self._result(protocol)
        wrong_failure["analysis"]["denominators"]["reactive"][
            "nonprovider_terminal_failures_retained"
        ] = 37
        cases.append(wrong_failure)
        for index, candidate in enumerate(cases):
            with self.subTest(case=index):
                with self.assertRaises(CrossDatasetResultsPending):
                    validate_cross_dataset_inputs(protocol=protocol, result=candidate)

    def test_displayed_paired_delta_is_recomputed_from_absolute_arms(self) -> None:
        protocol = load_protocol(PROTOCOL)
        result = self._result(protocol)
        result["analysis"]["paired_graph_minus_reactive"]["estimate"][
            "online_replay_monitoring"
        ]["task.average_precision"] += 0.01
        with self.assertRaisesRegex(CrossDatasetResultsPending, "arithmetic drifted"):
            validate_cross_dataset_inputs(protocol=protocol, result=result)

    def test_bootstrap_and_primary_endpoint_drift_fail_closed(self) -> None:
        protocol = load_protocol(PROTOCOL)
        wrong_seed = self._result(protocol)
        wrong_seed["analysis"]["paired_graph_minus_reactive"]["seed"] = 1
        with self.assertRaises(CrossDatasetResultsPending):
            validate_cross_dataset_inputs(protocol=protocol, result=wrong_seed)
        wrong_primary = self._result(protocol)
        wrong_primary["analysis"]["primary_endpoint"]["valid_replicates"] = 1999
        with self.assertRaises(CrossDatasetResultsPending):
            validate_cross_dataset_inputs(protocol=protocol, result=wrong_primary)

    def test_identity_or_event_relabelling_fails_closed(self) -> None:
        protocol = load_protocol(PROTOCOL)
        wrong_profile = self._result(protocol)
        wrong_profile["experiment_profile_id"] = "replacement-profile"
        with self.assertRaises(CrossDatasetResultsPending):
            validate_cross_dataset_inputs(protocol=protocol, result=wrong_profile)
        wrong_event = self._result(protocol)
        wrong_event["reporting_boundary"]["event_f1"] = 0.5
        with self.assertRaises(CrossDatasetResultsPending):
            validate_cross_dataset_inputs(protocol=protocol, result=wrong_event)

    def test_duplicate_markers_fail_before_output_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = load_protocol(PROTOCOL)
            paths = self._paths(root, self._result(protocol))
            paths["manuscript_path"].write_text(
                paths["manuscript_path"].read_text(encoding="utf-8")
                + f"{MANUSCRIPT_BEGIN}\n{MANUSCRIPT_END}\n",
                encoding="utf-8",
            )
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            with self.assertRaises(CrossDatasetResultsPending):
                write_cross_dataset_manuscript(**paths)
            self.assertEqual(paths["table_path"].read_text(encoding="utf-8"), "old table")
            self.assertEqual(paths["figure_path"].read_text(encoding="utf-8"), "old figure")

    def test_real_analyzer_output_is_consumed_without_raw_run_reads(self) -> None:
        from test_graph_cross_dataset_analysis import _records

        protocol = load_protocol(PROTOCOL)
        dataset = yaml.safe_load(DATASET_PROTOCOL.read_text(encoding="utf-8"))
        reactive = _records()
        graph = copy.deepcopy(reactive)
        for rows in (reactive, graph):
            for row in rows:
                sample_ids = row["sample_ids"]
                decisions = [
                    {
                        "sample_id": sample_ids[0],
                        "score": 0.1,
                        "predicted_class": "normal",
                    },
                    {
                        "sample_id": sample_ids[1],
                        "score": 0.6,
                        "predicted_class": "anomaly",
                    },
                    {
                        "sample_id": sample_ids[2],
                        "score": 0.9,
                        "predicted_class": "anomaly",
                    },
                ]
                row["replay_decisions"] = decisions
                row["submission"] = {"decisions": decisions}
                row["evaluation"] = {
                    "task_metrics": {"submission": 1.0},
                    "rollout_metrics": {
                        "submission_rate": 1.0,
                        "submission_grounding": 1.0,
                        "artifact_lineage_completeness": 1.0,
                        "supporting_reference_validity": 1.0,
                        "repeated_action_ratio": 0.0,
                    },
                }
        analysis = analyzer.analyze_accepted_records(
            reactive,
            graph,
            dataset=dataset,
            cross=protocol,
        )
        rows = validate_cross_dataset_inputs(
            protocol=protocol,
            result=self._result(protocol, analysis=analysis),
        )
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["label"], "Target-adverse Average Precision")
        self.assertEqual(rows[0]["delta"], 0.0)


if __name__ == "__main__":
    unittest.main()
