"""
SAGCO Wafer Importer
Reads on-disk wafer files from E:\\SAGCO-WORLD\\wafers\\ (or any path)
and imports them into the SAGCO wafer format.

The daemon on Lyra has already been generating:
  SAGCO_FULL_BOOT_PROOF.txt
  SAGCO_STATUS_PROOF.txt
  SAGCO_WORLD_ROOT_WAFER.csv

This importer reads them and integrates with sagco-true/wafers/runner.py.
"""

from __future__ import annotations
import csv
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Known paths where on-disk wafers may exist
SAGCO_WORLD_PATHS = [
    r"E:\SAGCO-WORLD\wafers",
    r"C:\Users\garza\SAGCO-WORLD\wafers",
    r"~/SAGCO-WORLD/wafers",
    "/mnt/e/SAGCO-WORLD/wafers",    # WSL mount
    "/mnt/c/Users/garza/SAGCO-WORLD/wafers",
]


@dataclass
class ImportedWafer:
    name: str
    expected: Any
    actual: Any
    passed: bool
    mode: str = "required"
    source_file: str = ""
    imported_at: float = field(default_factory=time.time)

    def to_csv_row(self) -> list[str]:
        return [
            self.name,
            str(self.expected),
            str(self.actual),
            "PASS" if self.passed else "FAIL",
            self.mode,
            "imported",
            f"from={self.source_file}",
        ]


def find_sagco_world() -> Path | None:
    for raw in SAGCO_WORLD_PATHS:
        p = Path(raw).expanduser()
        if p.exists():
            return p
    return None


def import_csv(path: Path) -> list[ImportedWafer]:
    wafers: list[ImportedWafer] = []
    try:
        with open(path, newline="", errors="replace") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name     = row.get("name", row.get("wafer", row.get("key", "unknown")))
                expected = row.get("expected", row.get("EXPECTED", "yes"))
                actual   = row.get("actual",   row.get("ACTUAL",   ""))
                result   = row.get("result",   row.get("STATUS",   ""))
                mode     = row.get("mode",     "required")
                passed = (
                    result.upper() == "PASS" or
                    str(expected).lower() == str(actual).lower()
                )
                wafers.append(ImportedWafer(
                    name=name, expected=expected, actual=actual,
                    passed=passed, mode=mode, source_file=str(path),
                ))
    except Exception as e:
        wafers.append(ImportedWafer(
            name=f"import_error:{path.name}",
            expected="ok", actual=str(e), passed=False,
            source_file=str(path),
        ))
    return wafers


def import_txt_proof(path: Path) -> list[ImportedWafer]:
    """Parse SAGCO_FULL_BOOT_PROOF.txt and SAGCO_STATUS_PROOF.txt style files."""
    wafers: list[ImportedWafer] = []
    try:
        content = path.read_text(errors="replace")
        # Extract KEY=VALUE pairs
        for m in re.finditer(r'^([A-Z_][A-Z0-9_]*)=(.+)$', content, re.MULTILINE):
            key, val = m.group(1), m.group(2).strip()
            # treat STATUS=PASS, STATUS=SAGCO_TOPOLOGY_PASS etc.
            passed = ("PASS" in val.upper() or val.upper() in ("TRUE", "YES", "OK", "1"))
            wafers.append(ImportedWafer(
                name=key.lower(),
                expected="pass",
                actual=val,
                passed=passed,
                mode="required",
                source_file=str(path),
            ))
    except Exception as e:
        wafers.append(ImportedWafer(
            name=f"txt_parse_error:{path.name}",
            expected="ok", actual=str(e), passed=False,
            source_file=str(path),
        ))
    return wafers


def import_all(wafer_dir: Path | str | None = None) -> list[ImportedWafer]:
    """Import all wafer files from E:\\SAGCO-WORLD\\wafers\\ or given path."""
    all_wafers: list[ImportedWafer] = []

    if wafer_dir is None:
        wafer_dir = find_sagco_world()

    if wafer_dir is None:
        return [ImportedWafer(
            name="sagco_world_not_found",
            expected="yes", actual="no", passed=False,
            mode="optional",
            source_file="searched: " + ", ".join(SAGCO_WORLD_PATHS[:3]),
        )]

    wafer_dir = Path(wafer_dir)

    for fpath in sorted(wafer_dir.iterdir()):
        if fpath.suffix.lower() == ".csv":
            all_wafers.extend(import_csv(fpath))
        elif fpath.suffix.lower() in (".txt", ".log"):
            all_wafers.extend(import_txt_proof(fpath))

    return all_wafers


def merge_with_runner(imported: list[ImportedWafer]) -> dict:
    """Merge imported wafers into a truth report compatible with runner.py format."""
    passed = sum(1 for w in imported if w.passed)
    failed_required = [w for w in imported if not w.passed and w.mode == "required"]
    return {
        "source": "E:\\SAGCO-WORLD\\wafers",
        "status": "TRUE_ENOUGH_TO_GROW" if not failed_required else "NEEDS_HEALING",
        "total": len(imported),
        "passed": passed,
        "failed_required": len(failed_required),
        "wafers": [
            {
                "name": w.name, "expected": w.expected, "actual": w.actual,
                "passed": w.passed, "mode": w.mode, "source": w.source_file,
            }
            for w in imported
        ],
    }


if __name__ == "__main__":
    import sys, json
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    wafers = import_all(path_arg)
    report = merge_with_runner(wafers)
    print(json.dumps(report, indent=2))
    print(f"\nImported: {report['total']} wafers")
    print(f"Status:   {report['status']}")
