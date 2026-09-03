from __future__ import annotations

import copy
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import yaml

from scripts.analyze_graph_dynamic_formal import (
    ACCEPTANCE_SCHEMA,
    Cell,
    GraphDynamicFormalError,
    Unit,
    _bootstrap_interval,
    _holm,
    _private_assignment_for_unit,
    _profile_semantics,
    _replay_task_summary,
    _recompute_evaluator_metrics,
    _validate_attempt_prefixes,
    _validate_private_dynamic_assignments,
    _validate_terminal_failure_pair,
    accept_formal_cohort,
    analyze_formal_cohort,
    build_private_dynamic_assignments,
    build_public_event_catalog,
    expected_units,
    load_protocol,
    unit_root,
    validate_acceptance,
    _expected_base_state,
)
from scripts.render_graph_dynamic_manuscript import (
    MANUSCRIPT_BEGIN,
    MANUSCRIPT_END,
    write_dynamic_manuscript,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
DATASET_PROTOCOL_PATH = (
    ROOT.parent
    / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
)


def _json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _jsonl(path: Path, values: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(value, sort_keys=True) + "\n" for value in values),
        encoding="utf-8",
    )


def _master(sequence_id: str, horizon: int) -> list[str]:
    sequence = int(sequence_id.removeprefix("sequence-"))
    return [f"sample-{sequence:04d}-{index:02d}" for index in range(horizon)]


def _private_assignments(protocol: dict) -> dict[str, dict]:
    assignments: dict[str, dict] = {}
    for sequence in range(1, protocol["dataset"]["held_out_bearings"] + 1):
        sequence_id = f"sequence-{sequence:04d}"
        sample_ids = _master(
            sequence_id, protocol["sequence_construction"]["master_horizon"]
        )
        target = (sequence - 1) % 2
        assignments[sequence_id] = {
            "sample_ids": sample_ids,
            "private_target": {sample_id: target for sample_id in sample_ids},
        }
    return assignments


def _event_id(protocol: dict, *, seed: int, sequence_id: str, release: int) -> str:
    seed_index = protocol["experiment_design"]["seeds"].index(seed)
    sequence_index = int(sequence_id.removeprefix("sequence-")) - 1
    release_index = [3, 6, 9].index(release)
    ordinal = (seed_index * 8 + sequence_index) * 3 + release_index + 1
    return f"occ-{ordinal:08d}"


def _state(profile: str | None, release: int) -> str | None:
    if profile is None:
        return None
    if release in {3, 6, 9}:
        if profile == "no_observation_conditioned_branching":
            return "Inspect"
        return "Monitor"
    if release - 1 in {3, 6, 9} and profile == "full":
        return "Revise"
    return "Inspect"


def _metrics(
    *,
    terminal_status: str,
    grounded: float,
    usage: dict,
    action_count: int,
    target_value: int,
    predictions: list[str],
) -> dict:
    anomaly_rate = (
        sum(value == "anomaly" for value in predictions) / len(predictions)
        if predictions
        else 0.0
    )
    task_metrics = {
        "average_precision": (
            1.0 if grounded == 1.0 and target_value == 1 else None
        ),
        "auroc": None,
        "false_alarm_rate": (
            anomaly_rate if grounded == 1.0 and target_value == 0 else None
        ),
        "true_positive_rate": (
            anomaly_rate if grounded == 1.0 and target_value == 1 else None
        ),
        "grounded_submission": grounded,
        "submission": grounded,
    }
    rollout_metrics = {
        "grounded_completion": grounded,
        "grounded_recovery_success": 0.0,
        "valid_tool_call_rate": 1.0 if action_count else 0.0,
        "repeated_action_ratio": 0.0,
        "budget_exhaustion": float(terminal_status == "budget_exhausted"),
        "steps_to_next_success_after_failure": None,
        "steps": float(action_count),
        "llm_turns": float(usage["llm_turns"]),
        "input_tokens": float(usage["input_tokens"]),
        "output_tokens": float(usage["output_tokens"]),
        "wall_clock_seconds": float(usage["wall_clock_seconds"]),
        "estimated_model_cost_usd": 0.0,
    }
    return {
        "evaluator_id": "phase1",
        "evaluator_method": "deterministic",
        "task_id": "online_replay_monitoring",
        "task_metrics": task_metrics,
        "rollout_metrics": rollout_metrics,
        "terminal_status": terminal_status,
    }


