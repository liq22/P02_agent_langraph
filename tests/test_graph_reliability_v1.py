from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_SRC = ROOT.parent / "p01-phm-agent-benchmark" / "src"
if BENCHMARK_SRC.is_dir() and str(BENCHMARK_SRC) not in sys.path:
    sys.path.insert(0, str(BENCHMARK_SRC))

from phm_agent_benchmark.phase1 import (
    Budget,
    DataAccessScope,
    EvaluatorResult,
    Rollout,
    RolloutEvent,
    TaskInstance,
)
from phm_agent_benchmark.phase1.active_path import evaluate_phase1_episode
from phm_agent_benchmark.phase1.policy_adapter import phase1_task_spec
from phm_agent_benchmark.rollout_io import read_run_bundle, write_run_bundle

from scripts.analyze_graph_reliability import (
    GraphReliabilityContractError,
    analyze_graph_reliability,
    load_graph_reliability_protocol,
    validate_graph_reliability_acceptance,
    validate_graph_reliability_protocol,
)
from scripts.schedule_graph_reliability import (
    accept_graph_reliability_cohort,
    build_graph_reliability_schedule,
    graph_reliability_runner_readiness,
)
from scripts.run_graph_reliability_v2 import (
    GraphReliabilityRunnerError,
    _exclusive_profile_lock,
    _stamp_attempts,
    _write_json as _write_runner_json,
)


PROTOCOL_PATH = ROOT / "paper/experiments/graph_reliability_protocol_v2.yaml"
LEGACY_PROTOCOL_PATH = ROOT / "paper/experiments/graph_reliability_protocol_v1.yaml"


def _fixture_protocol() -> dict:
    protocol = copy.deepcopy(load_graph_reliability_protocol(PROTOCOL_PATH))
    protocol["statistics"]["bootstrap"]["iterations"] = 60
    protocol["statistics"]["bootstrap"]["seed"] = 17
    return validate_graph_reliability_protocol(protocol)


