from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/audit_p2_e1_primary_readiness.py"
SPEC = importlib.util.spec_from_file_location("audit_p2_e1_primary_readiness", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class P2E1PrimaryReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.protocol = self.root / "dataset_protocol.yaml"
        self.protocol.write_text(
            yaml.safe_dump(
                {
                    "split": {
                        "folds": {"fold_0": ["B1"]},
                        "rotations": [
                            {
                                "run": "rotation_0",
                                "train": ["fold_0"],
                                "validation": "fold_0",
                                "test": "fold_0",
                            }
                        ],
                    },
                    "episode_sampling": {
                        "agent_test_samples_per_bearing": 1,
                        "monitoring_rotations": ["rotation_0"],
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.roots = {
            "reactive_core": self.root / "phm_skills_primary",
            "graph_core": self.root / "graph_core_primary",
            "reactive_replay": self.root / "reactive_monitor_primary",
            "graph_replay": self.root / "graph_monitor_primary",
        }
        self.acceptance_paths = {
            key: self.root / f"{key}_cohort_acceptance.json"
            for key in self.roots
        }

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    @staticmethod
    def _manifest(arm: str, tasks: tuple[str, ...], graph: bool) -> dict:
        value = {
            "arm": arm,
            "budget": {"max_llm_turns": 3, "max_tool_calls": 3},
            "max_output_tokens_per_turn": 128,
            "model_profile": {
                "provider": "free-provider",
                "model_id": "free-model",
                "protocol": "openai_chat_completions",
                "input_usd_per_million": 0.0,
                "output_usd_per_million": 0.0,
            },
            "protocol": "fixture-protocol",
            "replay_windows_per_episode": 3 if tasks == MODULE.REPLAY_TASKS else None,
            "rotation": "rotation_0",
            "runtime": "openai",
            "runtime_contract": "fixture-v6",
            "sample_handle": {"scheme": "opaque"},
            "seed": 1,
            "selected_diagnosis_model_id": "fixture-model",
            "tasks": list(tasks),
            "temperature": 0.2,
            "test_sample_selection": "registered",
            "test_samples_per_bearing": 1,
            "train_samples_per_bearing": 1,
            "validation_model_macro_f1": {"fixture-model": 0.5},
            "validation_samples_per_bearing": 1,
            "window_protocol": {"contract": "fixture-window"},
        }
        if graph:
            value["graph_policy_profile"] = "full"
        return value

    def _write_unit(self, root: Path, arm: str, tasks: tuple[str, ...], graph: bool) -> Path:
        unit = root / "seed_1/rotation_0"
        unit.mkdir(parents=True, exist_ok=True)
        (unit / "run_manifest.json").write_text(
            json.dumps(self._manifest(arm, tasks, graph)), encoding="utf-8"
        )
        return unit

    def _write_attempt(
        self,
        unit: Path,
        *,
        arm: str,
        graph: bool,
        task: str,
        attempt_index: int = 0,
        provider_error: bool = False,
    ) -> None:
        leaf = (
            unit
            / "episodes/rotation_0/sample-000001"
            / task
            / f"attempt-{attempt_index:03d}"
        )
        leaf.mkdir(parents=True, exist_ok=True)
        run = {
            "agent_id": "graph-agent" if graph else "reactive-agent",
            "budget": {"max_llm_turns": 3, "max_tool_calls": 3},
            "failure_kind": "provider_error" if provider_error else None,
            "metadata": {
                "arm": arm,
                "attempt_index": attempt_index,
                "dataset_protocol": "fixture-protocol",
                "episode_key": ["rotation_0", "sample-000001", task],
                "graph_policy_profile": "full" if graph else None,
                "inference_protocol": "openai_chat_completions",
                "model": "free-model",
                "provider": "free-provider",
                "rotation": "rotation_0",
                "runtime_contract": "fixture-v6",
                "sample_id": "sample-000001",
                "seed": 1,
                "selected_diagnosis_model_id": "fixture-model",
                "task_id": task,
                "thinking_mode": "not_requested",
            },
            "task": {
                "allowed_actions": ["data.read_window", "submit"],
                "budget": {"max_llm_turns": 3, "max_tool_calls": 3},
                "evaluator_id": "fixture-evaluator",
                "instruction": "fixture",
                "public_context": {"sample_id": "sample-000001"},
                "task_id": task,
                "task_type": task,
            },
            "terminal_status": "failed" if provider_error else "submitted",
        }
        action = {
            "event_type": "action",
            "action": {
                "name": "data.read_window",
                "arguments": {"sample_id": "sample-000001"},
                "decision_state": "Inspect" if graph else None,
            },
        }
        (leaf / "run.json").write_text(json.dumps(run), encoding="utf-8")
        (leaf / "rollout.jsonl").write_text(json.dumps(action) + "\n", encoding="utf-8")
        (leaf / "submission.json").write_text("{}\n", encoding="utf-8")
        (leaf / "metrics.json").write_text("{}\n", encoding="utf-8")
        (leaf / "failures.jsonl").write_text("", encoding="utf-8")
        (leaf / "artifacts.json").write_text("{}\n", encoding="utf-8")

    def _populate_arm(self, key: str, tasks: tuple[str, ...]) -> None:
        arm = {
            "reactive_core": "phm-skills",
            "graph_core": "graph",
            "reactive_replay": "reactive",
            "graph_replay": "graph",
        }[key]
        graph = key.startswith("graph")
        unit = self._write_unit(self.roots[key], arm, tasks, graph)
        for task in tasks:
            self._write_attempt(unit, arm=arm, graph=graph, task=task)

    def _accept_all(self) -> None:
        for key, path in self.acceptance_paths.items():
            core = key.endswith("core")
            expected_episodes = 2 if core else 1
            document = {
                "accepted": True,
                "contract": {"shared": "fixture-contract"},
                "errors": [],
                "expected_episodes": expected_episodes,
                "expected_runs": 1,
                "expected_runtime_contract": "fixture-v6",
                "inference_contract_required": True,
                "mode": "core" if core else "monitoring",
                "observed_runs": 1,
                "observed_unique_episodes": expected_episodes,
                "rotations": ["rotation_0"],
                "run_contracts": {"1:rotation_0": {}},
                "seeds": [1],
                "state_evaluation_required": key.startswith("graph"),
                "tasks": list(MODULE.CORE_TASKS if core else MODULE.REPLAY_TASKS),
            }
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

    def _build(self, **overrides):
        kwargs = {
            "protocol_path": self.protocol,
            "reactive_core_root": self.roots["reactive_core"],
            "graph_core_root": self.roots["graph_core"],
            "reactive_replay_root": self.roots["reactive_replay"],
            "graph_replay_root": self.roots["graph_replay"],
            "acceptance_paths": self.acceptance_paths,
            "registered_seeds": (1,),
            "expected_runtime_contract": "fixture-v6",
        }
        kwargs.update(overrides)
        return MODULE.build_report(**kwargs)

    def test_complete_matched_fixture_requires_and_accepts_all_four_gates(self) -> None:
        self._populate_arm("reactive_core", MODULE.CORE_TASKS)
        self._populate_arm("graph_core", MODULE.CORE_TASKS)
        self._populate_arm("reactive_replay", MODULE.REPLAY_TASKS)
        self._populate_arm("graph_replay", MODULE.REPLAY_TASKS)

        before = self._build()
        self.assertFalse(before["accepted"])
        self.assertFalse(before["checks"]["formal_p2_e1_result_eligible"])

        self._accept_all()
        after = self._build()
        self.assertTrue(after["accepted"])
        self.assertEqual(after["status"], "accepted_complete_cohort")
        self.assertNotIn("estimate", after)

    def test_partial_prefix_is_inventory_not_a_result(self) -> None:
        self._populate_arm("reactive_core", MODULE.CORE_TASKS)
        self._populate_arm("graph_core", MODULE.CORE_TASKS)
        self._accept_all()

        report = self._build()

        self.assertFalse(report["accepted"])
        self.assertEqual(report["counts"]["matched_statistical_keys"]["core"], 2)
        self.assertEqual(report["counts"]["matched_statistical_keys"]["replay"], 0)
        self.assertFalse(report["partial_prefix_policy"]["aggregate_performance"])
        self.assertFalse(report["partial_prefix_policy"]["emit_effect_estimate"])

    def test_generic_root_cannot_substitute_for_reactive_control(self) -> None:
        generic = self.root / "generic_primary"
        generic.mkdir()
        with self.assertRaisesRegex(MODULE.ReadinessError, "cannot use a Generic root"):
            self._build(reactive_core_root=generic)

    def test_multiple_statistical_attempts_fail_closed(self) -> None:
        self._populate_arm("reactive_core", MODULE.CORE_TASKS)
        unit = self.roots["reactive_core"] / "seed_1/rotation_0"
        self._write_attempt(
            unit,
            arm="phm-skills",
            graph=False,
            task=MODULE.CORE_TASKS[0],
            attempt_index=1,
        )
        with self.assertRaisesRegex(MODULE.ReadinessError, "multiple statistical attempts"):
            self._build()

    def test_provider_error_retry_is_retained_but_not_double_counted(self) -> None:
        for key, tasks in (
            ("reactive_core", MODULE.CORE_TASKS),
            ("graph_core", MODULE.CORE_TASKS),
            ("reactive_replay", MODULE.REPLAY_TASKS),
            ("graph_replay", MODULE.REPLAY_TASKS),
        ):
            self._populate_arm(key, tasks)
        unit = self.roots["reactive_core"] / "seed_1/rotation_0"
        first = (
            unit
            / "episodes/rotation_0/sample-000001"
            / MODULE.CORE_TASKS[0]
            / "attempt-000"
        )
        for child in first.iterdir():
            child.unlink()
        first.rmdir()
        self._write_attempt(
            unit,
            arm="phm-skills",
            graph=False,
            task=MODULE.CORE_TASKS[0],
            attempt_index=0,
            provider_error=True,
        )
        self._write_attempt(
            unit,
            arm="phm-skills",
            graph=False,
            task=MODULE.CORE_TASKS[0],
            attempt_index=1,
        )
        self._accept_all()

        report = self._build()

        counts = report["counts"]["reactive_core"]
        self.assertEqual(counts["attempt_leaves"], 3)
        self.assertEqual(counts["provider_error_attempts"], 1)
        self.assertEqual(counts["statistical_outcomes"], 2)
        self.assertTrue(report["accepted"])

    def test_provider_error_with_wrong_profile_fails_closed(self) -> None:
        unit = self._write_unit(
            self.roots["reactive_core"], "phm-skills", MODULE.CORE_TASKS, False
        )
        self._write_attempt(
            unit,
            arm="phm-skills",
            graph=False,
            task=MODULE.CORE_TASKS[0],
            provider_error=True,
        )
        run_path = (
            unit
            / "episodes/rotation_0/sample-000001"
            / MODULE.CORE_TASKS[0]
            / "attempt-000/run.json"
        )
        run = json.loads(run_path.read_text(encoding="utf-8"))
        run["metadata"]["model"] = "different-model"
        run_path.write_text(json.dumps(run), encoding="utf-8")

        with self.assertRaisesRegex(MODULE.ReadinessError, "model mismatch"):
            self._build()


class CurrentArtifactTests(unittest.TestCase):
    def test_checked_in_artifact_matches_fresh_provider_free_audit(self) -> None:
        output = MODULE.DEFAULT_OUTPUT
        self.assertTrue(output.is_file())
        stored = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(stored, MODULE.build_report())
        self.assertFalse(stored["accepted"])
        self.assertEqual(stored["provider_calls"], 0)
        self.assertEqual(stored["counts"]["matched_statistical_keys"]["core"], 32)
        self.assertEqual(stored["counts"]["matched_statistical_keys"]["replay"], 0)


if __name__ == "__main__":
    unittest.main()