def _write_attempt(
    directory: Path,
    protocol: dict,
    unit,
    *,
    attempt_index: int,
    provider_failure: bool = False,
    agent_failure: bool = False,
) -> tuple[dict, dict | None]:
    leaf = directory / f"attempt_{attempt_index:03d}"
    leaf.mkdir(parents=True, exist_ok=True)
    samples = _master(unit.public_sequence_id, unit.cell.horizon)
    target_value = (
        int(unit.public_sequence_id.removeprefix("sequence-")) - 1
    ) % 2
    terminal_status = "failed" if provider_failure or agent_failure else "submitted"
    failure_kind = (
        "provider_error"
        if provider_failure
        else "agent_decision_error"
        if agent_failure
        else None
    )
    grounded = float(terminal_status == "submitted")
    budget = protocol["budgets"]["by_horizon"][unit.cell.horizon]
    agent_id = (
        "reactive-sequential-agent"
        if unit.cell.arm == "reactive"
        else "graph-decision-agent"
    )
    run_id = f"fixture-{unit.cell.agent_profile_id}-{attempt_index}"
    metadata = {
        "agent_profile_id": unit.cell.agent_profile_id,
        "arm": unit.cell.arm,
        "attempt_index": attempt_index,
        "dataset_protocol": protocol["dataset"]["dataset_protocol_schema"],
        "ended_at": "2026-08-20T00:00:01+00:00",
        "episode_key": [unit.rotation, unit.public_sequence_id, "online_replay_monitoring"],
        "evidence_class": (
            "real_data_provider_failure_not_performance_evidence"
            if provider_failure
            else "real_data_formal_candidate"
        ),
        "graph_policy_profile": (
            "reactive" if unit.cell.graph_profile is None else unit.cell.graph_profile
        ),
        "horizon": unit.cell.horizon,
        "inference_protocol": "openai_chat_completions",
        "model": "cohere/north-mini-code:free",
        "provider": "openrouter-free",
        "public_sequence_id": unit.public_sequence_id,
        "rotation": unit.rotation,
        "runtime": "openai",
        "runtime_contract": protocol["runtime_and_provider_profile"][
            "effective_runtime_contract"
        ],
        "sample_id": unit.public_sequence_id,
        "seed": unit.seed,
        "started_at": "2026-08-20T00:00:00+00:00",
        "task_id": "online_replay_monitoring",
        "thinking_mode": "not_requested",
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": (
            "benchmark_generic_llm_tool_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_control_v1"
        ),
        "agent_implementation_id": (
            "reactive_sequential_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_agent_v1"
        ),
    }
    actions: list[dict] = []

    def append_action(
        *,
        name: str,
        arguments: dict,
        output: dict,
        prefix: list[str],
        cursor: int,
        event: dict | None = None,
    ) -> None:
        context = {
            "replay_cursor": cursor,
            "replay_length": unit.cell.horizon,
            "replay_sample_ids": prefix,
        }
        if event is not None:
            context["public_condition_event"] = event
        action = {"name": name, "arguments": arguments, "reasoning_trace": None}
        if unit.cell.graph_profile is not None:
            profile = protocol["graph_profiles"][unit.cell.graph_profile]
            toggles = profile["toggles"]
            previous_error = bool(actions and actions[-1]["result"]["status"] != "ok")
            previous_state = (
                actions[-1]["action"].get("decision_state")
                if actions and toggles["persistent_graph_state"]
                else None
            )
            if previous_error and toggles["recovery_revision_edge"]:
                state = "Recover"
            elif event is not None and toggles["observation_conditioned_branching"]:
                state = "Monitor"
            elif (
                previous_state == "Monitor"
                and toggles["recovery_revision_edge"]
                and toggles["replanning"]
            ):
                state = "Revise"
            else:
                state = _expected_base_state(actions, prefix)
            action["decision_state"] = state
        usage_delta = {
            "input_tokens": 10,
            "output_tokens": 1,
            "llm_turns": 1,
            "tool_calls": 1,
            "window_reads": int(name == "data.read_window"),
            "operator_calls": int(name == "op.run"),
            "model_calls": int(name == "model.predict"),
            "data_points_read": 8192 if name == "data.read_window" else 0,
            "data_bytes_read": 65536 if name == "data.read_window" else 0,
            "wall_clock_seconds": 0.001,
        }
        actions.append(
            {
                "protocol_version": "0.1.0",
                "run_id": run_id,
                "event_type": "action",
                "index": len(actions),
                "task_id": "online_replay_monitoring",
                "agent_id": agent_id,
                "observation": {
                    "sample_id": unit.public_sequence_id,
                    "task_id": "online_replay_monitoring",
                    "context": context,
                },
                "action": action,
                "result": {
                    "status": "ok",
                    "failure_kind": None,
                    "error_message": None,
                    "output": output,
                },
                "latency_seconds": 0.001,
                "usage_delta": usage_delta,
            }
        )

    alarms = [
        {
            "sample_id": sample,
            "score": 0.9 if index % 2 else 0.1,
            "predicted_class": "anomaly" if index % 2 else "normal",
            "supporting_refs": [f"artifact://prediction/{index:06d}"],
        }
        for index, sample in enumerate(samples)
    ]
    submission_payload = None
    if terminal_status == "submitted":
        predicted: set[str] = set()

        def process_current(
            *, prefix: list[str], cursor: int, event: dict | None = None
        ) -> None:
            sample = next(value for value in prefix if value not in predicted)
            sample_index = samples.index(sample)
            for operator_index in range(11):
                append_action(
                    name="op.run",
                    arguments={"name": f"fixture-op-{operator_index}", "sample_id": sample},
                    output={
                        "source_sample_id": sample,
                        "artifact_ref": f"artifact://op/{sample_index:04d}-{operator_index:02d}",
                    },
                    prefix=prefix,
                    cursor=cursor,
                    event=event if operator_index == 0 else None,
                )
            append_action(
                name="model.predict",
                arguments={"sample_id": sample},
                output={
                    "source_sample_id": sample,
                    "prediction_ref": f"artifact://prediction/{sample_index:06d}",
                },
                prefix=prefix,
                cursor=cursor,
            )
            predicted.add(sample)

        for release in range(unit.cell.horizon):
            prefix = samples[: release + 1]
            event = (
                {
                    "event": "operating_condition_change",
                    "event_id": _event_id(
                        protocol,
                        seed=unit.seed,
                        sequence_id=unit.public_sequence_id,
                        release=release,
                    ),
                    "release_index": release,
                }
                if release in {3, 6, 9}
                else None
            )
            current = next(value for value in prefix if value not in predicted)
            if event is None:
                sample_index = samples.index(current)
                append_action(
                    name="data.read_window",
                    arguments={"sample_id": current},
                    output={
                        "sample_id": current,
                        "artifact_ref": f"artifact://window/{sample_index:06d}",
                    },
                    prefix=prefix,
                    cursor=release,
                )
            if release == 0:
                append_action(
                    name="op.list",
                    arguments={},
                    output={"operators": []},
                    prefix=prefix,
                    cursor=release,
                )
            # Leave the current sample merely inspected immediately before a
            # registered event, so the event's Monitor edge starts from the
            # frozen legal Inspect state. The event turn then continues it.
            if event is not None:
                process_current(prefix=prefix, cursor=release, event=event)
            elif not (
                release + 1 in {3, 6, 9}
                and release + 1 < unit.cell.horizon
            ):
                process_current(prefix=prefix, cursor=release)

        while len(predicted) < len(samples):
            current = next(value for value in samples if value not in predicted)
            sample_index = samples.index(current)
            append_action(
                name="data.read_window",
                arguments={"sample_id": current},
                output={
                    "sample_id": current,
                    "artifact_ref": f"artifact://window/{sample_index:06d}",
                },
                prefix=samples,
                cursor=unit.cell.horizon,
            )
            process_current(prefix=samples, cursor=unit.cell.horizon)
        submission_payload = {
            "accepted": True,
            "alarms": alarms,
            "artifact_lineage_completeness": 1.0,
            "submission_grounding": 1.0,
            "supporting_reference_validity": 1.0,
        }
        append_action(
            name="submit",
            arguments={"alarms": alarms},
            output=submission_payload,
            prefix=samples,
            cursor=unit.cell.horizon,
        )

    usage = {
        "input_tokens": 10 * len(actions),
        "output_tokens": len(actions),
        "llm_turns": len(actions),
        "tool_calls": len(actions),
        "window_reads": unit.cell.horizon if actions else 0,
        "operator_calls": 11 * unit.cell.horizon if actions else 0,
        "model_calls": unit.cell.horizon if actions else 0,
        "data_points_read": 8192 * unit.cell.horizon if actions else 0,
        "data_bytes_read": 65536 * unit.cell.horizon if actions else 0,
        "wall_clock_seconds": 0.001 * len(actions),
    }
    evaluation = _metrics(
        terminal_status=terminal_status,
        grounded=grounded,
        usage=usage,
        action_count=len(actions),
        target_value=target_value,
        predictions=[str(item["predicted_class"]) for item in alarms],
    )
    run = {
        "agent_id": agent_id,
        "budget": budget,
        "failure_kind": failure_kind,
        "metadata": metadata,
        "protocol_version": "0.1.0",
        "raw_terminal_status": (
            "provider_error"
            if provider_failure
            else "agent_error"
            if agent_failure
            else None
        ),
        "run_id": run_id,
        "task": {
            "protocol_version": "0.1.0",
            "task_id": "online_replay_monitoring",
            "task_type": "online_replay_monitoring",
            "budget": budget,
            "public_context": {
                "replay_length": unit.cell.horizon,
                "replay_sample_ids": [samples[0]],
            },
        },
        "terminal_status": terminal_status,
        "usage": usage,
    }
    submission = {
        "status": "submitted" if submission_payload is not None else "missing",
        "terminal_status": terminal_status,
        "failure_kind": failure_kind,
        "message": None if failure_kind is None else "fixture failure",
        "payload": submission_payload,
    }
    terminal = {
        "protocol_version": "0.1.0",
        "run_id": run_id,
        "event_type": "terminal",
        "task_id": "online_replay_monitoring",
        "agent_id": agent_id,
        "terminal_status": terminal_status,
        "raw_terminal_status": run["raw_terminal_status"],
        "failure_kind": failure_kind,
        "terminal_message": None if failure_kind is None else "fixture failure",
        "usage": usage,
        "submission": submission,
    }
    failures = (
        []
        if failure_kind is None
        else [{"kind": failure_kind, "error": "fixture failure", "step": None}]
    )
    _json(leaf / "run.json", run)
    _jsonl(leaf / "rollout.jsonl", [*actions, terminal])
    _json(leaf / "submission.json", submission)
    _json(leaf / "metrics.json", evaluation)
    _jsonl(leaf / "failures.jsonl", failures)
    _json(leaf / "artifacts.json", {})
    private_row = None
    if not provider_failure:
        private_row = {
            "rotation": unit.rotation,
            "sample_id": unit.public_sequence_id,
            "sample_ids": samples,
            "task_id": "online_replay_monitoring",
            "private_target": {
                sample: target_value for sample in samples
            },
            "submission": submission_payload,
            "evaluation": evaluation,
        }
    return run, private_row


