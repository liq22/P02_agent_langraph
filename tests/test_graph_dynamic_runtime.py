from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import SimpleNamespace

import yaml
from scripts.run_graph_experiment import _load_dynamic_protocol

from phm_agent_benchmark.phase1 import EpisodeTrajectory, TrajectoryStep
from phm_agent_benchmark.phase1.environment import (
    PHASE1_BASE_RUNTIME_CONTRACT,
)
from phm_graph_agent import (
    ALLOWED_TRANSITIONS,
    DYNAMIC_LEGAL_TRANSITIONS,
    GRAPH_DYNAMIC_RUNTIME_CONTRACT,
    GraphDecisionAgent,
    GraphPolicyConfig,
    decision_state,
    legal_transitions,
    transition_validity_from_states,
)


ROOT = Path(__file__).resolve().parents[1]


def _step(
    index: int,
    tool_name: str,
    state: str,
    *,
    error: str | None = None,
    observation: dict[str, object] | None = None,
) -> TrajectoryStep:
    return TrajectoryStep(
        index=index,
        observation_summary=observation or {},
        action="tool_call",
        tool_name=tool_name,
        tool_args={"sample_id": "sample-a"},
        tool_result={"artifact_ref": "artifact://window/000001"},
        error=error,
        decision_state=state,
    )


def _task(*, event: bool) -> SimpleNamespace:
    context: dict[str, object] = {
        "replay_sample_ids": ["sample-a", "sample-b"],
        "replay_length": 2,
        "replay_cursor": 1,
    }
    if event:
        public_condition_event = {
            "event": "operating_condition_change",
            "event_id": "occ-00000001",
            "release_index": 1,
        }
        context["public_condition_event"] = public_condition_event
        context["public_condition_event_history"] = [public_condition_event]
    return SimpleNamespace(
        task_id="online_replay_monitoring",
        sample_id="sequence-0001",
        public_context=context,
        public_observation=lambda: {
            "task_id": "online_replay_monitoring",
            "sample_id": "sequence-0001",
            "context": context,
        },
    )


