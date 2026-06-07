"""
SAGCO Integrity Layer
Verifies that a deployed organism instance matches its manifest.
Every critical file is checksum-verified. Failures are antibody triggers.
"""

from __future__ import annotations
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import OrganismManifest, _sha256


@dataclass
class IntegrityResult:
    path: str
    expected: str
    actual: str
    passed: bool
    component: str


@dataclass
class IntegrityReport:
    cell_id: str
    target_root: str
    results: list[IntegrityResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> list[IntegrityResult]:
        return [r for r in self.results if not r.passed]

    @property
    def status(self) -> str:
        if not self.failed:
            return "INTEGRITY_PASS"
        required_failures = [
            r for r in self.failed
            if r.component in ("kernel", "language", "wafers", "antibodies")
        ]
        return "INTEGRITY_FAIL_CRITICAL" if required_failures else "INTEGRITY_FAIL_OPTIONAL"

    def summary(self) -> dict:
        return {
            "cell_id":    self.cell_id,
            "target":     self.target_root,
            "status":     self.status,
            "total":      len(self.results),
            "passed":     self.passed,
            "failed":     len(self.failed),
            "failures":   [
                {"path": r.path, "component": r.component,
                 "expected": r.expected[:8], "actual": r.actual[:8]}
                for r in self.failed[:20]
            ],
        }

    def print_report(self) -> None:
        icon = "✓" if not self.failed else "✗"
        print(f"  {icon} {self.status}")
        print(f"  Checked: {len(self.results):5d} files")
        print(f"  Passed:  {self.passed:5d}")
        print(f"  Failed:  {len(self.failed):5d}")
        if self.failed:
            print("  Critical failures:")
            for r in self.failed[:10]:
                print(f"    ✗ {r.component:12s} {r.path}")


def verify(manifest: OrganismManifest, target_root: str | Path) -> IntegrityReport:
    root = Path(target_root)
    report = IntegrityReport(cell_id=manifest.cell_id, target_root=str(root))

    for rel_path, record in manifest.files.items():
        target_file = root / rel_path
        if not target_file.exists():
            report.results.append(IntegrityResult(
                path=rel_path, expected=record.checksum, actual="MISSING",
                passed=False, component=record.component,
            ))
            continue
        actual = _sha256(target_file)
        report.results.append(IntegrityResult(
            path=rel_path, expected=record.checksum, actual=actual,
            passed=(actual == record.checksum), component=record.component,
        ))

    return report
