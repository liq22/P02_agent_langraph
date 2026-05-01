#!/usr/bin/env python3
"""Create the project-local venv described by requirement.yaml."""

from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = REPO_ROOT / "requirement.yaml"


def strip_comment(line: str) -> str:
    in_single = False
    in_double = False
    for idx, char in enumerate(line):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            return line[:idx]
    return line


def parse_scalar(value: str) -> object:
    value = value.strip()
    if not value:
        return ""
    if value[0] == value[-1:] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value.isdigit():
        return int(value)
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def load_manifest(path: Path) -> dict[str, object]:
    manifest: dict[str, object] = {}
    current_list: str | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = strip_comment(raw_line).rstrip()
        if not line.strip():
            continue

        stripped = line.strip()
        if line == stripped:
            current_list = None
            if ":" not in stripped:
                raise ValueError(f"Invalid manifest line: {raw_line}")
            key, value = stripped.split(":", 1)
            key = key.strip()
            value = value.strip()
            if not value:
                manifest[key] = []
                current_list = key
            else:
                manifest[key] = parse_scalar(value)
            continue

        if current_list is None or not stripped.startswith("- "):
            raise ValueError(f"Invalid manifest list item: {raw_line}")
        list_value = parse_scalar(stripped[2:].strip())
        current = manifest.setdefault(current_list, [])
        if not isinstance(current, list):
            raise ValueError(f"Manifest key is not a list: {current_list}")
        current.append(list_value)

    return manifest


def parse_version_tuple(value: str) -> tuple[int, int]:
    major, minor, *_ = value.split(".")
    return int(major), int(minor)


def check_python_spec(spec: str) -> None:
    current = sys.version_info[:2]
    for clause in (part.strip() for part in spec.split(",")):
        if clause.startswith(">="):
            required = parse_version_tuple(clause[2:].strip())
            if current < required:
                raise SystemExit(
                    f"Python {required[0]}.{required[1]}+ is required; "
                    f"current is {current[0]}.{current[1]}"
                )
        elif clause.startswith(">"):
            required = parse_version_tuple(clause[1:].strip())
            if current <= required:
                raise SystemExit(
                    f"Python >{required[0]}.{required[1]} is required; "
                    f"current is {current[0]}.{current[1]}"
                )
        elif clause.startswith("<="):
            limit = parse_version_tuple(clause[2:].strip())
            if current > limit:
                raise SystemExit(
                    f"Python <= {limit[0]}.{limit[1]} is required; "
                    f"current is {current[0]}.{current[1]}"
                )
        elif clause.startswith("<"):
            limit = parse_version_tuple(clause[1:].strip())
            if current >= limit:
                raise SystemExit(
                    f"Python <{limit[0]}.{limit[1]} is required; "
                    f"current is {current[0]}.{current[1]}"
                )
        elif clause:
            raise ValueError(f"Unsupported Python version clause: {clause}")


def resolve_venv_path(value: object) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("Manifest must define a non-empty venv path")
    path = (REPO_ROOT / value).resolve()
    if path != REPO_ROOT and REPO_ROOT not in path.parents:
        raise ValueError(f"Refusing to create venv outside repo: {path}")
    return path


def run_command(command: list[str], *, dry_run: bool) -> None:
    printable = shlex.join(command)
    if dry_run:
        print(f"[dry-run] {printable}", flush=True)
        return
    print(f"[run] {printable}", flush=True)
    subprocess.run(command, cwd=REPO_ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="Path to requirement.yaml",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without creating the venv or installing packages",
    )
    parser.add_argument(
        "--no-upgrade-pip",
        action="store_true",
        help="Skip pip self-upgrade inside the venv",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    manifest = load_manifest(manifest_path)

    python_spec = manifest.get("python")
    if isinstance(python_spec, str) and python_spec:
        check_python_spec(python_spec)

    venv_path = resolve_venv_path(manifest.get("venv"))
    pip_packages = manifest.get("pip", [])
    if not isinstance(pip_packages, list) or not all(
        isinstance(item, str) and item for item in pip_packages
    ):
        raise ValueError("Manifest pip section must be a non-empty list of strings")

    run_command([sys.executable, "-m", "venv", str(venv_path)], dry_run=args.dry_run)
    python_bin = venv_path / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")

    if not args.no_upgrade_pip:
        run_command(
            [str(python_bin), "-m", "pip", "install", "--upgrade", "pip"],
            dry_run=args.dry_run,
        )
    run_command(
        [str(python_bin), "-m", "pip", "install", *pip_packages],
        dry_run=args.dry_run,
    )

    print(f"[ok] venv ready: {venv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
