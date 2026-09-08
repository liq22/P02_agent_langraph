#!/usr/bin/env python3
"""Render the current Paper-2 mechanics-only evidence table and figure.

The renderer consumes only retained provider-free gates and the current
task-primary dynamic-v3 denominator. It intentionally exposes no task score or
treatment effect, and it fails if the active control is not the Benchmark
Generic base.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

import yaml

try:  # Direct execution places scripts/ rather than the repository on sys.path.
    from run_graph_dynamic_formal_v2 import (
        _parser as dynamic_runner_parser,
        build_dynamic_formal_unit_contract,
    )
    from schedule_graph_dynamic_formal_v2 import (
        build_manifest as build_dynamic_schedule,
        load_protocol as load_dynamic_protocol,
    )
except ModuleNotFoundError:  # Imported as scripts.render_current_mechanics_evidence.
    from scripts.run_graph_dynamic_formal_v2 import (
        _parser as dynamic_runner_parser,
        build_dynamic_formal_unit_contract,
    )
    from scripts.schedule_graph_dynamic_formal_v2 import (
        build_manifest as build_dynamic_schedule,
        load_protocol as load_dynamic_protocol,
    )


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TABLE = ROOT / "paper/assets/tables/p2_current_mechanics_status.md"
DEFAULT_FIGURE = ROOT / "paper/assets/figures/p2_current_mechanics_status.svg"

E0_GATE = ROOT / "paper/experiments/results/p2_e0_generic_base_adapter_equivalence_v2.json"
DYNAMIC_GATE = (
    ROOT
    / "paper/experiments/runs/mechanics/graph_dynamic_ablation_v2/mock_acceptance/gate.json"
)
DYNAMIC_PROTOCOL = ROOT / "paper/experiments/graph_dynamic_ablation_protocol_v3.yaml"
DYNAMIC_FORMAL_ACCEPTANCE = (
    ROOT
    / "paper/experiments/results/graph_dynamic_ablation_v3"
    / "openrouter_north_graph_dynamic_generic_ablation_v3/formal_acceptance.json"
)

CONTROL_LABEL = "Benchmark Generic (Reactive-equivalent)"
TREATMENT_LABEL = "GraphDecisionAgent over the same Generic base"
FORMAL_RUNNER_FOCUSED_TESTS = 17
DYNAMIC_FOCUSED_TESTS = 50


class CurrentMechanicsError(RuntimeError):
    """Raised when a retained gate no longer satisfies the displayed contract."""


def _mapping(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise CurrentMechanicsError(f"{label} must be a mapping")
    return dict(value)


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CurrentMechanicsError(f"cannot load {label}: {path}") from error
    return _mapping(value, label)


def _load_yaml(path: Path, label: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise CurrentMechanicsError(f"cannot load {label}: {path}") from error
    return _mapping(value, label)


def _observed_formal_units(formal_root: Path) -> int:
    if not formal_root.is_dir():
        return 0
    observed = 0
    for unit in formal_root.glob("**/episodes/*"):
        if not unit.is_dir():
            continue
        if any(
            child.is_dir()
            and (child.name.startswith("attempt_") or child.name.startswith("attempt-"))
            for child in unit.iterdir()
        ):
            observed += 1
    return observed


def load_current_mechanics(root: Path = ROOT) -> dict[str, Any]:
    """Return the evidence snapshot after validating its mechanics-only boundary."""

    e0 = _load_json(root / E0_GATE.relative_to(ROOT), "P2-E0-v2 gate")
    if e0.get("schema_version") != "p2_e0_generic_base_adapter_equivalence_v2":
        raise CurrentMechanicsError("P2-E0-v2 schema drifted")
    if e0.get("accepted") is not True or e0.get("provider_calls") != 0:
        raise CurrentMechanicsError("P2-E0-v2 must be accepted and provider-free")
    if e0.get("evidence_class") != (
        "provider_free_real_data_generic_base_adapter_world_mechanics"
    ):
        raise CurrentMechanicsError("P2-E0-v2 is not mechanics-only evidence")
    boundary = _mapping(e0.get("control_boundary"), "P2-E0-v2 control boundary")
    if boundary.get("reactive_direct_base") != "GenericLLMToolAgent":
        raise CurrentMechanicsError("P2-E0-v2 control is not Benchmark Generic")
    if boundary.get("reactive_behavior_overrides") != []:
        raise CurrentMechanicsError("Reactive-equivalent control has behavior overrides")
    if boundary.get("graph_direct_base") != "GenericLLMToolAgent":
        raise CurrentMechanicsError("Graph treatment is not Generic-derived")
    counts = _mapping(e0.get("counts"), "P2-E0-v2 counts")
    control = _mapping(counts.get("reactive"), "P2-E0-v2 control counts")
    graph = _mapping(counts.get("graph"), "P2-E0-v2 Graph counts")
    for label, arm in (("control", control), ("Graph", graph)):
        if arm.get("attempt_leaves") != 16:
            raise CurrentMechanicsError(f"P2-E0-v2 {label} leaves are not 16")
        if arm.get("canonical_action_rows") != 352:
            raise CurrentMechanicsError(f"P2-E0-v2 {label} actions are not 352")
        if _mapping(arm.get("terminal_outcomes"), f"{label} outcomes").get(
            "submitted"
        ) != 16:
            raise CurrentMechanicsError(f"P2-E0-v2 {label} submissions are not 16")

    dynamic = _load_json(
        root / DYNAMIC_GATE.relative_to(ROOT), "dynamic-v2 mechanics gate"
    )
    if dynamic.get("accepted") is not True:
        raise CurrentMechanicsError("dynamic-v2 provider-free mechanics gate is not accepted")
    if dynamic.get("evidence_class") != "mechanics_only_not_performance_evidence":
        raise CurrentMechanicsError("dynamic-v2 gate is not mechanics-only")
    if dynamic.get("performance_claims_allowed") is not False:
        raise CurrentMechanicsError("dynamic-v2 gate improperly allows performance claims")
    if dynamic.get("provider_calls_observed") != 0:
        raise CurrentMechanicsError("dynamic-v2 mechanics gate is not provider-free")
    matrix = _mapping(dynamic.get("matrix"), "dynamic-v2 mechanics matrix")
    cells = dynamic.get("cells")
    if not isinstance(cells, list) or not all(
        isinstance(cell, Mapping) and cell.get("exact_six") is True for cell in cells
    ):
        raise CurrentMechanicsError("dynamic-v2 mechanics cells are not all exact-six")
    if matrix.get("expected_cells") != 10 or len(cells) != 10:
        raise CurrentMechanicsError("dynamic-v2 mechanics gate is not 10/10")

    protocol = load_dynamic_protocol(root / DYNAMIC_PROTOCOL.relative_to(ROOT))
    scheduler = _mapping(protocol.get("formal_scheduler"), "dynamic-v3 scheduler")
    expected_formal = scheduler.get("expected_unique_units")
    if expected_formal != 240:
        raise CurrentMechanicsError("dynamic-v3 formal denominator is not 240")
    implementation = _mapping(
        protocol.get("implementation_status"), "dynamic-v3 implementation status"
    )
    if implementation.get("formal_matrix_scheduler_implemented") is not True:
        raise CurrentMechanicsError("dynamic-v3 formal scheduler is not implemented")
    if implementation.get("formal_runner_implemented") is not True:
        raise CurrentMechanicsError("dynamic-v3 dedicated formal runner is not implemented")
    schedule = build_dynamic_schedule(root / DYNAMIC_PROTOCOL.relative_to(ROOT))
    expected_schedule = {
        "planned_commands": 240,
        "commands_emitted": 240,
        "commands_suppressed": 0,
        "provider_calls_made": 0,
        "runner_invoked": False,
        "environment_values_read": False,
        "filesystem_writes_made": 0,
    }
    for key, expected in expected_schedule.items():
        if schedule.get(key) != expected:
            raise CurrentMechanicsError(
                f"dynamic-v3 dry schedule drifted at {key}={expected!r}"
            )
    readiness = _mapping(schedule.get("runtime_readiness"), "dynamic-v3 readiness")
    if readiness.get("ready") is not True:
        raise CurrentMechanicsError("dynamic-v3 dedicated formal runner is not ready")
    first_argv = schedule["units"][0]["argv"]
    if not isinstance(first_argv, list) or len(first_argv) < 3:
        raise CurrentMechanicsError("dynamic-v3 dry schedule lacks its first argv")
    validate_args = dynamic_runner_parser().parse_args(
        [str(value) for value in first_argv[2:]] + ["--validate-only"]
    )
    validate_contract = build_dynamic_formal_unit_contract(validate_args)
    expected_validate_only = {
        "provider_calls_performed": False,
        "environment_values_read": False,
        "probe_evidence_read": False,
        "filesystem_writes_performed": False,
    }
    for key, expected in expected_validate_only.items():
        if validate_contract.get(key) != expected:
            raise CurrentMechanicsError(
                f"dynamic-v3 validate-only contract drifted at {key}={expected!r}"
            )
    output_contract = _mapping(protocol.get("output_contract"), "dynamic output contract")
    formal_root = root / str(output_contract.get("formal_root"))
    observed_formal = _observed_formal_units(formal_root)
    formal_gate_path = root / DYNAMIC_FORMAL_ACCEPTANCE.relative_to(ROOT)
    formal_gate = (
        _load_json(formal_gate_path, "dynamic-v3 formal acceptance")
        if formal_gate_path.is_file()
        else {"accepted": False}
    )
    if observed_formal > 0 and not formal_gate_path.is_file():
        raise CurrentMechanicsError(
            "observed dynamic-v3 formal units lack a fail-closed acceptance artifact"
        )
    if observed_formal == 0 and formal_gate.get("accepted") is not False:
        raise CurrentMechanicsError("empty dynamic-v3 formal cohort is not fail-closed")

    return {
        "control_label": CONTROL_LABEL,
        "treatment_label": TREATMENT_LABEL,
        "e0": {
            "accepted": True,
            "exact_six_total": int(counts["exact_six_attempt_leaves_total"]),
            "matched_keys_per_arm": int(counts["matched_statistical_episode_keys"]),
            "actions_per_arm": int(control["canonical_action_rows"]),
            "submitted_per_arm": int(control["terminal_outcomes"]["submitted"]),
            "provider_calls": int(e0["provider_calls"]),
        },
        "dynamic_v3": {
            "mechanics_accepted": True,
            "mechanics_observed": len(cells),
            "mechanics_expected": int(matrix["expected_cells"]),
            "formal_observed": observed_formal,
            "formal_expected": int(expected_formal),
            "formal_runner_implemented": True,
            "runtime_ready": True,
            "planned_commands": int(schedule["planned_commands"]),
            "dry_run_commands_emitted": int(schedule["commands_emitted"]),
            "commands_invoked": 0,
            "environment_values_read": False,
            "probe_evidence_read": False,
            "provider_calls": 0,
            "filesystem_writes": 0,
            "formal_runner_focused_tests": FORMAL_RUNNER_FOCUSED_TESTS,
            "dynamic_focused_tests": DYNAMIC_FOCUSED_TESTS,
            "formal_accepted": formal_gate.get("accepted") is True,
            "mock_provider_calls": int(dynamic["provider_calls_observed"]),
        },
        "performance_claims_allowed": False,
    }


def render_table(status: Mapping[str, Any]) -> str:
    e0 = _mapping(status.get("e0"), "status.e0")
    dynamic = _mapping(status.get("dynamic_v3"), "status.dynamic_v3")
    return "\n".join(
        [
            "# Current provider-free mechanics evidence",
            "",
            "| Gate | Matched policies | Materialized mechanics | Formal coverage | Claim boundary |",
            "|---|---|---:|---:|---|",
            (
                f"| P2-E0-v2 | {status['control_label']} / {status['treatment_label']} | "
                f"{e0['exact_six_total']} exact-six leaves "
                f"({e0['matched_keys_per_arm']} per arm), "
                f"{e0['actions_per_arm']} actions and {e0['submitted_per_arm']} submitted "
                "terminal mechanics per arm | Not a provider-bound formal cohort | "
                "Accepted adapter/world equivalence mechanics only |"
            ),
            (
                f"| Dynamic-v3 | {status['control_label']} plus the full and four "
                f"Graph profiles | {dynamic['mechanics_observed']}/"
                f"{dynamic['mechanics_expected']} exact-six Mock cells, "
                f"{dynamic['mock_provider_calls']} provider calls; dedicated formal "
                f"runner {dynamic['formal_runner_focused_tests']}/"
                f"{dynamic['formal_runner_focused_tests']} and dynamic-focused "
                f"{dynamic['dynamic_focused_tests']}/{dynamic['dynamic_focused_tests']} | "
                f"runner ready; {dynamic['dry_run_commands_emitted']}/"
                f"{dynamic['planned_commands']} dry-run commands emitted, "
                f"{dynamic['commands_invoked']} invoked; "
                f"{dynamic['formal_observed']}/{dynamic['formal_expected']} formal units; "
                "formal gate not accepted | Event routing and profile mechanics only |"
            ),
            "",
            "Neither row contains a task-performance estimate or a Graph treatment effect. "
            "Submission counts above are terminal-path mechanics, not outcome quality.",
            "",
        ]
    )


def render_svg(status: Mapping[str, Any]) -> str:
    e0 = _mapping(status.get("e0"), "status.e0")
    dynamic = _mapping(status.get("dynamic_v3"), "status.dynamic_v3")
    return "\n".join(
        [
            '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="470" viewBox="0 0 1200 470" role="img" aria-labelledby="title desc">',
            '<title id="title">Current Paper-2 provider-free mechanics evidence</title>',
            '<desc id="desc">P2-E0-v2 adapter and world equivalence mechanics are accepted; dynamic-v3 retains ten of ten unchanged v2 Mock mechanics cells and has zero of 240 formal units. No performance claim is supported.</desc>',
            '<rect width="1200" height="470" fill="#f8fafc"/>',
            '<text x="600" y="42" text-anchor="middle" font-family="sans-serif" font-size="23" font-weight="700" fill="#0f172a">Current P2 evidence: mechanics, not performance</text>',
            '<text x="600" y="69" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#475569">Benchmark Generic (Reactive-equivalent) is the control; GraphDecisionAgent is the Generic-derived treatment.</text>',
            '<g data-gate="p2-e0-v2">',
            '<rect x="55" y="105" width="520" height="245" rx="18" fill="#ffffff" stroke="#0f766e" stroke-width="2"/>',
            '<text x="85" y="143" font-family="sans-serif" font-size="20" font-weight="700" fill="#115e59">P2-E0-v2</text>',
            '<text x="85" y="172" font-family="sans-serif" font-size="14" fill="#334155">Generic-base adapter/world equivalence</text>',
            f'<text data-e0-exact-six="{e0["exact_six_total"]}" x="85" y="226" font-family="sans-serif" font-size="36" font-weight="700" fill="#0f766e">{e0["exact_six_total"]} exact-six</text>',
            f'<text x="85" y="258" font-family="sans-serif" font-size="15" fill="#334155">{e0["matched_keys_per_arm"]} matched keys · {e0["actions_per_arm"]} actions · {e0["submitted_per_arm"]} submitted terminals per arm</text>',
            '<text x="85" y="298" font-family="sans-serif" font-size="14" fill="#64748b">Accepted provider-free mechanics gate</text>',
            '<text x="85" y="326" font-family="sans-serif" font-size="14" font-weight="700" fill="#b45309">No P2-E1 or performance estimate</text>',
            '</g>',
            '<g data-gate="dynamic-v3">',
            '<rect x="625" y="105" width="520" height="245" rx="18" fill="#ffffff" stroke="#7c3aed" stroke-width="2"/>',
            '<text x="655" y="143" font-family="sans-serif" font-size="20" font-weight="700" fill="#6d28d9">Dynamic-v3</text>',
            '<text x="655" y="172" font-family="sans-serif" font-size="14" fill="#334155">Public-event routing and five Graph profiles</text>',
            f'<text data-mechanics-observed="{dynamic["mechanics_observed"]}" x="655" y="226" font-family="sans-serif" font-size="36" font-weight="700" fill="#6d28d9">{dynamic["mechanics_observed"]}/{dynamic["mechanics_expected"]} Mock</text>',
            f'<text data-formal-observed="{dynamic["formal_observed"]}" data-formal-expected="{dynamic["formal_expected"]}" x="655" y="270" font-family="sans-serif" font-size="31" font-weight="700" fill="#be123c">{dynamic["formal_observed"]}/{dynamic["formal_expected"]} formal</text>',
            f'<text data-formal-runner-ready="true" data-planned-commands="{dynamic["planned_commands"]}" data-emitted-commands="{dynamic["dry_run_commands_emitted"]}" data-invoked-commands="{dynamic["commands_invoked"]}" x="655" y="303" font-family="sans-serif" font-size="14" fill="#64748b">Runner ready · {dynamic["dry_run_commands_emitted"]}/{dynamic["planned_commands"]} dry-run commands · {dynamic["commands_invoked"]} invoked</text>',
            f'<text data-provider-calls="{dynamic["provider_calls"]}" data-formal-runner-tests="{dynamic["formal_runner_focused_tests"]}" data-dynamic-tests="{dynamic["dynamic_focused_tests"]}" x="655" y="329" font-family="sans-serif" font-size="14" font-weight="700" fill="#b45309">{dynamic["formal_runner_focused_tests"]}/{dynamic["formal_runner_focused_tests"]} runner · {dynamic["dynamic_focused_tests"]}/{dynamic["dynamic_focused_tests"]} dynamic checks · no formal result</text>',
            '</g>',
            '<rect x="55" y="382" width="1090" height="54" rx="12" fill="#fff7ed" stroke="#fb923c"/>',
            '<text x="600" y="415" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="700" fill="#9a3412">Evidence boundary: executable mechanics only — no task score and no Graph treatment effect</text>',
            '</svg>',
            '',
        ]
    )


def write_assets(table_path: Path, figure_path: Path) -> dict[str, Any]:
    status = load_current_mechanics()
    table_path.parent.mkdir(parents=True, exist_ok=True)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text(render_table(status), encoding="utf-8")
    figure_path.write_text(render_svg(status), encoding="utf-8")
    return status


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--table", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--figure", type=Path, default=DEFAULT_FIGURE)
    args = parser.parse_args()
    write_assets(args.table, args.figure)


if __name__ == "__main__":
    main()
