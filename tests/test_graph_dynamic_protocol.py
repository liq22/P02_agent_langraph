from __future__ import annotations

import unittest
from pathlib import Path

import yaml
from scripts.analyze_graph_dynamic_formal import load_protocol


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_PATH = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
NARRATIVE_PATH = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.md"


class GraphDynamicProtocolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.protocol = load_protocol(PROTOCOL_PATH)

    def test_is_preregistered_implemented_provider_free_and_formal_not_run(self) -> None:
        protocol = self.protocol
        self.assertEqual(protocol["schema_version"], "graph_dynamic_ablation_protocol_v3")
        self.assertEqual(
            protocol["status"],
            "preregistered_task_primary_metric_amendment_formal_not_run",
        )
        implementation = protocol["implementation_status"]
        for key in (
            "event_emitter_implemented",
            "dynamic_runtime_profile_implemented",
            "ablation_conversation_profiles_implemented",
        ):
            self.assertIs(implementation[key], True)
        self.assertIs(implementation["formal_runner_implemented"], True)
        self.assertIs(implementation["provider_free_exact_six_acceptance_gate_passed"], True)
        self.assertIs(implementation["formal_provider_execution_started"], False)
        self.assertIs(implementation["formal_results_exist"], False)
        self.assertIs(implementation["task_primary_metric_contract_implemented"], True)
        self.assertIs(implementation["provider_free_metric_regression_passed"], True)
        self.assertIs(implementation["accepted_mechanism_reporting_implemented"], True)
        self.assertEqual(
            implementation["event_payload_key"], "public_condition_event"
        )
        narrative = NARRATIVE_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Task performance is primary",
            narrative,
        )
        mechanism = protocol["formal_analysis"]["accepted_manuscript_consumer"][
            "mechanism_reporting"
        ]
        self.assertEqual(mechanism["role"], "secondary_explanatory_not_task_performance")
        self.assertEqual(mechanism["horizon"], 12)
        self.assertIs(
            mechanism["operating_condition_change_rows"][
                "duplicate_no_branching_rows"
            ],
            False,
        )

    def test_task_metric_and_failed_window_population_are_primary(self) -> None:
        metrics = self.protocol["metrics"]
        primary = metrics["primary"]
        self.assertEqual(
            primary["name"], "target_adverse_window_average_precision"
        )
        self.assertEqual(
            primary["missing_score_policy_id"],
            "phase1_replay_target_adverse_missing_score_v1",
        )
        self.assertIn("failed", primary["denominator"])
        self.assertIn("grounded_completion_rate", metrics["general_rollout"])
        self.assertNotEqual(primary["name"], "grounded_completion_rate")

        statistics = self.protocol["statistics"]
        self.assertEqual(
            statistics["exact_paired_permutation"],
            "all_256_matched_bearing_cluster_arm_swaps_with_metric_recomputation",
        )
        self.assertIn("Never average per-bearing AP", statistics["bearing_cluster_handling"])
        self.assertEqual(
            self.protocol["formal_analysis"]["statistical_clarifications"]
            ["per_bearing_average_precision"],
            "forbidden",
        )

    def test_event_is_public_release_bounded_and_not_fault_onset(self) -> None:
        event = self.protocol["public_event_contract"]
        self.assertEqual(event["event_name"], "operating_condition_change")
        self.assertIn("fault_onset", event["forbidden_event_names"])
        self.assertTrue(event["delivery"]["before_release"] == "forbidden")
        self.assertTrue(event["delivery"]["future_event_visibility"] == "forbidden")
        forbidden = set(event["derivation"]["forbidden_inputs"])
        self.assertTrue(
            {"signal_values", "label", "anomaly_target", "bearing_id"}.issubset(forbidden)
        )
        self.assertNotIn("fault_onset", event["delivery"]["recipients"])
        self.assertIn("public_condition_event", event["delivery"]["payload"])
        self.assertNotIn("graph_observation", event["delivery"]["payload"])
        self.assertIn("event_f1", self.protocol["metrics"]["forbidden_metrics"])
        self.assertIn("detection_delay", self.protocol["metrics"]["forbidden_metrics"])

    def test_horizons_are_nested_and_condition_schedule_is_frozen(self) -> None:
        sequence = self.protocol["sequence_construction"]
        horizons = sequence["horizons"]
        self.assertEqual(horizons, [3, 6, 12])
        self.assertEqual(sequence["master_horizon"], max(horizons))
        self.assertIs(sequence["independently_resample_each_horizon"], False)
        self.assertEqual(
            sequence["expected_public_domain_schedule"],
            [1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0],
        )
        changes = sequence["expected_change_release_indices_zero_based"]
        self.assertEqual(changes, [3, 6, 9])
        expected_counts = sequence["expected_change_count_by_horizon"]
        for horizon in horizons:
            self.assertEqual(
                expected_counts[horizon], sum(index < horizon for index in changes)
            )

    def test_event_ids_are_unique_logical_public_events_shared_across_arms(self) -> None:
        catalog = self.protocol["public_event_contract"]["event_id_catalog"]
        self.assertEqual(
            catalog["logical_key_fields"],
            ["seed", "rotation", "public_sequence_id", "release_index"],
        )
        excluded = set(catalog["deliberately_excluded_key_fields"])
        self.assertTrue(
            {"horizon", "arm", "graph_profile", "private_target", "bearing_id"}.issubset(
                excluded
            )
        )
        expected = (
            len(self.protocol["experiment_design"]["seeds"])
            * self.protocol["dataset"]["held_out_bearings"]
            * len(self.protocol["sequence_construction"]["expected_change_release_indices_zero_based"])
        )
        self.assertEqual(catalog["expected_logical_events"], expected)

    def test_profiles_have_exact_toggle_and_legal_state_contracts(self) -> None:
        profiles = self.protocol["graph_profiles"]
        self.assertEqual(
            set(profiles),
            {
                "full",
                "no_recovery_revision_edge",
                "no_observation_conditioned_branching",
                "no_persistent_graph_state",
                "no_replanning",
            },
        )
        toggles = {
            "full": (True, True, True, True),
            "no_recovery_revision_edge": (False, True, True, True),
            "no_observation_conditioned_branching": (True, False, True, True),
            "no_persistent_graph_state": (True, True, False, True),
            "no_replanning": (True, True, True, False),
        }
        toggle_names = (
            "recovery_revision_edge",
            "observation_conditioned_branching",
            "persistent_graph_state",
            "replanning",
        )
        for name, expected in toggles.items():
            profile = profiles[name]
            self.assertEqual(
                tuple(profile["toggles"][key] for key in toggle_names), expected
            )
            reachable = set(profile["reachable_states"])
            transitions = profile["legal_transitions"]
            self.assertEqual(set(transitions), reachable)
            for sources in transitions.values():
                self.assertTrue(set(sources).issubset(reachable))

        self.assertNotIn("Recover", profiles["no_recovery_revision_edge"]["reachable_states"])
        self.assertNotIn("Revise", profiles["no_recovery_revision_edge"]["reachable_states"])
        self.assertNotIn(
            "Monitor", profiles["no_observation_conditioned_branching"]["reachable_states"]
        )
        self.assertNotIn(
            "Revise", profiles["no_observation_conditioned_branching"]["reachable_states"]
        )
        self.assertNotIn("Revise", profiles["no_persistent_graph_state"]["reachable_states"])
        self.assertNotIn("Revise", profiles["no_replanning"]["reachable_states"])

    def test_no_persistent_profile_removes_prior_state_from_conversation(self) -> None:
        profile = self.protocol["graph_profiles"]["no_persistent_graph_state"]
        self.assertEqual(profile["router_previous_state"], "forbidden")
        self.assertEqual(profile["model_conversation_previous_state"], "forbidden")
        rebuild = profile["conversation_rebuild"]
        self.assertIs(rebuild["every_turn"], True)
        self.assertIs(rebuild["retain_shared_public_action_result_history"], True)
        self.assertIs(rebuild["retain_prior_public_event_observations"], True)
        self.assertIs(rebuild["strip_prior_decision_state_fields"], True)
        self.assertIs(rebuild["strip_prior_state_guidance_messages"], True)
        self.assertIs(rebuild["include_current_state_guidance_once"], True)

    def test_matrix_counts_and_budgets_are_cross_field_consistent(self) -> None:
        design = self.protocol["experiment_design"]
        cells = design["cells_per_seed_sequence"]
        cell_count = sum(len(value) for value in cells.values())
        self.assertEqual(cell_count, design["total_cells_per_seed_sequence"])
        sequence_count = len(design["seeds"]) * self.protocol["dataset"]["held_out_bearings"]
        self.assertEqual(sequence_count, design["total_sequences_per_cell"])
        self.assertEqual(
            design["expected_formal_episode_bundles"], cell_count * sequence_count
        )

        budgets = self.protocol["budgets"]["by_horizon"]
        for horizon in self.protocol["sequence_construction"]["horizons"]:
            budget = budgets[horizon]
            self.assertEqual(budget["max_tool_calls"], 24 * horizon)
            self.assertEqual(budget["max_window_reads"], horizon)
            self.assertEqual(budget["max_operator_calls"], 50 * horizon // 3)
            self.assertEqual(budget["max_model_calls"], horizon)
            self.assertEqual(budget["max_llm_turns"], 24 * horizon)
            self.assertEqual(budget["max_data_points"], 8192 * horizon)
            self.assertEqual(budget["max_data_bytes"], 65536 * horizon)
            self.assertIsNone(budget["max_wall_clock_seconds"])

    def test_runtime_and_outputs_are_isolated_from_active_primary(self) -> None:
        runtime = self.protocol["runtime_and_provider_profile"]
        self.assertNotEqual(
            runtime["effective_runtime_contract"], runtime["base_runtime_contract"]
        )
        self.assertIs(runtime["separate_from_active_primary_profile"], True)
        self.assertIs(runtime["pool_with_active_paderborn_v6_primary"], False)
        self.assertIs(runtime["pool_across_provider_model_or_runtime_profiles"], False)
        outputs = self.protocol["output_contract"]
        self.assertIn("graph_dynamic_ablation_v2", outputs["mechanics_root"])
        self.assertIn("graph_dynamic_ablation_v3", outputs["formal_root"])
        self.assertIn("graph_dynamic_ablation_v3", outputs["results_root"])
        self.assertNotIn("graph_dynamic_ablation_v2", outputs["formal_root"])
        self.assertEqual(len(outputs["canonical_episode_files"]), 6)
        self.assertEqual(len(set(outputs["canonical_episode_files"])), 6)

    def test_provider_free_acceptance_is_mechanics_only(self) -> None:
        gate = self.protocol["acceptance_gates"]["provider_free_mock"]
        self.assertIs(gate["acceptance_gate_passed"], True)
        self.assertIs(gate["provider_calls_allowed"], False)
        self.assertEqual(gate["matrix_cells"], 10)
        self.assertEqual(gate["expected_episode_bundles"], 10)
        self.assertIs(gate["performance_claims_allowed"], False)
        self.assertIn(
            "no_persistent_outbound_requests_contain_prior_graph_state_or_guidance",
            gate["requirements"],
        )


if __name__ == "__main__":
    unittest.main()
