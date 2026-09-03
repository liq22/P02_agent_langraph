from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.analyze_p2_e0_adapter_equivalence import GateError, analyze_gate


BUDGET = {
    "max_data_bytes": None,
    "max_data_points": None,
    "max_llm_turns": 33,
    "max_model_calls": 2,
    "max_operator_calls": 17,
    "max_tool_calls": 33,
    "max_wall_clock_seconds": None,
    "max_window_reads": 3,
}
MODEL_PROFILE = {
    "provider": "openrouter-free",
    "model_id": "cohere/north-mini-code:free",
    "protocol": "openai_chat_completions",
    "input_usd_per_million": 0.0,
    "output_usd_per_million": 0.0,
}
WINDOW = {
    "contract": "phase1_single_vibration_full_rate_v3",
    "channel_indices": [2],
    "channel_semantics": "bearing_housing_acceleration",
    "start_point": 0,
    "end_point": 8192,
    "max_returned_points": 8192,
    "bounded_read": True,
    "sampling_mode": "full_rate_no_decimation",
}
ACTIONS = [
    "data.search",
    "data.describe",
    "data.read_window",
    "data.summarize",
    "op.list",
    "op.schema",
    "op.run",
    "model.list",
    "model.schema",
    "model.predict",
    "artifact.describe",
    "submit",
    "stop",
]


