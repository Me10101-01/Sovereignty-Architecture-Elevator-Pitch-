"""
AB-VALUATION-ASSUMPTION-001

trigger:  "Project valuation computed from estimated savings"
cause:    Savings ≠ Market Value
remedy:   Separate development cost, replacement cost,
          business value, and market value

These are four different numbers. Conflating them is the antibody trigger.
"""

from __future__ import annotations
from .detector import Antibody, AntibodyResult

# ── Sentinel values that indicate an assumption is being made ─────────────────

_ASSUMPTION_PHRASES = [
    "worth",
    "valued at",
    "market value",
    "saves",
    "ROI",
    "return on investment",
    "estimated value",
]


def _detect_valuation_assumption() -> bool:
    # Passive antibody — always returns False at runtime (no env to scan).
    # Activated explicitly via: sagco eru valuation
    # or when a ValuationFrame is built with market_value set but no market_evidence.
    return False


def _heal_valuation_assumption() -> bool:
    # Remedy: print the 4-pillar separation guide.
    print()
    print("  AB-VALUATION-ASSUMPTION-001 — Remedy")
    print()
    print("  Savings ≠ Market Value. Separate all four pillars:")
    print()
    print("  [1] Development Cost   = hours × rate")
    print("      (what you spent building it)")
    print()
    print("  [2] Replacement Cost   = engineers × hours × rate")
    print("      (what it costs someone else to rebuild)")
    print()
    print("  [3] Business Value     = estimated impact (time, cost, capability)")
    print("      (could exceed build cost — or not)")
    print()
    print("  [4] Market Value       = what someone will actually pay")
    print("      NOT: what it cost")
    print("      NOT: what it should be worth")
    print("      PROVEN BY: users, comparables, transactions")
    print()
    print("  Run: sagco eru valuation  — to assess any project claim")
    print()
    return True


VALUATION_ANTIBODY = Antibody(
    name    = "AB-VALUATION-ASSUMPTION-001",
    detect  = _detect_valuation_assumption,
    message = (
        "Valuation claim detected without 4-pillar separation. "
        "Savings ≠ Market Value. "
        "Run: sagco eru valuation"
    ),
    heal      = _heal_valuation_assumption,
    heal_desc = "Printed 4-pillar valuation separation guide",
)


def fire_valuation_antibody() -> AntibodyResult:
    """Manually fire the valuation antibody and apply remedy."""
    result = VALUATION_ANTIBODY.run()
    # Force trigger so the heal runs
    result.triggered = True
    result.healed    = True
    _heal_valuation_assumption()
    return result
