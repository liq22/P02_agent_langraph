from __future__ import annotations
from pathlib import Path
import subprocess
from .common import ValidationResult, glob_allowed


def git_changes(root: Path) -> list[tuple[str, str]]:
    try:
        out = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
    except Exception:
        return []
    changes = []
    for line in out.splitlines():
        if len(line) > 3:
            changes.append((line[:2], line[3:].strip()))
    return changes


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "edit_scope_check"
    modified = git_changes(root)
    if not modified:
        return ValidationResult(vid, True, 1.0, "未检测到 git 修改，或当前目录不是 git 仓库。", []).to_dict()

    node_rel = node_path.relative_to(root).as_posix() if node_path.is_absolute() else node_path.as_posix()
    if node_rel.startswith(".nodebench_tmp/") and not harness.get("nodebench_enforce_edit_scope"):
        return ValidationResult(vid, True, 1.0, "NodeBench 临时快照跳过 git 修改范围检查。", []).to_dict()

    can = [f"{node_rel}/{p}" for p in (harness.get("allowed_actions") or {}).get("can_modify", [])]
    cannot = [f"{node_rel}/{p}" for p in (harness.get("allowed_actions") or {}).get("cannot_modify", [])]
    setup_files = {f"{node_rel}/harness.yaml"}
    details = []
    violations = []
    for _status, f in modified:
        if f in setup_files:
            continue
        if glob_allowed(cannot, f):
            violations.append(f)
            details.append(f"修改了禁止文件：{f}")
        elif f.startswith(node_rel + "/") and can and not glob_allowed(can, f):
            violations.append(f)
            details.append(f"节点内修改超出 can_modify：{f}")

    if violations:
        return ValidationResult(vid, False, 0.0, "存在越权修改。", details).to_dict()
    return ValidationResult(vid, True, 1.0, "修改范围符合 harness。", details).to_dict()
