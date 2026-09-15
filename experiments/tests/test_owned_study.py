import unittest
import json
import importlib.util
from pathlib import Path
from phm_agent_benchmark.research import study as shared
spec = importlib.util.spec_from_file_location("owned_study", Path(__file__).resolve().parents[1] / "study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)
study.parse = lambda argv: shared.parse(argv, experiments=study.EXPERIMENTS)
from phm_graph_agent.components import graph_history_without_state
study.graph_history_without_state = graph_history_without_state

class OwnedStudyTests(unittest.TestCase):
    def test_horizon_is_explicit_replay(self):
        args = study.parse(['plan','--experiment','horizon'])
        rows=shared.cells(args)
        self.assertEqual({r['task'] for r in rows},{'replay'})
        self.assertEqual({r['horizon'] for r in rows},{2,3,5})

    def test_factorial_sanitization_preserves_tool_observation(self):
        messages=[{'role':'tool','content':json.dumps({'decision_state':'Check','tool_result':{'score':.3},'error':None})}]
        cleaned=study.graph_history_without_state(messages)
        self.assertNotIn('decision_state',json.loads(cleaned[0]['content']))
        self.assertEqual(json.loads(cleaned[0]['content'])['tool_result'],{'score':.3})
        self.assertIn('decision_state',json.loads(messages[0]['content']))


    def test_four_arms_separate_prompt_and_tool_visibility(self):
        from types import SimpleNamespace
        from phm_agent_benchmark.phase1 import GenericLLMToolAgent, EpisodeTrajectory
        from phm_graph_agent import GraphDecisionAgent, STATE_TOOLS
        from phm_graph_agent.components import make_component_agent
        task = SimpleNamespace(task_id="cold_start_fault_diagnosis")
        trajectory = EpisodeTrajectory(task.task_id, "fixture")
        names = sorted(set().union(*STATE_TOOLS.values()))
        tools = [{"type": "function", "function": {"name": n}} for n in names]
        generic = GenericLLMToolAgent(client=None)
        graph = GraphDecisionAgent(client=None)
        for condition, cue, filtering in [("factorial-reactive", False, False),
            ("factorial-state", True, False), ("factorial-filter", False, True), ("factorial-both", True, True)]:
            agent = make_component_agent(condition, None, "fixture")
            with self.subTest(condition=condition):
                self.assertEqual(agent.system_prompt(task), (graph if cue else generic).system_prompt(task))
                self.assertEqual(agent.available_tools(task, trajectory, tools),
                    graph.available_tools(task, trajectory, tools) if filtering else tools)
