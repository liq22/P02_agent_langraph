#!/usr/bin/env python3
"""Report internal jargon in entry docs, skills, and node-local files."""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


SCAN_EXTENSIONS = {".md", ".yaml", ".yml"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    term: str
    severity: str
    replacement: str


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report banned internal jargon without rewriting files.")
    parser.add_argument("paths", nargs="*", help="Files or directories to scan.")
    parser.add_argument("--paths", nargs="*", dest="extra_paths", help="Files or directories to scan.")
    parser.add_argument("--root", default=str(repo_root_from_script()), help="Repository root.")
    parser.add_argument("--rules", default="config/jargon_rules.yaml", help="Rules file relative to --root.")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when banned terms are found.")
    parser.add_argument("--warn-only", action="store_true", help="Always return zero; useful for skills and research nodes.")
    return parser.parse_args()


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def as_posix_under(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def is_skipped(rel_path: str, skip_patterns: list[str]) -> bool:
    parts = rel_path.split("/")
    if any(part in {".git", ".venv", "__pycache__"} for part in parts):
        return True
    parents = ["/".join(parts[:index]) for index in range(1, len(parts))]
    return any(
        fnmatch.fnmatch(rel_path, pattern)
        or rel_path.startswith(pattern.rstrip("/") + "/")
        or any(fnmatch.fnmatch(parent, pattern) for parent in parents)
        for pattern in skip_patterns
    )


def iter_scan_files(root: Path, inputs: list[str], skip_patterns: list[str]) -> list[Path]:
    raw_inputs = inputs or ["."]
    files: list[Path] = []
    for raw in raw_inputs:
        path = (root / raw).resolve() if not Path(raw).is_absolute() else Path(raw).resolve()
        if not path.exists():
            print(f"[warn] scan path does not exist: {raw}", file=sys.stderr)
            continue
        if path.is_file():
            rel_path = as_posix_under(path, root)
            if path.suffix in SCAN_EXTENSIONS and not is_skipped(rel_path, skip_patterns):
                files.append(path)
            continue
        for candidate in sorted(path.rglob("*")):
            if not candidate.is_file() or candidate.suffix not in SCAN_EXTENSIONS:
                continue
            rel_path = as_posix_under(candidate, root)
            if not is_skipped(rel_path, skip_patterns):
                files.append(candidate)
    return sorted(set(files))


def term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if re.fullmatch(r"[A-Za-z0-9_-]+", term):
        return re.compile(rf"(?<![A-Za-z0-9_-]){escaped}(?![A-Za-z0-9_-])", re.IGNORECASE)
    return re.compile(escaped, re.IGNORECASE)


def banned_term_findings(
    path: Path,
    root: Path,
    text: str,
    banned: dict[str, dict[str, Any]],
    severity: str,
) -> list[Finding]:
    findings: list[Finding] = []
    rel_path = Path(as_posix_under(path, root))
    for term, rule in banned.items():
        replacement = str((rule or {}).get("replacement", "")).strip()
        pattern = term_pattern(str(term))
        for line_no, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                findings.append(Finding(rel_path, line_no, str(term), severity, replacement))
    return findings


def frontmatter_text(text: str) -> str:
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    return match.group(1) if match else ""


def local_entry_field_findings(
    path: Path,
    root: Path,
    text: str,
    forbidden_fields: set[str],
    severity: str,
) -> list[Finding]:
    rel = as_posix_under(path, root)
    if not rel.endswith("/skills/local_entry.md"):
        return []
    findings: list[Finding] = []
    fm = frontmatter_text(text)
    if not fm:
        return findings
    for line_no, line in enumerate(fm.splitlines(), start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        field = stripped.split(":", 1)[0]
        if field in forbidden_fields:
            findings.append(Finding(Path(rel), line_no, field, severity, "move to backend/registry/runtime_policy/"))
    return findings


def node_mode_for_path(root: Path, node_rel: str) -> str:
    overrides_path = root / "backend" / "registry" / "skill_registry" / "local_skill_overrides.yaml"
    if not overrides_path.is_file():
        return ""
    payload = load_yaml(overrides_path)
    nodes = payload.get("nodes")
    if not isinstance(nodes, dict):
        return ""
    cfg = nodes.get(node_rel)
    if not isinstance(cfg, dict):
        return ""
    return str(cfg.get("node_mode", "")).strip()


def sop_findings(path: Path, root: Path, severity: str) -> list[Finding]:
    rel = as_posix_under(path, root)
    if not rel.endswith("/skills/SOP.md") or not rel.startswith("research/"):
        return []
    node_rel = str(Path(rel).parent.parent.as_posix())
    mode = node_mode_for_path(root, node_rel)
    if mode and mode != "execution":
        return [Finding(Path(rel), 1, "SOP.md", severity, "only execution nodes should carry SOP.md")]
    return []


def lite_review_findings(path: Path, root: Path, text: str, severity: str) -> list[Finding]:
    rel = as_posix_under(path, root)
    if not rel.endswith("/skills/local_entry.md") or "review/verdict.yaml" not in text:
        return []
    node_rel = str(Path(rel).parent.parent.as_posix())
    if node_mode_for_path(root, node_rel) == "lite":
        return [Finding(Path(rel), 1, "review/verdict.yaml", severity, "lite nodes should not hard-require review verdicts")]
    return []


def scan_file(
    path: Path,
    root: Path,
    rules: dict[str, Any],
    severity: str,
) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    banned = rules.get("banned") if isinstance(rules.get("banned"), dict) else {}
    fields = set(rules.get("local_entry_forbidden_fields") or [])
    findings = banned_term_findings(path, root, text, banned, severity)
    findings.extend(local_entry_field_findings(path, root, text, fields, severity))
    findings.extend(sop_findings(path, root, severity))
    findings.extend(lite_review_findings(path, root, text, severity))
    return findings


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    rules_path = (root / args.rules).resolve() if not Path(args.rules).is_absolute() else Path(args.rules).resolve()
    rules = load_yaml(rules_path)
    skip_patterns = [str(item) for item in (rules.get("default_skip") or [])]
    severity = "warning" if args.warn_only or not args.strict else "error"

    scan_inputs = list(args.paths or []) + list(args.extra_paths or [])
    files = iter_scan_files(root, scan_inputs, skip_patterns)
    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path, root, rules, severity))

    for item in findings:
        print(f"{item.path.as_posix()}:{item.line} | {item.term} | {item.severity} | {item.replacement}")

    if findings and args.strict and not args.warn_only:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
