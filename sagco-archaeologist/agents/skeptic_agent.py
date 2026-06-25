"""
Agent_004 — Prior-Art Honesty (The Skeptic)

This agent is MECHANICALLY PESSIMISTIC. It runs before Agent_005 and
tries to DISPROVE every novelty claim. It answers: "Has this been done before?"

Architecture mirrors INV-198's Agent_004:
  "Instead of proving you're right… it tries to prove you're WRONG first."

Logic:
  1. Load prior_art_db.yaml — known primitives + known combinations
  2. For each feature/claim extracted from origin+evidence results:
     a. Match against known primitives  → PRIOR ART EXISTS
     b. Match against known combinations → KNOWN COMBINATION
     c. No match → CANDIDATE NOVELTY
  3. ERU ratio = candidate_novelties / total_claims
     (low ratio = mostly known = good skeptic discipline = PROVEN skepticism)

The skeptic NEVER rounds up. Ambiguous = PRIOR ART.
"""

import re
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


_DEFAULT_DB = Path(__file__).parent.parent / "registry" / "prior_art_db.yaml"


def _load_db(db_path: str) -> dict:
    if yaml is None:
        return {"primitives": [], "combinations": []}
    p = Path(db_path)
    if not p.exists():
        return {"primitives": [], "combinations": []}
    try:
        with open(p) as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {"primitives": [], "combinations": []}


def _extract_claims(origin_result: dict, evidence_result: dict) -> list[str]:
    """
    Synthesize a list of feature/claim strings from upstream agent outputs.
    Each claim is a short lowercase descriptor we try to match against prior-art DB.
    """
    claims = set()

    # From git commit messages
    for commit in origin_result.get("signals", {}).get("git_first_commit") and [] or []:
        pass  # origin gives a single commit dict, not a list

    # Pull keywords from evidence sources
    sources = evidence_result.get("sources", {})

    if sources.get("git"):
        commits = sources["git"].get("sample", [])
        for msg in commits:
            low = msg.lower()
            for kw in ["sha256", "hashlib", "jsonl", "append-only", "ledger",
                       "receipt", "eru", "antibody", "raft", "pbft", "wireguard",
                       "rpki", "asn", "gpg", "git log", "pdftotext",
                       "haversine", "ohm", "bearing", "lexer", "parser", "ast",
                       "dispatch", "router", "decision trace", "variance",
                       "ninja", "ninjascript", "renko", "delta volume"]:
                if kw in low:
                    claims.add(kw)

    if sources.get("markdown"):
        # coarse: if markdown refs exist, artifact touches documented domain
        claims.add("markdown documentation")

    if sources.get("patents"):
        for p in sources["patents"].get("patents_found", []):
            if p.get("plausible"):
                claims.add(f"patent {p['number']}")

    # Always test these structural claims against the DB
    artifact = evidence_result.get("artifact", "")
    if artifact.endswith(".c") or artifact.endswith(".h"):
        claims.add("c language implementation")
    if artifact.endswith(".py"):
        claims.add("python implementation")
    if artifact.endswith(".cs"):
        claims.add("c# implementation")
    if "sha256" in artifact.lower() or "seal" in artifact.lower():
        claims.add("sha256 file hashing")
    if "receipt" in artifact.lower() or "ledger" in artifact.lower():
        claims.add("append-only audit log")
    if "dispatch" in artifact.lower() or "router" in artifact.lower():
        claims.add("command dispatcher pattern")
    if "eru" in artifact.lower():
        claims.add("eru decision scoring")

    return list(claims) if claims else ["general software artifact"]


def _match_primitive(claim: str, primitives: list[dict]) -> Optional[dict]:
    """Return first primitive record whose keywords overlap with claim."""
    for p in primitives:
        keywords = [k.lower() for k in p.get("keywords", [])]
        if any(kw in claim for kw in keywords):
            return p
    return None


def _match_combination(claim: str, combinations: list[dict]) -> Optional[dict]:
    """Return first known-combination record whose keywords overlap with claim."""
    for c in combinations:
        keywords = [k.lower() for k in c.get("keywords", [])]
        if any(kw in claim for kw in keywords):
            return c
    return None


def run(
    origin_result: dict,
    evidence_result: dict,
    db_path: Optional[str] = None,
) -> dict:
    """
    Agent_004 entry point.

    origin_result   : output of origin_agent.run()
    evidence_result : output of evidence_agent.run()
    db_path         : path to prior_art_db.yaml (defaults to registry/)
    """
    db = _load_db(str(db_path or _DEFAULT_DB))
    primitives   = db.get("primitives", [])
    combinations = db.get("combinations", [])

    claims = _extract_claims(origin_result, evidence_result)

    results = []
    candidate_count = 0

    for claim in claims:
        prim = _match_primitive(claim, primitives)
        if prim:
            results.append({
                "claim":   claim,
                "status":  "PRIOR_ART_EXISTS",
                "match":   prim.get("name"),
                "ref":     prim.get("reference", ""),
                "verdict": "UNPROVEN",
            })
            continue

        combo = _match_combination(claim, combinations)
        if combo:
            results.append({
                "claim":   claim,
                "status":  "KNOWN_COMBINATION",
                "match":   combo.get("name"),
                "ref":     combo.get("reference", ""),
                "verdict": "PROMISING",
            })
            continue

        # Nothing found — candidate novelty (skeptic reluctantly admits)
        results.append({
            "claim":   claim,
            "status":  "CANDIDATE_NOVELTY",
            "match":   None,
            "ref":     "",
            "verdict": "PROVEN",
        })
        candidate_count += 1

    total = len(results)
    # Skeptic's own ERU: ratio = how many claims we could NOT disprove / total
    # A GOOD skeptic has LOW ratio here (it found prior art for most things)
    # For the artifact novelty pipeline, we feed candidate_count upstream.
    skeptic_ratio = (candidate_count / total) if total > 0 else 0.0

    # Skeptic verdict on its own work:
    #   PROVEN   = found prior art for nearly everything (disciplined skeptic)
    #   INFLATED = couldn't disprove anything (lazy skeptic / empty DB)
    skeptic_discipline = "PROVEN" if skeptic_ratio <= 0.5 else \
                         "PROMISING" if skeptic_ratio <= 0.75 else \
                         "UNPROVEN" if skeptic_ratio <= 0.95 else "INFLATED"

    return {
        "agent":              "Agent_004_PriorArtHonesty",
        "artifact":           evidence_result.get("artifact", ""),
        "claims_evaluated":   results,
        "total_claims":       total,
        "candidate_novelties":candidate_count,
        "skeptic_ratio":      round(skeptic_ratio, 4),
        "skeptic_discipline": skeptic_discipline,
        # Pass forward for Agent_005
        "novel_claims":       [r["claim"] for r in results if r["status"] == "CANDIDATE_NOVELTY"],
        "known_primitives":   [r["claim"] for r in results if r["status"] == "PRIOR_ART_EXISTS"],
        "known_combos":       [r["claim"] for r in results if r["status"] == "KNOWN_COMBINATION"],
    }
