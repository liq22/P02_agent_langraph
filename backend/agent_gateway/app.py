from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.agent_gateway.research_intake import ResearchIntakeError, ingest_materials, intake_status

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


MINIMAL_GRAPH_FILES = [
    "backend/graph/graph.json",
    "backend/graph/graph_status.json",
]

FULL_PROJECTION_FILES = [
    "backend/graph/hierarchy.json",
    "backend/graph/node_details.json",
    "backend/graph/scope_rollup.json",
    "backend/graph/board_state.json",
]

SESSION_LOG_TAIL_LINES = 200
GRAPH_ONLY_REFRESH_COMMAND = "python scripts/refresh_views.py --mode graph_only"
FULL_REFRESH_COMMAND = "python scripts/refresh_views.py --mode full"
DEFAULT_AGENT_ID = "codex"
ALLOWED_NODE_STAGES = {"seed", "active", "review", "fix", "done", "archive"}


def session_context_key(session_type: str, target_node: str | None, target_scope: str | None) -> str:
    if session_type == "node" and target_node:
        return f"node::{target_node}"
    if session_type == "scope" and target_scope:
        return f"scope::{target_scope}"
    return "general"


@dataclass
class Session:
    id: str
    agent: str
    target_node: str | None
    cwd: str
    session_type: str = "general"
    target_scope: str | None = None
    context_key: str = "general"
    context_label: str = "repo"
    context_path: str = ""
    prompt: str = ""
    status: str = "idle"
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    finished_at: float | None = None
    return_code: int | None = None
    command: list[str] = field(default_factory=list)
    log_lines: list[str] = field(default_factory=list)
    log_path: str | None = None
    process: subprocess.Popen[str] | None = field(default=None, repr=False, compare=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent": self.agent,
            "target_node": self.target_node,
            "cwd": self.cwd,
            "session_type": self.session_type,
            "target_scope": self.target_scope,
            "context_key": self.context_key,
            "context_label": self.context_label,
            "context_path": self.context_path,
            "prompt": self.prompt,
            "status": self.status,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "return_code": self.return_code,
            "command": list(self.command),
            "log_lines": list(self.log_lines),
            "log_path": self.log_path,
        }


class SessionStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.lock = threading.Lock()
        self.sessions: dict[str, Session] = {}

    def list(
        self,
        *,
        session_type: str | None = None,
        target_node: str | None = None,
        target_scope: str | None = None,
        context_key: str | None = None,
    ) -> list[dict[str, Any]]:
        with self.lock:
            sessions = sorted(self.sessions.values(), key=lambda s: s.created_at, reverse=True)
            if session_type:
                sessions = [session for session in sessions if session.session_type == session_type]
            if target_node:
                sessions = [session for session in sessions if session.target_node == target_node]
            if target_scope:
                sessions = [session for session in sessions if session.target_scope == target_scope]
            if context_key:
                sessions = [session for session in sessions if session.context_key == context_key]
            return [session.to_dict() for session in sessions]

    def get(self, session_id: str) -> Session:
        with self.lock:
            if session_id not in self.sessions:
                raise KeyError(session_id)
            return self.sessions[session_id]

    def create(
        self,
        agent: str,
        target_node: str | None,
        cwd: str,
        *,
        session_type: str = "general",
        target_scope: str | None = None,
        context_key: str = "general",
        context_label: str = "repo",
        context_path: str = "",
    ) -> Session:
        session = Session(
            id=uuid.uuid4().hex[:12],
            agent=agent,
            target_node=target_node,
            cwd=cwd,
            session_type=session_type,
            target_scope=target_scope,
            context_key=context_key,
            context_label=context_label,
            context_path=context_path,
        )
        with self.lock:
            self.sessions[session.id] = session
        return session

    def write_session_metadata(self, session: Session) -> None:
        if not session.log_path:
            return
        payload = {
            "id": session.id,
            "agent": session.agent,
            "target_node": session.target_node,
            "cwd": session.cwd,
            "session_type": session.session_type,
            "target_scope": session.target_scope,
            "context_key": session.context_key,
            "context_label": session.context_label,
            "context_path": session.context_path,
            "status": session.status,
            "created_at": session.created_at,
            "started_at": session.started_at,
            "finished_at": session.finished_at,
            "return_code": session.return_code,
            "command": list(session.command),
            "log_path": session.log_path,
        }
        meta_path = Path(session.log_path).parent / "session.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def restore_log_path(self, log_path: Path) -> Session | None:
        session_dir = log_path.parent
        meta_path = session_dir / "session.json"
        meta: dict[str, Any] = {}
        if meta_path.is_file():
            try:
                loaded = json.loads(meta_path.read_text(encoding="utf-8"))
                meta = loaded if isinstance(loaded, dict) else {}
            except (OSError, json.JSONDecodeError):
                meta = {}
        try:
            lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
            stat = log_path.stat()
        except OSError:
            return None

        session_id = str(meta.get("id") or session_dir.name)
        session_type = str(meta.get("session_type") or "general")
        target_node = meta.get("target_node") if isinstance(meta.get("target_node"), str) else None
        target_scope = meta.get("target_scope") if isinstance(meta.get("target_scope"), str) else None
        command = meta.get("command") if isinstance(meta.get("command"), list) else []
        context_key = str(meta.get("context_key") or session_context_key(session_type, target_node, target_scope))
        return Session(
            id=session_id,
            agent=str(meta.get("agent") or "restored"),
            target_node=target_node,
            cwd=str(meta.get("cwd") or self.root),
            session_type=session_type,
            target_scope=target_scope,
            context_key=context_key,
            context_label=str(meta.get("context_label") or "restored session"),
            context_path=str(meta.get("context_path") or ""),
            status=str(meta.get("status") or "restored"),
            created_at=float(meta.get("created_at") or stat.st_mtime),
            started_at=meta.get("started_at") if isinstance(meta.get("started_at"), (int, float)) else None,
            finished_at=meta.get("finished_at") if isinstance(meta.get("finished_at"), (int, float)) else stat.st_mtime,
            return_code=meta.get("return_code") if isinstance(meta.get("return_code"), int) else None,
            command=[str(part) for part in command if isinstance(part, str)],
            log_lines=lines[-SESSION_LOG_TAIL_LINES:],
            log_path=str(log_path),
        )

    def restore_from_disk(self) -> None:
        session_logs: list[Path] = []
        sessions_root = self.root / "artifacts" / "agent_sessions"
        if sessions_root.is_dir():
            session_logs.extend(sessions_root.glob("*/session.log"))
            session_logs.extend(sessions_root.glob("*/*/session.log"))
        research_root = self.root / "research"
        if research_root.is_dir():
            session_logs.extend(research_root.rglob("logs/agent_sessions/*/session.log"))

        restored: list[Session] = []
        seen: set[Path] = set()
        for log_path in sorted(session_logs, key=lambda path: str(path)):
            resolved = log_path.resolve()
            if resolved in seen or not log_path.is_file():
                continue
            seen.add(resolved)
            session = self.restore_log_path(log_path)
            if not session:
                continue
            with self.lock:
                if session.id in self.sessions:
                    continue
            restored.append(session)
        if restored:
            with self.lock:
                for session in restored:
                    self.sessions.setdefault(session.id, session)

    def append_log(self, session_id: str, line: str) -> None:
        with self.lock:
            session = self.sessions[session_id]
            session.log_lines.append(line.rstrip("\n"))
            if session.log_path:
                log_path = Path(session.log_path)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as handle:
                    handle.write(line)

    def update(self, session_id: str, **kwargs: Any) -> None:
        with self.lock:
            session = self.sessions[session_id]
            for key, value in kwargs.items():
                setattr(session, key, value)
            self.write_session_metadata(session)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def configured_repo_root() -> Path:
    raw = os.environ.get("AUTORESEARCH_ROOT", "").strip()
    source = repo_root().resolve()
    if not raw:
        return source
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = (source / candidate).resolve()
    else:
        candidate = candidate.resolve()
    return candidate


SOURCE_ROOT = repo_root().resolve()
ROOT = configured_repo_root()
STORE = SessionStore(ROOT)


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    raise RuntimeError(f"Cannot parse YAML config: {path}")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def missing_files(required_files: list[str]) -> list[str]:
    return [rel for rel in required_files if not (ROOT / rel).exists()]


def missing_minimal_graph_files() -> list[str]:
    return missing_files(MINIMAL_GRAPH_FILES)


def missing_full_projection_files() -> list[str]:
    return missing_files(FULL_PROJECTION_FILES)


def missing_graph_files() -> list[str]:
    return missing_minimal_graph_files() + missing_full_projection_files()


def require_minimal_graph_files() -> None:
    missing = missing_minimal_graph_files()
    if missing:
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"Required minimal scheduler graph files are missing. Run `{GRAPH_ONLY_REFRESH_COMMAND}` first.",
                "missing": missing,
            },
        )


