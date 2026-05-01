#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path
from urllib.parse import quote, urlencode
from urllib.request import ProxyHandler, Request, build_opener

from gateway_fixture import add_graph_node, make_full_projection, make_graph_projection, repo_root, write_gateway_config, write_json, write_node_manuscript

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import sync_playwright
except Exception as exc:  # pragma: no cover - dependency-dependent
    raise SystemExit(
        "browser smoke: playwright is not installed. "
        "Run `python -m pip install -r test/requirements-browser.txt` first."
    ) from exc


DIRECT_HTTP = build_opener(ProxyHandler({}))


def free_port() -> int:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def http_json(base_url: str, path: str, *, method: str = "GET", payload: dict | None = None) -> dict:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = Request(f"{base_url}{path}", data=body, headers=headers, method=method)
    with DIRECT_HTTP.open(request, timeout=3) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_until_ready(base_url: str, process: subprocess.Popen[str], *, timeout_s: float = 15.0) -> dict:
    deadline = time.time() + timeout_s
    last_error = ""
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"gateway exited early with code {process.returncode}")
        try:
            payload = http_json(base_url, "/api/app/bootstrap")
            if payload.get("full_projection_ready") and payload.get("can_run_agents"):
                return payload
        except Exception as exc:  # pragma: no cover - readiness polling
            last_error = str(exc)
        time.sleep(0.2)
    raise RuntimeError(f"gateway not ready within timeout: {last_error}")


def start_gateway(base_url: str, fixture_root: Path) -> subprocess.Popen[str]:
    root = repo_root()
    env = os.environ.copy()
    env["AUTORESEARCH_ROOT"] = str(fixture_root)
    python_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(root) if not python_path else f"{root}{os.pathsep}{python_path}"
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.agent_gateway.app:app",
            "--host",
            "127.0.0.1",
            "--port",
            base_url.rsplit(":", 1)[1],
            "--log-level",
            "warning",
        ],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )


def stop_gateway(process: subprocess.Popen[str]) -> str:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:  # pragma: no cover - cleanup
            process.kill()
            process.wait(timeout=5)
    return process.stdout.read() if process.stdout else ""


def create_fixture(root: Path) -> tuple[str, str]:
    write_gateway_config(root / "config" / "agent_gateway.yaml", example=False)
    node_id = make_graph_projection(root)
    other_id = "research::P1_scope::P1_02_other"
    other_path = "research/P1_scope/P1_02_other"
    add_graph_node(root, other_id, other_path)
    make_full_projection(root, node_id)
    write_node_manuscript(root, "# Fixture Manuscript\n\n> quoted\n\n| a | b |\n| --- | --- |\n| 1 | 2 |\n")
    other_manuscript = root / other_path / "docs" / "manuscript.md"
    other_manuscript.parent.mkdir(parents=True, exist_ok=True)
    other_manuscript.write_text("# Other Manuscript\n\nother node body\n", encoding="utf-8")

    write_json(
        root / "backend" / "graph" / "hierarchy.json",
        {
            "id": "research",
            "name": "research",
            "children": [
                {"id": node_id, "name": "P1_01_node", "path": "research/P1_scope/P1_01_node", "children": []},
                {"id": other_id, "name": "P1_02_other", "path": other_path, "children": []},
            ],
        },
    )
    details_path = root / "backend" / "graph" / "node_details.json"
    details = json.loads(details_path.read_text(encoding="utf-8"))
    details["nodes"][other_id] = {
        "path": other_path,
        "title": "P1_02_other",
        "status": "active",
        "lifecycle_stage": "active",
        "kind": "leaf",
        "scheduler_ready": False,
        "truth_ready": False,
        "review_gate_state": "not_required",
        "execution_gate_state": "not_applicable",
        "handoff_readiness": "blocked_truth",
        "blocking_reasons": ["fixture_truth_missing"],
        "placeholder_risk": "none",
        "readme_path": f"{other_path}/README.md",
        "status_path": f"{other_path}/status.yaml",
        "review_gate": {},
        "files": [],
    }
    write_json(details_path, details)
    return node_id, other_id


def wait_for_condition(page, predicate, description: str, *, timeout_ms: float = 8000) -> None:
    deadline = time.time() + timeout_ms / 1000
    while time.time() < deadline:
        try:
            if predicate():
                return
        except Exception:
            pass
        page.wait_for_timeout(120)
    raise AssertionError(f"timeout waiting for: {description}")