def _write_unit(
    root: Path,
    protocol: dict,
    unit,
    *,
    provider_retry: bool,
    agent_failure: bool,
) -> None:
    directory = unit_root(root, unit)
    directory.mkdir(parents=True, exist_ok=True)
    attempt_count = 1
    if provider_retry:
        _write_attempt(
            directory,
            protocol,
            unit,
            attempt_index=0,
            provider_failure=True,
        )
        attempt_count = 2
    _run, private_row = _write_attempt(
        directory,
        protocol,
        unit,
        attempt_index=attempt_count - 1,
        agent_failure=agent_failure,
    )
    assert private_row is not None
    _jsonl(directory / "evaluation.jsonl", [private_row])
    runtime = protocol["runtime_and_provider_profile"]
    manifest = {
        "study": "graph_dynamic_ablation_v3",
        "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
        "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
        "agent_control_id": (
            "benchmark_generic_llm_tool_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_control_v1"
        ),
        "agent_implementation_id": (
            "reactive_sequential_agent_v1"
            if unit.cell.arm == "reactive"
            else "graph_decision_agent_v1"
        ),
        "dynamic_protocol": protocol["schema_version"],
        "dataset_protocol": protocol["dataset"]["dataset_protocol_schema"],
        "runtime_contract": runtime["effective_runtime_contract"],
        "runtime": "openai",
        "provider_profile_id": runtime["formal_provider_profile_id"],
        "provider": runtime["provider"],
        "model": runtime["model"],
        "inference_protocol": runtime["protocol"],
        "thinking_mode": "not_requested",
        "temperature": protocol["shared_agent_contract"]["shared"]["temperature"],
        "max_output_tokens_per_turn": protocol["shared_agent_contract"]["shared"]["max_output_tokens_per_turn"],
        "input_usd_per_million": runtime["input_usd_per_million"],
        "output_usd_per_million": runtime["output_usd_per_million"],
        "arm": unit.cell.arm,
        "graph_policy_profile": (
            "reactive" if unit.cell.graph_profile is None else unit.cell.graph_profile
        ),
        "agent_profile_id": unit.cell.agent_profile_id,
        "seed": unit.seed,
        "rotation": unit.rotation,
        "public_sequence_id": unit.public_sequence_id,
        "horizon": unit.cell.horizon,
        "budget": protocol["budgets"]["by_horizon"][unit.cell.horizon],
        "canonical_episode_count": attempt_count,
        "evidence_class": "real_data_formal_candidate",
    }
    _json(directory / "run_manifest.json", manifest)


