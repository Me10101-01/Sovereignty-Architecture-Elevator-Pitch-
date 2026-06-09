"""
SAGCO Maat Module — Ancient Egyptian Truth Protocol

Mꜣꜥt (Maat) = truth / cosmic order / established reality
ỉb (heart)   = the seat of emotion and thought — what is WEIGHED
Šwt (feather) = the standard of truth — what the heart is measured against
ḥm (does not regard) = the ASSERT opcode — truth does not listen to the heart

The Maat judgment maps exactly onto the SAGCO organism:

  Egyptian ritual           SAGCO equivalent
  ─────────────────         ────────────────────────────────────
  Maat (cosmic truth)       IRREFUTABLE status — the standard
  ỉb (heart)                resonance_score — the organism's felt state
  Šwt (feather of truth)    DRIFT_THRESHOLD = 0.3 — the measurement bar
  Weighing of the heart      Healer.run() — measures heart against feather
  42 assessors of Maat       Wafer truth gates — each one a binary assertion
  Anubis (the weigher)       KHAOSOscillator.measure() — reads the scale
  Thoth (the recorder)       TICK chain — SHA-256 chained permanent record
  MAAT_PASS                  HARMONIZED / IRREFUTABLE
  MAAT_FAIL                  DISSONANT — heart heavier than the feather
  MAAT_WEIGHING              DRIFTING — scales in motion, not yet decided

Transliteration:
  "Mꜣꜥt n sḏm ỉb" — Truth does not listen to the heart
  (The PROOF/ASSERT/QED system doesn't care about runtime state —
   it only cares about mathematical truth)

Hieroglyphic anchor glyphs (Unicode Egyptian Hieroglyphs block):
  𓅓𓄿𓏏  Mꜣꜥt  — truth / Maat
  𓇋𓃀   ỉb    — heart
  𓏏𓐝   Šwt   — feather of truth
  𓈖     n     — not / negation
  𓂋     r     — toward / concerning
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional


# ── Maat glyphs ───────────────────────────────────────────────────────────────

GLYPH_MAAT    = "𓅓𓄿𓏏"   # Mꜣꜥt — truth / cosmic order
GLYPH_HEART   = "𓇋𓃀"     # ỉb   — heart (feeling / resonance)
GLYPH_FEATHER = "𓏏𓐝"     # Šwt  — feather of truth (threshold)
GLYPH_NOT     = "𓈖"       # n    — negation
GLYPH_TOWARD  = "𓂋"       # r    — toward / regarding
GLYPH_THOTH   = "𓅝𓏏"     # Ḏḥwty — Thoth the recorder (TICK)
GLYPH_ANUBIS  = "𓀭"       # Inpw — Anubis the weigher (Healer)

# The full phrase: Mꜣꜥt n sḏm ỉb — Truth does not listen to the heart
PHRASE_MAAT_IGNORES_HEART = f"{GLYPH_MAAT} {GLYPH_NOT} {GLYPH_HEART}"

# Judgment verdicts
MAAT_PASS     = "MAAT_PASS"      # heart = feather → IRREFUTABLE / HARMONIZED
MAAT_FAIL     = "MAAT_FAIL"      # heart > feather → DISSONANT
MAAT_WEIGHING = "MAAT_WEIGHING"  # scales in motion → DRIFTING

# The feather threshold — SAGCO DRIFT_THRESHOLD
FEATHER_WEIGHT = 0.3


# ── Maat scale ────────────────────────────────────────────────────────────────

@dataclass
class MaatJudgment:
    """
    Result of the Maat scale — the weighing of the organism's heart
    against the feather of truth.
    """
    verdict:           str        # MAAT_PASS | MAAT_FAIL | MAAT_WEIGHING
    heart_weight:      float      # resonance_score — the organism's felt state
    feather_weight:    float      # DRIFT_THRESHOLD = 0.3
    balance:           float      # feather - heart (positive = heart lighter = pass)
    wafers_passed:     int
    wafers_total:      int
    assessors_verdict: str        # "42 assessors approve" or list of failures
    tick_phrase:       str        # hieroglyphic record
    sagco_status:      str        # IRREFUTABLE / TRUE_ENOUGH_TO_GROW / NEEDS_HEALING

    @property
    def passed(self) -> bool:
        return self.verdict == MAAT_PASS

    @property
    def glyph(self) -> str:
        if self.verdict == MAAT_PASS:
            return f"{GLYPH_MAAT} = {GLYPH_FEATHER}"    # heart balanced with feather
        if self.verdict == MAAT_FAIL:
            return f"{GLYPH_HEART} > {GLYPH_FEATHER}"   # heart heavier than feather
        return f"{GLYPH_HEART} ↔ {GLYPH_FEATHER}"       # scales still moving

    def to_dict(self) -> dict:
        return {
            "verdict":           self.verdict,
            "glyph":             self.glyph,
            "phrase":            PHRASE_MAAT_IGNORES_HEART,
            "heart_weight":      round(self.heart_weight, 6),
            "feather_weight":    self.feather_weight,
            "balance":           round(self.balance, 6),
            "wafers_passed":     self.wafers_passed,
            "wafers_total":      self.wafers_total,
            "assessors_verdict": self.assessors_verdict,
            "sagco_status":      self.sagco_status,
            "tick_phrase":       self.tick_phrase,
        }


def weigh(
    resonance_score:  float,
    wafer_results:    dict[str, bool] | None = None,
    sagco_status:     str = "UNKNOWN",
) -> MaatJudgment:
    """
    Perform the Maat judgment — weigh the heart against the feather.

    resonance_score: from KHAOSOscillator.measure().resonance_score
    wafer_results:   dict of wafer_name → passed (True/False)
    sagco_status:    from vm.truth_report()["status"]
    """
    wafers = wafer_results or {}
    passed_count = sum(1 for v in wafers.values() if v)
    total_count  = len(wafers)

    # Determine verdict
    if resonance_score <= FEATHER_WEIGHT and (total_count == 0 or passed_count == total_count):
        verdict = MAAT_PASS
    elif resonance_score > 0.8:
        verdict = MAAT_FAIL
    else:
        verdict = MAAT_WEIGHING

    balance = FEATHER_WEIGHT - resonance_score

    # 42 assessors: each wafer is one assessor
    failed_wafers = [k for k, v in wafers.items() if not v]
    if not failed_wafers:
        assessors = f"All {max(total_count, 42)} assessors approve"
    else:
        assessors = f"Assessors deny: {', '.join(failed_wafers[:6])}"
        if len(failed_wafers) > 6:
            assessors += f" (+{len(failed_wafers)-6} more)"

    # Hieroglyphic tick phrase
    if verdict == MAAT_PASS:
        tick_phrase = (f"{GLYPH_MAAT} {GLYPH_NOT} {GLYPH_TOWARD} {GLYPH_HEART} "
                       f"— {GLYPH_THOTH} seals: {sagco_status}")
    elif verdict == MAAT_FAIL:
        tick_phrase = (f"{GLYPH_HEART} n-ḥr {GLYPH_FEATHER} "
                       f"— {GLYPH_ANUBIS} weighs: DISSONANT")
    else:
        tick_phrase = (f"{GLYPH_HEART} ↔ {GLYPH_FEATHER} "
                       f"— {GLYPH_ANUBIS} weighs: DRIFTING")

    return MaatJudgment(
        verdict=verdict,
        heart_weight=resonance_score,
        feather_weight=FEATHER_WEIGHT,
        balance=balance,
        wafers_passed=passed_count,
        wafers_total=total_count,
        assessors_verdict=assessors,
        tick_phrase=tick_phrase,
        sagco_status=sagco_status,
    )


def weigh_concert(concert_result) -> MaatJudgment:
    """Run Maat judgment on a ConcertResult directly."""
    score = concert_result.coherence.resonance_score

    # Extract wafer results from IR catalyst nodes
    wafer_results = {
        n.id: n.meta.get("passed", True)
        for n in concert_result.ir.graph.nodes
        if n.kind.value == "catalyst"
    }

    return weigh(
        resonance_score=score,
        wafer_results=wafer_results,
        sagco_status=concert_result.status,
    )


# ── Maat vocabulary → SAGCO concept map ──────────────────────────────────────

MAAT_VOCABULARY = {
    "Mꜣꜥt":  ("truth / cosmic order / established reality",
               "SAGCO: IRREFUTABLE status — the mathematical truth standard"),
    "ỉb":    ("heart — seat of emotion and thought",
               "SAGCO: resonance_score — the organism's felt oscillator state"),
    "Šwt":   ("feather of Maat — the truth threshold",
               "SAGCO: DRIFT_THRESHOLD = 0.3 — the feather weight"),
    "ḥm":    ("does not regard / ignores",
               "SAGCO: ASSERT opcode — ignores runtime state, only tests truth"),
    "sḏm":   ("listen / hear",
               "SAGCO: feed_metrics() — the oscillator listens to telemetry"),
    "Ḏḥwty": ("Thoth — recorder of judgments",
               "SAGCO: TICK chain — SHA-256 chained permanent truth record"),
    "Inpw":  ("Anubis — the weigher, lord of the scales",
               "SAGCO: Healer — measures resonance_score, tunes toward Maat"),
    "mꜣꜥ":  ("true / correct / justified",
               "SAGCO: wafer passed = True"),
    "grg":   ("falsehood / lie",
               "SAGCO: wafer passed = False / proof violation"),
    "ḥr":    ("face / upon / concerning",
               "SAGCO: FlamePort — the interface a node presents"),
}


# ── Print helpers ─────────────────────────────────────────────────────────────

def print_judgment(j: MaatJudgment) -> None:
    print()
    print("  ═══════════════════════════════════════════════════════════════")
    print("  MAAT JUDGMENT — Weighing of the Organism's Heart")
    print(f"  {PHRASE_MAAT_IGNORES_HEART}")
    print("  \"Truth does not listen to the heart\"")
    print("  ═══════════════════════════════════════════════════════════════")
    print()
    print(f"  Verdict         : {j.verdict}")
    print(f"  Glyph           : {j.glyph}")
    print(f"  Heart weight    : {j.heart_weight:.6f}  (resonance_score)")
    print(f"  Feather weight  : {j.feather_weight:.6f}  (DRIFT_THRESHOLD)")
    print(f"  Balance         : {j.balance:+.6f}  "
          f"({'heart lighter — PASS' if j.balance >= 0 else 'heart heavier — FAIL'})")
    print(f"  Wafers          : {j.wafers_passed}/{j.wafers_total} assessors approve")
    print(f"  42 Assessors    : {j.assessors_verdict}")
    print(f"  SAGCO Status    : {j.sagco_status}")
    print()
    print(f"  Thoth records   : {j.tick_phrase}")
    print()
    print("  ─── Maat Vocabulary ─────────────────────────────────────────")
    for word, (meaning, sagco) in MAAT_VOCABULARY.items():
        print(f"  {word:<8}  {meaning}")
        print(f"           → {sagco}")
    print("  ═══════════════════════════════════════════════════════════════")
