from __future__ import annotations

import argparse
import json
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import yaml

from phm_graph_agent import STATES as EXECUTABLE_STATES
from phm_graph_agent.state import ALLOWED_TRANSITIONS, DYNAMIC_LEGAL_TRANSITIONS
from scripts.make_graph_figure import render_svg
from scripts.render_current_mechanics_evidence import (
    load_current_mechanics,
    render_svg as render_current_mechanics_svg,
    render_table as render_current_mechanics_table,
)
from scripts.render_graph_manuscript_table import (
    ANOMALY_TASK,
    CORE_MANUSCRIPT_HEADING,
    CORE_EPISODES_PER_TASK,
    CORE_ROTATIONS,
    CORE_TASKS,
    BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    BENCHMARK_REPOSITORY,
    DATA_FACTORY_REPOSITORY,
    DEFAULT_PROTOCOL,
    EXPECTED_BENCHMARK_CONTROL_SOURCE,
    PRIMARY_ENDPOINT,
    P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    P2_FORMAL_REPRODUCIBILITY_PATHS,
    P2_REPOSITORY,
    REPLAY_MANUSCRIPT_HEADING,
    REGISTERED_ENDPOINTS,
    REPLAY_EPISODES,
    REPLAY_MISSING_SCORE_POLICY_ID,
    REPLAY_TASK,
    RUNTIME_CONTRACT,
    FIGURES_MANUSCRIPT_HEADING,
    ResultsPending,
    SEEDS,
    STATES,
    write_table,
)

ROOT = Path(__file__).resolve().parents[1]


