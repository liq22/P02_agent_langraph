#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


RUBRIC_NAME = "NATURE_LEVEL_NODE_RUBRIC.md"
REQUIRED_SOURCE_URLS = (
    "https://www.nature.com/nature/for-authors/editorial-criteria-and-processes",
    "https://www.nature.com/nature-portfolio/about/communications-journals-guide-to-reviewers",
    "https://www.nature.com/ncomms/editorial-policies/reporting-standards",
    "https://www.nature.com/nature-portfolio/for-authors/publish",
)
REQUIRED_MARKERS = (
    "## Scoring Model",
    "## Hard Fail",
    "## Node Rubric",
    "Originality / Novelty",
    "Evidence / Technical Soundness",
    "Reproducibility / Transparency",
)
NODE_ROW_RE = re.compile(r"^\| `(?P<path>research/[^`]+)` \|", re.MULTILINE)
NODE_ROW_WITH_TEXT_RE = re.compile(
    r"^\| `(?P<path>research/[^`]+)` \| (?P<criterion>.+?) \| (?P<blocking>.+?) \|$",
    re.MULTILINE,
)


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    rubric = root / "test" / RUBRIC_NAME
    if not rubric.exists():
        print(f"nature rubric presence: fail\n- missing: test/{RUBRIC_NAME}")
        return 1

    text = rubric.read_text(encoding="utf-8")
    status_nodes = {
        path.parent.relative_to(root).as_posix()
        for path in (root / "research").glob("**/status.yaml")
    }
    rubric_rows = {match.group("path"): match.groupdict() for match in NODE_ROW_WITH_TEXT_RE.finditer(text)}
    rubric_nodes = set(NODE_ROW_RE.findall(text))

    missing_nodes = sorted(status_nodes - rubric_nodes)
    stale_nodes = sorted(rubric_nodes - status_nodes)
    missing_sources = [url for url in REQUIRED_SOURCE_URLS if url not in text]
    missing_markers = [marker for marker in REQUIRED_MARKERS if marker not in text]

    failures: list[str] = []
    failures.extend(f"missing node rubric: {node}" for node in missing_nodes)
    failures.extend(f"stale node rubric: {node}" for node in stale_nodes)
    failures.extend(f"missing source URL: {url}" for url in missing_sources)
    failures.extend(f"missing rubric marker: {marker}" for marker in missing_markers)
    for node in sorted(status_nodes):
        review_rubric = root / node / "prompts" / "review_rubric.yaml"
        if not review_rubric.is_file():
            failures.append(f"missing per-node review rubric: {node}/prompts/review_rubric.yaml")
            continue
        payload = yaml.safe_load(review_rubric.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            failures.append(f"invalid YAML review rubric: {node}/prompts/review_rubric.yaml")
            continue
        row = rubric_rows.get(node)
        if payload.get("node_path") != node:
            failures.append(f"node_path mismatch in {node}/prompts/review_rubric.yaml")
        if payload.get("reviewer_role") != "external_node_reviewer":
            failures.append(f"reviewer_role mismatch in {node}/prompts/review_rubric.yaml")
        independence = payload.get("independence_requirement") if isinstance(payload.get("independence_requirement"), dict) else {}
        if independence.get("reviewer_agent_must_be_distinct") is not True:
            failures.append(f"distinct reviewer requirement missing in {node}/prompts/review_rubric.yaml")
        if independence.get("same_author_agent_forbidden") is not True:
            failures.append(f"same-author reviewer ban missing in {node}/prompts/review_rubric.yaml")
        if not payload.get("node_level_5_criterion"):
            failures.append(f"missing node_level_5_criterion in {node}/prompts/review_rubric.yaml")
        if not payload.get("node_blocking_failure"):
            failures.append(f"missing node_blocking_failure in {node}/prompts/review_rubric.yaml")
        if row:
            if payload.get("node_level_5_criterion") != row.get("criterion"):
                failures.append(f"criterion mismatch between markdown rubric and per-node rubric for {node}")
            if payload.get("node_blocking_failure") != row.get("blocking"):
                failures.append(f"blocking failure mismatch between markdown rubric and per-node rubric for {node}")

    if failures:
        print("nature rubric presence: fail")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"nature rubric presence: pass nodes={len(status_nodes)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
