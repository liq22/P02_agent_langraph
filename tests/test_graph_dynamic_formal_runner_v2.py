from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.analyze_graph_dynamic_formal import expected_units, load_protocol, unit_root
from scripts.run_graph_dynamic_formal_v2 import (
    DEFAULT_DYNAMIC_PROTOCOL,
    FORMAL_EXECUTION_CONTRACT,
    GraphDynamicFormalRunnerError,
    ROOT,
    _check_execution_environment,
    _check_probe_evidence,
    _expected_manifest,
    _parser,
    _registered_unit,
    build_dynamic_formal_unit_contract,
    inspect_attempt_prefix,
    main,
)
from scripts.schedule_graph_dynamic_formal_v2 import build_manifest


LEGACY_PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v1.yaml"


def _fixture_module():
    name = "graph_dynamic_formal_fixture_support"
    if name in sys.modules:
        return sys.modules[name]
    path = ROOT / "tests/test_graph_dynamic_formal_analysis.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load dynamic formal fixture support")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )


class GraphDynamicFormalRunnerV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_protocol(DEFAULT_DYNAMIC_PROTOCOL)
        cls.schedule = build_manifest(DEFAULT_DYNAMIC_PROTOCOL)

    def _args(self, index: int = 0, *, validate_only: bool = True):
        argv = list(self.schedule["units"][index]["argv"][2:])
        if validate_only:
            argv.append("--validate-only")
        return _parser().parse_args(argv)

    def test_scheduler_is_ready_for_all_240_dedicated_wrapper_units(self) -> None:
        self.assertTrue(self.schedule["runtime_readiness"]["ready"])
        self.assertEqual(self.schedule["commands_emitted"], 240)
        self.assertEqual(self.schedule["commands_suppressed"], 0)
        self.assertEqual(self.schedule["provider_calls_made"], 0)
        self.assertFalse(self.schedule["runner_invoked"])
        self.assertFalse(self.schedule["formal_launch_allowed_by_this_scheduler"])
        registered = expected_units(self.protocol)
        self.assertEqual(len(registered), 240)
        for ordinal, scheduled in enumerate(self.schedule["units"], 1):
            args = self._args(ordinal - 1)
            observed_ordinal, unit = _registered_unit(self.protocol, args)
            self.assertEqual(observed_ordinal, ordinal)
            self.assertEqual(
                unit.key,
                (
                    scheduled["key"]["seed"],
                    scheduled["key"]["rotation"],
                    scheduled["key"]["public_sequence_id"],
                    scheduled["key"]["horizon"],
                    scheduled["key"]["cell"],
                ),
            )
            self.assertEqual(
                (ROOT / scheduled["output_root"]).resolve(),
                (
                    ROOT
                    / unit_root(
                        Path(self.protocol["output_contract"]["formal_root"]),
                        unit,
                    )
                ).resolve(),
            )
            argv = scheduled["argv"]
            self.assertEqual(
                argv[:2], ["python", "scripts/run_graph_dynamic_formal_v2.py"]
            )
            self.assertEqual(
                argv[argv.index("--input-usd-per-million") + 1], "0.0"
            )
            self.assertEqual(
                argv[argv.index("--output-usd-per-million") + 1], "0.0"
            )

    def test_validate_only_contract_is_provider_free_and_has_analyzer_proof(self) -> None:
        args = self._args(0)
        with mock.patch(
            "scripts.run_graph_dynamic_formal_v2._check_execution_environment",
            side_effect=AssertionError("provider env was read"),
        ), mock.patch(
            "scripts.run_graph_dynamic_formal_v2._check_probe_evidence",
            side_effect=AssertionError("probe evidence was read"),
        ), mock.patch(
            "scripts.run_graph_dynamic_formal_v2.execute_dynamic_formal_unit",
            side_effect=AssertionError("provider execution was invoked"),
        ):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(
                    main(self.schedule["units"][0]["argv"][2:] + ["--validate-only"]),
                    0,
                )
        contract = json.loads(stdout.getvalue())
        self.assertEqual(contract["registered_unit_count"], 240)
        self.assertEqual(contract["formal_execution_contract"], FORMAL_EXECUTION_CONTRACT)
        self.assertEqual(contract["attempt_state"]["state"], "pending")
        self.assertFalse(contract["provider_calls_performed"])
        self.assertFalse(contract["environment_values_read"])
        self.assertFalse(contract["probe_evidence_read"])
        self.assertFalse(contract["filesystem_writes_performed"])
        self.assertEqual(
            set(contract["analyzer_manifest_proof_fields"]),
            set(self.protocol["formal_analysis"]["manifest_proof_fields"]),
        )
        expected = _expected_manifest(
            self.protocol, expected_units(self.protocol)[0], attempt_count=1, complete=True
        )
        self.assertTrue(
            set(contract["analyzer_manifest_proof_fields"]).issubset(expected)
        )

    def test_representative_ten_cells_validate_exact_identity_and_budget(self) -> None:
        indices = list(range(10))
        contracts = [build_dynamic_formal_unit_contract(self._args(index)) for index in indices]
        self.assertEqual(
            {contract["cell"] for contract in contracts},
            {
                "reactive",
                "graph_full",
                "graph_no_recovery_revision_edge",
                "graph_no_observation_conditioned_branching",
                "graph_no_persistent_graph_state",
                "graph_no_replanning",
            },
        )
        for contract in contracts:
            self.assertEqual(contract["p2_experiment_id"], "p2_graph_vs_generic_llm_v1")
            self.assertEqual(
                contract["matched_control_id"], "benchmark_generic_llm_tool_agent_v1"
            )
            self.assertEqual(contract["input_usd_per_million"], 0.0)
            self.assertEqual(contract["output_usd_per_million"], 0.0)
            self.assertEqual(
                contract["budget"],
                self.protocol["budgets"]["by_horizon"][contract["horizon"]],
            )

    def test_v1_price_profile_and_output_drift_are_rejected_before_env(self) -> None:
        args = self._args(0)
        args.dynamic_protocol = LEGACY_PROTOCOL
        with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "v1/v2 are forbidden"):
            build_dynamic_formal_unit_contract(args)

        args = self._args(0)
        args.input_usd_per_million = 1.0
        with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "input_usd"):
            build_dynamic_formal_unit_contract(args)

        args = self._args(0)
        args.output = Path("paper/experiments/runs/formal/graph_dynamic_ablation_v1")
        with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "isolated registered"):
            build_dynamic_formal_unit_contract(args)

        args = self._args(0)
        args.graph_profile = "no_replanning"
        with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "graph profile"):
            build_dynamic_formal_unit_contract(args)

    def test_exact_six_provider_retry_then_effective_terminal_is_accepted(self) -> None:
        fixture = _fixture_module()
        unit = expected_units(self.protocol)[0]
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture._write_unit(
                root,
                self.protocol,
                unit,
                provider_retry=True,
                agent_failure=False,
            )
            directory = unit_root(root, unit)
            state = inspect_attempt_prefix(directory, unit, self.protocol)
            self.assertEqual(
                state,
                {
                    "state": "complete",
                    "attempt_count": 2,
                    "provider_failure_attempt_count": 1,
                    "effective_non_provider_terminal_count": 1,
                    "next_attempt_index": None,
                    "complete": True,
                },
            )
            (directory / "attempt_001/artifacts.json").unlink()
            with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "exact-six"):
                inspect_attempt_prefix(directory, unit, self.protocol)

    def test_unresolved_provider_prefix_is_exactly_next_attempt_resumable(self) -> None:
        fixture = _fixture_module()
        unit = expected_units(self.protocol)[0]
        with tempfile.TemporaryDirectory() as temporary:
            directory = unit_root(Path(temporary), unit)
            directory.mkdir(parents=True)
            fixture._write_attempt(
                directory,
                self.protocol,
                unit,
                attempt_index=0,
                provider_failure=True,
            )
            (directory / "evaluation.jsonl").write_text("{}\n", encoding="utf-8")
            _write_json(directory / "summary.json", {})
            _write_json(
                directory / "run_manifest.json",
                _expected_manifest(
                    self.protocol, unit, attempt_count=1, complete=False
                ),
            )
            state = inspect_attempt_prefix(directory, unit, self.protocol)
            self.assertEqual(state["state"], "provider_retry_pending")
            self.assertEqual(state["attempt_count"], 1)
            self.assertEqual(state["provider_failure_attempt_count"], 1)
            self.assertEqual(state["effective_non_provider_terminal_count"], 0)
            self.assertEqual(state["next_attempt_index"], 1)

            (directory / "attempt_002").mkdir()
            with self.assertRaisesRegex(
                GraphDynamicFormalRunnerError, "not contiguous zero-based"
            ):
                inspect_attempt_prefix(directory, unit, self.protocol)

    def test_normal_mode_routes_only_to_provider_bound_executor(self) -> None:
        argv = self.schedule["units"][0]["argv"][2:]
        contract = build_dynamic_formal_unit_contract(self._args(0))
        with mock.patch(
            "scripts.run_graph_dynamic_formal_v2.execute_dynamic_formal_unit",
            return_value=contract,
        ) as execute:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(main(argv), 0)
        execute.assert_called_once()

    def test_environment_and_fresh_two_turn_probe_are_exact_profile_checks(self) -> None:
        args = self._args(0)
        contract = build_dynamic_formal_unit_contract(args)
        env = {
            args.base_url_env: "https://openrouter.ai/api/v1",
            args.api_key_env: "not-a-real-key",
            args.model_env: contract["model"],
        }
        with mock.patch.dict(os.environ, env, clear=True):
            _check_execution_environment(args, contract)
        with mock.patch.dict(
            os.environ, {**env, args.model_env: "wrong/model"}, clear=True
        ):
            with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "model identity"):
                _check_execution_environment(args, contract)

        with tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "probe.json"
            _write_json(
                probe,
                {
                    "models": [
                        {
                            "model_id": contract["model"],
                            "status": "passed",
                            "completed_turns": 2,
                            "error": None,
                        }
                    ]
                },
            )
            _check_probe_evidence(probe, model=contract["model"], max_age_hours=24)
            value = json.loads(probe.read_text(encoding="utf-8"))
            value["models"][0]["completed_turns"] = 1
            _write_json(probe, value)
            with self.assertRaisesRegex(GraphDynamicFormalRunnerError, "has not passed"):
                _check_probe_evidence(probe, model=contract["model"], max_age_hours=24)


if __name__ == "__main__":
    unittest.main()
