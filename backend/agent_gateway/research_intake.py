from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


INTAKE_SCHEMA = "backend/registry/schema_registry/research_material_intake.schema.yaml"
INTAKE_FIELDS = (
    "material_summary",
    "available_assets",
    "desired_output",
    "constraints",
    "known_gaps",
)
VALID_PHASES = {"P0", "P1", "P2", "P3", "P4"}
TERMINAL_STATUSES = {"done", "archive"}

PHASE_DEFAULTS: dict[str, dict[str, str]] = {
    "P0": {
        "target_node": "research::P0_项目申请书::P0_02_研究挑战与科学问题_工程问题",
        "worker": "idea_discovery_or_problem_formulation",
        "next_action": "把材料收敛为可证伪问题、科学/工程边界和失败定义。",
    },
    "P1": {
        "target_node": "research::P1_实验设计与仓库蓝图::P1_07_优化目标_任务_评测协议",
        "worker": "experiment_design_or_execution",
        "next_action": "把材料绑定到实验目标、baseline、metric、protocol 和最小验证计划。",
    },
    "P2": {
        "target_node": "research::P2_论文撰写::P2_02_初稿_md::P2_02_01_引言",
        "worker": "manuscript_worker",
        "next_action": "把材料绑定到论文主线、claim-evidence 边界和局部写作任务。",
    },
    "P3": {
        "target_node": "research::P3_论文模拟评审与修改_多轮::P3_01_评审轮次",
        "worker": "auto_review_loop",
        "next_action": "把材料绑定到评审视角、blocking issue、修订地图和下一轮触发条件。",
    },
    "P4": {
        "target_node": "research::P4_论文回复_response::P4_01_审稿意见收集",
        "worker": "response_worker",
        "next_action": "把材料绑定到 reviewer comment、response coverage、修改证据和逐点回复入口。",
    },
}


class ResearchIntakeError(ValueError):
    pass


def require_yaml() -> None:
    if yaml is None:
        raise ResearchIntakeError("PyYAML is required for material intake")


def read_yaml(path: Path) -> dict[str, Any]:
    require_yaml()
    if not path.is_file():
        return {}
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def write_yaml(path: Path, payload: dict[str, Any]) -> None:
    require_yaml()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def normalize_text(value: Any, field: str) -> str:
    if isinstance(value, list):
        text = "\n".join(f"- {str(item).strip()}" for item in value if str(item).strip())
    elif isinstance(value, str):
        text = value.strip()
    else:
        raise ResearchIntakeError(f"{field} must be a string or list of strings")
    if not text:
        raise ResearchIntakeError(f"{field} is required")
    return text


def normalize_phase(value: Any) -> str | None:
    if value is None or value == "":
        return None
    phase = str(value).strip().upper()
    if phase not in VALID_PHASES:
        raise ResearchIntakeError(f"entry_phase must be one of: {', '.join(sorted(VALID_PHASES))}")
    return phase


def phase_from_path(path: Path) -> str | None:
    parts = path.as_posix().split("/")
    if len(parts) < 2:
        return None
    phase = parts[1].split("_", 1)[0]
    return phase if phase in VALID_PHASES else None


def path_to_node_id(path: Path) -> str:
    return path.as_posix().replace("/", "::")


def graph_payload(root: Path) -> dict[str, Any]:
    path = root / "backend" / "graph" / "graph.json"
    if not path.is_file():
        return {"nodes": {}, "edges": []}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"nodes": {}, "edges": []}
    return payload if isinstance(payload, dict) else {"nodes": {}, "edges": []}


def target_path_from_node(root: Path, target_node: str, graph: dict[str, Any]) -> tuple[str, Path]:
    normalized = target_node.strip()
    if not normalized:
        raise ResearchIntakeError("target_node cannot be empty")

    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    if normalized in nodes and isinstance(nodes[normalized], dict) and isinstance(nodes[normalized].get("path"), str):
        rel_path = Path(nodes[normalized]["path"])
        node_id = normalized
    elif normalized.startswith("research::"):
        rel_path = Path(normalized.replace("::", "/"))
        node_id = normalized
    elif normalized.startswith("research/"):
        rel_path = Path(normalized)
        node_id = path_to_node_id(rel_path)
    else:
        raise ResearchIntakeError("target_node must be a research:: id or research/ path")

    resolved = (root / rel_path).resolve()
    research_root = (root / "research").resolve()
    if research_root not in (resolved, *resolved.parents):
        raise ResearchIntakeError(f"target_node resolves outside research/: {target_node}")
    return node_id, rel_path


def normalize_intake(raw: dict[str, Any]) -> dict[str, Any]:
    graph = raw.get("_graph") if isinstance(raw.get("_graph"), dict) else {"nodes": {}, "edges": []}
    entry_phase = normalize_phase(raw.get("entry_phase"))
    target_node_raw = raw.get("target_node")

    if isinstance(target_node_raw, str) and target_node_raw.strip():
        node_id, rel_path = target_path_from_node(Path(str(raw.get("_root") or ".")).resolve(), target_node_raw, graph)
        inferred_phase = phase_from_path(rel_path)
        if entry_phase and inferred_phase and entry_phase != inferred_phase:
            raise ResearchIntakeError(f"entry_phase {entry_phase} does not match target_node phase {inferred_phase}")
        phase = entry_phase or inferred_phase
        if phase is None:
            raise ResearchIntakeError("Cannot infer phase from target_node")
    else:
        if entry_phase is None:
            raise ResearchIntakeError("entry_phase or target_node is required")
        phase = entry_phase
        node_id = PHASE_DEFAULTS[phase]["target_node"]
        rel_path = Path(node_id.replace("::", "/"))

    normalized: dict[str, Any] = {
        "entry_phase": phase,
        "target_node": node_id,
        "target_path": rel_path.as_posix(),
    }
    for field in INTAKE_FIELDS:
        normalized[field] = normalize_text(raw.get(field), field)
    return normalized


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def next_available_path(base: Path) -> Path:
    if not base.exists():
        return base
    stem = base.stem
    suffix = base.suffix
    for index in range(2, 100):
        candidate = base.with_name(f"{stem}_{index}{suffix}")
        if not candidate.exists():
            return candidate
    raise ResearchIntakeError(f"Could not allocate intake artifact path near {base}")


