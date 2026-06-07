"""
SAGCO Target Drivers — Base
All target drivers implement this interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sagco_true.replicator.manifest import OrganismManifest
from sagco_true.replicator.diff import DiffResult


@dataclass
class ReplicateResult:
    target_name: str
    target_type: str
    success: bool
    files_copied: int
    bytes_copied: int
    skipped: int
    errors: list[str]
    manifest_path: str | None = None
    duration_s: float = 0.0

    def print_summary(self) -> None:
        icon = "✓" if self.success else "✗"
        print(f"  {icon} {self.target_name} ({self.target_type})")
        print(f"    Copied:  {self.files_copied} files  ({self.bytes_copied/1024:.1f} KB)")
        print(f"    Skipped: {self.skipped}")
        print(f"    Errors:  {len(self.errors)}")
        if self.errors:
            for e in self.errors[:5]:
                print(f"      ! {e}")
        print(f"    Time:    {self.duration_s:.2f}s")


class BaseTarget(ABC):
    name: str = "base"
    description: str = ""

    @abstractmethod
    def probe(self) -> bool:
        """Return True if this target is available/reachable."""
        ...

    @abstractmethod
    def get_manifest(self) -> OrganismManifest | None:
        """Return the manifest currently on the target, or None if fresh."""
        ...

    @abstractmethod
    def replicate(
        self,
        source_root: Path,
        diff: DiffResult,
        source_manifest: OrganismManifest,
        dry_run: bool = False,
    ) -> ReplicateResult:
        """Copy the diff to the target."""
        ...

    def verify(self, manifest: OrganismManifest) -> "Any":
        from sagco_true.replicator.integrity import verify, IntegrityReport
        raise NotImplementedError
