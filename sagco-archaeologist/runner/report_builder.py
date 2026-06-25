"""
Report Builder — reads sealed manifests and produces a cross-artifact summary.

Usage:
  python -m runner.report_builder reports/

Output: reports/SAGCO_ARCHAEOLOGIST_SUMMARY.txt
        reports/SAGCO_ARCHAEOLOGIST_SUMMARY.jsonl
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_manifest(path: str) -> dict:
    with open(path) as f:
        return json.loads(f.readline())


def build_summary(reports_dir: str) -> dict:
    manifests = list(Path(reports_dir).glob("archaeologist_*.jsonl"))
    if not manifests:
        return {"error": "No manifests found", "count": 0}

    rows = []
    for m in sorted(manifests):
        try:
            data = load_manifest(str(m))
            rows.append({
                "artifact":            data.get("artifact", "?"),
                "aggregate_verdict":   data.get("aggregate_verdict", "?"),
                "aggregate_ratio":     data.get("aggregate_ratio", 0),
                "classification":      data.get("overall_classification", "?"),
                "patent_rec":          data.get("patent_recommendation", "?"),
                "novel_claims":        data.get("novel_claims", []),
                "manifest":            str(m.name),
            })
        except Exception as e:
            rows.append({"artifact": str(m), "error": str(e)})

    proven   = sum(1 for r in rows if r.get("aggregate_verdict") == "PROVEN")
    promising = sum(1 for r in rows if r.get("aggregate_verdict") == "PROMISING")
    total    = len(rows)
    burn_rate = (proven + promising) / total if total > 0 else 0.0

    ts_now = datetime.now(tz=timezone.utc).isoformat()

    summary = {
        "generated_at":  ts_now,
        "total_artifacts": total,
        "proven":          proven,
        "promising":       promising,
        "burn_rate":       round(burn_rate, 4),
        "rows":            rows,
    }

    # Write summary
    out_txt  = os.path.join(reports_dir, "SAGCO_ARCHAEOLOGIST_SUMMARY.txt")
    out_json = os.path.join(reports_dir, "SAGCO_ARCHAEOLOGIST_SUMMARY.jsonl")

    lines = [
        "SAGCO ARCHAEOLOGIST — CROSS-ARTIFACT SUMMARY",
        f"Generated : {ts_now}",
        f"Artifacts : {total}  |  PROVEN={proven}  PROMISING={promising}",
        f"BurnRate  : {burn_rate:.1%}",
        "",
        f"{'Artifact':<50}  {'Verdict':<12}  {'Ratio':>6}  Classification",
        "-" * 100,
    ]
    for r in rows:
        if "error" in r:
            lines.append(f"  ERROR: {r['artifact']}  {r['error']}")
        else:
            lines.append(
                f"  {r['artifact']:<48}  {r['aggregate_verdict']:<12}  "
                f"{r['aggregate_ratio']:>6.3f}  {r['classification']}"
            )

    lines += [
        "",
        "Novel Claims Across All Artifacts:",
    ]
    all_novel = []
    for r in rows:
        for c in r.get("novel_claims", []):
            if c not in all_novel:
                all_novel.append(c)
    for c in all_novel:
        lines.append(f"  • {c}")

    with open(out_txt, "w") as f:
        f.write("\n".join(lines) + "\n")

    with open(out_json, "w") as f:
        f.write(json.dumps(summary, default=str) + "\n")

    summary["out_txt"]  = out_txt
    summary["out_json"] = out_json
    return summary


if __name__ == "__main__":
    reports_dir = sys.argv[1] if len(sys.argv) > 1 else "reports"
    result = build_summary(reports_dir)
    print(f"Summary written:")
    print(f"  {result.get('out_txt')}")
    print(f"  BurnRate: {result.get('burn_rate', 0):.1%}")
