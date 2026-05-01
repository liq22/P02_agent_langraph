#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
import tempfile
from pathlib import Path

from gateway_fixture import (
    add_graph_node,
    install_root,
    make_full_projection,
    make_graph_projection,
    repo_root,
    wait_for_session,
    write_gateway_config,
)

def check_frontend_contract(root: Path) -> list[str]:
    failures: list[str] = []
    index = (root / "web" / "app" / "index.html").read_text(encoding="utf-8")
    module_files = [
        root / "web" / "app" / "app.js",
        root / "web" / "app" / "ui_core.js",
        root / "web" / "app" / "workspace.js",
        root / "web" / "app" / "manuscript.js",
        root / "web" / "app" / "sessions.js",
    ]
    app = "\n".join(path.read_text(encoding="utf-8") for path in module_files if path.is_file())
    styles = (root / "web" / "app" / "styles.css").read_text(encoding="utf-8")
    app_py = (root / "backend" / "agent_gateway" / "app.py").read_text(encoding="utf-8")
    dashboard = (root / "web" / "dashboard" / "app.js").read_text(encoding="utf-8")
    cockpit_app_doc = (root / "docs" / "architecture" / "agent_cockpit_app.md").read_text(encoding="utf-8")
    cockpit_v2_doc = (root / "docs" / "architecture" / "agent_cockpit_v2.md").read_text(encoding="utf-8")
    optimization_doc = (root / "docs" / "architecture" / "autoresearch_optimization_report_4level.md").read_text(encoding="utf-8")
    frontend_4level_doc = (root / "docs" / "architecture" / "frontend_optimization_plan_4level.md").read_text(encoding="utf-8")
    overview_pos = index.find('id="overview-view"')
    setup_pos = index.find('id="setup-content"')
    node_pos = index.find('id="node-view"')
    inspector_pos = index.find('id="inspector-content"')
    drawer_pos = index.find('id="context-drawer"')
    focus_card_pos = index.find('id="focus-card"')
    session_pos = index.find('id="session-view"')
    session_list_pos = index.find('id="session-list"')
    required = {
        "module entry": 'type="module"' in index and 'src="./app.js"' in index,
        "module files present": all(path.is_file() for path in module_files),
        "root redirects to app": 'return RedirectResponse(url="/app/")' in app_py,
        "start ui removed": not (root / "web" / "app" / "start.html").exists() and not (root / "web" / "app" / "start.js").exists(),
        "start route removed": '@app.get("/start")' not in app_py and "/app/start.html" not in app_py,
        "material intake api": '@app.post("/api/intake/materials")' in app_py and '@app.get("/api/intake/status")' in app_py,
        "material intake script": (root / "scripts" / "intake_research_materials.py").is_file(),
        "material intake skill": (root / ".agent" / "skills" / "research_material_intake" / "SKILL.md").is_file(),
        "bootstrap api": "/api/app/bootstrap" in app,
        "session run api": "/api/agents/run" not in app and "${API.sessions}/${encodeURIComponent(session.id)}/run" in app,
        "session context filtering": "function sessionMatchesContext" in app and "function visibleSessions" in app,
        "manuscript api": "/api/node/" in app and "/manuscript" in app,
        "node status patch api": "@app.patch(\"/api/node/{node_id}/status\")" in app_py,
        "setup panel": "setup-content" in index,
        "workspace tabs": "workspace-tab-toggle" not in index and "manuscript-view" in index and "node-view" in index,
        "single workspace control": "workspace-tab-toggle" not in index and "workspace-tab-toggle" not in app,
        "collapsible navigation": "sidebar-toggle-button" in index and "setNavOpen" in app and "nav-collapsed" in styles,
        "collapsible drawer": "drawer-toggle-button" in index and "setDrawerOpen" in app and "drawer-collapsed" in styles,
        "primary session cta": 'id="open-session-button"' in index and "hero-action" in index and 'id="more-actions-button"' in index,
        "compact topbar summary": "primary-stat" in app and "topbar-meta" in app and "repeat(3, minmax(0, 1fr))" in styles,
        "tree uses quiet status signals": "treeSignalsForNode(node.id, status)" in app and "tree-status-dot" in styles and "badgesForNode" not in app,
        "active set list removed": "hot-queue" not in index and "renderHotQueue" not in app and "showFullHotQueue" not in app,
        "tree collapse stays collapsed": "if (hasChildren && depth < 1 && !expanded)" not in app,
        "tree expansion persisted": "saveExpandedNodes" in app and "research_app_expanded_nodes" in app,
        "left scheduler removed": "scheduler-cards" not in index and "renderScheduler" not in app,
        "context drawer restored": drawer_pos >= 0 and "drawer-toggle-button" in index,
        "context drawer scrollable": ".sidebar-right" in styles and "overflow-y: auto" in styles and "overscroll-behavior: contain" in styles,
        "accessible workspace tabs": 'role="tablist"' in index and 'role="tab"' in index and 'role="tabpanel"' in index and "handleWorkspaceTabKeydown" in app,
        "accessible tree keyboard path": 'role="tree"' in index and 'role="treeitem"' in app and "handleTreeRowKeydown" in app and "aria-level" in app,
        "drawer aria controls": 'aria-controls="context-drawer-panels"' in index and 'aria-expanded="false"' in index and "button.setAttribute('aria-expanded'" in app,
        "heartbeat finite states": "HEARTBEAT_STATES" in app and 'data-state' in index and 'heartbeatGateway' in app,
        "setup moved into drawer": drawer_pos >= 0 and setup_pos > drawer_pos,
        "focus card moved into drawer": drawer_pos >= 0 and focus_card_pos > drawer_pos,
        "inspector moved into drawer": drawer_pos >= 0 and inspector_pos > drawer_pos,
        "single status authority": "statusSelectHtml('node-status-select'" in app and "statusSelectHtml('inspector-status-select'" not in app and 'data-open-node-status="true"' in app and "updateNodeStatus" in app and "/status" in app,
        "overview atlas replaces pack": "d3.tree().nodeSize" in app and "d3.pack()" not in app and "atlas-label" in styles,
        "session list moved into session tab": session_pos >= 0 and session_list_pos > session_pos,
        "overview has no setup sidecar": overview_pos >= 0 and (setup_pos < overview_pos or setup_pos > node_pos),
        "foldable node files": "foldSection(t('files')" in app and 'details class="fold-section"' in app and ".fold-section summary" in styles,
        "node panel avoids file duplication": "<h4>${t('files')}</h4>" not in app,
        "manuscript dirty guard": "confirmDiscardManuscriptChanges" in app and "beforeunload" in app and "renderMarkdownPreview" in app,
        "manuscript keyboard save": "event.key.toLowerCase() !== 's'" in app and "saveManuscript().catch" in app,
        "truthful manuscript mentions": "CONTEXT_MENTIONS" in app and "@current" in app and "promptWithResolvedMentions" in app and "manuscriptSaveFirst" in app and "resolveManuscriptContext" in app and "content=not loaded" not in app,
        "explicit node mention syntax": "@research::" in index and "@research::" in app and "prompt.match(/@research::" in app,
        "session persistence": "research_app_current_session_id" in app and "saveCurrentSessionId" in app and "loadCurrentSessionId" in app,
        "overview on demand render": "function renderOverviewIfVisible()" in app and "if (state.workspaceTab !== 'overview') return;" in app,
        "workspace render helpers": "function renderTreeRow(" in app and "function renderFocusCardBody(" in app and "function renderNodeReviewSection(" in app,
        "session render helpers": "function renderPromptActionChip(" in app and "function renderSessionHeaderCard(" in app and "function renderSessionListItem(" in app,
        "watch workset semantics": "watch-hint" in app and "Watched workset" in app and "pinned nodes" not in app,
        "browser smoke runner": (root / "test" / "run_browser_smoke.py").is_file(),
        "browser requirements": (root / "test" / "requirements-browser.txt").is_file(),
        "gateway root override": "AUTORESEARCH_ROOT" in app_py,
        "display title helper": "function displayNodeTitle(value)" in app and r"replace(/^P\d+_(?:\d+_)?/, '')" in app and r"replace(/_/g, '')" in app,
        "display title applied to tree": "displayNodeTitle(node.name)" in app and 'class="tree-title"' in app,
        "display title applied to graph": "displayNodeTitle(detail.title || node.name)" in app and "displayNodeTitle(d.data.name)" in app,
        "display title applied to node/session": "displayNodeTitle(detail.title)" in app and "displayNodeTitle(session.context_label)" in app,
        "tree navigator": "tree-root" in index and "collapse-all-button" in index,
        "node datalist": "node-options" in index,
        "mention suggestions": "mention-suggestions" in index and "renderMentionSuggestions" in app,
        "prompt actions": "prompt-actions" in index and "bounded experiment" in app.lower(),
        "run status": "agent-run-status" in index,
        "blocked refresh command": "python scripts/refresh_views.py --mode full" in app,
        "node mode label": "nodeMode" in app,
        "node profile label": "nodeProfile" in app,
        "dashboard scope rollup": "scopeRollup" in dashboard,
        "dashboard diagnostics label": "diagnostics" in dashboard,
        "dashboard binder count": "missingExecutionBinderCount" in dashboard,
        "dashboard boundary documented": "web/dashboard" in (root / "docs" / "dev.md").read_text(encoding="utf-8") and "static read-only" in (root / "docs" / "dev.md").read_text(encoding="utf-8"),
        "canonical cockpit vocabulary documented": "Deprecated Vocabulary" in cockpit_app_doc and "scope rail" in cockpit_app_doc and "Screenshots are reference artifacts only" in cockpit_app_doc and "Deprecated IA terms" in cockpit_v2_doc,
        "repo optimization report documented": "Autoresearch 仓库优化内容报告" in optimization_doc and "先删噪声，再补安全，再收敛语义，最后美化" in optimization_doc,
        "frontend 4level uses current cockpit ia": "Global Scheduler Bar" in frontend_4level_doc and "Tree Navigator" in frontend_4level_doc and "Overview / Node / Manuscript / Session" in frontend_4level_doc and "Overview / Board / Session 三种模式" not in frontend_4level_doc,
    }
    for name, ok in required.items():
        if not ok:
            failures.append(name)
    return failures


