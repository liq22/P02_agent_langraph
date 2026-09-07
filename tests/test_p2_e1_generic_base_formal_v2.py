from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

from phm_agent_benchmark import Budget, EvaluatorResult, Rollout, RolloutEvent, TaskSpec
from phm_agent_benchmark.phase1.cohort import (
    episode_attempt_directory,
    read_cohort_index,
    write_cohort_index,
)
from phm_agent_benchmark.phase1.experiment import (
    IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY,
    IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID,
)
from phm_agent_benchmark.protocol import DataAccessScope, EpisodeSpec, PROTOCOL_VERSION, USAGE_ACCOUNTING_CONTRACT
from phm_agent_benchmark.rollout_io import write_episode_bundle
from scripts import finalize_p2_e1_generic_base_formal_v2 as MODULE
from scripts.render_graph_manuscript_table import (
    render_tables_from_combined_result,
    write_table,
)


MODEL_PROFILE = {
    "provider": "openrouter-free",
    "model_id": "cohere/north-mini-code:free",
    "protocol": "openai_chat_completions",
    "input_usd_per_million": 0.0,
    "output_usd_per_million": 0.0,
}
CORE_BUDGET = {
    "max_tool_calls": 33,
    "max_window_reads": 3,
    "max_operator_calls": 17,
    "max_model_calls": 2,
    "max_llm_turns": 33,
}
REPLAY_BUDGET = {
    "max_tool_calls": 72,
    "max_window_reads": 3,
    "max_operator_calls": 50,
    "max_model_calls": 3,
    "max_llm_turns": 72,
}
WINDOW = {
    "contract": "phase1_single_vibration_full_rate_v3",
    "channel_indices": [2],
    "channel_semantics": "bearing_housing_acceleration",
    "upstream_column_mapping": {0: "x", 1: "y", 2: "vibration"},
    "mapping_source": "fixture",
    "mapping_source_url": "https://example.invalid/fixture",
    "start_point": 0,
    "end_point": 8192,
    "max_returned_points": 8192,
    "bounded_read": True,
    "sampling_mode": "full_rate_no_decimation",
    "selection_evidence": "fixture",
}
P2_IDENTITY = {
    "p2_experiment_id": "p2_graph_vs_generic_llm_v1",
    "matched_control_id": "benchmark_generic_llm_tool_agent_v1",
    "agent_control_id": "graph_decision_control_v1",
    "agent_implementation_id": "graph_decision_agent_v1",
}
FORMAL_RUN_STAMP = "20260901T010203Z"
BENCHMARK_CONTROL_SOURCE = {
    "contract": MODULE.BENCHMARK_CONTROL_SOURCE_CONTRACT,
    "formal_run_stamp": FORMAL_RUN_STAMP,
    "protocol_id": MODULE.ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
    "profile_id": MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
}
BENCHMARK_FORMAL_EXECUTION_TOPOLOGY = {
    "contract": MODULE.BENCHMARK_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    "benchmark_repository": MODULE.BENCHMARK_REPOSITORY,
    "benchmark_revision": "a" * 40,
    "data_factory_repository": MODULE.DATA_FACTORY_REPOSITORY,
    "data_factory_revision": "b" * 40,
    "data_factory_distribution_version": "0.2.1",
    "data_factory_lock_version": "0.2.1",
}
GRAPH_FORMAL_EXECUTION_TOPOLOGY = {
    "contract": MODULE.P2_FORMAL_EXECUTION_TOPOLOGY_CONTRACT,
    "benchmark_formal_execution_topology": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY,
    "source_repositories": {
        "benchmark": MODULE.BENCHMARK_REPOSITORY,
        "data_factory": MODULE.DATA_FACTORY_REPOSITORY,
        "p2": MODULE.P2_REPOSITORY,
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
    "p2_formal_reproducibility_paths": list(
        MODULE.P2_FORMAL_REPRODUCIBILITY_PATHS
    ),
}


class P2E1GenericBaseFormalV2Test(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.dataset_path = self.root / "dataset_protocol.yaml"
        self.protocol_path = self.root / "p2_e1_v2.yaml"
        self.formal_run_stamp = FORMAL_RUN_STAMP
        formal_family = self.root / MODULE.ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
        self.roots = {
            "generic_core": formal_family
            / "b3_generic_core"
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            / f"run_{self.formal_run_stamp}",
            "graph_core": formal_family
            / "graph_core_primary"
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            / f"run_{self.formal_run_stamp}",
            "generic_replay": formal_family
            / "b3_generic_replay"
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            / f"run_{self.formal_run_stamp}",
            "graph_replay": formal_family
            / "graph_replay_primary"
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            / f"run_{self.formal_run_stamp}",
        }
        self.dataset = self._dataset()
        self.dataset_path.write_text(yaml.safe_dump(self.dataset, sort_keys=False), encoding="utf-8")
        protocol = yaml.safe_load(MODULE.DEFAULT_PROTOCOL.read_text(encoding="utf-8"))
        protocol["dataset_protocol"] = str(self.dataset_path)
        self.protocol_path.write_text(yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def _dataset() -> dict:
        folds = {f"fold_{index}": [f"B{index}{bearing}" for bearing in range(8)] for index in range(4)}
        rotations = [
            {
                "run": f"rotation_{index}",
                "train": [f"fold_{(index + 2) % 4}"],
                "validation": f"fold_{(index + 1) % 4}",
                "test": f"fold_{index}",
            }
            for index in range(4)
        ]
        return {
            "protocol_id": "fixture_paderborn_phase1_v1",
            "schema_version": "phm_agent_dataset_protocol_v1",
            "status": "active_phase1",
            "agent_visibility": {
                "sample_handle": {
                    "scheme": "seeded_permutation_v1",
                    "seed": 20260808,
                    "purpose": "fixture_opaque_handle",
                }
            },
            "split": {"folds": folds, "rotations": rotations},
            "tasks": {
                "diagnosis": {
                    "labels": ["healthy", "inner_ring", "outer_ring"],
                },
                "monitoring": {
                    "missing_assigned_score_policy": dict(
                        IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY
                    ),
                },
            },
            "window_protocol": WINDOW,
            "episode_sampling": {
                "train_samples_per_bearing": 8,
                "healthy_validation_samples_per_bearing": 8,
                "agent_test_samples_per_bearing": 1,
                "monitoring_windows_per_episode": 3,
                "agent_selection": "metadata_order_floor_two_thirds",
                "numerical_selection": "evenly_spaced_over_metadata_order",
                "monitoring_rotations": ["rotation_0"],
            },
            "inference": {
                "temperature": 0.2,
                "max_output_tokens_per_turn": 2048,
                "model_profile": MODEL_PROFILE,
            },
            "budgets": {"core": CORE_BUDGET, "monitoring": REPLAY_BUDGET},
        }

    def _manifest(self, *, graph: bool, scope: str, seed: int, rotation: str) -> dict:
        tasks = list(MODULE.CORE_TASKS if scope == "core" else MODULE.REPLAY_TASKS)
        budget = CORE_BUDGET if scope == "core" else REPLAY_BUDGET
        value = {
            "protocol": "phm_agent_dataset_protocol_v1",
            "benchmark_protocol_version": PROTOCOL_VERSION,
            "dataset_protocol_id": self.dataset["protocol_id"],
            "dataset_protocol_schema": self.dataset["schema_version"],
            "window_contract": WINDOW["contract"],
            "runtime": "openai",
            "runtime_contract": "phase1_opaque_sample_vibration_feature_schema_v6",
            "rotation": rotation,
            "seed": seed,
            "tasks": tasks,
            "temperature": 0.2,
            "max_output_tokens_per_turn": 2048,
            "model_profile": MODEL_PROFILE,
            "sample_handle": self.dataset["agent_visibility"]["sample_handle"],
            "window_protocol": WINDOW,
            "train_samples_per_bearing": 8,
            "validation_samples_per_bearing": 8,
            "test_samples_per_bearing": 1 if scope == "core" else 3,
            "test_sample_selection": (
                "metadata_order_floor_two_thirds"
                if scope == "core"
                else "evenly_spaced_over_metadata_order"
            ),
            "max_test_bearings": None,
            "budget": budget,
            "budget_protocol": {
                **budget,
                "max_data_points": None,
                "max_data_bytes": None,
                "max_wall_clock_seconds": None,
            },
            "selected_diagnosis_model_id": "ridge-ovr-v1",
            "validation_model_macro_f1": {"ridge-ovr-v1": 0.6},
            "registered_evidence_class": "formal",
            "result_role": "confirmatory",
            "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
            "replay_missing_score_policy_id": (
                IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID
                if scope == "replay"
                else None
            ),
            "agent_id": "graph-decision-agent" if graph else "generic-llm-tool-agent",
            "formal_execution_topology": (
                GRAPH_FORMAL_EXECUTION_TOPOLOGY
                if graph
                else BENCHMARK_FORMAL_EXECUTION_TOPOLOGY
            ),
        }
        if graph:
            value.update(
                {
                    "arm": "graph",
                    "graph_policy_profile": "full",
                    "benchmark_control_source": dict(BENCHMARK_CONTROL_SOURCE),
                    **P2_IDENTITY,
                }
            )
        else:
            value["experiment_profile_id"] = (
                MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            )
        return value

    @staticmethod
    def _rollout_metrics(graph: bool) -> dict:
        grounded = 1.0 if graph else 0.0
        return {
            "artifact_lineage_completeness": grounded,
            "budget_exhaustion": 0.0,
            "estimated_model_cost_usd": 0.0,
            "failure_count": 0.0,
            "grounded_completion": grounded,
            "grounded_recovery_success": 0.0,
            "input_tokens": 10.0,
            "llm_turns": 1.0,
            "model_calls": 1.0,
            "operator_calls": 1.0,
            "output_tokens": 2.0,
            "repeated_action_ratio": 0.0,
            "recovery_coverage": None,
            "steps_to_recovery": None,
            "steps": 1.0,
            "steps_to_next_success_after_failure": None,
            "submission_grounding": grounded,
            "submission_rate": 1.0,
            "supporting_reference_validity": grounded,
            "tool_execution_failure_rate": 0.0,
            "valid_tool_call_rate": 1.0,
            "wall_clock_seconds": 1.0,
            "p95_step_latency_seconds": 0.1,
            "window_reads": 1.0,
        }

    def _evaluation_row(
        self, *, graph: bool, bearing: str, rotation: str, sample_id: str, task: str
    ) -> tuple[dict, dict]:
        target = int(bearing[-1]) % 2
        metrics = {
            "evaluator_id": "phase1",
            "evaluator_method": "deterministic",
            "rollout_metrics": self._rollout_metrics(graph),
            "task_id": task,
            "task_metrics": {"submission": 1.0, "confidence": 0.8},
            "terminal_status": "submitted",
        }
        if task == "cold_start_fault_diagnosis":
            private_target: object = "healthy" if target == 0 else "inner_ring"
            submission: object = {"label": private_target, "confidence": 0.8}
        elif task == "unsupervised_anomaly_detection":
            private_target = target
            submission = {
                "score": float(target),
                "predicted_class": "anomaly" if target else "normal",
            }
        else:
            private_target = {f"{sample_id}-w{index}": int(index == 2) for index in range(3)}
            submission = {
                "alarms": [
                    {
                        "sample_id": window_id,
                        "score": float(label),
                        "predicted_class": "anomaly" if label else "normal",
                    }
                    for window_id, label in private_target.items()
                ]
            }
        row = {
            "bearing_id": bearing,
            "evaluation": metrics,
            "private_target": private_target,
            "rotation": rotation,
            "sample_id": sample_id,
            "submission": submission,
            "task_id": task,
        }
        if task == "online_replay_monitoring":
            row["sample_ids"] = list(private_target)
            row["replay_decisions"] = []
        return metrics, row

    def _write_attempt(
        self,
        *,
        unit: Path,
        graph: bool,
        scope: str,
        seed: int,
        rotation: str,
        bearing: str,
        sample_id: str,
        task: str,
        attempt_index: int = 0,
        provider_failure: bool = False,
        natural_failure: bool = False,
    ) -> dict | None:
        budget_view = CORE_BUDGET if scope == "core" else REPLAY_BUDGET
        budget = Budget(**budget_view)
        _metrics, private_row = self._evaluation_row(
            graph=graph, bearing=bearing, rotation=rotation, sample_id=sample_id, task=task
        )
        task_spec_id = f"{task}.v0"
        episode_id = f"{rotation}--{task}--{sample_id}"
        task_spec = TaskSpec(
            task_spec_id=task_spec_id,
            task_type=task,
            instruction="Fixture task with no evaluator-private context.",
            budget=budget,
            evaluator_id="phase1",
        )
        rollout = Rollout(
            task_spec_id=task_spec_id,
            task_type=task,
            episode_id=episode_id,
            agent_id="graph-decision-agent" if graph else "generic-llm-tool-agent",
            usage={"input_tokens": 0, "output_tokens": 0},
        )
        if provider_failure:
            rollout.mark_failed("provider_error", "fixture provider interruption")
        elif natural_failure:
            rollout.mark_failed("budget_exhausted", "fixture budget exhausted")
            rollout.terminal_status = "budget_exhausted"
        elif task == "online_replay_monitoring":
            rollout.terminal_status = "stopped"
        else:
            payload = dict(private_row["submission"])
            payload["supporting_refs"] = []
            rollout.steps.append(
                RolloutEvent(
                    index=0,
                    observation_summary={"sample_id": sample_id},
                    action="tool_call",
                    tool_name="submit",
                    tool_args=payload,
                    tool_result=payload,
                    decision_state="Submit" if graph else None,
                )
            )
            rollout.submission = payload
            rollout.terminal_status = "submitted"
        terminal_status = rollout.normalized_terminal_status
        task_metrics = {
            "submission": float(terminal_status == "submitted"),
            "confidence": 0.8 if terminal_status == "submitted" else None,
        }
        evaluation = EvaluatorResult(
            task_spec_id=task_spec_id,
            task_type=task,
            episode_id=episode_id,
            task_metrics=task_metrics,
            rollout_metrics=self._rollout_metrics(graph),
            terminal_status=terminal_status,
            evaluator_id="phase1",
            evaluator_method="deterministic",
        )
        profile = self._manifest(
            graph=graph, scope=scope, seed=seed, rotation=rotation
        )
        resume_identity = {
            "registered_evidence_class": "formal",
            "result_role": "confirmatory",
            "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
            "replay_missing_score_policy_id": (
                IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID
                if scope == "replay"
                else None
            ),
            "monitoring_budget" if scope == "replay" else "core_budget": profile["budget_protocol"],
            "formal_execution_topology": profile["formal_execution_topology"],
        }
        if graph:
            resume_identity["benchmark_control_source"] = dict(
                BENCHMARK_CONTROL_SOURCE
            )
        metadata = {
            "episode_key": [rotation, sample_id, task],
            "attempt_index": attempt_index,
            "dataset_protocol": "phm_agent_dataset_protocol_v1",
            "benchmark_protocol_version": PROTOCOL_VERSION,
            "dataset_protocol_id": self.dataset["protocol_id"],
            "dataset_protocol_schema": self.dataset["schema_version"],
            "window_contract": WINDOW["contract"],
            "runtime_contract": "phase1_opaque_sample_vibration_feature_schema_v6",
            "provider": "openrouter-free",
            "model": "cohere/north-mini-code:free",
            "inference_protocol": "openai_chat_completions",
            "thinking_mode": "not_requested",
            "rotation": rotation,
            "sample_id": sample_id,
            "seed": seed,
            "task_id": task,
            "selected_diagnosis_model_id": "ridge-ovr-v1",
            "validation_model_macro_f1": {"ridge-ovr-v1": 0.6},
            "usage_accounting_contract": USAGE_ACCOUNTING_CONTRACT,
            "replay_missing_score_policy_id": (
                IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID
                if scope == "replay"
                else None
            ),
            "cohort_resume_identity": resume_identity,
            "formal_execution_topology": profile["formal_execution_topology"],
        }
        if graph:
            metadata.update(
                {
                    "arm": "graph",
                    "graph_policy_profile": "full",
                    "benchmark_control_source": dict(BENCHMARK_CONTROL_SOURCE),
                    **P2_IDENTITY,
                }
            )
        else:
            metadata["experiment_profile_id"] = (
                MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            )
        episode = EpisodeSpec(
            episode_id=episode_id,
            task=task_spec,
            scope=DataAccessScope(),
            sample_handle=sample_id,
        )
        write_episode_bundle(
            episode_attempt_directory(
                unit, (rotation, sample_id, task), attempt_index
            ),
            attempt_id=f"attempt_{attempt_index:03d}",
            episode=episode,
            rollout=rollout,
            evaluation=evaluation,
            run_metadata=metadata,
            artifacts={},
        )
        if provider_failure:
            return None
        private_row["submission"] = rollout.submission
        private_row["evaluation"] = evaluation.to_protocol_dict()
        return private_row

    def _populate_arm(
        self,
        name: str,
        *,
        provider_retry: bool = False,
        natural_failure: bool = False,
        max_units: int | None = None,
    ) -> None:
        graph = name.startswith("graph")
        scope = "replay" if name.endswith("replay") else "core"
        rotations = ("rotation_0",) if scope == "replay" else tuple(f"rotation_{index}" for index in range(4))
        tasks = MODULE.REPLAY_TASKS if scope == "replay" else MODULE.CORE_TASKS
        root = self.roots[name]
        first_episode = True
        populated_units = 0
        for seed in (20260808, 20260809, 20260810):
            for rotation in rotations:
                if max_units is not None and populated_units >= max_units:
                    return
                unit = root / f"seed_{seed}" / rotation
                unit.mkdir(parents=True, exist_ok=True)
                fold = self.dataset["split"]["rotations"][int(rotation[-1])]["test"]
                private_rows = []
                for bearing_index, bearing in enumerate(self.dataset["split"]["folds"][fold]):
                    sample_id = f"sample-{seed}-{rotation[-1]}-{bearing_index:02d}"
                    for task in tasks:
                        retry_this = provider_retry and first_episode
                        failure_this = natural_failure and first_episode
                        if retry_this:
                            self._write_attempt(
                                unit=unit,
                                graph=graph,
                                scope=scope,
                                seed=seed,
                                rotation=rotation,
                                bearing=bearing,
                                sample_id=sample_id,
                                task=task,
                                attempt_index=0,
                                provider_failure=True,
                            )
                        row = self._write_attempt(
                            unit=unit,
                            graph=graph,
                            scope=scope,
                            seed=seed,
                            rotation=rotation,
                            bearing=bearing,
                            sample_id=sample_id,
                            task=task,
                            attempt_index=1 if retry_this else 0,
                            natural_failure=failure_this,
                        )
                        assert row is not None
                        private_rows.append(row)
                        first_episode = False
                write_cohort_index(
                    unit / "cohort_index.json",
                    profile=self._manifest(
                        graph=graph,
                        scope=scope,
                        seed=seed,
                        rotation=rotation,
                    ),
                    records=private_rows,
                    status="complete",
                )
                populated_units += 1

    def _populate_generic_core_prefix_46(self) -> None:
        root = self.roots["generic_core"]
        seed = 20260808
        for rotation_index in range(3):
            rotation = f"rotation_{rotation_index}"
            unit = root / f"seed_{seed}" / rotation
            unit.mkdir(parents=True, exist_ok=True)
            fold = self.dataset["split"]["rotations"][rotation_index]["test"]
            records: list[dict] = []
            attempt_ordinal = 0
            limit = 16 if rotation_index < 2 else 14
            for bearing_index, bearing in enumerate(self.dataset["split"]["folds"][fold]):
                sample_id = f"prefix-{rotation_index}-{bearing_index:02d}"
                for task in MODULE.CORE_TASKS:
                    if attempt_ordinal >= limit:
                        break
                    provider_failure = rotation_index == 2 and attempt_ordinal == 13
                    row = self._write_attempt(
                        unit=unit,
                        graph=False,
                        scope="core",
                        seed=seed,
                        rotation=rotation,
                        bearing=bearing,
                        sample_id=sample_id,
                        task=task,
                        provider_failure=provider_failure,
                    )
                    if row is not None:
                        records.append(row)
                    attempt_ordinal += 1
                if attempt_ordinal >= limit:
                    break
            write_cohort_index(
                unit / "cohort_index.json",
                profile=self._manifest(
                    graph=False, scope="core", seed=seed, rotation=rotation
                ),
                records=records,
                status=(
                    "complete"
                    if rotation_index < 2
                    else "provider_failure_incomplete_cohort"
                ),
            )

    @staticmethod
    def _rewrite_unit_topology(unit: Path, topology: dict | None) -> None:
        cohort = read_cohort_index(unit / "cohort_index.json")
        profile = dict(cohort["profile"])
        if topology is None:
            profile.pop("formal_execution_topology", None)
        else:
            profile["formal_execution_topology"] = topology
        for run_path in unit.rglob("run.json"):
            run = json.loads(run_path.read_text(encoding="utf-8"))
            metadata = run["metadata"]
            resume_identity = metadata["cohort_resume_identity"]
            if topology is None:
                metadata.pop("formal_execution_topology", None)
                resume_identity.pop("formal_execution_topology", None)
            else:
                metadata["formal_execution_topology"] = topology
                resume_identity["formal_execution_topology"] = topology
            run_path.write_text(
                json.dumps(run, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        write_cohort_index(
            unit / "cohort_index.json",
            profile=profile,
            records=cohort["records"],
            status=cohort["status"],
        )

    def _build(self):
        return MODULE.build_documents(
            protocol_path=self.protocol_path,
            benchmark_formal_run_stamp=self.formal_run_stamp,
            benchmark_control_protocol_id=(
                MODULE.ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
            ),
            benchmark_control_profile_id=(
                MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            ),
            generic_core_root=self.roots["generic_core"],
            generic_replay_root=self.roots["generic_replay"],
            graph_core_root=self.roots["graph_core"],
            graph_replay_root=self.roots["graph_replay"],
        )

    def test_stable_46_attempt_prefix_is_45_statistical_plus_one_provider_error(self) -> None:
        usage = MODULE.build_parser().format_usage()
        for flag in (
            "--benchmark-formal-run-stamp",
            "--benchmark-control-protocol-id",
            "--benchmark-control-profile-id",
            "--generic-core-root",
            "--generic-replay-root",
            "--graph-core-root",
            "--graph-replay-root",
        ):
            self.assertIn(flag, usage)
            self.assertNotIn(f"[{flag}", usage)
        self._populate_generic_core_prefix_46()
        with patch.object(MODULE, "paired_bearing_bootstrap_deltas", side_effect=AssertionError("bootstrap must stay closed")):
            readiness, result = self._build()
        self.assertFalse(readiness["accepted"])
        self.assertEqual(readiness["evaluator_private_views_read"], 0)
        self.assertEqual(readiness["effect_estimates_emitted"], 0)
        self.assertFalse(readiness["gates"]["bootstrap_permitted"])
        self.assertIsNone(result["arm_summaries"])
        self.assertIsNone(result["graph_state_summaries"])
        self.assertIsNone(result["paired_bearing_bootstrap"])
        generic = readiness["observed"]["generic_core"]
        self.assertEqual(generic["attempt_leaves"], 46)
        self.assertEqual(generic["statistical_outcomes"], 45)
        self.assertEqual(generic["provider_error_attempts"], 1)
        self.assertEqual(generic["unresolved_provider_error_keys"], 1)
        self.assertEqual(readiness["observed"]["graph_core"]["statistical_outcomes"], 0)

    def test_complete_192_and_24_per_arm_unlocks_exact_2000_bearing_bootstrap(self) -> None:
        self._populate_arm("generic_core", provider_retry=True)
        for name in ("graph_core", "generic_replay", "graph_replay"):
            self._populate_arm(name)

        paired_calls = []
        interval_calls = []

        def registered_endpoints(tasks):
            analysis = yaml.safe_load(
                self.protocol_path.read_text(encoding="utf-8")
            )["analysis"]
            return {
                task: [
                    *analysis["task_endpoints"][task],
                    *analysis["rollout_endpoints"],
                ]
                for task in tasks
            }

        def fake_bootstrap(
            control,
            treatment,
            *,
            iterations,
            seed,
            replay_missing_score_policy_id,
        ):
            paired_calls.append(
                (
                    len(control),
                    len(treatment),
                    iterations,
                    seed,
                    replay_missing_score_policy_id,
                )
            )
            tasks = sorted({row["task_id"] for row in control})
            endpoints = registered_endpoints(tasks)
            control_summary = MODULE.aggregate_results(
                control,
                diagnosis_classes=self.dataset["tasks"]["diagnosis"]["labels"],
                replay_missing_score_policy_id=replay_missing_score_policy_id,
            )
            treatment_summary = MODULE.aggregate_results(
                treatment,
                diagnosis_classes=self.dataset["tasks"]["diagnosis"]["labels"],
                replay_missing_score_policy_id=replay_missing_score_policy_id,
            )

            def value(task, metric):
                section, name = metric.split(".", 1)
                control_value = control_summary[task][section][name]
                treatment_value = treatment_summary[task][section][name]
                if control_value is None or treatment_value is None:
                    return None
                return float(treatment_value) - float(control_value)

            return {
                "estimate": {
                    task: {
                        metric: value(task, metric) for metric in endpoints[task]
                    }
                    for task in tasks
                },
                "bearing_bootstrap_95ci": {
                    task: {
                        metric: (
                            None
                            if value(task, metric) is None
                            else [value(task, metric), value(task, metric)]
                        )
                        for metric in endpoints[task]
                    }
                    for task in tasks
                },
                "bearing_bootstrap_valid_replicates": {
                    task: {
                        metric: 0 if value(task, metric) is None else 2000
                        for metric in endpoints[task]
                    }
                    for task in tasks
                },
                "bootstrap_iterations": iterations,
                "seed": seed,
                "direction": "treatment_minus_control",
            }

        def fake_intervals(
            records,
            *,
            iterations,
            seed,
            diagnosis_classes,
            replay_missing_score_policy_id,
        ):
            interval_calls.append(
                (len(records), iterations, seed, replay_missing_score_policy_id)
            )
            summary = MODULE.aggregate_results(
                records,
                diagnosis_classes=diagnosis_classes,
                replay_missing_score_policy_id=replay_missing_score_policy_id,
            )
            endpoints = registered_endpoints(sorted(summary))
            intervals = {}
            valid = {}
            for task, metrics in endpoints.items():
                intervals[task] = {}
                valid[task] = {}
                for metric in metrics:
                    section, name = metric.split(".", 1)
                    value = summary[task][section][name]
                    intervals[task][metric] = (
                        None if value is None else [float(value), float(value)]
                    )
                    valid[task][metric] = 0 if value is None else iterations
            return intervals, valid

        with (
            patch.object(
                MODULE,
                "paired_bearing_bootstrap_deltas",
                side_effect=fake_bootstrap,
            ),
            patch.object(
                MODULE,
                "bearing_bootstrap_intervals",
                side_effect=fake_intervals,
            ),
        ):
            readiness, result = self._build()

        self.assertTrue(readiness["accepted"])
        self.assertEqual(
            paired_calls,
            [
                (192, 192, 2000, 20260820, None),
                (
                    24,
                    24,
                    2000,
                    20260820,
                    IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID,
                ),
            ],
        )
        self.assertEqual(
            interval_calls,
            [
                (192, 2000, 20260820, None),
                (192, 2000, 20260820, None),
                (
                    24,
                    2000,
                    20260820,
                    IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID,
                ),
                (
                    24,
                    2000,
                    20260820,
                    IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID,
                ),
            ],
        )
        self.assertEqual(readiness["evaluator_private_views_read"], 432)
        self.assertEqual(readiness["observed"]["generic_core"]["attempt_leaves"], 193)
        self.assertEqual(readiness["observed"]["generic_core"]["provider_error_attempts"], 1)
        self.assertEqual(readiness["observed"]["generic_core"]["retry_chains"], 1)
        self.assertEqual(readiness["observed"]["generic_core"]["failure_denominator"], 192)
        self.assertTrue(result["accepted"])
        protocol = yaml.safe_load(self.protocol_path.read_text(encoding="utf-8"))
        self.assertEqual(result["frozen_profile"], protocol["frozen_profile"])
        self.assertEqual(
            result["benchmark_control_source"], BENCHMARK_CONTROL_SOURCE
        )
        self.assertEqual(
            result["formal_execution_topology"],
            {
                "benchmark_control": BENCHMARK_FORMAL_EXECUTION_TOPOLOGY,
                "graph_treatment": GRAPH_FORMAL_EXECUTION_TOPOLOGY,
                "shared_benchmark_data_factory": (
                    BENCHMARK_FORMAL_EXECUTION_TOPOLOGY
                ),
            },
        )
        self.assertEqual(
            result["protocol_identity"],
            {
                "schema_version": protocol["schema_version"],
                "experiment_id": protocol["experiment_id"],
            },
        )
        self.assertEqual(result["registered_design"], protocol["registered_design"])
        self.assertEqual(result["analysis"], protocol["analysis"])
        self.assertEqual(result["registered_denominators"], {"core_per_arm": 192, "replay_per_arm": 24})
        self.assertEqual(result["paired_bearing_bootstrap"]["replay"]["bootstrap_iterations"], 2000)
        self.assertEqual(result["primary_endpoint"]["metric"], "task.average_precision")
        for arm in ("control", "treatment"):
            replay = result["arm_summaries"]["replay"][arm]
            task = replay["summary"]["online_replay_monitoring"]["task"]
            self.assertEqual(task["assigned_windows"], 72)
            self.assertEqual(task["submitted_windows"], 0)
            self.assertEqual(task["missing_assigned_scores"], 72)
            self.assertEqual(task["score_coverage"], 0.0)
            self.assertEqual(task["average_precision"], 0.0)
            self.assertEqual(
                replay["replay_missing_score_policy_id"],
                IMPLEMENTED_FORMAL_REPLAY_MISSING_SCORE_POLICY_ID,
            )
        core_table, replay_table = render_tables_from_combined_result(
            result=result,
        )
        self.assertEqual(
            result["graph_state_summaries"]["core"][
                "cold_start_fault_diagnosis"
            ]["episodes"],
            96,
        )
        self.assertEqual(
            result["graph_state_summaries"]["replay"][
                "online_replay_monitoring"
            ]["episodes"],
            24,
        )
        self.assertIn("| Task primary | Diagnosis Macro-F1 |", core_table)
        self.assertIn("| Primary | Monitoring Average Precision |", replay_table)
        self.assertIn("| Rollout | Grounded completion |", replay_table)

        result_path = self.root / "accepted_result.json"
        result_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        manuscript_path = self.root / "main.md"
        manuscript_path.write_text(
            "<!-- GRAPH_CORE_PRIMARY_COMPACT:BEGIN -->\ncore pending\n"
            "<!-- GRAPH_CORE_PRIMARY_COMPACT:END -->\n"
            "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:BEGIN -->\nreplay pending\n"
            "<!-- GRAPH_MONITOR_PRIMARY_COMPACT:END -->\n"
            "<!-- GRAPH_FORMAL_FIGURES:BEGIN -->\nfigures pending\n"
            "<!-- GRAPH_FORMAL_FIGURES:END -->\n",
            encoding="utf-8",
        )
        publication = argparse.Namespace(
            protocol=self.protocol_path,
            combined_result=result_path,
            expected_benchmark_formal_run_stamp=self.formal_run_stamp,
            core_state_summary=None,
            state_summary=None,
            core_comparison_figure=None,
            monitor_mechanism_json=None,
            monitor_mechanism_figure=None,
            output=self.root / "accepted_table.md",
            core_figure_output=self.root / "accepted_core.svg",
            state_json_output=self.root / "accepted_states.json",
            state_table_output=self.root / "accepted_states.md",
            manuscript=manuscript_path,
        )
        publication_protocol = yaml.safe_load(
            self.protocol_path.read_text(encoding="utf-8")
        )
        publication_protocol["outputs"]["result"] = str(result_path)
        declared_publication = publication_protocol["outputs"][
            "accepted_publication"
        ]
        declared_publication.update(
            {
                "table": str(publication.output),
                "core_figure": str(publication.core_figure_output),
                "state_json": str(publication.state_json_output),
                "state_table": str(publication.state_table_output),
                "manuscript": str(publication.manuscript),
            }
        )
        self.protocol_path.write_text(
            yaml.safe_dump(publication_protocol, sort_keys=False),
            encoding="utf-8",
        )
        write_table(publication)
        for path in (
            publication.output,
            publication.core_figure_output,
            publication.state_json_output,
            publication.state_table_output,
            publication.manuscript,
        ):
            self.assertTrue(path.is_file())
        self.assertIn(
            "No descriptive replay mechanism case is admitted",
            publication.manuscript.read_text(encoding="utf-8"),
        )

    def test_protocol_replay_policy_drift_fails_before_bootstrap(self) -> None:
        protocol = yaml.safe_load(self.protocol_path.read_text(encoding="utf-8"))
        protocol["analysis"]["replay_missing_score_policy_id"] = "wrong-policy"
        self.protocol_path.write_text(
            yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8"
        )
        with patch.object(
            MODULE,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                MODULE.FinalizationError,
                "replay missing-score policy differs",
            ):
                self._build()

    def test_protocol_bootstrap_seed_drift_fails_before_bootstrap(self) -> None:
        protocol = yaml.safe_load(self.protocol_path.read_text(encoding="utf-8"))
        protocol["analysis"]["bootstrap"]["seed"] = 20260821
        self.protocol_path.write_text(
            yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8"
        )
        with patch.object(
            MODULE,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                MODULE.FinalizationError,
                "bootstrap seed must be exactly 20260820",
            ):
                self._build()

    def test_cross_stamp_graph_root_is_rejected_before_pairing(self) -> None:
        other_stamp = "20260902T010203Z"
        self.roots["graph_core"] = (
            self.root
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
            / "graph_core_primary"
            / MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
            / f"run_{other_stamp}"
        )
        with self.assertRaisesRegex(
            MODULE.FinalizationError,
            "graph_core root belongs to a different formal run stamp",
        ):
            self._build()

    def test_missing_formal_execution_topology_fails_before_bootstrap(self) -> None:
        self._populate_arm("graph_core", max_units=1)
        unit = self.roots["graph_core"] / "seed_20260808" / "rotation_0"
        self._rewrite_unit_topology(unit, None)
        with patch.object(
            MODULE,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                MODULE.FinalizationError,
                "formal_execution_topology.*must be a mapping",
            ):
                self._build()

    def test_cross_unit_formal_execution_topology_drift_fails_before_bootstrap(self) -> None:
        self._populate_generic_core_prefix_46()
        unit = self.roots["generic_core"] / "seed_20260808" / "rotation_1"
        drifted = dict(BENCHMARK_FORMAL_EXECUTION_TOPOLOGY)
        drifted["benchmark_revision"] = "d" * 40
        self._rewrite_unit_topology(unit, drifted)
        with patch.object(
            MODULE,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                MODULE.FinalizationError,
                "formal_execution_topology differs across units",
            ):
                self._build()

    def test_generic_graph_shared_topology_drift_fails_before_bootstrap(self) -> None:
        self._populate_arm("generic_core", max_units=1)
        self._populate_arm("graph_core", max_units=1)
        unit = self.roots["graph_core"] / "seed_20260808" / "rotation_0"
        benchmark_drift = dict(BENCHMARK_FORMAL_EXECUTION_TOPOLOGY)
        benchmark_drift["benchmark_revision"] = "d" * 40
        graph_drift = json.loads(json.dumps(GRAPH_FORMAL_EXECUTION_TOPOLOGY))
        graph_drift["benchmark_formal_execution_topology"] = benchmark_drift
        graph_drift["source_revisions"]["benchmark"] = "d" * 40
        self._rewrite_unit_topology(unit, graph_drift)
        with patch.object(
            MODULE,
            "paired_bearing_bootstrap_deltas",
            side_effect=AssertionError("bootstrap must stay closed"),
        ):
            with self.assertRaisesRegex(
                MODULE.FinalizationError,
                "shared Benchmark/Data Factory formal_execution_topology differs",
            ):
                self._build()

    def test_retry_gap_fails_closed(self) -> None:
        self._populate_arm("generic_core")
        unit = self.roots["generic_core"] / "seed_20260808" / "rotation_0"
        cohort = read_cohort_index(unit / "cohort_index.json")
        first = cohort["records"][0]
        self._write_attempt(
            unit=unit,
            graph=False,
            scope="core",
            seed=20260808,
            rotation="rotation_0",
            bearing=str(first["bearing_id"]),
            sample_id=str(first["sample_id"]),
            task=str(first["task_id"]),
            attempt_index=2,
            provider_failure=True,
        )
        write_cohort_index(
            unit / "cohort_index.json",
            profile=cohort["profile"],
            records=cohort["records"],
            status="complete",
        )
        with self.assertRaisesRegex(MODULE.FinalizationError, "retry indices are not contiguous"):
            self._build()

    def test_natural_nonprovider_terminal_failure_remains_in_192_denominator(self) -> None:
        self._populate_arm("generic_core", natural_failure=True)

        readiness, _result = self._build()
        gate = readiness["observed"]["generic_core"]
        self.assertTrue(gate["accepted"])
        self.assertEqual(gate["statistical_outcomes"], 192)
        self.assertEqual(gate["failure_denominator"], 192)
        self.assertEqual(gate["nonprovider_terminal_failures_retained"], 1)

    def test_second_replace_failure_rolls_back_readiness_and_result(self) -> None:
        readiness_path = self.root / "outputs" / "readiness.json"
        result_path = self.root / "outputs" / "result.json"
        readiness_path.parent.mkdir(parents=True)
        readiness_path.write_text("old readiness\n", encoding="utf-8")
        result_path.write_text("old result\n", encoding="utf-8")
        originals = {
            readiness_path: readiness_path.read_bytes(),
            result_path: result_path.read_bytes(),
        }
        real_replace = MODULE.os.replace
        replacement_count = 0

        def fail_second_replace(source: object, destination: object) -> None:
            nonlocal replacement_count
            replacement_count += 1
            if replacement_count == 2:
                raise OSError("simulated second replace failure")
            real_replace(source, destination)

        argv = [
            "--benchmark-formal-run-stamp",
            self.formal_run_stamp,
            "--benchmark-control-protocol-id",
            MODULE.ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
            "--benchmark-control-profile-id",
            MODULE.ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
            "--generic-core-root",
            str(self.roots["generic_core"]),
            "--generic-replay-root",
            str(self.roots["generic_replay"]),
            "--graph-core-root",
            str(self.roots["graph_core"]),
            "--graph-replay-root",
            str(self.roots["graph_replay"]),
            "--readiness-output",
            str(readiness_path),
            "--result-output",
            str(result_path),
        ]
        documents = ({"accepted": False}, {"effect_estimates_emitted": 0})
        with (
            patch.object(MODULE, "build_documents", return_value=documents),
            patch.object(MODULE.os, "replace", side_effect=fail_second_replace),
        ):
            with self.assertRaisesRegex(OSError, "simulated second replace failure"):
                MODULE.main(argv)

        self.assertEqual(replacement_count, 2)
        for path, original in originals.items():
            self.assertEqual(path.read_bytes(), original)
        self.assertEqual(list(readiness_path.parent.glob(".*.tmp")), [])

    def test_publication_outputs_reject_aliases_and_immutable_inputs(self) -> None:
        output_root = self.root / "outputs"
        output_root.mkdir()

        def arguments(readiness: Path, result: Path) -> argparse.Namespace:
            return argparse.Namespace(
                protocol=self.protocol_path,
                generic_core_root=self.roots["generic_core"],
                generic_replay_root=self.roots["generic_replay"],
                graph_core_root=self.roots["graph_core"],
                graph_replay_root=self.roots["graph_replay"],
                readiness_output=readiness,
                result_output=result,
            )

        first = output_root / "same-inode-a.json"
        second = output_root / "same-inode-b.json"
        first.write_text("old\n", encoding="utf-8")
        os.link(first, second)
        with self.assertRaisesRegex(
            MODULE.FinalizationError,
            "distinct non-hardlinked paths",
        ):
            MODULE._validate_publication_output_paths(
                arguments(first, second), dataset_path=self.dataset_path
            )

        protocol_alias = output_root / "protocol-alias.json"
        os.link(self.protocol_path, protocol_alias)
        with self.assertRaisesRegex(
            MODULE.FinalizationError,
            "must not overwrite protocol, dataset, or cohort_index",
        ):
            MODULE._validate_publication_output_paths(
                arguments(protocol_alias, output_root / "result.json"),
                dataset_path=self.dataset_path,
            )

        immutable_root = self.roots["generic_core"]
        cohort_index = immutable_root / "seed_20260808/rotation_0/cohort_index.json"
        cohort_index.parent.mkdir(parents=True)
        cohort_index.write_text("{}\n", encoding="utf-8")
        cohort_alias = output_root / "cohort-index-alias.json"
        os.link(cohort_index, cohort_alias)
        with self.assertRaisesRegex(
            MODULE.FinalizationError,
            "must not overwrite protocol, dataset, or cohort_index",
        ):
            MODULE._validate_publication_output_paths(
                arguments(cohort_alias, output_root / "result.json"),
                dataset_path=self.dataset_path,
            )

        with self.assertRaisesRegex(
            MODULE.FinalizationError,
            "outside all four external immutable roots",
        ):
            MODULE._validate_publication_output_paths(
                arguments(
                    self.roots["graph_core"] / "publication.json",
                    output_root / "result.json",
                ),
                dataset_path=self.dataset_path,
            )

    def test_legacy_phmskills_e0_and_e1_clis_refuse_active_use(self) -> None:
        for script in (
            "scripts/analyze_p2_e0_adapter_equivalence.py",
            "scripts/audit_p2_e1_primary_readiness.py",
        ):
            completed = subprocess.run(
                [sys.executable, script],
                cwd=MODULE.ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 2)
            self.assertIn("superseded PHMskills-derived", completed.stderr)
            self.assertIn("active use is refused", completed.stderr)


if __name__ == "__main__":
    unittest.main()
