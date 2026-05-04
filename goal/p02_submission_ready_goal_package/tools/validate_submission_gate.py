#!/usr/bin/env python3
"""Validate a simple P02 submission gate JSON/YAML-like status file.

Input is JSON for portability. Codex may generate this status from the checklists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TRUE = [
    ("data_ready", "canonical_metadata_exists"),
    ("data_ready", "required_h5_exists"),
    ("data_ready", "checksum_manifest_exists"),
    ("data_ready", "metadata_h5_alignment_pass"),
    ("data_ready", "vibench_read_bundle_exists"),
    ("project_ready", "phmga_submodule_commit_recorded"),
    ("project_ready", "vibench_read_boundary_pass"),
    ("project_ready", "phmga_preflight_pass"),
    ("project_ready", "stage_b_selection_done"),
    ("project_ready", "stage_c_main_results_done"),
    ("project_ready", "main_tables_nonempty"),
    ("paper_ready", "claim_evidence_registry_complete"),
    ("paper_ready", "tables_trace_to_phmga"),
    ("paper_ready", "data_sources_trace_to_vibench"),
    ("paper_ready", "final_tex_complete"),
    ("paper_ready", "final_submission_check_pass"),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", required=True)
    args = ap.parse_args()
    data = json.loads(Path(args.status).read_text(encoding="utf-8"))
    blockers = []
    for section, field in REQUIRED_TRUE:
        if not data.get(section, {}).get(field, False):
            blockers.append(f"{section}.{field}")
    result = {"submission_ready": not blockers, "blockers": blockers}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
