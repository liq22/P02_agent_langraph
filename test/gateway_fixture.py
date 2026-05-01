from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_gateway_config(path: Path, *, example: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    marker = "# example config\n" if example else ""
    command = [sys.executable, "-c", "print('gateway-ok')"]
    path.write_text(
        marker
        + "default_agent: echo\n"
        + "agents:\n"
        + "  echo:\n"
        + "    label: Echo Agent\n"
        + "    cwd_mode: node\n"
        + "    command:\n"
        + "".join(f"      - {json.dumps(part)}\n" for part in command),
        encoding="utf-8",
    )


def install_root(gateway: Any, root: Path) -> None:
    gateway.ROOT = root
    gateway.STORE = gateway.SessionStore(root)


def make_graph_projection(root: Path) -> str:
    node_id = "research::P1_scope::P1_01_node"
    node_path = root / "research" / "P1_scope" / "P1_01_node"
    node_path.mkdir(parents=True, exist_ok=True)
    (node_path / "README.md").write_text("# Node\n", encoding="utf-8")
    (node_path / "status.yaml").write_text("status: active\n", encoding="utf-8")
    write_json(
        root / "backend" / "graph" / "graph.json",
        {"nodes": {node_id: {"path": "research/P1_scope/P1_01_node", "status": "active"}}, "edges": []},
    )
    write_json(
        root / "backend" / "graph" / "graph_status.json",
        {"current_phase": "P1", "next_node": node_id, "unfinished_count": 1, "ready_nodes": [node_id], "blocked_nodes": []},
    )
    refresh_script = root / "scripts" / "refresh_views.py"
    refresh_script.parent.mkdir(parents=True, exist_ok=True)
    refresh_script.write_text(
        "import json, re\n"
        "from pathlib import Path\n"
        "root = Path(__file__).resolve().parent.parent\n"
        f"node_id = {json.dumps(node_id)}\n"
        "status_text = (root / 'research/P1_scope/P1_01_node/status.yaml').read_text(encoding='utf-8')\n"
        "stage = re.search(r'(?m)^\\s*(?:status|stage):\\s*([^\\s#]+)', status_text).group(1)\n"
        "graph_path = root / 'backend/graph/graph.json'\n"
        "graph = json.loads(graph_path.read_text(encoding='utf-8'))\n"
        "graph['nodes'][node_id]['status'] = stage\n"
        "graph_path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n"
        "details_path = root / 'backend/graph/node_details.json'\n"
        "if details_path.is_file():\n"
        "    details = json.loads(details_path.read_text(encoding='utf-8'))\n"
        "    details['nodes'][node_id]['status'] = stage\n"
        "    details['nodes'][node_id]['lifecycle_stage'] = stage\n"
        "    details_path.write_text(json.dumps(details, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    return node_id


def add_graph_node(root: Path, node_id: str, node_path: str) -> None:
    full_path = root / node_path
    full_path.mkdir(parents=True, exist_ok=True)
    (full_path / "README.md").write_text("# Node\n", encoding="utf-8")
    (full_path / "status.yaml").write_text("status: active\n", encoding="utf-8")
    graph_path = root / "backend" / "graph" / "graph.json"
    graph = json.loads(graph_path.read_text(encoding="utf-8"))
    graph["nodes"][node_id] = {"path": node_path, "status": "active"}
    write_json(graph_path, graph)


def make_full_projection(root: Path, node_id: str) -> None:
    node_path = "research/P1_scope/P1_01_node"
    write_json(
        root / "backend" / "graph" / "hierarchy.json",
        {"id": "research", "name": "research", "children": [{"id": node_id, "name": "P1_01_node", "path": node_path, "children": []}]},
    )
    write_json(
        root / "backend" / "graph" / "node_details.json",
        {
            "nodes": {
                node_id: {
                    "path": node_path,
                    "title": "P1_01_node",
                    "status": "active",
                    "lifecycle_stage": "active",
                    "kind": "leaf",
                    "scheduler_ready": True,
                    "truth_ready": False,
                    "review_gate_state": "not_required",
                    "execution_gate_state": "not_applicable",
                    "handoff_readiness": "blocked_truth",
                    "blocking_reasons": ["fixture_truth_missing"],
                    "placeholder_risk": "none",
                    "readme_path": f"{node_path}/README.md",
                    "status_path": f"{node_path}/status.yaml",
                    "review_gate": {},
                    "files": [],
                }
            }
        },
    )
    write_json(
        root / "backend" / "graph" / "scope_rollup.json",
        {
            "scopes": {
                "research": {
                    "children_count": 1,
                    "leaf_count": 1,
                    "scheduler_ready_count": 1,
                    "scheduler_blocked_count": 0,
                    "truth_ready_count": 0,
                    "truth_blocked_count": 1,
                    "review_blocked_count": 0,
                    "execution_blocked_count": 0,
                    "handoff_ready_count": 0,
                    "placeholder_confirmed_count": 0,
                }
            }
        },
    )
    write_json(
        root / "backend" / "graph" / "board_state.json",
        {
            "lanes": {
                "scheduler_now": [node_id],
                "truth_ready": [],
                "review_blocked": [],
                "execution_blocked": [],
                "truth_blocked": [],
                "active_work": [],
                "parked": [],
            }
        },
    )


def write_node_manuscript(root: Path, content: str) -> Path:
    manuscript = root / "research" / "P1_scope" / "P1_01_node" / "docs" / "manuscript.md"
    manuscript.parent.mkdir(parents=True, exist_ok=True)
    manuscript.write_text(content, encoding="utf-8")
    return manuscript


def wait_for_session(gateway: Any, session_id: str, *, timeout_s: float = 5.0) -> dict[str, Any]:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        session = gateway.STORE.get(session_id)
        if session.status in {"finished", "failed"}:
            return session.to_dict()
        time.sleep(0.05)
    return gateway.STORE.get(session_id).to_dict()
