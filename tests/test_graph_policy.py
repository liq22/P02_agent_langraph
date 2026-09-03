from __future__ import annotations

import copy
import unittest
from pathlib import Path
from types import SimpleNamespace

from phm_agent_benchmark.phase1 import (
    EpisodeTrajectory,
    GenericLLMToolAgent,
    TrajectoryStep,
)
from phm_graph_agent import (
    GraphDecisionAgent,
    GraphGuidedPHMAgent,
    ReactiveSequentialAgent,
    STATE_TOOLS,
    STATES,
    decision_state,
    transition_validity,
)
from scripts.run_graph_experiment import _factory


def _step(
    index: int,
    tool: str,
    state: str,
    error: str | None = None,
    *,
    tool_args: dict[str, object] | None = None,
    tool_result: dict[str, object] | None = None,
) -> TrajectoryStep:
    return TrajectoryStep(
        index,
        {},
        "tool_call",
        tool,
        tool_args or {},
        tool_result=tool_result,
        error=error,
        decision_state=state,
    )


class GraphPolicyTest(unittest.TestCase):
    def test_production_agent_and_runner_are_p1_independent(self) -> None:
        root = Path(__file__).resolve().parents[1]
        production = (
            root / "src/phm_graph_agent/agent.py",
            root / "scripts/run_graph_experiment.py",
        )
        for path in production:
            with self.subTest(path=path):
                source = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("phm_skills", source)
                self.assertNotIn("p01-phmskills", source)

    def test_runner_constructs_generic_control_and_generic_derived_graph(self) -> None:
        common = {
            "runtime": "mock",
            "inject_recoverable_error": False,
            "graph_profile": "full",
            "runtime_contract": "phase1_opaque_sample_vibration_feature_schema_v6",
        }
        reactive = _factory(SimpleNamespace(arm="reactive", **common))("ridge-v1")
        graph = _factory(SimpleNamespace(arm="graph", **common))("ridge-v1")
        self.assertIs(type(reactive), ReactiveSequentialAgent)
        self.assertIs(type(graph), GraphDecisionAgent)
        self.assertIs(GraphGuidedPHMAgent, GraphDecisionAgent)
        self.assertIsInstance(reactive, GenericLLMToolAgent)
        self.assertIsInstance(graph, GenericLLMToolAgent)
        self.assertEqual(reactive.model, graph.model)
        self.assertEqual(reactive.catalog_disclosure, graph.catalog_disclosure)

    def test_graph_prompt_only_appends_decision_state_guidance(self) -> None:
        reactive = GenericLLMToolAgent(client=None)
        graph = GraphDecisionAgent(client=None)
        for task_id in (
            "cold_start_fault_diagnosis",
            "unsupervised_anomaly_detection",
            "online_replay_monitoring",
        ):
            with self.subTest(task_id=task_id):
                task = SimpleNamespace(task_id=task_id)
                reactive_prompt = reactive.system_prompt(task)
                graph_prompt = graph.system_prompt(task)
                self.assertTrue(graph_prompt.startswith(reactive_prompt + "\n\n"))
                suffix = graph_prompt[len(reactive_prompt) :]
                self.assertIn("Current decision state: Inspect", suffix)
                self.assertIn("Choose exactly one of the tools exposed", suffix)

    def test_graph_decision_control_only_filters_shared_tool_schemas(self) -> None:
        names = sorted(set().union(*STATE_TOOLS.values()))
        tools = [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": f"shared schema for {name}",
                },
            }
            for name in names
        ]
        original = copy.deepcopy(tools)
        trajectory = EpisodeTrajectory("cold_start_fault_diagnosis", "graph")
        task = SimpleNamespace(task_id="cold_start_fault_diagnosis")
        reactive = GenericLLMToolAgent(client=None)
        graph = GraphDecisionAgent(client=None)

        self.assertIs(reactive.available_tools(task, trajectory, tools), tools)
        visible = graph.available_tools(task, trajectory, tools)
        self.assertEqual(tools, original)
        self.assertEqual(
            [tool["function"]["name"] for tool in visible],
            [name for name in names if name in STATE_TOOLS["Inspect"]],
        )
        for tool in visible:
            self.assertIs(tool, tools[names.index(tool["function"]["name"])])

    def test_eight_states_and_recovery_are_rollout_derived(self) -> None:
        trajectory = EpisodeTrajectory("cold_start_fault_diagnosis", "graph")
        self.assertEqual(len(STATES), 8)
        self.assertIn("Monitor", STATES)
        self.assertIn("Revise", STATES)
        self.assertEqual(transition_validity(trajectory), 0.0)
        self.assertEqual(decision_state(trajectory), "Inspect")
        trajectory.steps.append(_step(0, "data.read_window", "Inspect"))
        self.assertEqual(decision_state(trajectory), "Hypothesize")
        trajectory.steps.append(_step(1, "data.summarize", "Hypothesize"))
        self.assertEqual(decision_state(trajectory), "Hypothesize")
        trajectory.steps.append(_step(2, "op.list", "Hypothesize"))
        self.assertEqual(decision_state(trajectory), "Analyze")
        trajectory.steps.append(_step(3, "op.run", "Analyze", "bad parameter"))
        self.assertEqual(decision_state(trajectory), "Recover")
        trajectory.steps.append(_step(4, "op.run", "Recover"))
        trajectory.steps.append(_step(5, "model.schema", "Analyze"))
        self.assertEqual(decision_state(trajectory), "Check")
        trajectory.steps.append(_step(6, "model.predict", "Check"))
        self.assertEqual(decision_state(trajectory), "Submit")
        trajectory.steps.append(_step(7, "submit", "Submit"))
        self.assertEqual(transition_validity(trajectory), 1.0)

        model_routed = EpisodeTrajectory("cold_start_fault_diagnosis", "graph")
        model_routed.steps.append(_step(0, "data.read_window", "Inspect"))
        model_routed.steps.append(_step(1, "model.list", "Hypothesize"))
        self.assertEqual(decision_state(model_routed), "Analyze")

        failed_submit = EpisodeTrajectory("cold_start_fault_diagnosis", "graph")
        failed_submit.steps.extend(
            [
                _step(0, "data.read_window", "Inspect"),
                _step(1, "op.list", "Hypothesize"),
                _step(2, "model.schema", "Analyze"),
                _step(3, "model.predict", "Check"),
                _step(4, "submit", "Submit", "missing supporting refs"),
            ]
        )
        self.assertEqual(decision_state(failed_submit), "Recover")
        failed_submit.steps.append(_step(5, "model.schema", "Recover"))
        self.assertEqual(transition_validity(failed_submit), 1.0)

        failed_read = EpisodeTrajectory("cold_start_fault_diagnosis", "graph")
        failed_read.steps.append(
            _step(0, "data.read_window", "Inspect", "temporary read failure")
        )
        self.assertEqual(decision_state(failed_read), "Recover")
        failed_read.steps.append(_step(1, "data.read_window", "Recover"))
        self.assertEqual(decision_state(failed_read), "Hypothesize")
        failed_read.steps.append(_step(2, "op.list", "Hypothesize"))
        self.assertEqual(transition_validity(failed_read), 1.0)

    def test_replay_state_advances_only_for_distinct_sample_predictions(self) -> None:
        replay_ids = ("sample-a", "sample-b", "sample-c")
        trajectory = EpisodeTrajectory("online_replay_monitoring", "graph")
        trajectory.steps.extend(
            [
                _step(
                    0,
                    "model.predict",
                    "Check",
                    tool_result={"source_sample_id": "sample-a"},
                ),
                _step(
                    1,
                    "model.predict",
                    "Check",
                    tool_result={"source_sample_id": "sample-a"},
                ),
                _step(
                    2,
                    "model.predict",
                    "Check",
                    tool_result={"source_sample_id": "sample-b"},
                ),
            ]
        )
        self.assertEqual(decision_state(trajectory, replay_ids), "Inspect")
        trajectory.steps.append(
            _step(
                3,
                "model.predict",
                "Check",
                tool_result={"source_sample_id": "sample-c"},
            )
        )
        self.assertEqual(decision_state(trajectory, replay_ids), "Submit")

    def test_replay_analysis_counts_only_current_sample_operators(self) -> None:
        replay_ids = ("sample-a", "sample-b")
        trajectory = EpisodeTrajectory("online_replay_monitoring", "graph")
        trajectory.steps.extend(
            [
                _step(
                    0,
                    "data.read_window",
                    "Inspect",
                    tool_args={"sample_id": "sample-a"},
                ),
                _step(1, "op.list", "Hypothesize"),
            ]
        )
        for index in range(10):
            trajectory.steps.append(
                _step(
                    index + 2,
                    "op.run",
                    "Analyze",
                    tool_result={"source_sample_id": "sample-a"},
                )
            )
        trajectory.steps.append(
            _step(
                12,
                "op.run",
                "Analyze",
                tool_result={"source_sample_id": "sample-b"},
            )
        )
        self.assertEqual(decision_state(trajectory, replay_ids), "Analyze")
        trajectory.steps.append(
            _step(
                13,
                "op.run",
                "Analyze",
                tool_result={"source_sample_id": "sample-a"},
            )
        )
        self.assertEqual(decision_state(trajectory, replay_ids), "Check")


if __name__ == "__main__":
    unittest.main()
