"""
Agent_003 — Evidence Correlator

Cross-references every provenance signal type for an artifact:
  - Git: commit history hash chain
  - PDF: embedded metadata + text keywords
  - SHA-256: seal log entries
  - Markdown: doc references (links, citations)
  - JSONL: invocation + decision trace logs
  - Patents: US patent number plausibility (grader_006 logic)

ERU ratio = corroborating_sources / total_source_types_checked (7 total)
  Sources that are absent (not just empty) score 0 for that slot.
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import Optional


# --- Patent plausibility (grader_006 inline) --------------------------------

_PATENT_RE = re.compile(r"\bUS\s?(\d{7,8})\b", re.IGNORECASE)

_YEAR_WINDOWS = {
    # approx first serial for patents granted in each decade
    1976: (3_930_000, 4_100_000),
    1980: (4_180_000, 4_350_000),
    1990: (4_900_000, 5_100_000),
    2000: (6_000_000, 6_250_000),
    2010: (7_600_000, 7_900_000),
    2020: (10_500_000, 11_200_000),
    2025: (11_900_000, 12_500_000),
}

def _patent_plausible(num_str: str) -> dict:
    n = int(num_str)
    for decade_start, (lo, hi) in sorted(_YEAR_WINDOWS.items()):
        if lo <= n <= hi:
            return {"number": f"US{n}", "plausible": True,
                    "decade_hint": decade_start, "flag": "PLAUSIBLE"}
    return {"number": f"US{n}", "plausible": False, "flag": "SUSPICIOUS — verify USPTO"}


# --- Source checkers --------------------------------------------------------

def _check_git(artifact_path: str, repo_root: str) -> Optional[dict]:
    try:
        r = subprocess.run(
            ["git", "log", "--all", "--follow", "--oneline", "--", artifact_path],
            capture_output=True, text=True, cwd=repo_root, timeout=15
        )
        commits = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        if not commits:
            return None
        return {"commit_count": len(commits), "sample": commits[:3]}
    except Exception:
        return None


def _check_pdf(artifact_path: str, repo_root: str) -> Optional[dict]:
    abs_path = os.path.join(repo_root, artifact_path)
    if not abs_path.lower().endswith(".pdf") or not os.path.exists(abs_path):
        # check if any PDF in the repo references the artifact name by stem
        stem = Path(artifact_path).stem.lower()
        found = []
        for pdf in Path(repo_root).rglob("*.pdf"):
            try:
                r = subprocess.run(
                    ["pdftotext", str(pdf), "-"],
                    capture_output=True, text=True, timeout=10
                )
                if stem in r.stdout.lower():
                    found.append(str(pdf.relative_to(repo_root)))
            except Exception:
                continue
        return {"referencing_pdfs": found} if found else None

    # it IS a pdf — extract metadata
    try:
        r = subprocess.run(["pdfinfo", abs_path], capture_output=True, text=True, timeout=10)
        meta = {}
        for line in r.stdout.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
        return meta if meta else None
    except Exception:
        return None


def _check_sha_seals(artifact_name: str, logs_dir: str) -> Optional[dict]:
    logs = Path(logs_dir)
    if not logs.exists():
        return None
    entries = []
    for f in logs.rglob("SHA256SUMS*"):
        try:
            for line in f.read_text(errors="replace").splitlines():
                if artifact_name in line:
                    entries.append({"file": str(f), "line": line.strip()})
        except Exception:
            continue
    return {"seal_entries": entries} if entries else None


def _check_markdown(artifact_name: str, repo_root: str) -> Optional[dict]:
    stem = Path(artifact_name).stem.lower()
    references = []
    for md in Path(repo_root).rglob("*.md"):
        try:
            text = md.read_text(errors="replace").lower()
            if stem in text or artifact_name.lower() in text:
                references.append(str(md.relative_to(repo_root)))
        except Exception:
            continue
    return {"markdown_references": references[:10]} if references else None


def _check_jsonl_logs(artifact_name: str, logs_dir: str) -> Optional[dict]:
    logs = Path(logs_dir)
    if not logs.exists():
        return None
    hits = []
    for f in logs.rglob("*.log"):
        try:
            for line in f.read_text(errors="replace").splitlines():
                if artifact_name in line:
                    hits.append({"file": str(f), "line": line[:120]})
        except Exception:
            continue
    return {"log_hits": hits} if hits else None


def _check_patents(artifact_path: str, repo_root: str) -> Optional[dict]:
    """Scan artifact text for US patent numbers; grade each with grader_006 logic."""
    abs_path = os.path.join(repo_root, artifact_path)
    text = ""
    try:
        if abs_path.lower().endswith(".pdf"):
            r = subprocess.run(["pdftotext", abs_path, "-"],
                               capture_output=True, text=True, timeout=10)
            text = r.stdout
        elif os.path.exists(abs_path):
            text = Path(abs_path).read_text(errors="replace")
    except Exception:
        return None

    matches = _PATENT_RE.findall(text)
    if not matches:
        return None
    graded = [_patent_plausible(m) for m in set(matches)]
    return {"patents_found": graded}


def _check_toml_links(artifact_name: str, repo_root: str) -> Optional[dict]:
    """Check sagco-brick.toml files for missing_links referencing artifact domain."""
    stem = Path(artifact_name).stem.lower()
    hits = []
    for toml in Path(repo_root).rglob("sagco-brick.toml"):
        try:
            text = toml.read_text(errors="replace").lower()
            if stem in text:
                hits.append(str(toml.relative_to(repo_root)))
        except Exception:
            continue
    return {"toml_references": hits} if hits else None


# ---------------------------------------------------------------------------

def run(artifact_path: str, repo_root: str, logs_dir: str = "logs") -> dict:
    artifact_name = Path(artifact_path).name

    sources = {
        "git":      _check_git(artifact_path, repo_root),
        "pdf":      _check_pdf(artifact_path, repo_root),
        "sha_seal": _check_sha_seals(artifact_name, logs_dir),
        "markdown": _check_markdown(artifact_name, repo_root),
        "jsonl":    _check_jsonl_logs(artifact_name, logs_dir),
        "patents":  _check_patents(artifact_path, repo_root),
        "toml":     _check_toml_links(artifact_name, repo_root),
    }

    found = sum(1 for v in sources.values() if v is not None)
    ratio = found / len(sources)

    if ratio >= 1.0:
        verdict = "PROVEN"
    elif ratio >= 0.5:
        verdict = "PROMISING"
    elif ratio >= 0.01:
        verdict = "UNPROVEN"
    else:
        verdict = "INFLATED"

    return {
        "agent":    "Agent_003_EvidenceCorrelator",
        "artifact": artifact_path,
        "sources":  sources,
        "sources_found":   found,
        "sources_checked": len(sources),
        "era_ratio": round(ratio, 4),
        "verdict":   verdict,
    }
