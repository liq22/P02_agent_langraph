#!/usr/bin/env python3
"""Render the shared eight-state topology and its two active relations."""

from __future__ import annotations

from collections.abc import Mapping, Set
from pathlib import Path

from phm_graph_agent.state import (
    ALLOWED_TRANSITIONS,
    DYNAMIC_LEGAL_TRANSITIONS,
    STATES,
)


EXPECTED_STATES = (
    "Inspect",
    "Hypothesize",
    "Analyze",
    "Check",
    "Monitor",
    "Revise",
    "Recover",
    "Submit",
)


def _render_matrix(
    *,
    relation_id: str,
    title: str,
    subtitle: str,
    transitions: Mapping[str, Set[str]],
    matrix_x: int,
    matrix_y: int,
    legal_fill: str,
) -> list[str]:
    """Render one labelled 8x8 relation without conflating runtime profiles."""

    cell = 42
    center_x = matrix_x + len(EXPECTED_STATES) * cell / 2
    lines = [
        f'<g data-transition-relation="{relation_id}">',
        f'<text x="{center_x}" y="352" text-anchor="middle" font-family="sans-serif" font-size="14" fill="#0f172a">{title}</text>',
        f'<text x="{center_x}" y="374" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#64748b">{subtitle}</text>',
    ]
    for column, target in enumerate(EXPECTED_STATES):
        x = matrix_x + column * cell + cell / 2
        lines.append(
            f'<text x="{x}" y="424" text-anchor="end" transform="rotate(-45 {x} 424)" '
            f'font-family="sans-serif" font-size="10">{target}</text>'
        )
    for row, source in enumerate(EXPECTED_STATES):
        y = matrix_y + row * cell
        lines.append(
            f'<text x="{matrix_x - 14}" y="{y + 27}" text-anchor="end" '
            f'font-family="sans-serif" font-size="11">{source}</text>'
        )
        for column, target in enumerate(EXPECTED_STATES):
            x = matrix_x + column * cell
            legal = target in transitions[source]
            fill = legal_fill if legal else "#f8fafc"
            legal_text = str(legal).lower()
            lines.append(
                f'<rect data-edge="{relation_id}:{source}-to-{target}" '
                f'data-relation="{relation_id}" data-legal="{legal_text}" '
                f'x="{x}" y="{y}" width="{cell}" height="{cell}" '
                f'fill="{fill}" stroke="#cbd5e1"/>'
            )
            if legal:
                lines.append(
                    f'<circle cx="{x + cell / 2}" cy="{y + cell / 2}" r="6" fill="white"/>'
                )
    edge_count = sum(len(targets) for targets in transitions.values())
    lines.extend(
        [
            f'<text x="{center_x}" y="810" text-anchor="middle" font-family="sans-serif" '
            f'font-size="12" fill="#334155">{edge_count} declared legal transitions imported from state.py</text>',
            "</g>",
        ]
    )
    return lines


