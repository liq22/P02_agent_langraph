#!/usr/bin/env python3
"""Validate a Claude Code handoff artifact for P02 submission-ready work.

The validator is intentionally dependency-light. JSON is preferred; YAML is
accepted when PyYAML is available.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REQUIRED = [
    "handoff_version", "task_id", "assistant", "role", "mode", "status",
    "non_authority_statement", "delegation", "scope", "commands_run",
    "findings", "evidence", "validation", "handoff_to_codex",
]

ALLOWED_STATUS = {"pass", "revise", "block", "incomplete"}
ALLOWED_MODES = {"read_only", "plan_first", "edit_allowed"}
FORBIDDEN_CHANGED_PREFIXES = (
    "backend/graph/", "obsidian/", "web/dashboard/",
)
FORBIDDEN_TRUTH_PHRASES = (
    "final submission-ready", "final submission ready", "submission-ready achieved",
    "submission ready achieved", "final gate passed", "research truth: pass",
)


def _parse(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    raise SystemExit(f"Cannot parse handoff as JSON or YAML: {path}")


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def validate(data: dict[str, Any]) -> dict[str, Any]:
    blockers: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED:
        if field not in data:
            blockers.append(f"missing field: {field}")

    if data.get("handoff_version") != "claude_code_handoff_v2":
        blockers.append("handoff_version must be claude_code_handoff_v2")
    if data.get("assistant") != "claude_code":
        blockers.append("assistant must be claude_code")
    if data.get("status") not in ALLOWED_STATUS:
        blockers.append(f"invalid status: {data.get('status')!r}")
    if data.get("mode") not in ALLOWED_MODES:
        blockers.append(f"invalid mode: {data.get('mode')!r}")

    non_auth = str(data.get("non_authority_statement", "")).lower()
    if "does not claim submission-ready" not in non_auth and "does not claim submission ready" not in non_auth:
        blockers.append("non_authority_statement must explicitly say it does not claim submission-ready")

    delegation = data.get("delegation", {}) if isinstance(data.get("delegation"), dict) else {}
    if delegation.get("requested_by") != "codex":
        blockers.append("delegation.requested_by must be codex")
    if not delegation.get("target_gate"):
        blockers.append("delegation.target_gate missing")

    scope = data.get("scope", {}) if isinstance(data.get("scope"), dict) else {}
    inspected = _as_list(scope.get("inspected_files"))
    changed = _as_list(scope.get("changed_files"))
    allowed = _as_list(scope.get("allowed_files"))
    forbidden = _as_list(scope.get("forbidden_files"))
    if not inspected:
        blockers.append("scope.inspected_files is empty")

    for path in changed:
        s = str(path)
        if any(s.startswith(prefix) for prefix in FORBIDDEN_CHANGED_PREFIXES):
            blockers.append(f"forbidden changed file: {s}")
        if any(s.startswith(str(prefix).rstrip('*').rstrip('/')) for prefix in forbidden):
            blockers.append(f"changed file matches explicit forbidden scope: {s}")
    if changed and allowed:
        for path in changed:
            s = str(path)
            if not any(s.startswith(str(prefix).rstrip('*').rstrip('/')) for prefix in allowed):
                warnings.append(f"changed file may be outside allowed scope: {s}")

    commands = _as_list(data.get("commands_run"))
    if data.get("status") == "pass":
        if not commands:
            blockers.append("status=pass requires commands_run or explicit command record with command=none")
        else:
            has_success = False
            for cmd in commands:
                if isinstance(cmd, dict) and cmd.get("exit_code") == 0:
                    has_success = True
            if not has_success:
                warnings.append("status=pass but no command has exit_code 0; Codex must verify manually")

    findings = data.get("findings", {}) if isinstance(data.get("findings"), dict) else {}
    for key in ("supported", "gaps", "risks", "hard_fail_candidates"):
        if key not in findings:
            blockers.append(f"findings.{key} missing")

    validation = data.get("validation", {}) if isinstance(data.get("validation"), dict) else {}
    if validation.get("requires_codex_validation") is not True:
        blockers.append("validation.requires_codex_validation must be true")
    expected = str(validation.get("expected_codex_validator", ""))
    if "validate_claude_handoff.py" not in expected:
        blockers.append("validation.expected_codex_validator must reference validate_claude_handoff.py")

    h = data.get("handoff_to_codex", {}) if isinstance(data.get("handoff_to_codex"), dict) else {}
    blockers_list = _as_list(h.get("blockers"))
    if "safe_to_merge" not in h:
        blockers.append("handoff_to_codex.safe_to_merge missing")
    if h.get("safe_to_merge") is True and blockers_list:
        blockers.append("safe_to_merge=true but blockers are non-empty")
    if not h.get("recommended_next_action"):
        blockers.append("handoff_to_codex.recommended_next_action missing")

    text_blob = json.dumps(data, ensure_ascii=False).lower()
    if any(token in text_blob for token in FORBIDDEN_TRUTH_PHRASES):
        warnings.append("handoff uses final submission-ready wording; Codex must not treat it as final authority")

    return {"handoff_valid": not blockers, "blockers": blockers, "warnings": warnings}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--handoff", required=True)
    args = ap.parse_args()
    result = validate(_parse(Path(args.handoff)))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["handoff_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
