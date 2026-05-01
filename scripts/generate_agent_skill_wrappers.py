#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
from pathlib import Path


FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}

    data: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip("\"'")
    return data


def canonical_skills(source_dir: Path) -> list[tuple[str, Path, dict[str, str]]]:
    if not source_dir.exists():
        return []

    skills: list[tuple[str, Path, dict[str, str]]] = []
    for skill_dir in sorted(source_dir.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if skill_dir.is_dir() and skill_file.is_file():
            text = skill_file.read_text(encoding="utf-8")
            skills.append((skill_dir.name, skill_file, parse_frontmatter(text)))
    return skills


def render_wrapper(skill_key: str, rel_source: str, meta: dict[str, str]) -> str:
    name = meta.get("name", skill_key)
    description = meta.get("description", f"Wrapper for canonical project skill {skill_key}.")
    return f"""---
name: {name}
description: {description}
---

@{rel_source}
"""


def remove_generated_dir(path: Path, repo_root: Path) -> None:
    resolved = path.resolve()
    allowed = {
        (repo_root / ".claude" / "skills").resolve(),
        (repo_root / ".codex" / "skills").resolve(),
    }
    if resolved not in allowed:
        raise ValueError(f"refusing to clean unexpected directory: {path}")
    if resolved.exists():
        shutil.rmtree(resolved)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate local Claude/Codex wrappers from canonical .agent/skills."
    )
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--source-dir", default=".agent/skills", help="Canonical skill source directory")
    parser.add_argument("--clean", action="store_true", help="Remove generated local wrapper dirs before writing")
    parser.add_argument("--target", choices=["both", "claude", "codex"], default="both", help="Wrapper target to generate")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    source_dir = (repo_root / args.source_dir).resolve()
    claude_dir = repo_root / ".claude" / "skills"
    codex_dir = repo_root / ".codex" / "skills"

    skills = canonical_skills(source_dir)
    if not skills:
        raise SystemExit(f"No canonical skills found under {source_dir}")

    targets = ["claude", "codex"] if args.target == "both" else [args.target]

    if args.clean:
        if "claude" in targets:
            remove_generated_dir(claude_dir, repo_root)
        if "codex" in targets:
            remove_generated_dir(codex_dir, repo_root)

    generated = {"claude": [], "codex": []}
    for skill_key, skill_file, meta in skills:
        rel_source_for_claude = os.path.relpath(skill_file, start=claude_dir / skill_key)
        rel_source_for_codex = os.path.relpath(skill_file, start=codex_dir / skill_key)

        claude_path = claude_dir / skill_key / "SKILL.md"
        codex_path = codex_dir / skill_key / "SKILL.md"

        if "claude" in targets:
            write_text(claude_path, render_wrapper(skill_key, rel_source_for_claude, meta))
            generated["claude"].append(str(claude_path.relative_to(repo_root)))

        if "codex" in targets:
            write_text(codex_path, render_wrapper(skill_key, rel_source_for_codex, meta))
            generated["codex"].append(str(codex_path.relative_to(repo_root)))

    print("Generated local skill wrappers:")
    for agent, paths in generated.items():
        if agent not in targets:
            continue
        print(f"- {agent}: {len(paths)}")
        for path in paths:
            print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
