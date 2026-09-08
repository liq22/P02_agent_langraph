from __future__ import annotations

import copy
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from scripts import analyze_graph_cross_dataset_replay as analyzer
from scripts.schedule_graph_cross_dataset_replay import (
    DEFAULT_PROTOCOL,
    load_protocol,
)


ROOT = Path(__file__).resolve().parents[1]
DATASET_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark"
    / "paper/experiments/datasets/ottawa_uored_v5/phase1_monitoring_protocol_v1.yaml"
)
SEEDS = (20260808, 20260809, 20260810)
ROTATION_BEARINGS = {
    "rotation_0": ("UO5", "UO9", "UO10", "UO20"),
    "rotation_1": ("UO1", "UO2", "UO6", "UO18"),
    "rotation_2": ("UO3", "UO4", "UO8", "UO19"),
}


def _records() -> list[dict]:
    rows: list[dict] = []
    for seed in SEEDS:
        for rotation, bearings in ROTATION_BEARINGS.items():
            for bearing in bearings:
                sample_ids = [
                    f"{bearing}-healthy",
                    f"{bearing}-developing",
                    f"{bearing}-faulty",
                ]
                rows.append(
                    {
                        "pair_run": str(seed),
                        "rotation": rotation,
                        "bearing_id": bearing,
                        "sample_id": sample_ids[0],
                        "sample_ids": sample_ids,
                        "task_id": "online_replay_monitoring",
                        "private_target": dict(zip(sample_ids, (0, 1, 1))),
                        "failure_kind": None,
                    }
                )
    return rows


class GraphCrossDatasetAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cross = load_protocol(DEFAULT_PROTOCOL)
        cls.dataset = yaml.safe_load(DATASET_PROTOCOL.read_text(encoding="utf-8"))

    def _blocked_main(self, argv: list[str]) -> None:
        with mock.patch.object(analyzer, "build_report") as build, mock.patch(
            "builtins.print"
        ):
            self.assertEqual(analyzer.main(argv), 2)
        build.assert_not_called()

    def _assert_production_cli_path_gates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            alternate_protocol = root / "alternate.yaml"
            alternate_protocol.write_text("{}\n", encoding="utf-8")
            alternate_dataset = root / "dataset.yaml"
            alternate_dataset.write_text("{}\n", encoding="utf-8")
            output = root / "formal_result.json"
            common = [
                "--reactive-root",
                str(root / "reactive"),
                "--graph-root",
                str(root / "graph"),
                "--output",
                str(output),
            ]
            self._blocked_main(
                [*common, "--protocol", str(alternate_protocol)]
            )
            self._blocked_main(
                [*common, "--dataset-protocol", str(alternate_dataset)]
            )
            self._blocked_main(common)
            self.assertFalse(output.exists())

        for kind in (
            "protocol_extension_symlink",
            "output_symlink",
            "output_dangling_symlink",
            "output_hardlink",
            "output_parent_escape",
        ):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                authority = Path(directory)
                p2_root = authority / "P02_agent_langraph"
                benchmark_root = authority / "p01-phm-agent-benchmark"
                p2_root.mkdir()
                protocol = p2_root / "active.yaml"
                protocol.write_text("{}\n", encoding="utf-8")
                dataset = (
                    benchmark_root
                    / "paper/experiments/datasets/ottawa_uored_v5/"
                    "phase1_monitoring_protocol_v1.yaml"
                )
                dataset.parent.mkdir(parents=True)
                dataset.write_text("registered dataset\n", encoding="utf-8")
                results_root = p2_root / str(
                    self.cross["analysis_gate"]["results_root"]
                )
                output = p2_root / str(
                    self.cross["analysis_gate"]["formal_result"]
                )
                external = results_root / "external.json"

                if kind == "protocol_extension_symlink":
                    protocol.write_text(
                        "extends_protocol: graph_cross_dataset_replay_protocol_v2.yaml\n",
                        encoding="utf-8",
                    )
                    external_protocol = authority / "external-v2.yaml"
                    external_protocol.write_text("external sentinel\n", encoding="utf-8")
                    protocol.with_name(
                        "graph_cross_dataset_replay_protocol_v2.yaml"
                    ).symlink_to(external_protocol)
                elif kind == "output_parent_escape":
                    results_root.parent.mkdir(parents=True)
                    escaped = authority / "escaped-results"
                    escaped.mkdir()
                    results_root.symlink_to(escaped, target_is_directory=True)
                else:
                    results_root.mkdir(parents=True)
                    if kind == "output_symlink":
                        external.write_text("external sentinel", encoding="utf-8")
                        output.symlink_to(external)
                    elif kind == "output_dangling_symlink":
                        output.symlink_to(external)
                    else:
                        external.write_text("external sentinel", encoding="utf-8")
                        os.link(external, output)

                argv = [
                    "--reactive-root",
                    str(p2_root / "reactive"),
                    "--graph-root",
                    str(p2_root / "graph"),
                    "--protocol",
                    str(protocol),
                    "--dataset-protocol",
                    str(dataset),
                    "--output",
                    str(output),
                ]
                with mock.patch.object(analyzer, "ROOT", p2_root), mock.patch.object(
                    analyzer, "BENCHMARK_ROOT", benchmark_root
                ), mock.patch.object(
                    analyzer, "DEFAULT_PROTOCOL", protocol
                ), mock.patch.object(
                    analyzer, "load_protocol", return_value=copy.deepcopy(self.cross)
                ) as load, mock.patch.object(
                    analyzer, "build_report"
                ) as build, mock.patch(
                    "builtins.print"
                ):
                    self.assertEqual(analyzer.main(argv), 2)
                build.assert_not_called()
                if kind == "protocol_extension_symlink":
                    load.assert_not_called()
                if external.exists():
                    self.assertEqual(
                        external.read_text(encoding="utf-8"), "external sentinel"
                    )

    def test_analysis_registration_freezes_accepted_denominator_and_statistics(
        self,
    ) -> None:
        analysis = analyzer._validate_analysis_registration(self.cross)
        self.assertEqual(
            analysis["accepted_input_contract"]["episode_bundles_per_arm"], 36
        )
        self.assertEqual(
            analysis["accepted_input_contract"]["assigned_windows_per_arm"],
            108,
        )
        self.assertEqual(
            analysis["accepted_input_contract"]["exact_matched_episode_pairs"],
            36,
        )
        self.assertEqual(analysis["statistics"]["iterations"], 2000)
        self.assertEqual(analysis["statistics"]["cluster_unit"], "physical_bearing")
        self.assertEqual(analysis["statistics"]["direction"], "graph_minus_reactive")
        self.assertEqual(analysis["result_schema"], analyzer.RESULT_SCHEMA)
        self._assert_production_cli_path_gates()

    def test_accepted_arm_roots_are_bound_to_registered_stamped_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory) / "registered"
            run_root = base / "run_20260903T010203Z"
            reactive = run_root / "reactive"
            graph = run_root / "graph"
            reactive.mkdir(parents=True)
            graph.mkdir()
            protocol = copy.deepcopy(self.cross)
            protocol["current_schedule"]["output_root"] = str(base)
            stamp, observed_root = analyzer._validate_registered_root_layout(
                reactive, graph, protocol
            )
            self.assertEqual(stamp, "20260903T010203Z")
            self.assertEqual(observed_root, run_root.resolve())

            other = Path(directory) / "other" / "run_20260903T010203Z"
            other_reactive = other / "reactive"
            other_graph = other / "graph"
            other_reactive.mkdir(parents=True)
            other_graph.mkdir()
            with self.assertRaisesRegex(
                analyzer.CrossDatasetAnalysisError,
                "current_schedule.output_root",
            ):
                analyzer._validate_registered_root_layout(
                    other_reactive, other_graph, protocol
                )

    def test_exact_36_pairs_retain_failures_and_108_windows_per_arm(self) -> None:
        reactive = _records()
        graph = copy.deepcopy(reactive)
        reactive[0]["failure_kind"] = "budget_exhausted"
        graph[1]["failure_kind"] = "invalid_submission"
        counts = analyzer._validate_records(reactive, graph)
        self.assertEqual(counts["matched_episode_pairs"], 36)
        self.assertEqual(counts["reactive"]["physical_bearing_clusters"], 12)
        self.assertEqual(counts["reactive"]["assigned_windows"], 108)
        self.assertEqual(
            counts["reactive"]["nonprovider_terminal_failures_retained"], 1
        )
        self.assertEqual(
            counts["graph"]["nonprovider_terminal_failures_retained"], 1
        )

    def test_partial_or_mismatched_cohort_cannot_reach_any_metric(self) -> None:
        reactive = _records()
        graph = copy.deepcopy(reactive[:-1])
        with mock.patch.object(
            analyzer,
            "aggregate_results",
            side_effect=AssertionError("metrics must stay closed"),
        ), mock.patch.object(
            analyzer,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                analyzer.CrossDatasetAnalysisError,
                "Graph accepted denominator is 35/36",
            ):
                analyzer.analyze_accepted_records(
                    reactive,
                    graph,
                    dataset=self.dataset,
                    cross=self.cross,
                )

        graph = copy.deepcopy(reactive)
        graph[-1]["sample_id"] = "different-anchor"
        with self.assertRaisesRegex(
            analyzer.CrossDatasetAnalysisError, "episode keys do not match"
        ):
            analyzer._validate_records(reactive, graph)

    def test_target_pattern_drift_fails_before_aggregation(self) -> None:
        reactive = _records()
        graph = copy.deepcopy(reactive)
        graph[0]["private_target"][graph[0]["sample_ids"][1]] = 0
        with mock.patch.object(
            analyzer,
            "aggregate_results",
            side_effect=AssertionError("metrics must stay closed"),
        ):
            with self.assertRaisesRegex(
                analyzer.CrossDatasetAnalysisError, "target pattern drifted"
            ):
                analyzer.analyze_accepted_records(
                    reactive,
                    graph,
                    dataset=self.dataset,
                    cross=self.cross,
                )

    def test_accepted_records_run_target_adverse_arm_and_paired_recomputation(
        self,
    ) -> None:
        reactive = _records()
        graph = copy.deepcopy(reactive)
        summaries = [
            {"online_replay_monitoring": {"task": {"average_precision": 0.4}}},
            {"online_replay_monitoring": {"task": {"average_precision": 0.6}}},
        ]
        interval = {
            "online_replay_monitoring": {"task.average_precision": [0.2, 0.8]}
        }
        valid = {
            "online_replay_monitoring": {"task.average_precision": 2000}
        }
        paired = {
            "estimate": {
                "online_replay_monitoring": {"task.average_precision": 0.2}
            },
            "bearing_bootstrap_95ci": {
                "online_replay_monitoring": {
                    "task.average_precision": [0.05, 0.35]
                }
            },
            "bearing_bootstrap_valid_replicates": {
                "online_replay_monitoring": {"task.average_precision": 2000}
            },
            "bootstrap_iterations": 2000,
            "seed": 20260902,
            "direction": "treatment_minus_control",
        }
        with mock.patch.object(
            analyzer, "aggregate_results", side_effect=summaries
        ) as aggregate, mock.patch.object(
            analyzer,
            "bearing_bootstrap_intervals",
            side_effect=[(interval, valid), (interval, valid)],
        ) as arm_bootstrap, mock.patch.object(
            analyzer,
            "paired_bearing_bootstrap_deltas",
            return_value=paired,
        ) as paired_bootstrap:
            result = analyzer.analyze_accepted_records(
                reactive,
                graph,
                dataset=self.dataset,
                cross=self.cross,
            )
        self.assertEqual(aggregate.call_count, 2)
        self.assertEqual(arm_bootstrap.call_count, 2)
        self.assertEqual(paired_bootstrap.call_count, 1)
        self.assertEqual(
            paired_bootstrap.call_args.kwargs,
            {
                "iterations": 2000,
                "seed": 20260902,
                "replay_missing_score_policy_id": analyzer.REPLAY_POLICY_ID,
            },
        )
        self.assertEqual(result["primary_endpoint"]["estimate"], 0.2)
        self.assertEqual(
            result["primary_endpoint"]["bearing_cluster_bootstrap_95ci"],
            [0.05, 0.35],
        )

    def test_only_arm_specific_identity_may_differ_between_accepted_reports(self) -> None:
        common = {
            "runtime_contract": analyzer.RUNTIME_CONTRACT,
            "dataset_protocol_id": self.dataset["protocol_id"],
        }
        reactive = {
            "accepted": True,
            "contract": {**common, "agent": "reactive", "agent_id": "reactive-sequential-agent"},
            "run_contracts": {"20260808:rotation_0": {"selected_diagnosis_model_id": "m1"}},
        }
        graph = {
            "accepted": True,
            "contract": {**common, "agent": "graph", "agent_id": "graph-decision-agent"},
            "run_contracts": copy.deepcopy(reactive["run_contracts"]),
        }
        analyzer._validate_matched_reports(reactive, graph)
        graph["contract"]["runtime_contract"] = "different"
        with self.assertRaisesRegex(
            analyzer.CrossDatasetAnalysisError, "worlds differ"
        ):
            analyzer._validate_matched_reports(reactive, graph)

    def test_profile_validation_binds_path_free_cross_dataset_identity(self) -> None:
        expected = analyzer._profile_expected(
            self.cross, self.dataset, "reactive"
        )
        with mock.patch.object(
            analyzer,
            "validate_cohort_index",
            return_value={"profile": expected},
        ):
            analyzer._validate_arm_profiles(
                [Path("seed_20260808/rotation_0")],
                cross=self.cross,
                dataset=self.dataset,
                arm="reactive",
            )
        self.assertEqual(
            expected["data_binding"],
            {
                "metadata_environment": "PHM_OTTAWA_METADATA",
                "signal_environment": "PHM_OTTAWA_SIGNAL_ROOT",
                "readiness_environment": "PHM_OTTAWA_READINESS",
            },
        )
        self.assertNotIn("benchmark_control_source", expected)


if __name__ == "__main__":
    unittest.main()
