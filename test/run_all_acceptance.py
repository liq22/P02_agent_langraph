#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def run(script: Path) -> subprocess.CompletedProcess[str]:
    root = repo_root()
    return subprocess.run([sys.executable, str(script)], cwd=str(root), text=True, capture_output=True)


def main() -> int:
    root = repo_root()
    fixture_script = root / "test" / "run_fixture_acceptance.py"
    context_script = root / "test" / "run_context_hygiene_acceptance.py"
    gateway_script = root / "test" / "run_gateway_acceptance.py"
    nature_script = root / "test" / "run_nature_rubric_presence.py"
    capability_script = root / "test" / "run_nature_capability_acceptance.py"
    live_script = root / "test" / "run_live_repo_smoke.py"

    for label, script in [
        ("fixture", fixture_script),
        ("context_hygiene", context_script),
        ("gateway", gateway_script),
        ("nature", nature_script),
        ("capability", capability_script),
        ("live", live_script),
    ]:
        if not script.exists():
            print(f"{label}: missing {script}")
            return 1

    fixture = run(fixture_script)
    print("== fixture acceptance ==")
    print(fixture.stdout.strip() or fixture.stderr.strip())

    context_hygiene = run(context_script)
    print("\n== context hygiene acceptance ==")
    print(context_hygiene.stdout.strip() or context_hygiene.stderr.strip())

    gateway = run(gateway_script)
    print("\n== gateway acceptance ==")
    print(gateway.stdout.strip() or gateway.stderr.strip())

    nature = run(nature_script)
    print("\n== nature rubric presence ==")
    print(nature.stdout.strip() or nature.stderr.strip())

    capability = run(capability_script)
    print("\n== nature capability acceptance ==")
    print(capability.stdout.strip() or capability.stderr.strip())

    live = run(live_script)
    print("\n== live repo smoke ==")
    print(live.stdout.strip() or live.stderr.strip())

    if (
        fixture.returncode == 0
        and context_hygiene.returncode == 0
        and gateway.returncode == 0
        and nature.returncode == 0
        and capability.returncode == 0
        and live.returncode == 0
    ):
        print("\nOVERALL=PASS")
        return 0
    print("\nOVERALL=FAIL")
    return 1


if __name__ == "__main__":
    sys.exit(main())
