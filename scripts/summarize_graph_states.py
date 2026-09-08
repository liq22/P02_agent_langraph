#!/usr/bin/env python3
"""Aggregate observable graph states from canonical episode bundles."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from phm_agent_benchmark.rollout_io import read_cohort_rollout_views
from phm_graph_agent import ALLOWED_TRANSITIONS, STATES
from phm_graph_agent.state import GRAPH_POLICY_PROFILES


def _run_contract(run_dir: Path) -> tuple[int, str, str]:
    manifest_path = run_dir / "run_manifest.json"
    if not manifest_path.is_file():
        raise ValueError(f"missing run manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, Mapping):
        raise ValueError(f"run manifest must contain one object: {manifest_path}")
    if manifest.get("arm") != "graph":
        raise ValueError(f"state summary accepts only Graph treatment runs: {run_dir}")
    profile = manifest.get("graph_policy_profile")
    if profile not in GRAPH_POLICY_PROFILES:
        raise ValueError(f"missing or unknown graph policy profile: {run_dir}")
    seed = manifest.get("seed")
    rotation = manifest.get("rotation")
    if type(seed) is not int or not isinstance(rotation, str) or not rotation:
        raise ValueError(f"run manifest lacks a valid seed/rotation: {run_dir}")
    return seed, rotation, str(profile)


def read_rows(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    profiles: set[str] = set()
    cohort_units: set[tuple[int, str]] = set()
    for run_dir in paths:
        seed, rotation, profile = _run_contract(run_dir)
        unit = (seed, rotation)
        if unit in cohort_units:
            raise ValueError(f"duplicate Graph cohort unit: seed={seed}, rotation={rotation}")
        cohort_units.add(unit)
        profiles.add(profile)
        for public_row in read_cohort_rollout_views(run_dir):
            if public_row["rotation"] != rotation:
                raise ValueError(
                    f"episode rotation disagrees with run manifest: {run_dir}"
                )
            states = [
                str(step["decision_state"])
                for step in public_row["trajectory"]["steps"]
                if isinstance(step.get("decision_state"), str)
                and step["decision_state"].strip()
            ]
            unknown = sorted(set(states) - set(STATES))
            if unknown:
                raise ValueError(f"unknown graph states in {run_dir}: {unknown}")
            rows.append(
                {
                    "seed": seed,
                    "rotation": public_row["rotation"],
                    "sample_id": public_row["sample_id"],
                    "task_id": public_row["task_id"],
                    "graph_policy_profile": profile,
                    "states": states,
                    "recover_state_count": states.count("Recover"),
                }
            )
    if len(profiles) > 1:
        raise ValueError(f"cannot pool graph policy profiles: {sorted(profiles)}")
    if not rows:
        raise ValueError("no graph-state rows were found")
    return rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    profiles = {row.get("graph_policy_profile") for row in rows}
    if None in profiles or len(profiles) != 1:
        raise ValueError("state rows must contain exactly one graph policy profile")
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["task_id"])].append(row)
    result: dict[str, Any] = {}
    for task_id, task_rows in sorted(grouped.items()):
        validities = [recompute_transition_validity(row.get("states", [])) for row in task_rows]
        recover_counts = [int(row["recover_state_count"]) for row in task_rows]
        total_steps = sum(len(row.get("states", [])) for row in task_rows)
        result[task_id] = {
            "episodes": len(task_rows),
            "mean_transition_validity": sum(validities) / len(validities),
            "all_transitions_valid_rate": sum(value == 1.0 for value in validities)
            / len(validities),
            "recover_episode_rate": sum(value > 0 for value in recover_counts)
            / len(recover_counts),
            "mean_recover_visits": sum(recover_counts) / len(recover_counts),
            "state_coverage": sorted(
                {state for row in task_rows for state in row.get("states", [])}
            ),
            "state_step_occupancy_proportion": {
                state: (
                    sum(row.get("states", []).count(state) for row in task_rows)
                    / total_steps
                    if total_steps
                    else 0.0
                )
                for state in STATES
            },
            "state_episode_visitation_rate": {
                state: sum(state in row.get("states", []) for row in task_rows)
                / len(task_rows)
                for state in STATES
            },
        }
    return result


def recompute_transition_validity(states: list[str]) -> float:
    """Derive validity from the raw state sequence and current executable graph."""
    if not states:
        return 0.0
    if len(states) == 1:
        return 1.0
    valid = sum(
        right in ALLOWED_TRANSITIONS.get(left, set())
        for left, right in zip(states, states[1:])
    )
    return valid / (len(states) - 1)


def markdown(summary: dict[str, Any]) -> str:
    lines = [
        "| Task | Episodes | Transition validity | All-valid rate | Recover episode rate | Mean recover visits | State coverage |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for task_id, values in summary.items():
        lines.append(
            f"| {task_id} | {values['episodes']} | "
            f"{values['mean_transition_validity']:.4f} | "
            f"{values['all_transitions_valid_rate']:.4f} | "
            f"{values['recover_episode_rate']:.4f} | "
            f"{values['mean_recover_visits']:.4f} | "
            f"{', '.join(values['state_coverage'])} |"
        )
    lines.extend(
        [
            "",
            "| Task | State | Step occupancy proportion | Episode visitation rate |",
            "|---|---|---:|---:|",
        ]
    )
    for task_id, values in summary.items():
        for state in STATES:
            lines.append(
                f"| {task_id} | {state} | "
                f"{values['state_step_occupancy_proportion'][state]:.4f} | "
                f"{values['state_episode_visitation_rate'][state]:.4f} |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--run-dirs",
        nargs="+",
        type=Path,
        required=True,
        help="Graph run directories containing canonical episode bundles.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-table", type=Path, required=True)
    args = parser.parse_args()
    summary = summarize(read_rows(args.run_dirs))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_table.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    args.output_table.write_text(markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
