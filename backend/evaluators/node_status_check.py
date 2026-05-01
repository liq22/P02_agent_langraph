from __future__ import annotations
from pathlib import Path
from .common import ValidationResult, is_paper_task, load_yaml

VALID_STATUSES = {"seed", "active", "review", "fix", "done", "archive"}
TERMINAL_STATUSES = {"done", "archive"}


def human_gate_passed(data: dict) -> bool:
    review_gate = data.get("review_gate") if isinstance(data.get("review_gate"), dict) else {}
    if review_gate.get("human_gate_passed") is True:
        return True
    if str(review_gate.get("human_gate_state") or "").strip().lower() in {"passed", "pass", "通过"}:
        return True
    try:
        return int(review_gate.get("human_review_count") or 0) > 0
    except (TypeError, ValueError):
        return False


def validate(root: Path, node_path: Path, harness: dict) -> dict:
    vid = "node_status_check"
    status = node_path / "status.yaml"
    if not status.exists():
        return ValidationResult(vid, False, 0.40, "缺少 status.yaml。", [str(status)]).to_dict()
    data = load_yaml(status)
    strict = is_paper_task(harness)
    lifecycle = data.get("lifecycle") if isinstance(data.get("lifecycle"), dict) else {}
    stage = data.get("status") or lifecycle.get("stage")
    details = []
    score = 1.0

    if not stage:
        details.append("status.yaml 缺少 status 或 lifecycle.stage。")
        score -= 0.35
    elif stage not in VALID_STATUSES:
        details.append(f"status.yaml 状态不在仓库契约内：{stage}")
        score -= 0.35

    if stage in TERMINAL_STATUSES and (harness.get("human_gate") or {}).get("required_before_stage_change", True):
        if human_gate_passed(data):
            details.append("节点已进入终态；检测到 human gate 记录。")
        else:
            details.append("节点已进入终态；缺少 human gate 通过记录。")
            score -= 0.20

    if "last_actor" not in data:
        details.append("status.yaml 缺少 last_actor，操作审计信息不完整。")
        score -= 0.10

    score = max(0.0, score)
    passed = score >= 0.70
    if strict and any("缺少" in item or "不在仓库契约内" in item for item in details):
        score = 0.0
        passed = False
    return ValidationResult(vid, passed, score, f"status.yaml 检查完成，当前状态：{stage or 'missing'}。", details).to_dict()
