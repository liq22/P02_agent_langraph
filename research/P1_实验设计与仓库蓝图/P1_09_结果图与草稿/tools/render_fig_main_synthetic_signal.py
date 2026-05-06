#!/usr/bin/env python3
"""Render the P1_09 synthetic/offline signal draft figure.

The script is intentionally dependency-free. It reads the node-local plotted
data TSV and writes the SVG draft deterministically.
"""

from __future__ import annotations

import csv
from pathlib import Path


NODE_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = NODE_ROOT / "figures" / "fig_main_synthetic_signal_data.tsv"
SVG_PATH = NODE_ROOT / "figures" / "fig_main_synthetic_signal.svg"


def read_rows() -> list[dict[str, str]]:
    with DATA_PATH.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 2:
        raise SystemExit(f"expected exactly 2 rows in {DATA_PATH}, found {len(rows)}")
    for row in rows:
        for key in ("row_id", "workflow_mode", "test_accuracy", "test_macro_f1"):
            if key not in row or row[key] == "":
                raise SystemExit(f"missing {key} in plotted data row: {row}")
    return rows


def bar_y(value: float) -> float:
    top = 105.0
    base = 375.0
    return base - (base - top) * value


def bar_height(value: float) -> float:
    return 375.0 - bar_y(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def render(rows: list[dict[str, str]]) -> str:
    baseline = rows[0]
    attempt = rows[1]
    values = {
        "acc_baseline": float(baseline["test_accuracy"]),
        "acc_attempt": float(attempt["test_accuracy"]),
        "f1_baseline": float(baseline["test_macro_f1"]),
        "f1_attempt": float(attempt["test_macro_f1"]),
    }

    bars = [
        ("180", values["acc_baseline"], "#2f6fed"),
        ("242", values["acc_attempt"], "#d97706"),
        ("380", values["f1_baseline"], "#2f6fed"),
        ("442", values["f1_attempt"], "#d97706"),
    ]
    bar_svg = []
    for x, value, color in bars:
        y = bar_y(value)
        h = bar_height(value)
        label_y = y - 8
        bar_svg.append(
            f'  <rect x="{x}" y="{y:.1f}" width="54" height="{h:.1f}" fill="{color}"/>'
        )
        bar_svg.append(
            f'  <text x="{int(x) + 4}" y="{label_y:.1f}" font-family="Arial, sans-serif" font-size="12" fill="#233042">{fmt(value)}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="520" viewBox="0 0 900 520" role="img" aria-labelledby="title desc">
  <title id="title">Draft figure: bounded synthetic/offline signal</title>
  <desc id="desc">Grouped bar chart showing P1_04 single-run synthetic offline accuracy and macro-F1 for simple_fullchain baseline and supervisor_proving controlled attempt.</desc>
  <rect width="900" height="520" fill="#ffffff"/>
  <text x="48" y="42" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#18212f">Bounded synthetic/offline signal</text>
  <text x="48" y="70" font-family="Arial, sans-serif" font-size="14" fill="#526071">P1_04 Ottawa synthetic, offline_stub, single run. Draft only; not formal Stage C/D evidence.</text>

  <line x1="110" y1="105" x2="110" y2="375" stroke="#233042" stroke-width="1.5"/>
  <line x1="110" y1="375" x2="675" y2="375" stroke="#233042" stroke-width="1.5"/>
  <line x1="106" y1="105" x2="675" y2="105" stroke="#d5dce5" stroke-width="1"/>
  <line x1="106" y1="240" x2="675" y2="240" stroke="#e7ebf0" stroke-width="1"/>
  <line x1="106" y1="375" x2="675" y2="375" stroke="#d5dce5" stroke-width="1"/>
  <text x="74" y="110" font-family="Arial, sans-serif" font-size="12" fill="#526071">1.0</text>
  <text x="74" y="245" font-family="Arial, sans-serif" font-size="12" fill="#526071">0.5</text>
  <text x="82" y="380" font-family="Arial, sans-serif" font-size="12" fill="#526071">0</text>

{chr(10).join(bar_svg)}
  <text x="198" y="407" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#233042">Accuracy</text>
  <text x="423" y="407" font-family="Arial, sans-serif" font-size="14" text-anchor="middle" fill="#233042">Macro-F1</text>

  <rect x="545" y="124" width="16" height="16" fill="#2f6fed"/>
  <text x="568" y="137" font-family="Arial, sans-serif" font-size="13" fill="#233042">{baseline["workflow_mode"]} baseline</text>
  <rect x="545" y="150" width="16" height="16" fill="#d97706"/>
  <text x="568" y="163" font-family="Arial, sans-serif" font-size="13" fill="#233042">{attempt["workflow_mode"]} attempt</text>

  <rect x="705" y="115" width="150" height="190" rx="6" fill="#f6f8fb" stroke="#d5dce5"/>
  <text x="722" y="142" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#18212f">Scope guard</text>
  <text x="722" y="170" font-family="Arial, sans-serif" font-size="12" fill="#526071">Synthetic/offline only</text>
  <text x="722" y="194" font-family="Arial, sans-serif" font-size="12" fill="#526071">Single run, no variance</text>
  <text x="722" y="218" font-family="Arial, sans-serif" font-size="12" fill="#526071">No real-data claim</text>
  <text x="722" y="242" font-family="Arial, sans-serif" font-size="12" fill="#526071">No RM101 resolution</text>
  <text x="722" y="266" font-family="Arial, sans-serif" font-size="12" fill="#526071">Not selected backend</text>

  <text x="110" y="458" font-family="Arial, sans-serif" font-size="13" fill="#526071">Source: P1_04 auto_experiment/results.tsv and P1_05 result_registry.yaml. Values are plotted directly from observed rows.</text>
  <text x="110" y="482" font-family="Arial, sans-serif" font-size="13" fill="#526071">Legend must not claim formal performance improvement, real-data generalization, or submission readiness.</text>
</svg>
"""


def main() -> int:
    SVG_PATH.write_text(render(read_rows()), encoding="utf-8")
    print(f"rendered {SVG_PATH.relative_to(NODE_ROOT)} from {DATA_PATH.relative_to(NODE_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
