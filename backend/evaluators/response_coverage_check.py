from __future__ import annotations
from pathlib import Path
import re
from .common import ValidationResult, read_text, find_primary_markdown


STRICT_RESPONSE_TASKS = {"response_node", "review_node"}


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "response_coverage_check"
    candidates = [
        node_path / "docs" / "response_matrix.md",
        node_path / "docs" / "review_response.md",
        node_path / "docs" / "manuscript.md",
    ]
    md = next((p for p in candidates if p.exists()), None) or find_primary_markdown(node_path, harness)
    if not md:
        return ValidationResult(vid, False, 0.0, "未找到回复矩阵或回复文档。", []).to_dict()
    text = read_text(md)
    comments = re.findall(r"Reviewer\s*#?\d+|审稿人\s*\d+|Comment\s*\d+|意见\s*\d+", text, flags=re.IGNORECASE)
    responses = re.findall(r"Response|回复|答复", text, flags=re.IGNORECASE)
    changes = re.findall(r"修改|修订|changed|revised|Section|章节|位置|location", text, flags=re.IGNORECASE)
    evidence = re.findall(r"证据|实验|表\s*\d+|图\s*\d+|Table\s*\d+|Figure\s*\d+|Appendix|附录", text, flags=re.IGNORECASE)

    details = []
    checks = [
        (comments, "缺少 reviewer/comment 标识。"),
        (responses, "缺少 response/回复 段落。"),
        (changes, "缺少稿件修改位置或修改动作。"),
        (evidence, "缺少证据、图表、实验或附录引用。"),
    ]
    hit = 0
    for arr, msg in checks:
        if arr:
            hit += 1
        else:
            details.append(msg)
    score = hit / len(checks)
    strict = str(harness.get("task_type") or "") in STRICT_RESPONSE_TASKS
    passed = hit == len(checks) if strict else score >= 0.75
    if strict and not passed:
        score = 0.0
    return ValidationResult(vid, passed, score, f"回复覆盖检查命中 {hit}/{len(checks)} 类要素。", details).to_dict()
