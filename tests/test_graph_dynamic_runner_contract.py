from __future__ import annotations

import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from phm_agent_benchmark import Budget, EvaluatorResult, Rollout, RolloutEvent, TaskSpec
from phm_agent_benchmark.phase1.resume import ProviderResumePlan, ResumeProfile
from phm_graph_agent import GRAPH_DYNAMIC_RUNTIME_CONTRACT
from scripts.run_graph_experiment import (
    P2_EXPERIMENT_ID,
    P2_GRAPH_CONTROL_ID,
    P2_GRAPH_IMPLEMENTATION_ID,
    P2_MATCHED_CONTROL_ID,
    _dynamic_agent_profile,
    _load_dynamic_protocol,
    _validate_dynamic_arguments,
    _write_dynamic_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"


def _args(output: Path) -> SimpleNamespace:
    return SimpleNamespace(
        arm="graph",
        runtime="mock",
        graph_profile="full",
        runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
        dynamic_protocol=PROTOCOL_PATH,
        public_sequence_id="sequence-0001",
        horizon=6,
        tasks=["online_replay_monitoring"],
        seed=20260808,
        rotation="rotation_0",
        output=output,
    )


class GraphDynamicRunnerContractTest(unittest.TestCase):
    def test_explicit_dynamic_flags_are_required_as_one_contract(self):
        protocol = _load_dynamic_protocol(PROTOCOL_PATH)
        args = _args(Path("unused"))
        _validate_dynamic_arguments(args, protocol)

        missing = _args(Path("unused"))
        missing.public_sequence_id = None
        with self.assertRaisesRegex(ValueError, "public-sequence-id"):
            _validate_dynamic_arguments(missing, protocol)

        active = _args(Path("unused"))
        active.runtime_contract = "phase1_opaque_sample_vibration_feature_schema_v6"
        active.dynamic_protocol = None
        active.public_sequence_id = None
        active.horizon = None
        active.tasks = ["cold_start_fault_diagnosis"]
        _validate_dynamic_arguments(active, None)

        unknown = _args(Path("unused"))
        unknown.runtime_contract = "unregistered-runtime"
        unknown.dynamic_protocol = None
        unknown.public_sequence_id = None
        unknown.horizon = None
        with self.assertRaisesRegex(ValueError, "unsupported runtime contract"):
            _validate_dynamic_arguments(unknown, None)

    def test_one_dynamic_unit_routes_one_attempt_leaf_to_canonical_writer(self):
        output = Path("formal-root/episodes/sequence-0001")
        args = _args(output)
        task = TaskSpec(
            task_id="online_replay_monitoring",
            task_type="online_replay_monitoring",
            instruction="Use bounded released samples.",
            budget=Budget(
                max_tool_calls=144,
                max_window_reads=6,
                max_operator_calls=100,
                max_model_calls=6,
                max_llm_turns=144,
                max_data_points=49152,
                max_data_bytes=393216,
            ),
        )
        rollout = Rollout(task.task_id, "graph-guided-phm-agent")
        rollout.steps.append(
            RolloutEvent(
                index=0,
                observation_summary={
                    "context": {
                        "replay_sample_ids": ["sample-a"],
                        "replay_cursor": 0,
                    }
                },
                action="tool_call",
                tool_name="data.read_window",
                tool_args={"sample_id": "sample-a"},
                tool_result={"artifact_ref": "artifact://window/000001"},
                decision_state="Inspect",
            )
        )
        rollout.terminal_status = "provider_error"
        evaluation = EvaluatorResult(
            task_id=task.task_id,
            task_metrics={"submission": 0.0},
            rollout_metrics={"steps": 1.0},
            terminal_status="provider_error",
        )
        result = SimpleNamespace(
            task_spec=task,
            trajectory=rollout,
            evaluation=evaluation,
            artifact_descriptors={},
        )
        profile = ResumeProfile(
            runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
            model="deterministic-mock-llm",
            provider="benchmark-local",
            inference_protocol="mock-tools",
        )
        with patch("scripts.run_graph_experiment.write_run_bundle") as writer:
            attempt = _write_dynamic_bundle(
                args,
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                profile,
                {
                    "model": "deterministic-mock-llm",
                    "provider": "benchmark-local",
                    "inference_protocol": "mock-tools",
                    "thinking_mode": "not_applicable",
                },
                ProviderResumePlan(frozenset()),
                result,
                None,
                "ridge-ovr-v1",
                "2026-08-20T00:00:00+00:00",
                "2026-08-20T00:00:01+00:00",
            )
        self.assertEqual(attempt, output / "attempt_000")
        writer.assert_called_once()
        self.assertEqual(writer.call_args.args[0], output / "attempt_000")
        metadata = writer.call_args.kwargs["run_metadata"]
        self.assertEqual(metadata["runtime_contract"], GRAPH_DYNAMIC_RUNTIME_CONTRACT)
        self.assertEqual(metadata["horizon"], 6)
        self.assertEqual(metadata["public_sequence_id"], "sequence-0001")
        self.assertEqual(
            metadata["agent_profile_id"], "graph_dynamic_full_generic_v2"
        )
        self.assertEqual(metadata["p2_experiment_id"], P2_EXPERIMENT_ID)
        self.assertEqual(metadata["matched_control_id"], P2_MATCHED_CONTROL_ID)
        self.assertEqual(metadata["agent_control_id"], P2_GRAPH_CONTROL_ID)
        self.assertEqual(
            metadata["agent_implementation_id"], P2_GRAPH_IMPLEMENTATION_ID
        )
        self.assertNotIn("bearing_id", metadata)
        self.assertEqual(
            _dynamic_agent_profile(args), "graph_dynamic_full_generic_v2"
        )


if __name__ == "__main__":
    unittest.main()
