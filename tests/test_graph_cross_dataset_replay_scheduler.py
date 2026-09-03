from __future__ import annotations

import contextlib
import copy
import io
import json
import sys
import tempfile
import unittest
from collections import Counter
from collections.abc import Mapping
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_graph_experiment import build_parser as build_runner_parser  # noqa: E402
from schedule_graph_cross_dataset_replay import (  # noqa: E402
    ContractError,
    DATASET_ID,
    DEFAULT_PROTOCOL,
    LEGACY_PROTOCOL,
    PROFILE_ID,
    SUPERSEDED_PROTOCOL,
    audit_candidate,
    build_manifest,
    load_protocol,
    main,
    validate_protocol,
)


def _load(path: Path) -> dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError(f"expected mapping: {path}")
    return payload


class GraphCrossDatasetReplaySchedulerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_protocol(DEFAULT_PROTOCOL)

    def test_v3_is_default_and_binds_ottawa_generic_base_cohort(self) -> None:
        self.assertEqual(
            DEFAULT_PROTOCOL.name, "graph_cross_dataset_replay_protocol_v3.yaml"
        )
        self.assertNotEqual(DEFAULT_PROTOCOL, SUPERSEDED_PROTOCOL)
        validate_protocol(self.protocol)
        self.assertEqual(
            self.protocol["schema_version"],
            "graph_cross_dataset_replay_protocol_v3",
        )
        self.assertEqual(
            self.protocol["extends_protocol"],
            "graph_cross_dataset_replay_protocol_v2.yaml",
        )
        self.assertEqual(
            self.protocol["dataset_registration"]["dataset_id"], DATASET_ID
        )
        self.assertEqual(
            self.protocol["formal_execution"]["experiment_profile_id"],
            PROFILE_ID,
        )
        self.assertEqual(
            self.protocol["current_schedule"]["expected_runner_commands"], 18
        )
        self.assertEqual(
            self.protocol["current_schedule"]["expected_episode_bundles"], 72
        )
        self.assertEqual(
            self.protocol["current_schedule"]["expected_matched_episode_pairs"],
            36,
        )
        self.assertEqual(
            self.protocol["current_schedule"]["expected_assigned_windows_across_arms"],
            216,
        )
        self.assertFalse(
            self.protocol["scope"]["monitor_or_revise_event_branch_estimand"]
        )
        self.assertFalse(
            self.protocol["scope"]["event_f1_or_detection_delay_estimand"]
        )

    def test_v1_and_v2_are_non_executable_records(self) -> None:
        legacy = _load(LEGACY_PROTOCOL)
        superseded = _load(SUPERSEDED_PROTOCOL)
        with self.assertRaisesRegex(ContractError, "superseded_phmskills_base"):
            validate_protocol(legacy)
        with self.assertRaisesRegex(ContractError, "zero-eligible"):
            validate_protocol(superseded)
        with self.assertRaisesRegex(ContractError, "launch forbidden"):
            build_manifest(LEGACY_PROTOCOL)
        with self.assertRaisesRegex(ContractError, "launch forbidden"):
            build_manifest(SUPERSEDED_PROTOCOL)

    def test_accepted_ottawa_source_and_runtime_emit_exact_dry_schedule(self) -> None:
        manifest = build_manifest(DEFAULT_PROTOCOL, run_stamp="20260902T000000Z")
        self.assertEqual(
            manifest["schema_version"], "graph_cross_dataset_replay_schedule_v3"
        )
        self.assertEqual(manifest["authority_version"], "v3_ottawa_generic_base")
        self.assertEqual(manifest["eligible_external_dataset_ids"], [DATASET_ID])
        self.assertEqual(manifest["eligible_external_dataset_count"], 1)
        self.assertTrue(manifest["external_outcome_target_ready"])
        self.assertTrue(manifest["runtime_readiness"]["ready"])
        self.assertTrue(manifest["schedule_ready"])
        self.assertEqual(manifest["schedule_blocked_reasons"], [])
        self.assertEqual(manifest["unit_count"], 18)
        self.assertEqual(manifest["arm_unit_counts"], {"reactive": 9, "graph": 9})
        self.assertEqual(manifest["expected_episode_bundles"], 72)
        self.assertEqual(manifest["expected_matched_episode_pairs"], 36)
        self.assertEqual(manifest["expected_assigned_windows_across_arms"], 216)

        audit = manifest["candidate_audits"][0]
        self.assertEqual(audit["expected_dataset_id"], DATASET_ID)
        self.assertTrue(audit["eligible"])
        self.assertTrue(audit["outcome_target_available"])
        self.assertTrue(all(row["passed"] for row in audit["required_checks"]))

    def test_provider_free_preflight_is_ready_but_same_day_retry_gate_stays_closed(self) -> None:
        manifest = build_manifest(DEFAULT_PROTOCOL)
        self.assertTrue(manifest["analysis_readiness"]["ready"])
        self.assertEqual(
            manifest["analysis_readiness"]["analyzer"],
            "scripts/analyze_graph_cross_dataset_replay.py",
        )
        self.assertEqual(
            manifest["analysis_readiness"]["missing_source_fragments"], []
        )
        self.assertTrue(manifest["provider_free_preflight_ready"])
        self.assertFalse(manifest["activation_ready"])
        self.assertFalse(manifest["formal_launch_prerequisites_satisfied"])
        self.assertFalse(manifest["formal_launch_allowed_by_this_scheduler"])
        self.assertEqual(
            manifest["activation_blocked_reasons"],
            ["same_day_north_retry_forbidden_after_http_429_20260902"],
        )
        self.assertEqual(manifest["unit_count"], 18)

    def test_all_18_commands_parse_and_preserve_registered_identity(self) -> None:
        manifest = build_manifest(
            DEFAULT_PROTOCOL,
            run_stamp="20260902T000000Z",
            python_executable="python",
        )
        outputs: set[str] = set()
        partitions = Counter()
        for unit in manifest["units"]:
            command = unit["command"]
            args = build_runner_parser().parse_args(command[2:])
            self.assertEqual(args.dataset_id, DATASET_ID)
            self.assertEqual(args.data_backend, "csv_directory")
            self.assertEqual(args.experiment_profile_id, PROFILE_ID)
            self.assertEqual(args.tasks, ["online_replay_monitoring"])
            self.assertEqual(args.test_samples_per_bearing, 3)
            self.assertIsNone(args.dynamic_protocol)
            self.assertNotIn("--public-sequence-id", command)
            self.assertNotIn("--horizon", command)
            self.assertNotIn("--benchmark-formal-run-stamp", command)
            self.assertNotIn(unit["output"], outputs)
            outputs.add(unit["output"])
            partitions[unit["matched_pair_partition"]] += 1
        self.assertEqual(len(outputs), 18)
        self.assertEqual(set(partitions.values()), {2})
        self.assertEqual(len(partitions), 9)

    def test_schedule_is_deterministic_and_provider_free(self) -> None:
        first = build_manifest(DEFAULT_PROTOCOL, run_stamp="DRYRUN")
        second = build_manifest(DEFAULT_PROTOCOL, run_stamp="DRYRUN")
        self.assertEqual(first, second)
        self.assertEqual(first["provider_calls_made"], 0)
        self.assertFalse(first["runner_invoked"])
        self.assertFalse(first["raw_signals_read"])
        self.assertFalse(first["private_targets_read"])
        self.assertFalse(first["environment_values_read"])
        self.assertEqual(first["filesystem_writes_made"], 0)

    def test_source_target_drift_fails_closed(self) -> None:
        candidate = copy.deepcopy(self.protocol["candidate_sources"][0])
        source = _load((ROOT / candidate["protocol_path"]).resolve())
        source["tasks"]["monitoring"]["labels"] = {
            "healthy": 0,
            "developing_fault": 0,
            "faulty": 1,
        }
        audited = audit_candidate(candidate, source)
        self.assertFalse(audited["outcome_target_available"])
        self.assertFalse(audited["eligible"])
        self.assertEqual(
            audited["blocked_reasons"], ["no_legal_external_outcome_target"]
        )

    def test_missing_runner_implementation_fragment_suppresses_all_units(self) -> None:
        source = (ROOT / "scripts/run_graph_experiment.py").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            runner = Path(directory) / "runner.py"
            runner.write_text(source.replace("LocalCSVPhase1DataPort", "CSVPort"), encoding="utf-8")
            manifest = build_manifest(DEFAULT_PROTOCOL, runner_override=runner)
        self.assertFalse(manifest["runtime_readiness"]["ready"])
        self.assertIn(
            "LocalCSVPhase1DataPort",
            manifest["runtime_readiness"]["missing_source_fragments"],
        )
        self.assertFalse(manifest["schedule_ready"])
        self.assertEqual(manifest["unit_count"], 0)

    def test_strict_preflight_distinguishes_source_from_full_activation(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            eligible_code = main(["--dry-run", "--require-eligible"])
        self.assertEqual(eligible_code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["unit_count"], 18)

        with contextlib.redirect_stdout(io.StringIO()):
            ready_code = main(["--dry-run", "--require-ready"])
        self.assertEqual(ready_code, 4)

    def test_non_dry_run_invocation_is_refused(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main([])
        self.assertEqual(raised.exception.code, 2)

    def test_validation_rejects_generic_base_identity_drift(self) -> None:
        protocol = copy.deepcopy(self.protocol)
        protocol["agent_identity"]["control"][
            "direct_base_class"
        ] = "phm_skills.PHMSkillsAgent"
        with self.assertRaisesRegex(ContractError, "Generic-base control identity drift"):
            validate_protocol(protocol)

    def test_validation_rejects_event_metric_relabelling(self) -> None:
        protocol = copy.deepcopy(self.protocol)
        protocol["scope"]["event_f1_or_detection_delay_estimand"] = True
        with self.assertRaisesRegex(ContractError, "event metrics"):
            validate_protocol(protocol)


if __name__ == "__main__":
    unittest.main()
