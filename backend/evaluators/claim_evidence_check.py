from __future__ import annotations
from pathlib import Path
import re
from .common import ValidationResult, find_primary_markdown, has_citation_or_evidence, is_paper_task, read_text, sentence_split

STRONG_PATTERNS = [
    r"首次|第一|唯一|根本|本质|必然|显著|大幅|超过|优于|最优|SOTA|state[- ]of[- ]the[- ]art",
    r"证明|表明|显示|可以得出|因此|因而|结论是|核心贡献|关键创新",
    r"outperform|improve|reduce|increase|demonstrate|prove|show|significant|novel|contribution",
]


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "claim_evidence_check"
    md = find_primary_markdown(node_path, harness)
    if not md:
        return ValidationResult(vid, False, 0.0, "未找到可检查的正文。", []).to_dict()
    text = read_text(md)
    strict = is_paper_task(harness)
    sentences = sentence_split(text)
    strong = []
    missing = []
    for s in sentences:
        if any(re.search(p, s, flags=re.IGNORECASE) for p in STRONG_PATTERNS):
            strong.append(s)
            if not has_citation_or_evidence(s):
                missing.append(s[:180])

    details = []
    if not strong:
        details.append("未识别到强主张；可能是文本过弱，也可能是启发式未命中。")
        score = 0.0 if strict else 0.65
        passed = False
    else:
        ratio = 1 - len(missing) / len(strong)
        if missing:
            details.extend([f"强主张缺少证据/引用：{m}" for m in missing[:10]])
        if strict and missing:
            score = 0.0
            passed = False
        else:
            score = max(0.0, min(1.0, ratio))
            passed = score >= 0.75

    if (node_path / "logs" / "claim_evidence_map.md").exists() or (node_path / "docs" / "claim_evidence_map.md").exists():
        if passed and not strict:
            score = min(1.0, score + 0.10)
        details.append("检测到 claim_evidence_map，作为审计信息记录。")

    summary = f"识别强主张 {len(strong)} 条，缺证据 {len(missing)} 条。"
    return ValidationResult(vid, passed, score, summary, details).to_dict()
