"""
SAGCO Differential Engine
Compares two organism manifests (source vs target) and computes
exactly what needs to be replicated. No unnecessary copies.

Delta types:
  new       — file exists in source, not in target
  modified  — file exists in both, checksum differs
  deleted   — file exists in target, not in source (only in smart mode)
  unchanged — identical checksum, skip
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

from .manifest import OrganismManifest, FileRecord, build_manifest


class DeltaType(Enum):
    NEW       = auto()
    MODIFIED  = auto()
    DELETED   = auto()
    UNCHANGED = auto()


@dataclass
class FileDelta:
    path: str
    delta: DeltaType
    source_checksum: str | None
    target_checksum: str | None
    size: int = 0
    component: str = ""

    @property
    def needs_copy(self) -> bool:
        return self.delta in (DeltaType.NEW, DeltaType.MODIFIED)

    @property
    def symbol(self) -> str:
        return {
            DeltaType.NEW:       "+",
            DeltaType.MODIFIED:  "~",
            DeltaType.DELETED:   "-",
            DeltaType.UNCHANGED: "=",
        }[self.delta]


@dataclass
class DiffResult:
    source_cell: str
    target_cell: str | None
    new: list[FileDelta]      = field(default_factory=list)
    modified: list[FileDelta] = field(default_factory=list)
    deleted: list[FileDelta]  = field(default_factory=list)
    unchanged: list[FileDelta]= field(default_factory=list)

    @property
    def changes(self) -> list[FileDelta]:
        return self.new + self.modified

    @property
    def total_bytes(self) -> int:
        return sum(d.size for d in self.changes)

    @property
    def is_clean(self) -> bool:
        return not self.new and not self.modified and not self.deleted

    def summary(self) -> dict:
        return {
            "source_cell":   self.source_cell,
            "target_cell":   self.target_cell,
            "new":           len(self.new),
            "modified":      len(self.modified),
            "deleted":       len(self.deleted),
            "unchanged":     len(self.unchanged),
            "bytes_to_copy": self.total_bytes,
            "is_clean":      self.is_clean,
        }

    def print_report(self, verbose: bool = False) -> None:
        print(f"  Source: {self.source_cell}")
        print(f"  Target: {self.target_cell or '(fresh — no manifest)'}")
        print(f"  {'─'*40}")
        print(f"  + New:       {len(self.new):5d} files")
        print(f"  ~ Modified:  {len(self.modified):5d} files")
        print(f"  - Deleted:   {len(self.deleted):5d} files")
        print(f"  = Unchanged: {len(self.unchanged):5d} files")
        print(f"  {'─'*40}")
        kb = self.total_bytes / 1024
        print(f"  Bytes to copy: {kb:.1f} KB")
        if verbose:
            for d in self.changes[:20]:
                print(f"  {d.symbol} {d.path}")
            if len(self.changes) > 20:
                print(f"  ... and {len(self.changes)-20} more")


def diff(
    source: OrganismManifest,
    target: OrganismManifest | None = None,
    include_deletes: bool = False,
) -> DiffResult:
    result = DiffResult(
        source_cell=source.cell_id,
        target_cell=target.cell_id if target else None,
    )

    target_files: dict[str, FileRecord] = target.files if target else {}

    # Files in source
    for path, src_rec in source.files.items():
        if path in target_files:
            tgt_rec = target_files[path]
            if src_rec.checksum == tgt_rec.checksum:
                result.unchanged.append(FileDelta(
                    path=path, delta=DeltaType.UNCHANGED,
                    source_checksum=src_rec.checksum,
                    target_checksum=tgt_rec.checksum,
                    component=src_rec.component,
                ))
            else:
                result.modified.append(FileDelta(
                    path=path, delta=DeltaType.MODIFIED,
                    source_checksum=src_rec.checksum,
                    target_checksum=tgt_rec.checksum,
                    size=src_rec.size,
                    component=src_rec.component,
                ))
        else:
            result.new.append(FileDelta(
                path=path, delta=DeltaType.NEW,
                source_checksum=src_rec.checksum,
                target_checksum=None,
                size=src_rec.size,
                component=src_rec.component,
            ))

    # Files only in target (deletions)
    if include_deletes:
        for path, tgt_rec in target_files.items():
            if path not in source.files:
                result.deleted.append(FileDelta(
                    path=path, delta=DeltaType.DELETED,
                    source_checksum=None,
                    target_checksum=tgt_rec.checksum,
                    component=tgt_rec.component,
                ))

    return result


def diff_from_disk(
    source_root: str | Path,
    target_manifest_path: str | Path | None,
    mode: str = "smart",
) -> DiffResult:
    source = build_manifest(source_root, mode=mode)

    target: OrganismManifest | None = None
    if target_manifest_path and Path(target_manifest_path).exists():
        from .manifest import OrganismManifest as M
        target = M.load(target_manifest_path)

    return diff(source, target, include_deletes=(mode == "smart"))
