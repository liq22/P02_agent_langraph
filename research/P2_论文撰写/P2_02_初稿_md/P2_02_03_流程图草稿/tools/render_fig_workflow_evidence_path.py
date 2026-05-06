#!/usr/bin/env python3
"""Render Figure 1 workflow/evidence path as deterministic SVG."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures" / "fig_workflow_evidence_path.svg"


def text(x: int, y: int, value: str, size: int = 16, weight: str = "400") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="#111111">{value}</text>'
    )


def box(x: int, y: int, w: int, h: int, title: str, body: list[str], fill: str) -> str:
    lines = [
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" ry="6" '
        f'fill="{fill}" stroke="#222222" stroke-width="1.4"/>',
        text(x + 18, y + 30, title, 16, "700"),
    ]
    for idx, item in enumerate(body):
        lines.append(text(x + 18, y + 58 + idx * 22, item, 13))
    return "\n".join(lines)


def arrow(x1: int, y1: int, x2: int, y2: int, label: str = "") -> str:
    mid_x = (x1 + x2) // 2
    parts = [
        f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
        'stroke="#111111" stroke-width="1.6" marker-end="url(#arrow)"/>'
    ]
    if label:
        parts.append(text(mid_x - 48, y1 - 9, label, 12, "700"))
    return "\n".join(parts)


def render() -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720" role="img" aria-labelledby="title desc">
<title id="title">Evidence-governed workflow and claim evidence path</title>
<desc id="desc">Workflow schematic showing node authoring, claim registry, evidence gate, independent review, response closure, and bounded manuscript upgrade with a visible negative evidence lane.</desc>
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#111111"/>
  </marker>
</defs>
<rect x="0" y="0" width="1280" height="720" fill="#ffffff"/>
{text(64, 54, "Figure 1. Evidence-governed workflow and claim/evidence path", 24, "700")}
{text(64, 82, "The figure is a schematic provenance map, not evidence of empirical performance.", 14)}

{box(70, 130, 180, 125, "1. Node authoring", ["local manuscript", "prompt assets", "artifact draft"], "#E8EEF7")}
{box(300, 130, 180, 125, "2. Claim identity", ["claim_id", "evidence_id", "protocol_id"], "#E7F2EC")}
{box(530, 130, 180, 125, "3. Evidence gate", ["support_status", "boundary_label", "eligibility rule"], "#FFF1D6")}
{box(760, 130, 180, 125, "4. Review gate", ["independent verdict", "hard-fail check", "score + comments"], "#F3E8F5")}
{box(990, 130, 180, 125, "5. Response close", ["comment response", "downgrade or fix", "node close"], "#EAF4F4")}

{arrow(250, 192, 300, 192, "ids")}
{arrow(480, 192, 530, 192, "gate")}
{arrow(710, 192, 760, 192, "review")}
{arrow(940, 192, 990, 192, "respond")}

{box(185, 350, 215, 120, "Negative evidence lane", ["failed, rejected, unclear", "kept as first-class rows", "never hidden as denominator"], "#F8E1DF")}
{box(520, 350, 240, 120, "Formal result eligibility", ["data alignment", "artifact contract", "repeat + ablation gates"], "#EAE7D6")}
{box(885, 350, 250, 120, "Manuscript upgrade", ["only bounded claims upgrade", "blocked claims stay visible", "no graph/projection truth"], "#E2ECF0")}

{arrow(620, 255, 620, 350, "eligibility")}
{arrow(300, 255, 300, 350, "retain")}
{arrow(760, 410, 885, 410, "upgrade only after gate")}
{arrow(990, 255, 1005, 350, "closed response")}

<line x1="70" y1="300" x2="1170" y2="300" stroke="#666666" stroke-dasharray="6 7" stroke-width="1.2"/>
{text(78, 322, "Top lane: node closure. Bottom lane: evidence preservation and formal-result eligibility.", 13, "700")}

{text(70, 575, "claim_ref: C_WORKFLOW_EVIDENCE_PATH", 14, "700")}
{text(70, 602, "evidence_ref: P2_02_03_FIG_WORKFLOW_MANIFEST + P2_02_outline_map_v1", 14)}
{text(70, 629, "boundary: schematic only; no performance, backend, RM101, Stage C/D, or submission-ready claim.", 14)}
{text(70, 656, "first callout: P2_02_03 docs/manuscript.md, paragraph 1.", 14)}
</svg>
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
