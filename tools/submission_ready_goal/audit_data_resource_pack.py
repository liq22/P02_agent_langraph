#!/usr/bin/env python3
"""Audit a P02 DATA_ROOT resource pack.

The audit is deliberately conservative:
- It never copies large H5 files into the repo.
- It records checksums and lightweight metadata/H5 facts.
- It writes both JSON and YAML-like files so humans and Codex can consume the same facts.
- It produces a single data_gate_status.json for downstream `/goal` gates.

Optional dependencies:
- pandas + openpyxl for XLSX inspection
- h5py for H5 inspection
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FORMAL_H5 = ["RM_017_Ottawa19.h5", "RM_101_THU_GEARBOX.h5"]
CANONICAL_METADATA = "metadata.xlsx"
LINEAGE = ["metadata_25_10_30.xlsx", "metadata_25_11_13.xlsx"]


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value)
    if not text:
        return "''"
    if any(ch in text for ch in [":", "#", "\n", "[", "]", "{", "}"]):
        return json.dumps(text, ensure_ascii=False)
    return text


def _yaml_dump(data: Any, indent: int = 0) -> str:
    sp = " " * indent
    if isinstance(data, dict):
        lines: list[str] = []
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{sp}{k}:")
                lines.append(_yaml_dump(v, indent + 2))
            else:
                lines.append(f"{sp}{k}: {_yaml_scalar(v)}")
        return "\n".join(lines)
    if isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(f"{sp}-")
                lines.append(_yaml_dump(item, indent + 2))
            else:
                lines.append(f"{sp}- {_yaml_scalar(item)}")
        return "\n".join(lines)
    return f"{sp}{_yaml_scalar(data)}"


def write_yaml(path: Path, data: Any) -> None:
    path.write_text(_yaml_dump(data) + "\n", encoding="utf-8")


def inspect_xlsx(path: Path) -> dict[str, Any]:
    info: dict[str, Any] = {
        "file": str(path),
        "exists": path.exists(),
        "rows": None,
        "columns": [],
        "sample_id_columns": [],
        "dataset_columns": [],
        "label_columns": [],
        "error": None,
    }
    if not path.exists():
        return info
    try:
        import pandas as pd  # type: ignore
        df = pd.read_excel(path)
        cols = [str(c) for c in df.columns]
        lowered = {c.lower(): c for c in cols}
        info["rows"] = int(len(df))
        info["columns"] = cols
        info["sample_id_columns"] = [c for c in cols if c.lower() in {"id", "sample_id", "sampleid"}]
        info["dataset_columns"] = [c for c in cols if c.lower() in {"name", "dataset", "dataset_name", "dataset_id"}]
        info["label_columns"] = [c for c in cols if c.lower() in {"label", "fault", "class", "y"}]
        # small preview for alignment; not full metadata export
        id_col = lowered.get("id") or lowered.get("sample_id")
        if id_col:
            info["sample_ids_preview"] = [str(x) for x in df[id_col].dropna().head(20).tolist()]
    except Exception as e:  # noqa: BLE001
        info["error"] = repr(e)
    return info


def inspect_h5(path: Path, max_keys: int = 20) -> dict[str, Any]:
    info: dict[str, Any] = {
        "file": str(path),
        "exists": path.exists(),
        "key_count": None,
        "sample_keys": [],
        "sample_shapes": {},
        "error": None,
    }
    if not path.exists():
        return info
    try:
        import h5py  # type: ignore
        with h5py.File(path, "r") as h:
            keys = list(h.keys())
            info["key_count"] = len(keys)
            info["sample_keys"] = [str(k) for k in keys[:max_keys]]
            for k in keys[: min(len(keys), 10)]:
                obj = h[k]
                shape = getattr(obj, "shape", None)
                info["sample_shapes"][str(k)] = list(shape) if shape is not None else None
    except Exception as e:  # noqa: BLE001
        info["error"] = repr(e)
    return info


def build_alignment(metadata_info: dict[str, Any], h5_info: dict[str, Any]) -> dict[str, Any]:
    """Best-effort metadata/H5 alignment without loading the whole data set."""
    meta_ids = set(str(x) for x in metadata_info.get("sample_ids_preview", []) or [])
    rows: list[dict[str, Any]] = []
    for name, h5 in h5_info.items():
        h5_keys = set(str(x) for x in h5.get("sample_keys", []) or [])
        overlap_preview = sorted(meta_ids & h5_keys)[:20]
        rows.append({
            "h5_file": name,
            "exists": h5.get("exists", False),
            "key_count": h5.get("key_count"),
            "preview_overlap_count": len(overlap_preview),
            "preview_overlap_ids": overlap_preview,
            "status": "auditable" if h5.get("exists") and h5.get("error") is None else "not_auditable",
        })
    hard_fail = []
    if metadata_info.get("exists") is not True:
        hard_fail.append("canonical_metadata_missing")
    if metadata_info.get("error"):
        hard_fail.append("canonical_metadata_unreadable")
    for name, h5 in h5_info.items():
        if h5.get("exists") is not True:
            hard_fail.append(f"missing:{name}")
        if h5.get("error"):
            hard_fail.append(f"unreadable:{name}")
    return {
        "alignment_scope": "preview_and_auditability",
        "note": "Full sample-level alignment should be run by PHMGA/Vibench adapter once DATA_ROOT is mounted.",
        "metadata_rows": metadata_info.get("rows"),
        "metadata_id_preview_available": bool(meta_ids),
        "h5_alignment_rows": rows,
        "hard_fail": hard_fail,
        "passed": not hard_fail,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()

    data_root = Path(args.data_root).expanduser().resolve()
    out = Path(args.output_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    required = [CANONICAL_METADATA, *FORMAL_H5]
    audited_files = [*required, *LINEAGE]
    files = {name: data_root / name for name in audited_files}

    checksums = {}
    for name, path in files.items():
        if path.exists():
            checksums[name] = sha256_file(path)

    metadata_info = inspect_xlsx(data_root / CANONICAL_METADATA)
    lineage_info = {name: inspect_xlsx(data_root / name) for name in LINEAGE}
    h5_info = {name: inspect_h5(data_root / name) for name in FORMAL_H5}
    alignment = build_alignment(metadata_info, h5_info)

    manifest = {
        "version": "data_manifest_v1",
        "data_root": str(data_root),
        "canonical_metadata": CANONICAL_METADATA,
        "metadata_lineage": [
            {"file": name, "exists": (data_root / name).exists(), "checksum_sha256": checksums.get(name)}
            for name in LINEAGE
        ],
        "formal_p02_datasets": [
            {"dataset_name": name.removesuffix(".h5"), "h5_file": name, "required": True, "checksum_sha256": checksums.get(name)}
            for name in FORMAL_H5
        ],
        "extension_datasets": sorted(p.name for p in data_root.glob("RM_*.h5") if p.name not in FORMAL_H5),
        "checksums": checksums,
        "audit_status": "pass" if all((data_root / x).exists() for x in required) and alignment["passed"] else "fail",
    }

    dataset_registry = {
        "version": "dataset_registry_v1",
        "formal_scope": [
            {"dataset_name": "RM_017_Ottawa19", "h5_file": "RM_017_Ottawa19.h5", "paper_role": "Ottawa formal run"},
            {"dataset_name": "RM_101_THU_GEARBOX", "h5_file": "RM_101_THU_GEARBOX.h5", "paper_role": "RM101 formal run"},
        ],
        "extension_h5_files": manifest["extension_datasets"],
    }

    write_json(out / "data_manifest.json", manifest)
    write_yaml(out / "data_manifest.yaml", manifest)
    write_json(out / "dataset_registry.json", dataset_registry)
    write_yaml(out / "dataset_registry.yaml", dataset_registry)
    write_json(out / "metadata_audit.json", {"canonical": metadata_info, "lineage": lineage_info})
    write_json(out / "h5_audit.json", h5_info)
    write_json(out / "metadata_h5_alignment.json", alignment)
    (out / "checksums.sha256").write_text("\n".join(f"{v}  {k}" for k, v in checksums.items()) + "\n", encoding="utf-8")

    missing = [x for x in required if not (data_root / x).exists()]
    score = 100
    if missing:
        score -= 35
    if not checksums:
        score -= 15
    if not alignment["passed"]:
        score -= 25
    if metadata_info.get("error"):
        score -= 15
    score = max(score, 0)

    scorecard = {
        "scorecard_id": "data_readiness_runtime_audit_v2",
        "missing_required_files": missing,
        "score": score,
        "passed": score >= 90 and not missing and alignment["passed"],
        "hard_fail": alignment.get("hard_fail", []),
        "notes": ["Install pandas/openpyxl/h5py for richer metadata and H5 audits if fields are null."],
    }
    write_json(out / "data_readiness_scorecard.json", scorecard)
    write_yaml(out / "data_readiness_scorecard.yaml", scorecard)

    gate = {
        "gate": "data_ready",
        "passed": bool(scorecard["passed"]),
        "score": score,
        "hard_fail": scorecard["hard_fail"],
        "blockers": missing + scorecard["hard_fail"],
        "outputs": {
            "data_manifest_yaml": str(out / "data_manifest.yaml"),
            "data_manifest_json": str(out / "data_manifest.json"),
            "dataset_registry_yaml": str(out / "dataset_registry.yaml"),
            "checksums": str(out / "checksums.sha256"),
            "metadata_audit": str(out / "metadata_audit.json"),
            "h5_audit": str(out / "h5_audit.json"),
            "metadata_h5_alignment": str(out / "metadata_h5_alignment.json"),
        },
    }
    write_json(out / "data_gate_status.json", gate)
    print(json.dumps(gate, ensure_ascii=False, indent=2))
    return 0 if gate["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