def _build_fixture(root: Path, protocol: dict) -> None:
    units = expected_units(protocol)
    for index, unit in enumerate(units):
        _write_unit(
            root,
            protocol,
            unit,
            provider_retry=index == 0,
            agent_failure=(
                unit.seed == 20260810
                and unit.public_sequence_id == "sequence-0008"
                and unit.cell.name == "graph_no_replanning"
            ),
        )


class GraphDynamicFormalAnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_protocol(PROTOCOL_PATH)

    def test_protocol_registers_exact_240_isolated_units_and_analyzer(self) -> None:
        units = expected_units(self.protocol)
        self.assertEqual(len(units), 240)
        self.assertEqual(len({unit.key for unit in units}), 240)
        self.assertEqual(
            self.protocol["formal_analysis"]["analyzer"],
            "scripts/analyze_graph_dynamic_formal.py",
        )
        self.assertFalse(
            self.protocol["formal_analysis"]["identity_and_grouping"][
                "pool_episode_rows_across_horizons"
            ]
        )
        self.assertEqual(
            self.protocol["runtime_and_provider_profile"]["input_usd_per_million"],
            0.0,
        )
        catalog = build_public_event_catalog(self.protocol)
        self.assertEqual(catalog["event_count"], 72)
        self.assertEqual(len({row["event_id"] for row in catalog["events"]}), 72)
        self.assertFalse(catalog["provider_calls_performed"])
        self.assertFalse(catalog["private_identifiers_included"])
        self.assertNotIn("horizon", json.dumps(catalog))
        self.assertNotIn("bearing", json.dumps(catalog))

    def test_target_adverse_primary_keeps_failed_bearing_windows_in_denominator(
        self,
    ) -> None:
        healthy_ids = ["healthy-0", "healthy-1", "healthy-2"]
        fault_ids = ["fault-0", "fault-1", "fault-2"]
        healthy_submission = {
            "alarms": [
                {
                    "sample_id": sample_id,
                    "score": score,
                    "predicted_class": "normal",
                }
                for sample_id, score in zip(
                    healthy_ids, (0.1, 0.2, 0.3), strict=True
                )
            ]
        }

        def row(
            bearing_id: str,
            sample_ids: list[str],
            target: int,
            submission: dict | None,
        ) -> dict:
            return {
                "_analysis_replay_record": {
                    "task_id": "online_replay_monitoring",
                    "bearing_id": bearing_id,
                    "sample_ids": sample_ids,
                    "private_target": {
                        sample_id: target for sample_id in sample_ids
                    },
                    "submission": submission,
                    "evaluation": {
                        "task_metrics": {
                            "submission": float(submission is not None)
                        },
                        "rollout_metrics": {},
                    },
                }
            }

        summary = _replay_task_summary(
            [
                row("healthy-bearing", healthy_ids, 0, healthy_submission),
                row("fault-bearing", fault_ids, 1, None),
            ]
        )
        self.assertEqual(summary["assigned_windows"], 6)
        self.assertEqual(summary["submitted_windows"], 3)
        self.assertEqual(summary["missing_assigned_scores"], 3)
        self.assertEqual(summary["score_coverage"], 0.5)
        self.assertEqual(summary["average_precision"], 0.0)
        self.assertEqual(summary["true_positive_rate"], 0.0)

    def test_private_assignments_are_exact_nested_nonoverlapping_binary_masters(
        self,
    ) -> None:
        assignments = _private_assignments(self.protocol)
        normalized = _validate_private_dynamic_assignments(
            assignments, self.protocol
        )
        self.assertEqual(len(normalized), 8)

        projected: dict[tuple[str, int], set[tuple[tuple[str, int], ...]]] = {}
        for unit in expected_units(self.protocol):
            assignment = _private_assignment_for_unit(normalized, unit)
            key = (unit.public_sequence_id, unit.cell.horizon)
            projected.setdefault(key, set()).add(
                tuple(assignment["private_target"].items())
            )
        self.assertTrue(all(len(values) == 1 for values in projected.values()))
        for sequence_id in normalized:
            h3 = dict(next(iter(projected[(sequence_id, 3)])))
            h6 = dict(next(iter(projected[(sequence_id, 6)])))
            h12 = dict(next(iter(projected[(sequence_id, 12)])))
            self.assertEqual(list(h6.items())[:3], list(h3.items()))
            self.assertEqual(list(h12.items())[:6], list(h6.items()))

        missing = copy.deepcopy(assignments)
        missing.pop("sequence-0008")
        with self.assertRaisesRegex(
            GraphDynamicFormalError, "do not cover the registered sequences"
        ):
            _validate_private_dynamic_assignments(missing, self.protocol)

        overlap = copy.deepcopy(assignments)
        overlap["sequence-0002"] = copy.deepcopy(overlap["sequence-0001"])
        with self.assertRaisesRegex(
            GraphDynamicFormalError, "overlap across registered sequences"
        ):
            _validate_private_dynamic_assignments(overlap, self.protocol)

        nonbinary = copy.deepcopy(assignments)
        first_sample = nonbinary["sequence-0001"]["sample_ids"][0]
        nonbinary["sequence-0001"]["private_target"][first_sample] = True
        with self.assertRaisesRegex(GraphDynamicFormalError, "is not binary"):
            _validate_private_dynamic_assignments(nonbinary, self.protocol)

    def test_private_assignment_builder_binds_registered_dataset_identity(self) -> None:
        dataset = yaml.safe_load(DATASET_PROTOCOL_PATH.read_text(encoding="utf-8"))
        sequences = {
            f"sequence-{index:04d}": SimpleNamespace(
                sample_ids=tuple(_master(f"sequence-{index:04d}", 12))
            )
            for index in range(1, 9)
        }

        class FakeData:
            def private_record(self, sample_id: str) -> dict:
                sequence = int(sample_id.split("-")[1])
                return {"target": (sequence - 1) % 2}

        port = mock.MagicMock()
        port.__enter__.return_value = FakeData()
        port.__exit__.return_value = None
        with (
            mock.patch(
                "scripts.analyze_graph_dynamic_formal.load_dataset_protocol",
                return_value=dataset,
            ),
            mock.patch(
                "scripts.analyze_graph_dynamic_formal.LocalPaderbornDataPort",
                return_value=port,
            ) as data_port,
            mock.patch(
                "scripts.analyze_graph_dynamic_formal.build_master_sequences",
                return_value=sequences,
            ),
            mock.patch(
                "scripts.analyze_graph_dynamic_formal.anomaly_target",
                side_effect=lambda record: record["target"],
            ),
        ):
            observed = build_private_dynamic_assignments(
                self.protocol,
                dataset_protocol_path=DATASET_PROTOCOL_PATH,
                metadata_path="/private/metadata.xlsx",
                signal_path="/private/signals.h5",
            )
        self.assertEqual(observed, _private_assignments(self.protocol))
        data_port.assert_called_once_with(
            "/private/metadata.xlsx",
            "/private/signals.h5",
            public_id_seed=20260808,
        )

        drifted = copy.deepcopy(dataset)
        drifted["protocol_id"] = "wrong_private_dataset"
        with mock.patch(
            "scripts.analyze_graph_dynamic_formal.load_dataset_protocol",
            return_value=drifted,
        ):
            with self.assertRaisesRegex(
                GraphDynamicFormalError, "authority drifted"
            ):
                build_private_dynamic_assignments(
                    self.protocol,
                    dataset_protocol_path=DATASET_PROTOCOL_PATH,
                    metadata_path="/private/not-opened.xlsx",
                    signal_path="/private/not-opened.h5",
                )

    def test_derived_evaluation_is_ignored_and_private_tamper_fails_closed(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build_fixture(root, self.protocol)
            assignments = _private_assignments(self.protocol)
            baseline_acceptance = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertTrue(
                baseline_acceptance["accepted"], baseline_acceptance["errors"]
            )

            def analyze(acceptance: dict) -> dict:
                with (
                    mock.patch(
                        "scripts.analyze_graph_dynamic_formal._bootstrap_interval",
                        return_value=[0.0, 0.0],
                    ),
                    mock.patch(
                        "scripts.analyze_graph_dynamic_formal._task_metric_bootstrap",
                        return_value=([0.0, 0.0], 10000),
                    ),
                    mock.patch(
                        "scripts.analyze_graph_dynamic_formal._task_interaction_bootstrap",
                        return_value=([0.0, 0.0], 10000),
                    ),
                    mock.patch(
                        "scripts.analyze_graph_dynamic_formal._task_metric_exact_swap",
                        return_value=(1.0, 256),
                    ),
                    mock.patch(
                        "scripts.analyze_graph_dynamic_formal._task_interaction_exact_swap",
                        return_value=(1.0, 256),
                    ),
                ):
                    return analyze_formal_cohort(
                        root,
                        self.protocol,
                        acceptance,
                        private_dynamic_assignments=assignments,
                    )

            baseline_result = analyze(baseline_acceptance)
            derived = next(root.rglob("evaluation.jsonl"))
            derived.write_text("not derived evaluator truth\n", encoding="utf-8")
            tampered_acceptance = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertEqual(tampered_acceptance, baseline_acceptance)
            self.assertEqual(analyze(tampered_acceptance), baseline_result)

            derived.unlink()
            deleted_acceptance = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertEqual(deleted_acceptance, baseline_acceptance)
            self.assertEqual(analyze(deleted_acceptance), baseline_result)

            wrong_order = copy.deepcopy(assignments)
            wrong_order["sequence-0001"]["sample_ids"][:2] = reversed(
                wrong_order["sequence-0001"]["sample_ids"][:2]
            )
            order_report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=wrong_order,
            )
            self.assertFalse(order_report["accepted"])
            self.assertIn("released prefix disagrees", order_report["errors"][0])

            wrong_target = copy.deepcopy(assignments)
            sample_id = wrong_target["sequence-0001"]["sample_ids"][0]
            wrong_target["sequence-0001"]["private_target"][sample_id] = 1
            target_report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=wrong_target,
            )
            self.assertFalse(target_report["accepted"])
            self.assertIn("average_precision", target_report["errors"][0])

            public = json.dumps(
                {"acceptance": baseline_acceptance, "result": baseline_result},
                sort_keys=True,
            )
            public_keys: set[str] = set()

            def collect_keys(value: object) -> None:
                if isinstance(value, dict):
                    public_keys.update(str(key) for key in value)
                    for item in value.values():
                        collect_keys(item)
                elif isinstance(value, list):
                    for item in value:
                        collect_keys(item)

            collect_keys({"acceptance": baseline_acceptance, "result": baseline_result})
            self.assertNotIn("private_target", public_keys)
            self.assertNotIn("bearing_id", public_keys)
            self.assertNotIn("metadata_path", public_keys)
            self.assertNotIn("signal_path", public_keys)
            self.assertNotIn("sample-0001-00", public)
            self.assertNotIn("/private/metadata.xlsx", public)
            self.assertNotIn("/private/signals.h5", public)

    def test_complete_cohort_retains_failures_and_never_pools(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build_fixture(root, self.protocol)
            assignments = _private_assignments(self.protocol)
            acceptance = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            inclusion = acceptance["canonical_inclusion"]
            self.assertEqual(inclusion["scheduled_unit_denominator"], 240)
            self.assertEqual(inclusion["effective_non_provider_terminal_count"], 240)
            self.assertEqual(inclusion["retained_provider_failure_attempt_count"], 1)
            self.assertEqual(inclusion["retained_non_provider_failure_count"], 1)
            self.assertEqual(set(inclusion["cell_denominators"].values()), {24})
            with (
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._bootstrap_interval",
                    return_value=[0.0, 0.0],
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_metric_bootstrap",
                    return_value=([0.0, 0.0], 10000),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_interaction_bootstrap",
                    return_value=([0.0, 0.0], 10000),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_metric_exact_swap",
                    return_value=(1.0, 256),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_interaction_exact_swap",
                    return_value=(1.0, 256),
                ),
            ):
                result = analyze_formal_cohort(
                    root,
                    self.protocol,
                    acceptance,
                    private_dynamic_assignments=assignments,
                )

        self.assertFalse(result["provider_calls_performed_by_analyzer"])
        self.assertEqual(len(result["by_cell"]), 10)
        self.assertNotIn("pooled", result)
        invariants = result["grouping_invariants"]
        self.assertFalse(invariants["pooled_headline_graph_effect_across_horizons"])
        self.assertFalse(invariants["pool_across_provider_model_or_runtime_profiles"])
        self.assertTrue(
            invariants[
                "task_primary_recomputed_over_all_assigned_windows_within_seed_cell"
            ]
        )
        self.assertFalse(invariants["per_bearing_average_precision_performed"])
        failed_cell = result["by_cell"]["h12:graph_no_replanning"]
        primary = failed_cell["metrics"][
            "target_adverse_window_average_precision"
        ]
        self.assertEqual(primary["assigned_episode_denominator"], 24)
        self.assertEqual(primary["assigned_window_denominator"], 288)
        self.assertEqual(primary["submitted_window_numerator"], 276)
        self.assertEqual(primary["missing_assigned_scores"], 12)
        self.assertAlmostEqual(primary["score_coverage"], 23 / 24)
        self.assertFalse(primary["per_bearing_metric_averaging_performed"])
        self.assertNotEqual(primary["estimate"], 1.0)
        completion = failed_cell["metrics"]["grounded_completion_rate"]
        self.assertAlmostEqual(completion["estimate"], 23 / 24)
        p2e6 = result["registered_contrasts"]["P2-E3_to_P2-E6"]["P2-E6"]
        self.assertAlmostEqual(
            p2e6["grounded_completion_rate"]["estimate"], 1 / 24
        )
        task_primary_delta = p2e6[
            "target_adverse_window_average_precision"
        ]
        self.assertEqual(task_primary_delta["treatment_assigned_windows"], 288)
        self.assertEqual(task_primary_delta["control_assigned_windows"], 288)
        self.assertTrue(
            task_primary_delta[
                "metric_recomputed_after_each_cluster_draw_or_swap"
            ]
        )
        full_dynamic = result["by_cell"]["h12:graph_full"]["metrics"]
        self.assertEqual(
            full_dynamic["event_to_Monitor_transition_rate"]["estimate"], 1.0
        )
        self.assertEqual(
            full_dynamic["event_to_Revise_transition_rate"]["estimate"], 1.0
        )
        no_branch = result["by_cell"][
            "h12:graph_no_observation_conditioned_branching"
        ]["metrics"]
        self.assertEqual(
            no_branch["event_to_Monitor_transition_rate"]["estimate"], 0.0
        )
        self.assertEqual(
            result["registered_contrasts"]["P2-E7"]["new_episode_bundles_added"],
            0,
        )
        recovery_report = p2e6["grounded_recovery_success"]
        self.assertEqual(
            set(recovery_report["seed_level_differences_by_public_sequence"]),
            {f"sequence-{index:04d}" for index in range(1, 9)},
        )
        self.assertEqual(
            recovery_report["paired_cluster_bootstrap_valid_replicates"],
            10000,
        )
        self.assertEqual(
            result["registered_contrasts"]["P2-E7"][
                "registered_report_sources"
            ]["graph_full_minus_reactive"],
            "P2-E2.graph_full_minus_reactive_by_horizon.12",
        )

    def test_real_240_unit_analyzer_result_feeds_manuscript_consumer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            formal_root = root / "formal"
            _build_fixture(formal_root, self.protocol)
            assignments = _private_assignments(self.protocol)
            acceptance = accept_formal_cohort(
                formal_root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertTrue(acceptance["accepted"], acceptance["errors"])
            with (
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_metric_bootstrap",
                    return_value=([0.0, 0.0], 10000),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_interaction_bootstrap",
                    return_value=([0.0, 0.0], 10000),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_metric_exact_swap",
                    return_value=(1.0, 256),
                ),
                mock.patch(
                    "scripts.analyze_graph_dynamic_formal._task_interaction_exact_swap",
                    return_value=(1.0, 256),
                ),
            ):
                result = analyze_formal_cohort(
                    formal_root,
                    self.protocol,
                    acceptance,
                    private_dynamic_assignments=assignments,
                )
            acceptance_path = root / "formal_acceptance.json"
            result_path = root / "formal_result.json"
            _json(acceptance_path, acceptance)
            _json(result_path, result)
            manuscript_path = root / "main.md"
            manuscript_path.write_text(
                f"Before\n{MANUSCRIPT_BEGIN}\npending\n{MANUSCRIPT_END}\nAfter\n",
                encoding="utf-8",
            )
            table_path = root / "table.md"
            figure_path = root / "figure.svg"
            summary = write_dynamic_manuscript(
                protocol_path=PROTOCOL_PATH,
                result_path=result_path,
                acceptance_path=acceptance_path,
                table_path=table_path,
                figure_path=figure_path,
                manuscript_path=manuscript_path,
            )
            self.assertEqual(summary["task_primary_rows"], 8)
            self.assertEqual(summary["secondary_mechanism_rows"], 26)
            table = table_path.read_text(encoding="utf-8")
            self.assertIn("Registered secondary mechanism outcomes", table)
            self.assertIn("P2-E4 / P2-E7", table)
            self.assertTrue(figure_path.is_file())

    def test_gate_fails_closed_on_profile_transition_event_and_attempt_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _build_fixture(root, self.protocol)
            units = expected_units(self.protocol)
            full = next(
                unit
                for unit in units
                if unit.seed == 20260808
                and unit.public_sequence_id == "sequence-0001"
                and unit.cell.key == "h12:graph_full"
            )
            leaf = unit_root(root, full) / "attempt_000"
            run_path = leaf / "run.json"
            original_run = _read(run_path)
            drifted = copy.deepcopy(original_run)
            drifted["metadata"]["model"] = "wrong/model"
            _json(run_path, drifted)
            assignments = _private_assignments(self.protocol)
            report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertFalse(report["accepted"])
            self.assertIn("profile drift", report["errors"][0])
            _json(run_path, original_run)

            rollout_path = leaf / "rollout.jsonl"
            original_rollout = _read_lines(rollout_path)
            illegal = copy.deepcopy(original_rollout)
            event_row = next(
                row
                for row in illegal
                if row.get("event_type") == "action"
                and row["observation"]["context"].get("public_condition_event")
            )
            event_row["action"]["decision_state"] = "Inspect"
            _jsonl(rollout_path, illegal)
            report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertFalse(report["accepted"])
            self.assertTrue(
                "did not enter Monitor" in report["errors"][0]
                or "illegal in state" in report["errors"][0]
            )
            _jsonl(rollout_path, original_rollout)

            event_drift = copy.deepcopy(original_rollout)
            event_row = next(
                row
                for row in event_drift
                if row.get("event_type") == "action"
                and row["observation"]["context"].get("public_condition_event")
            )
            event_row["observation"]["context"]["public_condition_event"][
                "event_id"
            ] = "occ-99999999"
            _jsonl(rollout_path, event_drift)
            report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertFalse(report["accepted"])
            self.assertIn("event identity/release drift", report["errors"][0])
            _jsonl(rollout_path, original_rollout)

            provider_unit = units[0]
            retry = unit_root(root, provider_unit) / "attempt_001"
            shutil.rmtree(retry)
            manifest_path = unit_root(root, provider_unit) / "run_manifest.json"
            manifest = _read(manifest_path)
            manifest["canonical_episode_count"] = 1
            _json(manifest_path, manifest)
            report = accept_formal_cohort(
                root,
                self.protocol,
                private_dynamic_assignments=assignments,
            )
            self.assertFalse(report["accepted"])
            self.assertIn("0 non-provider terminals", report["errors"][0])

    def test_analysis_rejects_unaccepted_or_drifted_acceptance(self) -> None:
        unaccepted = {
            "schema_version": ACCEPTANCE_SCHEMA,
            "accepted": False,
        }
        with self.assertRaisesRegex(GraphDynamicFormalError, "acceptance report drifted"):
            validate_acceptance("/tmp/unused", self.protocol, unaccepted)


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


if __name__ == "__main__":
    unittest.main()
