from __future__ import annotations

import asyncio
import csv
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

from phm_agent_benchmark.phase1 import Budget
from phm_agent_benchmark.phase1.experiment import build_evaluator_assignments

from scripts.run_graph_experiment import (
    P2_E8_DATASET_ID,
    P2_E8_PROFILE_ID,
    P2_E8_RUNTIME_CONTRACT,
    _active_cohort_contract,
    _open_data_port,
    _run,
    _runtime_identity,
    build_parser,
)


ROOT = Path(__file__).resolve().parents[1]
CROSS_PROTOCOL = (
    ROOT / "paper/experiments/graph_cross_dataset_replay_protocol_v3.yaml"
)
SOURCE_PROTOCOL = (
    ROOT.parent
    / "p01-phm-agent-benchmark"
    / "paper/experiments/datasets/ottawa_uored_v5/phase1_monitoring_protocol_v1.yaml"
)
SOURCE_COLUMNS = [
    "Accelerometer",
    "Acoustic",
    "Speed",
    "Load",
    "Temperature Difference",
]
PRIVATE_FIELDS = [
    "Id",
    "Dataset_id",
    "Name",
    "File",
    "FolderPath",
    "Visiable",
    "Label",
    "Domain_id",
    "Sample_rate",
    "Sample_lenth",
    "Channel",
    "Fault_Diagnosis",
    "Anomaly_Detection",
    "Remaining_Life",
    "Digital_Twin_Prediction",
    "SourceAsset",
    "SourceDiagnosisLabel",
]


def _write_fixture(root: Path) -> tuple[Path, Path, Path]:
    protocol = yaml.safe_load(SOURCE_PROTOCOL.read_text(encoding="utf-8"))
    protocol["dataset"].update(
        {
            "source_records_verified": 9,
            "records": 9,
            "physical_bearings": 3,
            "source_state_counts": {
                "healthy": 3,
                "developing_fault": 3,
                "faulty": 3,
            },
            "sample_length": 8,
        }
    )
    protocol["window_protocol"].update(
        {
            "start_point": 0,
            "end_point": 8,
            "max_returned_points": 8,
            "selected_window_duration_seconds": 8 / 42000,
        }
    )
    protocol["split"]["folds"] = {
        "fold_a": ["UO1"],
        "fold_b": ["UO2"],
        "fold_c": ["UO3"],
    }
    protocol["split"]["rotations"] = [
        {
            "run": "rotation_0",
            "train": ["fold_a"],
            "validation": "fold_b",
            "test": "fold_c",
        },
        {
            "run": "rotation_1",
            "train": ["fold_b"],
            "validation": "fold_c",
            "test": "fold_a",
        },
        {
            "run": "rotation_2",
            "train": ["fold_c"],
            "validation": "fold_a",
            "test": "fold_b",
        },
    ]
    required = protocol["activation_gate"]["required_report_values"]
    required.update(
        {
            "records": 9,
            "physical_asset_count": 3,
            "signals_validated": 9,
            "opaque_sample_handles_validated": 9,
        }
    )

    signal_root = root / "private_signals"
    metadata_rows: list[dict[str, object]] = []
    labels = ("healthy", "developing_fault", "faulty")
    for asset_index, asset in enumerate(("UO1", "UO2", "UO3"), start=1):
        folder = signal_root / "Data" / asset
        folder.mkdir(parents=True)
        for state_index, label in enumerate(labels):
            filename = f"state_{state_index}.csv"
            with (folder / filename).open("w", encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(SOURCE_COLUMNS)
                for row_index in range(8):
                    writer.writerow(
                        [
                            asset_index * 100 + state_index * 10 + row_index,
                            row_index + 0.5,
                            1750,
                            400,
                            row_index / 10,
                        ]
                    )
            metadata_rows.append(
                {
                    "Id": f"private-{asset}-{label}",
                    "Dataset_id": P2_E8_DATASET_ID,
                    "Name": protocol["dataset"]["provider_name"],
                    "File": filename,
                    "FolderPath": f"Data/{asset}",
                    "Visiable": 1,
                    "Label": int(label != "healthy"),
                    "Domain_id": 1,
                    "Sample_rate": 42000,
                    "Sample_lenth": 8,
                    "Channel": 1,
                    "Fault_Diagnosis": 0,
                    "Anomaly_Detection": 0,
                    "Remaining_Life": 0,
                    "Digital_Twin_Prediction": 0,
                    "SourceAsset": asset,
                    "SourceDiagnosisLabel": label,
                }
            )

    metadata = root / "private_metadata.csv"
    with metadata.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=PRIVATE_FIELDS)
        writer.writeheader()
        writer.writerows(metadata_rows)

    protocol_path = root / "ottawa_protocol.yaml"
    protocol_path.write_text(
        yaml.safe_dump(protocol, sort_keys=False), encoding="utf-8"
    )
    readiness = {
        "schema_version": protocol["activation_gate"]["readiness_report_schema"],
        "dataset_id": P2_E8_DATASET_ID,
        "projection_id": protocol["dataset"]["projection_id"],
        "records": 9,
        "physical_asset_count": 3,
        "value_columns": ["Accelerometer"],
        "source_columns": SOURCE_COLUMNS,
        "sample_rate_hz": 42000,
        "sample_length": 8,
        "channels": 1,
        "signals_validated": 9,
        "opaque_sample_handles_validated": 9,
        "data_port_ready": True,
    }
    readiness_path = root / "private_readiness.json"
    readiness_path.write_text(json.dumps(readiness), encoding="utf-8")
    return protocol_path, metadata, signal_root