def run_browser_flow(base_url: str, node_id: str, other_id: str) -> None:
    with sync_playwright() as playwright:
        browser = None
        try:
            browser = playwright.chromium.launch(headless=True)
        except PlaywrightError as exc:  # pragma: no cover - environment-dependent
            raise SystemExit(
                "browser smoke: chromium is not installed for Playwright. "
                "Run `python -m playwright install chromium` first."
            ) from exc

        page = browser.new_page()
        page.goto(f"{base_url}/app/", wait_until="domcontentloaded")

        wait_for_condition(
            page,
            lambda: page.locator("#heartbeat").get_attribute("data-state") in {"ready", "failed"},
            "heartbeat to leave loading",
        )
        if page.locator("#heartbeat").get_attribute("data-state") != "ready":
            raise AssertionError(f"heartbeat did not become ready: {page.locator('#heartbeat').text_content()}")

        if page.locator(".hero-action").count() != 1:
            raise AssertionError("shell must expose exactly one primary hero CTA")
        if page.locator("#drawer-toggle-button").get_attribute("aria-expanded") != "false":
            raise AssertionError("context drawer should be collapsed by default")

        tree_row = page.locator(f'.tree-row[data-node-id="{node_id}"]')
        wait_for_condition(page, lambda: tree_row.count() == 1, "tree node to appear")
        tree_row.click()

        page.locator("#workspace-tab-node").click()
        node_status = page.locator("#node-status-select")
        wait_for_condition(page, lambda: node_status.count() == 1, "node status select")
        if page.locator("#inspector-content #inspector-status-select").count() != 0:
            raise AssertionError("inspector still exposes editable status select")
        node_status.select_option("review")
        wait_for_condition(page, lambda: page.locator("#node-status-select").input_value() == "review", "status update to review")

        page.locator("#more-actions-button").click()
        watch_button = page.locator("#pin-node-button")
        wait_for_condition(page, lambda: watch_button.count() == 1 and watch_button.is_visible(), "watch node button")
        watch_button.click()
        watch_hint = page.locator("#watch-content .watch-hint")
        wait_for_condition(page, lambda: watch_hint.count() == 1, "watched workset hint")
        hint_text = watch_hint.text_content()
        if "不会改变" not in hint_text and "does not change" not in hint_text:
            raise AssertionError(f"watched workset hint is not explicit enough: {hint_text}")
        tree_meta = page.locator(f'.tree-row[data-node-id="{node_id}"] .tree-meta').first
        if tree_meta.locator(".tree-status-dot, .tree-signal").count() > 2:
            raise AssertionError("tree row exposes too many signals")

        page.locator("#workspace-tab-manuscript").click()
        editor = page.locator("#manuscript-editor")
        wait_for_condition(page, lambda: editor.count() == 1, "manuscript editor")
        dirty_text = "# Unsaved Draft\n\nthis text must survive a cancelled node switch\n"
        editor.fill(dirty_text)
        dismissed_dialogs: list[str] = []
        page.once("dialog", lambda dialog: (dismissed_dialogs.append(dialog.message), dialog.dismiss()))
        other_tree_row = page.locator(f'.tree-row[data-node-id="{other_id}"]')
        wait_for_condition(page, lambda: other_tree_row.count() == 1, "other tree node to appear")
        other_tree_row.click()
        wait_for_condition(page, lambda: len(dismissed_dialogs) == 1, "dirty manuscript switch confirm")
        if editor.input_value() != dirty_text:
            raise AssertionError("cancelled dirty-node switch did not preserve manuscript text")

        page.once("dialog", lambda dialog: dialog.accept())
        other_tree_row.click()
        wait_for_condition(page, lambda: "Other Manuscript" in editor.input_value(), "accepted dirty-node switch")
        tree_row.click()
        wait_for_condition(page, lambda: "Fixture Manuscript" in editor.input_value(), "return to original manuscript")
        page.locator("#workspace-tab-manuscript").click()
        wait_for_condition(page, lambda: editor.is_visible(), "manuscript editor visible after returning to original node")

        updated_text = "# Browser Smoke\n\n> evidence quote\n\n| left | right |\n| --- | --- |\n| alpha | beta |\n"
        editor.fill(updated_text)
        page.keyboard.press("Control+S")
        wait_for_condition(page, lambda: "Saved" in page.locator("#manuscript-status").text_content() or "已保存" in page.locator("#manuscript-status").text_content(), "manuscript save state")
        if not page.locator("#save-manuscript-button").is_disabled():
            raise AssertionError("save button should be disabled once the manuscript is saved")
        saved_payload = http_json(base_url, f"/api/node/{quote(node_id, safe='')}/manuscript")
        if saved_payload.get("content") != updated_text:
            raise AssertionError("Ctrl/Cmd+S did not persist manuscript content")
        preview = page.locator("#manuscript-preview")
        wait_for_condition(page, lambda: preview.locator("blockquote").count() == 1, "blockquote preview")
        wait_for_condition(page, lambda: preview.locator("table").count() == 1, "table preview")

        page.locator("#workspace-tab-session").click()
        prompt = page.locator("#agent-prompt")
        wait_for_condition(page, lambda: prompt.count() == 1, "session prompt")
        prompt.fill(
            f"Use @current, @scope, @node, @readme, @status, @manuscript, "
            f"and @research::{node_id.split('research::', 1)[1]} to summarize the current node."
        )
        for expected in ("@current ->", "@scope ->", "@node ->", "@readme ->", "@status ->", "@manuscript ->", node_id):
            wait_for_condition(page, lambda expected=expected: expected in page.locator(".resolved-context-preview").text_content(), f"draft mention preview {expected}")
        page.locator("#run-session-button").click()
        session_log = page.locator("#session-log")
        wait_for_condition(page, lambda: "gateway-ok" in session_log.text_content(), "session log output")
        wait_for_condition(page, lambda: "Browser Smoke" in page.locator(".resolved-context-preview").text_content(), "submitted resolved context preview")
        wait_for_condition(page, lambda: node_id in page.locator(".resolved-context-preview").text_content(), "submitted explicit-node preview")

        sessions = http_json(base_url, f"/api/agents/sessions?{urlencode({'session_type': 'node', 'target_node': node_id})}")
        latest = sessions["sessions"][0]
        if "content=not loaded" in latest.get("prompt", ""):
            raise AssertionError("@manuscript prompt still contains placeholder content")
        if "Browser Smoke" not in latest.get("prompt", ""):
            raise AssertionError("@manuscript prompt did not include saved manuscript content")
        for expected in ("current:", "scope:", "readme:", "status:", "manuscript_path:", node_id):
            if expected not in latest.get("prompt", ""):
                raise AssertionError(f"resolved mention prompt missing {expected}")

        selected_session = page.locator("#session-list .session-item.active").get_attribute("data-id")
        if not selected_session:
            raise AssertionError("no active session selected before reload")

        page.locator("#drawer-toggle-button").click()
        wait_for_condition(page, lambda: page.locator("#drawer-toggle-button").get_attribute("aria-expanded") == "true", "drawer expand")
        page.locator("#drawer-toggle-button").click()
        wait_for_condition(page, lambda: page.locator("#drawer-toggle-button").get_attribute("aria-expanded") == "false", "drawer collapse")
        sidebar_toggle = page.locator("#sidebar-toggle-button")
        if sidebar_toggle.is_visible():
            sidebar_toggle.click()

        page.reload(wait_until="domcontentloaded")
        wait_for_condition(
            page,
            lambda: page.locator("#heartbeat").get_attribute("data-state") in {"ready", "failed"},
            "heartbeat after reload",
        )
        if page.locator("#drawer-toggle-button").get_attribute("aria-expanded") != "false":
            raise AssertionError("drawer collapsed state did not persist across reload")
        active_after_reload = page.locator("#session-list .session-item.active").get_attribute("data-id")
        if active_after_reload != selected_session:
            raise AssertionError("current session id did not persist across reload")

        page.evaluate("localStorage.setItem('research_app_current_session_id', 'missing-session-id')")
        page.reload(wait_until="domcontentloaded")
        wait_for_condition(
            page,
            lambda: page.locator("#heartbeat").get_attribute("data-state") in {"ready", "failed"},
            "heartbeat after stale session reload",
        )
        if page.locator("#session-list .session-item.active").count() == 0 and page.locator("#session-list .session-item").count() == 0:
            raise AssertionError("stale session restore left no visible safe fallback")

        browser.close()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="browser_smoke_") as tmpdir:
        fixture_root = Path(tmpdir)
        node_id, other_id = create_fixture(fixture_root)
        port = free_port()
        base_url = f"http://127.0.0.1:{port}"
        process = start_gateway(base_url, fixture_root)
        try:
            wait_until_ready(base_url, process)
            run_browser_flow(base_url, node_id, other_id)
        finally:
            output = stop_gateway(process)
            if process.returncode not in (0, -15, 143):
                print(output)
                raise SystemExit(f"browser smoke: gateway exited with code {process.returncode}")
    print("browser smoke: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
