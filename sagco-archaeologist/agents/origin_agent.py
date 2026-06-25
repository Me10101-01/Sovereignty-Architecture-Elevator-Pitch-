"""
Agent_001 — Origin Finder

Finds the absolute earliest provenance signal for an artifact:
  - Earliest git commit touching the file/directory
  - PDF creation date (via pdfinfo, falls back to mtime)
  - Earliest SHA-256 seal entry in logs/
  - Earliest JSONL invocation log entry referencing the artifact

Returns: OriginResult with ERU verdict on how far back we can prove origin.
"""

import os
import subprocess
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


def _run(cmd: list[str], cwd: str = ".") -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=15)
        return r.stdout.strip()
    except Exception:
        return ""


def _git_first_commit(path: str, repo_root: str) -> Optional[dict]:
    """Return the oldest git commit touching path."""
    out = _run(
        ["git", "log", "--all", "--follow", "--diff-filter=A",
         "--format=%H %aI %s", "--", path],
        cwd=repo_root
    )
    if not out:
        # Fall back: oldest commit touching the path at all
        out = _run(
            ["git", "log", "--all", "--follow",
             "--format=%H %aI %s", "--", path],
            cwd=repo_root
        )
    if not out:
        return None
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    if not lines:
        return None
    # oldest = last line (git log newest-first)
    oldest = lines[-1]
    parts = oldest.split(" ", 2)
    return {
        "commit_hash": parts[0] if len(parts) > 0 else "",
        "timestamp":   parts[1] if len(parts) > 1 else "",
        "message":     parts[2] if len(parts) > 2 else "",
    }


def _pdf_creation_date(pdf_path: str) -> Optional[str]:
    """Extract PDF creation date via pdfinfo."""
    out = _run(["pdfinfo", pdf_path])
    for line in out.splitlines():
        if line.lower().startswith("creationdate:"):
            raw = line.split(":", 1)[1].strip()
            return raw
    return None


def _earliest_sha_seal(artifact_name: str, logs_dir: str) -> Optional[dict]:
    """Scan SHA256SUMS files in logs_dir for artifact_name."""
    logs = Path(logs_dir)
    if not logs.exists():
        return None
    earliest_ts = None
    earliest_entry = None
    for f in logs.rglob("SHA256SUMS*"):
        try:
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc).isoformat()
            for line in f.read_text(errors="replace").splitlines():
                if artifact_name in line:
                    if earliest_ts is None or mtime < earliest_ts:
                        earliest_ts = mtime
                        earliest_entry = {"file": str(f), "line": line.strip(), "mtime": mtime}
        except Exception:
            continue
    return earliest_entry


def _earliest_invocation_log(artifact_name: str, logs_dir: str) -> Optional[dict]:
    """Scan JSONL invocation logs for entries referencing artifact_name."""
    logs = Path(logs_dir)
    if not logs.exists():
        return None
    earliest_ts = None
    earliest_entry = None
    for f in logs.rglob("*.log"):
        try:
            for line in f.read_text(errors="replace").splitlines():
                if artifact_name not in line:
                    continue
                try:
                    entry = json.loads(line.split("  sha256=")[0])
                    ts = entry.get("ts", "")
                    if earliest_ts is None or ts < earliest_ts:
                        earliest_ts = ts
                        earliest_entry = {"file": str(f), "entry": entry}
                except Exception:
                    continue
        except Exception:
            continue
    return earliest_entry


def classify_eru(ratio: float) -> str:
    if ratio >= 1.0:
        return "PROVEN"
    if ratio >= 0.5:
        return "PROMISING"
    if ratio >= 0.01:
        return "UNPROVEN"
    return "INFLATED"


def run(artifact_path: str, repo_root: str, logs_dir: str = "logs") -> dict:
    """
    Main entry point for Agent_001.

    artifact_path : path to the file/dir being audited (relative to repo_root)
    repo_root     : absolute path to the git repository root
    logs_dir      : path to SAGCO logs directory (for SHA seals + invocation logs)
    """
    artifact_name = Path(artifact_path).name
    abs_artifact  = os.path.join(repo_root, artifact_path)

    signals = {}

    # 1. Git origin
    git_origin = _git_first_commit(artifact_path, repo_root)
    signals["git_first_commit"] = git_origin

    # 2. PDF date (only if it's a PDF)
    if artifact_path.lower().endswith(".pdf") and os.path.exists(abs_artifact):
        pdf_date = _pdf_creation_date(abs_artifact)
        signals["pdf_creation_date"] = pdf_date
    else:
        signals["pdf_creation_date"] = None

    # 3. File mtime as fallback
    if os.path.exists(abs_artifact):
        mtime = datetime.fromtimestamp(
            Path(abs_artifact).stat().st_mtime, tz=timezone.utc
        ).isoformat()
        signals["mtime"] = mtime
    else:
        signals["mtime"] = None

    # 4. SHA seal in logs
    signals["sha_seal"] = _earliest_sha_seal(artifact_name, logs_dir)

    # 5. Invocation log reference
    signals["invocation_log"] = _earliest_invocation_log(artifact_name, logs_dir)

    # ERU: ratio = (number of distinct provenance signals found) / 5
    found = sum(1 for v in signals.values() if v is not None)
    ratio = found / 5.0
    verdict = classify_eru(ratio)

    # Determine canonical earliest timestamp
    timestamps = []
    if git_origin and git_origin.get("timestamp"):
        timestamps.append(git_origin["timestamp"])
    if signals.get("mtime"):
        timestamps.append(signals["mtime"])
    if signals.get("sha_seal") and signals["sha_seal"].get("mtime"):
        timestamps.append(signals["sha_seal"]["mtime"])
    if signals.get("invocation_log"):
        entry_ts = signals["invocation_log"].get("entry", {}).get("ts")
        if entry_ts:
            timestamps.append(entry_ts)

    earliest = min(timestamps) if timestamps else None

    return {
        "agent":     "Agent_001_OriginFinder",
        "artifact":  artifact_path,
        "signals":   signals,
        "earliest":  earliest,
        "era_ratio": round(ratio, 4),
        "verdict":   verdict,
    }
