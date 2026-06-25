#!/usr/bin/env python3
"""
variance_reporter.py — Aggregate variance report across all decision traces

Reads decision_trace.jsonl, groups by domain+claim_id, computes drift:
  - mean ratio, stddev, min/max
  - trending: IMPROVING | STABLE | DEGRADING
  - antibody candidates: claims with ratio < 0.5 on last 3 entries
"""

import json
import math
from pathlib import Path
from datetime import datetime, timezone

from decision_tracer import load_all, DEFAULT_TRACE

DEFAULT_REPORT = Path(__file__).parent.parent / "reports" / "variance_report.json"


def _mean(vals: list[float]) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _stddev(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / len(vals))


def _trend(vals: list[float]) -> str:
    if len(vals) < 3:
        return "INSUFFICIENT_DATA"
    slope = vals[-1] - vals[0]
    if slope > 0.05:
        return "IMPROVING"
    if slope < -0.05:
        return "DEGRADING"
    return "STABLE"


def build_report(
    trace_path: Path = DEFAULT_TRACE,
    out_path: Path = DEFAULT_REPORT,
) -> dict:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    entries = load_all(trace_path)

    # Group by (domain, claim_id)
    groups: dict[str, list[dict]] = {}
    for e in entries:
        key = f"{e.get('domain', 'sagco')}::{e.get('claim_id', 'unknown')}"
        groups.setdefault(key, []).append(e)

    claims_summary = []
    antibody_candidates = []

    for key, group in sorted(groups.items()):
        domain, claim_id = key.split("::", 1)
        ratios = [e["ratio"] for e in group]

        mean_r  = _mean(ratios)
        std_r   = _stddev(ratios)
        trend   = _trend(ratios)
        last_3  = ratios[-3:]
        degraded = all(r < 0.5 for r in last_3) and len(last_3) >= 1

        entry = {
            "claim_id":    claim_id,
            "domain":      domain,
            "count":       len(ratios),
            "mean_ratio":  round(mean_r, 4),
            "stddev":      round(std_r, 4),
            "min":         round(min(ratios), 4),
            "max":         round(max(ratios), 4),
            "trend":       trend,
            "last_verdict": group[-1]["verdict"],
        }
        claims_summary.append(entry)

        if degraded:
            antibody_candidates.append({
                "id":       f"AB-VARIANCE-{claim_id.upper().replace('-', '_')}",
                "type":     "variance_drift",
                "claim_id": claim_id,
                "domain":   domain,
                "trigger":  f"Last {len(last_3)} ratios all below 0.5: {[round(r,3) for r in last_3]}",
                "msg":      f"Claim {claim_id} is consistently underperforming — review expected value.",
                "severity": "HIGH" if mean_r < 0.25 else "MEDIUM",
            })

    total     = len(entries)
    proven    = sum(1 for e in entries if e.get("verdict") == "PROVEN")
    burn_rate = round(proven / total, 4) if total else 0.0

    report = {
        "generated":           datetime.now(timezone.utc).isoformat(),
        "total_decisions":     total,
        "global_burn_rate":    burn_rate,
        "claims_tracked":      len(claims_summary),
        "antibody_candidates": len(antibody_candidates),
        "claims":              claims_summary,
        "antibodies":          antibody_candidates,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    return report


def print_report(report: dict) -> None:
    print(f"\n  Variance Report  {report['generated'][:19]}")
    print(f"  {'─'*50}")
    print(f"  Total decisions    : {report['total_decisions']}")
    print(f"  Global BurnRate    : {report['global_burn_rate']:.1%}")
    print(f"  Claims tracked     : {report['claims_tracked']}")
    print(f"  Antibody candidates: {report['antibody_candidates']}")
    print()
    print(f"  {'CLAIM':30s} {'MEAN':>6} {'TREND':>12} {'LAST VERDICT':>14}")
    print(f"  {'─'*66}")
    for c in report["claims"]:
        print(f"  {c['claim_id']:30s} {c['mean_ratio']:>6.3f} {c['trend']:>12} {c['last_verdict']:>14}")
    if report["antibodies"]:
        print()
        print(f"  Antibody candidates:")
        for ab in report["antibodies"]:
            print(f"    [{ab['severity']:6s}] {ab['id']} — {ab['trigger'][:60]}")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))

    report = build_report()
    print_report(report)
    print(f"\n  Written to: {DEFAULT_REPORT}")
