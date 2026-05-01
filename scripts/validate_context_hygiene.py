#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


POLICY_PATH = Path("backend/registry/runtime_policy/context_hygiene.yaml")
REQUIRED_KEYS = {
    "trusted_instruction_roots",
    "default_read_allowlist",
    "explicit_request_only_globs",
    "never_read_content_globs",
    "default_exclude_globs",
    "human_only_globs",
    "generated_globs",
    "reference_quarantine_globs",
    "large_noise_globs",
    "required_doc_refs",
}
ALLOWED_HUMAN_ONLY_CONTEXT = (
    "do not read",
    "not read",
    "unless explicitly requested",
    "explicitly requested",
    "human-only",
    "human only",
    "protected",
    "agent_read_exclude",
    "cannot_modify",
    "required_files",
    "protected_files",
    "exclude",
    "excludes",
    "optional",
    "不默认",
    "不读取",
    "显式",
    "人类",
)
TEXT_SUFFIXES = {
    ".md",
    ".py",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".txt",
    ".html",
    ".css",
    ".js",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=str(root),
        text=True,
        capture_output=True,
        check=False,
    )


def tracked_files(root: Path) -> list[str]:
    proc = run_git(root, ["ls-files", "-z"])
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "git ls-files failed")
    return sorted(item for item in proc.stdout.split("\0") if item)


def load_policy(root: Path) -> dict[str, Any]:
    path = root / POLICY_PATH
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{POLICY_PATH}: expected mapping")
    return payload


def as_string_list(policy: dict[str, Any], key: str) -> list[str]:
    value = policy.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{POLICY_PATH}: `{key}` must be a list of strings")
    return value


def tracked_secret_like_files(files: list[str], secret_globs: list[str]) -> list[str]:
    return [path for path in files if matches_any(path, secret_globs)]


def existing_secret_candidates(root: Path) -> list[str]:
    candidates: set[str] = set()
    for pattern in (".env", ".env.*", "**/.env", "**/.env.*"):
        for path in root.glob(pattern):
            if path.is_file():
                candidates.add(rel(path, root))
    sensitive_tokens = ("secret", "credential", "private_key")
    for path in root.rglob("*"):
        if ".git" in path.parts or not path.is_file():
            continue
        name = path.name.lower()
        if any(token in name for token in sensitive_tokens) or name in {"id_rsa", "id_ed25519"}:
            candidates.add(rel(path, root))
    return sorted(candidates)


def git_ignored(root: Path, path: str) -> bool:
    proc = run_git(root, ["check-ignore", "--quiet", path])
    return proc.returncode == 0


def text_files_for_policy_scan(files: list[str], policy: dict[str, Any]) -> list[str]:
    skip = (
        as_string_list(policy, "never_read_content_globs")
        + as_string_list(policy, "reference_quarantine_globs")
        + as_string_list(policy, "large_noise_globs")
    )
    result = []
    for path in files:
        if matches_any(path, skip):
            continue
        if Path(path).suffix.lower() in TEXT_SUFFIXES:
            result.append(path)
    return result


