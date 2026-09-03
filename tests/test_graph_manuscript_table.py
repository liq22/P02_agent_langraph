from __future__ import annotations

import argparse
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

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
    CORE_EPISODES_PER_TASK,
    CORE_ROTATIONS,
    CORE_TASKS,
    PRIMARY_ENDPOINT,
    REGISTERED_ENDPOINTS,
    REPLAY_EPISODES,
    REPLAY_MISSING_SCORE_POLICY_ID,
    REPLAY_TASK,
    RUNTIME_CONTRACT,
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
            "evidence_class": "real_data_formal_candidate",
        }

    def _delta(self, tasks: tuple[str, ...]) -> dict[str, object]:
        source = self._summary(tasks, offset=0.0)
        estimates: dict[str, dict[str, float | None]] = {}
        for task in tasks:
            values = source["summary"][task]  # type: ignore[index]
            estimates[task] = {
                **{f"task.{name}": value for name, value in values["task"].items()},
                **{
                    f"rollout.{name}": value
                    for name, value in values["rollout"].items()
                },
            }
        return {
            "estimate": estimates,
            "bearing_bootstrap_95ci": source["bearing_bootstrap_95ci"],
            "bearing_bootstrap_valid_replicates": source[
                "bearing_bootstrap_valid_replicates"
            ],
            "bootstrap_iterations": 2000,
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
        return {
            "schema_version": "p2_e1_generic_base_formal_v2_result",
            "gate_id": "P2-E1",
            "accepted": True,
            "status": "accepted_paired_result",
            "provider_calls": 0,
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
        }

    def test_accepted_contract_renders_core_replay_states_and_figures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            write_table(args)
            rendered = args.output.read_text(encoding="utf-8")
            self.assertEqual(tuple(STATES), tuple(EXECUTABLE_STATES))
            self.assertEqual(
                tuple(STATES),
                (
                    "Inspect",
                    "Hypothesize",
                    "Analyze",
                    "Check",
                    "Monitor",
                    "Revise",
                    "Recover",
                    "Submit",
                ),
            )
            self.assertIn(
                "| cold_start_fault_diagnosis | Task primary | Diagnosis Macro-F1 |",
                rendered,
            )
            self.assertIn(
                "| unsupervised_anomaly_detection | Task primary | Anomaly completion-adjusted AP |",
                rendered,
            )
            self.assertIn("| Tool | Valid tool-call rate |", rendered)
            self.assertIn(
                "| online_replay_monitoring | Primary | Monitoring Average Precision |",
                rendered,
            )
            self.assertIn(
                "| online_replay_monitoring | Rollout | Grounded completion |",
                rendered,
            )
            self.assertIn("p95 step latency (seconds)", rendered)
            self.assertIn("N/A [CI N/A]; 0/2000", rendered)
            self.assertIn("1999/2000", rendered)
            for task in CORE_TASKS:
                self.assertEqual(rendered.count(f"| {task} | Recover |"), 1)
                self.assertEqual(rendered.count(f"| {task} | Monitor | 0.0000 | 0.0000 |"), 1)
                self.assertEqual(rendered.count(f"| {task} | Revise | 0.0000 | 0.0000 |"), 1)
            self.assertEqual(rendered.count(f"| {REPLAY_TASK} | Recovery |"), 3)
            self.assertEqual(
                rendered.count(f"| {REPLAY_TASK} | Monitor | 0.0000 | 0.0000 |"),
                1,
            )
            self.assertEqual(
                rendered.count(f"| {REPLAY_TASK} | Revise | 0.0000 | 0.0000 |"),
                1,
            )
            self.assertIn("defines no `public_condition_event`", rendered)
            self.assertIn("supports no dynamic-revision claim", rendered)
            self.assertIn("`graph_dynamic_ablation_protocol_v3`", rendered)
            self.assertIn("accepted provider-free mechanics", rendered)
            self.assertIn("0/240 formal coverage", rendered)
            manuscript = args.manuscript.read_text(encoding="utf-8")
            self.assertIn("../assets/figures/graph_core_comparison.svg", manuscript)
            self.assertIn(
                "../assets/figures/graph_monitor_mechanism_case.svg", manuscript
            )
            self.assertIn(
                "| cold_start_fault_diagnosis | Task primary | Diagnosis Macro-F1 |",
                manuscript,
            )

    def test_combined_finalizer_result_renders_without_legacy_gate_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            args.combined_result = self._write(
                root, "combined_result.json", self._combined_result(args)
            )
            args.core_control_summary = None
            args.core_graph_summary = None
            args.core_paired_delta = None
            args.core_control_acceptance = None
            args.core_graph_acceptance = None
            write_table(args)
            rendered = args.output.read_text(encoding="utf-8")
            self.assertIn("# Accepted replay task-primary comparison", rendered)
            self.assertIn("| Primary | Monitoring Average Precision |", rendered)
            self.assertIn("| Task primary | Diagnosis Macro-F1 |", rendered)

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
            args.combined_result = self._write(root, "combined_result.json", result)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "primary_endpoint"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_combined_tables_render_before_optional_figures_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self._args(root)
            args.combined_result = self._write(
                root, "combined_result.json", self._combined_result(args)
            )
            args.core_comparison_figure = None
            args.monitor_mechanism_json = None
            args.monitor_mechanism_figure = None
            write_table(args)
            manuscript = args.manuscript.read_text(encoding="utf-8")
            self.assertIn("| Primary | Monitoring Average Precision |", manuscript)
            self.assertIn("| Task primary | Diagnosis Macro-F1 |", manuscript)
            self.assertIn("figures pending", manuscript)
            self.assertNotIn("graph_core_comparison.svg", manuscript)

    def test_rejected_core_gate_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary), reject_core=True)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "accepted"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_rejected_replay_gate_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary), reject_replay=True)
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "accepted"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_contract_mismatch_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            gate = json.loads(args.core_graph_acceptance.read_text(encoding="utf-8"))
            gate["run_contracts"]["20260808:rotation_0"] = {
                "selected_diagnosis_model_id": "different-model"
            }
            args.core_graph_acceptance.write_text(json.dumps(gate), encoding="utf-8")
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "numerical run contracts"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_missing_figure_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            args.core_comparison_figure.unlink()
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "core comparison figure"):
                write_table(args)
            self.assertFalse(args.output.exists())
            self.assertEqual(before, args.manuscript.read_bytes())

    def test_invalid_core_state_contract_leaves_manuscript_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            args = self._args(Path(temporary))
            states = json.loads(args.core_state_summary.read_text(encoding="utf-8"))
            del states[ANOMALY_TASK]["state_episode_visitation_rate"]["Monitor"]
            args.core_state_summary.write_text(json.dumps(states), encoding="utf-8")
            before = args.manuscript.read_bytes()
            with self.assertRaisesRegex(ResultsPending, "eight executable states"):
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
        self.assertIn("dynamic-focused 46/46", current_table)
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
        self.assertEqual(evidence_text.attrib.get("data-dynamic-tests"), "46")
        self.assertEqual(evidence_text.attrib.get("data-provider-calls"), "0")
        self.assertIn(
            "../assets/figures/p2_current_mechanics_status.svg", manuscript
        )
        self.assertIn("dedicated formal runner is implemented and ready", manuscript)
        self.assertIn("zero environment reads, zero probe reads", manuscript)
        self.assertIn("240/240 dry-run commands", manuscript)
        self.assertIn("17/17", manuscript)
        self.assertIn("46/46", manuscript)
        self.assertIn("0/240 formal units", manuscript)


if __name__ == "__main__":
    unittest.main()