def _args(protocol: Path, output: Path, *, runtime: str = "mock"):
    values = [
        "--arm",
        "reactive",
        "--runtime",
        runtime,
        "--protocol",
        str(protocol),
        "--cross-dataset-protocol",
        str(CROSS_PROTOCOL),
        "--dataset-id",
        P2_E8_DATASET_ID,
        "--data-backend",
        "csv_directory",
        "--metadata-env",
        "PHM_OTTAWA_METADATA",
        "--signal-env",
        "PHM_OTTAWA_SIGNAL_ROOT",
        "--data-readiness-env",
        "PHM_OTTAWA_READINESS",
        "--experiment-profile-id",
        P2_E8_PROFILE_ID,
        "--rotation",
        "rotation_0",
        "--tasks",
        "online_replay_monitoring",
        "--train-samples-per-bearing",
        "1",
        "--validation-samples-per-bearing",
        "1",
        "--test-samples-per-bearing",
        "3",
        "--runtime-contract",
        P2_E8_RUNTIME_CONTRACT,
        "--seed",
        "20260808",
        "--output",
        str(output),
    ]
    if runtime == "openai":
        values.extend(
            [
                "--provider-label",
                "openrouter-free",
                "--input-usd-per-million",
                "0",
                "--output-usd-per-million",
                "0",
            ]
        )
    return build_parser().parse_args(values)


class GraphCrossDatasetRuntimeTests(unittest.TestCase):
    def test_csv_dataport_builds_private_ordered_assignments_and_path_free_identity(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path, metadata, signal_root = _write_fixture(root)
            readiness = root / "private_readiness.json"
            protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
            args = _args(protocol_path, root / "output")
            environment = {
                "PHM_OTTAWA_METADATA": str(metadata),
                "PHM_OTTAWA_SIGNAL_ROOT": str(signal_root),
                "PHM_OTTAWA_READINESS": str(readiness),
            }
            with mock.patch.dict(os.environ, environment, clear=False):
                with _open_data_port(args, protocol) as data:
                    public_rows = data.search_samples({}, 20)
                    public_text = json.dumps(public_rows, sort_keys=True)
                    self.assertEqual(len(public_rows), 9)
                    self.assertNotIn("private-UO", public_text)
                    self.assertNotIn("SourceAsset", public_text)
                    self.assertNotIn("SourceDiagnosisLabel", public_text)

                    assignments = build_evaluator_assignments(
                        data,
                        protocol,
                        "rotation_0",
                        tasks=["online_replay_monitoring"],
                        test_samples_per_bearing=3,
                    )
                    self.assertEqual(len(assignments), 1)
                    assignment = next(iter(assignments.values()))
                    self.assertEqual(assignment["bearing_id"], "UO3")
                    self.assertEqual(len(assignment["sample_ids"]), 3)
                    self.assertEqual(
                        list(assignment["private_target"].values()), [0, 1, 1]
                    )
                    artifact = data.read_window(
                        {
                            "sample_id": assignment["sample_ids"][0],
                            "start": 0,
                            "end": 8,
                            "channels": [0],
                            "max_points": 8,
                        }
                    )
                    self.assertEqual(artifact.signal.sample_count, 8)
                    self.assertEqual(artifact.signal.channel_count, 1)

                inference, _base_resume, model_profile = _runtime_identity(args)
                profile, identity, _resume = _active_cohort_contract(
                    args,
                    protocol,
                    inference,
                    core_budget=Budget(),
                    monitoring_budget=Budget(
                        max_tool_calls=72,
                        max_window_reads=3,
                        max_operator_calls=50,
                        max_model_calls=3,
                        max_llm_turns=72,
                    ),
                    test_samples_per_bearing=3,
                    matches_formal_sampling=True,
                    model_profile=model_profile,
                )
            self.assertEqual(profile["data_backend"], "csv_directory")
            self.assertEqual(profile["experiment_profile_id"], P2_E8_PROFILE_ID)
            self.assertEqual(
                identity["data_binding"],
                {
                    "metadata_environment": "PHM_OTTAWA_METADATA",
                    "signal_environment": "PHM_OTTAWA_SIGNAL_ROOT",
                    "readiness_environment": "PHM_OTTAWA_READINESS",
                },
            )
            serialized = json.dumps({"profile": profile, "identity": identity})
            self.assertNotIn(str(metadata), serialized)
            self.assertNotIn(str(signal_root), serialized)
            self.assertNotIn(str(readiness), serialized)

    def test_openai_formal_path_blocks_before_output_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            protocol_path, metadata, signal_root = _write_fixture(root)
            output = root / "must-not-exist"
            args = _args(protocol_path, output, runtime="openai")
            environment = {
                "PHM_OTTAWA_METADATA": str(metadata),
                "PHM_OTTAWA_SIGNAL_ROOT": str(signal_root),
                "PHM_OTTAWA_READINESS": str(root / "private_readiness.json"),
                "LLM_BASE_URL": "https://openrouter.ai/api/v1",
                "LLM_API_KEY": "not-used",
                "LLM_MODEL": "cohere/north-mini-code:free",
            }
            with mock.patch.dict(os.environ, environment, clear=False):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "explicit_provider_destination_and_payload_egress_authorization_required",
                ):
                    asyncio.run(_run(args))
            self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
