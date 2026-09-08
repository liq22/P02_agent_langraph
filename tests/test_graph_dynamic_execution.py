from __future__ import annotations

import unittest
from collections.abc import Mapping
from pathlib import Path

import numpy as np
import yaml
from scripts.run_graph_experiment import _load_dynamic_protocol

from phm_agent_benchmark.phase1 import (
    DeterministicMockLLM,
    Phase1ModelPool,
    WindowArtifact,
    feature_vector,
)
from phm_agent_benchmark.vibration.contracts import SignalBatch
from phm_graph_agent import (
    GRAPH_DYNAMIC_RUNTIME_CONTRACT,
    GraphDecisionAgent,
    GraphPolicyConfig,
    ReactiveSequentialAgent,
    transition_validity,
)
from phm_graph_agent.dynamic_runtime import (
    DynamicPublicSequence,
    budget_for_horizon,
    build_event_catalog,
    build_master_sequences,
    event_schedule_for_horizon,
    run_dynamic_episode,
)


ROOT = Path(__file__).resolve().parents[1]
DYNAMIC = _load_dynamic_protocol(
    ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
)
DATASET = yaml.safe_load(
    (
        ROOT.parent
        / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml"
    ).read_text(encoding="utf-8")
)


def _signal(
    index: int,
    ref: str,
    *,
    sample_count: int = 512,
    sample_rate_hz: float = 1024.0,
    channels: tuple[str, ...] = ("ch0",),
) -> SignalBatch:
    time = np.arange(sample_count, dtype=np.float64) / sample_rate_hz
    values = np.sin(2.0 * np.pi * (20.0 + index) * time)
    matrix = np.repeat(values[:, None], len(channels), axis=1)
    return SignalBatch(matrix, sample_rate_hz, channels, source_ref=ref)


class DynamicFakeData:
    def __init__(self, records: Mapping[str, Mapping[str, object]]) -> None:
        self.records = {str(key): dict(value) for key, value in records.items()}
        self.order = {sample_id: index for index, sample_id in enumerate(self.records)}
        self.windows: dict[str, WindowArtifact] = {}
        self.next_window = 1

    def search_samples(self, query, limit):
        del query
        rows = [
            {
                "sample_id": sample_id,
                "domain_id": record["domain_id"],
                "sample_rate": 64000.0,
            }
            for sample_id, record in self.records.items()
        ]
        return rows[:limit]

    def describe_sample(self, sample_id):
        record = self.records[str(sample_id)]
        return {
            "sample_id": str(sample_id),
            "domain_id": record["domain_id"],
            "sample_rate": 64000.0,
            "channels": [0, 1, 2],
        }

    def private_record(self, sample_id):
        return self.records[str(sample_id)]

    def metadata_order(self, sample_id):
        return self.order[str(sample_id)]

    def read_window(self, request):
        sample_id = str(request["sample_id"])
        start = int(request["start"])
        end = int(request["end"])
        channel_indices = tuple(int(value) for value in request["channels"])
        ref = f"artifact://window/{self.next_window:06d}"
        self.next_window += 1
        signal = _signal(
            self.order[sample_id] % 7,
            ref,
            sample_count=end - start,
            sample_rate_hz=64000.0,
            channels=tuple(f"ch{value}" for value in channel_indices),
        )
        artifact = WindowArtifact(
            ref,
            signal,
            sample_id,
            start,
            end,
            1,
            channel_indices,
            64000.0,
        )
        self.windows[ref] = artifact
        return artifact

    def summarize_window(self, artifact_ref):
        return {"artifact_ref": artifact_ref, "sample_count": 512}


def _master_records() -> dict[str, dict[str, object]]:
    records: dict[str, dict[str, object]] = {}
    domains = [1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0]
    for bearing in DATASET["split"]["folds"]["fold_0"]:
        for index, domain in enumerate(domains):
            sample_id = f"{bearing}-sample-{index:02d}"
            records[sample_id] = {
                "domain_id": domain,
                "label": 0 if bearing.startswith("K00") else 1,
                "file": f"{bearing}/sample-{index:02d}.mat",
            }
    return records


