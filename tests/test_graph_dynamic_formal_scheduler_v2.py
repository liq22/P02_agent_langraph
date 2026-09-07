from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from scripts.analyze_graph_dynamic_formal import expected_units, unit_root
from scripts.schedule_graph_dynamic_formal_v2 import (
    DEFAULT_PROTOCOL,
    ROOT,
    ScheduleContractError,
    build_manifest,
    build_units,
    load_protocol,
    main,
    runtime_readiness,
    validate_protocol,
)


class GraphDynamicFormalSchedulerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_protocol(DEFAULT_PROTOCOL)

    def test_protocol_declares_complete_provider_free_scheduler_and_runner(self) -> None:
        implementation = self.protocol["implementation_status"]
        self.assertTrue(implementation["formal_matrix_scheduler_implemented"])
        self.assertTrue(implementation["formal_runner_implemented"])
        scheduler = self.protocol["formal_scheduler"]
        self.assertEqual(
            scheduler["schema_version"], "graph_dynamic_formal_schedule_v3"
        )
        self.assertEqual(scheduler["mode"], "provider_free_dry_run_only")
        for field in (
            "provider_calls_allowed",
            "runner_invocation_allowed",
            "environment_value_reads_allowed",
            "filesystem_writes_allowed",
        ):
            self.assertFalse(scheduler[field])
        validate_protocol(self.protocol)

    def test_manifest_emits_all_240_registered_units_deterministically(self) -> None:
        first = build_manifest(DEFAULT_PROTOCOL)
        second = build_manifest(DEFAULT_PROTOCOL)
        self.assertEqual(first, second)
        self.assertEqual(first["unit_count"], 240)
        self.assertEqual(first["planned_commands"], 240)
        self.assertEqual(first["unique_output_root_count"], 240)
        self.assertEqual(len({unit["unit_id"] for unit in first["units"]}), 240)
        self.assertEqual(
            len(
                {
                    tuple(unit["key"][name] for name in (
                        "seed",
                        "rotation",
                        "public_sequence_id",
                        "horizon",
                        "cell",
                    ))
                    for unit in first["units"]
                }
            ),
            240,
        )
        self.assertEqual(
            first["registered_contrast_unit_references"],
            {
                "P2-E2": 144,
                "P2-E3": 48,
                "P2-E4": 48,
                "P2-E5": 48,
                "P2-E6": 48,
                "P2-E7": 72,
            },
        )

    def test_units_match_analyzer_roots_and_exact_cell_denominators(self) -> None:
        scheduled = build_units(self.protocol)
        analyzed = expected_units(self.protocol)
        scheduled_by_key = {
            (
                unit["key"]["seed"],
                unit["key"]["rotation"],
                unit["key"]["public_sequence_id"],
                unit["key"]["horizon"],
                unit["key"]["cell"],
            ): unit
            for unit in scheduled
        }
        self.assertEqual(set(scheduled_by_key), {unit.key for unit in analyzed})
        formal_root = Path(self.protocol["output_contract"]["formal_root"])
        for analyzed_unit in analyzed:
            self.assertEqual(
                scheduled_by_key[analyzed_unit.key]["output_root"],
                unit_root(formal_root, analyzed_unit).as_posix(),
            )
        by_cell = Counter(unit["key"]["cell"] for unit in scheduled)
        self.assertEqual(by_cell["reactive"], 72)
        self.assertEqual(by_cell["graph_full"], 72)
        self.assertEqual(set(by_cell.values()), {24, 72})
        self.assertEqual(
            Counter(unit["key"]["horizon"] for unit in scheduled),
            {3: 48, 6: 48, 12: 144},
        )

    def test_each_planned_command_has_one_registered_assignment_and_zero_price(self) -> None:
        for unit in build_units(self.protocol):
            argv = unit["planned_argv"]
            assignment = unit["assignment"]
            for flag in ("--arm", "--graph-profile", "--horizon", "--output"):
                self.assertEqual(argv.count(flag), 1)
            self.assertEqual(argv[argv.index("--arm") + 1], assignment["arm"])
            self.assertEqual(
                argv[argv.index("--graph-profile") + 1],
                assignment["graph_profile"],
            )
            self.assertEqual(
                int(argv[argv.index("--horizon") + 1]), assignment["horizon"]
            )
            self.assertEqual(
                argv[argv.index("--input-usd-per-million") + 1], "0.0"
            )
            self.assertEqual(
                argv[argv.index("--output-usd-per-million") + 1], "0.0"
            )
            self.assertEqual(
                argv[argv.index("--dynamic-protocol") + 1],
                "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml",
            )
            self.assertEqual(argv[argv.index("--output") + 1], unit["output_root"])
            self.assertNotIn("graph_dynamic_ablation_v1", unit["output_root"])
            self.assertNotIn(".env", unit["planned_command"])
            self.assertNotIn("bearing_id", unit["planned_command"])
            self.assertEqual(
                unit["generic_base_identity"]["base_agent_class"],
                "phm_agent_benchmark.phase1.GenericLLMToolAgent",
            )
            self.assertFalse(
                unit["generic_base_identity"][
                    "legacy_phmskills_superclass_allowed"
                ]
            )

    def test_real_cross_file_proof_makes_commands_ready_without_invocation(self) -> None:
        readiness = runtime_readiness(self.protocol)
        self.assertTrue(readiness["ready"])
        self.assertEqual(readiness["missing_runner_flags"], [])
        self.assertEqual(readiness["missing_identity_literals"], [])
        self.assertEqual(readiness["invalid_identity_proof_files"], [])
        self.assertEqual(readiness["missing_implementation_flags"], [])
        manifest = build_manifest(DEFAULT_PROTOCOL)
        self.assertEqual(manifest["provider_calls_made"], 0)
        self.assertFalse(manifest["runner_invoked"])
        self.assertFalse(manifest["environment_values_read"])
        self.assertEqual(manifest["filesystem_writes_made"], 0)
        self.assertEqual(manifest["commands_emitted"], 240)
        self.assertEqual(manifest["commands_suppressed"], 0)
        self.assertFalse(manifest["formal_launch_allowed_by_this_scheduler"])
        self.assertTrue(
            all(
                unit["argv"] == unit["planned_argv"]
                and unit["command"] == unit["planned_command"]
                for unit in manifest["units"]
            )
        )
        self.assertTrue(
            all(
                unit["argv"][:2]
                == ["python", "scripts/run_graph_dynamic_formal_v2.py"]
                for unit in manifest["units"]
            )
        )

    def test_identity_evidence_is_deliberately_cross_file(self) -> None:
        runner = ROOT / "scripts/run_graph_dynamic_formal_v2.py"
        runner_only = runtime_readiness(
            self.protocol,
            runner_override=runner,
            identity_proof_overrides=[runner],
        )
        self.assertEqual(runner_only["missing_identity_literals"], [])
        self.assertEqual(len(runtime_readiness(self.protocol)["identity_proof_files"]), 4)
        self.assertEqual(runtime_readiness(self.protocol)["missing_identity_literals"], [])

    def test_synthetic_complete_proof_exposes_commands_as_data_only(self) -> None:
        protocol = copy.deepcopy(self.protocol)
        runner_contract = protocol["formal_scheduler"]["runner"]
        source = "\n".join(
            ["parser = object()"]
            + [
                f'parser.add_argument("{flag}")'
                for flag in runner_contract["required_flags"]
            ]
            + [repr(value) for value in runner_contract["required_identity_literals"]]
        )
        with tempfile.TemporaryDirectory() as directory:
            runner = Path(directory) / "complete_runner.py"
            runner.write_text(source, encoding="utf-8")
            readiness = runtime_readiness(
                protocol,
                runner_override=runner,
                identity_proof_overrides=[runner],
            )
        self.assertTrue(readiness["ready"], readiness["blocked_reasons"])
        units = build_units(protocol, expose_runnable_commands=readiness["ready"])
        self.assertEqual(len(units), 240)
        self.assertTrue(all(unit["argv"] == unit["planned_argv"] for unit in units))
        self.assertTrue(all(unit["command"] == unit["planned_command"] for unit in units))
        # Static readiness never broadens this scheduler into a launch surface.
        manifest = build_manifest(DEFAULT_PROTOCOL)
        self.assertFalse(manifest["formal_launch_allowed_by_this_scheduler"])

    def test_default_cli_is_dry_run_and_strict_readiness_succeeds(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(main([]), 0)
        emitted = json.loads(stdout.getvalue())
        self.assertEqual(emitted["mode"], "dry_run")
        self.assertEqual(emitted["unit_count"], 240)
        self.assertEqual(emitted["provider_calls_made"], 0)
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--require-runtime-ready"]), 0)

    def test_identity_or_root_drift_fails_before_schedule_emission(self) -> None:
        identity_drift = copy.deepcopy(self.protocol)
        identity_drift["formal_scheduler"]["cell_assignments"]["reactive"][
            "agent_profile_id"
        ] = "legacy-profile"
        with self.assertRaisesRegex(ScheduleContractError, "assignment reactive"):
            build_units(identity_drift)

        root_drift = copy.deepcopy(self.protocol)
        root_drift["output_contract"]["formal_root"] = (
            "paper/experiments/runs/formal/graph_dynamic_ablation_v1/legacy"
        )
        with self.assertRaisesRegex(ScheduleContractError, "isolated dynamic-v3"):
            build_units(root_drift)


if __name__ == "__main__":
    unittest.main()
