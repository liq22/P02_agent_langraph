#!/usr/bin/env python3
"""Run the active Generic-base P2-E1 formal-v2 readiness/finalization gate."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

from scripts.finalize_p2_e1_generic_base_formal_v2 import (
    DEFAULT_PROTOCOL,
    DEFAULT_READINESS as OUTPUT,
    DEFAULT_RESULT,
    FinalizationError as ReadinessError,
    audit as _audit,
    build_documents,
)


ROOT = Path(__file__).resolve().parents[1]


def audit(**kwargs: Any) -> dict[str, Any]:
    return _audit(**kwargs)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=DEFAULT_PROTOCOL)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--result-output", type=Path, default=DEFAULT_RESULT)
    parser.add_argument("--benchmark-formal-run-stamp", required=True)
    parser.add_argument("--benchmark-control-protocol-id", required=True)
    parser.add_argument("--benchmark-control-profile-id", required=True)
    parser.add_argument("--generic-core-root", type=Path, required=True)
    parser.add_argument("--generic-replay-root", type=Path, required=True)
    parser.add_argument("--graph-core-root", type=Path, required=True)
    parser.add_argument("--graph-replay-root", type=Path, required=True)
    args = parser.parse_args(argv)
    readiness, result = build_documents(
        protocol_path=args.protocol,
        benchmark_formal_run_stamp=args.benchmark_formal_run_stamp,
        benchmark_control_protocol_id=args.benchmark_control_protocol_id,
        benchmark_control_profile_id=args.benchmark_control_profile_id,
        generic_core_root=args.generic_core_root,
        generic_replay_root=args.generic_replay_root,
        graph_core_root=args.graph_core_root,
        graph_replay_root=args.graph_replay_root,
    )
    for path, document in ((args.output, readiness), (args.result_output, result)):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "accepted": readiness["accepted"],
                "effect_estimates_emitted": result["effect_estimates_emitted"],
                "provider_calls": 0,
                "readiness": str(args.output),
                "result": str(args.result_output),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