class GraphManuscriptTableTest(unittest.TestCase):
    def _write(self, root: Path, name: str, value: object) -> Path:
        path = root / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def _gate(
        self,
        *,
        graph: bool,
        mode: str,
        accepted: bool = True,
    ) -> dict[str, object]:
        core = mode == "core"
        tasks = list(CORE_TASKS) if core else [REPLAY_TASK]
        rotations = CORE_ROTATIONS if core else ["rotation_0"]
        runs = 12 if core else 3
        episodes = 192 if core else REPLAY_EPISODES
        contract = {
            "runtime_contract": RUNTIME_CONTRACT,
            "tasks": tasks,
            "budget": {"max_tool_calls": 72 if core else 120},
        }
        return {
            "accepted": accepted,
            "mode": mode,
            "expected_episodes": episodes,
            "observed_unique_episodes": episodes,
            "expected_runs": runs,
            "observed_runs": runs,
            "seeds": SEEDS,
            "rotations": rotations,
            "tasks": tasks,
            "inference_contract_required": True,
            "state_evaluation_required": graph,
            "expected_runtime_contract": RUNTIME_CONTRACT,
            "expected_evidence_classes": ["real_data_formal_candidate"],
            "contract": contract,
            "run_contracts": {
                f"{seed}:{rotation}": {
                    "selected_diagnosis_model_id": "ridge-ovr-v1"
                }
                for seed in SEEDS
                for rotation in rotations
            },
            "errors": [],
        }

    def _summary(
        self, tasks: tuple[str, ...], *, offset: float
    ) -> dict[str, object]:
        summaries: dict[str, object] = {}
        intervals: dict[str, object] = {}
        counts: dict[str, object] = {}
        rollout_names = (
            "grounded_completion",
            "submission_rate",
            "valid_tool_call_rate",
            "grounded_recovery_success",
            "steps",
            "estimated_model_cost_usd",
            "recovery_coverage",
            "steps_to_recovery",
            "repeated_action_ratio",
            "budget_exhaustion",
            "p95_step_latency_seconds",
            "llm_turns",
            "input_tokens",
            "output_tokens",
            "wall_clock_seconds",
        )
        for task_index, task in enumerate(tasks):
            if task == CORE_TASKS[0]:
                outcome_name = "macro_f1"
            elif task == ANOMALY_TASK:
                outcome_name = "completion_adjusted_average_precision"
            else:
                outcome_name = "average_precision"
            task_value = offset + 0.40 + task_index / 10
            task_metrics = {outcome_name: task_value}
            task_intervals = {
                f"task.{outcome_name}": [task_value - 0.01, task_value + 0.01]
            }
            task_counts = {f"task.{outcome_name}": 1999}
            rollout: dict[str, float | None] = {}
            for index, name in enumerate(rollout_names, 1):
                metric = f"rollout.{name}"
                if name == "steps_to_recovery":
                    rollout[name] = None
                    task_intervals[metric] = None
                    task_counts[metric] = 0
                else:
                    value = offset + task_index / 10 + index / 20
                    rollout[name] = value
                    task_intervals[metric] = [value - 0.01, value + 0.01]
                    task_counts[metric] = 1999
            summaries[task] = {"task": task_metrics, "rollout": rollout}
            intervals[task] = task_intervals
            counts[task] = task_counts
        return {
            "summary": summaries,
            "bearing_bootstrap_95ci": intervals,
            "bearing_bootstrap_valid_replicates": counts,
            "bootstrap_iterations": 2000,
            "seed": 20260820,
            "evidence_class": "real_data_formal_candidate",
        }

    def _delta(self, tasks: tuple[str, ...]) -> dict[str, object]:
        source = self._summary(tasks, offset=0.0)
        estimates: dict[str, dict[str, float | None]] = {}
        for task in tasks:
            values = source["summary"][task]  # type: ignore[index]
            estimates[task] = {
                **{
                    f"task.{name}": None if value is None else 0.1
                    for name, value in values["task"].items()
                },
                **{
                    f"rollout.{name}": None if value is None else 0.1
                    for name, value in values["rollout"].items()
                },
            }
        intervals = {
            task: {
                metric: None if value is None else [0.09, 0.11]
                for metric, value in estimates[task].items()
            }
            for task in tasks
        }
        counts = {
            task: {
                metric: 0 if value is None else 1999
                for metric, value in estimates[task].items()
            }
            for task in tasks
        }
        return {
            "estimate": estimates,
            "bearing_bootstrap_95ci": intervals,
            "bearing_bootstrap_valid_replicates": counts,
            "bootstrap_iterations": 2000,
            "seed": 20260820,
            "direction": "treatment_minus_control",
            "evidence_class": "real_data_formal_candidate",
        }

    def _state_summary(
        self, tasks: tuple[str, ...], *, episodes: int
    ) -> dict[str, object]:
        result: dict[str, object] = {}
        for task in tasks:
            inactive = {"Monitor", "Revise", "Recover"}
            active_occupancy = 1.0 / (len(STATES) - len(inactive))
            occupancy = {
                state: 0.0 if state in inactive else active_occupancy
                for state in STATES
            }
            visitation = {
                state: 0.0 if state in inactive else 1.0 for state in STATES
            }
            result[task] = {
                "episodes": episodes,
                "mean_transition_validity": 1.0,
                "all_transitions_valid_rate": 1.0,
                "recover_episode_rate": 0.0,
                "mean_recover_visits": 0.0,
                "state_coverage": [state for state in STATES if state not in inactive],
                "state_step_occupancy_proportion": occupancy,
                "state_episode_visitation_rate": visitation,
            }
        return result

    def _args(
        self,
        root: Path,
        *,
        reject_core: bool = False,
        reject_replay: bool = False,
    ) -> argparse.Namespace:
        manuscript = root / "main.md"
        manuscript.write_text(
            "Before\n"
            "<!-- GRAPH_CORE_PRIMARY_COMPACT:BEGIN -->\n\ncore pending\n\n"
            "<!-- GRAPH_CORE_PRIMARY_COMPACT:END -->\n"
            "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:BEGIN -->\n\nreplay pending\n\n"
            "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:END -->\n"
            "<!-- GRAPH_FORMAL_FIGURES:BEGIN -->\n\nfigures pending\n\n"
            "<!-- GRAPH_FORMAL_FIGURES:END -->\nAfter\n",
            encoding="utf-8",
        )
        core_control_acceptance = self._write(
            root,
            "core_control_gate.json",
            self._gate(graph=False, mode="core", accepted=not reject_core),
        )
        core_graph_acceptance = self._write(
            root,
            "core_graph_gate.json",
            self._gate(graph=True, mode="core", accepted=not reject_core),
        )
        reactive_acceptance = self._write(
            root,
            "replay_control_gate.json",
            self._gate(graph=False, mode="monitoring", accepted=not reject_replay),
        )
        graph_acceptance = self._write(
            root,
            "replay_graph_gate.json",
            self._gate(graph=True, mode="monitoring", accepted=not reject_replay),
        )

        core_control = self._summary(CORE_TASKS, offset=0.0)
        core_control["cohort_acceptance"] = str(core_control_acceptance)
        core_graph = self._summary(CORE_TASKS, offset=0.1)
        core_graph["cohort_acceptance"] = str(core_graph_acceptance)
        core_delta = self._delta(CORE_TASKS)
        core_delta["cohort_acceptance"] = {
            "control": str(core_control_acceptance),
            "treatment": str(core_graph_acceptance),
        }
        replay_control = self._summary((REPLAY_TASK,), offset=0.0)
        replay_control["cohort_acceptance"] = str(reactive_acceptance)
        replay_graph = self._summary((REPLAY_TASK,), offset=0.1)
        replay_graph["cohort_acceptance"] = str(graph_acceptance)
        replay_delta = self._delta((REPLAY_TASK,))
        replay_delta["cohort_acceptance"] = {
            "control": str(reactive_acceptance),
            "treatment": str(graph_acceptance),
        }

        core_figure = root / "graph_core_comparison.svg"
        core_figure.write_text("<svg/>", encoding="utf-8")
        monitor_figure = root / "graph_monitor_mechanism_case.svg"
        monitor_figure.write_text("<svg/>", encoding="utf-8")
        monitor_case = {
            "case_kind": "semantic-divergence",
            "task_id": REPLAY_TASK,
            "protocol_identity": {
                "schema_version": "p2_e1_generic_base_formal_v2",
                "experiment_id": "P2-E1",
            },
            "benchmark_control_source": {
                **EXPECTED_BENCHMARK_CONTROL_SOURCE,
                "formal_run_stamp": "20260901T010203Z",
            },
            "matched_statistical_key": {
                "seed": 20260808,
                "rotation": "rotation_0",
                "sample_id": "sequence-0001",
                "task_id": REPLAY_TASK,
            },
            "control": {"semantic_sequence": ["data.read_window", "submit"]},
            "treatment": {
                "semantic_sequence": ["data.read_window", "op.list", "submit"],
                "decision_states": ["Inspect", "Hypothesize", "Submit"],
            },
        }
        return argparse.Namespace(
            core_control_summary=self._write(root, "core_control.json", core_control),
            core_graph_summary=self._write(root, "core_graph.json", core_graph),
            core_paired_delta=self._write(root, "core_delta.json", core_delta),
            core_state_summary=self._write(
                root,
                "core_states.json",
                self._state_summary(CORE_TASKS, episodes=CORE_EPISODES_PER_TASK),
            ),
            core_control_acceptance=core_control_acceptance,
            core_graph_acceptance=core_graph_acceptance,
            core_comparison_figure=core_figure,
            monitor_mechanism_json=self._write(
                root, "graph_monitor_mechanism_case.json", monitor_case
            ),
            monitor_mechanism_figure=monitor_figure,
            reactive_summary=self._write(root, "replay_control.json", replay_control),
            graph_summary=self._write(root, "replay_graph.json", replay_graph),
            paired_delta=self._write(root, "replay_delta.json", replay_delta),
            state_summary=self._write(
                root,
                "replay_states.json",
                self._state_summary((REPLAY_TASK,), episodes=REPLAY_EPISODES),
            ),
            reactive_acceptance=reactive_acceptance,
            graph_acceptance=graph_acceptance,
            output=root / "graph_manuscript_results.md",
            manuscript=manuscript,
            protocol=DEFAULT_PROTOCOL,
            expected_benchmark_formal_run_stamp="20260901T010203Z",
            core_figure_output=root / "p2_e1_core_primary.svg",
            state_json_output=root / "p2_e1_graph_state_summary_v2.json",
            state_table_output=root / "p2_e1_graph_state_summary.md",
        )

    def _combined_result(self, args: argparse.Namespace) -> dict[str, object]:
        def load(path: Path) -> dict[str, object]:
            return json.loads(path.read_text(encoding="utf-8"))

        core_control = load(args.core_control_summary)
        core_treatment = load(args.core_graph_summary)
        core_paired = load(args.core_paired_delta)
        replay_control = load(args.reactive_summary)
        replay_treatment = load(args.graph_summary)
        replay_paired = load(args.paired_delta)
        for value in (core_control, core_treatment, core_paired):
            value.update(
                {
                    "registered_evidence_class": "formal",
                    "result_role": "confirmatory",
                    "replay_missing_score_policy_id": None,
                }
            )
        for summary in (core_control, core_treatment):
            for task in CORE_TASKS:
                summary["summary"][task].update(  # type: ignore[index]
                    {"episodes": CORE_EPISODES_PER_TASK, "bearings": 32}
                )
        for value in (replay_control, replay_treatment, replay_paired):
            value.update(
                {
                    "registered_evidence_class": "formal",
                    "result_role": "confirmatory",
                    "replay_missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
                }
            )
        for summary in (replay_control, replay_treatment):
            task = summary["summary"][REPLAY_TASK]  # type: ignore[index]
            task.update(
                {
                    "episodes": REPLAY_EPISODES,
                    "bearings": 8,
                    "evaluation_contract": {
                        "missing_assigned_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID
                    },
                }
            )
            task["task"].update(  # type: ignore[index]
                {
                    "assigned_windows": 3 * REPLAY_EPISODES,
                    "submitted_windows": 3 * REPLAY_EPISODES,
                    "missing_assigned_scores": 0,
                    "score_coverage": 1.0,
                }
            )
        protocol = yaml.safe_load(DEFAULT_PROTOCOL.read_text(encoding="utf-8"))
        benchmark_topology = {
            "contract": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
            "benchmark_repository": BENCHMARK_REPOSITORY,
            "benchmark_revision": "a" * 40,
            "data_factory_repository": DATA_FACTORY_REPOSITORY,
            "data_factory_revision": "b" * 40,
            "data_factory_distribution_version": "0.2.1",
            "data_factory_lock_version": "0.2.1",
        }
        graph_topology = {
            "contract": P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
            "benchmark_formal_execution_topology": json.loads(
                json.dumps(benchmark_topology)
            ),
            "source_repositories": {
                "benchmark": BENCHMARK_REPOSITORY,
                "data_factory": DATA_FACTORY_REPOSITORY,
                "p2": P2_REPOSITORY,
            },
            "source_revisions": {
                "benchmark": "a" * 40,
                "data_factory": "b" * 40,
                "p2": "c" * 40,
            },
            "formal_sources_clean": {
                "benchmark": True,
                "data_factory": True,
                "p2": True,
            },
            "canonical_origins_verified": {
                "benchmark": True,
                "data_factory": True,
                "p2": True,
            },
            "p2_formal_reproducibility_paths": list(
                P2_FORMAL_REPRODUCIBILITY_PATHS
            ),
        }
        return {
            "schema_version": "p2_e1_generic_base_formal_v2_result",
            "gate_id": "P2-E1",
            "accepted": True,
            "status": "accepted_paired_result",
            "provider_calls": 0,
            "benchmark_control_source": {
                **EXPECTED_BENCHMARK_CONTROL_SOURCE,
                "formal_run_stamp": args.expected_benchmark_formal_run_stamp,
            },
            "formal_execution_topology": {
                "benchmark_control": benchmark_topology,
                "graph_treatment": graph_topology,
                "shared_benchmark_data_factory": json.loads(
                    json.dumps(benchmark_topology)
                ),
            },
            "protocol_identity": {
                "schema_version": protocol["schema_version"],
                "experiment_id": protocol["experiment_id"],
            },
            "frozen_profile": protocol["frozen_profile"],
            "registered_design": protocol["registered_design"],
            "analysis": protocol["analysis"],
            "evaluator_private_views_read": 2 * (192 + REPLAY_EPISODES),
            "effect_estimates_emitted": 45,
            "registered_denominators": {
                "core_per_arm": 192,
                "replay_per_arm": REPLAY_EPISODES,
            },
            "registered_endpoints": {
                task: list(endpoints)
                for task, endpoints in REGISTERED_ENDPOINTS.items()
            },
            "replay_missing_score_policy_id": REPLAY_MISSING_SCORE_POLICY_ID,
            "direction": "GraphDecisionAgent_minus_Benchmark_GenericLLMToolAgent",
            "graph_state_summaries": {
                "core": load(args.core_state_summary),
                "replay": load(args.state_summary),
            },
            "arm_summaries": {
                "core": {"control": core_control, "treatment": core_treatment},
                "replay": {
                    "control": replay_control,
                    "treatment": replay_treatment,
                },
            },
            "paired_bearing_bootstrap": {
                "core": core_paired,
                "replay": replay_paired,
            },
            "primary_endpoint": PRIMARY_ENDPOINT,
            "gates": {
                "arms": {
                    name: {
                        "accepted": True,
                        "statistical_outcomes": expected,
                        "expected_statistical_outcomes": expected,
                        "blockers": [],
                    }
                    for name, expected in {
                        "generic_core": 192,
                        "graph_core": 192,
                        "generic_replay": REPLAY_EPISODES,
                        "graph_replay": REPLAY_EPISODES,
                    }.items()
                },
                "paired_cohorts": {
                    scope: {
                        "accepted": True,
                        "expected_pairs": expected,
                        "matched_statistical_keys": expected,
                        "control_only_keys": 0,
                        "treatment_only_keys": 0,
                        "blockers": [],
                    }
                    for scope, expected in {
                        "core": 192,
                        "replay": REPLAY_EPISODES,
                    }.items()
                },
                "all_four_arm_gates_accepted": True,
                "both_exact_pairing_gates_accepted": True,
            },
            "blockers": [],
            "claim_boundary": (
                "Accepted absolute and paired estimates are available only when accepted=true. "
                "When false, arm_summaries and paired_bearing_bootstrap are null and no "
                "partial-prefix estimate exists."
            ),
        }

    def _activate_combined(
        self,
        root: Path,
        args: argparse.Namespace,
        result: dict[str, object] | None = None,
    ) -> dict[str, object]:
        value = self._combined_result(args) if result is None else result
        args.combined_result = self._write(root, "combined_result.json", value)
        protocol = yaml.safe_load(DEFAULT_PROTOCOL.read_text(encoding="utf-8"))
        protocol["outputs"]["readiness"] = str(root / "readiness.json")
        protocol["outputs"]["result"] = str(args.combined_result)
        publication = protocol["outputs"]["accepted_publication"]
        publication["table"] = str(args.output)
        publication["core_figure"] = str(args.core_figure_output)
        publication["state_json"] = str(args.state_json_output)
        publication["state_table"] = str(args.state_table_output)
        publication["manuscript"] = str(args.manuscript)
        args.protocol = root / "active_protocol.yaml"
        args.protocol.write_text(
            yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8"
        )
        args.core_control_summary = None
        args.core_graph_summary = None
        args.core_paired_delta = None
        args.core_control_acceptance = None
        args.core_graph_acceptance = None
        args.core_state_summary = None
        args.state_summary = None
        args.core_comparison_figure = None
        args.monitor_mechanism_json = None
        args.monitor_mechanism_figure = None
        return value

    def test_legacy_publication_is_forbidden_without_combined_result(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "legacy publication is forbidden"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_finalizer_result_renders_without_legacy_gate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            write_table(args)
            rendered = args.output.read_text(encoding="utf-8")
            self.assertIn("# Accepted replay task-primary comparison", rendered)
            self.assertIn("| Primary | Monitoring Average Precision |", rendered)
            self.assertIn("| Task primary | Diagnosis Macro-F1 |", rendered)
            self.assertTrue(args.core_figure_output.is_file())
            self.assertTrue(args.state_json_output.is_file())
            self.assertTrue(args.state_table_output.is_file())
            ET.fromstring(args.core_figure_output.read_text(encoding="utf-8"))

    def test_combined_primary_endpoint_drift_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            result = self._combined_result(args)
            result["primary_endpoint"] = {
                "cohort": "replay",
                "task": REPLAY_TASK,
                "metric": "rollout.grounded_completion",
            }
            self._activate_combined(root, args, result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "primary_endpoint"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_tables_render_before_optional_figures_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.monitor_mechanism_json = None
            args.monitor_mechanism_figure = None
            write_table(args)
            manuscript = args.manuscript.read_text(encoding="utf-8")
            self.assertIn("| Primary | Monitoring Average Precision |", manuscript)
            self.assertIn("| Task primary | Diagnosis Macro-F1 |", manuscript)
            self.assertEqual(manuscript.count(CORE_MANUSCRIPT_HEADING), 1)
            self.assertEqual(manuscript.count(REPLAY_MANUSCRIPT_HEADING), 1)
            self.assertEqual(manuscript.count(FIGURES_MANUSCRIPT_HEADING), 1)
            self.assertNotIn("figures pending", manuscript)
            self.assertIn("p2_e1_core_primary.svg", manuscript)
            self.assertIn("No descriptive replay mechanism case is admitted", manuscript)
            self.assertTrue(args.core_figure_output.is_file())

    def test_combined_result_rejects_external_state_override_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.core_state_summary = self._write(root, "override.json", {})
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "forbids external Graph state"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertFalse(args.core_figure_output.exists())
            self.assertFalse(args.state_json_output.exists())
            self.assertFalse(args.state_table_output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_identity_drift_fails_closed(self) -> None:
        mutations = {
            "frozen profile": lambda result: result["frozen_profile"].__setitem__(
                "model", "wrong/model"
            ),
            "formal stamp": lambda result: result[
                "benchmark_control_source"
            ].__setitem__("formal_run_stamp", "20260902T010203Z"),
            "control profile": lambda result: result[
                "benchmark_control_source"
            ].__setitem__("profile_id", "wrong-profile"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args = self._args(root)
                result = self._combined_result(args)
                mutate(result)
                self._activate_combined(root, args, result)
                before = args.manuscript.read_bytes()
                with self.assertRaises(ResultsPending):
                    write_table(args)
                self.assertFalse(args.output.exists())
                self.assertFalse(args.core_figure_output.exists())
                self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_paired_delta_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            result = self._combined_result(args)
            result["paired_bearing_bootstrap"]["replay"]["estimate"][REPLAY_TASK][
                "task.average_precision"
            ] = 0.25
            self._activate_combined(root, args, result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "paired point arithmetic drift"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertFalse(args.core_figure_output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_replay_accounting_tamper_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            result = self._combined_result(args)
            task = result["arm_summaries"]["replay"]["control"]["summary"][
                REPLAY_TASK
            ]["task"]
            task["missing_assigned_scores"] = 1
            self._activate_combined(root, args, result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "replay score accounting"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_second_replace_failure_restores_every_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.monitor_mechanism_json = None
            args.monitor_mechanism_figure = None
            targets = (
                args.output,
                args.core_figure_output,
                args.state_json_output,
                args.state_table_output,
                args.manuscript,
            )
            for index, target in enumerate(targets):
                target.write_bytes(f"original-{index}".encode("utf-8"))
            # Restore a valid marked manuscript after seeding the other targets.
            args.manuscript.write_text(
                "Before\n"
                "<!-- GRAPH_CORE_PRIMARY_COMPACT:BEGIN -->\n\ncore pending\n\n"
                "<!-- GRAPH_CORE_PRIMARY_COMPACT:END -->\n"
                "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:BEGIN -->\n\nreplay pending\n\n"
                "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:END -->\n"
                "<!-- GRAPH_FORMAL_FIGURES:BEGIN -->\n\nfigures pending\n\n"
                "<!-- GRAPH_FORMAL_FIGURES:END -->\nAfter\n",
                encoding="utf-8",
            )
            originals = {target: target.read_bytes() for target in targets}
            real_replace = os.replace
            replacement_count = 0

            def fail_second_replace(source: Path, destination: Path) -> None:
                nonlocal replacement_count
                replacement_count += 1
                if replacement_count == 2:
                    raise OSError("simulated second replace failure")
                real_replace(source, destination)

            with patch(
                "scripts.render_graph_manuscript_table._replace_path",
                side_effect=fail_second_replace,
            ):
                with self.assertRaisesRegex(OSError, "simulated second replace failure"):
                    write_table(args)
            self.assertEqual(replacement_count, 2)
            for target, original in originals.items():
                self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(root.glob(".*.tmp")), [])

    def test_combined_output_alias_is_rejected_before_writes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.monitor_mechanism_json = None
            args.monitor_mechanism_figure = None
            args.core_figure_output = args.output
            protocol = yaml.safe_load(args.protocol.read_text(encoding="utf-8"))
            protocol["outputs"]["accepted_publication"]["core_figure"] = str(
                args.output
            )
            args.protocol.write_text(
                yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8"
            )
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "outputs must be distinct"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_result_requires_finalizer_counters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            result = self._combined_result(args)
            del result["evaluator_private_views_read"]
            self._activate_combined(root, args, result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "finalizer output schema"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_result_requires_exact_formal_execution_topology(self) -> None:
        for mutation, message in (
            ("missing", "finalizer output schema"),
            ("shared_drift", "shared Benchmark/Data Factory topology drifted"),
            ("p2_revision", "invalid p2 revision"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args = self._args(root)
                result = self._combined_result(args)
                if mutation == "missing":
                    del result["formal_execution_topology"]
                elif mutation == "shared_drift":
                    result["formal_execution_topology"][  # type: ignore[index]
                        "shared_benchmark_data_factory"
                    ]["benchmark_revision"] = "d" * 40
                else:
                    result["formal_execution_topology"]["graph_treatment"][  # type: ignore[index]
                        "source_revisions"
                    ]["p2"] = "not-a-revision"
                self._activate_combined(root, args, result)
                before = args.manuscript.read_bytes()
                with self.assertRaisesRegex(ResultsPending, message):
                    write_table(args)
                self.assertFalse(args.output.exists())
                self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_core_episode_and_bearing_counts_are_bound(self) -> None:
        for field, value in (("episodes", 95), ("bearings", 31)):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args = self._args(root)
                result = self._combined_result(args)
                result["arm_summaries"]["core"]["control"]["summary"][  # type: ignore[index]
                    ANOMALY_TASK
                ][field] = value
                self._activate_combined(root, args, result)
                before = args.manuscript.read_bytes()
                with self.assertRaisesRegex(ResultsPending, "episode/bearing counts"):
                    write_table(args)
                self.assertFalse(args.output.exists())
                self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_bootstrap_seed_and_interval_count_are_bound(self) -> None:
        for mutation, message in (
            ("seed", "bootstrap seed"),
            ("interval_count", "interval/count availability"),
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                args = self._args(root)
                result = self._combined_result(args)
                paired = result["paired_bearing_bootstrap"]["replay"]
                if mutation == "seed":
                    paired["seed"] = 7
                else:
                    paired["bearing_bootstrap_valid_replicates"][REPLAY_TASK][
                        "task.average_precision"
                    ] = 0
                self._activate_combined(root, args, result)
                before = args.manuscript.read_bytes()
                with self.assertRaisesRegex(ResultsPending, message):
                    write_table(args)
                self.assertFalse(args.output.exists())
                self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_state_summary_rejects_unexpected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            result = self._combined_result(args)
            result["graph_state_summaries"]["core"][ANOMALY_TASK][
                "evaluator_private_target"
            ] = "must-not-publish"
            self._activate_combined(root, args, result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "unexpected or missing fields"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertFalse(args.state_json_output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_publication_path_must_match_protocol(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.state_json_output = root / "undeclared-state.json"
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "differs from protocol"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertFalse(args.state_json_output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_mechanism_input_is_omitted_until_bound_extractor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            self._activate_combined(root, args)
            args.monitor_mechanism_json = root / "unbound-case.json"
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "until a bound extractor exists"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_policy_figure_separates_base_and_dynamic_full_relations(self) -> None:
        svg = render_svg()
        self.assertEqual(
            (ROOT / "paper/assets/figures/graph_policy_states.svg").read_text(
                encoding="utf-8"
            ),
            svg,
        )
        self.assertEqual(svg.count('data-state="'), len(STATES))
        self.assertEqual(svg.count('data-edge="'), 2 * len(STATES) ** 2)
        for state in STATES:
            self.assertEqual(svg.count(f'data-state="{state}"'), 1)
            for target in STATES:
                self.assertEqual(
                    svg.count(f'data-edge="base-v6:{state}-to-{target}"'), 1
                )
                self.assertEqual(
                    svg.count(f'data-edge="dynamic-full:{state}-to-{target}"'), 1
                )

        xml_root = ET.fromstring(svg)
        for relation_id, transitions in (
            ("base-v6", ALLOWED_TRANSITIONS),
            ("dynamic-full", DYNAMIC_LEGAL_TRANSITIONS["full"]),
        ):
            cells = [
                element
                for element in xml_root.iter()
                if element.attrib.get("data-relation") == relation_id
            ]
            self.assertEqual(len(cells), len(STATES) ** 2)
            self.assertEqual(
                sum(cell.attrib.get("data-legal") == "true" for cell in cells),
                sum(len(targets) for targets in transitions.values()),
            )

        self.assertIn("Base-v6 declared relation (50 edges)", svg)
        self.assertIn("Dynamic-full profile relation (33 edges)", svg)
        self.assertIn("Monitor and Revise are unreachable", svg)
        self.assertIn("provider-bound formal cohort has not run", svg)
        self.assertNotIn("complete executable transition relation", svg.lower())

        manuscript = (ROOT / "paper/draft/main.md").read_text(encoding="utf-8")
        abstract = manuscript.split("## 1. Introduction", 1)[0]
        self.assertIn("Monitor and Revise are unreachable", abstract)
        self.assertIn("formal coverage is 0/240", abstract)
        self.assertIn("target-adverse assigned-window Average Precision", abstract)
        self.assertIn("50-edge base-v6", manuscript)
        self.assertIn("33-edge dynamic-full", manuscript)
        self.assertIn("### 1.1 Contributions", manuscript)
        self.assertNotIn("*Pending:", manuscript)
        for false_heading in (
            "#### Accepted dynamic-v3 horizon and ablation comparisons",
            "#### Accepted P2-E8 Ottawa cross-dataset comparison",
            "#### Accepted P2-E9 reliability comparison",
            "#### Accepted replay task-primary comparison",
            "#### Accepted core comparison",
            "#### Accepted formal figures",
        ):
            self.assertNotIn(false_heading, manuscript)
        for marker in (
            "P2_DYNAMIC_FORMAL",
            "P2_E8_OTTAWA",
            "P2_E9_RELIABILITY",
            "GRAPH_MONITOR_PRIMARY_COMPACT",
            "GRAPH_CORE_PRIMARY_COMPACT",
            "GRAPH_FORMAL_FIGURES",
        ):
            self.assertEqual(manuscript.count(f"<!-- {marker}:BEGIN -->"), 1)
            self.assertEqual(manuscript.count(f"<!-- {marker}:END -->"), 1)

        paper_yaml_text = (ROOT / "paper/paper.yaml").read_text(encoding="utf-8")
        evidence = (ROOT / "paper/experiments/evidence_matrix.md").read_text(
            encoding="utf-8"
        )
        paper = yaml.safe_load(paper_yaml_text)
        reference = paper["shared_provider_free_reference"]
        self.assertEqual(
            reference["aggregate"],
            "../p01-phm-agent-benchmark/paper/experiments/results/"
            "p0_active_v02_provider_free_reference_subset_v1.json",
        )
        self.assertEqual(reference["benchmark_revision_short"], "b6cf5796")
        self.assertEqual(reference["data_factory_revision_short"], "5805071")
        self.assertEqual(reference["formal_run_stamp"], "20260903T080515Z")
        self.assertEqual(reference["core_episodes"], 64)
        self.assertEqual(reference["replay_episodes"], 8)
        aggregate = json.loads(
            (ROOT / reference["aggregate"]).read_text(encoding="utf-8")
        )
        self.assertIs(aggregate["accepted"], True)
        self.assertEqual(
            aggregate["accepted_scope"],
            "B0_B1_B2_active_v0_2_provider_free_reference_subset_only",
        )
        self.assertEqual(
            aggregate["execution"]["benchmark_execution_revision"],
            reference["benchmark_revision"],
        )
        self.assertEqual(
            aggregate["execution"]["data_factory_revision"],
            reference["data_factory_revision"],
        )
        self.assertEqual(
            aggregate["execution"]["formal_run_stamp"],
            reference["formal_run_stamp"],
        )
        self.assertEqual(aggregate["inputs"]["B2_core"]["observed_unique_episodes"], 64)
        self.assertEqual(aggregate["inputs"]["B2_replay"]["observed_unique_episodes"], 8)
        self.assertNotIn(
            "deterministic_runbundle_v1", manuscript + paper_yaml_text + evidence
        )

        status = load_current_mechanics()
        current_table = render_current_mechanics_table(status)
        current_svg = render_current_mechanics_svg(status)
        self.assertEqual(
            (ROOT / "paper/assets/tables/p2_current_mechanics_status.md").read_text(
                encoding="utf-8"
            ),
            current_table,
        )
        self.assertEqual(
            (ROOT / "paper/assets/figures/p2_current_mechanics_status.svg").read_text(
                encoding="utf-8"
            ),
            current_svg,
        )
        self.assertIn("Benchmark Generic (Reactive-equivalent)", current_table)
        self.assertIn("10/10 exact-six Mock cells", current_table)
        self.assertIn("runner ready; 240/240 dry-run commands emitted, 0 invoked", current_table)
        self.assertIn("runner 17/17", current_table)
        self.assertIn("dynamic-focused 50/50", current_table)
        self.assertIn("0/240 formal units", current_table)
        self.assertIn("a Graph treatment effect", current_table)
        dynamic_status = status["dynamic_v3"]
        self.assertTrue(dynamic_status["formal_runner_implemented"])
        self.assertTrue(dynamic_status["runtime_ready"])
        self.assertEqual(dynamic_status["commands_invoked"], 0)
        self.assertFalse(dynamic_status["environment_values_read"])
        self.assertFalse(dynamic_status["probe_evidence_read"])
        self.assertEqual(dynamic_status["provider_calls"], 0)
        self.assertEqual(dynamic_status["filesystem_writes"], 0)
        current_root = ET.fromstring(current_svg)
        dynamic_group = next(
            element
            for element in current_root.iter()
            if element.attrib.get("data-gate") == "dynamic-v3"
        )
        formal_text = next(
            element
            for element in dynamic_group.iter()
            if element.attrib.get("data-formal-expected") == "240"
        )
        self.assertEqual(formal_text.attrib.get("data-formal-observed"), "0")
        command_text = next(
            element
            for element in dynamic_group.iter()
            if element.attrib.get("data-planned-commands") == "240"
        )
        self.assertEqual(command_text.attrib.get("data-formal-runner-ready"), "true")
        self.assertEqual(command_text.attrib.get("data-emitted-commands"), "240")
        self.assertEqual(command_text.attrib.get("data-invoked-commands"), "0")
        evidence_text = next(
            element
            for element in dynamic_group.iter()
            if element.attrib.get("data-formal-runner-tests") == "17"
        )
        self.assertEqual(evidence_text.attrib.get("data-dynamic-tests"), "50")
        self.assertEqual(evidence_text.attrib.get("data-provider-calls"), "0")
        self.assertIn(
            "../assets/figures/p2_current_mechanics_status.svg", manuscript
        )
        self.assertIn("dedicated formal runner is implemented and ready", manuscript)
        self.assertIn("zero environment reads, zero probe reads", manuscript)
        self.assertIn("240/240 dry-run commands", manuscript)
        self.assertIn("17/17", manuscript)
        self.assertIn("50/50", manuscript)
        self.assertIn("0/240 formal units", manuscript)


if __name__ == "__main__":
    unittest.main()
