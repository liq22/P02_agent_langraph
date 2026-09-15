"""Independent cue/filter controls for the new component study."""
import json
from phm_agent_benchmark.phase1 import GenericLLMToolAgent
from .agent import GraphDecisionAgent

def graph_history_without_state(messages: list[dict]) -> list[dict]:
    """Remove the historical state cue in every arm of the new 2x2 experiment."""
    result = []
    for message in messages:
        row = dict(message)
        if row.get("role") == "tool":
            content = json.loads(row["content"])
            content.pop("decision_state", None)
            row["content"] = json.dumps(content, sort_keys=True)
        result.append(row)
    return result


def make_component_agent(condition, client, model):
    if condition not in {"factorial-reactive", "factorial-state", "factorial-filter", "factorial-both"}:
        raise ValueError("Unknown graph component condition: " + condition)
    state_cue = condition in {"factorial-state", "factorial-both"}
    filtering = condition in {"factorial-filter", "factorial-both"}

    class ComponentAgent(GraphDecisionAgent):
        """New factorial study; original graph profile is left unchanged."""
        def system_prompt(self, task):
            return super().system_prompt(task) if state_cue else GenericLLMToolAgent.system_prompt(self, task)
        def available_tools(self, task, trajectory, tools):
            return super().available_tools(task, trajectory, tools) if filtering else tools
        def conversation(self, task, trajectory):
            return graph_history_without_state(super().conversation(task, trajectory))
    agent = ComponentAgent(client, model=model)
    agent.agent_id = condition
    return agent
