from __future__ import annotations
from pathlib import Path
import re
from .common import ValidationResult, find_primary_markdown, is_paper_task, read_text


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "markdown_structure"
    md = find_primary_markdown(node_path, harness)
    if not md:
        return ValidationResult(vid, False, 0.0, "未找到主要 Markdown 产物。", ["expected_outputs.primary 中没有可读 .md 文件。"] ).to_dict()

    text = read_text(md)
    strict = is_paper_task(harness)
    details = []
    score = 1.0

    if len(text.strip()) < 300:
        details.append("正文过短，低于 300 字符。")
        score -= 0.35
    if not re.search(r"^#{1,3}\s+", text, flags=re.MULTILINE):
        details.append("缺少 Markdown 标题结构。")
        score -= 0.25
    if re.search(r"TODO|待补|placeholder|占位", text, flags=re.IGNORECASE):
        details.append("存在 TODO / 待补 / placeholder。")
        score -= 0.20
    if text.count("\n") < 5:
        details.append("段落结构过少。")
        score -= 0.10
    if len(re.findall(r"^#{2,3}\s+", text, flags=re.MULTILINE)) < 2:
        details.append("二级/三级标题不足，建议拆分为问题、方法、证据、边界等小节。")
        score -= 0.10

    score = max(0.0, min(1.0, score))
    if strict and details:
        score = 0.0
        passed = False
    else:
        passed = score >= 0.75
    summary = "Markdown 结构可接受。" if passed else "Markdown 结构未达标。"
    return ValidationResult(vid, passed, score, summary, details).to_dict()
