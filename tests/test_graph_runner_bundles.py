from __future__ import annotations

import asyncio
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from phm_agent_benchmark import (
    Budget,
    EvaluatorResult,
    Rollout,
    RolloutEvent,
    TaskSpec,
)
from phm_agent_benchmark.phase1 import ModelProfile
from phm_agent_benchmark.phase1.resume import ResumeProfile
from phm_agent_benchmark.phase1.cohort import write_cohort_index
from phm_agent_benchmark.rollout_io import RUN_BUNDLE_FILES, read_run_bundle
from scripts import run_graph_experiment as RUNNER
from scripts.run_graph_experiment import (
    ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
    ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
    BENCHMARK_CONTROL_SOURCE_CONTRACT,
    BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    BENCHMARK_REPOSITORY,
    DATA_FACTORY_REPOSITORY,
    P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    P2_FORMAL_REPRODUCIBILITY_PATHS,
    P2_REPOSITORY,
    P2_EXPERIMENT_ID,
    P2_GRAPH_CONTROL_ID,
    P2_GRAPH_IMPLEMENTATION_ID,
    P2_MATCHED_CONTROL_ID,
    _active_cohort_contract,
    _benchmark_control_unit_topology,
    _episode_sink,
    _graph_policy_profile,
    _public_bundle_evaluation,
    _resume_context,
    _state_rows,
)


PROFILE = ResumeProfile(
    runtime_contract="runtime-v6",
    model="deterministic-mock-llm",
    provider="benchmark-local",
    inference_protocol="mock-tools",
)
INFERENCE = {
    "model": "deterministic-mock-llm",
    "provider": "benchmark-local",
    "inference_protocol": "mock-tools",
    "thinking_mode": "not_applicable",
}
FORMAL_INFERENCE = {
    "model": "cohere/north-mini-code:free",
    "provider": "openrouter-free",
    "inference_protocol": "openai_chat_completions",
    "thinking_mode": "not_requested",
}
BENCHMARK_FORMAL_EXECUTION_TOPOLOGY = {
    "contract": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    "benchmark_repository": BENCHMARK_REPOSITORY,
    "benchmark_revision": "a" * 40,
    "data_factory_repository": DATA_FACTORY_REPOSITORY,
    "data_factory_revision": "b" * 40,
    "data_factory_distribution_version": "0.2.1",
    "data_factory_lock_version": "0.2.1",
}
P2_FORMAL_EXECUTION_TOPOLOGY = {
    "contract": P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    "benchmark_formal_execution_topology": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY,
    "source_repositories": {
        "benchmark": BENCHMARK_REPOSITORY,
        "data_factory": DATA_FACTORY_REPOSITORY,
        "p2": P2_REPOSITORY,
    },
    "source_revisions": {
        "benchmark": "a" * 40,
        "data_factory": "b" * 40,
        "p2": "c" * 40,
    },
    "formal_sources_clean": {
        "benchmark": True,
        "data_factory": True,
        "p2": True,
    },
    "canonical_origins_verified": {
        "benchmark": True,
        "data_factory": True,
        "p2": True,
    },
    "p2_formal_reproducibility_paths": list(P2_FORMAL_REPRODUCIBILITY_PATHS),
}


def _task(task_id: str = "cold_start_fault_diagnosis") -> TaskSpec:
    return TaskSpec(
        task_id=task_id,
        task_type=task_id,
        instruction="Use the public tools and submit one result.",
        budget=Budget(),
    )


def _rollout(
    states: list[str],
    *,
    terminal_status: str,
) -> Rollout:
    rollout = Rollout("cold_start_fault_diagnosis", "graph-guided-phm-agent")
    for index, state in enumerate(states):
        submitted = terminal_status == "submitted" and index == len(states) - 1
        payload = {"label": "healthy", "supporting_refs": []}
        rollout.steps.append(
            RolloutEvent(
                index=index,
                observation_summary={"step": index},
                action="tool_call",
                tool_name=(
                    "submit"
                    if submitted
                    else "data.read_window"
                    if index == 0
                    else "op.list"
                ),
                tool_args=payload if submitted else {},
                tool_result=payload if submitted else {"ok": True},
                decision_state=state,
            )
        )
    if terminal_status == "submitted":
        rollout.submission = {"label": "healthy", "supporting_refs": []}
        rollout.terminal_status = "submitted"
    elif terminal_status == "provider_error":
        rollout.mark_failed("provider_error", "fixture provider interruption")
    else:
        rollout.terminal_status = terminal_status
    return rollout


