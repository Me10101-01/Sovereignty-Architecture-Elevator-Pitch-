"""
SAGCO ERU — Expected Reality Unit

A truth-checking protocol. Fires when a claim is made without evidence.

Structure:
  Claim    → what is being asserted
  Expected → what evidence would be needed to support it
  Actual   → what evidence currently exists
  Variance → the gap (Expected - Actual)
  Verdict  → PROVEN | PROMISING | UNPROVEN | INFLATED

Usage:
  from sagco_true.eru.eru import ERU, ValuationFrame, run_eru
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import json
import time


# ── Verdict ────────────────────────────────────────────────────────────────────

VERDICT_PROVEN    = "PROVEN"
VERDICT_PROMISING = "PROMISING"
VERDICT_UNPROVEN  = "UNPROVEN"
VERDICT_INFLATED  = "INFLATED"


# ── ERU Core ───────────────────────────────────────────────────────────────────

@dataclass
class ERU:
    """Expected Reality Unit — one claim assessed against evidence."""
    claim:       str
    expected:    list[str]           # evidence that would prove the claim
    actual:      list[str]           # evidence that actually exists
    variance:    list[str] = field(default_factory=list)  # gaps auto-computed
    verdict:     str       = VERDICT_UNPROVEN
    notes:       str       = ""
    timestamp:   float     = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not self.variance:
            expected_set = set(self.expected)
            actual_set   = set(self.actual)
            self.variance = sorted(expected_set - actual_set)
        if not self.verdict or self.verdict == VERDICT_UNPROVEN:
            self.verdict = self._auto_verdict()

    def _auto_verdict(self) -> str:
        if not self.expected:
            return VERDICT_UNPROVEN
        coverage = len(self.actual) / len(self.expected)
        if coverage >= 1.0:
            return VERDICT_PROVEN
        if coverage >= 0.5:
            return VERDICT_PROMISING
        if coverage > 0.0:
            return VERDICT_UNPROVEN
        return VERDICT_INFLATED

    def coverage_pct(self) -> float:
        if not self.expected:
            return 0.0
        return round(len(self.actual) / len(self.expected) * 100, 1)

    def report(self) -> str:
        lines = []
        lines.append("")
        lines.append("  ── ERU Assessment ──────────────────────────────────────")
        lines.append(f"  Claim:    {self.claim}")
        lines.append("")
        lines.append("  Expected evidence:")
        for e in self.expected:
            tick = "✓" if e in self.actual else "·"
            lines.append(f"    [{tick}] {e}")
        lines.append("")
        if self.variance:
            lines.append("  Variance (missing evidence):")
            for v in self.variance:
                lines.append(f"    [✗] {v}")
            lines.append("")
        lines.append(f"  Coverage: {self.coverage_pct()}% ({len(self.actual)}/{len(self.expected)})")
        lines.append(f"  Verdict:  {self.verdict}")
        if self.notes:
            lines.append(f"  Notes:    {self.notes}")
        lines.append("  ────────────────────────────────────────────────────────")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "claim":    self.claim,
            "expected": self.expected,
            "actual":   self.actual,
            "variance": self.variance,
            "verdict":  self.verdict,
            "coverage": self.coverage_pct(),
            "notes":    self.notes,
        }


# ── 4-Pillar Valuation Frame ───────────────────────────────────────────────────

@dataclass
class ValuationFrame:
    """
    Separates the four numbers that hide inside any value claim.

    AB-VALUATION-ASSUMPTION-001:
      trigger: "Project valuation computed from estimated savings"
      cause:   Savings ≠ Market Value
      remedy:  Separate all four pillars
    """
    project:          str

    # Pillar 1 — Development Cost
    dev_hours:        float = 0.0
    dev_rate:         float = 0.0    # $/hr

    # Pillar 2 — Replacement Cost
    replacement_engineers: int   = 0
    replacement_hours:     float = 0.0
    replacement_rate:      float = 0.0

    # Pillar 3 — Business Value (estimated)
    business_value_low:  float = 0.0
    business_value_high: float = 0.0
    business_value_basis: str  = ""   # what drives it (time saved, etc.)

    # Pillar 4 — Market Value (what someone will actually pay)
    market_value:       Optional[float] = None
    market_comparables: list[str]       = field(default_factory=list)
    market_evidence:    list[str]       = field(default_factory=list)

    @property
    def development_cost(self) -> float:
        return self.dev_hours * self.dev_rate

    @property
    def replacement_cost(self) -> float:
        return self.replacement_engineers * self.replacement_hours * self.replacement_rate

    @property
    def business_value_midpoint(self) -> float:
        return (self.business_value_low + self.business_value_high) / 2

    def eru(self) -> ERU:
        """Generate an ERU for the valuation claim."""
        claim = f"{self.project} market value = ${self.market_value or self.business_value_high:,.0f}"
        expected = [
            "users or paying customers",
            "performance metrics / backtest results",
            "adoption data",
            "comparable market sales",
            "revenue or cost reduction proof",
        ]
        actual = list(self.market_evidence)
        notes = (
            f"Dev cost ${self.development_cost:,.0f} · "
            f"Replacement ${self.replacement_cost:,.0f} · "
            f"Business value ${self.business_value_low:,.0f}–${self.business_value_high:,.0f}"
        )
        return ERU(claim=claim, expected=expected, actual=actual, notes=notes)

    def report(self) -> str:
        lines = []
        lines.append("")
        lines.append("  ╔══════════════════════════════════════════════════════╗")
        lines.append(f"  ║  ValuationFrame — {self.project:<35}║")
        lines.append("  ╚══════════════════════════════════════════════════════╝")
        lines.append("")

        lines.append(f"  [1] Development Cost")
        lines.append(f"      {self.dev_hours:.0f} hrs × ${self.dev_rate:.0f}/hr = ${self.development_cost:,.0f}")
        lines.append("")

        lines.append(f"  [2] Replacement Cost")
        lines.append(f"      {self.replacement_engineers} engineers × {self.replacement_hours:.0f} hrs × ${self.replacement_rate:.0f}/hr = ${self.replacement_cost:,.0f}")
        lines.append("")

        lines.append(f"  [3] Business Value (estimated)")
        lines.append(f"      ${self.business_value_low:,.0f} – ${self.business_value_high:,.0f}")
        if self.business_value_basis:
            lines.append(f"      Basis: {self.business_value_basis}")
        lines.append("")

        mv = f"${self.market_value:,.0f}" if self.market_value else "NOT YET DETERMINED"
        lines.append(f"  [4] Market Value")
        lines.append(f"      {mv}")
        lines.append(f"      (what someone will actually pay — not cost, not should-be)")
        if self.market_comparables:
            lines.append(f"      Comparables:")
            for c in self.market_comparables:
                lines.append(f"        • {c}")
        if self.market_evidence:
            lines.append(f"      Evidence:")
            for e in self.market_evidence:
                lines.append(f"        ✓ {e}")
        lines.append("")

        lines.append("  ── ERU Check ──────────────────────────────────────────")
        eru = self.eru()
        lines.append(eru.report())

        lines.append("")
        lines.append("  AB-VALUATION-ASSUMPTION-001:")
        lines.append("    trigger: valuation from savings estimate alone")
        lines.append("    remedy:  all 4 pillars must be stated separately")
        lines.append("  ────────────────────────────────────────────────────────")
        return "\n".join(lines)


# ── Built-in ERUs ──────────────────────────────────────────────────────────────

def renko_eru() -> ERU:
    """ERU assessment for RenkoMasterVisualization_AI."""
    return ERU(
        claim="RenkoMasterVisualization_AI worth $55,000+",
        expected=[
            "users or paying customers",
            "backtest performance metrics",
            "adoption / install data",
            "comparable NinjaTrader indicator sales",
            "revenue or documented cost savings",
        ],
        actual=[
            "architecture and codebase (C#, NinjaTrader, Renko)",
            "repo with visualization, data processing, AI integration",
            "portfolio signal: trading + viz + automation + C# in one",
        ],
        notes=(
            "Promising portfolio asset. Valuation not yet proven. "
            "Dev cost ≈ $4k, replacement ≈ $40k, business value $10k–$50k+. "
            "Market value requires user adoption or sale transaction."
        ),
    )


def sagco_graph_eru() -> ERU:
    """ERU assessment for the SAGCO knowledge graph as an asset."""
    return ERU(
        claim="SAGCO knowledge graph exceeds value of any single component",
        expected=[
            "multiple interconnected projects",
            "shared registry / truth layer",
            "cross-project lineage",
            "reusable architecture patterns",
        ],
        actual=[
            "Renko trading system",
            "FlameLang VM (lexer→parser→AST→IR→compiler→bytecode→VM)",
            "Truth Compiler / ERU protocol",
            "KHAOS 72-element registry",
            "Chess Stack 640-node execution grid",
            "SAGCO brick registry (9 bricks)",
            "Excel dashboards + EVM analytics",
            "Postgres schema (Neon)",
            "Obsidian knowledge graph",
            "Primameria Calendar",
        ],
        notes=(
            "Project → Artifact → Lineage → Knowledge System. "
            "The graph is the asset. Each component is a node."
        ),
    )


def run_eru(eru: ERU, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(eru.to_dict(), indent=2))
    else:
        print(eru.report())