def render_svg() -> str:
    """Return a self-contained SVG that keeps base and dynamic relations distinct."""

    if tuple(STATES) != EXPECTED_STATES:
        raise RuntimeError("executable Graph topology is not the frozen eight-state contract")
    if set(DYNAMIC_LEGAL_TRANSITIONS) != {
        "full",
        "no_recovery_revision_edge",
        "no_observation_conditioned_branching",
        "no_persistent_graph_state",
        "no_replanning",
    }:
        raise RuntimeError("dynamic Graph profiles do not match the frozen ablation contract")

    width = 1500
    height = 920
    node_width = 150
    node_height = 54
    positions = {
        "Inspect": (80, 80),
        "Hypothesize": (285, 80),
        "Analyze": (490, 80),
        "Check": (695, 80),
        "Submit": (1235, 80),
        "Monitor": (390, 200),
        "Revise": (620, 200),
        "Recover": (850, 200),
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><marker id="a" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#475569"/></marker></defs>',
        f'<rect width="{width}" height="{height}" fill="white"/>',
        '<text x="750" y="32" text-anchor="middle" font-family="sans-serif" font-size="19">Eight-state PHM graph: shared topology, profile-specific relations</text>',
        '<text x="750" y="54" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#64748b">The base-v6 and dynamic-full legal-transition matrices are distinct experiment contracts.</text>',
    ]

    primary = (
        ("Inspect", "Hypothesize"),
        ("Hypothesize", "Analyze"),
        ("Analyze", "Check"),
        ("Check", "Submit"),
    )
    for left, right in primary:
        left_x, left_y = positions[left]
        right_x, right_y = positions[right]
        lines.append(
            f'<line x1="{left_x + node_width}" y1="{left_y + node_height / 2}" '
            f'x2="{right_x}" y2="{right_y + node_height / 2}" '
            'stroke="#2563eb" stroke-width="3" marker-end="url(#a)"/>'
        )

    lines.extend(
        [
            '<path d="M 155 134 C 190 170, 300 178, 465 200" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#a)"/>',
            '<text x="315" y="166" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#6d28d9">released public_condition_event (dynamic profile only)</text>',
            '<line x1="540" y1="227" x2="620" y2="227" stroke="#7c3aed" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#a)"/>',
            '<path d="M 695 227 C 660 185, 610 165, 565 134" fill="none" stroke="#7c3aed" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#a)"/>',
            '<path d="M 770 134 C 790 166, 850 176, 925 200" fill="none" stroke="#dc2626" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#a)"/>',
            '<text x="900" y="163" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#b91c1c">recorded action error</text>',
            '<path d="M 850 227 C 760 278, 630 278, 565 134" fill="none" stroke="#dc2626" stroke-width="2" marker-end="url(#a)"/>',
        ]
    )

    for state in EXPECTED_STATES:
        x, y = positions[state]
        color = {
            "Submit": "#dcfce7",
            "Monitor": "#ede9fe",
            "Revise": "#ede9fe",
            "Recover": "#fee2e2",
        }.get(state, "#dbeafe")
        lines.extend(
            [
                f'<rect data-state="{state}" x="{x}" y="{y}" width="{node_width}" height="{node_height}" rx="9" fill="{color}" stroke="#334155"/>',
                f'<text x="{x + node_width / 2}" y="{y + 33}" text-anchor="middle" font-family="sans-serif" font-size="14">{state}</text>',
            ]
        )

    lines.extend(
        [
            '<text x="750" y="294" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#334155">Active v6 registers no public_condition_event: Monitor and Revise are unreachable in that primary cohort.</text>',
            '<text x="750" y="315" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#64748b">The separate dynamic-full mechanics gate is accepted; its provider-bound formal cohort has not run.</text>',
        ]
    )
    lines.extend(
        _render_matrix(
            relation_id="base-v6",
            title="Base-v6 declared relation (50 edges)",
            subtitle="Monitor/Revise remain declared but unreachable without an event",
            transitions=ALLOWED_TRANSITIONS,
            matrix_x=180,
            matrix_y=440,
            legal_fill="#2563eb",
        )
    )
    lines.extend(
        _render_matrix(
            relation_id="dynamic-full",
            title="Dynamic-full profile relation (33 edges)",
            subtitle="Separate runtime identity; provider-bound formal cohort not run",
            transitions=DYNAMIC_LEGAL_TRANSITIONS["full"],
            matrix_x=930,
            matrix_y=440,
            legal_fill="#7c3aed",
        )
    )
    lines.extend(
        [
            '<text x="750" y="852" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#64748b">Filled cells are legal transitions. The four preregistered dynamic ablations use their own profile-specific relations.</text>',
            '<text x="750" y="876" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#64748b">The active state restricts the visible subset of the unchanged shared tool surface before each LLM decision.</text>',
            "</svg>",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    output = Path("paper/assets/figures/graph_policy_states.svg")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_svg(), encoding="utf-8")


if __name__ == "__main__":
    main()
