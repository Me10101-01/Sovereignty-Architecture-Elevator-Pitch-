"""
Agent_002 — Evolution Tracker

Reconstructs the version history of an artifact from git:
  - Full commit timeline (hash, author, date, message)
  - Line count delta per commit (growth curve)
  - Rename/move history
  - Identifies structural inflection points (first test, first sha-seal, first ERU keyword)

ERU verdict: ratio = commits_with_eru_keywords / total_commits
  If an artifact evolved without ERU context → UNPROVEN evolution path.
"""

import subprocess
import re
from pathlib import Path
from typing import Optional


_ERU_KEYWORDS = frozenset([
    "eru", "verdict", "proven", "promising", "unproven", "inflated",
    "antibody", "burn_rate", "burnrate", "sha256", "receipt",
])


def _run(cmd: list[str], cwd: str = ".") -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=30)
        return r.stdout.strip()
    except Exception:
        return ""


def _commit_log(artifact_path: str, repo_root: str) -> list[dict]:
    """Full commit log for artifact_path."""
    out = _run(
        ["git", "log", "--all", "--follow",
         "--format=COMMIT|%H|%aI|%an|%s", "--", artifact_path],
        cwd=repo_root,
    )
    commits = []
    for line in out.splitlines():
        if not line.startswith("COMMIT|"):
            continue
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue
        commits.append({
            "hash":      parts[1],
            "timestamp": parts[2],
            "author":    parts[3],
            "message":   parts[4],
        })
    # newest first → reverse to oldest first
    commits.reverse()
    return commits


def _line_count_at(commit_hash: str, artifact_path: str, repo_root: str) -> Optional[int]:
    out = _run(
        ["git", "show", f"{commit_hash}:{artifact_path}"],
        cwd=repo_root,
    )
    if not out:
        return None
    return len(out.splitlines())


def _detect_renames(artifact_path: str, repo_root: str) -> list[str]:
    """Return list of previous names (oldest first)."""
    out = _run(
        ["git", "log", "--all", "--follow", "--name-only", "--format=", "--diff-filter=R",
         "--", artifact_path],
        cwd=repo_root,
    )
    seen = []
    for line in out.splitlines():
        line = line.strip()
        if line and line not in seen and line != artifact_path:
            seen.append(line)
    return seen


def _eru_in_message(msg: str) -> bool:
    low = msg.lower()
    return any(kw in low for kw in _ERU_KEYWORDS)


def _inflection_points(commits: list[dict]) -> list[dict]:
    """Tag special commits: first test, first sha-seal reference, first ERU keyword."""
    inflections = []
    eru_seen = test_seen = sha_seen = False

    for c in commits:
        msg = c["message"].lower()
        tags = []
        if not test_seen and "test" in msg:
            tags.append("FIRST_TEST")
            test_seen = True
        if not sha_seen and ("sha256" in msg or "seal" in msg):
            tags.append("FIRST_SHA_SEAL")
            sha_seen = True
        if not eru_seen and any(kw in msg for kw in ("eru", "verdict", "proven", "antibody")):
            tags.append("FIRST_ERU")
            eru_seen = True
        if tags:
            inflections.append({**c, "inflection_tags": tags})

    return inflections


def run(artifact_path: str, repo_root: str) -> dict:
    commits = _commit_log(artifact_path, repo_root)
    renames = _detect_renames(artifact_path, repo_root)

    total = len(commits)
    eru_commits = sum(1 for c in commits if _eru_in_message(c["message"]))

    # Line count samples: first, midpoint, last
    line_samples = []
    if commits:
        for idx in [0, total // 2, total - 1] if total > 1 else [0]:
            lc = _line_count_at(commits[idx]["hash"], artifact_path, repo_root)
            line_samples.append({
                "commit_index": idx,
                "hash":         commits[idx]["hash"][:8],
                "timestamp":    commits[idx]["timestamp"],
                "line_count":   lc,
            })

    inflections = _inflection_points(commits)

    # ERU ratio: how much of the evolution was ERU-aware?
    ratio = (eru_commits / total) if total > 0 else 0.0

    if ratio >= 1.0:
        verdict = "PROVEN"
    elif ratio >= 0.5:
        verdict = "PROMISING"
    elif ratio >= 0.01:
        verdict = "UNPROVEN"
    else:
        verdict = "INFLATED"

    return {
        "agent":          "Agent_002_EvolutionTracker",
        "artifact":       artifact_path,
        "total_commits":  total,
        "eru_commits":    eru_commits,
        "renames":        renames,
        "line_samples":   line_samples,
        "inflections":    inflections,
        "timeline":       commits,
        "era_ratio":      round(ratio, 4),
        "verdict":        verdict,
    }