def main() -> int:
    root = repo_root()
    sys.path.insert(0, str(root))
    gateway = importlib.import_module("backend.agent_gateway.app")
    failures: list[str] = []

    with tempfile.TemporaryDirectory(prefix="gateway_acceptance_") as tmpdir:
        tmp = Path(tmpdir)
        write_gateway_config(tmp / "config" / "agent_gateway.yaml.example", example=True)
        install_root(gateway, tmp)

        bootstrap = gateway.gateway_readiness()
        if bootstrap["graph_ready"]:
            failures.append("missing graph should not be ready")
        if "python scripts/refresh_views.py --mode graph_only" not in bootstrap["setup_steps"]:
            failures.append("bootstrap missing graph_only setup step")
        if bootstrap["can_run_agents"]:
            failures.append("example config should not be runnable before graph is ready")

        node_id = make_graph_projection(tmp)
        bootstrap = gateway.gateway_readiness()
        if not bootstrap["graph_ready"] or not bootstrap["can_run_agents"] or bootstrap["next_node"] != node_id:
            failures.append("example config + minimal graph should be runnable when command exists")
        if bootstrap.get("full_projection_ready"):
            failures.append("full projection should not be ready after minimal graph only")
        if "python scripts/refresh_views.py --mode full" not in bootstrap["setup_steps"]:
            failures.append("bootstrap missing full projection setup step")
        if bootstrap.get("default_agent") != "echo":
            failures.append("bootstrap did not expose default agent")

        try:
            status_payload = gateway.api_graph_status()
            structure_payload = gateway.api_graph_structure()
            if status_payload.get("next_node") != node_id:
                failures.append("minimal graph status endpoint did not return next_node")
            if node_id not in (structure_payload.get("nodes") or {}):
                failures.append("minimal graph structure endpoint did not return node")
            if set(structure_payload.keys()) != {"nodes", "edges"}:
                failures.append(f"graph structure has non-minimal top-level keys: {sorted(structure_payload.keys())}")
            for item_id, payload in (structure_payload.get("nodes") or {}).items():
                if set(payload.keys()) != {"path", "status"}:
                    failures.append(f"graph node payload is not minimal for {item_id}: {sorted(payload.keys())}")
            for index, payload in enumerate(structure_payload.get("edges") or []):
                if set(payload.keys()) != {"src", "rel", "dst"}:
                    failures.append(f"graph edge payload is not minimal at {index}: {sorted(payload.keys())}")
            graph_status_keys = {"current_phase", "next_node", "ready_nodes", "blocked_nodes", "unfinished_count"}
            if not graph_status_keys.issubset(status_payload.keys()):
                failures.append(f"graph status missing scheduler keys: {sorted(graph_status_keys - set(status_payload.keys()))}")
            for ui_key in ("currentSessionId", "drawerOpen", "workspaceTab", "selectedNodeId"):
                if ui_key in status_payload:
                    failures.append(f"graph status leaked UI-only key: {ui_key}")
        except Exception as exc:
            failures.append(f"minimal graph endpoints should not require full projection: {exc}")

        try:
            intake = gateway.api_intake_materials(
                {
                    "target_node": node_id,
                    "material_summary": "Existing P1 protocol notes.",
                    "available_assets": "A fixture dataset and a baseline script.",
                    "desired_output": "Turn these notes into a bounded experiment plan.",
                    "constraints": "No external downloads.",
                    "known_gaps": "Metrics are not finalized.",
                }
            )
            if intake.get("entry_phase") != "P1":
                failures.append(f"material intake did not infer P1: {intake}")
            if intake.get("target_node") != node_id:
                failures.append(f"material intake targeted wrong node: {intake}")
            if intake.get("recommended_worker") != "experiment_design_or_execution":
                failures.append(f"material intake returned wrong P1 worker: {intake}")
            for key in ("artifact_path", "docs_path"):
                if not (tmp / str(intake.get(key, ""))).is_file():
                    failures.append(f"material intake did not write {key}: {intake}")
        except Exception as exc:
            failures.append(f"material intake endpoint failed: {exc}")

        try:
            manuscript = gateway.api_get_node_manuscript(node_id)
            expected_path = "research/P1_scope/P1_01_node/docs/manuscript.md"
            if manuscript.get("path") != expected_path:
                failures.append(f"manuscript endpoint returned wrong path: {manuscript}")
            saved = gateway.api_put_node_manuscript(node_id, {"content": "draft body\n"})
            if saved.get("content") != "draft body\n":
                failures.append("manuscript save response did not echo content")
            if (tmp / expected_path).read_text(encoding="utf-8") != "draft body\n":
                failures.append("manuscript save did not write node-local docs/manuscript.md")
        except Exception as exc:
            failures.append(f"manuscript endpoints failed: {exc}")

        try:
            gateway.api_put_node_manuscript(node_id, {"content": 12})
            failures.append("manuscript save should reject non-string content")
        except Exception as exc:
            if getattr(exc, "status_code", None) != 400:
                failures.append(f"manuscript save invalid payload should return 400: {exc}")

        try:
            gateway.api_graph_details()
            failures.append("details endpoint should require full projection")
        except Exception as exc:
            if getattr(exc, "status_code", None) != 409:
                failures.append(f"details endpoint should return 409 when full projection is missing: {exc}")

        write_gateway_config(tmp / "config" / "agent_gateway.yaml", example=False)
        bootstrap = gateway.gateway_readiness()
        if bootstrap.get("default_agent") != "echo":
            failures.append("real config default agent missing")

        try:
            gateway.api_run_agent({"agent": "echo", "target_node": "missing", "prompt": "hello"})
            failures.append("unknown target node should fail")
        except Exception:
            pass

        response = gateway.api_run_agent({"agent": "echo", "target_node": node_id, "prompt": "hello"})
        session = wait_for_session(gateway, response["session"]["id"])
        if session["status"] != "finished" or session["return_code"] != 0:
            failures.append(f"run session failed: {session}")
        if session.get("context_key") != f"node::{node_id}":
            failures.append(f"node session has wrong context key: {session.get('context_key')}")
        if "research/P1_scope/P1_01_node/logs/agent_sessions" not in session.get("log_path", ""):
            failures.append(f"node session log is not node-local: {session.get('log_path')}")
        if not any("gateway-ok" in line for line in session.get("log_lines", [])):
            failures.append("session log missing command output")
        if not any("Author agent id for this run: gateway:echo:" in line for line in session.get("prompt", "").splitlines()):
            failures.append("session prompt missing author agent id")

        other_id = "research::P1_scope::P1_02_other"
        add_graph_node(tmp, other_id, "research/P1_scope/P1_02_other")
        other_session = gateway.api_create_session({"agent": "echo", "target_node": other_id})["session"]
        node_sessions = gateway.api_agents_sessions(session_type="node", target_node=node_id)["sessions"]
        if not node_sessions or any(item.get("target_node") != node_id for item in node_sessions):
            failures.append("target_node session filter leaked another node session")
        other_sessions = gateway.api_agents_sessions(context_key=f"node::{other_id}")["sessions"]
        if [item.get("id") for item in other_sessions] != [other_session["id"]]:
            failures.append("context_key session filter did not isolate the other node")

        try:
            gateway.api_run_agent({"agent": "echo", "session_type": "scope", "target_scope": node_id, "prompt": "hello"})
            failures.append("scope session should require full projection")
        except Exception as exc:
            if getattr(exc, "status_code", None) != 409:
                failures.append(f"scope session should return 409 when full projection is missing: {exc}")

        make_full_projection(tmp, node_id)
        bootstrap = gateway.gateway_readiness()
        if not bootstrap.get("full_projection_ready"):
            failures.append("full projection should be ready after projection files are written")
        try:
            details_payload = gateway.api_graph_details()
            rollup_payload = gateway.api_graph_rollup()
            board_payload = gateway.api_graph_board()
            detail = details_payload.get("nodes", {}).get(node_id, {})
            if detail.get("kind") not in {"parent", "leaf"}:
                failures.append("details endpoint missing parent/leaf kind")
            for key in ("scheduler_ready", "truth_ready", "review_gate_state", "execution_gate_state", "handoff_readiness", "blocking_reasons", "placeholder_risk"):
                if key not in detail:
                    failures.append(f"details endpoint missing truth field: {key}")
            root_roll = rollup_payload.get("scopes", {}).get("research", {})
            for key in ("scheduler_ready_count", "scheduler_blocked_count", "truth_ready_count", "truth_blocked_count", "review_blocked_count", "execution_blocked_count", "handoff_ready_count", "placeholder_confirmed_count"):
                if key not in root_roll:
                    failures.append(f"rollup endpoint missing truth count: {key}")
            lane_keys = set((board_payload.get("lanes") or {}).keys())
            expected_lanes = {"scheduler_now", "truth_ready", "review_blocked", "execution_blocked", "truth_blocked", "active_work", "parked"}
            if lane_keys != expected_lanes:
                failures.append(f"board endpoint returned wrong lane set: {sorted(lane_keys)}")
        except Exception as exc:
            failures.append(f"truth-facing projection endpoints failed: {exc}")

        try:
            patched = gateway.api_patch_node_status(node_id, {"stage": "review"})
            status_text = (tmp / "research/P1_scope/P1_01_node/status.yaml").read_text(encoding="utf-8")
            graph_payload = json.loads((tmp / "backend/graph/graph.json").read_text(encoding="utf-8"))
            details_payload = json.loads((tmp / "backend/graph/node_details.json").read_text(encoding="utf-8"))
            if patched.get("stage") != "review":
                failures.append(f"status patch returned wrong stage: {patched}")
            if "status: review" not in status_text or "stage: review" not in status_text:
                failures.append("status patch did not update status.yaml status and lifecycle.stage")
            if graph_payload["nodes"][node_id]["status"] != "review":
                failures.append("status patch did not refresh graph status")
            if details_payload["nodes"][node_id]["status"] != "review":
                failures.append("status patch did not refresh node details")
        except Exception as exc:
            failures.append(f"node status patch failed: {exc}")

        try:
            gateway.api_patch_node_status(node_id, {"stage": "invalid"})
            failures.append("status patch should reject invalid stage")
        except Exception as exc:
            if getattr(exc, "status_code", None) != 400:
                failures.append(f"status patch invalid stage should return 400: {exc}")

        restored = gateway.SessionStore(tmp)
        restored.restore_from_disk()
        if not restored.list():
            failures.append("session restore did not load disk logs")
        restored_node = [item for item in restored.list(target_node=node_id) if item.get("id") == session["id"]]
        if not restored_node or restored_node[0].get("context_key") != f"node::{node_id}":
            failures.append("session restore did not preserve node context metadata")

    failures.extend(check_frontend_contract(root))

    if failures:
        print("gateway acceptance: fail")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("gateway acceptance: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
