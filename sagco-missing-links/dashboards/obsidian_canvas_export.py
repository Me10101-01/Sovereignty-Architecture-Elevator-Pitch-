"""
SAGCO → Obsidian Canvas Export
Generates a .canvas file (JSON) for Obsidian visualization.
Separate from kg_builder.py — this one is layout-aware and
places nodes in semantic columns: Bricks | Claims | Verdicts | Gaps

Usage:
  python dashboards/obsidian_canvas_export.py --out sagco.canvas
  python dashboards/obsidian_canvas_export.py --out sagco.canvas --open
"""

from __future__ import annotations
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

REGISTRY = Path(__file__).parent.parent / "registry"

# Canvas layout constants
COL_BRICK   = -900
COL_CLAIM   = -300
COL_VERDICT =  300
COL_GAP     =  900
ROW_START   = -600
ROW_STEP    =  200
NODE_W      =  260
NODE_H      =  80
GAP_H       =  60


VERDICT_COLORS: dict[str, str] = {
    "PROVEN":    "6",   # green
    "PROMISING": "3",   # yellow
    "UNPROVEN":  "4",   # gray/blue
    "INFLATED":  "1",   # red
    "OPEN":      "5",   # purple
}

CLAIMS = [
    {"id": "SAGCO-GRAPH-001",      "project": "sagco-missing-links",   "verdict": "PROVEN",    "coverage": 250.0,
     "text": "SAGCO graph exceeds value of any single component",
     "gaps": []},
    {"id": "RENKO-VAL-001",        "project": "sagco-node-renko",       "verdict": "INFLATED",  "coverage": 0.0,
     "text": "Renko project worth $55k+ in market value",
     "gaps": ["No market transaction", "No comparable sales"]},
    {"id": "RENKO-PORTFOLIO-001",  "project": "sagco-node-renko",       "verdict": "PROVEN",    "coverage": 100.0,
     "text": "Renko strategies improve risk-adjusted returns",
     "gaps": []},
    {"id": "ERU-FOUNDATIONAL-001", "project": "sagco-true",             "verdict": "PROVEN",    "coverage": 100.0,
     "text": "ERU is the universal training format",
     "gaps": []},
    {"id": "CHESS-STACK-001",      "project": "sagco-chess-stack",      "verdict": "PROVEN",    "coverage": 100.0,
     "text": "640-node grid forms a closed loop — QED",
     "gaps": []},
    {"id": "HP-NODE-001",          "project": "sagco-node-hp",          "verdict": "PROMISING", "coverage": 75.0,
     "text": "HP AMD node is operational sovereign compute",
     "gaps": ["ML-PROBE-001: live probe not run"]},
    {"id": "TRADE-SIM-001",        "project": "sagco-trade-simulator",  "verdict": "PROMISING", "coverage": 50.0,
     "text": "Dividend Capture + Trend Following positive EV",
     "gaps": ["Simulation only — no live trades"]},
    {"id": "TRADE-SIM-002",        "project": "sagco-trade-simulator",  "verdict": "INFLATED",  "coverage": 0.0,
     "text": "Renko Mean Reversion viable at WR=48%",
     "gaps": ["AB-OVERFIT-001: EV=-$11.23, PF=0.76"]},
    {"id": "RENKO-SIGNAL-001",     "project": "sagco-node-renko",       "verdict": "OPEN",      "coverage": 0.0,
     "text": "Renko reduces false reversals ≥20% vs candles",
     "gaps": ["ML-DATASET-001: no dataset yet"]},
]

BRICKS = [
    "sagco-missing-links",
    "sagco-node-renko",
    "sagco-true",
    "sagco-chess-stack",
    "sagco-node-hp",
    "sagco-trade-simulator",
]


def make_id(prefix: str, suffix: str) -> str:
    return f"{prefix}-{suffix}".replace(" ", "-")[:32]


