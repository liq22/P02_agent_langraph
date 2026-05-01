from __future__ import annotations
from pathlib import Path
import re
from .common import ValidationResult, find_primary_markdown, is_paper_task, read_text


def extract_citekeys(text: str) -> list[str]:
    citekeys: list[str] = []
    for chunk in re.findall(r"\[([^\]]*@[^]]*)\]", text):
        citekeys.extend(re.findall(r"@([A-Za-z0-9_:\-]+)", chunk))
    return citekeys


def extract_bibtex_keys(refs_text: str) -> set[str]:
    return set(re.findall(r"@[A-Za-z]+\s*\{\s*([^,\s]+)", refs_text))


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "citation_integrity"
    md = find_primary_markdown(node_path, harness)
    if not md:
        return ValidationResult(vid, False, 0.0, "未找到主要 Markdown 文件。", []).to_dict()
    text = read_text(md)
    strict = is_paper_task(harness)
    citekeys = extract_citekeys(text)
    numeric = re.findall(r"\[[0-9,\-\s]+\]", text)
    links = re.findall(r"https?://[^\s)]+", text)
    refs_files = [root / "references.bib", root / "refs.bib", node_path / "references.bib", node_path / "refs.bib"]
    refs_text = "\n".join(read_text(p) for p in refs_files if p.exists())
    bibtex_keys = extract_bibtex_keys(refs_text)
    details = []

    if citekeys and refs_text:
        missing = [key for key in citekeys if key not in bibtex_keys]
        if missing:
            details.extend([f"BibTeX 中未找到 citekey：{k}" for k in missing[:20]])
            if strict:
                return ValidationResult(vid, False, 0.0, "存在未解析引用。", details).to_dict()
            score = max(0.0, 1 - len(missing) / max(1, len(citekeys)))
            return ValidationResult(vid, score >= 0.85, score, "存在未解析引用。", details).to_dict()
        return ValidationResult(vid, True, 1.0, f"检测到 {len(citekeys)} 个 citekey，BibTeX 匹配通过。", details).to_dict()

    if citekeys and not refs_text:
        details.append("存在 citekey，但未找到 references.bib / refs.bib。")
        score = 0.0 if strict else 0.55
        return ValidationResult(vid, False, score, "引用格式存在，但缺少 BibTeX 索引。", details).to_dict()

    if strict:
        if numeric or links:
            details.append("论文相关节点必须使用可解析 BibTeX citekey；数字引用或裸链接不合格。")
        else:
            details.append("论文相关节点未检测到 BibTeX citekey。")
        return ValidationResult(vid, False, 0.0, "缺少可解析 BibTeX citekey。", details).to_dict()

    if numeric or links:
        return ValidationResult(vid, True, 0.80, f"检测到数字引用 {len(numeric)} 个、链接 {len(links)} 个。", details).to_dict()

    details.append("未检测到引用。对论文/申请书节点通常不可接受。")
    return ValidationResult(vid, False, 0.30, "未检测到引用。", details).to_dict()
