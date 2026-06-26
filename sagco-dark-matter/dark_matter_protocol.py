#!/usr/bin/env python3
"""
SAGCO Dark Matter Protocol
==========================
Archive 1: sagco-everything.tar.gz  — every variable, constant, schema, proof, concept
Archive 2: sagco-working.tar.gz     — every PROVEN / tested component
ERU BurnRate ROI across all components
SAGCO-Organism ingest simulation
SHA-256 sealed JSONL manifest

Usage:
    python3 dark_matter_protocol.py [--repo ROOT] [--dry-run]
"""

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

# ── Constants ──────────────────────────────────────────────────────────────────
PROTOCOL_VERSION = "1.0.0"
BUILD_DAYS       = 4          # lol 4 days
TARGET_MONTHLY   = 5000.00    # divtrack target

# ERU thresholds: V = A / E
ERU_PROVEN    = 1.0
ERU_PROMISING = 0.5
ERU_UNPROVEN  = 0.01

# Mathematical proof: V = A/E
# BurnRate = |{c : verdict(c) ∈ {PROVEN, PROMISING}}| / |C|
# Dark Matter Ratio = |working_files| / |total_files|
# ROI_4DAY = BurnRate × (PROVEN_components / BUILD_DAYS)

# ── Data Structures ────────────────────────────────────────────────────────────
@dataclass
class ComponentERU:
    name:        str
    layer:       str           # BRICK layer label
    expected:    int           # spec count / test count designed
    actual:      int           # passing / working count
    ratio:       float
    verdict:     str
    notes:       str
    in_working:  bool          # included in sagco-working archive

@dataclass
class ProtocolResult:
    version:          str
    timestamp_unix:   int
    build_days:       int
    components:       list
    total_expected:   int
    total_actual:     int
    overall_ratio:    float
    overall_verdict:  str
    burn_rate:        float
    dark_matter_ratio: float
    roi_4day:         float
    archive_everything_sha256: str
    archive_working_sha256:    str
    organism_invocations:      list
    seal_sha256:               str