def read_text_safe(root: Path, path: str) -> str:
    try:
        return (root / path).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def check_policy(root: Path, policy: dict[str, Any], files: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing_keys = sorted(REQUIRED_KEYS - set(policy))
    if missing_keys:
        errors.append(f"{POLICY_PATH}: missing keys: {', '.join(missing_keys)}")

    for key in REQUIRED_KEYS & set(policy):
        try:
            as_string_list(policy, key)
        except ValueError as exc:
            errors.append(str(exc))

    for path in as_string_list(policy, "required_doc_refs"):
        if not (root / path).is_file():
            errors.append(f"required context hygiene doc missing: {path}")

    excluded = as_string_list(policy, "default_exclude_globs") + as_string_list(policy, "explicit_request_only_globs")
    allowlist = as_string_list(policy, "default_read_allowlist")
    for pattern in allowlist:
        if matches_any(pattern, excluded) or any(fnmatch.fnmatch(pattern, excluded_pattern) for excluded_pattern in excluded):
            errors.append(f"default read allowlist includes excluded pattern: {pattern}")

    secret_tracked = tracked_secret_like_files(files, as_string_list(policy, "never_read_content_globs"))
    if secret_tracked:
        errors.append("secret-like paths are tracked: " + ", ".join(secret_tracked[:20]))

    existing_secrets = existing_secret_candidates(root)
    unignored = [path for path in existing_secrets if not git_ignored(root, path)]
    if unignored:
        errors.append("secret-like paths exist but are not ignored: " + ", ".join(unignored[:20]))
    if existing_secrets:
        warnings.append(f"secret-like path names detected and not read: {len(existing_secrets)}")

    reference_instruction_files = [
        path
        for path in files
        if path.startswith("_reference/") and Path(path).name in {"AGENTS.md", "CLAUDE.md", "README.md"}
    ]
    if reference_instruction_files:
        errors.append("_reference instruction files are tracked: " + ", ".join(reference_instruction_files[:20]))

    return errors, warnings


def check_human_only_mentions(root: Path, policy: dict[str, Any], files: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    human_only = "docs/HUMAN_ONLY.md"

    root_readme = root / "README.md"
    if root_readme.is_file():
        readme_text = root_readme.read_text(encoding="utf-8")
        if "Do not read `docs/HUMAN_ONLY.md` unless explicitly requested" not in readme_text:
            errors.append("README.md must explicitly ban default reads of docs/HUMAN_ONLY.md")

    for path in files:
        if not path.endswith("/skills/local_entry.md"):
            continue
        text = read_text_safe(root, path)
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            window = "\n".join(lines[max(0, line_no - 6):line_no + 1]).lower()
            if human_only in line and not any(token in window for token in ALLOWED_HUMAN_ONLY_CONTEXT):
                errors.append(f"{path}:{line_no}: HUMAN_ONLY.md appears outside an explicit optional/protected context")

    for path in text_files_for_policy_scan(files, policy):
        text = read_text_safe(root, path)
        if human_only not in text:
            continue
        lines = text.splitlines()
        for line_no, line in enumerate(lines, start=1):
            window = "\n".join(lines[max(0, line_no - 6):line_no + 1]).lower()
            if human_only in line and not any(token in window for token in ALLOWED_HUMAN_ONLY_CONTEXT):
                warnings.append(f"{path}:{line_no}: HUMAN_ONLY.md mention should state protected/optional semantics")
                break

    return errors, warnings


def check_reference_quarantine(root: Path, policy: dict[str, Any], files: list[str]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    if (root / "_reference").exists() and "_reference/**" not in as_string_list(policy, "reference_quarantine_globs"):
        errors.append("policy must quarantine _reference/**")

    for path in ("AGENTS.md", "README.md"):
        text = read_text_safe(root, path)
        lowered = text.lower()
        if (
            "_reference/" in text
            and "external or historical references only" not in text
            and "not default context" not in text
            and "do not read `_reference/**`" not in lowered
        ):
            warnings.append(f"{path}: _reference mention should state quarantine semantics")

    tracked_reference = [path for path in files if path.startswith("_reference/")]
    if tracked_reference:
        errors.append("_reference files are tracked; quarantine should remain untracked: " + ", ".join(tracked_reference[:20]))

    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate agent context hygiene boundaries.")
    parser.add_argument("--root", type=Path, default=repo_root())
    args = parser.parse_args(argv)

    root = args.root.resolve()
    policy = load_policy(root)
    files = tracked_files(root)

    errors: list[str] = []
    warnings: list[str] = []
    for checker in (check_policy, check_human_only_mentions, check_reference_quarantine):
        new_errors, new_warnings = checker(root, policy, files)
        errors.extend(new_errors)
        warnings.extend(new_warnings)

    print(f"context_hygiene_policy: {POLICY_PATH.as_posix()}")
    print(f"tracked_files_scanned: {len(files)}")
    if warnings:
        print("warnings:")
        for item in warnings:
            print(f"- {item}")

    if errors:
        print("context_hygiene: fail")
        for item in errors:
            print(f"- {item}")
        return 1

    print("context_hygiene: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
