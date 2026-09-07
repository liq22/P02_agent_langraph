#!/usr/bin/env python3
"""Materialize and validate the Generic-base Graph dynamic v2 Mock gate.

The command calls the existing ``run_graph_experiment`` dynamic Mock entry for
the ten registered sequence-0001 cells.  It never selects a provider runtime,
never aggregates task performance, and accepts only the mechanics contract.
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import io
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from phm_agent_benchmark.phase1 import DeterministicMockLLM
try:
    from scripts import run_graph_experiment as graph_runner
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    import run_graph_experiment as graph_runner  # type: ignore[no-redef]


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_FILES = frozenset(
    {
        "run.json",
        "rollout.jsonl",
        "submission.json",
        "metrics.json",
        "failures.jsonl",
        "artifacts.json",
    }
)
EVIDENCE_CLASS = "mechanics_only_not_performance_evidence"
LEGACY_GRAPH_DYNAMIC_RUNTIME_CONTRACT = "phase1_graph_dynamic_generic_ablation_v2"
GUIDANCE_MARKER = "Current decision state:"
EVENT_ID = re.compile(r"occ-\d{8}\Z")


@dataclass(frozen=True, slots=True)
class Cell:
    horizon: int
    registered_name: str
    arm: str
    graph_profile: str
    agent_profile_id: str

    @property
    def key(self) -> str:
        return f"h{self.horizon}:{self.registered_name}"


def load_yaml(path: Path) -> dict[str, Any]:
    return graph_runner._load_dynamic_protocol(path)


def registered_cells(protocol: Mapping[str, Any]) -> tuple[Cell, ...]:
    raw = protocol["experiment_design"]["cells_per_seed_sequence"]
    cells: list[Cell] = []
    for horizon in (3, 6, 12):
        names = raw[f"horizon_{horizon}"]
        for name_value in names:
            name = str(name_value)
            if name == "reactive":
                cells.append(
                    Cell(
                        horizon,
                        name,
                        "reactive",
                        "full",
                        str(
                            protocol["formal_analysis"]["agent_identity"][
                                "reactive_agent_profile_id"
                            ]
                        ),
                    )
                )
                continue
            if not name.startswith("graph_"):
                raise ValueError(f"unsupported registered dynamic cell: {name}")
            profile = name.removeprefix("graph_")
            cells.append(
                Cell(
                    horizon,
                    name,
                    "graph",
                    profile,
                    str(protocol["graph_profiles"][profile]["agent_profile_id"]),
                )
            )
    expected = int(protocol["experiment_design"]["total_cells_per_seed_sequence"])
    if len(cells) != expected or len({cell.key for cell in cells}) != expected:
        raise ValueError("registered dynamic cells are not ten unique units")
    return tuple(cells)


def unit_root(mechanics_root: Path, cell: Cell) -> Path:
    return (
        mechanics_root
        / cell.agent_profile_id
        / "seed_20260808"
        / "rotation_0"
        / f"horizon_{cell.horizon}"
        / "episodes"
        / "sequence-0001"
    )


def _json_contains_key(value: Any, key: str) -> bool:
    if isinstance(value, Mapping):
        return key in value or any(_json_contains_key(item, key) for item in value.values())
    if isinstance(value, list):
        return any(_json_contains_key(item, key) for item in value)
    return False


def audit_outbound_messages(messages: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    guidance_roles: list[str] = []
    decision_state_key_messages = 0
    tool_messages = 0
    for message in messages:
        role = str(message.get("role", ""))
        content = message.get("content")
        if GUIDANCE_MARKER in str(content):
            guidance_roles.append(role)
        if role != "tool" or not isinstance(content, str):
            continue
        tool_messages += 1
        parsed = json.loads(content)
        if _json_contains_key(parsed, "decision_state"):
            decision_state_key_messages += 1
    return {
        "message_count": len(messages),
        "tool_message_count": tool_messages,
        "historical_decision_state_key_messages": decision_state_key_messages,
        "current_state_guidance_count": len(guidance_roles),
        "state_guidance_roles": guidance_roles,
    }


class AuditedDeterministicMockLLM(DeterministicMockLLM):
    """Deterministic Mock with metadata-only request audits (no prompt capture)."""

    active_cell: str | None = None
    request_audits: dict[str, list[dict[str, Any]]] = {}

    async def generate(
        self,
        messages: list[dict[str, Any]],
        *,
        model: str,
        tools: list[dict[str, Any]] | None = None,
    ):
        if self.active_cell is not None:
            self.request_audits.setdefault(self.active_cell, []).append(
                audit_outbound_messages(messages)
            )
        return await super().generate(messages, model=model, tools=tools)


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number} must contain a JSON object")
        rows.append(value)
    return rows


def _sample_refs(value: Any) -> set[str]:
    refs: set[str] = set()
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in {"sample_id", "source_sample_id"} and isinstance(item, str):
                refs.add(item)
            else:
                refs.update(_sample_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.update(_sample_refs(item))
    return refs


def _validate_rollout(
    rows: Sequence[Mapping[str, Any]],
    *,
    horizon: int,
    graph_profile: str | None,
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    actions = [row for row in rows if row.get("event_type") == "action"]
    terminals = [row for row in rows if row.get("event_type") == "terminal"]
    if not actions or len(terminals) != 1 or terminals[0].get("terminal_status") != "submitted":
        raise ValueError("dynamic mechanics rollout must contain actions and one submitted terminal")

    released_prefixes: list[tuple[str, ...]] = []
    events: list[dict[str, Any]] = []
    states: list[str] = []
    for expected_index, row in enumerate(actions):
        if row.get("index") != expected_index:
            raise ValueError("dynamic action indices must be contiguous")
        observation = row.get("observation")
        if not isinstance(observation, Mapping):
            raise ValueError("dynamic action lacks a public observation")
        context = observation.get("context")
        if not isinstance(context, Mapping):
            raise ValueError("dynamic observation context must be a mapping")
        released = context.get("replay_sample_ids")
        cursor = context.get("replay_cursor")
        if (
            not isinstance(released, list)
            or not released
            or type(cursor) is not int
            or cursor not in {len(released) - 1, len(released)}
            or (cursor == len(released) and len(released) != horizon)
            or len(released) > horizon
        ):
            raise ValueError("dynamic observation exposes a malformed released prefix")
        prefix = tuple(str(value) for value in released)
        if len(set(prefix)) != len(prefix):
            raise ValueError("dynamic released prefix contains duplicate sample handles")
        released_prefixes.append(prefix)

        action = row.get("action")
        result = row.get("result")
        if not isinstance(action, Mapping) or not isinstance(result, Mapping):
            raise ValueError("dynamic action/result record has an invalid shape")
        visible = set(prefix)
        for ref in _sample_refs(action.get("arguments", {})) | _sample_refs(
            result.get("output", {})
        ):
            if ref not in visible:
                raise ValueError(f"action/result referenced unreleased sample {ref}")

        event = context.get("public_condition_event")
        if event is not None:
            if not isinstance(event, Mapping) or set(event) != {
                "event",
                "event_id",
                "release_index",
            }:
                raise ValueError("public condition event has an invalid payload")
            payload = dict(event)
            if (
                payload["event"] != "operating_condition_change"
                or not isinstance(payload["event_id"], str)
                or EVENT_ID.fullmatch(payload["event_id"]) is None
                or payload["release_index"] != cursor
                or payload["release_index"] >= len(prefix)
            ):
                raise ValueError("public condition event is unmatched or visible before release")
            events.append(payload)

        state = action.get("decision_state")
        if graph_profile is None:
            if state is not None:
                raise ValueError("Reactive mechanics cell unexpectedly emitted a Graph state")
        else:
            if not isinstance(state, str):
                raise ValueError("Graph mechanics action is missing its decision state")
            states.append(state)

    full = max(released_prefixes, key=len)
    if len(full) != horizon or any(prefix != full[: len(prefix)] for prefix in released_prefixes):
        raise ValueError("dynamic rollout exposed a non-prefix or incomplete replay sequence")
    expected_event_indices = [index for index in (3, 6, 9) if index < horizon]
    observed_event_indices = [int(event["release_index"]) for event in events]
    if observed_event_indices != expected_event_indices:
        raise ValueError("dynamic event releases disagree with the frozen horizon schedule")

    if graph_profile is not None:
        profile = protocol["graph_profiles"][graph_profile]
        reachable = set(str(value) for value in profile["reachable_states"])
        legal = {
            str(source): {str(target) for target in targets}
            for source, targets in profile["legal_transitions"].items()
        }
        if any(state not in reachable for state in states):
            raise ValueError("Graph rollout reached a state excluded by its profile")
        invalid = [
            [source, target]
            for source, target in zip(states, states[1:])
            if target not in legal[source]
        ]
        if invalid:
            raise ValueError(f"Graph rollout contains illegal profile transitions: {invalid}")

    return {
        "action_count": len(actions),
        "terminal_status": "submitted",
        "released_sequence": list(full),
        "event_payloads": events,
        "event_release_indices": observed_event_indices,
        "observed_states": sorted(set(states)),
        "transition_count": max(0, len(states) - 1),
    }


def _validate_outbound_audit(path: Path) -> dict[str, Any]:
    audit = _read_json(path)
    requests = audit.get("requests")
    if not isinstance(requests, list) or not requests:
        raise ValueError("no-persistent outbound audit must contain actual Mock requests")
    if not any(int(request.get("tool_message_count", 0)) > 0 for request in requests):
        raise ValueError("no-persistent outbound audit did not exercise message history")
    for request in requests:
        if (
            request.get("historical_decision_state_key_messages") != 0
            or request.get("current_state_guidance_count") != 1
            or request.get("state_guidance_roles") != ["system"]
        ):
            raise ValueError("no-persistent outbound request retained prior state/guidance")
    return {
        "request_count": len(requests),
        "requests_with_tool_history": sum(
            int(request.get("tool_message_count", 0)) > 0 for request in requests
        ),
        "historical_decision_state_key_messages": 0,
        "prior_state_guidance_messages": 0,
        "current_state_guidance_once_per_request": True,
    }


def validate_gate(
    mechanics_root: Path,
    protocol: Mapping[str, Any],
) -> dict[str, Any]:
    cells = registered_cells(protocol)
    reports: list[dict[str, Any]] = []
    event_payloads: dict[int, list[dict[str, Any]]] = {3: [], 6: [], 9: []}
    sequences: dict[int, list[tuple[str, ...]]] = {3: [], 6: [], 12: []}
    observed_leaves: set[Path] = set()
    no_persistent_audit: dict[str, Any] | None = None

    for cell in cells:
        root = unit_root(mechanics_root, cell)
        leaves = sorted(root.rglob("run.json")) if root.exists() else []
        if len(leaves) != 1:
            raise ValueError(f"{cell.key} must contain exactly one canonical attempt leaf")
        leaf = leaves[0].parent
        observed_leaves.add(leaf.resolve())
        if {path.name for path in leaf.iterdir() if path.is_file()} != CANONICAL_FILES:
            raise ValueError(f"{cell.key} attempt leaf is not exact-six canonical")

        run = _read_json(leaf / "run.json")
        metadata = run.get("metadata")
        if not isinstance(metadata, Mapping):
            raise ValueError(f"{cell.key} run metadata is missing")
        expected_metadata = {
            "runtime_contract": LEGACY_GRAPH_DYNAMIC_RUNTIME_CONTRACT,
            "runtime": "mock",
            "provider": "benchmark-local",
            "model": "deterministic-mock-llm",
            "seed": 20260808,
            "rotation": "rotation_0",
            "horizon": cell.horizon,
            "public_sequence_id": "sequence-0001",
            "sample_id": "sequence-0001",
            "task_id": "online_replay_monitoring",
            "arm": cell.arm,
            "graph_policy_profile": (
                "reactive" if cell.arm == "reactive" else cell.graph_profile
            ),
            "agent_profile_id": cell.agent_profile_id,
            "evidence_class": EVIDENCE_CLASS,
        }
        mismatches = {
            name: {"expected": expected, "observed": metadata.get(name)}
            for name, expected in expected_metadata.items()
            if metadata.get(name) != expected
        }
        if mismatches:
            raise ValueError(f"{cell.key} identity mismatch: {mismatches}")
        if run.get("terminal_status") != "submitted":
            raise ValueError(f"{cell.key} did not reach submitted mechanics terminal")
        task = run.get("task")
        if not isinstance(task, Mapping):
            raise ValueError(f"{cell.key} task contract is missing")
        task_context = task.get("public_context")
        if (
            not isinstance(task_context, Mapping)
            or task_context.get("replay_length") != cell.horizon
            or not isinstance(task_context.get("replay_sample_ids"), list)
            or len(task_context["replay_sample_ids"]) != 1
        ):
            raise ValueError(f"{cell.key} initial task exposed more than the first release")

        rollout = _validate_rollout(
            _read_jsonl(leaf / "rollout.jsonl"),
            horizon=cell.horizon,
            graph_profile=None if cell.arm == "reactive" else cell.graph_profile,
            protocol=protocol,
        )
        sequences[cell.horizon].append(tuple(rollout.pop("released_sequence")))
        for payload in rollout.pop("event_payloads"):
            event_payloads[int(payload["release_index"])].append(payload)
        reports.append(
            {
                "cell": cell.key,
                "agent_profile_id": cell.agent_profile_id,
                "horizon": cell.horizon,
                "attempt_leaf": str(leaf.relative_to(ROOT)),
                "exact_six": True,
                **rollout,
            }
        )

        if cell.registered_name == "graph_no_persistent_graph_state":
            no_persistent_audit = _validate_outbound_audit(
                root / "outbound_request_audit.json"
            )

    all_run_leaves = {path.parent.resolve() for path in mechanics_root.rglob("run.json")}
    if all_run_leaves != observed_leaves or len(observed_leaves) != 10:
        raise ValueError("mechanics root contains a missing, duplicate, or unregistered bundle")
    for horizon, observed in sequences.items():
        if any(sequence != observed[0] for sequence in observed):
            raise ValueError(f"horizon-{horizon} cells do not share one public sequence")
    if not (
        sequences[6][0][:3] == sequences[3][0]
        and sequences[12][0][:6] == sequences[6][0]
    ):
        raise ValueError("horizons are not exact prefixes of one master sequence")
    expected_payload_counts = {3: 8, 6: 6, 9: 6}
    for release_index, payloads in event_payloads.items():
        if (
            len(payloads) != expected_payload_counts[release_index]
            or any(payload != payloads[0] for payload in payloads)
        ):
            raise ValueError(f"release-{release_index} event payloads are not matched")
    if no_persistent_audit is None:
        raise ValueError("no-persistent outbound audit was not validated")

    return {
        "schema_version": "graph_dynamic_mock_acceptance_gate_v2",
        "protocol_id": protocol["protocol_id"],
        "accepted": True,
        "evidence_class": EVIDENCE_CLASS,
        "performance_claims_allowed": False,
        "provider_calls_observed": 0,
        "matrix": {
            "seed": 20260808,
            "rotation": "rotation_0",
            "public_sequence_id": "sequence-0001",
            "expected_cells": 10,
            "observed_exact_six_bundles": len(observed_leaves),
            "horizons": [3, 6, 12],
        },
        "checks": {
            "exact_six_canonical_bundle_per_episode": True,
            "matched_public_events_and_release_indices": True,
            "future_samples_and_events_inaccessible": True,
            "profile_specific_legal_transitions": True,
            "no_persistent_outbound_history_stripped": True,
            "mechanics_only_evidence_class": True,
            "zero_provider_calls": True,
        },
        "no_persistent_outbound_request_audit": no_persistent_audit,
        "cells": reports,
        "claim_boundary": (
            "Accepted provider-free execution mechanics only. This gate contains no "
            "Graph performance estimate and does not complete the formal cohort."
        ),
    }


def _namespace(args: argparse.Namespace, cell: Cell, output: Path) -> argparse.Namespace:
    return argparse.Namespace(
        arm=cell.arm,
        runtime="mock",
        inject_recoverable_error=True,
        graph_profile=cell.graph_profile,
        metadata=str(args.metadata),
        signal=str(args.signal),
        protocol=str(args.protocol),
        dynamic_protocol=args.dynamic_protocol,
        public_sequence_id="sequence-0001",
        horizon=cell.horizon,
        rotation="rotation_0",
        tasks=["online_replay_monitoring"],
        train_samples_per_bearing=8,
        validation_samples_per_bearing=8,
        test_samples_per_bearing=3,
        max_test_bearings=1,
        temperature=0.2,
        max_output_tokens_per_turn=2048,
        local_cli_timeout=300.0,
        runtime_contract=LEGACY_GRAPH_DYNAMIC_RUNTIME_CONTRACT,
        resume_provider_partial=False,
        seed=20260808,
        provider_label="unused_for_mock",
        input_usd_per_million=None,
        output_usd_per_million=None,
        base_url_env="UNUSED_DYNAMIC_MOCK_BASE_URL",
        api_key_env="UNUSED_DYNAMIC_MOCK_API_KEY",
        model_env="UNUSED_DYNAMIC_MOCK_MODEL",
        output=output,
    )


async def materialize(args: argparse.Namespace, protocol: Mapping[str, Any]) -> None:
    original_mock = graph_runner.DeterministicMockLLM
    graph_runner.DeterministicMockLLM = AuditedDeterministicMockLLM
    try:
        for cell in registered_cells(protocol):
            output = unit_root(args.mechanics_root, cell)
            existing = sorted(output.rglob("run.json")) if output.exists() else []
            if existing:
                if len(existing) != 1:
                    raise ValueError(f"{cell.key} contains multiple existing attempts")
                continue
            if output.exists() and any(output.iterdir()):
                raise ValueError(f"{cell.key} has non-resumable partial Mock output")
            AuditedDeterministicMockLLM.active_cell = cell.key
            AuditedDeterministicMockLLM.request_audits[cell.key] = []
            with contextlib.redirect_stdout(io.StringIO()):
                await graph_runner._run(_namespace(args, cell, output))
            if cell.registered_name == "graph_no_persistent_graph_state":
                requests = AuditedDeterministicMockLLM.request_audits[cell.key]
                (output / "outbound_request_audit.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "graph_dynamic_outbound_request_audit_v2",
                            "cell": cell.key,
                            "content_retained": False,
                            "requests": requests,
                        },
                        indent=2,
                        sort_keys=True,
                    )
                    + "\n",
                    encoding="utf-8",
                )
    finally:
        AuditedDeterministicMockLLM.active_cell = None
        graph_runner.DeterministicMockLLM = original_mock


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser()
    value.add_argument("--metadata", type=Path, default=Path("/mnt/e/D01_vibench/metadata.xlsx"))
    value.add_argument("--signal", type=Path, default=Path("/mnt/e/D01_vibench/RM_027_PU.h5"))
    value.add_argument(
        "--protocol",
        type=Path,
        default=ROOT.parent / "p01-phm-agent-benchmark/paper/experiments/datasets/dataset_protocol.yaml",
    )
    value.add_argument(
        "--dynamic-protocol",
        type=Path,
        default=ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v2.yaml",
    )
    value.add_argument(
        "--mechanics-root",
        type=Path,
        default=ROOT / "paper/experiments/runs/mechanics/graph_dynamic_ablation_v2/mock_acceptance",
    )
    value.add_argument("--validate-only", action="store_true")
    return value


def main() -> None:
    args = parser().parse_args()
    protocol = load_yaml(args.dynamic_protocol)
    if not args.validate_only:
        asyncio.run(materialize(args, protocol))
    report = validate_gate(args.mechanics_root, protocol)
    gate_path = args.mechanics_root / "gate.json"
    gate_path.parent.mkdir(parents=True, exist_ok=True)
    gate_path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "accepted": report["accepted"],
                "bundles": report["matrix"]["observed_exact_six_bundles"],
                "evidence_class": report["evidence_class"],
                "gate": str(gate_path),
                "provider_calls": report["provider_calls_observed"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
