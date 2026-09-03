from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

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


ROOT = Path(__file__).resolve().parents[1]
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
) -> None:
    scope = protocol["scope"]
    profile = protocol["profile"]
    leaf = (
        run_dir
        / "episodes"
        / scope["rotation"]
        / sequence_id
        / scope["task_id"]
        / f"attempt_{attempt_index:03d}"
    )
    leaf.mkdir(parents=True)
    grounded = None if provider_failure else (0.0 if agent_failure else 1.0)
    failure_kind = (
        "provider_error"
        if provider_failure
        else ("agent_decision_error" if agent_failure else None)
    )
    terminal_status = "failed" if failure_kind is not None else "submitted"
    usage = {
        "input_tokens": 120 if arm == "graph" else 100,
        "output_tokens": 12 if arm == "graph" else 10,
        "llm_turns": 4,
        "tool_calls": 6,
    }
    shared = protocol["matched_contract"]["shared"]
    run = {
        "run_id": f"{repeat_id}-{arm}-{sequence_id}-{attempt_index}",
        "agent_id": profile["arms"][arm]["agent_id"],
        "budget": dict(profile["budget"]),
        "metadata": {
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
            "episode_key": [scope["rotation"], sequence_id, scope["task_id"]],
            "attempt_index": attempt_index,
        },
        "terminal_status": terminal_status,
        "failure_kind": failure_kind,
        "usage": usage,
    }
    metrics = {
        "task_id": scope["task_id"],
        "terminal_status": terminal_status,
        "task_metrics": {
            "completion_adjusted_average_precision": None,
            "average_precision": None,
            "auroc": None,
            "false_alarm_rate": None,
            "true_positive_rate": None,
        },
        "rollout_metrics": {
            "grounded_completion": grounded,
            "submission_rate": 0.0 if failure_kind is not None else 1.0,
            "grounded_recovery_success": None,
            "repeated_action_ratio": 0.0,
            "budget_exhaustion": 0.0,
            "steps": 6.0,
            "llm_turns": float(usage["llm_turns"]),
            "tool_calls": float(usage["tool_calls"]),
            "input_tokens": float(usage["input_tokens"]),
            "output_tokens": float(usage["output_tokens"]),
            "estimated_model_cost_usd": 0.0,
        },
    }
    decisions = [
        {
            "sample_id": f"{sequence_id}-window-{index}",
            "score": score,
            "predicted_class": "normal" if index == 0 else "anomaly",
        }
        for index, score in enumerate((0.1, 0.9, 0.8))
    ]
    effective_decisions = [] if failure_kind is not None else decisions
    rollout_rows = []
    if effective_decisions:
        rollout_rows.append(
            {
                "event_type": "action",
                "action": {"name": "submit"},
                "result": {
                    "status": "ok",
                    "output": {"accepted": True, "alarms": effective_decisions},
                },
            }
        )
    rollout_rows.append(
        {"event_type": "terminal", "terminal_status": terminal_status}
    )
    _json(leaf / "run.json", run)
    (leaf / "rollout.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rollout_rows),
        encoding="utf-8",
    )
    _json(
        leaf / "submission.json",
        {
            "status": terminal_status,
            "terminal_status": terminal_status,
            "payload": (
                {"accepted": True, "alarms": effective_decisions}
                if terminal_status == "submitted"
                else None
            ),
        },
    )
    _json(leaf / "metrics.json", metrics)
    (leaf / "failures.jsonl").write_text("", encoding="utf-8")
    _json(leaf / "artifacts.json", {"artifacts": []})


def _build_fixture(root: Path, *, unresolved_provider: bool = False) -> dict:
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
                )
    return protocol


class GraphReliabilityV2Tests(unittest.TestCase):
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
