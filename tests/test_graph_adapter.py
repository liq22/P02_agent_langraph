from __future__ import annotations

import unittest

from phm_agent_benchmark.phase1 import DeterministicMockLLM
from phm_agent_benchmark.phase1.contracts import EpisodeTrajectory, TaskInstance, TrajectoryStep
from graph_phm_paper import GraphDecisionAgent, evaluate_decision_states


class GraphAdapterTests(unittest.TestCase):
    def test_state_progression_and_recovery(self) -> None:
        task = TaskInstance("cold_start_fault_diagnosis", "s1", "healthy")
        trajectory = EpisodeTrajectory(task.task_id, "b5")
        agent = GraphDecisionAgent(DeterministicMockLLM(), model="mock")
        self.assertEqual("orient", agent.decision_state(task, trajectory))
        trajectory.steps.append(TrajectoryStep(0, task.public_observation(), "tool_call", "data.describe", {}, tool_result={}))
        self.assertEqual("acquire", agent.decision_state(task, trajectory))
        trajectory.steps.append(TrajectoryStep(1, task.public_observation(), "tool_call", "data.read_window", {}, error="bad bounds"))
        self.assertEqual("recover", agent.decision_state(task, trajectory))

    def test_state_metrics_reject_invalid_jump(self) -> None:
        valid = evaluate_decision_states([
            {"decision_state": "orient"},
            {"decision_state": "acquire"},
            {"decision_state": "analyze"},
            {"decision_state": "model"},
            {"decision_state": "submit"},
        ])
        invalid = evaluate_decision_states([
            {"decision_state": "orient"},
            {"decision_state": "submit"},
        ])
        self.assertEqual(1.0, valid["state_transition_validity"])
        self.assertEqual(0.0, invalid["state_transition_validity"])


if __name__ == "__main__":
    unittest.main()
