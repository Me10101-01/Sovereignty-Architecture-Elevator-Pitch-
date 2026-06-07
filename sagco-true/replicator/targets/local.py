"""
SAGCO Target — Local Directory
Replicates the organism to any accessible local path.
Used for: USB drives (already mounted), local clones, test deploys.

USB flow:
  1. User mounts USB: macOS → /Volumes/SAGCO, Linux → /mnt/usb, Windows → D:\
  2. sagco replicate --target usb --mount D:\
  3. We write organism structure + manifest to mount point
"""

from __future__ import annotations
import shutil
import time
from pathlib import Path

from sagco_true.replicator.manifest import OrganismManifest, MANIFEST_FILENAME
from sagco_true.replicator.diff import DiffResult
from .base import BaseTarget, ReplicateResult


MANIFEST_FILENAME = "SAGCO_MANIFEST.json"


class LocalTarget(BaseTarget):
    name = "local"
    description = "Local directory — USB mount point, clone directory, test deploy"

    def __init__(self, mount_point: str | Path) -> None:
        self.mount = Path(mount_point)

    def probe(self) -> bool:
        return self.mount.exists() and self.mount.is_dir()

    def get_manifest(self) -> OrganismManifest | None:
        mp = self.mount / MANIFEST_FILENAME
        if mp.exists():
            return OrganismManifest.load(mp)
        return None

    def replicate(
        self,
        source_root: Path,
        diff: DiffResult,
        source_manifest: OrganismManifest,
        dry_run: bool = False,
    ) -> ReplicateResult:
        t0 = time.time()
        copied = 0
        skipped = 0
        bytes_copied = 0
        errors: list[str] = []

        if not dry_run:
            self.mount.mkdir(parents=True, exist_ok=True)

        for delta in diff.changes:
            src = source_root / delta.path
            dst = self.mount / delta.path
            if dry_run:
                print(f"  [dry] {delta.symbol} {delta.path}")
                copied += 1
                bytes_copied += delta.size
                continue
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied += 1
                bytes_copied += delta.size
            except Exception as e:
                errors.append(f"{delta.path}: {e}")

        for delta in diff.deleted:
            dst = self.mount / delta.path
            if dry_run:
                print(f"  [dry] - {delta.path}")
                continue
            try:
                if dst.exists():
                    dst.unlink()
            except Exception as e:
                errors.append(f"delete {delta.path}: {e}")

        skipped = len(diff.unchanged)

        # Write manifest on target
        manifest_path = None
        if not dry_run:
            mp = self.mount / MANIFEST_FILENAME
            source_manifest.save(mp)
            manifest_path = str(mp)

        return ReplicateResult(
            target_name=str(self.mount),
            target_type="local",
            success=not errors,
            files_copied=copied,
            bytes_copied=bytes_copied,
            skipped=skipped,
            errors=errors,
            manifest_path=manifest_path,
            duration_s=time.time() - t0,
        )

    def verify(self, manifest: OrganismManifest):
        from sagco_true.replicator.integrity import verify
        return verify(manifest, self.mount)
