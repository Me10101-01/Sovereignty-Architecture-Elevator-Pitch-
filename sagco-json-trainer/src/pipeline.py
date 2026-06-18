#!/usr/bin/env python3
"""
pipeline.py — Full headless trainer pipeline

Runs all four stages in sequence:
  1. schema_fingerprint  → schemas/fingerprint.yaml
  2. token_extractor     → vocabulary/tokens.json + sagco_vocab.yaml
  3. qa_trainer          → trainer/cards.jsonl
  4. antibody_builder    → antibodies/parse_failures.yaml

Usage:
  python pipeline.py <sandbox_dir> [base_output_dir]

  python pipeline.py sandbox/
  python pipeline.py C:/SAGCO/493.88_VAULT/json-ingest/sandbox .
"""

import sys
import os
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

import schema_fingerprint
import token_extractor
import qa_trainer
import antibody_builder


def run_pipeline(sandbox_dir: str, base_dir: str = ".") -> None:
    sandbox = Path(sandbox_dir)
    base    = Path(base_dir)

    if not sandbox.exists():
        print(f"  ERROR: sandbox not found: {sandbox}")
        print(f"  Run the PowerShell intake script first.")
        sys.exit(1)

    print("\n" + "="*60)
    print("  SAGCO JSON HEADLESS TRAINER PIPELINE")
    print("="*60)
    print(f"  Sandbox: {sandbox}")
    print(f"  Base:    {base}")
    print()

    stages = [
        ("STAGE 1 — Schema Fingerprint",
         lambda: schema_fingerprint.run(str(sandbox), str(base / "schemas"))),

        ("STAGE 2 — Token Extractor",
         lambda: token_extractor.run(str(sandbox), str(base / "vocabulary"))),

        ("STAGE 3 — Q/A Trainer",
         lambda: qa_trainer.run(str(sandbox), str(base / "trainer"))),

        ("STAGE 4 — Antibody Builder",
         lambda: antibody_builder.run(
             str(sandbox),
             str(base / "schemas" / "fingerprint.yaml"),
             str(base / "antibodies")
         )),
    ]

    results = {}
    for label, fn in stages:
        print(f"\n  [{label}]")
        t0 = time.time()
        try:
            result = fn()
            results[label] = result
        except Exception as e:
            print(f"  ERROR: {e}")
            results[label] = None
        print(f"  Time: {time.time()-t0:.2f}s")

    print("\n" + "="*60)
    print("  PIPELINE COMPLETE")
    print("="*60)
    print()
    print("  Outputs:")
    print(f"    schemas/fingerprint.yaml")
    print(f"    vocabulary/tokens.json")
    print(f"    vocabulary/sagco_vocab.yaml")
    print(f"    trainer/cards.jsonl")
    print(f"    antibodies/parse_failures.yaml")
    print()
    print("  Next steps:")
    print("    1. Review vocabulary/sagco_vocab.yaml → wire FlameLang type seeds")
    print("    2. Review trainer/cards.jsonl → ingest to Qdrant on Pi 4")
    print("    3. Review antibodies/parse_failures.yaml → add to antibody registry")
    print()
    print("  sagco missing-links status: ML-TRAINER-001, ML-TRAINER-002 → UNCOMPUTED")
    print("="*60)


if __name__ == "__main__":
    sandbox_dir = sys.argv[1] if len(sys.argv) > 1 else "sandbox"
    base_dir    = sys.argv[2] if len(sys.argv) > 2 else "."
    run_pipeline(sandbox_dir, base_dir)