def _evaluation(terminal_status: str) -> EvaluatorResult:
    return EvaluatorResult(
        task_id="cold_start_fault_diagnosis",
        task_metrics={
            "submission": float(terminal_status == "submitted"),
            "private_target": 1.0,
        },
        rollout_metrics={"steps": 2.0},
        terminal_status=terminal_status,
    )


def _args(output: Path, *, resume: bool = False) -> SimpleNamespace:
    return SimpleNamespace(
        arm="graph",
        runtime="mock",
        runtime_contract="runtime-v6",
        seed=20260808,
        output=output,
        resume_provider_partial=resume,
        graph_profile="full",
    )


def _formal_output(root: Path, stamp: str) -> Path:
    return (
        root
        / ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
        / "graph_core_primary"
        / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
        / f"run_{stamp}"
        / "seed_20260808"
        / "rotation_0"
    )


def _formal_args(
    output: Path,
    stamp: str,
    *,
    resume: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        arm="graph",
        runtime="openai",
        runtime_contract="phase1_opaque_sample_vibration_feature_schema_v6",
        seed=20260808,
        rotation="rotation_0",
        tasks=["cold_start_fault_diagnosis", "unsupervised_anomaly_detection"],
        train_samples_per_bearing=8,
        validation_samples_per_bearing=8,
        max_test_bearings=None,
        temperature=0.2,
        max_output_tokens_per_turn=2048,
        output=output,
        resume_provider_partial=resume,
        graph_profile="full",
        benchmark_formal_run_stamp=stamp,
        benchmark_control_protocol_id=ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
        benchmark_control_profile_id=ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
        benchmark_control_unit_root=None,
        protocol="/fixture/benchmark/dataset_protocol.yaml",
    )


def _formal_protocol() -> dict:
    return {
        "schema_version": "phm_agent_dataset_protocol_v1",
        "protocol_id": "paderborn_phase1_v1",
        "status": "active_phase1",
        "dataset": {
            "data_provider_contract": {
                "provider": "phm-data-factory",
                "package_version": "0.2.1",
                "api_schema_version": "1.0.0",
                "capability_schema_version": "1.0.0",
            }
        },
        "agent_visibility": {
            "sample_handle": {
                "scheme": "seeded_permutation_v1",
                "seed": 20260808,
                "purpose": "fixture",
            }
        },
        "window_protocol": {
            "contract": "phase1_single_vibration_full_rate_v3"
        },
        "episode_sampling": {
            "train_samples_per_bearing": 8,
            "healthy_validation_samples_per_bearing": 8,
            "agent_test_samples_per_bearing": 1,
            "monitoring_windows_per_episode": 3,
            "agent_selection": "metadata_order_floor_two_thirds",
            "numerical_selection": "evenly_spaced_over_metadata_order",
        },
    }


def _emit(
    sink,
    sample_id: str,
    states: list[str],
    terminal_status: str,
) -> None:
    key = ("rotation_0", sample_id, "cold_start_fault_diagnosis")
    sink(
        key,
        _task(),
        _rollout(states, terminal_status=terminal_status),
        _evaluation(terminal_status),
        {},
        {
            "rotation": key[0],
            "sample_id": key[1],
            "task_id": key[2],
            "episode_key": list(key),
            "selected_diagnosis_model_id": "logistic-regression",
            "started_at": "2026-08-13T00:00:00+00:00",
            "ended_at": "2026-08-13T00:00:01+00:00",
        },
    )


def _write_index(output: Path, rows: list[dict], *, status: str) -> None:
    write_cohort_index(
        output / "cohort_index.json",
        profile={},
        records=rows,
        status=status,
    )


