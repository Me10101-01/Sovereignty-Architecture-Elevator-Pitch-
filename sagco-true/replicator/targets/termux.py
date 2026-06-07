"""
SAGCO Target — Termux (Android/Z Fold)
Replicates organism to Termux via ADB or SSH.
The Z Fold IS the node. It needs to carry the organism.

sagco replicate --target phone --ip 192.168.1.89 --via termux
sagco replicate --target phone --via adb
"""

from __future__ import annotations
import json
import shutil
import subprocess
import time
from pathlib import Path

from sagco_true.replicator.manifest import OrganismManifest
from sagco_true.replicator.diff import DiffResult
from .base import BaseTarget, ReplicateResult


MANIFEST_FILENAME = "SAGCO_MANIFEST.json"
DEFAULT_TERMUX_HOME = "/data/data/com.termux/files/home"
DEFAULT_TERMUX_DEST = "~/sagco-world"


class TermuxTarget(BaseTarget):
    name = "termux"
    description = "Android/Termux — ADB push or SSH replication"

    def __init__(
        self,
        ip: str | None = None,
        port: int = 8022,           # Termux default SSH port
        user: str = "u0_a0",
        via: str = "ssh",           # "ssh" | "adb"
        dest: str = DEFAULT_TERMUX_DEST,
    ) -> None:
        self.ip = ip or "192.168.1.89"    # Z Fold default
        self.port = port
        self.user = user
        self.via = via
        self.dest = dest

    def _ssh_args(self) -> list[str]:
        return [
            "ssh", "-p", str(self.port),
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{self.user}@{self.ip}",
        ]

    def probe(self) -> bool:
        if self.via == "adb":
            try:
                result = subprocess.run(
                    ["adb", "shell", "echo", "sagco-probe"],
                    capture_output=True, timeout=8,
                )
                return result.returncode == 0
            except Exception:
                return False
        else:
            try:
                result = subprocess.run(
                    self._ssh_args()[:-1] + [f"{self.user}@{self.ip}", "echo sagco-probe"],
                    capture_output=True, timeout=8,
                )
                return result.returncode == 0
            except Exception:
                return False

    def get_manifest(self) -> OrganismManifest | None:
        return None   # fresh replicate assumed for phone

    def replicate(
        self,
        source_root: Path,
        diff: DiffResult,
        source_manifest: OrganismManifest,
        dry_run: bool = False,
    ) -> ReplicateResult:
        t0 = time.time()
        errors: list[str] = []
        copied = 0

        if self.via == "adb":
            return self._replicate_adb(source_root, diff, source_manifest, dry_run)

        # SSH path
        for delta in diff.changes:
            src = source_root / delta.path
            remote_dir = f"{self.dest}/{str(Path(delta.path).parent)}"
            if dry_run:
                print(f"  [dry] → termux:{delta.path}")
                copied += 1
                continue
            # mkdir on remote
            subprocess.run(
                self._ssh_args() + [f"mkdir -p {remote_dir}"],
                capture_output=True, timeout=10,
            )
            r = subprocess.run(
                ["scp", "-P", str(self.port),
                 str(src), f"{self.user}@{self.ip}:{self.dest}/{delta.path}"],
                capture_output=True, timeout=30,
            )
            if r.returncode == 0:
                copied += 1
            else:
                errors.append(f"{delta.path}: {r.stderr.decode()[:60]}")

        return ReplicateResult(
            target_name=f"termux@{self.ip}",
            target_type="termux",
            success=not errors,
            files_copied=copied,
            bytes_copied=sum(d.size for d in diff.changes),
            skipped=len(diff.unchanged),
            errors=errors,
            duration_s=time.time() - t0,
        )

    def _replicate_adb(
        self, source_root: Path, diff: DiffResult,
        source_manifest: OrganismManifest, dry_run: bool
    ) -> ReplicateResult:
        t0 = time.time()
        errors = []
        copied = 0
        adb_dest = f"{DEFAULT_TERMUX_HOME}/sagco-world"

        for delta in diff.changes:
            src = source_root / delta.path
            remote_path = f"{adb_dest}/{delta.path}"
            if dry_run:
                print(f"  [dry] adb push {delta.path}")
                copied += 1
                continue
            subprocess.run(
                ["adb", "shell", f"mkdir -p {adb_dest}/{str(Path(delta.path).parent)}"],
                capture_output=True, timeout=10,
            )
            r = subprocess.run(
                ["adb", "push", str(src), remote_path],
                capture_output=True, timeout=30,
            )
            if r.returncode == 0:
                copied += 1
            else:
                errors.append(f"adb push {delta.path}: {r.stderr.decode()[:60]}")

        return ReplicateResult(
            target_name="adb:termux",
            target_type="termux",
            success=not errors,
            files_copied=copied,
            bytes_copied=sum(d.size for d in diff.changes),
            skipped=len(diff.unchanged),
            errors=errors,
            duration_s=time.time() - t0,
        )

    def verify(self, manifest: OrganismManifest):
        from sagco_true.replicator.integrity import IntegrityReport
        return IntegrityReport(cell_id=manifest.cell_id, target_root=f"termux@{self.ip}")
