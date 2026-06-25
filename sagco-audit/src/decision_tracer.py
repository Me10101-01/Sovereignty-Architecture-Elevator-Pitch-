#!/usr/bin/env python3
"""
decision_tracer.py — ERU decision trace with full evidence chain

Every V=A/E computation logs here: expected, actual, ratio, verdict,
SHA-256 of evidence payload. Feeds variance_reporter.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone


DEFAULT_TRACE = Path(__file__).parent.parent / "reports" / "decision_trace.jsonl"

VERDICT_THRESHOLDS = {
    "PROVEN":    (1.0,  float("inf")),   # A/E >= 1.0
    "PROMISING": (0.5,  1.0),            # 0.5 <= A/E < 1.0
    "UNPROVEN":  (0.01, 0.5),            # 0.01 <= A/E < 0.5
    "INFLATED":  (0.0,  0.01),           # A/E < 0.01  (expected was wildly off)
}


def _classify(ratio: float) -> str:
    if ratio >= 1.0:
        return "PROVEN"
    if ratio >= 0.5:
        return "PROMISING"
    if ratio >= 0.01:
        return "UNPROVEN"
    return "INFLATED"


def _sha256_evidence(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def trace_decision(
    claim_id: str,
    expected: float,
    actual: float,
    domain: str = "sagco",
    context: dict | None = None,
    trace_path: Path = DEFAULT_TRACE,
) -> dict:
    """
    Compute V=A/E, classify verdict, append to decision_trace.jsonl.

    Returns the full trace entry.
    """
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    ratio   = actual / expected if expected != 0 else 0.0
    verdict = _classify(ratio)

    evidence = {
        "claim_id": claim_id,
        "expected": expected,
        "actual":   actual,
        "ratio":    round(ratio, 6),
        "domain":   domain,
        "context":  context or {},
    }

    entry = {
        "ts":       datetime.now(timezone.utc).isoformat(),
        "verdict":  verdict,
        "sha256":   _sha256_evidence(evidence),
        **evidence,
    }

    with open(trace_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

    return entry


def load_all(trace_path: Path = DEFAULT_TRACE) -> list[dict]:
    if not trace_path.exists():
        return []
    entries = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def burn_rate(trace_path: Path = DEFAULT_TRACE) -> dict:
    """BurnRate = PROVEN / total across all traces."""
    entries = load_all(trace_path)
    if not entries:
        return {"total": 0, "proven": 0, "burn_rate": 0.0, "by_verdict": {}}

    by_verdict: dict[str, int] = {}
    for e in entries:
        v = e.get("verdict", "UNKNOWN")
        by_verdict[v] = by_verdict.get(v, 0) + 1

    total  = len(entries)
    proven = by_verdict.get("PROVEN", 0)

    return {
        "total":      total,
        "proven":     proven,
        "burn_rate":  round(proven / total, 4) if total else 0.0,
        "by_verdict": by_verdict,
    }


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "burnrate"

    if cmd == "burnrate":
        stats = burn_rate()
        print(f"  Total decisions : {stats['total']}")
        print(f"  Proven          : {stats['proven']}")
        print(f"  BurnRate        : {stats['burn_rate']:.1%}")
        print(f"  By verdict:")
        for v, c in sorted(stats["by_verdict"].items()):
            print(f"    {v:12s}: {c}")

    elif cmd == "trace":
        # trace <claim_id> <expected> <actual> [domain]
        claim_id = sys.argv[2] if len(sys.argv) > 2 else "MANUAL-001"
        expected = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
        actual   = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
        domain   = sys.argv[5] if len(sys.argv) > 5 else "sagco"
        entry    = trace_decision(claim_id, expected, actual, domain)
        print(f"  [{entry['verdict']}] {claim_id}  V={entry['ratio']}  sha256={entry['sha256'][:16]}...")
