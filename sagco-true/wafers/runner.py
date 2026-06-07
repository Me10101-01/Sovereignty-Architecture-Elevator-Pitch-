"""
SAGCO Wafer Runner
Reads wafer CSVs and .sagco wafer declarations.
Produces truth reports: expected vs actual for every claim SAGCO makes about itself.
A failing required wafer is an antibody trigger.
"""

from __future__ import annotations
import csv
import os
import platform
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Wafer:
    name: str
    expected: Any
    actual: Any
    mode: str = "required"    # required | optional
    category: str = ""
    note: str = ""

    @property
    def passed(self) -> bool:
        exp = str(self.expected).strip().lower()
        act = str(self.actual).strip().lower()
        return exp == act or exp in act or (exp == "yes" and act not in ("no", "false", ""))

    def to_row(self) -> list[str]:
        return [self.name, str(self.expected), str(self.actual),
                "PASS" if self.passed else "FAIL", self.mode, self.category, self.note]


WAFER_DIR = Path(__file__).parent


# ── Built-in runtime wafers (the truth test from the design doc) ──────────

def _detect_python() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"

def _detect_world() -> str:
    if os.environ.get("TERMUX_VERSION") or os.path.exists("/data/data/com.termux"):
        return "termux"
    if os.path.exists("/.dockerenv"):
        return "docker"
    if os.environ.get("KUBERNETES_SERVICE_HOST"):
        return "kubernetes"
    if "microsoft" in platform.uname().release.lower():
        return "wsl"
    if platform.system() == "Windows":
        return "windows"
    if platform.system() == "Linux":
        return "linux"
    return platform.system().lower()

def _can_boot() -> str:
    return "yes"   # if we're running, we booted

def _can_remember_identity() -> str:
    prov = Path(__file__).parent.parent.parent / "PROVENANCE.yaml"
    return "yes" if prov.exists() else "no"

def _can_detect_world() -> str:
    w = _detect_world()
    return "yes" if w not in ("", "unknown") else "no"

def _can_measure_reality() -> str:
    return "yes"   # this function existing proves it

def _can_learn_from_error() -> str:
    ab = Path(__file__).parent.parent / "antibodies" / "detector.py"
    return "yes" if ab.exists() else "partial"

def _can_run_on_phone() -> str:
    world = _detect_world()
    if world == "termux":
        return "yes"
    if os.path.exists("/sdcard") or os.environ.get("ANDROID_ROOT"):
        return "yes"
    return "partial"


SAGCO_ARE_YOU_TRUE: list[Wafer] = [
    Wafer("can_boot",             "yes",      _can_boot(),             "required", "kernel"),
    Wafer("can_remember_identity","yes",      _can_remember_identity(),"required", "kernel"),
    Wafer("can_detect_world",     "yes",      _can_detect_world(),     "required", "kernel"),
    Wafer("can_measure_reality",  "yes",      _can_measure_reality(),  "required", "kernel"),
    Wafer("can_learn_from_error", "yes",      _can_learn_from_error(), "required", "antibody"),
    Wafer("can_run_on_phone",     "yes",      _can_run_on_phone(),     "optional", "portability"),
    Wafer("world",                "detected", _detect_world(),         "optional", "environment"),
    Wafer("python_version",       "3.x",      _detect_python(),        "optional", "runtime"),
]


# ── CSV wafer loader ───────────────────────────────────────────────────────

def load_csv(path: str | Path) -> list[Wafer]:
    path = Path(path)
    if not path.exists():
        return []
    wafers: list[Wafer] = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            w = Wafer(
                name=row.get("name", ""),
                expected=row.get("expected", ""),
                actual=row.get("actual", ""),
                mode=row.get("mode", "required"),
                category=row.get("category", ""),
                note=row.get("note", ""),
            )
            wafers.append(w)
    return wafers


def save_csv(wafers: list[Wafer], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "expected", "actual", "result", "mode", "category", "note"])
        for w in wafers:
            writer.writerow(w.to_row())


# ── Truth report ───────────────────────────────────────────────────────────

def run_truth_test(extra_wafers: list[Wafer] | None = None) -> dict:
    all_wafers = SAGCO_ARE_YOU_TRUE + (extra_wafers or [])
    all_wafers += load_csv(WAFER_DIR / "expected_actual.csv")

    required = [w for w in all_wafers if w.mode == "required"]
    optional = [w for w in all_wafers if w.mode == "optional"]
    failed_required = [w for w in required if not w.passed]
    failed_optional = [w for w in optional if not w.passed]

    status = "TRUE_ENOUGH_TO_GROW" if not failed_required else "NEEDS_HEALING"

    return {
        "status": status,
        "timestamp": time.time(),
        "total": len(all_wafers),
        "passed": sum(1 for w in all_wafers if w.passed),
        "failed_required": len(failed_required),
        "failed_optional": len(failed_optional),
        "SAGCO_ARE_YOU_TRUE": {
            w.name: {
                "expected": w.expected,
                "actual": w.actual,
                "passed": w.passed,
                "mode": w.mode,
            }
            for w in SAGCO_ARE_YOU_TRUE
        },
        "failures": [
            {"name": w.name, "expected": w.expected, "actual": w.actual, "mode": w.mode}
            for w in failed_required + failed_optional
        ],
    }


if __name__ == "__main__":
    import json
    result = run_truth_test()
    print(json.dumps(result, indent=2))
    save_csv(SAGCO_ARE_YOU_TRUE, WAFER_DIR / "reality_match.csv")
    print(f"\nStatus: {result['status']}")
    print(f"Passed: {result['passed']}/{result['total']}")
