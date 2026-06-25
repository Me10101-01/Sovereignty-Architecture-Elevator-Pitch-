"""
Agent_005 — Novelty Detector

Takes Agent_004's "novel_claims" (what the skeptic COULD NOT disprove)
and computes a structured novelty verdict.

Classification:
  KNOWN_PRIMITIVE          — single known technique, no surprise
  KNOWN_COMBINATION        — known parts assembled in a known way
  NOVEL_COMPOSITION        — known parts assembled in an UNKNOWN way (INV-198 class)
  CANDIDATE_INVENTION      — genuinely new mechanism or architecture
  INSUFFICIENT_EVIDENCE    — skeptic couldn't even form a claim

ERU ratio = weighted score:
  CANDIDATE_INVENTION  →  1.0 per claim
  NOVEL_COMPOSITION    →  0.75
  KNOWN_COMBINATION    →  0.25
  KNOWN_PRIMITIVE      →  0.0
  INSUFFICIENT_EVIDENCE → 0.0

This matches INV-198's classification rubric: "Not the components but their
recursive arrangement."
"""

from typing import Optional


_NOVELTY_MARKERS = {
    # Patterns that elevate a claim toward NOVEL_COMPOSITION
    "recursive":          0.5,   # INV-198: recursive verification IS the novelty
    "self-audit":         0.3,
    "mobile-native":      0.2,
    "provenance substrate": 0.4,
    "verifier verifies":  0.5,
    "eru":                0.2,
    "antibody":           0.2,
    "flamelang":          0.3,
    "sagco":              0.1,
    "organism":           0.1,
    "archaeologist":      0.4,
    "swarm":              0.2,
    "bft":                0.2,
    "reflexshell":        0.3,
    "zero-trust":         0.1,
    "decision trace":     0.2,
}


def _score_claim(claim: str, novel_claims: list[str], known_combos: list[str]) -> dict:
    low = claim.lower()

    # If it was NOT in novel_claims, it's known
    if claim in known_combos:
        return {"claim": claim, "classification": "KNOWN_COMBINATION", "weight": 0.25}

    if claim not in novel_claims:
        return {"claim": claim, "classification": "KNOWN_PRIMITIVE", "weight": 0.0}

    # Compute elevation score from novelty markers
    elevation = sum(v for kw, v in _NOVELTY_MARKERS.items() if kw in low)

    if elevation >= 0.5:
        return {"claim": claim, "classification": "CANDIDATE_INVENTION", "weight": 1.0,
                "elevation_score": round(elevation, 3)}
    elif elevation >= 0.2:
        return {"claim": claim, "classification": "NOVEL_COMPOSITION", "weight": 0.75,
                "elevation_score": round(elevation, 3)}
    else:
        # Skeptic couldn't disprove but no strong novelty markers
        return {"claim": claim, "classification": "NOVEL_COMPOSITION", "weight": 0.75,
                "elevation_score": round(elevation, 3), "note": "weak markers — borderline"}


def _aggregate_classification(scored: list[dict]) -> str:
    """Overall artifact classification from individual claim scores."""
    if not scored:
        return "INSUFFICIENT_EVIDENCE"
    classes = [s["classification"] for s in scored]
    if "CANDIDATE_INVENTION" in classes:
        return "CANDIDATE_INVENTION"
    if "NOVEL_COMPOSITION" in classes:
        return "NOVEL_COMPOSITION"
    if "KNOWN_COMBINATION" in classes:
        return "KNOWN_COMBINATION"
    if "KNOWN_PRIMITIVE" in classes:
        return "KNOWN_PRIMITIVE"
    return "INSUFFICIENT_EVIDENCE"


def run(skeptic_result: dict, evolution_result: Optional[dict] = None) -> dict:
    """
    Agent_005 entry point.

    skeptic_result   : output of skeptic_agent.run()
    evolution_result : output of evolution_agent.run() (optional enrichment)
    """
    novel_claims = skeptic_result.get("novel_claims", [])
    known_combos = skeptic_result.get("known_combos", [])
    known_prims  = skeptic_result.get("known_primitives", [])

    # Score every claim the skeptic evaluated
    all_claims = novel_claims + known_combos + known_prims
    scored = [_score_claim(c, novel_claims, known_combos) for c in all_claims]

    # Evolution enrichment: if the artifact has ERU inflections → elevate
    if evolution_result:
        inflections = evolution_result.get("inflections", [])
        eru_inflection = any(
            "FIRST_ERU" in i.get("inflection_tags", []) for i in inflections
        )
        if eru_inflection:
            # Bump any NOVEL_COMPOSITION to CANDIDATE_INVENTION if ERU was baked in early
            for s in scored:
                if s["classification"] == "NOVEL_COMPOSITION":
                    s["classification"] = "CANDIDATE_INVENTION"
                    s["weight"] = 1.0
                    s["elevation_note"] = "elevated by early ERU integration (evolution_agent)"

    if not scored:
        scored.append({
            "claim": "(no claims extracted)",
            "classification": "INSUFFICIENT_EVIDENCE",
            "weight": 0.0,
        })

    # ERU ratio
    total_weight = sum(s["weight"] for s in scored)
    max_possible = len(scored) * 1.0
    ratio = (total_weight / max_possible) if max_possible > 0 else 0.0

    if ratio >= 0.75:
        verdict = "PROVEN"       # strong novelty signal
    elif ratio >= 0.5:
        verdict = "PROMISING"
    elif ratio >= 0.1:
        verdict = "UNPROVEN"
    else:
        verdict = "INFLATED"     # entirely prior art

    overall = _aggregate_classification(scored)

    return {
        "agent":               "Agent_005_NoveltyDetector",
        "artifact":            skeptic_result.get("artifact", ""),
        "claims_scored":       scored,
        "overall_classification": overall,
        "novelty_ratio":       round(ratio, 4),
        "era_ratio":           round(ratio, 4),
        "verdict":             verdict,
        "patent_recommendation": (
            "RECOMMEND UTILITY PATENT — recursive/novel composition detected"
            if overall == "CANDIDATE_INVENTION" else
            "CONSIDER PROVISIONAL — novel composition, not fully novel mechanism"
            if overall == "NOVEL_COMPOSITION" else
            "NO PATENT FILING — prior art or known combination"
        ),
    }