def require_full_projection_files() -> None:
    require_minimal_graph_files()
    missing = missing_full_projection_files()
    if missing:
        raise HTTPException(
            status_code=409,
            detail={
                "message": f"Required cockpit projection files are missing. Run `{FULL_REFRESH_COMMAND}` first.",
                "missing": missing,
            },
        )


def gateway_config_path() -> Path:
    return ROOT / "config" / "agent_gateway.yaml"


def load_gateway_config(*, allow_example: bool = True) -> dict[str, Any]:
    cfg_path = gateway_config_path()
    if cfg_path.is_file():
        config = load_yaml(cfg_path)
        config["_source"] = str(cfg_path)
        config["_is_example"] = False
        return config

    if allow_example:
        example = ROOT / "config" / "agent_gateway.yaml.example"
        if example.is_file():
            config = load_yaml(example)
            config["_source"] = str(example)
            config["_is_example"] = True
            return config

    raise HTTPException(
        status_code=409,
        detail="Missing config/agent_gateway.yaml. Copy config/agent_gateway.yaml.example and set real local agent commands first.",
    )


def command_binary_ready(binary: str) -> bool:
    if not binary:
        return False
    if os.path.sep in binary:
        candidate = Path(binary)
        if not candidate.is_absolute():
            candidate = (ROOT / candidate).resolve()
        return candidate.exists()
    return shutil.which(binary) is not None


def command_template_issues(command: Any) -> list[str]:
    if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
        return ["invalid_command_template"]
    issues: list[str] = []
    binary = str(command[0]).strip()
    if not command_binary_ready(binary):
        issues.append(f"missing_binary:{binary}")
    for part in command:
        if "./scripts/run_worker.sh" in part and not (ROOT / "scripts" / "run_worker.sh").is_file():
            issues.append("missing_local_wrapper_script")
    return issues


