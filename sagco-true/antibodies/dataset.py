"""
AB-DATASET-HOARDING-001

trigger:  Downloading datasets before defining claims
cause:    Collecting data faster than defining experiments
remedy:   Every dataset must answer a claim
severity: LOW

Because 100 datasets with no claims = 100 answers to questions you never asked.
"""

from __future__ import annotations
from .detector import Antibody, AntibodyResult


def _detect_dataset_hoarding() -> bool:
    return False   # passive — fire explicitly


def _heal_dataset_hoarding() -> bool:
    print()
    print("  AB-DATASET-HOARDING-001 — Remedy")
    print()
    print("  Every dataset must answer a claim.")
    print()
    print("  Before downloading any dataset, define:")
    print()
    print("  claim_id:  [e.g. RENKO-SIGNAL-001]")
    print("  claim:     Renko improves signal quality over raw candles")
    print("  dataset:   AAPL daily OHLC (Kaggle / yfinance)")
    print("  expected:  Renko reduces false reversals by ≥20%")
    print("  actual:    [measure after experiment]")
    print("  variance:  [compute]")
    print("  verdict:   PASS / FAIL")
    print()
    print("  Format (claims.yaml):")
    print("    - id: RENKO-SIGNAL-001")
    print("      dataset: aapl_ohlc.csv")
    print("      expected: reversals_renko < reversals_candle × 0.8")
    print("      actual: TBD")
    print("      verdict: OPEN")
    print()
    print("  The organism learns from experiments, not downloads.")
    print()
    return True


DATASET_HOARDING_ANTIBODY = Antibody(
    name      = "AB-DATASET-HOARDING-001",
    detect    = _detect_dataset_hoarding,
    message   = "Dataset downloaded without a defined claim. What question does this data answer?",
    heal      = _heal_dataset_hoarding,
    heal_desc = "Printed claim-first dataset template",
)


def fire_dataset_antibody() -> AntibodyResult:
    r = DATASET_HOARDING_ANTIBODY.run()
    r.triggered = True
    r.healed    = True
    _heal_dataset_hoarding()
    return r