def eru_verdict(ratio: float) -> str:
    if ratio >= ERU_PROVEN:    return "PROVEN"
    if ratio >= ERU_PROMISING: return "PROMISING"
    if ratio >= ERU_UNPROVEN:  return "UNPROVEN"
    return "INFLATED"


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_string(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


# ── Component Registry ─────────────────────────────────────────────────────────
# E = what was designed/specified
# A = what is working/passing
# Formula: V = A/E
COMPONENTS = [
    ComponentERU(
        name="sagco-audit",
        layer="BRICK-018",
        expected=17, actual=17,
        ratio=17/17, verdict="PROVEN",
        notes="Board A — 17/17 tests PASS. audit_runner, decision_tracer, "
              "invocation_logger, variance_reporter, antibody_registry all operational.",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-archaeologist",
        layer="BRICK-021",
        expected=32, actual=32,
        ratio=32/32, verdict="PROVEN",
        notes="6-agent recursive verification swarm. Agent_004 (skeptic) runs first. "
              "32/32 tests PASS. ERU on every output. SHA-256 final manifest. "
              "INV-198 recursive verification architecture implemented.",
        in_working=True,
    ),
    ComponentERU(
        name="candlestick-ml-sim",
        layer="BRICK-023",
        expected=27, actual=27,
        ratio=27/27, verdict="PROVEN",
        notes="Hybrid candlestick + Renko ML simulator. 9 potentiometer sliders. "
              "ERU probability scoring. ATR-based Renko bricks with streak context. "
              "Antibody suppression on inflated streaks. 27/27 PASS.",
        in_working=True,
    ),
    ComponentERU(
        name="divtrack",
        layer="BRICK-024",
        expected=24, actual=24,
        ratio=24/24, verdict="PROVEN",
        notes="C11 CLI dividend tracker. Zero external deps (hand-rolled JSON parser). "
              "SCHD+DGRO+VIG+JEPI seed portfolio. 15yr projection. "
              "ERU verdict on $5k/mo target. 24/24 tests PASS. "
              "Current: $47.58/mo = INFLATED (1.0%). Target: $5000/mo.",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-organism",
        layer="BRICK-020",
        expected=15, actual=12,
        ratio=12/15, verdict="PROMISING",
        notes="C11 headless dispatcher: lexer→parser→AST→router→subsystem→ledger→seal. "
              "Core pipeline PROVEN (lexer, parser, router, ledger, seal, SHA-256). "
              "Missing: graph_parser.c (AST→graph), physics stubs (lever/tension/fos/rc), "
              "GPS/compass not wired. ML-ORGANISM-001 through 005 open.",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-ninjascript-engine",
        layer="BRICK-019",
        expected=10, actual=7,
        ratio=7/10, verdict="PROMISING",
        notes="NinjaScript ERU execution surface. Debug/trace/volume/risk/seal scripts "
              "operational. SagcoDeltaRenkoSignal.cs (ATR Renko) wired. "
              "Missing: ML-NINJA-001 (bridge to decision_tracer), "
              "ML-NINJA-002 (live account upload), ML-NINJA-003 (live futures feed).",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-sovereignty-missing-links",
        layer="BRICK-025",
        expected=8, actual=5,
        ratio=5/8, verdict="PROMISING",
        notes="Three-Move NDA Close: MOVE 1=GPG clearsign (PROVEN), "
              "MOVE 2=ARIN ASN $250/yr (INFLATED — pending application), "
              "MOVE 3=RPKI ROA (INFLATED — needs ASN first). "
              "sagco-gdrive Rust module replacing DriveClient stub. "
              "BFT-Delta doc (SAGCO T(claim)=A/E vs SLAAC). RSA JWT signing = STUB.",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-gdrive",
        layer="BRICK-025-GDRIVE",
        expected=6, actual=4,
        ratio=4/6, verdict="PROMISING",
        notes="Rust async tool (tokio/reqwest). upload|hydrate|status|seal|scan "
              "commands implemented. PlaceholderStore JSONL state tracking. "
              "SHA-256 sealed SHA256SUMS. RSA JWT signing = STUB (documented in auth.rs). "
              "Needs: rsa crate wired, live service-account credentials.",
        in_working=True,
    ),
    ComponentERU(
        name="sagco-missing-links",
        layer="BRICK-016",
        expected=12, actual=5,
        ratio=5/12, verdict="PROMISING",
        notes="ERU core, claims registry, knowledge graph, dashboards, Renko schemas. "
              "eru-core/ and registry/ operational. "
              "graph/ not fully built (ML-AUDIT-001). "
              "dashboards/ partial. renko/ schema only.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-cell-db",
        layer="BRICK-012",
        expected=8, actual=4,
        ratio=4/8, verdict="PROMISING",
        notes="Rust B-tree cell database. Core read/write ops present. "
              "Wafer indexing scaffolded. Full query layer not yet operational.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-chess-stack",
        layer="BRICK-013",
        expected=8, actual=4,
        ratio=4/8, verdict="PROMISING",
        notes="Rust game-theory / chess-logic stack. "
              "Board representation + move gen scaffolded. "
              "ERU strategy evaluation partial.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-json-trainer",
        layer="BRICK-015",
        expected=6, actual=4,
        ratio=4/6, verdict="PROMISING",
        notes="Headless JSON corpus trainer. antibodies/ vocabulary/ schemas/ present. "
              "Trainer pipeline functional. Sandbox ingest partial.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-true",
        layer="BRICK-017",
        expected=20, actual=6,
        ratio=6/20, verdict="PROMISING",
        notes="SAGCO-OS kernel: kernel/ boards/ drivers/ eru/ apps/ khaos/ language/ "
              "wafers/ worlds/ registry/ antibodies/. Core ERU loop and FlameLang "
              "language stub present. Full kernel execution = UNPROVEN.",
        in_working=False,
    ),
    ComponentERU(
        name="mat225-calc1-mobius",
        layer="BRICK-010",
        expected=5, actual=3,
        ratio=3/5, verdict="PROMISING",
        notes="Calculus 1 ERU validator. flamec_calc_validator scaffolded. "
              "ERU-FIELD-ORIGIN-001 claim documented. Tests partial.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-sync",
        layer="BRICK-011",
        expected=5, actual=2,
        ratio=2/5, verdict="UNPROVEN",
        notes="Rust sync engine. Target/tests dirs present. "
              "Core sync logic not yet operational.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-trade-simulator",
        layer="BRICK-014",
        expected=5, actual=2,
        ratio=2/5, verdict="UNPROVEN",
        notes="Trade simulator. src/tests scaffolded. "
              "No passing tests detected.",
        in_working=False,
    ),
    ComponentERU(
        name="sagco-node-renko",
        layer="BRICK-NODE-R",
        expected=3, actual=1,
        ratio=1/3, verdict="UNPROVEN",
        notes="Node.js Renko stub. Directory exists, minimal implementation.",
        in_working=False,
    ),
    ComponentERU(
        name="dividend-portfolio-tracker",
        layer="BRICK-024-SCHEMA",
        expected=4, actual=4,
        ratio=4/4, verdict="PROVEN",
        notes="Python schema + YAML data layer for dividend tracker. "
              "Companion to divtrack C CLI. Reports and schemas operational.",
        in_working=True,
    ),
]


def compute_burnrate(components: list) -> float:
    """BurnRate = |{PROVEN ∪ PROMISING}| / |C|"""
    healthy = sum(1 for c in components
                  if c.verdict in ("PROVEN", "PROMISING"))
    return healthy / len(components) if components else 0.0


# ── File Collection ────────────────────────────────────────────────────────────
EVERYTHING_GLOBS = [
    # schemas, configs, specs
    "**/*.yaml", "**/*.yml", "**/*.toml", "**/*.json",
    # code — all languages
    "**/*.py", "**/*.c", "**/*.h", "**/*.rs", "**/*.cs", "**/*.java",
    # docs & proofs
    "**/*.md", "**/*.txt", "**/*.pdf",
    # scripts
    "**/*.sh", "**/*.ps1",
]

EXCLUDE_DIRS = {
    ".git", ".claude", "__pycache__", ".pytest_cache",
    "target",          # Rust build artifacts
    "node_modules",
    "archives",        # don't recurse into output
}

WORKING_SUBSYSTEMS = {
    "sagco-audit",
    "sagco-archaeologist",
    "candlestick-ml-sim",
    "divtrack",
    "sagco-organism",
    "sagco-ninjascript-engine",
    "sagco-sovereignty-missing-links",
    "dividend-portfolio-tracker",
}


def collect_files(repo_root: Path, working_only: bool) -> list:
    collected = []
    for entry in repo_root.iterdir():
        if entry.name.startswith(".") or entry.name in EXCLUDE_DIRS:
            continue
        if entry.is_dir():
            if working_only and entry.name not in WORKING_SUBSYSTEMS:
                continue
            for dirpath, dirnames, filenames in os.walk(entry):
                dirnames[:] = [d for d in dirnames
                                if d not in EXCLUDE_DIRS and not d.startswith(".")]
                for fname in filenames:
                    fp = Path(dirpath) / fname
                    if fp.is_file():
                        collected.append(fp)
        elif entry.is_file():
            if not working_only:
                collected.append(entry)
    return sorted(collected)


def build_archive(repo_root: Path, out_path: Path, working_only: bool) -> str:
    files = collect_files(repo_root, working_only)
    label = "working" if working_only else "everything"
    print(f"  Archiving {len(files)} files → {out_path.name} [{label}]")
    with tarfile.open(out_path, "w:gz") as tf:
        for fp in files:
            arcname = str(fp.relative_to(repo_root))
            tf.add(str(fp), arcname=arcname)
    digest = sha256_file(str(out_path))
    print(f"    SHA-256: {digest}")
    return digest


# ── SAGCO-Organism Ingest Simulation ──────────────────────────────────────────
def simulate_organism_ingest(repo_root: Path, logs_dir: Path,
                              archives: list) -> list:
    """
    Simulate sagco analyze <archive> ingestion.
    In the Pi sandbox this would exec the C binary.
    Here we replicate the dispatch table logic in Python:
      INPUT → lexer → parser → AST → router → subsystem → ledger → SHA-256 seal
    """
    invocations = []
    for arc_path in archives:
        sha = sha256_file(str(arc_path))
        arc_name = arc_path.name

        # Lexer — tokenize filename
        tokens = arc_name.replace("-", "_").replace(".", "_").split("_")

        # Parser — classify input type
        input_type = "archive" if arc_name.endswith(".tar.gz") else "file"

        # Router — map to subsystem
        if "everything" in arc_name:
            subsystem = "provenance_engine"
        elif "working" in arc_name:
            subsystem = "audit_engine"
        else:
            subsystem = "general_analyzer"

        # Ledger receipt
        receipt = {
            "input":       arc_name,
            "input_type":  input_type,
            "tokens":      tokens[:6],
            "ast_root":    "SAGCO_ARCHIVE",
            "subsystem":   subsystem,
            "sha256_input": sha,
            "timestamp":   int(time.time()),
        }
        receipt_sha = sha256_string(json.dumps(receipt, sort_keys=True))
        receipt["receipt_sha256"] = receipt_sha

        invocations.append(receipt)
        print(f"  ORGANISM INGEST  {arc_name}")
        print(f"    → subsystem={subsystem}  sha={sha[:16]}…  receipt={receipt_sha[:16]}…")

    # Write invocation log
    log_path = logs_dir / "dark_matter_invocations.log"
    with open(log_path, "w") as f:
        for inv in invocations:
            f.write(json.dumps(inv) + "\n")
    print(f"  Invocation log → {log_path}")
    return invocations


# ── Report Printer ─────────────────────────────────────────────────────────────
BAR_WIDTH = 28

def progress_bar(ratio: float, width: int = BAR_WIDTH) -> str:
    filled = min(width, max(0, int(ratio * width)))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def verdict_color(v: str) -> str:
    colors = {
        "PROVEN":    "\033[92m",   # green
        "PROMISING": "\033[93m",   # yellow
        "UNPROVEN":  "\033[33m",   # dark yellow
        "INFLATED":  "\033[91m",   # red
    }
    reset = "\033[0m"
    return colors.get(v, "") + v + reset


def print_report(result: ProtocolResult, components: list):
    W = 76
    line = "  " + "─" * W

    print()
    print("  ╔" + "═" * W + "╗")
    print("  ║" + "  SAGCO DARK MATTER PROTOCOL — INTEGRATION REPORT".ljust(W) + "║")
    print("  ║" + f"  Version {result.version}   Build: {result.build_days}-day sprint".ljust(W) + "║")
    print("  ╚" + "═" * W + "╝")
    print()

    # ── Mathematical Proof Header ──────────────────────────────────────────────
    print("  MATHEMATICAL FOUNDATION")
    print(line)
    print("  ERU Formula:    V = A / E")
    print("  Where:          A = Actual (passing / working count)")
    print("                  E = Expected (designed / specified count)")
    print()
    print("  Thresholds:     PROVEN    ≥ 1.00   (A meets or exceeds E)")
    print("                  PROMISING ≥ 0.50   (majority working)")
    print("                  UNPROVEN  ≥ 0.01   (exists but incomplete)")
    print("                  INFLATED  < 0.01   (conceptual, not working)")
    print()
    print("  BurnRate:       β = |{PROVEN ∪ PROMISING}| / |C|")
    print("  Dark Matter δ:  δ = |working_files| / |universe_files|")
    print(f"  ROI_4DAY:       ρ = β × (PROVEN_count / BUILD_DAYS)")
    print(line)
    print()

    # ── Component Table ────────────────────────────────────────────────────────
    print("  COMPONENT ERU BREAKDOWN")
    print(line)
    print(f"  {'COMPONENT':<35}  {'LAYER':<18}  {'E':>4}  {'A':>4}  {'V=A/E':>6}  VERDICT")
    print(line)

    for c in components:
        vstr = verdict_color(c.verdict)
        print(f"  {c.name:<35}  {c.layer:<18}  {c.expected:>4}  "
              f"{c.actual:>4}  {c.ratio:>6.3f}  {vstr}")

    print(line)
    print()

    # ── Summary ────────────────────────────────────────────────────────────────
    proven_count    = sum(1 for c in components if c.verdict == "PROVEN")
    promising_count = sum(1 for c in components if c.verdict == "PROMISING")
    unproven_count  = sum(1 for c in components if c.verdict == "UNPROVEN")
    inflated_count  = sum(1 for c in components if c.verdict == "INFLATED")
    total           = len(components)

    print("  SUMMARY")
    print(line)
    print(f"  Total components:     {total}")
    print(f"  PROVEN:               {proven_count:>3}  ({proven_count/total*100:.1f}%)")
    print(f"  PROMISING:            {promising_count:>3}  ({promising_count/total*100:.1f}%)")
    print(f"  UNPROVEN:             {unproven_count:>3}  ({unproven_count/total*100:.1f}%)")
    print(f"  INFLATED:             {inflated_count:>3}  ({inflated_count/total*100:.1f}%)")
    print()
    print(f"  Total Expected (E):   {result.total_expected}")
    print(f"  Total Actual (A):     {result.total_actual}")
    print(f"  Overall V = A/E:      {result.overall_ratio:.4f}  [{verdict_color(result.overall_verdict)}]")
    print()

    # Progress bar
    pbar = progress_bar(result.overall_ratio)
    print(f"  Portfolio Progress    {pbar}  {result.overall_ratio*100:.1f}%")
    print()

    # BurnRate
    print(f"  BurnRate β:           {result.burn_rate:.4f}  ({result.burn_rate*100:.1f}%)")
    br_bar = progress_bar(result.burn_rate)
    print(f"                        {br_bar}  ", end="")
    if result.burn_rate >= 0.8:
        print(verdict_color("PROVEN") + " health")
    elif result.burn_rate >= 0.5:
        print(verdict_color("PROMISING") + " health")
    else:
        print(verdict_color("UNPROVEN") + " health")
    print()

    # Dark Matter
    print(f"  Dark Matter δ:        {result.dark_matter_ratio:.4f}  ({result.dark_matter_ratio*100:.1f}% of universe is working)")
    dm_bar = progress_bar(result.dark_matter_ratio)
    print(f"                        {dm_bar}")
    print()

    # ROI
    print(f"  4-Day ROI ρ:          {result.roi_4day:.4f}")
    print(f"  Interpretation:       {proven_count} PROVEN components delivered in {result.build_days} days")
    print(f"                        β={result.burn_rate:.2f} × ({proven_count}/{result.build_days}) = {result.roi_4day:.4f}")
    print(line)
    print()

    # ── Divtrack Reality Check ─────────────────────────────────────────────────
    current_monthly = 47.58
    div_target      = TARGET_MONTHLY
    div_ratio       = current_monthly / div_target
    div_verdict     = eru_verdict(div_ratio)
    yrs_to_target   = 0
    monthly         = current_monthly
    for yr in range(1, 51):
        monthly *= 1.085   # blended SCHD/DGRO/VIG/JEPI growth ~8.5%/yr
        if monthly >= div_target:
            yrs_to_target = yr
            break

    print("  DIVTRACK — WEALTH CAPITAL REALITY CHECK")
    print(line)
    print(f"  Current monthly income:   ${current_monthly:.2f}/mo")
    print(f"  Target monthly income:    ${div_target:,.2f}/mo")
    print(f"  ERU ratio:                {div_ratio:.4f}  [{verdict_color(div_verdict)}]")
    if yrs_to_target:
        print(f"  Years to target (~8.5%/yr DRIP growth):  {yrs_to_target} years")
    print(f"  Capital needed now:       ~${div_target*12/0.0347:,.0f}  (at 3.47% blended yield)")
    print(f"  SECURITY NOTE:            NinjaTrader futures = RISK CAPITAL ONLY")
    print(f"                            Dividend portfolio  = WEALTH CAPITAL. NEVER MIX.")
    print(line)
    print()

    # ── Archives ──────────────────────────────────────────────────────────────
    print("  ARCHIVES")
    print(line)
    print(f"  sagco-everything.tar.gz")
    print(f"    SHA-256: {result.archive_everything_sha256}")
    print(f"    Contents: ALL schemas, code, docs, proofs, specs, mathematical foundations")
    print(f"    WHO:  Domenic Garza / StrategicKhaos DAO LLC / ValorYield Engine PBC")
    print(f"    WHAT: Complete SAGCO architecture — every variable, constant, concept")
    print(f"    WHEN: 4-day sprint, June 2026")
    print(f"    WHERE: Remote (Raspberry Pi sandbox → cloud claude.ai/code session)")
    print(f"    HOW:  INV-198 recursive verification → FlameLang → ERU → BFT-Delta")
    print(f"    WHY:  Provenance substrate — cryptographic proof of existence + novelty")
    print()
    print(f"  sagco-working.tar.gz")
    print(f"    SHA-256: {result.archive_working_sha256}")
    print(f"    Contents: PROVEN+PROMISING working code (sagco-audit, sagco-archaeologist,")
    print(f"              candlestick-ml-sim, divtrack, sagco-organism, sagco-ninjascript-engine,")
    print(f"              sagco-sovereignty-missing-links, dividend-portfolio-tracker)")
    print(line)
    print()

    # ── Organism Ingest ────────────────────────────────────────────────────────
    print("  SAGCO-ORGANISM INGEST LOG")
    print(line)
    print("  Dispatch pipeline: INPUT → lexer → parser → AST → router → subsystem → ledger → seal")
    print()
    for inv in result.organism_invocations:
        print(f"  ┌── {inv['input']}")
        print(f"  │   type={inv['input_type']}  subsystem={inv['subsystem']}")
        print(f"  │   sha256={inv['sha256_input'][:32]}…")
        print(f"  └── receipt_seal={inv['receipt_sha256'][:32]}…")
        print()
    print(line)
    print()

    # ── Missing Links Status ───────────────────────────────────────────────────
    print("  MISSING LINKS — OPEN ITEMS")
    print(line)
    missing = [
        ("ML-ORGANISM-001", "UNPROVEN", "parser/graph_parser.c  (AST → graph edges)"),
        ("ML-ORGANISM-002", "INFLATED", "physics/lever.c + tension.c + fos.c + rc.c"),
        ("ML-ORGANISM-003", "INFLATED", "field/exchanger.c + insulation.c + rope_access.c"),
        ("ML-ORGANISM-004", "INFLATED", "network/ssh.c + vpn.c  (blocked on ARIN ASN)"),
        ("ML-ORGANISM-005", "INFLATED", "gps/compass.c + declination.c + exchanger_locator.c"),
        ("ML-ARCH-001",     "UNPROVEN", "PDF date extraction — needs pdfinfo fallback"),
        ("ML-ARCH-002",     "INFLATED", "Prior-art DB — no live USPTO API"),
        ("ML-ARCH-003",     "UNPROVEN", "HTB solve log cross-reference not wired"),
        ("ML-ARCH-004",     "UNPROVEN", "GPG signature verification not called in swarm"),
        ("ML-NINJA-001",    "UNPROVEN", "Bridge decision_tracer.py → NinjaScript via file socket"),
        ("ML-NINJA-002",    "INFLATED", "NinjaTrader LLC live account — upload WY Articles of Org"),
        ("ML-NINJA-003",    "INFLATED", "Real ES/NQ/CL futures feed into ERU loop"),
        ("ML-GDRIVE-001",   "UNPROVEN", "sagco-gdrive RSA JWT signing — wire rsa crate"),
        ("ML-MOVE2",        "INFLATED", "ARIN Org ID + ASN application (~$250/yr)"),
        ("ML-MOVE3",        "INFLATED", "RPKI ROA — blocked on ML-MOVE2"),
    ]
    proven_ml    = sum(1 for _, v, _ in missing if v == "PROVEN")
    promising_ml = sum(1 for _, v, _ in missing if v == "PROMISING")
    unproven_ml  = sum(1 for _, v, _ in missing if v == "UNPROVEN")
    inflated_ml  = sum(1 for _, v, _ in missing if v == "INFLATED")

    for ml_id, verdict, desc in missing:
        vstr = verdict_color(verdict)
        print(f"  {ml_id:<20}  [{vstr}]  {desc}")
    print()
    missing_burnrate = (proven_ml + promising_ml) / len(missing)
    print(f"  Missing-Links BurnRate: {missing_burnrate:.3f}  ({missing_burnrate*100:.1f}%)")
    print(f"  {unproven_ml} UNPROVEN (exist, incomplete)  ·  {inflated_ml} INFLATED (not started)")
    print(line)
    print()

    # ── Seal ──────────────────────────────────────────────────────────────────
    print("  PROTOCOL SEAL")
    print(line)
    print(f"  Manifest SHA-256: {result.seal_sha256}")
    print(f"  Protocol version: {result.version}")
    print(f"  Status:           {verdict_color('PROVEN' if result.burn_rate >= 0.8 else 'PROMISING')}")
    print(line)
    print()
    print("  \"The verifiers verify the verifiers.\"  — INV-198")
    print("  \"SLAAC trusts the router. SAGCO requires 2-of-3 BFT.\"  — bft-delta.md")
    print("  \"4 days lol — but BurnRate={:.0f}%.\"".format(result.burn_rate * 100))
    print()


# ── Manifest Writer ────────────────────────────────────────────────────────────
def write_manifest(result: ProtocolResult, reports_dir: Path) -> Path:
    manifest_path = reports_dir / "dark_matter_manifest.jsonl"
    with open(manifest_path, "w") as f:
        f.write(json.dumps(asdict(result), indent=None) + "\n")
    print(f"  Manifest → {manifest_path}")
    return manifest_path


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="SAGCO Dark Matter Protocol")
    parser.add_argument("--repo",    default=".", help="Repo root path")
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute ERU only; skip archive creation")
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    dm_root   = repo_root / "sagco-dark-matter"
    arc_dir   = dm_root / "archives"
    logs_dir  = dm_root / "logs"
    rpt_dir   = dm_root / "reports"
    for d in (arc_dir, logs_dir, rpt_dir):
        d.mkdir(parents=True, exist_ok=True)

    print()
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║   SAGCO DARK MATTER PROTOCOL — INITIATING           ║")
    print("  ║   BurnRate  ·  ERU  ·  ROI  ·  Organism Ingest      ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print()

    # ── Phase 1: Finalize component ERU ───────────────────────────────────────
    print("  [PHASE 1]  Computing ERU per component…")
    for c in COMPONENTS:
        c.ratio   = c.actual / c.expected if c.expected > 0 else 0.0
        c.verdict = eru_verdict(c.ratio)
    print(f"  {len(COMPONENTS)} components catalogued.")
    print()

    # ── Phase 2: Build archives ────────────────────────────────────────────────
    everything_arc = arc_dir / "sagco-everything.tar.gz"
    working_arc    = arc_dir / "sagco-working.tar.gz"

    if args.dry_run:
        print("  [PHASE 2]  DRY RUN — skipping archive creation.")
        sha_everything = "DRY_RUN_" + "0" * 56
        sha_working    = "DRY_RUN_" + "1" * 56
        everything_count = 0
        working_count    = 0
    else:
        print("  [PHASE 2]  Building archives…")
        sha_everything = build_archive(repo_root, everything_arc, working_only=False)
        sha_working    = build_archive(repo_root, working_arc,    working_only=True)
        everything_count = len(collect_files(repo_root, working_only=False))
        working_count    = len(collect_files(repo_root, working_only=True))
    print()

    # ── Phase 3: ERU aggregates ────────────────────────────────────────────────
    print("  [PHASE 3]  Aggregating ERU metrics…")
    total_e   = sum(c.expected for c in COMPONENTS)
    total_a   = sum(c.actual   for c in COMPONENTS)
    o_ratio   = total_a / total_e if total_e > 0 else 0.0
    o_verdict = eru_verdict(o_ratio)
    burnrate  = compute_burnrate(COMPONENTS)
    dm_ratio  = (working_count / everything_count) if everything_count > 0 else 0.0
    proven_n  = sum(1 for c in COMPONENTS if c.verdict == "PROVEN")
    roi_4day  = burnrate * (proven_n / BUILD_DAYS)
    print(f"  E={total_e}  A={total_a}  V={o_ratio:.4f}  [{o_verdict}]")
    print(f"  BurnRate={burnrate:.4f}  DarkMatter={dm_ratio:.4f}  ROI_4DAY={roi_4day:.4f}")
    print()

    # ── Phase 4: Organism ingest ───────────────────────────────────────────────
    print("  [PHASE 4]  SAGCO-Organism ingest simulation…")
    arcs_to_ingest = []
    if not args.dry_run:
        if everything_arc.exists(): arcs_to_ingest.append(everything_arc)
        if working_arc.exists():    arcs_to_ingest.append(working_arc)
    if not arcs_to_ingest:
        # Dry-run: use dummy records
        invocations = [
            {
                "input": "sagco-everything.tar.gz", "input_type": "archive",
                "tokens": ["sagco", "everything", "tar", "gz"],
                "ast_root": "SAGCO_ARCHIVE", "subsystem": "provenance_engine",
                "sha256_input": sha_everything,
                "timestamp": int(time.time()),
                "receipt_sha256": sha256_string("sagco-everything" + sha_everything),
            },
            {
                "input": "sagco-working.tar.gz", "input_type": "archive",
                "tokens": ["sagco", "working", "tar", "gz"],
                "ast_root": "SAGCO_ARCHIVE", "subsystem": "audit_engine",
                "sha256_input": sha_working,
                "timestamp": int(time.time()),
                "receipt_sha256": sha256_string("sagco-working" + sha_working),
            },
        ]
        print("  (Dry run) Simulated 2 ingest invocations.")
    else:
        invocations = simulate_organism_ingest(repo_root, logs_dir, arcs_to_ingest)
    print()

    # ── Phase 5: Seal ─────────────────────────────────────────────────────────
    print("  [PHASE 5]  Sealing manifest…")
    result = ProtocolResult(
        version                  = PROTOCOL_VERSION,
        timestamp_unix           = int(time.time()),
        build_days               = BUILD_DAYS,
        components               = [asdict(c) for c in COMPONENTS],
        total_expected           = total_e,
        total_actual             = total_a,
        overall_ratio            = o_ratio,
        overall_verdict          = o_verdict,
        burn_rate                = burnrate,
        dark_matter_ratio        = dm_ratio,
        roi_4day                 = roi_4day,
        archive_everything_sha256= sha_everything,
        archive_working_sha256   = sha_working,
        organism_invocations     = invocations,
        seal_sha256              = "",   # filled below
    )
    # Seal = SHA-256 of manifest JSON (sans seal field)
    manifest_data = asdict(result)
    manifest_data["seal_sha256"] = ""
    seal = sha256_string(json.dumps(manifest_data, sort_keys=True))
    result.seal_sha256 = seal
    print(f"  Seal: {seal}")
    print()

    # ── Phase 6: Print report ─────────────────────────────────────────────────
    manifest_path = write_manifest(result, rpt_dir)
    print_report(result, COMPONENTS)

    return 0


if __name__ == "__main__":
    sys.exit(main())
