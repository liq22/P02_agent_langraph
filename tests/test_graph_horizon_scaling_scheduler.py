from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from scripts.schedule_graph_horizon_scaling import (
    ContractError,
    DEFAULT_PROTOCOL,
    LEGACY_PROTOCOL,
    ROOT,
    SUPERSEDED_PROTOCOL,
    _load_protocol_yaml,
    _load_source_yaml,
    build_manifest,
    build_units,
    main,
    runtime_readiness,
    validate_projection,
)
from scripts.run_graph_dynamic_formal_v2 import main as formal_runner_main


SOURCE_PATH = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"


class GraphHorizonScalingSchedulerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = _load_protocol_yaml(DEFAULT_PROTOCOL)
        cls.source = _load_source_yaml(SOURCE_PATH)

    def test_v1_is_superseded_and_cannot_be_scheduled(self) -> None:
        legacy = yaml.safe_load(LEGACY_PROTOCOL.read_text(encoding="utf-8"))
        self.assertEqual(legacy["status"], "superseded_phmskills_base")
        self.assertEqual(legacy["formal_launch"], "forbidden")
        self.assertEqual(legacy["superseded_by"], SUPERSEDED_PROTOCOL.name)
        with self.assertRaisesRegex(ContractError, "schema_version mismatch"):
            build_manifest(LEGACY_PROTOCOL)
        with self.assertRaisesRegex(ContractError, "schema_version mismatch"):
            build_manifest(SUPERSEDED_PROTOCOL)

    def test_projection_binds_task_primary_dynamic_v3_authority(self) -> None:
        validate_projection(self.protocol, self.source)
        self.assertEqual(
            self.protocol["authority"]["source_dynamic_protocol"],
            "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml",
        )
        identity = self.protocol["identity_contract"]
        self.assertEqual(identity["p2_experiment_id"], "p2_graph_vs_generic_llm_v1")
        self.assertEqual(
            identity["matched_control_id"], "benchmark_generic_llm_tool_agent_v1"
        )
        self.assertEqual(identity["control_agent_id"], "reactive-sequential-agent")
        self.assertEqual(identity["treatment_agent_id"], "graph-decision-agent")
        self.assertFalse(identity["phmskills_runtime_or_catalog_allowed"])
        self.assertEqual(
            self.protocol["matched_cells"]["shared"]["runtime_contract"],
            "phase1_graph_dynamic_generic_ablation_v3",
        )
        self.assertEqual(
            self.protocol["budgets"]["by_horizon"],
            self.source["budgets"]["by_horizon"],
        )

    def test_current_manifest_registers_144_ready_dry_run_commands(self) -> None:
        manifest = build_manifest(DEFAULT_PROTOCOL)
        self.assertEqual(manifest["schema_version"], "graph_horizon_scaling_schedule_v3")
        self.assertEqual(manifest["unit_count"], 144)
        self.assertEqual(len({unit["unit_id"] for unit in manifest["units"]}), 144)
        self.assertEqual(len({unit["output_root"] for unit in manifest["units"]}), 144)
        self.assertTrue(manifest["runtime_integration"]["ready"])
        self.assertEqual(
            manifest["runtime_integration"]["missing_source_implementation_flags"],
            [],
        )
        self.assertEqual(manifest["commands_emitted"], 144)
        self.assertEqual(manifest["commands_suppressed"], 0)
        self.assertTrue(
            all(
                unit["argv"][:2]
                == ["python", "scripts/run_graph_dynamic_formal_v2.py"]
                and unit["command"] is not None
                for unit in manifest["units"]
            )
        )
        self.assertIn("graph_dynamic_ablation_v3", manifest["units"][0]["output_root"])
        self.assertNotIn("graph_dynamic_ablation_v2", manifest["units"][0]["output_root"])
        self.assertNotIn("graph_dynamic_ablation_v1", manifest["units"][0]["output_root"])

    def test_ready_projection_commands_explicitly_freeze_zero_prices(self) -> None:
        source = copy.deepcopy(self.source)
        source["implementation_status"]["formal_runner_implemented"] = True
        required_flags = self.protocol["runtime_projection"]["required_runner_flags"]
        identities = self.protocol["runtime_projection"]["required_runner_identity_literals"]
        runner_text = "\n".join(
            ["parser = object()"]
            + [f'parser.add_argument("{flag}")' for flag in required_flags]
            + [repr(identity) for identity in identities]
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = Path(directory) / "runner.py"
            runner.write_text(runner_text, encoding="utf-8")
            readiness = runtime_readiness(self.protocol, source, runner)
        self.assertTrue(readiness["ready"], readiness["blocked_reasons"])
        units = build_units(self.protocol, source, emit_commands=readiness["ready"])
        self.assertEqual(len(units), 144)
        for unit in (units[0], units[1], units[-1]):
            argv = unit["argv"]
            self.assertIsInstance(argv, list)
            self.assertEqual(
                argv[argv.index("--input-usd-per-million") + 1], "0.0"
            )
            self.assertEqual(
                argv[argv.index("--output-usd-per-million") + 1], "0.0"
            )
            self.assertIn("--dynamic-protocol", argv)
            self.assertEqual(
                argv[argv.index("--dynamic-protocol") + 1],
                "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml",
            )
            self.assertNotIn(".env", unit["command"])
            self.assertNotIn("bearing_id", unit["command"])

    def test_emitted_horizon_command_passes_provider_free_formal_validation(self) -> None:
        manifest = build_manifest(DEFAULT_PROTOCOL)
        argv = manifest["units"][0]["argv"]
        self.assertIsInstance(argv, list)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(formal_runner_main(argv[2:] + ["--validate-only"]), 0)
        contract = json.loads(stdout.getvalue())
        self.assertEqual(contract["registered_unit_count"], 240)
        self.assertFalse(contract["provider_calls_performed"])
        self.assertFalse(contract["environment_values_read"])
        self.assertFalse(contract["probe_evidence_read"])
        self.assertFalse(contract["filesystem_writes_performed"])

    def test_schedule_is_matched_nested_and_failure_complete(self) -> None:
        units = build_units(self.protocol, self.source)
        self.assertEqual(len(units), 144)
        pairs = {
            (
                unit["key"]["seed"],
                unit["key"]["rotation"],
                unit["key"]["public_sequence_id"],
                unit["key"]["horizon"],
            )
            for unit in units
        }
        self.assertEqual(len(pairs), 72)
        for pair in pairs:
            cells = {
                unit["key"]["cell"]
                for unit in units
                if (
                    unit["key"]["seed"],
                    unit["key"]["rotation"],
                    unit["key"]["public_sequence_id"],
                    unit["key"]["horizon"],
                )
                == pair
            }
            self.assertEqual(cells, {"reactive", "graph_full"})
        self.assertEqual(
            self.protocol["sequence_contract"]["construction"],
            "sequence_h = master_sequence[0:h]",
        )
        denominator = self.protocol["failure_and_denominator_contract"]
        for status in ("failed", "partial", "budget_exhausted"):
            self.assertIn(status, denominator["retain_terminal_statuses"])
        self.assertEqual(
            denominator["non_provider_failure_policy"],
            "retain_episode_and_all_assigned_windows_in_denominator",
        )
        self.assertFalse(self.protocol["statistics"]["pool_episode_rows_across_horizons"])
        self.assertFalse(
            self.protocol["statistics"]["treat_nested_horizons_as_independent_samples"]
        )
        primary = self.protocol["metrics"]["primary"]
        self.assertEqual(
            primary["name"], "target_adverse_window_average_precision"
        )
        self.assertEqual(
            primary["missing_score_policy_id"],
            "phase1_replay_target_adverse_missing_score_v1",
        )
        self.assertEqual(self.protocol["metrics"]["general_rollout_role"], "secondary")
        self.assertEqual(
            self.protocol["statistics"]["per_bearing_average_precision"],
            "forbidden",
        )
        self.assertEqual(
            self.protocol["statistics"]["exact_paired_permutation"],
            "all_256_matched_bearing_cluster_arm_swaps_with_metric_recomputation",
        )

    def test_dry_run_is_deterministic_provider_free_and_strict_mode_passes(self) -> None:
        first = build_manifest(DEFAULT_PROTOCOL)
        second = build_manifest(DEFAULT_PROTOCOL)
        self.assertEqual(first, second)
        self.assertEqual(first["provider_calls_made"], 0)
        self.assertFalse(first["runner_invoked"])
        self.assertFalse(first["environment_values_read"])
        self.assertEqual(first["filesystem_writes_made"], 0)
        self.assertFalse(first["formal_launch_allowed_by_this_scheduler"])

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            exit_code = main(["--dry-run"])
        self.assertEqual(exit_code, 0)
        emitted = json.loads(stdout.getvalue())
        self.assertTrue(emitted["runtime_integration"]["ready"])
        self.assertEqual(emitted["commands_emitted"], 144)

        with contextlib.redirect_stdout(io.StringIO()):
            exit_code = main(["--dry-run", "--require-runtime-ready"])
        self.assertEqual(exit_code, 0)

    def test_non_dry_run_invocation_is_refused(self) -> None:
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as raised:
                main([])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
