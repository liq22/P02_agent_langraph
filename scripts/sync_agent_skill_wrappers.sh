#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="${1:-.}"
TARGET="${2:-both}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python "$SCRIPT_DIR/generate_agent_skill_wrappers.py" --repo-root "$REPO_ROOT" --target "$TARGET" --clean

echo
echo "Done."
if [ "$TARGET" = "both" ] || [ "$TARGET" = "claude" ]; then
  echo "Claude project wrappers generated under $REPO_ROOT/.claude/skills"
fi
if [ "$TARGET" = "both" ] || [ "$TARGET" = "codex" ]; then
  echo "Codex project wrappers generated under $REPO_ROOT/.codex/skills"
fi
echo "Restart Claude Code and Codex to pick up local wrapper changes."
