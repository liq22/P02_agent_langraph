from __future__ import annotations
from pathlib import Path
import re
from .common import ValidationResult, read_text, load_yaml, find_primary_markdown, is_paper_task

COMPLETE_STATUSES = {"done", "complete", "completed", "pass", "passed", "ok", "true", "yes", "closed", "resolved", "完成", "通过"}
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".tex", ".tsv", ".csv"}
CONTRACT_SECTIONS = (
    "required_questions_answered",
    "required_outputs",
    "quality_checks",
    "handoff_ready_if",
    "author_exit",
)
HUMAN_GATE_MARKERS = (
    "review/verdict.yaml",
    "reviewer",
    "review_complete",
    "overall_verdict",
    "hard_fail",
    "independence_confirmed",
    "独立 reviewer",
    "人类",
)


def status_is_complete(value: object) -> bool:
    return str(value or "").strip().lower() in COMPLETE_STATUSES


def path_exists(node_path: Path, raw_path: object) -> bool:
    raw = str(raw_path or "").strip()
    if not raw:
        return False
    if "/" not in raw and "\\" not in raw and "." not in Path(raw).name:
        return False
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate.exists()
    return (node_path / candidate).exists()


def author_output_text(node_path: Path, harness: dict) -> str:
    paths: list[Path] = []
    primary = find_primary_markdown(node_path, harness)
    if primary:
        paths.append(primary)
    for directory in [node_path / "docs", node_path / "artifacts"]:
        if directory.is_dir():
            paths.extend(path for path in sorted(directory.rglob("*")) if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES)
    for rel in ["logs/claim_evidence_map.md", "logs/run_report.md"]:
        path = node_path / rel
        if path.is_file():
            paths.append(path)
    seen: set[Path] = set()
    chunks: list[str] = []
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        chunks.append(read_text(path))
    return "\n".join(chunks)


def concept_terms(text: str) -> list[str]:
    terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]*|[\u4e00-\u9fff]{2,}", text)
    ignored = {"true", "false", "yaml", "md", "item", "path", "status", "profile", "required", "local", "artifact"}
    return [term for term in terms if term.lower() not in ignored]


def concept_covered(name: str, output_text: str) -> bool:
    terms = concept_terms(name)
    if not terms:
        return False
    hits = sum(1 for term in terms if term in output_text)
    required = 1 if len(terms) <= 2 else max(2, min(4, len(terms) // 2))
    return hits >= required


def is_human_gate_item(name: str) -> bool:
    return any(marker in name for marker in HUMAN_GATE_MARKERS)


def validate_keyword_items(node_path: Path, harness: dict, items: list[object]) -> dict:
    vid = "acceptance_checklist"
    text = author_output_text(node_path, harness)
    strict = is_paper_task(harness)
    passed_items = 0
    details = []

    for item in items:
        if isinstance(item, dict):
            name = item.get("id") or item.get("name") or item.get("text") or "unnamed"
            keywords = item.get("keywords") or []
        else:
            name = str(item)
            keywords = []
        if keywords:
            hit = any(str(k) in text for k in keywords)
        else:
            tokens = [t for t in re.split(r"\s+|，|。|、|:|：", name) if len(t) >= 2]
            hit = any(t in text for t in tokens[:5])
        if hit:
            passed_items += 1
        else:
            details.append(f"未覆盖验收项：{name}")

    score = passed_items / max(1, len(items))
    passed = passed_items == len(items) if strict else score >= 0.80
    if strict and not passed:
        score = 0.0
    return ValidationResult(vid, passed, score, f"验收项覆盖率 {passed_items}/{len(items)}。", details).to_dict()


def validate_repo_contract(node_path: Path, harness: dict, data: dict) -> dict:
    vid = "acceptance_checklist"
    output_text = author_output_text(node_path, harness)
    strict = is_paper_task(harness)
    total = 0
    complete = 0
    details = []

    for section in CONTRACT_SECTIONS:
        values = data.get(section) or []
        if not isinstance(values, list):
            continue
        for item in values:
            if not isinstance(item, dict):
                continue
            name = item.get("item") or item.get("path") or item.get("id") or "unnamed"
            name_text = str(name)
            if is_human_gate_item(name_text):
                continue
            total += 1
            if status_is_complete(item.get("status")) or path_exists(node_path, item.get("path")) or concept_covered(name_text, output_text):
                complete += 1
            else:
                details.append(f"{section} 未完成：{name}")

    if total == 0:
        score = 0.0 if strict else 0.20
        return ValidationResult(vid, False, score, "验收清单未包含可识别的验收项。", ["需要 items/checklist 或仓库本地 checklist sections。"]).to_dict()
    score = complete / total
    passed = complete == total if strict else score >= 0.80
    if strict and not passed:
        score = 0.0
    return ValidationResult(vid, passed, score, f"验收契约完成率 {complete}/{total}。", details).to_dict()


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "acceptance_checklist"
    checklist_path = node_path / "prompts" / "acceptance_checklist.yaml"
    if not checklist_path.exists():
        return ValidationResult(vid, False, 0.0, "缺少 acceptance_checklist.yaml。", [str(checklist_path)]).to_dict()

    data = load_yaml(checklist_path)
    items = data.get("items") or data.get("checklist") or []
    if not items:
        return validate_repo_contract(node_path, harness, data)
    return validate_keyword_items(node_path, harness, items)
