"""
Agent_006 — Timeline Builder + Manifest Sealer

Final agent in the pipeline:
  1. Assembles the canonical timeline from all upstream agent outputs
  2. Writes a JSONL manifest — one entry per agent output
  3. SHA-256 seals the entire manifest
  4. Writes a human-readable summary report

ERU ratio = agents_with_proven_or_promising / total_agents
"""

import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _sha256_str(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _extract_timestamp(result: dict) -> Optional[str]:
    """Pull earliest timestamp from an agent result."""
    # origin_agent gives earliest directly
    if "earliest" in result:
        return result["earliest"]
    # evolution_agent gives timeline list
    timeline = result.get("timeline", [])
    if timeline:
        return timeline[0].get("timestamp")
    return None


def _verdict_rank(verdict: str) -> int:
    return {"PROVEN": 3, "PROMISING": 2, "UNPROVEN": 1, "INFLATED": 0}.get(verdict, -1)


def run(
    origin_result:    dict,
    evolution_result: dict,
    evidence_result:  dict,
    skeptic_result:   dict,
    novelty_result:   dict,
    out_dir:          str = "reports",
    artifact_path:    str = "",
) -> dict:
    """
    Agent_006 entry point.

    Takes all upstream agent results, builds sealed manifest, writes report.
    """
    os.makedirs(out_dir, exist_ok=True)

    all_results = [
        origin_result,
        evolution_result,
        evidence_result,
        skeptic_result,
        novelty_result,
    ]

    # Sort timeline events
    timeline_events = []
    for r in all_results:
        ts = _extract_timestamp(r)
        agent = r.get("agent", "unknown")
        verdict = r.get("verdict", r.get("skeptic_discipline", "UNCOMPUTED"))
        if ts:
            timeline_events.append({"timestamp": ts, "agent": agent, "verdict": verdict})

    timeline_events.sort(key=lambda e: e.get("timestamp", ""))

    # ERU aggregate across agents
    verdicts = [
        origin_result.get("verdict", "UNCOMPUTED"),
        evolution_result.get("verdict", "UNCOMPUTED"),
        evidence_result.get("verdict", "UNCOMPUTED"),
        novelty_result.get("verdict", "UNCOMPUTED"),
        # skeptic: use discipline
        skeptic_result.get("skeptic_discipline", "UNCOMPUTED"),
    ]
    proven_count = sum(1 for v in verdicts if v in ("PROVEN", "PROMISING"))
    total_agents = len(verdicts)
    aggregate_ratio = proven_count / total_agents if total_agents > 0 else 0.0

    if aggregate_ratio >= 0.8:
        aggregate_verdict = "PROVEN"
    elif aggregate_ratio >= 0.6:
        aggregate_verdict = "PROMISING"
    elif aggregate_ratio >= 0.2:
        aggregate_verdict = "UNPROVEN"
    else:
        aggregate_verdict = "INFLATED"

    ts_now = datetime.now(tz=timezone.utc).isoformat()
    artifact_name = Path(artifact_path).name if artifact_path else "unknown"

    # Build manifest
    manifest = {
        "sagco_archaeologist_manifest": True,
        "artifact":           artifact_path,
        "generated_at":       ts_now,
        "timeline":           timeline_events,
        "agent_verdicts":     {r.get("agent", f"agent_{i}"): r.get("verdict", r.get("skeptic_discipline", "UNCOMPUTED"))
                               for i, r in enumerate(all_results)},
        "aggregate_ratio":    round(aggregate_ratio, 4),
        "aggregate_verdict":  aggregate_verdict,
        "overall_classification": novelty_result.get("overall_classification", "UNCOMPUTED"),
        "patent_recommendation":  novelty_result.get("patent_recommendation", ""),
        "novel_claims":           skeptic_result.get("novel_claims", []),
        "known_primitives":       skeptic_result.get("known_primitives", []),
        "agent_outputs": {
            "origin":    origin_result,
            "evolution": evolution_result,
            "evidence":  evidence_result,
            "skeptic":   skeptic_result,
            "novelty":   novelty_result,
        },
    }

    # Write JSONL manifest
    safe_name = artifact_name.replace("/", "_").replace("\\", "_")
    manifest_path = os.path.join(out_dir, f"archaeologist_{safe_name}.jsonl")
    manifest_json = json.dumps(manifest, default=str)

    with open(manifest_path, "w") as f:
        f.write(manifest_json + "\n")

    # SHA-256 seal
    seal = _sha256_str(manifest_json)
    seal_path = os.path.join(out_dir, f"archaeologist_{safe_name}.sha256")
    with open(seal_path, "w") as f:
        f.write(f"{seal}  {manifest_path}\n")

    # Human-readable summary
    summary_lines = [
        f"SAGCO ARCHAEOLOGIST — {artifact_path}",
        f"Generated : {ts_now}",
        f"Aggregate : {aggregate_verdict}  (ratio={aggregate_ratio:.2f})",
        f"Classification : {novelty_result.get('overall_classification','?')}",
        f"Patent rec     : {novelty_result.get('patent_recommendation','?')}",
        "",
        "Agent Verdicts:",
    ]
    for r in all_results:
        agent = r.get("agent", "?")
        v = r.get("verdict", r.get("skeptic_discipline", "UNCOMPUTED"))
        ratio = r.get("era_ratio", r.get("novelty_ratio", r.get("skeptic_ratio", "?")))
        summary_lines.append(f"  {agent:<45}  {v}  (ratio={ratio})")

    summary_lines += [
        "",
        f"Novel claims   : {skeptic_result.get('novel_claims',[])}",
        f"Known prims    : {skeptic_result.get('known_primitives',[])}",
        "",
        "Timeline (oldest first):",
    ]
    for ev in timeline_events:
        summary_lines.append(f"  {ev.get('timestamp','?')}  [{ev.get('verdict','?')}]  {ev.get('agent','?')}")

    summary_lines += [
        "",
        f"Manifest : {manifest_path}",
        f"SHA-256  : {seal}",
    ]

    summary_path = os.path.join(out_dir, f"archaeologist_{safe_name}.txt")
    with open(summary_path, "w") as f:
        f.write("\n".join(summary_lines) + "\n")

    return {
        "agent":             "Agent_006_TimelineBuilder",
        "artifact":          artifact_path,
        "manifest_path":     manifest_path,
        "seal_path":         seal_path,
        "summary_path":      summary_path,
        "manifest_sha256":   seal,
        "aggregate_ratio":   round(aggregate_ratio, 4),
        "aggregate_verdict": aggregate_verdict,
        "era_ratio":         round(aggregate_ratio, 4),
        "verdict":           aggregate_verdict,
        "timeline":          timeline_events,
    }
