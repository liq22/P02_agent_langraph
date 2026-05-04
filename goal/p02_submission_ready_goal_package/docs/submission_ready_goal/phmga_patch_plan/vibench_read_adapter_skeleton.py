"""Skeleton for PHMGA-side Vibench read-only adapter.

This file is a scaffold for Codex. Do not copy blindly without adapting to the
actual PHMGA package layout and imports.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict
import json


@dataclass
class VibenchReadBundle:
    dataset_name: str
    catalog: str
    reader_backend: str
    factory_name: str
    data_root: str
    metadata_file: str
    h5_file: str
    metadata_rows: int | None
    h5_keys: int | None
    sample_id_key: str
    tensor_layout_before_phmga: str
    handoff_target: str
    read_status: str
    provenance: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def write_bundle(bundle: VibenchReadBundle, output_path: str | Path) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")


class VibenchReadAdapter:
    """Read-only adapter: Vibench reads, PHMGA processes."""

    def __init__(self, data_cfg: Dict[str, Any]):
        self.data_cfg = dict(data_cfg)

    def read(self) -> VibenchReadBundle:
        data_source = dict(self.data_cfg.get("data_source", {}))
        data_root = Path(data_source.get("data_dir", self.data_cfg.get("data_root", ""))).expanduser()
        metadata_file = data_source.get("metadata_file", self.data_cfg.get("metadata_file", "metadata.xlsx"))
        h5_file = data_source.get("h5_file", self.data_cfg.get("h5_file", f"{self.data_cfg.get('dataset_name')}.h5"))

        # Codex should replace this with actual metadata/H5 audits using pandas/h5py.
        metadata_rows = None
        h5_keys = None

        return VibenchReadBundle(
            dataset_name=str(self.data_cfg.get("dataset_name")),
            catalog=str(self.data_cfg.get("catalog", "PHM-Vibench")),
            reader_backend="vibench_data_factory",
            factory_name=str(data_source.get("factory_name", "read_only")),
            data_root=str(data_root),
            metadata_file=str(metadata_file),
            h5_file=str(h5_file),
            metadata_rows=metadata_rows,
            h5_keys=h5_keys,
            sample_id_key="Id",
            tensor_layout_before_phmga="L_C_or_L_C_1",
            handoff_target="PHMGA DatasetProtocol",
            read_status="pending_audit",
            provenance={"source": "user_supplied_DATA_ROOT"},
        )
