#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a bounded node harness round. This wrapper does not call an LLM; it audits and evaluates the node.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--node", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    node = root / args.node
    logs = node / "logs"
    logs.mkdir(parents=True, exist_ok=True)

    run_report = logs / "run_report.md"
    run_report.write_text(f"""# Node Harness Run Report\n\n- node: `{args.node}`\n- time: `{datetime.now(timezone.utc).isoformat()}`\n- dry_run: `{args.dry_run}`\n\n## Scope\n\n本脚本只执行 harness 审计与 verifier 评测，不调用外部 LLM。\n\n## Next\n\n1. 若 dry_run 为 true：人工或 agent 根据 prompts/research_prompt.md 修改允许文件。\n2. 修改后运行 scripts/evaluate_node.py。\n3. 通过后进入 human gate。\n""", encoding="utf-8")

    cmd = [sys.executable, str(root / "scripts" / "evaluate_node.py"), "--root", str(root), "--node", args.node, "--write-status"]
    proc = subprocess.run(cmd, cwd=str(root))
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