class P2E0AdapterEquivalenceTest(unittest.TestCase):
    def _fixture(self, root: Path) -> tuple[Path, Path, Path]:
        generic = root / "benchmark/generic"
        graph = root / "p02/graph"
        protocol_path = root / "dataset_protocol.yaml"
        protocol = {
            "schema_version": "phm_agent_dataset_protocol_v1",
            "agent_visibility": {"sample_handle": {"scheme": "seeded_permutation_v1", "seed": 20260808, "purpose": "opaque"}},
            "split": {
                "folds": {"fold_0": [f"B{i}" for i in range(8)], "fold_1": ["V"]},
                "rotations": [{"run": "rotation_0", "train": ["fold_1"], "validation": "fold_1", "test": "fold_0"}],
            },
            "window_protocol": WINDOW,
            "episode_sampling": {
                "train_samples_per_bearing": 8,
                "healthy_validation_samples_per_bearing": 8,
                "agent_test_samples_per_bearing": 1,
                "agent_selection": "metadata_order_floor_two_thirds",
            },
            "inference": {"temperature": 0.2, "max_output_tokens_per_turn": 2048, "model_profile": MODEL_PROFILE},
            "budgets": {"core": {key: value for key, value in BUDGET.items() if value is not None}},
        }
        protocol_path.write_text(yaml.safe_dump(protocol), encoding="utf-8")
        base_manifest = {
            "budget": {key: value for key, value in BUDGET.items() if value is not None},
            "max_output_tokens_per_turn": 2048,
            "model_profile": MODEL_PROFILE,
            "protocol": "phm_agent_dataset_protocol_v1",
            "rotation": "rotation_0",
            "runtime_contract": "phase1_opaque_sample_vibration_feature_schema_v6",
            "sample_handle": protocol["agent_visibility"]["sample_handle"],
            "seed": 20260808,
            "selected_diagnosis_model_id": "ridge-ovr-v1",
            "temperature": 0.2,
            "test_sample_selection": "metadata_order_floor_two_thirds",
            "test_samples_per_bearing": 1,
            "train_samples_per_bearing": 8,
            "validation_model_macro_f1": {"nearest-centroid-v1": 0.3, "ridge-ovr-v1": 0.6},
            "validation_samples_per_bearing": 8,
            "window_protocol": WINDOW,
        }
        for arm_root, arm in ((generic, "generic"), (graph, "graph")):
            arm_root.mkdir(parents=True)
            manifest = dict(base_manifest)
            if arm == "graph":
                manifest.update({"arm": "graph", "graph_policy_profile": "full"})
            (arm_root / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            for sample_index in range(8):
                for task_id in ("cold_start_fault_diagnosis", "unsupervised_anomaly_detection"):
                    terminal = "submitted"
                    failure = None
                    if sample_index == 0 and task_id == "cold_start_fault_diagnosis":
                        if arm == "generic":
                            terminal, failure = "budget_exhausted", "budget_exhausted"
                        else:
                            terminal, failure = "failed", "agent_decision_error"
                    self._write_leaf(arm_root, arm, f"sample-{sample_index:06d}", task_id, terminal, failure)
        return generic, graph, protocol_path

    def _write_leaf(self, root: Path, arm: str, sample_id: str, task_id: str, terminal: str, failure: str | None) -> None:
        leaf = root / "episodes/rotation_0" / sample_id / task_id / "attempt-000"
        leaf.mkdir(parents=True)
        task = {
            "task_id": task_id,
            "task_type": task_id,
            "instruction": "public task",
            "allowed_actions": ACTIONS,
            "budget": BUDGET,
            "evaluator_id": "diagnosis-v0" if task_id.startswith("cold") else "anomaly-v0",
            "public_context": {"sample_id": sample_id, "channels": [2]},
            "submission_schema": {"type": "object"},
            "primary_metrics": ["macro_f1"],
            "protocol_version": "0.1.0",
        }
        metadata = {
            "attempt_index": 0,
            "dataset_protocol": "phm_agent_dataset_protocol_v1",
            "episode_key": ["rotation_0", sample_id, task_id],
            "inference_protocol": MODEL_PROFILE["protocol"],
            "model": MODEL_PROFILE["model_id"],
            "provider": MODEL_PROFILE["provider"],
            "selected_diagnosis_model_id": "ridge-ovr-v1",
        }
        if arm == "graph":
            metadata.update({"arm": "graph", "graph_policy_profile": "full"})
        run = {"agent_id": arm, "budget": BUDGET, "failure_kind": failure, "metadata": metadata, "task": task, "terminal_status": terminal}
        action = {"name": "data.read_window", "arguments": {}, "decision_state": "Inspect" if arm == "graph" else None}
        files = {
            "run.json": json.dumps(run),
            "submission.json": json.dumps({"failure_kind": failure, "payload": {} if terminal == "submitted" else None}),
            "metrics.json": json.dumps({"evaluator_id": "phase1", "terminal_status": terminal}),
            "artifacts.json": "{}",
            "rollout.jsonl": json.dumps({"event_type": "action", "action": action, "observation": {"sample_id": sample_id}}) + "\n",
            "failures.jsonl": "" if failure is None else json.dumps({"kind": failure}) + "\n",
        }
        for filename, content in files.items():
            (leaf / filename).write_text(content, encoding="utf-8")

    def test_accepts_world_equivalence_and_retains_natural_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            generic, graph, protocol = self._fixture(Path(temporary))
            report = analyze_gate(generic, graph, protocol)
            self.assertTrue(report["accepted"])
            self.assertEqual(report["counts"]["matched_statistical_episode_keys"], 16)
            self.assertEqual(report["counts"]["generic"]["non_submitted_statistical_outcomes_retained"], 1)
            self.assertEqual(report["counts"]["graph"]["agent_decision_error_outcomes_retained"], 1)
            self.assertEqual(report["intervention_boundary"]["treatment_only_tools"], [])

    def test_rejects_private_bearing_in_public_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            generic, graph, protocol = self._fixture(Path(temporary))
            rollout = next(graph.glob("episodes/*/*/*/attempt-000/rollout.jsonl"))
            rollout.write_text(json.dumps({"observation": {"bearing_id": "B0"}}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(GateError, "private field"):
                analyze_gate(generic, graph, protocol)

    def test_rejects_graph_action_without_decision_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            generic, graph, protocol = self._fixture(Path(temporary))
            rollout = next(graph.glob("episodes/*/*/*/attempt-000/rollout.jsonl"))
            row = json.loads(rollout.read_text(encoding="utf-8"))
            row["action"]["decision_state"] = None
            rollout.write_text(json.dumps(row) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(GateError, "decision_state"):
                analyze_gate(generic, graph, protocol)


if __name__ == "__main__":
    unittest.main()
