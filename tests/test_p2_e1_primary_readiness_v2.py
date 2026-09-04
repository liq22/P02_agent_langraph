from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import audit_p2_e1_primary_readiness_v2 as READINESS
from scripts.audit_p2_e1_primary_readiness_v2 import (
    OUTPUT,
    ReadinessError,
    audit,
)
from scripts.finalize_p2_e1_generic_base_formal_v2 import (
    ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
    ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
    DEFAULT_PROTOCOL,
    DEFAULT_RESULT,
)
import yaml


class P2E1PrimaryReadinessV2Test(unittest.TestCase):
    def test_cli_passes_joint_schedule_acceptance_to_current_builder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            paths = {
                "protocol": root / "protocol.yaml",
                "joint_schedule_acceptance": root / "joint-acceptance.json",
                "generic_core_root": root / "generic-core",
                "generic_replay_root": root / "generic-replay",
                "graph_core_root": root / "graph-core",
                "graph_replay_root": root / "graph-replay",
                "output": root / "readiness.json",
                "result_output": root / "result.json",
            }
            readiness = {"accepted": False}
            result = {"effect_estimates_emitted": 0}
            argv = [
                "--protocol", str(paths["protocol"]),
                "--joint-schedule-acceptance", str(paths["joint_schedule_acceptance"]),
                "--generic-core-root", str(paths["generic_core_root"]),
                "--generic-replay-root", str(paths["generic_replay_root"]),
                "--graph-core-root", str(paths["graph_core_root"]),
                "--graph-replay-root", str(paths["graph_replay_root"]),
                "--output", str(paths["output"]),
                "--result-output", str(paths["result_output"]),
            ]
            with (
                patch.object(
                    READINESS,
                    "build_documents",
                    return_value=(readiness, result),
                ) as builder,
                patch("builtins.print"),
            ):
                self.assertEqual(READINESS.main(argv), 0)
            builder.assert_called_once_with(
                protocol_path=paths["protocol"],
                joint_schedule_acceptance=paths["joint_schedule_acceptance"],
                generic_core_root=paths["generic_core_root"],
                generic_replay_root=paths["generic_replay_root"],
                graph_core_root=paths["graph_core_root"],
                graph_replay_root=paths["graph_replay_root"],
            )
            self.assertEqual(
                json.loads(paths["output"].read_text(encoding="utf-8")),
                readiness,
            )
            self.assertEqual(
                json.loads(paths["result_output"].read_text(encoding="utf-8")),
                result,
            )

    def test_current_authority_correct_gate_is_fail_closed_and_provider_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp = "20260901T010203Z"
            family = root / ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
            kwargs = {
                "generic_core_root": family
                / "joint_generic_core"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "generic_replay_root": family
                / "joint_generic_replay"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "graph_core_root": family
                / "joint_graph_core"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "graph_replay_root": family
                / "joint_graph_replay"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
            }
            with self.assertRaisesRegex(
                ReadinessError, "blocked without --joint-schedule-acceptance"
            ):
                audit(**kwargs)

    def test_roots_are_generic_control_and_new_graph_identity_only(self) -> None:
        protocol = yaml.safe_load(DEFAULT_PROTOCOL.read_text(encoding="utf-8"))
        for arm in (protocol["authority"]["control"], protocol["authority"]["treatment"]):
            self.assertIsNone(arm["core_root"])
            self.assertIsNone(arm["replay_root"])
            self.assertEqual(
                arm["external_root_contract"]["schema"],
                "p1_p2_joint_external_timestamped_root_v1",
            )

    def test_checked_in_readiness_and_result_match_current_fail_closed_audit(self) -> None:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        result = json.loads(DEFAULT_RESULT.read_text(encoding="utf-8"))
        self.assertEqual(stored["status"], "external_roots_required_no_audit_performed")
        self.assertNotIn("canonical_runbundle_v1", json.dumps(stored))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["status"], "external_roots_required_no_result")
        self.assertIsNone(result["paired_bearing_bootstrap"])
        self.assertEqual(result["effect_estimates_emitted"], 0)


if __name__ == "__main__":
    unittest.main()
