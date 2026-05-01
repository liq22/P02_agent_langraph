#!/usr/bin/env python3
"""Summarize optimizer validation results and expose structured payloads to downstream planners."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
RESULTS_BASE_DIR = REPO_ROOT / "_reference" / "test" / "v2" / "results"

SECTION_TITLES = [
    "Validation Target",
    "Why This Target Is High Risk Now",
    "Ground Truth Sources Used",
    "Assumptions / UNVERIFIED",
    "Validation Setup",
    "Execution / Inspection Steps",
    "Evidence Collected",
    "Adversarial Findings",
    "Verdict",
    "Handoff Readiness",
    "Residual Risks",
    "Next Node / Next Smallest Action",
]
SECTION_RE = re.compile(
    r"(?mi)^#+\s*(?:\d+\.\s*)?(" + "|".join(re.escape(title) for title in SECTION_TITLES) + r")(?:\s*[:：].*)?$"
)
VERDICT_RE = re.compile(r"\b(WORKS|PARTIAL|DOES_NOT_WORK)\b")
PATH_RE = re.compile(r"(\.agent/[\w./-]+|_reference/[\w./-]+|backend/[\w./-]+|research/[\w./\u4e00-\u9fff-]+|test/[\w./-]+)")
PAYLOAD_RE = re.compile(
    r"(?ms)^#{1,6}\s*Structured Evaluation Payload\s*$\s*```(?:yaml|yml)\s*(.*?)\s*```"
)


def extract_verdict(content: str) -> str:
    match = VERDICT_RE.search(content)
    return match.group(1).upper() if match else "UNKNOWN"


def split_sections(content: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(content))
    sections: dict[str, str] = {}
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        sections[match.group(1)] = content[start:end].strip()
    return sections


def first_meaningful_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip().lstrip("-*0123456789. ").strip()
        if line:
            return line
    return "UNKNOWN"


def extract_target_node(content: str) -> str:
    sections = split_sections(content)
    target = first_meaningful_line(sections.get("Validation Target", ""))
    if target != "UNKNOWN":
        return target
    match = PATH_RE.search(content)
    return match.group(1) if match else "UNKNOWN"


def extract_findings(content: str) -> list[str]:
    sections = split_sections(content)
    source = sections.get("Adversarial Findings", "")
    findings: list[str] = []
    for raw_line in source.splitlines():
        line = raw_line.strip().lstrip("-*0123456789. ").strip()
        if len(line) >= 12:
            findings.append(line[:240])
    return findings


def extract_structured_payload(content: str) -> dict[str, Any]:
    match = PAYLOAD_RE.search(content)
    if not match:
        return {}
    try:
        payload = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return payload if isinstance(payload, dict) else {}


def normalize_list_of_dicts(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in value:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def parse_agent_result(result_dir: Path) -> dict[str, Any] | None:
    metadata_file = result_dir / "metadata.json"
    result_file = result_dir / "result.md"
    if not result_file.exists():
        return None

    metadata: dict[str, Any] = {}
    if metadata_file.exists():
        try:
            payload = json.loads(metadata_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                metadata = payload
        except Exception:
            metadata = {}

    try:
        content = result_file.read_text(encoding="utf-8")
    except Exception:
        return None

    structured_payload = extract_structured_payload(content)
    maintenance_findings = normalize_list_of_dicts(structured_payload.get("maintenance_findings"))
    research_findings = normalize_list_of_dicts(structured_payload.get("research_findings"))
    score_inputs = normalize_list_of_dicts(structured_payload.get("score_inputs"))
    findings = extract_findings(content)
    if not findings:
        findings = [
            str(item.get("summary") or item.get("claim_or_surface") or item.get("finding_id") or "")
            for item in maintenance_findings + research_findings
            if str(item.get("summary") or item.get("claim_or_surface") or item.get("finding_id") or "").strip()
        ]

    result = {
        "agent_name": result_dir.name,
        "metadata": metadata,
        "verdict": extract_verdict(content),
        "target_node": structured_payload.get("target_path") or extract_target_node(content),
        "findings": findings,
        "maintenance_findings": maintenance_findings,
        "research_findings": research_findings,
        "score_inputs": score_inputs,
        "structured_payload": structured_payload,
        "boundary_class": str(structured_payload.get("boundary_class") or "maintenance_only"),
        "exploratory": bool(structured_payload.get("exploratory", False)),
        "phase": structured_payload.get("phase"),
        "node_mode": structured_payload.get("node_mode"),
        "node_profile": structured_payload.get("node_profile"),
        "execution_profile": structured_payload.get("execution_profile"),
        "content_length": len(content),
    }
    return result


def collect_all_results(results_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    results_dir = Path(results_dir)
    all_results: list[dict[str, Any]] = []
    batch_summaries: list[dict[str, Any]] = []
    candidate_dirs: list[Path] = []

    for summary_file in results_dir.glob("batch_summary_*.json"):
        try:
            payload = json.loads(summary_file.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                batch_summaries.append(payload)
        except Exception:
            continue

    manifest_path = results_dir / "validation_manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(manifest, dict):
                for item in manifest.get("results", []):
                    if isinstance(item, dict):
                        result_dir = item.get("result_dir")
                        if isinstance(result_dir, str) and result_dir:
                            candidate_dirs.append(Path(result_dir))
        except Exception:
            pass

    if not candidate_dirs:
        for item in sorted(results_dir.iterdir()):
            if item.is_dir() and item.name.endswith("_agent"):
                candidate_dirs.append(item)

    seen: set[str] = set()
    for item in candidate_dirs:
        key = str(item.resolve()) if item.exists() else str(item)
        if key in seen or not item.is_dir():
            continue
        seen.add(key)
        parsed = parse_agent_result(item)
        if parsed:
            all_results.append(parsed)
    return all_results, batch_summaries


def generate_cross_validation_report(all_results: list[dict[str, Any]]) -> str:
    if not all_results:
        return "# 验证报告\n\n未找到任何验证结果。\n"

    verdict_counter = Counter(result["verdict"] for result in all_results)
    boundary_counter = Counter(result.get("boundary_class", "maintenance_only") for result in all_results)
    target_counter = Counter(result["target_node"] for result in all_results)
    exploratory_count = sum(1 for result in all_results if result.get("exploratory"))
    keyword_counter: defaultdict[str, int] = defaultdict(int)
    for result in all_results:
        for finding in result.get("findings", []):
            for word in re.findall(r"[\u4e00-\u9fff]+|[a-zA-Z]{3,}", finding):
                if len(word) >= 2:
                    keyword_counter[word] += 1

    report: list[str] = ["# 批量节点验证报告", "", f"生成时间: {datetime.now().isoformat()}", "", "## 概览"]
    report.append(f"- Agent 数量: {len(all_results)}")
    report.append(f"- Exploratory 节点: {exploratory_count}")
    report.append("")
    report.append("## Verdict 分布")
    for verdict, count in verdict_counter.most_common():
        report.append(f"- {verdict}: {count}")
    report.append("")
    report.append("## Boundary Class 分布")
    for boundary_class, count in boundary_counter.most_common():
        report.append(f"- {boundary_class}: {count}")
    report.append("")
    report.append("## 目标节点分布")
    for node, count in target_counter.most_common(10):
        report.append(f"- {node}: {count}")
    report.append("")
    report.append("## 各 Agent 结果摘要")
    for result in all_results:
        report.append(f"### {result['agent_name']}")
        report.append(f"- Verdict: {result['verdict']}")
        report.append(f"- Target: {result['target_node']}")
        report.append(f"- Boundary Class: {result.get('boundary_class', 'maintenance_only')}")
        report.append(f"- Exploratory: {result.get('exploratory', False)}")
        report.append(f"- Score Inputs: {len(result.get('score_inputs', []))}")
        report.append(f"- Maintenance Findings: {len(result.get('maintenance_findings', []))}")
        report.append(f"- Research Findings: {len(result.get('research_findings', []))}")
        if result.get("findings"):
            report.append("- 关键发现:")
            for finding in result["findings"][:5]:
                report.append(f"  - {finding}")
        report.append("")
    report.append("## 高频关键词")
    for word, count in sorted(keyword_counter.items(), key=lambda item: item[1], reverse=True)[:20]:
        report.append(f"- {word}: {count}")
    report.append("")
    return "\n".join(report) + "\n"


def save_summary_report(results_dir: Path, report: str) -> Path:
    results_dir = Path(results_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = results_dir / f"validation_report_{timestamp}.md"
    report_file.write_text(report, encoding="utf-8")
    latest = results_dir / "validation_report_latest.md"
    latest.write_text(report, encoding="utf-8")
    return report_file


def main() -> int:
    parser = argparse.ArgumentParser(description="汇总多个 Agent 的验证结果")
    parser.add_argument("-r", "--results-dir", type=Path, default=RESULTS_BASE_DIR)
    parser.add_argument("-o", "--output", type=Path, default=None)
    parser.add_argument("--stats-only", action="store_true")
    parser.add_argument("--stdout", action="store_true")
    args = parser.parse_args()

    if not args.results_dir.exists():
        print(f"错误: 结果目录不存在: {args.results_dir}")
        return 1

    all_results, _batch_summaries = collect_all_results(args.results_dir)
    if not all_results:
        print(f"警告: 未找到任何验证结果: {args.results_dir}")
        return 1

    report = generate_cross_validation_report(all_results)
    if args.stats_only:
        report = report.split("## 各 Agent 结果摘要", 1)[0].rstrip() + "\n"

    if args.stdout:
        print(report)
        return 0

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(report, encoding="utf-8")
        print(f"报告已保存: {args.output}")
    else:
        report_file = save_summary_report(args.results_dir, report)
        print(f"报告已保存: {report_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
