#!/usr/bin/env python3
"""Generate Obsidian Canvas IDE views from the minimal research graph."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from node_tier import (
    archetype_family_for,
    binder_any_of_for,
    load_local_skill_overrides,
    load_node_tier_policy,
    node_mode_for,
    requires_node_skill,
    requires_sop,
)


GENERATED_PREFIX = "gen:"
PHASES = ["P0", "P1", "P2", "P3", "P4"]
TERMINAL_STATUSES = {"done", "archive"}

COLOR_READY = "4"
COLOR_BLOCKED = "1"
COLOR_REVIEW_BLOCKED = "6"
COLOR_TERMINAL = "3"
COLOR_NEUTRAL = "2"
COLOR_FRAMEWORK = "5"
COLOR_NEXT = "6"
LEGACY_MINIMAL_ENTRY_BODY = "Use implicit local-entry conventions from the registry. Keep this node-local and bounded."
PROMPT_ENTRY_REFERENCES = (
    "prompts/research_prompt.md",
    "prompts/acceptance_checklist.yaml",
    "prompts/review_rubric.yaml",
)

OVERVIEW_PHASE_WIDTH = 620
OVERVIEW_PHASE_GAP = 80
FOCUS_CARD_WIDTH = 420
FOCUS_CARD_HEIGHT = 160

PHASE_FALLBACK_SKILLS = {
    "P0": ".agent/skills/idea_discovery_or_problem_formulation/SKILL.md",
    "P1": ".agent/skills/experiment_design_or_execution/SKILL.md",
    "P2": ".agent/skills/manuscript_worker/SKILL.md",
    "P3": ".agent/skills/auto_review_loop/SKILL.md",
    "P4": ".agent/skills/response_worker/SKILL.md",
}

DEFAULT_LAYOUT_HINTS: dict[str, Any] = {
    "version": 1,
    "overview": {
        "scheduler": {"x": -700, "y": -20, "width": 580, "height": 220},
        "phase": {
            "x_start": 0,
            "y": -80,
            "width": OVERVIEW_PHASE_WIDTH,
            "gap": OVERVIEW_PHASE_GAP,
            "group_x_offset": -24,
            "min_group_height": 520,
            "label_y": -40,
            "label_width": 220,
            "label_height": 72,
        },
        "node": {
            "y_start": 80,
            "y_gap": 170,
            "readme_width": 520,
            "readme_height": 96,
            "badge_gap": 8,
            "badge_width": 520,
            "badge_height": 52,
        },
    },
    "focus": {
        "scheduler": {"x": 0, "y": -260, "width": 780, "height": 200},
        "no_next": {"x": 0, "y": 0, "width": 720, "height": 120},
        "center": {"x": 0, "y": 0},
        "node_block": {
            "card_width": FOCUS_CARD_WIDTH,
            "card_height": FOCUS_CARD_HEIGHT,
            "status_height": 120,
            "status_gap": 20,
            "badge_height": 120,
            "badge_gap": 20,
        },
        "dependencies": {"x": -560, "y_start": 0, "y_gap": 460},
        "downstream": {"x": 560, "y_start": 0, "y_gap": 460},
        "skills": {"x": 0, "y_start": 480, "width": 420, "height": 140, "gap": 160},
        "siblings": {
            "x": 0,
            "y_start": 700,
            "y_gap": 132,
            "width": 420,
            "height": 96,
            "badge_x": 440,
            "badge_width": 340,
            "badge_height": 96,
        },
    },
}


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def warn(message: str) -> None:
    print(f"[warn] {message}", file=sys.stderr)


def fail(message: str) -> None:
    print(f"[error] {message}", file=sys.stderr)
    raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"missing JSON file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")
    if not isinstance(payload, dict):
        fail(f"{path} must contain a JSON object")
    return payload


def merge_layout_hints(defaults: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for key, default_value in defaults.items():
        override_value = overrides.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = merge_layout_hints(default_value, override_value)
        elif override_value is not None:
            merged[key] = override_value
        else:
            merged[key] = default_value

    for key, override_value in overrides.items():
        if key not in merged:
            merged[key] = override_value
    return merged


def load_layout_hints(root: Path) -> dict[str, Any]:
    hints_path = root / "obsidian" / "canvases" / "layout_hints.json"
    if not hints_path.is_file():
        return DEFAULT_LAYOUT_HINTS
    try:
        payload = json.loads(hints_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        warn(f"invalid layout hints JSON ({exc}); using defaults")
        return DEFAULT_LAYOUT_HINTS
    if not isinstance(payload, dict):
        warn("layout_hints.json must contain an object; using defaults")
        return DEFAULT_LAYOUT_HINTS
    return merge_layout_hints(DEFAULT_LAYOUT_HINTS, payload)


def hint_int(layout: dict[str, Any], *keys: str) -> int:
    value: Any = layout
    default_value: Any = DEFAULT_LAYOUT_HINTS
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            value = None
        if isinstance(default_value, dict):
            default_value = default_value.get(key)
        else:
            default_value = None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    if isinstance(default_value, (int, float)) and not isinstance(default_value, bool):
        warn(f"layout hint {'.'.join(keys)} is invalid; using default")
        return int(default_value)
    raise RuntimeError(f"missing numeric default layout hint: {'.'.join(keys)}")


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f"{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(tmp_path, path)
    except Exception:
        if tmp_path.exists():
            tmp_path.unlink()
        raise


def stable_id(kind: str, value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]
    return f"{GENERATED_PREFIX}{kind}:{digest}"


def phase_from_path(path: str) -> str:
    parts = path.split("/")
    if len(parts) < 2:
        return "PX"
    match = re.match(r"^(P\d+)", parts[1])
    return match.group(1) if match else "PX"


def node_depth(path: str) -> int:
    return path.count("/")


def node_title(path: str) -> str:
    return Path(path).name


def text_node(node_id: str, text: str, x: int, y: int, width: int, height: int, color: str = COLOR_NEUTRAL) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "text",
        "text": text,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "color": color,
    }


def file_node(node_id: str, file_path: str, x: int, y: int, width: int, height: int, color: str = COLOR_NEUTRAL) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "file",
        "file": file_path,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "color": color,
    }


def group_node(node_id: str, label: str, x: int, y: int, width: int, height: int, color: str = COLOR_NEUTRAL) -> dict[str, Any]:
    return {
        "id": node_id,
        "type": "group",
        "label": label,
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "color": color,
    }


def canvas_edge(edge_id: str, from_node: str, to_node: str, label: str, color: str = COLOR_NEUTRAL) -> dict[str, Any]:
    return {
        "id": edge_id,
        "fromNode": from_node,
        "fromSide": "right",
        "toNode": to_node,
        "toSide": "left",
        "label": label,
        "color": color,
    }


def read_status_text(root: Path, node_path: str) -> str:
    status_path = root / node_path / "status.yaml"
    try:
        return status_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        warn(f"status file not found: {status_path}")
        return ""


def regex_value(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^\s*{re.escape(key)}:\s*([^\s#]+)", text)
    return match.group(1) if match else None


def local_skill_files(root: Path, node_path: str) -> list[str]:
    skills_dir = root / node_path / "skills"
    if not skills_dir.is_dir():
        return []
    return [
        path.relative_to(root).as_posix()
        for path in sorted(skills_dir.iterdir())
        if path.is_file() and path.suffix.lower() in {".md", ".markdown"}
    ]


def local_entry_is_thin(root: Path, node_path: str, mode: str, cfg: dict[str, Any]) -> bool:
    entry = root / node_path / "skills" / "local_entry.md"
    if not entry.is_file():
        return False
    text = entry.read_text(encoding="utf-8")
    if LEGACY_MINIMAL_ENTRY_BODY in text:
        return True
    if any(ref not in text for ref in PROMPT_ENTRY_REFERENCES):
        return True
    if requires_node_skill(mode) and "skills/SKILL.md" not in text:
        return True
    if requires_sop(mode, cfg) and "skills/SOP.md" not in text:
        return True
    if (root / node_path / "skills" / "local_wrapper.md").is_file() and "skills/local_wrapper.md" not in text:
        return True
    if (root / node_path / "skills" / "local_execution.md").is_file() and "skills/local_execution.md" not in text:
        return True
    return False


def derive_badges(root: Path, node_id: str, node: dict[str, Any], overrides: dict[str, Any], policy: dict[str, Any]) -> list[str]:
    node_path = str(node["path"])
    mode = node_mode_for(node_path, overrides)
    cfg = (overrides.get("nodes") or {}).get(node_path, {})
    status = str(node.get("status", "seed"))
    status_text = read_status_text(root, node_path)
    badges: list[str] = []
    skill_files = local_skill_files(root, node_path)

    progress_pct = regex_value(status_text, "progress_pct")
    if status == "active" and progress_pct == "0":
        badges.append("zero-progress-active")

    ai_review_count = regex_value(status_text, "ai_review_count")
    human_review_count = regex_value(status_text, "human_review_count")
    if ai_review_count == "0" and human_review_count == "0":
        badges.append("review-not-started")

    if not any(path.endswith("/skills/local_entry.md") for path in skill_files):
        badges.append("missing-local-entry")
    has_node_skill = any(path.endswith("/skills/SKILL.md") for path in skill_files)
    has_sop = any(path.endswith("/skills/SOP.md") for path in skill_files)
    has_local_execution = any(path.endswith("/skills/local_execution.md") for path in skill_files)
    if requires_node_skill(mode):
        if not has_node_skill:
            badges.append("missing-node-skill")
    elif has_node_skill:
        badges.append("unexpected-node-skill")
    if requires_sop(mode, cfg):
        if not has_sop:
            badges.append("missing-sop")
    elif has_sop:
        badges.append("unexpected-sop")
    if mode != "execution" and has_local_execution:
        badges.append("unexpected-local-execution")
    binder_any_of = binder_any_of_for(mode, policy)
    if binder_any_of and not any((root / node_path / rel_path).is_file() for rel_path in binder_any_of):
        badges.append("missing-execution-binder")
    if local_entry_is_thin(root, node_path, mode, cfg):
        badges.append("thin-local-entry")

    if node_id:
        return badges
    return badges


def node_state(node_id: str, node: dict[str, Any], node_details: dict[str, dict[str, Any]]) -> str:
    detail = node_details.get(node_id, {}) if isinstance(node_details, dict) else {}
    handoff = str(detail.get("handoff_readiness") or "blocked_unknown")
    status = str(detail.get("status") or node.get("status", "seed"))
    if handoff == "ready":
        return "truth-ready"
    if handoff == "blocked_review":
        return "review-blocked"
    if handoff == "blocked_execution":
        return "execution-blocked"
    if handoff in {"blocked_truth", "blocked_parent_rollup", "blocked_unknown"}:
        return "truth-blocked"
    if status in TERMINAL_STATUSES:
        return "terminal"
    return "neutral"


def color_for_state(state: str) -> str:
    return {
        "truth-ready": COLOR_READY,
        "review-blocked": COLOR_REVIEW_BLOCKED,
        "execution-blocked": COLOR_BLOCKED,
        "truth-blocked": COLOR_NEUTRAL,
        "terminal": COLOR_TERMINAL,
        "neutral": COLOR_NEUTRAL,
    }[state]


def scheduler_panel(status: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Scheduler Summary",
            "",
            f"- current_phase: `{status.get('current_phase')}`",
            f"- scheduler_next: `{status.get('next_node')}`",
            f"- unfinished_count: `{status.get('unfinished_count')}`",
            f"- scheduler_ready_nodes: `{len(status.get('ready_nodes', []))}`",
            f"- scheduler_blocked_nodes: `{len(status.get('blocked_nodes', []))}`",
            "",
            "Canvas is projection + IDE, not canonical truth.",
        ]
    )


def validate_graph(graph: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[dict[str, str]]]:
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, dict) or not isinstance(edges, list):
        fail("graph.json must contain object 'nodes' and list 'edges'")
    clean_nodes: dict[str, dict[str, Any]] = {}
    for node_id, node in nodes.items():
        if isinstance(node_id, str) and isinstance(node, dict) and isinstance(node.get("path"), str):
            clean_nodes[node_id] = node
        else:
            warn(f"invalid graph node skipped: {node_id}")
    clean_edges: list[dict[str, str]] = []
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            warn(f"edge #{index}: not an object, skipped")
            continue
        src, rel, dst = edge.get("src"), edge.get("rel"), edge.get("dst")
        if all(isinstance(item, str) for item in (src, rel, dst)):
            clean_edges.append({"src": src, "rel": rel, "dst": dst})
        else:
            warn(f"edge #{index}: src/rel/dst must be strings, skipped")
    return clean_nodes, clean_edges


def build_overview(
    root: Path,
    graph: dict[str, Any],
    graph_status: dict[str, Any],
    node_details: dict[str, dict[str, Any]],
    layout: dict[str, Any],
    overrides: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    nodes, edges = validate_graph(graph)
    canvas_nodes: list[dict[str, Any]] = [
        text_node(
            f"{GENERATED_PREFIX}overview:scheduler",
            scheduler_panel(graph_status),
            hint_int(layout, "overview", "scheduler", "x"),
            hint_int(layout, "overview", "scheduler", "y"),
            hint_int(layout, "overview", "scheduler", "width"),
            hint_int(layout, "overview", "scheduler", "height"),
            COLOR_FRAMEWORK,
        )
    ]
    canvas_edges: list[dict[str, Any]] = []
    canvas_node_by_graph_id: dict[str, str] = {}

    by_phase: dict[str, list[tuple[str, dict[str, Any]]]] = {phase: [] for phase in PHASES}
    for node_id, node in sorted(nodes.items(), key=lambda item: (item[1]["path"], item[0])):
        phase = phase_from_path(str(node["path"]))
        if phase in by_phase and node_depth(str(node["path"])) <= 2:
            by_phase[phase].append((node_id, node))

    for phase_index, phase in enumerate(PHASES):
        phase_items = by_phase[phase]
        phase_width = hint_int(layout, "overview", "phase", "width")
        phase_x = hint_int(layout, "overview", "phase", "x_start") + phase_index * (
            phase_width + hint_int(layout, "overview", "phase", "gap")
        )
        node_y_gap = hint_int(layout, "overview", "node", "y_gap")
        group_height = max(
            hint_int(layout, "overview", "phase", "min_group_height"),
            120 + len(phase_items) * node_y_gap,
        )
        canvas_nodes.append(
            group_node(
                f"{GENERATED_PREFIX}overview:phase:{phase}",
                phase,
                phase_x + hint_int(layout, "overview", "phase", "group_x_offset"),
                hint_int(layout, "overview", "phase", "y"),
                phase_width,
                group_height,
            )
        )
        canvas_nodes.append(
            text_node(
                f"{GENERATED_PREFIX}overview:phase-label:{phase}",
                f"# {phase}",
                phase_x,
                hint_int(layout, "overview", "phase", "label_y"),
                hint_int(layout, "overview", "phase", "label_width"),
                hint_int(layout, "overview", "phase", "label_height"),
                COLOR_FRAMEWORK,
            )
        )

        for index, (node_id, node) in enumerate(phase_items):
            path = str(node["path"])
            detail = node_details.get(node_id, {}) if isinstance(node_details, dict) else {}
            state = node_state(node_id, node, node_details)
            card_id = stable_id("overview-node", node_id)
            canvas_node_by_graph_id[node_id] = card_id
            y = hint_int(layout, "overview", "node", "y_start") + index * node_y_gap
            canvas_nodes.append(
                file_node(
                    card_id,
                    f"{path}/README.md",
                    phase_x,
                    y,
                    hint_int(layout, "overview", "node", "readme_width"),
                    hint_int(layout, "overview", "node", "readme_height"),
                    color_for_state(state),
                )
            )
            badges = derive_badges(root, node_id, node, overrides, policy)
            badge_text = f"{node_title(path)}\nstatus: {node.get('status', 'seed')} | truth_state: {state}"
            badge_text += f"\nhandoff: {detail.get('handoff_readiness', 'blocked_unknown')} | truth_ready: {detail.get('truth_ready', False)}"
            if node_id == graph_status.get("next_node"):
                badge_text += "\nscheduler_next: true"
            if badges:
                badge_text += "\n" + " | ".join(badges)
            canvas_nodes.append(
                text_node(
                    stable_id("overview-badge", node_id),
                    badge_text,
                    phase_x,
                    y
                    + hint_int(layout, "overview", "node", "readme_height")
                    + hint_int(layout, "overview", "node", "badge_gap"),
                    hint_int(layout, "overview", "node", "badge_width"),
                    hint_int(layout, "overview", "node", "badge_height"),
                    color_for_state(state),
                )
            )

    for edge in edges:
        src_id = canvas_node_by_graph_id.get(edge["src"])
        dst_id = canvas_node_by_graph_id.get(edge["dst"])
        if src_id and dst_id:
            canvas_edges.append(
                canvas_edge(
                    stable_id("overview-edge", f"{edge['src']}|{edge['rel']}|{edge['dst']}"),
                    src_id,
                    dst_id,
                    edge["rel"],
                    COLOR_BLOCKED if edge["rel"] == "depends_on" else COLOR_FRAMEWORK,
                )
            )

    return {"nodes": canvas_nodes, "edges": canvas_edges}


def neighbor_node_ids(next_node: str, edges: list[dict[str, str]]) -> tuple[list[str], list[str]]:
    dependencies = sorted({edge["dst"] for edge in edges if edge["src"] == next_node and edge["rel"] == "depends_on"})
    downstream = sorted({edge["src"] for edge in edges if edge["dst"] == next_node})
    return dependencies, downstream


def current_phase_siblings(next_node: str, nodes: dict[str, dict[str, Any]]) -> list[str]:
    next_meta = nodes[next_node]
    next_phase = phase_from_path(str(next_meta["path"]))
    next_parent = str(next_meta["path"]).split("/")[:2]
    siblings = []
    for node_id, node in nodes.items():
        path = str(node["path"])
        if node_id != next_node and phase_from_path(path) == next_phase and path.split("/")[:2] == next_parent and node_depth(path) <= 2:
            siblings.append(node_id)
    return sorted(siblings, key=lambda node_id: nodes[node_id]["path"])[:8]


def add_focus_node_block(
    root: Path,
    canvas_nodes: list[dict[str, Any]],
    node_id: str,
    node: dict[str, Any],
    x: int,
    y: int,
    graph_status: dict[str, Any],
    node_details: dict[str, dict[str, Any]],
    label: str,
    overrides: dict[str, Any],
    policy: dict[str, Any],
    card_width: int = FOCUS_CARD_WIDTH,
    card_height: int = FOCUS_CARD_HEIGHT,
    status_height: int = 120,
    status_gap: int = 20,
    badge_height: int = 120,
    badge_gap: int = 20,
) -> tuple[str, str]:
    path = str(node["path"])
    detail = node_details.get(node_id, {}) if isinstance(node_details, dict) else {}
    state = node_state(node_id, node, node_details)
    color = color_for_state(state)
    readme_id = stable_id(f"focus-readme-{label}", node_id)
    status_id = stable_id(f"focus-status-{label}", node_id)
    badge_id = stable_id(f"focus-badge-{label}", node_id)

    status_y = y + card_height + status_gap
    badge_y = status_y + status_height + badge_gap
    canvas_nodes.append(file_node(readme_id, f"{path}/README.md", x, y, card_width, card_height, color))
    canvas_nodes.append(file_node(status_id, f"{path}/status.yaml", x, status_y, card_width, status_height, color))
    mode = node_mode_for(path, overrides)
    badge_lines = [
        f"# {label}: {node_title(path)}",
        f"- status: `{node.get('status', 'seed')}`",
        f"- truth_state: `{state}`",
        f"- handoff: `{detail.get('handoff_readiness', 'blocked_unknown')}`",
        f"- truth_ready: `{detail.get('truth_ready', False)}`",
        f"- archetype: `{archetype_family_for(path, overrides)}`",
    ]
    if node_id == graph_status.get("next_node"):
        badge_lines.append("- scheduler_next: `true`")
    profile = node.get("node_profile")
    if profile:
        badge_lines.append(f"- node_profile: `{profile}`")
    badges = derive_badges(root, node_id, node, overrides, policy)
    if badges:
        badge_lines.append(f"- badges: `{', '.join(badges)}`")
    canvas_nodes.append(text_node(badge_id, "\n".join(badge_lines), x, badge_y, card_width, badge_height, color))
    return readme_id, status_id


def build_focus(
    root: Path,
    graph: dict[str, Any],
    graph_status: dict[str, Any],
    node_details: dict[str, dict[str, Any]],
    layout: dict[str, Any],
    overrides: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    nodes, edges = validate_graph(graph)
    next_node = graph_status.get("next_node")
    canvas_nodes: list[dict[str, Any]] = [
        text_node(
            f"{GENERATED_PREFIX}focus:scheduler",
            scheduler_panel(graph_status),
            hint_int(layout, "focus", "scheduler", "x"),
            hint_int(layout, "focus", "scheduler", "y"),
            hint_int(layout, "focus", "scheduler", "width"),
            hint_int(layout, "focus", "scheduler", "height"),
            COLOR_FRAMEWORK,
        )
    ]
    canvas_edges: list[dict[str, Any]] = []

    if not isinstance(next_node, str) or next_node not in nodes:
        canvas_nodes.append(
            text_node(
                f"{GENERATED_PREFIX}focus:no-next",
                "No next_node. Inspect blocked nodes or finished state.",
                hint_int(layout, "focus", "no_next", "x"),
                hint_int(layout, "focus", "no_next", "y"),
                hint_int(layout, "focus", "no_next", "width"),
                hint_int(layout, "focus", "no_next", "height"),
                COLOR_BLOCKED,
            )
        )
        return {"nodes": canvas_nodes, "edges": canvas_edges}

    node_block_kwargs = {
        "card_width": hint_int(layout, "focus", "node_block", "card_width"),
        "card_height": hint_int(layout, "focus", "node_block", "card_height"),
        "status_height": hint_int(layout, "focus", "node_block", "status_height"),
        "status_gap": hint_int(layout, "focus", "node_block", "status_gap"),
        "badge_height": hint_int(layout, "focus", "node_block", "badge_height"),
        "badge_gap": hint_int(layout, "focus", "node_block", "badge_gap"),
    }
    center_readme, center_status = add_focus_node_block(
        root,
        canvas_nodes,
        next_node,
        nodes[next_node],
        hint_int(layout, "focus", "center", "x"),
        hint_int(layout, "focus", "center", "y"),
        graph_status,
        node_details,
        "next",
        overrides,
        policy,
        **node_block_kwargs,
    )
    canvas_edges.append(canvas_edge(f"{GENERATED_PREFIX}focus:status-edge", center_readme, center_status, "status", COLOR_FRAMEWORK))

    dependencies, downstream = neighbor_node_ids(next_node, edges)
    for index, dep_node in enumerate(dependencies):
        readme_id, _ = add_focus_node_block(
            root,
            canvas_nodes,
            dep_node,
            nodes[dep_node],
            hint_int(layout, "focus", "dependencies", "x"),
            hint_int(layout, "focus", "dependencies", "y_start") + index * hint_int(layout, "focus", "dependencies", "y_gap"),
            graph_status,
            node_details,
            "depends_on",
            overrides,
            policy,
            **node_block_kwargs,
        )
        canvas_edges.append(canvas_edge(stable_id("focus-dep-edge", dep_node), readme_id, center_readme, "depends_on", COLOR_BLOCKED))

    for index, downstream_node in enumerate(downstream):
        readme_id, _ = add_focus_node_block(
            root,
            canvas_nodes,
            downstream_node,
            nodes[downstream_node],
            hint_int(layout, "focus", "downstream", "x"),
            hint_int(layout, "focus", "downstream", "y_start") + index * hint_int(layout, "focus", "downstream", "y_gap"),
            graph_status,
            node_details,
            "downstream",
            overrides,
            policy,
            **node_block_kwargs,
        )
        rels = sorted({edge["rel"] for edge in edges if edge["dst"] == next_node and edge["src"] == downstream_node})
        canvas_edges.append(canvas_edge(stable_id("focus-downstream-edge", downstream_node), center_readme, readme_id, ",".join(rels), COLOR_READY))

    next_path = str(nodes[next_node]["path"])
    skill_files = local_skill_files(root, next_path)
    for skill_index, skill_file in enumerate(skill_files):
        canvas_nodes.append(
            file_node(
                stable_id("focus-local-skill", skill_file),
                skill_file,
                hint_int(layout, "focus", "skills", "x"),
                hint_int(layout, "focus", "skills", "y_start") + skill_index * hint_int(layout, "focus", "skills", "gap"),
                hint_int(layout, "focus", "skills", "width"),
                hint_int(layout, "focus", "skills", "height"),
                COLOR_FRAMEWORK,
            )
        )
    if not skill_files:
        fallback = PHASE_FALLBACK_SKILLS.get(phase_from_path(next_path))
        if fallback and (root / fallback).is_file():
            canvas_nodes.append(
                file_node(
                    stable_id("focus-fallback-skill", fallback),
                    fallback,
                    hint_int(layout, "focus", "skills", "x"),
                    hint_int(layout, "focus", "skills", "y_start"),
                    hint_int(layout, "focus", "skills", "width"),
                    hint_int(layout, "focus", "skills", "height"),
                    COLOR_FRAMEWORK,
                )
            )

    for index, sibling_id in enumerate(current_phase_siblings(next_node, nodes)):
        sibling = nodes[sibling_id]
        sibling_path = str(sibling["path"])
        y = hint_int(layout, "focus", "siblings", "y_start") + index * hint_int(layout, "focus", "siblings", "y_gap")
        canvas_nodes.append(
            file_node(
                stable_id("focus-sibling", sibling_id),
                f"{sibling_path}/README.md",
                hint_int(layout, "focus", "siblings", "x"),
                y,
                hint_int(layout, "focus", "siblings", "width"),
                hint_int(layout, "focus", "siblings", "height"),
                color_for_state(node_state(sibling_id, sibling, node_details)),
            )
        )
        canvas_nodes.append(
            text_node(
                stable_id("focus-sibling-badge", sibling_id),
                f"{node_title(sibling_path)} | {sibling.get('status', 'seed')}",
                hint_int(layout, "focus", "siblings", "badge_x"),
                y,
                hint_int(layout, "focus", "siblings", "badge_width"),
                hint_int(layout, "focus", "siblings", "badge_height"),
                color_for_state(node_state(sibling_id, sibling, node_details)),
            )
        )

    return {"nodes": canvas_nodes, "edges": canvas_edges}


def initial_workbench() -> dict[str, Any]:
    nodes = [
        group_node(f"{GENERATED_PREFIX}workbench:group", "Framework workbench (manual)", -460, -180, 1480, 520, COLOR_NEXT),
        text_node(
            f"{GENERATED_PREFIX}workbench:methods",
            "# Method sketches\n\nDraft exploratory method ideas here. Promote accepted changes through the inbox.",
            -420,
            -100,
            360,
            180,
            COLOR_NEXT,
        ),
        text_node(
            f"{GENERATED_PREFIX}workbench:skills",
            "# Skill ideas\n\nKeep skill proposals here until they are ready for `.agent/skills/` or node-local `skills/`.",
            0,
            -100,
            360,
            180,
            COLOR_NEXT,
        ),
        text_node(
            f"{GENERATED_PREFIX}workbench:relations",
            "# Relation / framework proposals\n\nDo not treat Canvas lines as canonical edges. Write accepted proposals to the inbox.",
            420,
            -100,
            360,
            180,
            COLOR_NEXT,
        ),
        file_node(f"{GENERATED_PREFIX}workbench:inbox", "obsidian/inbox/canvas_proposals.md", -420, 120, 520, 160, COLOR_FRAMEWORK),
        file_node(f"{GENERATED_PREFIX}workbench:workflow", "docs/architecture/obsidian_canvas_workflow.md", 140, 120, 520, 160, COLOR_FRAMEWORK),
    ]
    return {"nodes": nodes, "edges": []}


def ensure_workbench(path: Path, dry_run: bool) -> str:
    if path.exists():
        return "preserved"
    if dry_run:
        return "would_create"
    atomic_write_json(path, initial_workbench())
    return "created"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Obsidian Canvas views from graph.json.")
    parser.add_argument(
        "--root",
        default=str(repo_root_from_script()),
        help="Repository root. Defaults to the parent of scripts/.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and report target files without writing generated canvases.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    graph_path = root / "backend" / "graph" / "graph.json"
    graph_status_path = root / "backend" / "graph" / "graph_status.json"
    overview_path = root / "obsidian" / "canvases" / "research_overview.canvas"
    focus_path = root / "obsidian" / "canvases" / "current_focus.canvas"
    workbench_path = root / "obsidian" / "canvases" / "framework_workbench.canvas"

    try:
        graph = load_json(graph_path)
        graph_status = load_json(graph_status_path)
        node_details = load_json(root / "backend" / "graph" / "node_details.json").get("nodes", {})
        if not isinstance(node_details, dict):
            fail("node_details.json must contain a 'nodes' object")
        overrides = load_local_skill_overrides(root)
        policy = load_node_tier_policy(root)
        layout = load_layout_hints(root)
        overview = build_overview(root, graph, graph_status, node_details, layout, overrides, policy)
        focus = build_focus(root, graph, graph_status, node_details, layout, overrides, policy)
        workbench_state = ensure_workbench(workbench_path, args.dry_run)

        if args.dry_run:
            print(
                "[canvas_dry_run] "
                f"overview={overview_path} nodes={len(overview['nodes'])} edges={len(overview['edges'])}; "
                f"focus={focus_path} nodes={len(focus['nodes'])} edges={len(focus['edges'])}; "
                f"workbench={workbench_path} state={workbench_state}"
            )
            return 0

        atomic_write_json(overview_path, overview)
        atomic_write_json(focus_path, focus)
    except Exception as exc:
        print(f"[canvas_failed] {exc}", file=sys.stderr)
        return 1

    print(
        "[canvas_ok] "
        f"overview_nodes={len(overview['nodes'])} overview_edges={len(overview['edges'])} "
        f"focus_nodes={len(focus['nodes'])} focus_edges={len(focus['edges'])} "
        f"workbench={workbench_state}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