def configured_agent_catalog(cfg: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    raw_agents = cfg.get("agents", {}) if isinstance(cfg.get("agents"), dict) else {}
    diagnostics: dict[str, dict[str, Any]] = {}
    ready_agents: list[str] = []
    for agent_id, agent_cfg in raw_agents.items():
        issues = command_template_issues(agent_cfg.get("command"))
        entry = {
            "label": agent_cfg.get("label", agent_id),
            "cwd_mode": agent_cfg.get("cwd_mode", "repo"),
            "command_ready": not issues,
            "issues": issues,
        }
        diagnostics[agent_id] = entry
        if not issues:
            ready_agents.append(agent_id)
    return diagnostics, ready_agents


def resolve_default_agent(cfg: dict[str, Any], ready_agents: list[str]) -> str | None:
    preferred = cfg.get("default_agent")
    if isinstance(preferred, str) and preferred in ready_agents:
        return preferred
    if DEFAULT_AGENT_ID in ready_agents:
        return DEFAULT_AGENT_ID
    return ready_agents[0] if ready_agents else None


def gateway_readiness() -> dict[str, Any]:
    missing_minimal = missing_minimal_graph_files()
    missing_full_projection = missing_full_projection_files()
    graph_ready = not missing_minimal
    cfg: dict[str, Any] = {}
    config_error: str | None = None

    try:
        cfg = load_gateway_config(allow_example=True)
    except Exception as exc:
        config_error = str(exc)

    agent_catalog, ready_agents = configured_agent_catalog(cfg)
    using_example = bool(cfg.get("_is_example"))
    setup_steps: list[str] = []
    if missing_minimal:
        setup_steps.append(GRAPH_ONLY_REFRESH_COMMAND)
    elif missing_full_projection:
        setup_steps.append(FULL_REFRESH_COMMAND)
    if config_error:
        setup_steps.append("Create config/agent_gateway.yaml from config/agent_gateway.yaml.example")
    elif using_example and not ready_agents:
        setup_steps.append("cp config/agent_gateway.yaml.example config/agent_gateway.yaml")
        setup_steps.append("Edit config/agent_gateway.yaml with real local agent commands")
    elif using_example:
        setup_steps.append("Optional: copy config/agent_gateway.yaml.example to config/agent_gateway.yaml for local overrides")

    graph_status: dict[str, Any] = {}
    if graph_ready:
        try:
            graph_status = load_json(ROOT / "backend" / "graph" / "graph_status.json")
        except Exception as exc:
            graph_ready = False
            if "backend/graph/graph_status.json" not in missing_minimal:
                missing_minimal.append("backend/graph/graph_status.json")
            setup_steps.insert(0, GRAPH_ONLY_REFRESH_COMMAND)
            config_error = config_error or f"Cannot read graph status: {exc}"

    default_agent = resolve_default_agent(cfg, ready_agents)
    can_run_agents = graph_ready and not config_error and bool(ready_agents)
    full_projection_ready = graph_ready and not missing_full_projection
    return {
        "ok": True,
        "root": str(ROOT),
        "graph_ready": graph_ready,
        "full_projection_ready": full_projection_ready,
        "missing_minimal_graph_files": missing_minimal,
        "missing_full_projection_files": missing_full_projection,
        "missing_projection_files": missing_minimal + missing_full_projection,
        "config_source": cfg.get("_source"),
        "using_example_config": using_example,
        "config_error": config_error,
        "configured_agents": list(agent_catalog.keys()),
        "ready_agents": ready_agents,
        "default_agent": default_agent,
        "agent_diagnostics": agent_catalog,
        "agents_ready": bool(ready_agents) and not config_error,
        "can_run_agents": can_run_agents,
        "next_node": graph_status.get("next_node"),
        "current_phase": graph_status.get("current_phase"),
        "setup_steps": setup_steps,
    }


def minimal_graph_files() -> dict[str, dict[str, Any]]:
    require_minimal_graph_files()
    return {
        "graph": load_json(ROOT / "backend" / "graph" / "graph.json"),
        "graph_status": load_json(ROOT / "backend" / "graph" / "graph_status.json"),
    }


def full_graph_files() -> dict[str, dict[str, Any]]:
    require_full_projection_files()
    files = minimal_graph_files()
    files.update(
        {
            "hierarchy": load_json(ROOT / "backend" / "graph" / "hierarchy.json"),
            "node_details": load_json(ROOT / "backend" / "graph" / "node_details.json"),
            "scope_rollup": load_json(ROOT / "backend" / "graph" / "scope_rollup.json"),
            "board_state": load_json(ROOT / "backend" / "graph" / "board_state.json"),
        }
    )
    return files


def graph_files() -> dict[str, dict[str, Any]]:
    return full_graph_files()



def safe_repo_path(path_value: str | None) -> Path:
    if not isinstance(path_value, str) or not path_value:
        return ROOT
    resolved = (ROOT / path_value).resolve()
    if ROOT.resolve() not in (resolved, *resolved.parents):
        return ROOT
    return resolved if resolved.is_dir() else ROOT


def graph_node(files: dict[str, dict[str, Any]], node_id: str | None) -> dict[str, Any]:
    if not node_id:
        return {}
    nodes = files.get("graph", {}).get("nodes", {})
    if not isinstance(nodes, dict):
        return {}
    node = nodes.get(node_id)
    return node if isinstance(node, dict) else {}


def node_detail(files: dict[str, dict[str, Any]], node_id: str | None) -> dict[str, Any]:
    if not node_id:
        return {}
    nodes = files.get("node_details", {}).get("nodes", {})
    if not isinstance(nodes, dict):
        return {}
    node = nodes.get(node_id)
    return node if isinstance(node, dict) else {}


def node_title_from_path(path_value: str | None, fallback: str) -> str:
    if isinstance(path_value, str) and path_value.strip():
        return Path(path_value).name
    return fallback


def node_cwd(target_node: str | None, files: dict[str, dict[str, Any]]) -> Path:
    if not target_node:
        return ROOT
    node = graph_node(files, target_node)
    if not node:
        return ROOT
    return safe_repo_path(node.get("path"))


def find_hierarchy_node(target_scope: str | None, hierarchy: dict[str, Any]) -> dict[str, Any] | None:
    if not target_scope:
        return None

    def walk(node: dict[str, Any]) -> dict[str, Any] | None:
        if node.get("id") == target_scope:
            return node
        for child in node.get("children", []) or []:
            if isinstance(child, dict):
                found = walk(child)
                if found:
                    return found
        return None

    return walk(hierarchy)


def scope_cwd(target_scope: str | None, hierarchy: dict[str, Any]) -> Path:
    scope = find_hierarchy_node(target_scope, hierarchy)
    if not scope:
        return ROOT
    return safe_repo_path(scope.get("path"))


def validate_target_node(target_node: str | None, files: dict[str, dict[str, Any]], *, required: bool = False) -> str | None:
    if target_node is None or target_node == "":
        if required:
            raise HTTPException(status_code=400, detail="Target node is required")
        return None
    nodes = files.get("graph", {}).get("nodes", {})
    if not isinstance(nodes, dict) or target_node not in nodes:
        raise HTTPException(status_code=404, detail=f"Unknown target node: {target_node}")
    return target_node


def validate_target_scope(target_scope: str | None, hierarchy: dict[str, Any], *, required: bool = False) -> str | None:
    if target_scope is None or target_scope == "":
        if required:
            raise HTTPException(status_code=400, detail="Target scope is required")
        return None
    if not find_hierarchy_node(target_scope, hierarchy):
        raise HTTPException(status_code=404, detail=f"Unknown target scope: {target_scope}")
    return target_scope


def normalize_session_type(payload: dict[str, Any]) -> str:
    raw_type = payload.get("session_type")
    target_node = payload.get("target_node")
    target_scope = payload.get("target_scope")
    if raw_type is None:
        if isinstance(target_node, str) and target_node.strip():
            return "node"
        if isinstance(target_scope, str) and target_scope.strip():
            return "scope"
        return "general"
    if not isinstance(raw_type, str) or raw_type not in {"general", "scope", "node"}:
        raise HTTPException(status_code=400, detail="session_type must be one of: general, scope, node")
    return raw_type


def session_context_metadata(
    session_type: str,
    target_node: str | None,
    target_scope: str | None,
    files: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    if session_type == "node":
        node_id = validate_target_node(target_node, files, required=True)
        node = graph_node(files, node_id)
        detail = node_detail(files, node_id)
        node_path = detail.get("path") or node.get("path") or node_id
        return {
            "target_node": node_id,
            "target_scope": target_scope if isinstance(target_scope, str) and target_scope.strip() else None,
            "cwd": str(node_cwd(node_id, files)),
            "context_key": session_context_key("node", node_id, None),
            "context_label": detail.get("title") or node_title_from_path(node_path, node_id),
            "context_path": node_path,
        }

    if session_type == "scope":
        hierarchy = files["hierarchy"]
        scope_id = validate_target_scope(target_scope, hierarchy, required=True)
        scope = find_hierarchy_node(scope_id, hierarchy) or {}
        return {
            "target_node": None,
            "target_scope": scope_id,
            "cwd": str(scope_cwd(scope_id, hierarchy)),
            "context_key": session_context_key("scope", None, scope_id),
            "context_label": scope.get("name") or scope_id,
            "context_path": scope.get("path") or scope_id,
        }

    return {
        "target_node": None,
        "target_scope": None,
        "cwd": str(ROOT),
        "context_key": "general",
        "context_label": "repo",
        "context_path": str(ROOT),
    }

def build_command(agent_name: str, prompt: str, cwd: str) -> list[str]:
    cfg = load_gateway_config(allow_example=True)
    agents = cfg.get("agents", {})
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail=f"Unknown agent: {agent_name}")
    agent_cfg = agents[agent_name]
    command = agent_cfg.get("command")
    if not isinstance(command, list) or not all(isinstance(x, str) for x in command):
        raise HTTPException(status_code=500, detail=f"Invalid command template for agent: {agent_name}")
    issues = command_template_issues(command)
    if issues:
        raise HTTPException(status_code=409, detail=f"Agent `{agent_name}` is not runnable: {', '.join(issues)}")
    return [part.replace("{prompt}", prompt).replace("{cwd}", cwd) for part in command]


def build_prompt_with_context(prompt: str, session: Session, files: dict[str, dict[str, Any]]) -> str:
    rollups = files.get("scope_rollup", {}).get("scopes", {})
    lines = [
        f"Session type: {session.session_type}",
        f"Context label: {session.context_label}",
        f"Context path: {session.context_path}",
        f"Author agent id for this run: gateway:{session.agent}:{session.id}",
    ]

    if session.session_type == "node" and session.target_node:
        graph_meta = graph_node(files, session.target_node)
        detail = node_detail(files, session.target_node)
        node = {**graph_meta, **detail}
        review_gate = node.get("review_gate", {}) if isinstance(node.get("review_gate"), dict) else {}
        external_review = node.get("external_review", {}) if isinstance(node.get("external_review"), dict) else {}
        lines.extend(
            [
                f"Target node: {session.target_node}",
                f"Status: {node.get('status', 'seed')}",
                f"Progress: {node.get('progress_pct')}",
                f"AI reviews: {review_gate.get('ai_review_count')}",
                f"Human reviews: {review_gate.get('human_review_count')}",
                f"External review required: {review_gate.get('external_ai_review_required')}",
                f"External review complete: {review_gate.get('external_ai_review_complete')}",
                f"External review verdict: {review_gate.get('external_ai_review_verdict')}",
                f"External review score: {review_gate.get('external_ai_review_score')}",
                f"External review hard fail: {review_gate.get('external_ai_review_hard_fail')}",
                f"External reviewer id: {review_gate.get('external_ai_reviewer_id')}",
                f"Recorded author agent id: {node.get('author_agent_id')}",
                f"External review independence confirmed: {external_review.get('independence_confirmed')}",
                f"Can enter fix: {node.get('can_enter_fix')}",
            ]
        )
    elif session.session_type == "scope" and session.target_scope:
        rollup = rollups.get(session.target_scope, {}) if isinstance(rollups, dict) else {}
        lines.extend(
            [
                f"Target scope: {session.target_scope}",
                f"Leaf descendants: {rollup.get('leaf_count')}",
                f"Ready count: {rollup.get('ready_count')}",
                f"Blocked count: {rollup.get('blocked_count')}",
                f"Review due count: {rollup.get('review_due_count')}",
            ]
        )

    lines.append("Boundedness: act only within this graph context; do not become the global router.")
    return "\n".join(lines) + "\n\n" + prompt


def ensure_session_log(session: Session) -> Session:
    if session.log_path:
        return session
    log_dir = session_log_dir(session)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "session.log"
    STORE.update(session.id, log_path=str(log_path))
    return STORE.get(session.id)


def session_log_dir(session: Session) -> Path:
    if session.session_type in {"node", "scope"} and session.context_path:
        context_dir = safe_repo_path(session.context_path)
        research_root = (ROOT / "research").resolve()
        if research_root in (context_dir, *context_dir.parents):
            return context_dir / "logs" / "agent_sessions" / session.id
    return ROOT / "artifacts" / "agent_sessions" / "general" / session.id


def start_session(session: Session, prompt: str, files: dict[str, dict[str, Any]]) -> Session:
    if session.status == "running":
        raise HTTPException(status_code=409, detail="Session is already running")
    enriched_prompt = build_prompt_with_context(prompt.strip(), session, files)
    command = build_command(session.agent, enriched_prompt, session.cwd)
    session = ensure_session_log(session)
    STORE.update(session.id, prompt=enriched_prompt, command=command, status="queued")
    STORE.append_log(session.id, f"[context] {session.session_type} {session.context_label}\n")
    STORE.append_log(session.id, f"[run] {' '.join(command)}\n")
    thread = threading.Thread(target=run_session_thread, args=(session.id, command, session.cwd), daemon=True)
    thread.start()
    return STORE.get(session.id)


def create_session(
    agent: str,
    session_type: str,
    target_node: str | None,
    target_scope: str | None,
    files: dict[str, dict[str, Any]],
) -> Session:
    meta = session_context_metadata(session_type, target_node, target_scope, files)
    session = STORE.create(
        agent=agent,
        target_node=meta["target_node"],
        cwd=meta["cwd"],
        session_type=session_type,
        target_scope=meta["target_scope"],
        context_key=meta["context_key"],
        context_label=meta["context_label"],
        context_path=meta["context_path"],
    )
    return ensure_session_log(session)


def graph_files_for_session_type(session_type: str) -> dict[str, dict[str, Any]]:
    if session_type == "scope":
        return full_graph_files()
    return minimal_graph_files()


def node_dir_for_node(node_id: str) -> Path:
    files = minimal_graph_files()
    node_id = validate_target_node(node_id, files, required=True) or ""
    node = graph_node(files, node_id)
    path_value = node.get("path")
    if not isinstance(path_value, str) or not path_value.strip():
        raise HTTPException(status_code=409, detail=f"Node has no path: {node_id}")

    node_dir = (ROOT / path_value).resolve()
    research_root = (ROOT / "research").resolve()
    if research_root not in (node_dir, *node_dir.parents):
        raise HTTPException(status_code=400, detail=f"Node path is outside research/: {path_value}")
    if not node_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Node directory does not exist: {path_value}")
    return node_dir


def node_manuscript_path(node_id: str) -> Path:
    node_dir = node_dir_for_node(node_id)
    return node_dir / "docs" / "manuscript.md"


def refresh_full_projection() -> None:
    script = ROOT / "scripts" / "refresh_views.py"
    if not script.is_file():
        raise HTTPException(status_code=409, detail=f"Refresh script not found: {path_for_client(script)}")
    result = subprocess.run(
        [sys.executable, str(script), "--mode", "full"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        tail = "\n".join(result.stdout.splitlines()[-12:])
        raise HTTPException(status_code=500, detail=f"Projection refresh failed:\n{tail}")


def write_node_stage(node_id: str, stage: str) -> dict[str, Any]:
    normalized = stage.strip().lower()
    if normalized not in ALLOWED_NODE_STAGES:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")
    if yaml is None:
        raise HTTPException(status_code=500, detail="PyYAML is required to edit status.yaml")

    status_path = node_dir_for_node(node_id) / "status.yaml"
    original = status_path.read_text(encoding="utf-8")
    data = yaml.safe_load(original)
    if not isinstance(data, dict):
        raise HTTPException(status_code=409, detail=f"status.yaml is not a mapping: {path_for_client(status_path)}")

    lifecycle = data.get("lifecycle")
    if not isinstance(lifecycle, dict):
        lifecycle = {}
        data["lifecycle"] = lifecycle
    lifecycle["stage"] = normalized
    if "status" in data:
        data["status"] = normalized
    data["heartbeat_at"] = datetime.now(timezone.utc).date().isoformat()
    data["last_actor"] = "human"

    status_path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    try:
        refresh_full_projection()
    except HTTPException:
        status_path.write_text(original, encoding="utf-8")
        raise

    return {
        "node_id": node_id,
        "path": path_for_client(status_path),
        "stage": normalized,
        "updated_at": mtime_iso(status_path),
    }


def path_for_client(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def mtime_iso(path: Path) -> str | None:
    if not path.exists():
        return None
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def run_session_thread(session_id: str, command: list[str], cwd: str) -> None:
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except Exception as exc:
        STORE.update(session_id, status="failed", finished_at=time.time(), return_code=-1)
        STORE.append_log(session_id, f"[launch_failed] {exc}\n")
        return

    STORE.update(session_id, process=process, status="running", started_at=time.time())
    assert process.stdout is not None
    for line in process.stdout:
        STORE.append_log(session_id, line)
    return_code = process.wait()
    final_status = "finished" if return_code == 0 else "failed"
    STORE.update(session_id, status=final_status, finished_at=time.time(), return_code=return_code, process=None)


STORE.restore_from_disk()


app = FastAPI(title="Research Agent Gateway", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

web_dir = SOURCE_ROOT / "web" / "app"
if web_dir.exists():
    app.mount("/app", StaticFiles(directory=str(web_dir), html=True), name="app")

research_dir = ROOT / "research"
if research_dir.exists():
    app.mount("/research", StaticFiles(directory=str(research_dir), html=False), name="research")


@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(url="/app/")


@app.get("/api/health")
def health() -> dict[str, Any]:
    cfg = load_gateway_config()
    return {
        "ok": True,
        "root": str(ROOT),
        "configured_agents": list((cfg.get("agents", {}) or {}).keys()),
        "config_source": cfg.get("_source"),
        "using_example_config": bool(cfg.get("_is_example")),
    }


@app.get("/api/app/bootstrap")
def api_app_bootstrap() -> dict[str, Any]:
    return gateway_readiness()


@app.get("/api/graph/status")
def api_graph_status() -> dict[str, Any]:
    return minimal_graph_files()["graph_status"]


@app.get("/api/graph/structure")
def api_graph_structure() -> dict[str, Any]:
    return minimal_graph_files()["graph"]


@app.get("/api/graph/hierarchy")
def api_graph_hierarchy() -> dict[str, Any]:
    return full_graph_files()["hierarchy"]


@app.get("/api/graph/details")
def api_graph_details() -> dict[str, Any]:
    return full_graph_files()["node_details"]


@app.get("/api/graph/rollup")
def api_graph_rollup() -> dict[str, Any]:
    return full_graph_files()["scope_rollup"]


@app.get("/api/graph/board")
def api_graph_board() -> dict[str, Any]:
    return full_graph_files()["board_state"]


@app.get("/api/intake/status")
def api_intake_status() -> dict[str, Any]:
    try:
        return intake_status(ROOT)
    except ResearchIntakeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))


@app.post("/api/intake/materials")
def api_intake_materials(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return ingest_materials(ROOT, payload, refresh=True)
    except ResearchIntakeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/node/{node_id}/manuscript")
def api_get_node_manuscript(node_id: str) -> dict[str, Any]:
    manuscript = node_manuscript_path(node_id)
    content = manuscript.read_text(encoding="utf-8") if manuscript.is_file() else ""
    return {
        "node_id": node_id,
        "path": path_for_client(manuscript),
        "content": content,
        "updated_at": mtime_iso(manuscript),
    }


@app.patch("/api/node/{node_id}/status")
def api_patch_node_status(node_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    stage = payload.get("stage")
    if not isinstance(stage, str):
        raise HTTPException(status_code=400, detail="stage must be a string")
    return write_node_stage(node_id, stage)


@app.put("/api/node/{node_id}/manuscript")
def api_put_node_manuscript(node_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    content = payload.get("content")
    if not isinstance(content, str):
        raise HTTPException(status_code=400, detail="content must be a string")
    manuscript = node_manuscript_path(node_id)
    manuscript.parent.mkdir(parents=True, exist_ok=True)
    manuscript.write_text(content, encoding="utf-8")
    return {
        "node_id": node_id,
        "path": path_for_client(manuscript),
        "content": content,
        "updated_at": mtime_iso(manuscript),
    }


@app.get("/api/agents/catalog")
def api_agents_catalog() -> dict[str, Any]:
    cfg = load_gateway_config()
    diagnostics, ready_agents = configured_agent_catalog(cfg)
    payload = {
        key: {
            "label": value.get("label", key),
            "cwd_mode": value.get("cwd_mode", "repo"),
            "command_ready": value.get("command_ready", False),
            "issues": value.get("issues", []),
        }
        for key, value in diagnostics.items()
    }
    return {
        "agents": payload,
        "ready_agents": ready_agents,
        "default_agent": resolve_default_agent(cfg, ready_agents),
    }


@app.get("/api/agents/sessions")
def api_agents_sessions(
    session_type: str | None = None,
    target_node: str | None = None,
    target_scope: str | None = None,
    context_key: str | None = None,
) -> dict[str, Any]:
    if session_type is not None and session_type not in {"general", "scope", "node"}:
        raise HTTPException(status_code=400, detail="session_type must be one of: general, scope, node")
    return {
        "sessions": STORE.list(
            session_type=session_type,
            target_node=target_node,
            target_scope=target_scope,
            context_key=context_key,
        )
    }


@app.get("/api/agents/sessions/{session_id}")
def api_agent_session(session_id: str) -> dict[str, Any]:
    try:
        session = STORE.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown session")
    return {"session": session.to_dict()}


@app.post("/api/agents/sessions")
def api_create_session(payload: dict[str, Any]) -> dict[str, Any]:
    target_node = payload.get("target_node")
    target_scope = payload.get("target_scope")
    agent = payload.get("agent")
    if not isinstance(agent, str) or not agent.strip():
        raise HTTPException(status_code=400, detail="Missing agent")
    session_type = normalize_session_type(payload)
    files = graph_files_for_session_type(session_type)
    session = create_session(
        agent=agent.strip(),
        session_type=session_type,
        target_node=target_node if isinstance(target_node, str) else None,
        target_scope=target_scope if isinstance(target_scope, str) else None,
        files=files,
    )
    return {"session": session.to_dict()}


@app.post("/api/agents/sessions/{session_id}/run")
def api_run_session(session_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    try:
        session = STORE.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown session")

    if session.status == "running":
        raise HTTPException(status_code=409, detail="Session is already running")

    prompt = payload.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")

    session = start_session(session, prompt.strip(), graph_files_for_session_type(session.session_type))
    return {"session": session.to_dict()}


@app.post("/api/agents/run")
def api_run_agent(payload: dict[str, Any]) -> dict[str, Any]:
    agent = payload.get("agent")
    target_node = payload.get("target_node")
    target_scope = payload.get("target_scope")
    prompt = payload.get("prompt")
    if not isinstance(agent, str) or not agent.strip():
        raise HTTPException(status_code=400, detail="Missing agent")
    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt is required")
    session_type = normalize_session_type(payload)
    files = graph_files_for_session_type(session_type)
    session = create_session(
        agent=agent.strip(),
        session_type=session_type,
        target_node=target_node if isinstance(target_node, str) else None,
        target_scope=target_scope if isinstance(target_scope, str) else None,
        files=files,
    )
    session = start_session(session, prompt.strip(), files)
    return {"session": session.to_dict()}


@app.post("/api/agents/sessions/{session_id}/stop")
def api_stop_session(session_id: str) -> dict[str, Any]:
    try:
        session = STORE.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Unknown session")
    if session.process and session.status == "running":
        session.process.terminate()
        STORE.append_log(session.id, "[stop] terminate signal sent\n")
        STORE.update(session.id, status="stopping")
    return {"session": STORE.get(session.id).to_dict()}
