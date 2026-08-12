"""B5 graph-guided policy over the benchmark-owned action surface."""

from __future__ import annotations

from typing import Any

from phm_agent_benchmark.phase1 import GenericLLMToolAgent
from phm_agent_benchmark.phase1.contracts import EpisodeTrajectory, LLMClient, TaskInstance

GRAPH_STATES = ("orient", "acquire", "analyze", "model", "recover", "submit")
ALLOWED_TRANSITIONS = {
    "orient": {"acquire"},
    "acquire": {"analyze", "recover"},
    "analyze": {"analyze", "model", "recover"},
    "model": {"analyze", "submit", "recover"},
    "recover": {"acquire", "analyze", "model", "submit", "recover"},
    "submit": {"submit"},
}


def _success(trajectory: EpisodeTrajectory, name: str) -> bool:
    return any(step.tool_name == name and step.error is None for step in trajectory.steps)


class ReactivePHMAgent(GenericLLMToolAgent):
    agent_id = "reactive-phm-agent"

    def system_prompt(self, task: TaskInstance) -> str:
        del task
        return (
            "Complete the PHM task with one benchmark tool call per turn. React to the latest "
            "observation, inspect schemas when needed, recover from executable errors, and submit "
            "only runtime-produced artifact references."
        )


class GraphDecisionAgent(GenericLLMToolAgent):
    agent_id = "graph-decision-agent"

    def __init__(self, client: LLMClient, *, model: str) -> None:
        super().__init__(client, model=model)

    def decision_state(self, task: TaskInstance, trajectory: EpisodeTrajectory) -> str:
        del task
        if trajectory.steps and trajectory.steps[-1].error is not None:
            return "recover"
        if not trajectory.steps:
            return "orient"
        if not _success(trajectory, "data.read_window"):
            return "acquire"
        if not _success(trajectory, "model.list"):
            return "analyze"
        if not _success(trajectory, "model.predict"):
            return "model"
        return "submit"

    def system_prompt(self, task: TaskInstance) -> str:
        del task
        return (
            "You are a graph-guided PHM Agent. At each turn operate inside one state: orient, "
            "acquire, analyze, model, recover, or submit. Follow the compact PHM graph, make one "
            "tool call, and use only public observations and returned artifact references. A tool "
            "failure moves to recover; recover by changing a concrete action or parameter rather "
            "than repeating the same failed call."
        )

    def available_tools(
        self,
        task: TaskInstance,
        trajectory: EpisodeTrajectory,
        tools: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        state = self.decision_state(task, trajectory)
        allowed = {
            "orient": {"data.search", "data.describe"},
            "acquire": {"data.search", "data.describe", "data.read_window"},
            "analyze": {"data.summarize", "op.list", "op.schema", "op.run"},
            "model": {"op.schema", "op.run", "model.list", "model.schema", "model.predict"},
            "recover": {
                "data.describe", "data.read_window", "data.summarize", "op.list", "op.schema", "op.run",
                "model.list", "model.schema", "model.predict", "submit",
            },
            "submit": {"model.schema", "model.predict", "submit"},
        }[state]
        return [tool for tool in tools if tool["function"]["name"] in allowed]