class GraphRunnerBundleTest(unittest.TestCase):
    @staticmethod
    def _formal_contract(args: SimpleNamespace):
        with patch.object(
            RUNNER,
            "_formal_execution_topology",
            return_value=P2_FORMAL_EXECUTION_TOPOLOGY,
        ):
            return _active_cohort_contract(
                args,
                _formal_protocol(),
                FORMAL_INFERENCE,
                core_budget=Budget(),
                monitoring_budget=Budget(
                    max_tool_calls=72,
                    max_window_reads=3,
                    max_operator_calls=50,
                    max_model_calls=3,
                    max_llm_turns=72,
                ),
                test_samples_per_bearing=1,
                matches_formal_sampling=True,
                model_profile=None,
            )

    def test_formal_graph_output_is_isolated_by_benchmark_run_stamp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp_a = "20260901T010203Z"
            stamp_b = "20260902T010203Z"
            args_a = _formal_args(_formal_output(root, stamp_a), stamp_a)
            args_b = _formal_args(_formal_output(root, stamp_b), stamp_b)
            _manifest_a, identity_a, _profile_a = self._formal_contract(args_a)
            _manifest_b, identity_b, _profile_b = self._formal_contract(args_b)

            self.assertNotEqual(args_a.output, args_b.output)
            self.assertEqual(
                identity_a["benchmark_control_source"]["formal_run_stamp"],
                stamp_a,
            )
            self.assertEqual(
                identity_b["benchmark_control_source"]["formal_run_stamp"],
                stamp_b,
            )
            drifted = _formal_args(args_a.output, stamp_b)
            with self.assertRaisesRegex(ValueError, "different Benchmark run stamp"):
                self._formal_contract(drifted)

    def test_public_evaluation_preserves_identity_and_attaches_model_cost(self) -> None:
        private = EvaluatorResult(
            task_spec_id="online_replay_monitoring.v1",
            task_type="online_replay_monitoring",
            episode_id="episode-fixture-001",
            task_metrics={"average_precision": 0.75, "private_target": 1.0},
            rollout_metrics={"input_tokens": 100.0, "output_tokens": 20.0},
            terminal_status="submitted",
            evaluator_id="monitoring-v1",
            evaluator_method="target-adverse-average-precision",
        )
        profile = ModelProfile(
            "fixture-provider",
            "fixture-model",
            "openai_chat_completions",
            1.0,
            2.0,
        )

        public = _public_bundle_evaluation(private, profile)
        self.assertEqual(public.task_spec_id, private.task_spec_id)
        self.assertEqual(public.task_type, private.task_type)
        self.assertEqual(public.episode_id, private.episode_id)
        self.assertEqual(public.evaluator_id, private.evaluator_id)
        self.assertEqual(public.evaluator_method, private.evaluator_method)
        self.assertNotIn("private_target", public.task_metrics)
        self.assertAlmostEqual(
            public.rollout_metrics["estimated_model_cost_usd"],
            0.00014,
        )
        self.assertEqual(
            _public_bundle_evaluation(private, None).rollout_metrics[
                "estimated_model_cost_usd"
            ],
            0.0,
        )

    def test_formal_control_source_is_in_resume_identity_without_absolute_path(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp_a = "20260901T010203Z"
            stamp_b = "20260902T010203Z"
            args_a = _formal_args(_formal_output(root, stamp_a), stamp_a)
            protocol = _formal_protocol()
            _manifest_a, identity_a, profile_a = self._formal_contract(args_a)
            sink = _episode_sink(
                args_a,
                protocol,
                profile_a,
                FORMAL_INFERENCE,
                _resume_context(args_a, profile_a)[0],
                cohort_resume_identity=identity_a,
            )
            _emit(sink, "sample-a", ["Inspect", "Hypothesize"], "submitted")
            run_path = next(args_a.output.rglob("run.json"))
            run = json.loads(run_path.read_text(encoding="utf-8"))
            expected_source = {
                "contract": BENCHMARK_CONTROL_SOURCE_CONTRACT,
                "formal_run_stamp": stamp_a,
                "protocol_id": ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
                "profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
            }
            self.assertEqual(
                run["metadata"]["benchmark_control_source"], expected_source
            )
            self.assertEqual(
                run["metadata"]["cohort_resume_identity"][
                    "benchmark_control_source"
                ],
                expected_source,
            )
            self.assertEqual(
                run["metadata"]["formal_execution_topology"],
                P2_FORMAL_EXECUTION_TOPOLOGY,
            )
            self.assertEqual(
                run["metadata"]["cohort_resume_identity"][
                    "formal_execution_topology"
                ],
                P2_FORMAL_EXECUTION_TOPOLOGY,
            )
            self.assertNotIn(str(root), run_path.read_text(encoding="utf-8"))

            output_b = _formal_output(root, stamp_b)
            output_b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(args_a.output, output_b)
            args_b = _formal_args(output_b, stamp_b, resume=True)
            _manifest_b, _identity_b, profile_b = self._formal_contract(args_b)
            with self.assertRaisesRegex(ValueError, "cohort_identity"):
                _resume_context(args_b, profile_b)

    def test_completed_benchmark_unit_supplies_exact_formal_topology(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp = "20260901T010203Z"
            control = (
                root
                / ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
                / "b3_generic_core"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}"
                / "seed_20260808"
                / "rotation_0"
            )
            control.mkdir(parents=True)
            (control / "cohort_index.json").write_text("{}\n", encoding="utf-8")
            args = _formal_args(_formal_output(root, stamp), stamp)
            args.benchmark_control_unit_root = control
            profile = {
                "seed": args.seed,
                "rotation": args.rotation,
                "tasks": args.tasks,
                "agent_id": "generic-llm-tool-agent",
                "registered_evidence_class": "formal",
                "result_role": "confirmatory",
                "experiment_profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
                "formal_execution_topology": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY,
            }
            source = {
                "formal_run_stamp": stamp,
                "protocol_id": ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
                "profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
            }
            with patch.object(
                RUNNER,
                "validate_cohort_index",
                return_value={"status": "complete", "profile": profile},
            ):
                observed = _benchmark_control_unit_topology(args, source)
            self.assertEqual(observed, BENCHMARK_FORMAL_EXECUTION_TOPOLOGY)

            profile["formal_execution_topology"] = {
                **BENCHMARK_FORMAL_EXECUTION_TOPOLOGY,
                "benchmark_revision": "d" * 40,
            }
            with patch.object(
                RUNNER,
                "validate_cohort_index",
                return_value={"status": "complete", "profile": profile},
            ):
                self.assertEqual(
                    _benchmark_control_unit_topology(args, source)[
                        "benchmark_revision"
                    ],
                    "d" * 40,
                )

    def test_formal_topology_failure_precedes_provider_factory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp = "20260901T010203Z"
            output = _formal_output(root, stamp)
            args = RUNNER.build_parser().parse_args(
                [
                    "--arm",
                    "graph",
                    "--runtime",
                    "openai",
                    "--tasks",
                    "cold_start_fault_diagnosis",
                    "unsupervised_anomaly_detection",
                    "--benchmark-formal-run-stamp",
                    stamp,
                    "--benchmark-control-protocol-id",
                    ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
                    "--benchmark-control-profile-id",
                    ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
                    "--benchmark-control-unit-root",
                    str(root / "missing-control-unit"),
                    "--output",
                    str(output),
                ]
            )
            factory = Mock()
            with (
                patch.object(
                    RUNNER,
                    "load_dataset_protocol",
                    return_value=_formal_protocol(),
                ),
                patch.object(
                    RUNNER,
                    "_runtime_identity",
                    return_value=(FORMAL_INFERENCE, PROFILE, None),
                ),
                patch.object(
                    RUNNER,
                    "_formal_execution_topology",
                    side_effect=RuntimeError("formal topology rejected"),
                ),
                patch.object(RUNNER, "_factory", factory),
            ):
                with self.assertRaisesRegex(RuntimeError, "formal topology rejected"):
                    asyncio.run(RUNNER._run(args))
            factory.assert_not_called()
            self.assertFalse(output.exists())

    def test_sink_writes_six_file_attempts_without_root_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            sink = _episode_sink(
                _args(output),
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                _resume_context(_args(output), PROFILE)[0],
            )
            _emit(sink, "sample-a", ["Inspect", "Recover"], "provider_error")
            first_plan, _rows = _resume_context(_args(output, resume=True), PROFILE)
            sink = _episode_sink(
                _args(output, resume=True),
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                first_plan,
            )
            _emit(
                sink,
                "sample-a",
                ["Inspect", "Hypothesize", "Analyze"],
                "submitted",
            )

            leaves = sorted(output.rglob("run.json"))
            self.assertEqual(len(leaves), 2)
            self.assertFalse((output / "rollout.jsonl").exists())
            self.assertFalse((output / "provider_failures.jsonl").exists())
            self.assertFalse((output / "state_evaluation.jsonl").exists())
            for run_path in leaves:
                self.assertRegex(run_path.parent.name, r"^attempt_\d{3}$")
                self.assertEqual(
                    {item.name for item in run_path.parent.iterdir()},
                    set(RUN_BUNDLE_FILES),
                )
                bundle = read_run_bundle(run_path.parent)
                self.assertNotIn("private_target", bundle.metrics["task_metrics"])
                metadata = bundle.run["metadata"]
                self.assertEqual(metadata["p2_experiment_id"], P2_EXPERIMENT_ID)
                self.assertEqual(
                    metadata["matched_control_id"], P2_MATCHED_CONTROL_ID
                )
                self.assertEqual(metadata["agent_control_id"], P2_GRAPH_CONTROL_ID)
                self.assertEqual(
                    metadata["agent_implementation_id"],
                    P2_GRAPH_IMPLEMENTATION_ID,
                )

    def test_state_view_uses_effective_attempt_across_saved_bundles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            sink = _episode_sink(
                _args(output),
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                _resume_context(_args(output), PROFILE)[0],
            )
            _emit(sink, "sample-a", ["Inspect", "Hypothesize"], "submitted")
            _emit(sink, "sample-b", ["Inspect", "Recover"], "provider_error")
            _write_index(
                output,
                [
                    {
                        "rotation": "rotation_0",
                        "sample_id": "sample-a",
                        "task_id": "cold_start_fault_diagnosis",
                    }
                ],
                status="provider_failure_incomplete_cohort",
            )
            first_plan, _rows = _resume_context(_args(output, resume=True), PROFILE)
            sink = _episode_sink(
                _args(output, resume=True),
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                first_plan,
            )
            _emit(
                sink,
                "sample-b",
                ["Inspect", "Hypothesize", "Analyze"],
                "submitted",
            )

            rows = _state_rows(output)
            self.assertEqual([row["sample_id"] for row in rows], ["sample-a", "sample-b"])
            self.assertTrue(
                any(
                    path.parent.name == "attempt_001"
                    for path in output.rglob("run.json")
                )
            )
            self.assertEqual(
                rows[1]["states"], ["Inspect", "Hypothesize", "Analyze"]
            )
            self.assertEqual(rows[1]["transition_validity"], 1.0)
            self.assertNotIn("bearing_id", rows[0])
            self.assertNotIn("private_target", rows[0])

    def test_resume_loads_only_completed_private_evaluations(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            sink = _episode_sink(
                _args(output),
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                _resume_context(_args(output), PROFILE)[0],
            )
            _emit(sink, "sample-a", ["Inspect", "Hypothesize"], "submitted")
            _emit(sink, "sample-b", ["Inspect", "Recover"], "provider_error")
            _write_index(
                output,
                [
                    {
                        "rotation": "rotation_0",
                        "sample_id": "sample-a",
                        "task_id": "cold_start_fault_diagnosis",
                        "bearing_id": "bearing-a",
                        "private_target": "healthy",
                    }
                ],
                status="provider_failure_incomplete_cohort",
            )

            plan, rows = _resume_context(_args(output, resume=True), PROFILE)
            self.assertEqual(
                plan.completed_episode_keys,
                frozenset(
                    {
                        (
                            "rotation_0",
                            "sample-a",
                            "cold_start_fault_diagnosis",
                        )
                    }
                ),
            )
            self.assertEqual(
                plan.retry_episode_key,
                ("rotation_0", "sample-b", "cold_start_fault_diagnosis"),
            )
            self.assertEqual([row["sample_id"] for row in rows], ["sample-a"])

    def test_resume_rejects_a_different_graph_ablation_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            args = _args(output)
            sink = _episode_sink(
                args,
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                _resume_context(args, PROFILE)[0],
            )
            _emit(sink, "sample-a", ["Inspect", "Hypothesize"], "submitted")
            _write_index(
                output,
                [{"rotation": "rotation_0", "sample_id": "sample-a", "task_id": "cold_start_fault_diagnosis"}],
                status="complete",
            )
            changed = _args(output, resume=True)
            changed.graph_profile = "no_replanning"
            with self.assertRaisesRegex(ValueError, "profile mismatch"):
                _resume_context(changed, PROFILE)

    def test_resume_rejects_legacy_phmskills_derived_leaf_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            args = _args(output)
            sink = _episode_sink(
                args,
                {"schema_version": "phm_agent_dataset_protocol_v1"},
                PROFILE,
                INFERENCE,
                _resume_context(args, PROFILE)[0],
            )
            _emit(sink, "sample-a", ["Inspect", "Hypothesize"], "submitted")
            run_path = next(output.rglob("run.json"))
            run = json.loads(run_path.read_text(encoding="utf-8"))
            metadata = run["metadata"]
            metadata.pop("p2_experiment_id")
            metadata["matched_control_id"] = "phm-skills-agent-v0"
            metadata["agent_control_id"] = "phm-skills-plus-graph-v0"
            run_path.write_text(
                json.dumps(run, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            _write_index(
                output,
                [{"rotation": "rotation_0", "sample_id": "sample-a", "task_id": "cold_start_fault_diagnosis"}],
                status="complete",
            )
            with self.assertRaisesRegex(
                ValueError,
                "experiment/control identity mismatch",
            ):
                _resume_context(_args(output, resume=True), PROFILE)

    def test_reactive_arm_cannot_select_a_graph_ablation(self) -> None:
        args = _args(Path("unused"))
        args.arm = "reactive"
        args.graph_profile = "no_replanning"
        with self.assertRaisesRegex(ValueError, "only to --arm graph"):
            _graph_policy_profile(args)


if __name__ == "__main__":
    unittest.main()
