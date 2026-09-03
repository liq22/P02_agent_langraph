from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

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
    def test_current_authority_correct_gate_is_fail_closed_and_provider_free(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            stamp = "20260901T010203Z"
            family = root / ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID
            kwargs = {
                "benchmark_formal_run_stamp": stamp,
                "benchmark_control_protocol_id": ACTIVE_BENCHMARK_CONTROL_PROTOCOL_ID,
                "benchmark_control_profile_id": ACTIVE_BENCHMARK_CONTROL_PROFILE_ID,
                "generic_core_root": family
                / "b3_generic_core"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "generic_replay_root": family
                / "b3_generic_replay"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "graph_core_root": family
                / "graph_core_primary"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
                "graph_replay_root": family
                / "graph_replay_primary"
                / ACTIVE_BENCHMARK_CONTROL_PROFILE_ID
                / f"run_{stamp}",
            }
            report = audit(**kwargs)
            kwargs["generic_core_root"].mkdir(parents=True)
            (kwargs["generic_core_root"] / "retired-layout.txt").write_text(
                "not canonical", encoding="utf-8"
            )
            with self.assertRaisesRegex(
                ReadinessError, "non-empty root contains zero active-v0.2"
            ):
                audit(**kwargs)
        self.assertFalse(report["accepted"])
        self.assertEqual(report["provider_calls"], 0)
        self.assertEqual(report["effect_estimates_emitted"], 0)
        self.assertFalse(report["authority"]["legacy_phmskills_graph_roots_included"])
        self.assertFalse(report["authority"]["duplicate_reactive_provider_execution_required"])
        self.assertEqual(report["observed"]["generic_core"]["statistical_outcomes"], 0)
        self.assertEqual(report["observed"]["graph_core"]["statistical_outcomes"], 0)
        self.assertFalse(report["gates"]["bootstrap_permitted"])
        self.assertEqual(report["evaluator_private_views_read"], 0)

    def test_roots_are_generic_control_and_new_graph_identity_only(self) -> None:
        protocol = yaml.safe_load(DEFAULT_PROTOCOL.read_text(encoding="utf-8"))
        for arm in (protocol["authority"]["control"], protocol["authority"]["treatment"]):
            self.assertIsNone(arm["core_root"])
            self.assertIsNone(arm["replay_root"])
            self.assertEqual(
                arm["external_root_contract"]["schema"],
                "benchmark_active_v0_2_external_timestamped_root_v1",
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
