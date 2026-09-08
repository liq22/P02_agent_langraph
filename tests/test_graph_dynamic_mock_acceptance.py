from __future__ import annotations

import json
import unittest
from pathlib import Path

import yaml

from scripts.run_graph_dynamic_mock_acceptance import (
    GUIDANCE_MARKER,
    audit_outbound_messages,
    load_yaml,
    registered_cells,
)


ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = load_yaml(
    ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml"
)


class GraphDynamicMockAcceptanceTest(unittest.TestCase):
    def test_registered_matrix_is_exactly_the_frozen_ten_cells(self):
        cells = registered_cells(PROTOCOL)
        self.assertEqual(len(cells), 10)
        self.assertEqual(
            [(cell.horizon, cell.registered_name) for cell in cells],
            [
                (3, "reactive"),
                (3, "graph_full"),
                (6, "reactive"),
                (6, "graph_full"),
                (12, "reactive"),
                (12, "graph_full"),
                (12, "graph_no_recovery_revision_edge"),
                (12, "graph_no_observation_conditioned_branching"),
                (12, "graph_no_persistent_graph_state"),
                (12, "graph_no_replanning"),
            ],
        )

    def test_outbound_audit_distinguishes_current_guidance_from_history(self):
        clean = audit_outbound_messages(
            [
                {"role": "system", "content": f"{GUIDANCE_MARKER} Analyze."},
                {"role": "user", "content": "{}"},
                {
                    "role": "tool",
                    "content": json.dumps({"tool_result": {}, "error": None}),
                },
            ]
        )
        self.assertEqual(clean["historical_decision_state_key_messages"], 0)
        self.assertEqual(clean["current_state_guidance_count"], 1)
        self.assertEqual(clean["state_guidance_roles"], ["system"])

        leaked = audit_outbound_messages(
            [
                {"role": "system", "content": f"{GUIDANCE_MARKER} Analyze."},
                {
                    "role": "tool",
                    "content": json.dumps(
                        {"tool_result": {}, "decision_state": "Monitor"}
                    ),
                },
            ]
        )
        self.assertEqual(leaked["historical_decision_state_key_messages"], 1)


if __name__ == "__main__":
    unittest.main()
