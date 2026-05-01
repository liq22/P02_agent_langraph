#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def main() -> int:
    root = repo_root()
    validator = root / "scripts" / "validate_context_hygiene.py"
    if not validator.is_file():
        print(f"context hygiene acceptance: missing {validator}")
        return 1

    proc = subprocess.run(
        [sys.executable, str(validator), "--root", str(root)],
        cwd=str(root),
        text=True,
        capture_output=True,
        check=False,
    )
    print(proc.stdout.strip() or proc.stderr.strip())
    if proc.returncode != 0:
        print("context hygiene acceptance: fail")
        return proc.returncode

    print("context hygiene acceptance: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
