#!/usr/bin/env python3
"""Validate the P02 traceability matrix before paper prose/table use."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

REQUIRED_ITEM_FIELDS = [
    'item_id', 'item_type', 'paper_section', 'status', 'evidence_id',
    'data_source', 'phmga_source', 'validation'
]
POSITIVE_STATUSES = {'supported'}
ALLOWED_STATUSES = {'supported', 'planned', 'unclear', 'unsupported', 'negative'}


def parse(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    try:
        return json.loads(text)
    except Exception:
        import yaml  # type: ignore
        return yaml.safe_load(text)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--matrix', required=True)
    args = ap.parse_args()
    data = parse(Path(args.matrix))
    blockers, warnings = [], []
    if not data.get('submodule', {}).get('phmga_commit'):
        blockers.append('submodule.phmga_commit missing')
    if not data.get('data', {}).get('data_manifest'):
        blockers.append('data.data_manifest missing')
    if not data.get('data', {}).get('vibench_read_bundle'):
        blockers.append('data.vibench_read_bundle missing')
    items = data.get('items') or []
    if not items:
        blockers.append('items empty')
    for i, item in enumerate(items):
        for f in REQUIRED_ITEM_FIELDS:
            if f not in item:
                blockers.append(f'items[{i}] missing {f}')
        status = item.get('status')
        if status not in ALLOWED_STATUSES:
            blockers.append(f'items[{i}] invalid status {status!r}')
        if item.get('item_type') in {'table', 'figure', 'claim'} and status in POSITIVE_STATUSES:
            ph = item.get('phmga_source') or {}
            if not ph.get('artifact_dir'):
                blockers.append(f'items[{i}] supported item missing artifact_dir')
            if not ph.get('result_md') and item.get('item_type') == 'table':
                blockers.append(f'items[{i}] supported table missing result_md')
            if str(ph.get('ledger_row', '')).lower() in {'pending', 'fail', 'no_evidence'}:
                blockers.append(f'items[{i}] supported item uses invalid ledger row status')
        if status != 'supported':
            warnings.append(f"items[{i}] {item.get('item_id')} is {status}; do not write as positive result")
    result = {'traceability_lock_valid': not blockers, 'blockers': blockers, 'warnings': warnings}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['traceability_lock_valid'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
