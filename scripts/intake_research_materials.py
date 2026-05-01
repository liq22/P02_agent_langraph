#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RESEARCH_MATERIAL_INTAKE_SCHEMA = "backend/registry/schema_registry/research_material_intake.schema.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Record research materials into a phase or node entry point.")
    parser.add_argument("--input", required=True, help="YAML or JSON intake file.")
    parser.add_argument("--root", default=Path(__file__).resolve().parent.parent, help="Repository root.")
    parser.add_argument("--target-phase", dest="entry_phase", help="Optional phase override: P0, P1, P2, P3, or P4.")
    parser.add_argument("--target-node", help="Optional target node id or research/ path override.")
    parser.add_argument("--no-refresh", action="store_true", help="Do not refresh generated views after recording.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))

    from backend.agent_gateway.research_intake import ResearchIntakeError, ingest_materials, read_intake_file

    root = Path(args.root).resolve()
    payload = read_intake_file(Path(args.input))
    if args.entry_phase:
        payload["entry_phase"] = args.entry_phase
    if args.target_node:
        payload["target_node"] = args.target_node

    try:
        result = ingest_materials(root, payload, refresh=not args.no_refresh)
    except (ResearchIntakeError, json.JSONDecodeError) as exc:
        print(f"material intake: fail: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