class GraphDynamicRuntimeTest(unittest.TestCase):
    def test_code_transition_tables_match_the_frozen_protocol_exactly(self):
        protocol = _load_dynamic_protocol(
            ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
        )
        expected = {
            profile: {
                state: set(targets)
                for state, targets in details["legal_transitions"].items()
            }
            for profile, details in protocol["graph_profiles"].items()
        }
        self.assertEqual(DYNAMIC_LEGAL_TRANSITIONS, expected)

    def test_full_and_four_ablations_have_observable_distinct_behavior(self):
        trajectory = EpisodeTrajectory("online_replay_monitoring", "graph")
        trajectory.steps.append(_step(0, "data.read_window", "Inspect"))
        event_states = {}
        post_event_states = {}
        for profile in (
            "full",
            "no_recovery_revision_edge",
            "no_observation_conditioned_branching",
            "no_persistent_graph_state",
            "no_replanning",
        ):
            config = GraphPolicyConfig.for_profile(
                profile, runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT
            )
            previous = None if not config.persistent_graph_state else "Inspect"
            event_states[profile] = decision_state(
                trajectory,
                ("sample-a", "sample-b"),
                config=config,
                previous_state=previous,
                observation_event="operating_condition_change",
            )
            previous = None if not config.persistent_graph_state else event_states[profile]
            post_event_states[profile] = decision_state(
                trajectory,
                ("sample-a", "sample-b"),
                config=config,
                previous_state=previous,
            )

        self.assertEqual(event_states["no_observation_conditioned_branching"], "Hypothesize")
        for profile in (
            "full",
            "no_recovery_revision_edge",
            "no_persistent_graph_state",
            "no_replanning",
        ):
            self.assertEqual(event_states[profile], "Monitor")
        self.assertEqual(post_event_states["full"], "Revise")
        for profile in (
            "no_recovery_revision_edge",
            "no_observation_conditioned_branching",
            "no_persistent_graph_state",
            "no_replanning",
        ):
            self.assertEqual(post_event_states[profile], "Hypothesize")

        errored = EpisodeTrajectory("online_replay_monitoring", "graph")
        errored.steps.append(
            _step(0, "data.read_window", "Inspect", error="recoverable")
        )
        no_edge = GraphPolicyConfig.for_profile(
            "no_recovery_revision_edge",
            runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
        )
        no_replanning = GraphPolicyConfig.for_profile(
            "no_replanning",
            runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
        )
        self.assertEqual(
            decision_state(errored, config=no_edge, previous_state="Inspect"),
            "Inspect",
        )
        self.assertEqual(
            decision_state(errored, config=no_replanning, previous_state="Inspect"),
            "Recover",
        )

    def test_no_persistent_outbound_history_has_no_prior_graph_state(self):
        trajectory = EpisodeTrajectory("online_replay_monitoring", "graph")
        event_observation = {
            "context": {
                "public_condition_event": {
                    "event": "operating_condition_change",
                    "event_id": "occ-00000001",
                    "release_index": 1,
                }
            }
        }
        trajectory.steps.append(
            _step(0, "data.read_window", "Monitor", observation=event_observation)
        )
        no_persistent = GraphDecisionAgent(
            client=None,
            policy_config=GraphPolicyConfig.for_profile(
                "no_persistent_graph_state",
                runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
            ),
        )
        no_persistent._active_state = "Analyze"
        messages = no_persistent.conversation(_task(event=False), trajectory)
        tool_payload = json.loads(
            next(
                str(message["content"])
                for message in messages
                if message.get("role") == "tool"
            )
        )
        self.assertNotIn("decision_state", tool_payload)
        self.assertEqual(
            sum(
                "Current decision state:" in str(message.get("content", ""))
                for message in messages
            ),
            1,
        )

        retained = GraphDecisionAgent(
            client=None,
            policy_config=GraphPolicyConfig.for_profile(
                "no_replanning",
                runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
            ),
        )
        retained_payload = json.loads(
            next(
                str(message["content"])
                for message in retained.conversation(_task(event=False), trajectory)
                if message.get("role") == "tool"
            )
        )
        self.assertEqual(retained_payload["decision_state"], "Monitor")

    def test_dynamic_runtime_rejects_fault_onset_and_uses_profile_legality(self):
        config = GraphPolicyConfig.for_profile(
            "full", runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT
        )
        with self.assertRaisesRegex(ValueError, "only operating_condition_change"):
            decision_state(
                EpisodeTrajectory("online_replay_monitoring", "graph"),
                config=config,
                previous_state="Inspect",
                observation_event="fault_onset",
            )
        self.assertEqual(
            transition_validity_from_states(["Inspect", "Monitor", "Revise"], config),
            1.0,
        )
        no_observation = GraphPolicyConfig.for_profile(
            "no_observation_conditioned_branching",
            runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
        )
        self.assertEqual(
            transition_validity_from_states(["Inspect", "Monitor"], no_observation),
            0.0,
        )

    def test_active_v6_defaults_retain_the_existing_semantics(self):
        config = GraphPolicyConfig()
        self.assertEqual(config.runtime_contract, PHASE1_BASE_RUNTIME_CONTRACT)
        self.assertEqual(legal_transitions(config), ALLOWED_TRANSITIONS)
        self.assertEqual(
            decision_state(
                EpisodeTrajectory("online_replay_monitoring", "graph"),
                config=config,
                previous_state="Inspect",
                observation_event="fault_onset",
            ),
            "Monitor",
        )
        self.assertEqual(
            config.to_dict(),
            {
                "recovery_revision_edge": True,
                "observation_conditioned_branching": True,
                "persistent_graph_state": True,
                "replanning": True,
            },
        )
        with self.assertRaisesRegex(ValueError, "unsupported Graph runtime contract"):
            GraphPolicyConfig(runtime_contract="unregistered-runtime")


if __name__ == "__main__":
    unittest.main()