def build_canvas(claims: list[dict], bricks: list[str]) -> dict:
    nodes: list[dict] = []
    edges: list[dict] = []

    # ── Brick column ──────────────────────────────────────────────────────────
    for i, brick in enumerate(bricks):
        y = ROW_START + i * ROW_STEP
        nodes.append({
            "id":     f"brick-{i}",
            "type":   "text",
            "text":   f"**{brick}**\nbrick",
            "x":      COL_BRICK,
            "y":      y,
            "width":  NODE_W,
            "height": NODE_H,
            "color":  "2",   # blue
        })

    # ── Claim column ─────────────────────────────────────────────────────────
    for i, claim in enumerate(claims):
        y = ROW_START + i * ROW_STEP
        color = VERDICT_COLORS.get(claim["verdict"], "4")
        node_id = f"claim-{i}"
        verdict = claim["verdict"]
        cov = claim["coverage"]
        nodes.append({
            "id":     node_id,
            "type":   "text",
            "text":   f"**{claim['id']}**\n{claim['text']}\n_{verdict} {cov:.0f}%_",
            "x":      COL_CLAIM,
            "y":      y,
            "width":  NODE_W + 40,
            "height": NODE_H + 20,
            "color":  color,
        })

        # Edge: brick → claim
        brick_idx = next(
            (j for j, b in enumerate(bricks) if b == claim["project"]),
            0
        )
        edges.append({
            "id":       f"e-brick{brick_idx}-claim{i}",
            "fromNode": f"brick-{brick_idx}",
            "fromSide": "right",
            "toNode":   node_id,
            "toSide":   "left",
            "label":    "makes_claim",
        })

        # ── Verdict column ────────────────────────────────────────────────────
        verdict_id = f"verdict-{i}"
        nodes.append({
            "id":     verdict_id,
            "type":   "text",
            "text":   f"**{verdict}**\n{cov:.0f}% coverage",
            "x":      COL_VERDICT,
            "y":      y,
            "width":  NODE_W - 20,
            "height": NODE_H,
            "color":  color,
        })
        edges.append({
            "id":       f"e-claim{i}-verdict{i}",
            "fromNode": node_id,
            "fromSide": "right",
            "toNode":   verdict_id,
            "toSide":   "left",
            "label":    "has_verdict",
        })

        # ── Gap column ────────────────────────────────────────────────────────
        for j, gap in enumerate(claim.get("gaps", [])):
            gap_id = f"gap-{i}-{j}"
            gap_y  = y + j * GAP_H
            nodes.append({
                "id":     gap_id,
                "type":   "text",
                "text":   f"⚠ {gap}",
                "x":      COL_GAP,
                "y":      gap_y,
                "width":  NODE_W + 40,
                "height": GAP_H - 10,
                "color":  "1",  # red
            })
            edges.append({
                "id":       f"e-verdict{i}-gap{j}",
                "fromNode": verdict_id,
                "fromSide": "right",
                "toNode":   gap_id,
                "toSide":   "left",
                "label":    "gap",
            })

    return {"nodes": nodes, "edges": edges}


def write_canvas(canvas: dict, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(canvas, f, indent=2)
    print(f"  Canvas written → {out_path}")
    print(f"  Nodes: {len(canvas['nodes'])} | Edges: {len(canvas['edges'])}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export SAGCO to Obsidian Canvas")
    parser.add_argument("--out", default="sagco.canvas", help="Output .canvas file path")
    parser.add_argument("--open", action="store_true", help="Open in Obsidian after export")
    args = parser.parse_args()

    canvas = build_canvas(CLAIMS, BRICKS)
    out = Path(args.out)
    write_canvas(canvas, out)

    print(f"\n  SAGCO Canvas — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  {len(BRICKS)} bricks | {len(CLAIMS)} claims")

    if args.open:
        try:
            subprocess.run(["open", str(out)], check=False)
        except FileNotFoundError:
            print("  (Could not auto-open — open the .canvas file in Obsidian manually)")


if __name__ == "__main__":
    main()
