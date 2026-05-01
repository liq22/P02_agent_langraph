#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


def main() -> int:
    ap = argparse.ArgumentParser(description="Run minimal NodeBench cases.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--cases", default="tests/nodebench/cases")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    cases_dir = root / args.cases
    reports_dir = root / "tests" / "nodebench" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if not cases_dir.exists():
        print(f"No cases directory: {cases_dir}")
        return 2

    tmp = root / ".nodebench_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    try:
        for case in sorted([p for p in cases_dir.iterdir() if p.is_dir()]):
            input_snapshot = case / "input" / "node_snapshot"
            if not input_snapshot.exists():
                continue
            expected_path = case / "expected.json"
            if expected_path.exists():
                expected = json.loads(expected_path.read_text(encoding="utf-8"))
            else:
                expected = {"passed": True}
            node_path = tmp / case.name
            shutil.copytree(input_snapshot, node_path)
            if (case / "harness.yaml").exists():
                shutil.copy2(case / "harness.yaml", node_path / "harness.yaml")
            rel_node = node_path.relative_to(root).as_posix()
            cmd = [sys.executable, str(root / "scripts" / "evaluate_node.py"), "--root", str(root), "--node", rel_node]
            proc = subprocess.run(cmd, cwd=str(root), text=True, capture_output=True)
            try:
                payload = json.loads(proc.stdout)
            except Exception:
                payload = {"passed": False, "score": 0.0, "stdout": proc.stdout, "stderr": proc.stderr}
            expected_passed = bool(expected.get("passed", True))
            expected_blocker = expected.get("blocking_validator")
            matched = payload.get("passed") is expected_passed
            if expected_blocker is not None:
                matched = matched and payload.get("blocking_validator") == expected_blocker
            results.append({
                "case": case.name,
                "returncode": proc.returncode,
                "passed": payload.get("passed"),
                "score": payload.get("score"),
                "blocking_validator": payload.get("blocking_validator"),
                "expected_passed": expected_passed,
                "expected_blocking_validator": expected_blocker,
                "matched": matched,
            })
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    summary = {
        "run_id": datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "case_count": len(results),
        "passed_count": sum(1 for r in results if r.get("passed")),
        "matched_count": sum(1 for r in results if r.get("matched")),
        "results": results,
    }
    (reports_dir / "latest_nodebench_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    md = ["# Latest NodeBench Report", "", f"- cases: `{summary['case_count']}`", f"- passed: `{summary['passed_count']}`", f"- matched: `{summary['matched_count']}`", "", "| case | matched | passed | expected | score | blocker | expected blocker |", "|---|---:|---:|---:|---:|---|---|"]
    for r in results:
        md.append(f"| {r['case']} | {r.get('matched')} | {r.get('passed')} | {r.get('expected_passed')} | {r.get('score')} | {r.get('blocking_validator')} | {r.get('expected_blocking_validator')} |")
    (reports_dir / "latest_nodebench_report.md").write_text("\n".join(md), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["matched_count"] == summary["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