def _json(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _private_assignments(protocol: dict) -> dict[str, dict]:
    return {
        sequence_id: {
            "sample_ids": [f"{sequence_id}-window-{index}" for index in range(3)],
            "private_target": {
                f"{sequence_id}-window-0": 0,
                f"{sequence_id}-window-1": 1,
                f"{sequence_id}-window-2": 1,
            },
        }
        for sequence_id in protocol["scope"]["public_sequence_ids"]
    }


def _selected_success_leaf(root: Path, protocol: dict) -> Path:
    return (
        root
        / protocol["profile"]["reliability_profile_id"]
        / protocol["cohort"]["repeats"][0]["repeat_id"]
        / "graph"
        / protocol["scope"]["rotation"]
        / "episodes"
        / protocol["scope"]["rotation"]
        / protocol["scope"]["public_sequence_ids"][0]
        / protocol["scope"]["task_id"]
        / "attempt_000"
    )


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _write_attempt(
    run_dir: Path,
    protocol: dict,
    *,
    repeat_id: str,
    seed: int,
    arm: str,
    sequence_id: str,
    attempt_index: int,
    provider_failure: bool = False,
    agent_failure: bool = False,
    submitted_window_count: int = 3,
) -> None:
    scope = protocol["scope"]
    profile = protocol["profile"]
    sample_ids = [f"{sequence_id}-window-{index}" for index in range(3)]
    targets = {
        sample_ids[0]: 0,
        sample_ids[1]: 1,
        sample_ids[2]: 1,
    }
    leaf = (
        run_dir
        / "episodes"
        / scope["rotation"]
        / sequence_id
        / scope["task_id"]
        / f"attempt_{attempt_index:03d}"
    )
    leaf.parent.mkdir(parents=True, exist_ok=True)
    failure_kind = (
        "provider_error"
        if provider_failure
        else ("agent_decision_error" if agent_failure else None)
    )
    terminal_status = "failed" if failure_kind is not None else "submitted"
    instance = TaskInstance(
        task_id=scope["task_id"],
        sample_id=sequence_id,
        private_target=targets,
        public_context={
            "replay_sample_ids": sample_ids,
            "window_start": 0,
            "window_end": 8192,
            "channels": [2],
            "max_points": 8192,
        },
    )
    task = phase1_task_spec(instance, Budget(**profile["budget"]))
    episode_id = task.task_spec_id
    decisions = [
        {
            "sample_id": sample_id,
            "score": score,
            "predicted_class": "normal" if index == 0 else "anomaly",
            "supporting_refs": [f"prediction-{sequence_id}-{index}"],
        }
        for index, (sample_id, score) in enumerate(
            zip(sample_ids, (0.1, 0.9, 0.8), strict=True)
        )
    ]
    active_decisions = decisions[:submitted_window_count]
    input_tokens = 120 if arm == "graph" else 100
    output_tokens = 12 if arm == "graph" else 10
    steps: list[RolloutEvent] = []
    if failure_kind is None:
        for index, decision in enumerate(active_decisions):
            observation = {
                "task_id": scope["task_id"],
                "sample_id": sample_ids[index],
                "task_spec_id": task.task_spec_id,
                "task_type": scope["task_id"],
                "episode_id": episode_id,
                "context": {
                    "replay_sample_ids": sample_ids[: index + 1],
                    "replay_cursor": index,
                },
            }
            prediction_ref = decision["supporting_refs"][0]
            steps.append(
                RolloutEvent(
                    index=len(steps),
                    observation_summary=observation,
                    action="tool_call",
                    tool_name="model.predict",
                    tool_args={"sample_id": sample_ids[index]},
                    tool_result={
                        "prediction_ref": prediction_ref,
                        "required_supporting_refs": [prediction_ref],
                        "source_sample_id": sample_ids[index],
                        "anomaly_score": decision["score"],
                        "predicted_class": decision["predicted_class"],
                    },
                    usage_delta={
                        "tool_calls": 1,
                        "model_calls": 1,
                        "llm_turns": 1,
                        "input_tokens": input_tokens if index == 0 else 0,
                        "output_tokens": output_tokens if index == 0 else 0,
                        "agent_inference_seconds": 0.0,
                        "tool_execution_seconds": 0.0,
                    },
                )
            )
            prefix = copy.deepcopy(active_decisions[: index + 1])
            stream_end = index == len(active_decisions) - 1
            submit_output = {
                "accepted": True,
                "decisions": prefix,
                "stream_end": stream_end,
                "released_sample_id": None if stream_end else sample_ids[index + 1],
            }
            steps.append(
                RolloutEvent(
                    index=len(steps),
                    observation_summary=observation,
                    action="tool_call",
                    tool_name="submit",
                    tool_args={"decision": copy.deepcopy(decision)},
                    tool_result=submit_output,
                    usage_delta={
                        "tool_calls": 1,
                        "llm_turns": 1,
                        "input_tokens": 0,
                        "output_tokens": 0,
                        "agent_inference_seconds": 0.0,
                        "tool_execution_seconds": 0.0,
                    },
                )
            )
    usage = {
        "tool_calls": len(steps),
        "window_reads": 0,
        "data_points_read": 0,
        "data_bytes_read": 0,
        "operator_calls": 0,
        "model_calls": len(active_decisions) if steps else 0,
        "llm_turns": len(steps),
        "input_tokens": input_tokens if steps else 0,
        "output_tokens": output_tokens if steps else 0,
        "agent_inference_seconds": 0.0,
        "tool_execution_seconds": 0.0,
        "wall_clock_seconds": 0.0,
    }
    failures = (
        []
        if failure_kind is None
        else [
            {
                "step": None,
                "tool_name": None,
                "kind": failure_kind,
                "error": "fixture terminal failure",
            }
        ]
    )
    submission = None if failure_kind is not None else dict(steps[-1].tool_result)
    rollout = Rollout(
        task_spec_id=task.task_spec_id,
        task_type=task.task_type,
        episode_id=episode_id,
        agent_id=profile["arms"][arm]["agent_id"],
        steps=steps,
        failures=failures,
        usage=usage,
        submission=submission,
        terminal_status=terminal_status,
        terminal_failure_kind=failure_kind,
        terminal_message=(None if failure_kind is None else "fixture terminal failure"),
        runtime_contract=profile["effective_runtime_contract"],
    )
    evaluator_instance = TaskInstance(
        episode_id=episode_id,
        task_spec_id=task.task_spec_id,
        task_type=task.task_type,
        sample_handle=sequence_id,
        private_target=targets,
        public_context=dict(task.public_context),
        scope=DataAccessScope(replay_handles=tuple(sample_ids)),
    )
    evaluated = evaluate_phase1_episode(
        task=task,
        instance=evaluator_instance,
        rollout=rollout,
    )
    evaluated_rollout = dict(evaluated.rollout_metrics)
    evaluated_rollout["estimated_model_cost_usd"] = 0.0
    evaluation = EvaluatorResult(
        task_spec_id=evaluated.task_spec_id,
        task_type=evaluated.task_type,
        episode_id=evaluated.episode_id,
        task_metrics=evaluated.task_metrics,
        rollout_metrics=evaluated_rollout,
        terminal_status=evaluated.terminal_status,
        evaluator_id=evaluated.evaluator_id,
        evaluator_method=evaluated.evaluator_method,
    )
    shared = protocol["matched_contract"]["shared"]
    write_run_bundle(
        leaf,
        run_id=f"{repeat_id}-{arm}-{sequence_id}-{attempt_index}",
        task=task,
        rollout=rollout,
        evaluation=evaluation,
        artifacts={},
        run_metadata={
            "reliability_profile_id": profile["reliability_profile_id"],
            "reliability_execution_contract": protocol["execution"][
                "dedicated_runner_contract"
            ],
            "dataset_protocol": shared["dataset_protocol_schema"],
            "dataset_protocol_id": shared["dataset_protocol_id"],
            "dataset_protocol_schema": shared["dataset_protocol_schema"],
            "dataset_id": shared["dataset_id"],
            "evaluator_assignment_contract": shared[
                "evaluator_assignment_contract"
            ],
            "runtime_contract": profile["effective_runtime_contract"],
            "dynamic_protocol_id": protocol["execution"]["dynamic_protocol_id"],
            "model": profile["model"],
            "provider": profile["provider"],
            "inference_protocol": profile["inference_protocol"],
            "thinking_mode": profile["thinking_mode"],
            "seed": seed,
            "repeat_id": repeat_id,
            "rotation": scope["rotation"],
            "horizon": scope["windows_per_episode"],
            "arm": arm,
            "graph_policy_profile": profile["arms"][arm]["graph_policy_profile"],
            "agent_control_id": profile["arms"][arm]["agent_control_id"],
            "agent_implementation_id": profile["arms"][arm][
                "agent_implementation_id"
            ],
            "p2_experiment_id": profile["p2_experiment_id"],
            "matched_control_id": profile["matched_control_id"],
            "task_id": scope["task_id"],
            "temperature": profile["temperature"],
            "max_output_tokens_per_turn": profile["max_output_tokens_per_turn"],
            "input_usd_per_million": float(profile["input_usd_per_million"]),
            "output_usd_per_million": float(profile["output_usd_per_million"]),
            "public_sequence_id": sequence_id,
            "sample_id": sequence_id,
            "episode_key": [scope["rotation"], sequence_id, scope["task_id"]],
            "attempt_index": attempt_index,
            "started_at": "2026-09-03T00:00:00+00:00",
            "ended_at": "2026-09-03T00:00:01+00:00",
        },
    )


def _build_fixture(
    root: Path,
    *,
    unresolved_provider: bool = False,
    truncated_submission: bool = False,
) -> dict:
    protocol = _fixture_protocol()
    profile = protocol["profile"]
    scope = protocol["scope"]
    for repeat_index, repeat in enumerate(protocol["cohort"]["repeats"]):
        repeat_id = repeat["repeat_id"]
        seed = repeat["seed"]
        for arm in scope["arms"]:
            run_dir = (
                root
                / profile["reliability_profile_id"]
                / repeat_id
                / arm
                / scope["rotation"]
            )
            run_dir.mkdir(parents=True)
            model_profile = {
                "provider": profile["provider"],
                "model_id": profile["model"],
                "protocol": profile["inference_protocol"],
                "input_usd_per_million": float(profile["input_usd_per_million"]),
                "output_usd_per_million": float(profile["output_usd_per_million"]),
            }
            shared = protocol["matched_contract"]["shared"]
            manifest = {
                "reliability_profile_id": profile["reliability_profile_id"],
                "reliability_execution_contract": protocol["execution"][
                    "dedicated_runner_contract"
                ],
                "protocol": shared["dataset_protocol_schema"],
                "dataset_protocol_id": shared["dataset_protocol_id"],
                "dataset_protocol_schema": shared["dataset_protocol_schema"],
                "dataset_id": shared["dataset_id"],
                "evaluator_assignment_contract": shared[
                    "evaluator_assignment_contract"
                ],
                "runtime_contract": profile["effective_runtime_contract"],
                "dynamic_protocol_id": protocol["execution"][
                    "dynamic_protocol_id"
                ],
                "seed": seed,
                "repeat_id": repeat_id,
                "rotation": scope["rotation"],
                "horizon": scope["windows_per_episode"],
                "arm": arm,
                "agent_id": profile["arms"][arm]["agent_id"],
                "agent_control_id": profile["arms"][arm]["agent_control_id"],
                "agent_implementation_id": profile["arms"][arm][
                    "agent_implementation_id"
                ],
                "p2_experiment_id": profile["p2_experiment_id"],
                "matched_control_id": profile["matched_control_id"],
                "graph_policy_profile": profile["arms"][arm][
                    "graph_policy_profile"
                ],
                "tasks": [scope["task_id"]],
                "temperature": profile["temperature"],
                "max_output_tokens_per_turn": profile[
                    "max_output_tokens_per_turn"
                ],
                "input_usd_per_million": float(
                    profile["input_usd_per_million"]
                ),
                "output_usd_per_million": float(
                    profile["output_usd_per_million"]
                ),
                "model_profile": model_profile,
                "budget": profile["budget"],
                "evidence_class": scope["evidence_class"],
            }
            _json(run_dir / "run_manifest.json", manifest)
            for sequence_index, sequence_id in enumerate(
                scope["public_sequence_ids"]
            ):
                unresolved = (
                    unresolved_provider
                    and repeat_index == 0
                    and arm == "graph"
                    and sequence_index == 0
                )
                if unresolved:
                    _write_attempt(
                        run_dir,
                        protocol,
                        repeat_id=repeat_id,
                        seed=seed,
                        arm=arm,
                        sequence_id=sequence_id,
                        attempt_index=0,
                        provider_failure=True,
                    )
                    continue
                resolved_provider_retry = (
                    repeat_index == 0
                    and arm == "reactive"
                    and sequence_index == 0
                )
                if resolved_provider_retry:
                    _write_attempt(
                        run_dir,
                        protocol,
                        repeat_id=repeat_id,
                        seed=seed,
                        arm=arm,
                        sequence_id=sequence_id,
                        attempt_index=0,
                        provider_failure=True,
                    )
                agent_failure = (
                    repeat_index == 9 and arm == "graph" and sequence_index == 0
                )
                _write_attempt(
                    run_dir,
                    protocol,
                    repeat_id=repeat_id,
                    seed=seed,
                    arm=arm,
                    sequence_id=sequence_id,
                    attempt_index=1 if resolved_provider_retry else 0,
                    agent_failure=agent_failure,
                    submitted_window_count=(
                        1
                        if truncated_submission
                        and repeat_index == 0
                        and arm == "graph"
                        and sequence_index == 0
                        else 3
                    ),
                )
    return protocol


class GraphReliabilityV2Tests(unittest.TestCase):
    def test_runner_profile_lock_and_unique_temporary_write_are_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            lock = root / "profile/.provider.lock"
            with _exclusive_profile_lock(lock):
                with self.assertRaisesRegex(
                    GraphReliabilityRunnerError, "holds the profile lock"
                ):
                    with _exclusive_profile_lock(lock):
                        pass

            fixed_temporary = root / "run.json.tmp"
            fixed_temporary.write_text("unrelated writer\n", encoding="utf-8")
            output = root / "run.json"
            _write_runner_json(output, {"status": "complete"})
            self.assertEqual(
                json.loads(output.read_text(encoding="utf-8")),
                {"status": "complete"},
            )
            self.assertEqual(
                fixed_temporary.read_text(encoding="utf-8"), "unrelated writer\n"
            )

    def test_runner_does_not_rewrite_stamped_attempts_and_rejects_partial_stamp(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _fixture_protocol()
            profile = protocol["profile"]
            scope = protocol["scope"]
            repeat = protocol["cohort"]["repeats"][0]
            arm = "reactive"
            sequence_id = scope["public_sequence_ids"][0]
            run_directory = (
                root
                / profile["reliability_profile_id"]
                / repeat["repeat_id"]
                / arm
                / scope["rotation"]
            )
            _write_attempt(
                run_directory,
                protocol,
                repeat_id=repeat["repeat_id"],
                seed=repeat["seed"],
                arm=arm,
                sequence_id=sequence_id,
                attempt_index=0,
            )
            episode_root = (
                run_directory
                / "episodes"
                / scope["rotation"]
                / sequence_id
                / scope["task_id"]
            )
            contract = {
                "episode_root": str(episode_root),
                "run_directory": str(run_directory),
                "reliability_profile_id": profile["reliability_profile_id"],
                "seed": repeat["seed"],
                "repeat_id": repeat["repeat_id"],
                "arm": arm,
                "agent_id": profile["arms"][arm]["agent_id"],
                "agent_control_id": profile["arms"][arm]["agent_control_id"],
                "agent_implementation_id": profile["arms"][arm][
                    "agent_implementation_id"
                ],
                "graph_policy_profile": profile["arms"][arm][
                    "graph_policy_profile"
                ],
                "rotation": scope["rotation"],
                "horizon": scope["windows_per_episode"],
                "public_sequence_id": sequence_id,
                "task_id": scope["task_id"],
            }
            run_path = episode_root / "attempt_000/run.json"
            before = run_path.read_bytes()
            _stamp_attempts(contract, protocol)
            self.assertEqual(run_path.read_bytes(), before)

            run = json.loads(run_path.read_text(encoding="utf-8"))
            del run["metadata"]["repeat_id"]
            _json(run_path, run)
            with self.assertRaisesRegex(
                GraphReliabilityRunnerError, "partial reliability provenance stamp"
            ):
                _stamp_attempts(contract, protocol)

    def test_v1_is_superseded_and_rejected(self) -> None:
        legacy = yaml.safe_load(LEGACY_PROTOCOL_PATH.read_text(encoding="utf-8"))
        self.assertEqual(legacy["status"], "superseded_phmskills_base")
        self.assertEqual(legacy["formal_launch"], "forbidden")
        with self.assertRaisesRegex(
            GraphReliabilityContractError, "unsupported reliability protocol schema"
        ):
            validate_graph_reliability_protocol(legacy)

    def test_protocol_freezes_disjoint_n10_matched_replay_and_isolated_roots(self) -> None:
        protocol = load_graph_reliability_protocol(PROTOCOL_PATH)
        repeats = protocol["cohort"]["repeats"]
        seeds = {item["seed"] for item in repeats}
        self.assertEqual(len(repeats), 10)
        self.assertEqual(len(seeds), 10)
        self.assertFalse(seeds & set(protocol["cohort"]["primary_cohort_seeds"]))
        self.assertEqual(protocol["scope"]["arms"], ["reactive", "graph"])
        self.assertEqual(len(protocol["scope"]["public_sequence_ids"]), 8)
        self.assertEqual(protocol["scope"]["expected_pairs_total"], 80)
        self.assertEqual(protocol["scope"]["expected_episode_bundles_total"], 160)
        self.assertEqual(protocol["metrics"]["primary"], "task.average_precision")
        self.assertEqual(
            protocol["metrics"]["primary_contract"]["missing_score_policy_id"],
            "phase1_replay_target_adverse_missing_score_v1",
        )
        self.assertTrue(
            protocol["profile"]["separate_from_active_v6_primary_profile"]
        )
        self.assertEqual(
            protocol["profile"]["arms"]["reactive"]["agent_id"],
            "reactive-sequential-agent",
        )
        self.assertEqual(
            protocol["profile"]["arms"]["graph"]["agent_id"],
            "graph-decision-agent",
        )
        self.assertEqual(
            protocol["profile"]["p2_experiment_id"],
            "p2_graph_vs_generic_llm_v1",
        )
        self.assertEqual(
            protocol["profile"]["matched_control_id"],
            "benchmark_generic_llm_tool_agent_v1",
        )
        self.assertNotEqual(
            protocol["profile"]["base_runtime_contract"],
            protocol["profile"]["effective_runtime_contract"],
        )
        forbidden = " ".join(protocol["execution"]["forbidden_primary_roots"])
        self.assertIn("graph_monitor_primary", forbidden)
        self.assertEqual(
            protocol["execution"]["formal_parent_root"],
            "paper/experiments/runs/formal/graph_reliability_v2",
        )
        self.assertEqual(
            protocol["execution"]["formal_root"],
            "paper/experiments/runs/formal/graph_reliability_v2/"
            "graph_reliability_generic_n10_v2",
        )
        self.assertEqual(
            protocol["execution"]["results_root"],
            "paper/experiments/results/graph_reliability_v2/"
            "graph_reliability_generic_n10_v2",
        )

    def test_dry_schedule_is_deterministic_counterbalanced_and_provider_free(self) -> None:
        protocol = _fixture_protocol()
        first = build_graph_reliability_schedule(protocol, "/tmp/p2-e9")
        second = build_graph_reliability_schedule(protocol, "/tmp/p2-e9")
        self.assertEqual(first, second)
        self.assertEqual(first["run_assignment_count"], 20)
        self.assertEqual(first["paired_unit_count"], 80)
        self.assertEqual(first["episode_assignment_count"], 160)
        self.assertFalse(first["provider_calls_performed"])
        self.assertFalse(first["provider_execution_authorized_by_schedule"])
        self.assertTrue(first["runner_readiness"]["ready"])
        self.assertEqual(first["runner_readiness"]["blocked_reasons"], [])
        self.assertEqual(first["runner_commands_emitted"], 160)
        self.assertEqual(len(first["runner_commands"]), 160)
        first_positions = [item["arm_order"][0] for item in first["paired_units"]]
        self.assertEqual(first_positions.count("reactive"), 40)
        self.assertEqual(first_positions.count("graph"), 40)
        self.assertEqual(
            {tuple(item["arm_order"]) for item in first["paired_units"]},
            {("reactive", "graph"), ("graph", "reactive")},
        )
        readiness = graph_reliability_runner_readiness(protocol)
        self.assertTrue(readiness["ready"])
        self.assertEqual(readiness["missing_runner_flags"], [])
        self.assertEqual(readiness["missing_runner_identity_literals"], [])

        argv = first["runner_commands"][0]["argv"]
        for flag in (
            "--reliability-protocol",
            "--reliability-profile-id",
            "--repeat-id",
            "--dynamic-protocol",
            "--public-sequence-id",
            "--horizon",
            "--input-usd-per-million",
            "--output-usd-per-million",
            "--output-root",
        ):
            self.assertIn(flag, argv)
        self.assertEqual(argv[argv.index("--horizon") + 1], "3")
        self.assertEqual(argv[argv.index("--input-usd-per-million") + 1], "0.0")
        self.assertEqual(argv[argv.index("--output-usd-per-million") + 1], "0.0")
        self.assertEqual(
            argv[argv.index("--reliability-profile-id") + 1],
            "graph_reliability_generic_n10_v2",
        )
        self.assertEqual(
            argv[argv.index("--dynamic-protocol") + 1],
            "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml",
        )
        validation = subprocess.run(
            [sys.executable, *argv[1:], "--validate-only"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(validation.returncode, 0, validation.stderr)
        validated = json.loads(validation.stdout)
        self.assertFalse(validated["provider_calls_performed"])
        self.assertFalse(validated["filesystem_writes_performed"])
        self.assertEqual(validated["seed"], 20260828)
        self.assertEqual(
            validated["run_directory"],
            "/tmp/p2-e9/graph_reliability_generic_n10_v2/"
            "graph_reliability_repeat_01/reactive/rotation_0",
        )

    def test_complete_canonical_cohort_retains_failure_and_reports_reliability(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            result = analyze_graph_reliability(
                root,
                protocol,
                acceptance,
                private_replay_assignments=_private_assignments(protocol),
            )

        inclusion = result["canonical_inclusion"]
        self.assertEqual(inclusion["canonical_non_provider_terminal_count"], 160)
        self.assertEqual(inclusion["matched_pair_count"], 80)
        self.assertEqual(inclusion["retained_provider_failure_attempt_count"], 1)
        self.assertEqual(inclusion["non_provider_failures_retained"], 1)
        reactive = result["arms"]["reactive"]
        graph = result["arms"]["graph"]
        self.assertEqual(
            (reactive["reliability"]["pass_at_1"]["numerator"],
             reactive["reliability"]["pass_at_1"]["denominator"]),
            (80, 80),
        )
        self.assertEqual(
            (graph["reliability"]["pass_at_1"]["numerator"],
             graph["reliability"]["pass_at_1"]["denominator"]),
            (79, 80),
        )
        self.assertEqual(
            (graph["reliability"]["pass_all_10"]["numerator"],
             graph["reliability"]["pass_all_10"]["denominator"]),
            (7, 8),
        )
        self.assertEqual(graph["failure_kind_counts"], {"agent_decision_error": 1})
        reliability = graph["metrics"]["rollout.grounded_completion"]
        self.assertAlmostEqual(
            reliability["mean_across_registered_repeats"], 0.9875
        )
        self.assertGreater(reliability["between_repeat_variance"], 0.0)
        self.assertEqual(reliability["bootstrap_valid_replicates"], 60)
        self.assertEqual(
            result["paired_graph_minus_reactive"]["pass_at_1_delta"]["estimate"],
            -0.0125,
        )
        self.assertEqual(
            graph["cost"]["rollout.estimated_model_cost_usd"][
                "assigned_episode_denominator"
            ],
            80,
        )
        self.assertEqual(
            graph["cost"]["rollout.estimated_model_cost_usd"][
                "defined_episode_numerator"
            ],
            80,
        )
        self.assertEqual(
            graph["cost"]["rollout.estimated_model_cost_usd"][
                "mean_across_registered_repeats"
            ],
            0.0,
        )
        self.assertEqual(
            graph["cost"]["rollout.total_tokens"][
                "assigned_episode_denominator"
            ],
            80,
        )
        primary = graph["metrics"]["task.average_precision"]
        failed_repeat_ap = ((7 / 8) * 7 + (14 / 15) * 7) / 16
        expected_graph_ap = (9.0 + failed_repeat_ap) / 10
        self.assertEqual(primary["status"], "defined")
        self.assertAlmostEqual(
            reactive["metrics"]["task.average_precision"][
                "mean_across_registered_repeats"
            ],
            1.0,
        )
        self.assertAlmostEqual(
            primary["mean_across_registered_repeats"], expected_graph_ap
        )
        self.assertEqual(primary["assigned_window_denominator_per_arm"], 240)
        self.assertEqual(primary["submitted_window_numerator"], 237)
        self.assertEqual(primary["missing_assigned_scores"], 3)
        self.assertFalse(
            primary["per_sequence_average_precision_averaging_performed"]
        )
        paired_primary = result["paired_graph_minus_reactive"][
            "primary_task_outcome"
        ]
        self.assertAlmostEqual(
            paired_primary["estimate"], expected_graph_ap - 1.0
        )
        self.assertEqual(result["primary_endpoint"]["metric"], "task.average_precision")
        self.assertFalse(result["primary_endpoint"]["derived_evaluation_jsonl_ingested"])
        self.assertFalse(primary["missing_values_imputed_as_zero"])
        self.assertFalse(result["cohort"]["primary_results_ingested"])

    def test_derived_evaluation_rows_are_ignored_and_private_assignments_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            assignments = _private_assignments(protocol)
            baseline = analyze_graph_reliability(
                root,
                protocol,
                acceptance,
                private_replay_assignments=assignments,
            )
            derived = next(root.rglob("online_replay_monitoring")) / "evaluation.jsonl"
            derived.write_text(
                json.dumps(
                    {
                        "private_target": {"tampered": 1},
                        "evaluation": {"task_metrics": {"average_precision": 0.0}},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            observed = analyze_graph_reliability(
                root,
                protocol,
                acceptance,
                private_replay_assignments=assignments,
            )
            self.assertEqual(
                observed["paired_graph_minus_reactive"]["primary_task_outcome"],
                baseline["paired_graph_minus_reactive"]["primary_task_outcome"],
            )

            malformed = copy.deepcopy(assignments)
            first = protocol["scope"]["public_sequence_ids"][0]
            first_sample = malformed[first]["sample_ids"][0]
            malformed[first]["private_target"][first_sample] = 2
            with self.assertRaisesRegex(
                GraphReliabilityContractError, "not binary"
            ):
                analyze_graph_reliability(
                    root,
                    protocol,
                    acceptance,
                    private_replay_assignments=malformed,
                )

    def test_canonical_gate_rejects_exact_six_identity_submission_failure_and_usage_tamper(
        self,
    ) -> None:
        for tamper in ("exact_six", "identity", "submission", "failure", "usage"):
            with self.subTest(tamper=tamper), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                protocol = _build_fixture(root)
                leaf = _selected_success_leaf(root, protocol)
                if tamper == "exact_six":
                    (leaf / "unexpected.txt").write_text("extra\n", encoding="utf-8")
                elif tamper == "identity":
                    rows = _read_jsonl(leaf / "rollout.jsonl")
                    rows[0]["agent_id"] = "tampered-agent"
                    _write_jsonl(leaf / "rollout.jsonl", rows)
                elif tamper == "submission":
                    submission = json.loads(
                        (leaf / "submission.json").read_text(encoding="utf-8")
                    )
                    submission["payload"]["decisions"][0]["score"] = 0.25
                    _json(leaf / "submission.json", submission)
                elif tamper == "failure":
                    _write_jsonl(
                        leaf / "failures.jsonl",
                        [
                            {
                                "step": None,
                                "tool_name": None,
                                "kind": "tool_error",
                                "error": "fabricated failure",
                            }
                        ],
                    )
                else:
                    run = json.loads((leaf / "run.json").read_text(encoding="utf-8"))
                    run["usage"]["tool_calls"] += 1
                    _json(leaf / "run.json", run)

                report = accept_graph_reliability_cohort(root, protocol)
                self.assertFalse(report["accepted"])
                self.assertTrue(report["errors"])

    def test_analyzer_rejects_metrics_tamper_after_canonical_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root)
            leaf = _selected_success_leaf(root, protocol)
            metrics = json.loads((leaf / "metrics.json").read_text(encoding="utf-8"))
            metrics["task_metrics"]["average_precision"] = 0.125
            _json(leaf / "metrics.json", metrics)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            with self.assertRaisesRegex(
                GraphReliabilityContractError,
                "metrics differ from the independent evaluator",
            ):
                analyze_graph_reliability(
                    root,
                    protocol,
                    acceptance,
                    private_replay_assignments=_private_assignments(protocol),
                )

    def test_analyzer_rejects_coherent_unassigned_prefix_and_incomplete_submission(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root)
            leaf = _selected_success_leaf(root, protocol)
            assigned = _private_assignments(protocol)
            sequence_id = protocol["scope"]["public_sequence_ids"][0]
            old_sample = assigned[sequence_id]["sample_ids"][0]
            new_sample = "unregistered-window"

            def replace(value):
                if isinstance(value, dict):
                    return {key: replace(child) for key, child in value.items()}
                if isinstance(value, list):
                    return [replace(child) for child in value]
                return new_sample if value == old_sample else value

            rows = replace(_read_jsonl(leaf / "rollout.jsonl"))
            submission = replace(
                json.loads((leaf / "submission.json").read_text(encoding="utf-8"))
            )
            _write_jsonl(leaf / "rollout.jsonl", rows)
            _json(leaf / "submission.json", submission)
            read_run_bundle(leaf)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            with self.assertRaisesRegex(
                GraphReliabilityContractError,
                "registered assigned-window prefix",
            ):
                analyze_graph_reliability(
                    root,
                    protocol,
                    acceptance,
                    private_replay_assignments=assigned,
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root, truncated_submission=True)
            acceptance = accept_graph_reliability_cohort(root, protocol)
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            with self.assertRaisesRegex(
                GraphReliabilityContractError,
                "submit cursor differs from the registered assignment",
            ):
                analyze_graph_reliability(
                    root,
                    protocol,
                    acceptance,
                    private_replay_assignments=_private_assignments(protocol),
                )

    def test_unresolved_provider_attempt_and_empty_root_fail_closed(self) -> None:
        protocol = _fixture_protocol()
        with tempfile.TemporaryDirectory() as temporary:
            empty_report = accept_graph_reliability_cohort(temporary, protocol)
        self.assertFalse(empty_report["accepted"])
        self.assertIn("missing registered run directory", empty_report["errors"][0])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            protocol = _build_fixture(root, unresolved_provider=True)
            report = accept_graph_reliability_cohort(root, protocol)
        self.assertFalse(report["accepted"])
        self.assertIn("0 non-provider terminals", report["errors"][0])

    def test_analyzer_rejects_unaccepted_or_primary_overlapping_inputs(self) -> None:
        protocol = _fixture_protocol()
        unaccepted = {
            "schema_version": "graph_reliability_acceptance_v2",
            "accepted": False,
        }
        with self.assertRaisesRegex(
            GraphReliabilityContractError, "acceptance report drift"
        ):
            validate_graph_reliability_acceptance(protocol, unaccepted)

        overlapping = copy.deepcopy(protocol)
        overlapping["cohort"]["primary_cohort_seeds"] = [
            overlapping["cohort"]["repeats"][0]["seed"]
        ]
        with self.assertRaisesRegex(GraphReliabilityContractError, "overlap"):
            validate_graph_reliability_protocol(overlapping)


if __name__ == "__main__":
    unittest.main()
