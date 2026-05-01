#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

try:
    import yaml
except Exception:
    print("PyYAML is required. Install with: pip install PyYAML", file=sys.stderr)
    raise


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def main() -> int:
    ap = argparse.ArgumentParser(description="Evaluate one AutoResearch node using harness.yaml")
    ap.add_argument("--root", default=".", help="AutoResearch repo root")
    ap.add_argument("--node", required=True, help="Node path relative to root")
    ap.add_argument("--harness", default=None, help="Optional harness path")
    ap.add_argument("--write-status", action="store_true", help="Write backend/graph/node_eval_status.json")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from backend.evaluators.common import is_paper_task

    node_path = (root / args.node).resolve()
    harness_path = Path(args.harness).resolve() if args.harness else node_path / "harness.yaml"
    if not harness_path.exists():
        print(f"Missing harness: {harness_path}", file=sys.stderr)
        return 2

    harness = load_yaml(harness_path)
    registry_path = root / "backend" / "harness" / "verifier_registry.yaml"
    if not registry_path.exists():
        registry_path = Path(__file__).resolve().parents[1] / "backend" / "harness" / "verifier_registry.yaml"
    registry = load_yaml(registry_path).get("validators", {})

    # Basic required input check.
    input_errors = []
    for rel in ((harness.get("inputs") or {}).get("required_files") or []):
        if not (node_path / rel).exists():
            input_errors.append(f"missing required input: {rel}")

    results = []
    if input_errors:
        results.append({
            "id": "required_inputs",
            "passed": False,
            "score": 0.0,
            "summary": "缺少 required_files。",
            "details": input_errors,
        })

    for item in harness.get("validators", []):
        vid = item.get("id") if isinstance(item, dict) else str(item)
        if vid not in registry:
            results.append({
                "id": vid,
                "passed": False,
                "score": 0.0,
                "summary": "validator 未在 registry 中注册。",
                "details": [vid],
            })
            continue
        meta = registry[vid]
        try:
            mod = importlib.import_module(meta["module"])
            fn = getattr(mod, meta.get("function", "validate"))
            res = fn(root, node_path, harness)
        except Exception as e:
            res = {
                "id": vid,
                "passed": False,
                "score": 0.0,
                "summary": "validator 执行异常。",
                "details": [repr(e)],
            }
        results.append(res)

    threshold = float((harness.get("scorecard") or {}).get("pass_threshold", 0.80))
    required_failed = []
    validator_specs = { (v.get("id") if isinstance(v, dict) else str(v)): v for v in harness.get("validators", []) }
    for r in results:
        spec = validator_specs.get(r["id"], {})
        required = True if not isinstance(spec, dict) else bool(spec.get("required", True))
        if required and not r.get("passed", False):
            required_failed.append(r["id"])

    if is_paper_task(harness):
        for r in results:
            if r.get("id") in required_failed:
                r["score"] = 0.0
        score = 0.0 if required_failed else (sum(float(r.get("score", 0.0)) for r in results) / len(results) if results else 0.0)
    else:
        score = sum(float(r.get("score", 0.0)) for r in results) / len(results) if results else 0.0

    passed = score >= threshold and not required_failed
    blocking = required_failed[0] if required_failed else (None if passed else "score_below_threshold")
    report = {
        "node_path": args.node,
        "harness": str(harness_path),
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "score": round(score, 4),
        "pass_threshold": threshold,
        "passed": passed,
        "blocking_validator": blocking,
        "human_gate_required": bool((harness.get("human_gate") or {}).get("required_before_stage_change", True)),
        "results": results,
    }

    logs = node_path / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    (logs / "eval_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    # Markdown report for humans.
    md_lines = [
        f"# Eval Report: {args.node}",
        "",
        f"- score: `{report['score']}`",
        f"- pass_threshold: `{threshold}`",
        f"- passed: `{passed}`",
        f"- blocking_validator: `{blocking}`",
        f"- human_gate_required: `{report['human_gate_required']}`",
        "",
        "## Validators",
        "",
    ]
    for r in results:
        md_lines.append(f"### {r.get('id')}")
        md_lines.append(f"- passed: `{r.get('passed')}`")
        md_lines.append(f"- score: `{r.get('score')}`")
        md_lines.append(f"- summary: {r.get('summary')}")
        details = r.get("details") or []
        if details:
            md_lines.append("- details:")
            for d in details[:20]:
                md_lines.append(f"  - {d}")
        md_lines.append("")
    (logs / "eval_report.md").write_text("\n".join(md_lines), encoding="utf-8")

    if args.write_status:
        status_path = root / "backend" / "graph" / "node_eval_status.json"
        status_path.parent.mkdir(parents=True, exist_ok=True)
        if status_path.exists():
            try:
                status = json.loads(status_path.read_text(encoding="utf-8"))
            except Exception:
                status = {}
        else:
            status = {}
        status[args.node] = {
            "last_run_id": report["run_id"],
            "harness_passed": passed,
            "score": report["score"],
            "blocking_validator": blocking,
            "failure_reason": None if passed else next((r.get("summary") for r in results if r.get("id") == blocking), "score below threshold"),
            "next_action": "human_review" if passed and report["human_gate_required"] else ("revise_node" if not passed else "stage_update_allowed"),
            "human_gate_required": report["human_gate_required"],
            "updated_at": report["updated_at"],
        }
        status_path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
