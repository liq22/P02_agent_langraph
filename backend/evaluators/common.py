from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List
import json
import re
import subprocess
import sys

try:
    import yaml
except Exception:  # pragma: no cover
    yaml = None


@dataclass
class ValidationResult:
    id: str
    passed: bool
    score: float
    summary: str
    details: List[str]

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["score"] = max(0.0, min(1.0, float(d["score"])))
        return d


PAPER_TASK_TYPES = {"proposal_node", "manuscript_node", "response_node"}


def is_paper_task(harness: Dict[str, Any]) -> bool:
    return str(harness.get("task_type") or "") in PAPER_TASK_TYPES


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    if yaml is None:
        raise RuntimeError("PyYAML is required. Install with: pip install PyYAML")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data or {}


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def find_primary_markdown(node_path: Path, harness: Dict[str, Any]) -> Path | None:
    primary = (harness.get("expected_outputs") or {}).get("primary") or []
    for rel in primary:
        p = node_path / rel
        if p.suffix.lower() in {".md", ".markdown"}:
            return p
    candidates = [
        node_path / "docs" / "manuscript.md",
        node_path / "README.md",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def sentence_split(text: str) -> List[str]:
    parts = re.split(r"(?<=[。！？.!?])\s+|\n+", text)
    return [p.strip() for p in parts if p.strip()]


def has_citation_or_evidence(sentence: str) -> bool:
    patterns = [
        r"\[@[A-Za-z0-9_:\-]+\]",          # pandoc citekey
        r"\[[0-9,\-\s]+\]",                # numeric citation
        r"\([A-Z][A-Za-z\-]+\s*,?\s*20\d{2}\)",  # Author, 2024
        r"https?://",                       # link
        r"见表|见图|如表|如图|实验|消融|附录|数据|结果|benchmark|Bench|Table|Figure|Appendix|ablation|experiment",
    ]
    return any(re.search(p, sentence, flags=re.IGNORECASE) for p in patterns)


def safe_git_status(root: Path) -> List[str]:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
    except Exception:
        return []
    files = []
    for line in out.splitlines():
        if len(line) > 3:
            files.append(line[3:].strip())
    return files


def glob_allowed(patterns: List[str], rel_path: str) -> bool:
    from fnmatch import fnmatch
    normalized = rel_path.replace("\\", "/")
    return any(fnmatch(normalized, p.replace("\\", "/")) for p in patterns)
