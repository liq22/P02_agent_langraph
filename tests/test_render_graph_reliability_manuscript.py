from __future__ import annotations

import copy
import json
import os
import stat
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock

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
    PUBLICATION_WRITE_CONTRACT,
    ReliabilityResultsPending,
    validate_reliability_inputs,
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

    def _protocol_json(self, path: Path, value: object) -> Path:
        path.write_text(
            json.dumps(value, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        return path

    def _fixture(
        self, output_root: Path, *, undefined_primary: bool = False
    ) -> tuple[dict, dict, dict]:
        protocol = load_graph_reliability_protocol(PROTOCOL)
        fixture_root = output_root.resolve().parent
        output_root = (
            fixture_root / "repository" / protocol["execution"]["formal_root"]
        ).resolve()
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
        repository_root = root / "repository"
        results_root = (
            repository_root
            / "paper/experiments/results/graph_reliability_v2"
            / "graph_reliability_generic_n10_v2"
        )
        table = repository_root / "paper/assets/tables/p2_e9_reliability_results.md"
        figure = repository_root / "paper/assets/figures/p2_e9_reliability_primary.svg"
        manuscript = repository_root / "paper/draft/main.md"
        for directory in (
            results_root,
            table.parent,
            figure.parent,
            manuscript.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        manuscript.write_text(
            "Before\n"
            f"{MANUSCRIPT_BEGIN}\n\npending\n\n{MANUSCRIPT_END}\n"
            "After\n",
            encoding="utf-8",
        )
        return {
            "protocol_path": self._protocol_json(
                root / "protocol.yaml", load_graph_reliability_protocol(PROTOCOL)
            ),
            "result_path": self._json(results_root / "formal_result.json", result),
            "acceptance_path": self._json(
                results_root / "formal_acceptance.json", acceptance
            ),
            "table_path": table,
            "figure_path": figure,
            "manuscript_path": manuscript,
        }

    def _write(self, paths: dict[str, Path]) -> dict:
        from scripts import render_graph_reliability_manuscript as renderer

        repository_root = paths["manuscript_path"].parents[2]
        with mock.patch.object(renderer, "ROOT", repository_root):
            return renderer.write_reliability_manuscript(**paths)

    def _validate(self, *, protocol: dict, acceptance: dict, result: dict) -> list[dict]:
        from scripts import render_graph_reliability_manuscript as renderer

        repository_root = Path(result["output_root"])
        for _part in Path(protocol["execution"]["formal_root"]).parts:
            repository_root = repository_root.parent
        with mock.patch.object(renderer, "ROOT", repository_root):
            return validate_reliability_inputs(
                protocol=protocol,
                acceptance=acceptance,
                result=result,
            )

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
        self.assertEqual(consumer["write_contract"], PUBLICATION_WRITE_CONTRACT)
        self.assertEqual(
            protocol["execution"]["accepted_manuscript"], "paper/draft/main.md"
        )

    def test_accepted_result_writes_table_svg_and_unique_manuscript_block(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            summary = self._write(paths)
            self.assertEqual(summary["registered_rows"], 8)
            self.assertEqual(summary["formal_episode_bundles"], 160)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("Target-adverse Average Precision", table)
            self.assertIn("+0.0500", table)
            self.assertIn("Valid bootstrap replicates", table)
            self.assertIn("2000/2000", table)
            self.assertIn("accepted all 160 registered episode bundles", manuscript)
            self.assertIn(
                "![Accepted P2-E9 bounded reliability contrasts](../assets/figures/p2_e9_reliability_primary.svg)",
                manuscript,
            )
            self.assertEqual(manuscript.count(MANUSCRIPT_BEGIN), 1)
            self.assertEqual(manuscript.count(MANUSCRIPT_END), 1)
            self.assertNotIn(str(root / "formal"), table + manuscript)
            self.assertNotIn("private_target", table + manuscript)
            ET.parse(paths["figure_path"])

    def test_real_analyzer_fixture_is_consumed_without_raw_run_reads(self) -> None:
        from test_graph_reliability_v1 import _build_fixture, _private_assignments

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol = load_graph_reliability_protocol(PROTOCOL)
            formal_root = root / "repository" / protocol["execution"]["formal_root"]
            protocol = _build_fixture(formal_root)
            acceptance = accept_graph_reliability_cohort(formal_root, protocol)
            result = analyze_graph_reliability(
                formal_root,
                protocol,
                acceptance,
                private_replay_assignments=_private_assignments(protocol),
            )
            rows = self._validate(
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
                self._write(paths)
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
                self._validate(
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
            incomplete_grounded = copy.deepcopy(result)
            incomplete_grounded["arms"]["graph"]["metrics"][
                "rollout.grounded_completion"
            ]["defined_episode_numerator"] = 79
            cases.append(incomplete_grounded)
            wrong_bootstrap = copy.deepcopy(result)
            wrong_bootstrap["paired_graph_minus_reactive"]["metrics"][
                PRIMARY_METRIC
            ]["bootstrap_valid_replicates"] = 2001
            cases.append(wrong_bootstrap)
            for index, candidate in enumerate(cases):
                with self.subTest(case=index):
                    with self.assertRaises(ReliabilityResultsPending):
                        self._validate(
                            protocol=protocol,
                            acceptance=acceptance,
                            result=candidate,
                        )

    def test_synchronized_pass_numerator_and_estimate_tamper_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            pass_at_1 = result["arms"]["graph"]["reliability"]["pass_at_1"]
            pass_at_1["numerator"] = 69
            pass_at_1["estimate"] = 69 / 80
            paths = self._paths(root, acceptance, result)
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            originals = {
                key: paths[key].read_bytes()
                for key in ("table_path", "figure_path", "manuscript_path")
            }

            with self.assertRaisesRegex(
                ReliabilityResultsPending, "grounded repeat mean"
            ):
                self._write(paths)

            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)

    def test_provider_or_profile_identity_drift_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            acceptance["contract"]["model"] = "replacement-model"
            with self.assertRaises(ReliabilityResultsPending):
                self._validate(
                    protocol=protocol, acceptance=acceptance, result=result
                )

    def test_result_output_root_is_bound_to_protocol_formal_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol, acceptance, result = self._fixture(root / "formal")
            replacement = str((root / "different-formal-root").resolve())
            result["output_root"] = replacement
            acceptance["output_root"] = replacement
            with self.assertRaisesRegex(ReliabilityResultsPending, "formal_root"):
                self._validate(
                    protocol=protocol,
                    acceptance=acceptance,
                    result=result,
                )

    def test_undefined_primary_renders_na_without_directional_prose(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(
                root / "formal", undefined_primary=True
            )
            paths = self._paths(root, acceptance, result)
            self._write(paths)
            table = paths["table_path"].read_text(encoding="utf-8")
            manuscript = paths["manuscript_path"].read_text(encoding="utf-8")
            self.assertIn("N/A [N/A, N/A]", table)
            self.assertIn("0/2000", table)
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
                self._write(paths)
            self.assertEqual(paths["table_path"].read_text(encoding="utf-8"), "old table")
            self.assertEqual(paths["figure_path"].read_text(encoding="utf-8"), "old figure")

    def test_equal_output_paths_are_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            protocol = json.loads(paths["protocol_path"].read_text(encoding="utf-8"))
            protocol["execution"]["accepted_manuscript_figure"] = protocol[
                "execution"
            ]["accepted_manuscript_table"]
            self._protocol_json(paths["protocol_path"], protocol)
            paths["figure_path"] = paths["table_path"]

            with self.assertRaisesRegex(ReliabilityResultsPending, "must be distinct"):
                self._write(paths)
            self.assertFalse(paths["table_path"].exists())
            self.assertIn("pending", paths["manuscript_path"].read_text(encoding="utf-8"))

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            paths["table_path"].write_text("shared inode", encoding="utf-8")
            os.link(paths["table_path"], paths["figure_path"])
            with self.assertRaisesRegex(ReliabilityResultsPending, "must be distinct"):
                self._write(paths)
            self.assertEqual(paths["table_path"].read_text(encoding="utf-8"), "shared inode")

    def test_symlink_and_hardlink_input_aliases_are_rejected(self) -> None:
        for kind in ("symlink", "hardlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, acceptance, result = self._fixture(root / "formal")
                paths = self._paths(root, acceptance, result)
                source = (
                    paths["result_path"]
                    if kind == "symlink"
                    else paths["protocol_path"]
                )
                if kind == "symlink":
                    paths["table_path"].symlink_to(source)
                else:
                    os.link(source, paths["table_path"])
                original = source.read_bytes()

                with self.assertRaisesRegex(
                    ReliabilityResultsPending,
                    "must not overwrite an input authority",
                ):
                    self._write(paths)
                self.assertEqual(source.read_bytes(), original)

    def test_nonordinary_existing_outputs_are_rejected_before_staging(self) -> None:
        from scripts import render_graph_reliability_manuscript as renderer

        for kind in ("external_symlink", "dangling_symlink", "unrelated_hardlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, acceptance, result = self._fixture(root / "formal")
                paths = self._paths(root, acceptance, result)
                external = root / "unrelated.txt"
                if kind == "external_symlink":
                    external.write_text("external sentinel", encoding="utf-8")
                    paths["table_path"].symlink_to(external)
                elif kind == "dangling_symlink":
                    paths["table_path"].symlink_to(external)
                else:
                    external.write_text("external sentinel", encoding="utf-8")
                    os.link(external, paths["table_path"])
                manuscript = paths["manuscript_path"].read_bytes()
                with mock.patch.object(renderer, "_stage_bytes") as stage:
                    with self.assertRaisesRegex(
                        ReliabilityResultsPending,
                        "ordinary single-link regular file",
                    ):
                        self._write(paths)
                    stage.assert_not_called()
                self.assertEqual(paths["manuscript_path"].read_bytes(), manuscript)
                if external.exists():
                    self.assertEqual(
                        external.read_text(encoding="utf-8"), "external sentinel"
                    )
                if "symlink" in kind:
                    self.assertTrue(paths["table_path"].is_symlink())
                else:
                    self.assertTrue(os.path.samefile(external, paths["table_path"]))

    def test_source_symlink_escape_and_output_parent_escape_fail_before_staging(self) -> None:
        from scripts import render_graph_reliability_manuscript as renderer

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            external = root / "outside-result.json"
            original = paths["result_path"].read_bytes()
            external.write_bytes(original)
            paths["result_path"].unlink()
            paths["result_path"].symlink_to(external)
            with mock.patch.object(renderer, "_stage_bytes") as stage:
                with self.assertRaisesRegex(ReliabilityResultsPending, "results_root"):
                    self._write(paths)
                stage.assert_not_called()
            self.assertEqual(external.read_bytes(), original)
            self.assertTrue(paths["result_path"].is_symlink())

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            publication = paths["table_path"].parent
            publication.rmdir()
            outside = root.parent / f"{root.name}-outside"
            outside.mkdir()
            publication.symlink_to(outside, target_is_directory=True)
            try:
                with mock.patch.object(renderer, "_stage_bytes") as stage:
                    with self.assertRaisesRegex(
                        ReliabilityResultsPending,
                        "resolves outside its authority root",
                    ):
                        self._write(paths)
                    stage.assert_not_called()
                self.assertEqual(list(outside.iterdir()), [])
            finally:
                outside.rmdir()

    def test_cli_requires_registered_protocol(self) -> None:
        from scripts import render_graph_reliability_manuscript as renderer

        with tempfile.TemporaryDirectory() as directory:
            alternate = Path(directory) / "alternate.yaml"
            alternate.write_text("{}\n", encoding="utf-8")
            with self.assertRaisesRegex(ReliabilityResultsPending, "registered P2-E9"):
                renderer.main(["--protocol", str(alternate)])

    def test_undeclared_and_input_root_output_paths_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            paths["table_path"] = paths["table_path"].with_name("undeclared.md")
            with self.assertRaisesRegex(ReliabilityResultsPending, "differs from"):
                self._write(paths)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            protocol = json.loads(paths["protocol_path"].read_text(encoding="utf-8"))
            repository_root = paths["manuscript_path"].parents[2]
            unsafe_relative = Path(protocol["execution"]["results_root"]) / "unsafe.md"
            unsafe = repository_root / unsafe_relative
            protocol["execution"]["accepted_manuscript_table"] = unsafe_relative.as_posix()
            self._protocol_json(paths["protocol_path"], protocol)
            paths["table_path"] = unsafe
            with self.assertRaisesRegex(
                ReliabilityResultsPending, "inside an input root"
            ):
                self._write(paths)

    def test_staging_failure_writes_nothing_and_cleans_temporaries(self) -> None:
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
            from scripts import render_graph_reliability_manuscript as renderer

            real_stage = renderer._stage_bytes
            stage_count = 0

            def fail_second_stage(path: Path, payload: bytes, mode: int) -> Path:
                nonlocal stage_count
                stage_count += 1
                if stage_count == 2:
                    raise OSError("simulated staging failure")
                return real_stage(path, payload, mode)

            with mock.patch.object(renderer, "_stage_bytes", side_effect=fail_second_stage):
                with self.assertRaisesRegex(OSError, "simulated staging failure"):
                    self._write(paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)
            self.assertEqual(list(root.rglob(".*.tmp")), [])

    def test_third_replace_failure_rolls_back_all_outputs(self) -> None:
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

            def fail_third_replace(source: object, destination: object) -> None:
                nonlocal replacement_count
                replacement_count += 1
                if replacement_count == 3:
                    raise OSError("simulated third replace failure")
                real_replace(source, destination)

            with mock.patch(
                "scripts.render_graph_reliability_manuscript._replace_path",
                side_effect=fail_third_replace,
            ):
                with self.assertRaisesRegex(OSError, "simulated third"):
                    self._write(paths)
            for key, original in originals.items():
                self.assertEqual(paths[key].read_bytes(), original)

    def test_repeated_publication_is_byte_identical_and_preserves_modes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _, acceptance, result = self._fixture(root / "formal")
            paths = self._paths(root, acceptance, result)
            paths["table_path"].write_text("old table", encoding="utf-8")
            paths["figure_path"].write_text("old figure", encoding="utf-8")
            modes = {
                "table_path": 0o640,
                "figure_path": 0o600,
                "manuscript_path": 0o644,
            }
            for key, mode in modes.items():
                paths[key].chmod(mode)

            self._write(paths)
            first = {
                key: paths[key].read_bytes()
                for key in ("table_path", "figure_path", "manuscript_path")
            }
            self._write(paths)
            for key, payload in first.items():
                self.assertEqual(paths[key].read_bytes(), payload)
                self.assertEqual(stat.S_IMODE(paths[key].stat().st_mode), modes[key])


if __name__ == "__main__":
    unittest.main()