class DynamicConstructionTest(unittest.TestCase):
    def test_master_prefixes_catalog_and_budgets_are_exact(self):
        sequences = build_master_sequences(
            DynamicFakeData(_master_records()), DATASET, DYNAMIC, "rotation_0"
        )
        self.assertEqual(sorted(sequences), [f"sequence-{i:04d}" for i in range(1, 9)])
        self.assertEqual(
            {sequence.public_domain_ids for sequence in sequences.values()},
            {(1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0)},
        )
        catalog = build_event_catalog(DYNAMIC)
        self.assertEqual(len(catalog), 72)
        self.assertEqual(len(set(catalog.values())), 72)
        self.assertEqual(min(catalog.values()), "occ-00000001")
        self.assertEqual(max(catalog.values()), "occ-00000072")

        sequence = sequences["sequence-0001"]
        for horizon, expected_indices in ((3, set()), (6, {3}), (12, {3, 6, 9})):
            sample_ids, schedule = event_schedule_for_horizon(
                DYNAMIC,
                sequence,
                seed=20260808,
                rotation="rotation_0",
                horizon=horizon,
            )
            self.assertEqual(sample_ids, sequence.sample_ids[:horizon])
            self.assertEqual(set(schedule.event_ids_by_release_index), expected_indices)
            self.assertEqual(
                budget_for_horizon(DYNAMIC, horizon).max_window_reads, horizon
            )


class DynamicProviderFreeEpisodeTest(unittest.IsolatedAsyncioTestCase):
    async def test_mock_full_and_ablations_receive_only_released_condition_events(self):
        domains = (1, 1, 1, 2, 2, 2, 3, 3, 3, 0, 0, 0)
        sample_ids = tuple(f"sample-{index}" for index in range(12))
        records = {
            sample_id: {
                "domain_id": domains[index],
                "label": 0 if index < 3 else 1,
                "file": f"opaque-{index}/sample.mat",
            }
            for index, sample_id in enumerate(sample_ids)
        }
        data = DynamicFakeData(records)
        sequence = DynamicPublicSequence("sequence-0001", sample_ids, domains)
        features = np.vstack(
            [
                feature_vector(_signal(index, f"artifact://train/{index}"))
                for index in range(3)
            ]
        )
        models = Phase1ModelPool()
        models.fit_anomaly(features)

        cells = (
            (3, "reactive"),
            (3, "full"),
            (6, "reactive"),
            (6, "full"),
            (12, "reactive"),
            (12, "full"),
            (12, "no_recovery_revision_edge"),
            (12, "no_observation_conditioned_branching"),
            (12, "no_persistent_graph_state"),
            (12, "no_replanning"),
        )
        events_by_release: dict[int, list[dict[str, object]]] = {}
        observed_profiles: dict[str, list[str]] = {}
        for horizon, profile in cells:
            if profile == "reactive":
                agent = ReactiveSequentialAgent(
                    DeterministicMockLLM(inject_recoverable_error=True)
                )
            else:
                agent = GraphDecisionAgent(
                    DeterministicMockLLM(inject_recoverable_error=True),
                    policy_config=GraphPolicyConfig.for_profile(
                        profile,
                        runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
                    ),
                )
            result = await run_dynamic_episode(
                data,
                models,
                agent,
                DATASET,
                DYNAMIC,
                sequence,
                seed=20260808,
                rotation="rotation_0",
                horizon=horizon,
                strip_historical_decision_state=(
                    profile == "no_persistent_graph_state"
                ),
            )
            self.assertEqual(result.trajectory.terminal_status, "submitted")
            events = [
                dict(step.observation_summary["context"]["public_condition_event"])
                for step in result.trajectory.steps
                if "public_condition_event"
                in step.observation_summary.get("context", {})
            ]
            self.assertEqual(
                [int(event["release_index"]) for event in events],
                [index for index in (3, 6, 9) if index < horizon],
            )
            for event in events:
                events_by_release.setdefault(int(event["release_index"]), []).append(
                    event
                )
            if profile != "reactive":
                states = [
                    str(step.decision_state)
                    for step in result.trajectory.steps
                    if step.decision_state is not None
                ]
                if horizon == 12:
                    observed_profiles[profile] = states
                self.assertEqual(
                    transition_validity(
                        result.trajectory,
                        GraphPolicyConfig.for_profile(
                            profile,
                            runtime_contract=GRAPH_DYNAMIC_RUNTIME_CONTRACT,
                        ),
                    ),
                    1.0,
                )
            for step in result.trajectory.steps:
                event = step.observation_summary.get("context", {}).get(
                    "public_condition_event"
                )
                if event is not None:
                    self.assertLess(
                        int(event["release_index"]),
                        len(step.observation_summary["context"]["replay_sample_ids"]),
                    )

        self.assertEqual(len(cells), 10)
        for payloads in events_by_release.values():
            self.assertEqual(payloads, [payloads[0]] * len(payloads))
        self.assertIn("Revise", observed_profiles["full"])
        self.assertNotIn(
            "Monitor", observed_profiles["no_observation_conditioned_branching"]
        )
        self.assertNotIn(
            "Recover", observed_profiles["no_recovery_revision_edge"]
        )
        self.assertNotEqual(
            observed_profiles["full"], observed_profiles["no_replanning"]
        )


if __name__ == "__main__":
    unittest.main()
