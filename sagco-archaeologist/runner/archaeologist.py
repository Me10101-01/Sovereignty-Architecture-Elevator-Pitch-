"""
SAGCO Archaeologist — Orchestrator

Runs all 6 agents in dependency order:
  Agent_001 (origin) + Agent_002 (evolution) + Agent_003 (evidence)  [parallel-safe]
       ↓
  Agent_004 (skeptic) — needs origin + evidence
       ↓
  Agent_005 (novelty) — needs skeptic + evolution
       ↓
  Agent_006 (seal)    — needs all 5

Returns the sealed manifest path + aggregate verdict.
"""

import os
import sys
from pathlib import Path

# Allow running from any directory
_HERE = Path(__file__).parent.parent
sys.path.insert(0, str(_HERE))

from agents import origin_agent, evolution_agent, evidence_agent
from agents import skeptic_agent, novelty_agent, seal_agent


def audit(
    artifact_path: str,
    repo_root: str,
    logs_dir: str = "logs",
    out_dir: str = "reports",
    prior_art_db: str = None,
    verbose: bool = False,
) -> dict:
    """
    Full 6-agent pipeline for one artifact.

    artifact_path : relative path from repo_root
    repo_root     : absolute path to git repo root
    logs_dir      : SAGCO logs directory (absolute or relative to cwd)
    out_dir       : where reports are written
    prior_art_db  : path to prior_art_db.yaml (defaults to registry/)
    verbose       : print progress to stdout
    """

    def log(msg: str):
        if verbose:
            print(f"  [ARCH] {msg}")

    log(f"Auditing: {artifact_path}")

    # Phase 1 — independent agents
    log("Agent_001: Origin Finder …")
    origin = origin_agent.run(artifact_path, repo_root, logs_dir)
    log(f"  → {origin['verdict']}  earliest={origin.get('earliest','?')}")

    log("Agent_002: Evolution Tracker …")
    evolution = evolution_agent.run(artifact_path, repo_root)
    log(f"  → {evolution['verdict']}  commits={evolution['total_commits']}")

    log("Agent_003: Evidence Correlator …")
    evidence = evidence_agent.run(artifact_path, repo_root, logs_dir)
    log(f"  → {evidence['verdict']}  sources={evidence['sources_found']}/{evidence['sources_checked']}")

    # Phase 2 — skeptic (depends on origin + evidence)
    log("Agent_004: Prior-Art Honesty …")
    skeptic = skeptic_agent.run(
        origin_result=origin,
        evidence_result=evidence,
        db_path=prior_art_db,
    )
    log(f"  → discipline={skeptic['skeptic_discipline']}  novel_claims={len(skeptic['novel_claims'])}")

    # Phase 3 — novelty (depends on skeptic + evolution)
    log("Agent_005: Novelty Detector …")
    novelty = novelty_agent.run(
        skeptic_result=skeptic,
        evolution_result=evolution,
    )
    log(f"  → {novelty['verdict']}  classification={novelty['overall_classification']}")

    # Phase 4 — seal + report
    log("Agent_006: Timeline Builder + Seal …")
    sealed = seal_agent.run(
        origin_result=origin,
        evolution_result=evolution,
        evidence_result=evidence,
        skeptic_result=skeptic,
        novelty_result=novelty,
        out_dir=out_dir,
        artifact_path=artifact_path,
    )
    log(f"  → {sealed['aggregate_verdict']}  manifest={sealed['manifest_path']}")
    log(f"     SHA-256: {sealed['manifest_sha256']}")

    return sealed


def audit_multiple(
    artifact_paths: list[str],
    repo_root: str,
    logs_dir: str = "logs",
    out_dir: str = "reports",
    prior_art_db: str = None,
    verbose: bool = True,
) -> list[dict]:
    """Run audit() on a list of artifacts."""
    results = []
    for path in artifact_paths:
        try:
            result = audit(path, repo_root, logs_dir, out_dir, prior_art_db, verbose)
            results.append(result)
        except Exception as e:
            results.append({
                "artifact": path,
                "error": str(e),
                "aggregate_verdict": "FAILED_COMPUTE",
            })
    return results
