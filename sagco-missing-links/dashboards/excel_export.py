"""
SAGCO Excel Dashboard Export
Writes claims, verdicts, burnrate, and missing links to .xlsx
Requires: pip install xlsxwriter pyyaml
"""

from __future__ import annotations
import os
import yaml
from pathlib import Path
from datetime import datetime

try:
    import xlsxwriter
except ImportError:
    print("pip install xlsxwriter")
    raise

REGISTRY = Path(__file__).parent.parent / "registry"
OUT_DIR   = Path(__file__).parent.parent / "dashboards"


def load_claims() -> list[dict]:
    p = REGISTRY / "claims.yaml"
    with open(p) as f:
        data = yaml.safe_load(f)
    return data.get("claims", [])


def verdict_color(verdict: str) -> str:
    return {
        "PROVEN":    "#7ED321",
        "PROMISING": "#F5A623",
        "UNPROVEN":  "#9B9B9B",
        "INFLATED":  "#D0021B",
        "OPEN":      "#B8E986",
    }.get(verdict, "#FFFFFF")


def write_dashboard(claims: list[dict], out_path: Path) -> None:
    wb = xlsxwriter.Workbook(str(out_path))

    # ── Formats ──────────────────────────────────────────────────────────────
    header_fmt = wb.add_format({
        "bold": True, "bg_color": "#1A1A2E", "font_color": "#E0E0E0",
        "border": 1, "align": "center", "valign": "vcenter",
    })
    cell_fmt = wb.add_format({"border": 1, "valign": "top", "text_wrap": True})
    pct_fmt  = wb.add_format({"border": 1, "num_format": "0.0%", "align": "center"})
    num_fmt  = wb.add_format({"border": 1, "num_format": "0.0", "align": "center"})

    verdict_fmts: dict[str, object] = {}
    for v, color in {
        "PROVEN": "#7ED321", "PROMISING": "#F5A623",
        "UNPROVEN": "#9B9B9B", "INFLATED": "#D0021B", "OPEN": "#B8E986",
    }.items():
        verdict_fmts[v] = wb.add_format({
            "bold": True, "bg_color": color,
            "font_color": "#FFFFFF" if v in ("INFLATED", "UNPROVEN") else "#000000",
            "border": 1, "align": "center",
        })

    # ── Sheet 1: Claims Summary ───────────────────────────────────────────────
    ws1 = wb.add_worksheet("Claims Summary")
    ws1.set_column("A:A", 26)
    ws1.set_column("B:B", 50)
    ws1.set_column("C:C", 16)
    ws1.set_column("D:D", 14)
    ws1.set_column("E:E", 12)
    ws1.set_column("F:F", 12)
    ws1.set_row(0, 22)

    headers = ["Claim ID", "Claim Text", "Project", "Verdict", "Coverage %", "Gaps"]
    for col, h in enumerate(headers):
        ws1.write(0, col, h, header_fmt)

    for row, c in enumerate(claims, start=1):
        ws1.write(row, 0, c["id"],           cell_fmt)
        ws1.write(row, 1, c["text"],          cell_fmt)
        ws1.write(row, 2, c.get("project", ""), cell_fmt)
        v = c.get("verdict", "OPEN")
        ws1.write(row, 3, v,                  verdict_fmts.get(v, cell_fmt))
        ws1.write(row, 4, c.get("coverage_pct", 0) / 100.0, pct_fmt)
        gaps = c.get("gaps", [])
        ws1.write(row, 5, len(gaps),          num_fmt)

    ws1.autofilter(0, 0, len(claims), len(headers) - 1)

    # ── Sheet 2: BurnRate ─────────────────────────────────────────────────────
    ws2 = wb.add_worksheet("BurnRate")
    ws2.set_column("A:A", 24)
    ws2.set_column("B:B", 14)

    verdicts = [c.get("verdict", "OPEN") for c in claims]
    total    = len(verdicts)
    proven   = verdicts.count("PROVEN")
    promising= verdicts.count("PROMISING")
    unproven = verdicts.count("UNPROVEN")
    inflated = verdicts.count("INFLATED")
    burnrate = proven / total if total else 0.0
    ev       = (proven*1.0 + promising*0.5 + unproven*0.1 - inflated*0.5) / total if total else 0.0

    rows = [
        ("Total Claims",  total),
        ("Proven",        proven),
        ("Promising",     promising),
        ("Unproven",      unproven),
        ("Inflated",      inflated),
        ("BurnRate",      f"{burnrate*100:.1f}%"),
        ("EV / Claim",    f"{ev:.3f}"),
        ("Generated",     datetime.now().strftime("%Y-%m-%d %H:%M")),
    ]
    ws2.write(0, 0, "BurnRate Report", header_fmt)
    ws2.write(0, 1, "Value",           header_fmt)
    for r, (label, val) in enumerate(rows, start=1):
        ws2.write(r, 0, label, cell_fmt)
        ws2.write(r, 1, str(val), cell_fmt)

    # ── Sheet 3: Missing Links ────────────────────────────────────────────────
    ws3 = wb.add_worksheet("Missing Links")
    ws3.set_column("A:A", 20)
    ws3.set_column("B:B", 55)
    ws3.set_column("C:C", 20)

    ml_headers = ["ID", "Description", "Blocks Claim"]
    for col, h in enumerate(ml_headers):
        ws3.write(0, col, h, header_fmt)

    open_claims = [c for c in claims if c.get("verdict") == "OPEN"]
    for row, c in enumerate(open_claims, start=1):
        ml_id = c.get("missing_link", "ML-???-001")
        ws3.write(row, 0, ml_id,    cell_fmt)
        ws3.write(row, 1, c["text"], cell_fmt)
        ws3.write(row, 2, c["id"],  cell_fmt)

    wb.close()
    print(f"  Dashboard written → {out_path}")


def main() -> None:
    claims = load_claims()
    out = OUT_DIR / f"sagco_dashboard_{datetime.now().strftime('%Y%m%d')}.xlsx"
    write_dashboard(claims, out)
    print(f"\n  {len(claims)} claims exported.")
    print(f"  BurnRate: {sum(1 for c in claims if c.get('verdict')=='PROVEN')}/{len(claims)} PROVEN")


if __name__ == "__main__":
    main()