def unmet_prerequisites(root: Path, target_node: str, graph: dict[str, Any]) -> list[dict[str, str]]:
    nodes = graph.get("nodes") if isinstance(graph.get("nodes"), dict) else {}
    edges = graph.get("edges") if isinstance(graph.get("edges"), list) else []
    unmet: list[dict[str, str]] = []
    for edge in edges:
        if not isinstance(edge, dict) or edge.get("rel") != "depends_on" or edge.get("src") != target_node:
            continue
        dst = edge.get("dst")
        if not isinstance(dst, str):
            continue
        payload = nodes.get(dst) if isinstance(nodes.get(dst), dict) else {}
        status = str(payload.get("status") or "seed")
        if status not in TERMINAL_STATUSES:
            unmet.append({"node_id": dst, "path": str(payload.get("path") or dst.replace("::", "/")), "status": status})
    return unmet


def material_markdown(payload: dict[str, Any], worker: str, next_action: str, prerequisites: list[dict[str, str]]) -> str:
    prereq_text = "\n".join(
        f"- {item['node_id']} ({item['status']})"
        for item in prerequisites
    ) or "- None detected from explicit dependencies."
    return f"""# Research Material Intake

## Routing
- entry_phase: `{payload["entry_phase"]}`
- target_node: `{payload["target_node"]}`
- recommended_worker: `{worker}`

## Material Summary
{payload["material_summary"]}

## Available Assets
{payload["available_assets"]}

## Desired Output
{payload["desired_output"]}

## Constraints
{payload["constraints"]}

## Known Gaps
{payload["known_gaps"]}

## Next Action
{next_action}

## Unmet Prerequisites
{prereq_text}

## Boundary
This intake records where the material should enter the workspace. It does not mark upstream phases complete, bypass local acceptance checklists, or prove handoff readiness.
"""


def refresh_views(root: Path) -> None:
    script = root / "scripts" / "refresh_views.py"
    if not script.is_file():
        return
    result = subprocess.run(
        [sys.executable, str(script), "--mode", "full"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-12:])
        raise ResearchIntakeError(f"Material intake refresh failed:\n{tail}")


def ingest_materials(root: Path, raw_intake: dict[str, Any], *, refresh: bool = True) -> dict[str, Any]:
    root = root.resolve()
    graph = graph_payload(root)
    payload = normalize_intake({**raw_intake, "_root": str(root), "_graph": graph})
    phase = payload["entry_phase"]
    target_node = payload["target_node"]
    target_path = Path(payload["target_path"])
    node_dir = root / target_path
    worker = PHASE_DEFAULTS[phase]["worker"]
    next_action = PHASE_DEFAULTS[phase]["next_action"]
    prerequisites = unmet_prerequisites(root, target_node, graph)

    stamp = timestamp()
    artifact_path = next_available_path(node_dir / "artifacts" / "intake" / f"material_{stamp}.yaml")
    docs_path = next_available_path(node_dir / "docs" / f"intake_{stamp}.md")
    artifact_payload = {
        "schema": INTAKE_SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "entry_phase": phase,
        "target_node": target_node,
        "target_path": target_path.as_posix(),
        "recommended_worker": worker,
        "next_action": next_action,
        "unmet_prerequisites": prerequisites,
        **{field: payload[field] for field in INTAKE_FIELDS},
    }

    write_yaml(artifact_path, artifact_payload)
    write_text(docs_path, material_markdown(payload, worker, next_action, prerequisites))
    if refresh:
        refresh_views(root)

    return {
        "message": "Research material intake recorded.",
        "entry_phase": phase,
        "target_node": target_node,
        "target_path": target_path.as_posix(),
        "recommended_worker": worker,
        "next_action": next_action,
        "unmet_prerequisites": prerequisites,
        "artifact_path": artifact_path.relative_to(root).as_posix(),
        "docs_path": docs_path.relative_to(root).as_posix(),
    }


def intake_status(root: Path) -> dict[str, Any]:
    root = root.resolve()
    records = sorted((root / "research").rglob("artifacts/intake/material_*.yaml")) if (root / "research").is_dir() else []
    recent = [
        {
            "path": path.relative_to(root).as_posix(),
            "target_path": path.parents[2].relative_to(root).as_posix() if len(path.parents) > 2 else "",
        }
        for path in records[-10:]
    ]
    return {
        "phase_defaults": {phase: dict(config) for phase, config in PHASE_DEFAULTS.items()},
        "recent_intakes": recent,
        "recent_count": len(records),
    }


def read_intake_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ResearchIntakeError(f"Input file not found: {path}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
    else:
        require_yaml()
        payload = yaml.safe_load(text)
    if not isinstance(payload, dict):
        raise ResearchIntakeError("Input file must contain a mapping")
    return payload
