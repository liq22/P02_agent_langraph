from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from phm_agent_benchmark import Budget, EvaluatorResult, Rollout, RolloutEvent, TaskSpec
from phm_agent_benchmark.rollout_io import write_run_bundle
from scripts.summarize_graph_states import read_rows, summarize


TASK_ID = "cold_start_fault_diagnosis"


def _write_graph_run(
    root: Path,
    *,
    seed: int,
    rotation: str,
    sample_id: str,
    profile: str,
    states: list[str],
) -> Path:
    run_dir = root / f"seed-{seed}-{rotation}-{profile}"
    task = TaskSpec(
        task_id=TASK_ID,
        task_type=TASK_ID,
        instruction="Diagnose one public vibration episode.",
        budget=Budget(),
    )
    rollout = Rollout(TASK_ID, "graph-guided-phm-agent")
    payload = {"label": "healthy", "supporting_refs": []}
    for index, state in enumerate(states):
        submitted = index == len(states) - 1
        rollout.steps.append(
            RolloutEvent(
                index=index,
                observation_summary={"step": index},
                action="tool_call",
                tool_name=(
                    "submit"
                    if submitted
                    else "data.read_window"
                    if index == 0
                    else "op.list"
                ),
                tool_args=payload if submitted else {},
                tool_result=payload if submitted else {"ok": True},
                decision_state=state,
            )
        )
    rollout.submission = payload
    rollout.terminal_status = "submitted"
    evaluation = EvaluatorResult(
        task_id=TASK_ID,
        task_metrics={"submission": 1.0},
        rollout_metrics={"steps": float(len(states))},
        terminal_status="submitted",
    )
    write_run_bundle(
        run_dir
        / "episodes"
        / rotation
        / sample_id
        / TASK_ID
        / "attempt-000",
        run_id=f"{seed}-{rotation}-{sample_id}-attempt-000",
        task=task,
        rollout=rollout,
        evaluation=evaluation,
        run_metadata={
            "model": "deterministic-mock-llm",
            "provider": "benchmark-local",
            "inference_protocol": "mock-tools",
            "thinking_mode": "not_applicable",
            "dataset_protocol": "phm_agent_dataset_protocol_v1",
            "runtime_contract": "runtime-v6",
            "seed": seed,
            "started_at": "2026-08-13T00:00:00+00:00",
            "ended_at": "2026-08-13T00:00:01+00:00",
            "rotation": rotation,
            "sample_id": sample_id,
            "task_id": TASK_ID,
            "episode_key": [rotation, sample_id, TASK_ID],
            "attempt_index": 0,
            "arm": "graph",
            "graph_policy_profile": profile,
        },
    )
    (run_dir / "run_manifest.json").write_text(
        json.dumps(
            {
                "arm": "graph",
                "graph_policy_profile": profile,
                "seed": seed,
                "rotation": rotation,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return run_dir


class CanonicalGraphStateSummaryTest(unittest.TestCase):
    def test_reads_canonical_run_dirs_and_cli_uses_required_flag(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = _write_graph_run(
                root,
                seed=20260808,
                rotation="rotation_0",
                sample_id="sample-a",
                profile="full",
                states=["Inspect", "Monitor", "Revise", "Analyze"],
            )
            second = _write_graph_run(
                root,
                seed=20260809,
                rotation="rotation_1",
                sample_id="sample-b",
                profile="full",
                states=["Inspect", "Hypothesize", "Analyze", "Check", "Submit"],
            )

            rows = read_rows([first, second])
            result = summarize(rows)
            self.assertEqual(result[TASK_ID]["episodes"], 2)
            self.assertEqual(result[TASK_ID]["mean_transition_validity"], 1.0)
            self.assertIn("Monitor", result[TASK_ID]["state_coverage"])
            self.assertIn("Revise", result[TASK_ID]["state_coverage"])
            self.assertNotIn("bearing_id", rows[0])
            self.assertNotIn("private_target", rows[0])

            script = Path(__file__).resolve().parents[1] / "scripts/summarize_graph_states.py"
            help_result = subprocess.run(
                [sys.executable, str(script), "--help"],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("--run-dirs", help_result.stdout)
            output_json = root / "state-summary.json"
            output_table = root / "state-summary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--run-dirs",
                    str(first),
                    str(second),
                    "--output-json",
                    str(output_json),
                    "--output-table",
                    str(output_table),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                json.loads(output_json.read_text(encoding="utf-8"))[TASK_ID][
                    "episodes"
                ],
                2,
            )
            self.assertIn("| Monitor |", output_table.read_text(encoding="utf-8"))

    def test_refuses_profile_pooling_and_duplicate_cohort_units(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            full = _write_graph_run(
                root,
                seed=20260808,
                rotation="rotation_0",
                sample_id="sample-a",
                profile="full",
                states=["Inspect", "Hypothesize"],
            )
            ablation = _write_graph_run(
                root,
                seed=20260809,
                rotation="rotation_1",
                sample_id="sample-b",
                profile="no_replanning",
                states=["Inspect", "Hypothesize"],
            )
            with self.assertRaisesRegex(ValueError, "cannot pool"):
                read_rows([full, ablation])

            duplicate = _write_graph_run(
                root,
                seed=20260808,
                rotation="rotation_0",
                sample_id="sample-c",
                profile="no_replanning",
                states=["Inspect", "Hypothesize"],
            )
            with self.assertRaisesRegex(ValueError, "duplicate Graph cohort unit"):
                read_rows([full, duplicate])


if __name__ == "__main__":
    unittest.main()
