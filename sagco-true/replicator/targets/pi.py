"""
SAGCO Target — Raspberry Pi (SSH + rsync)
Replicates organism to a Pi over SSH.
Handles both direct IP and mDNS hostname (raspberrypi.local).

sagco replicate --target pi --ip 192.168.1.42
sagco replicate --target pi --host raspberrypi.local --user pi
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
DEFAULT_PI_USER = "pi"
DEFAULT_PI_DEST = "~/sagco-world"


class PiTarget(BaseTarget):
    name = "pi"
    description = "Raspberry Pi — SSH + rsync replication"

    def __init__(
        self,
        host: str,
        user: str = DEFAULT_PI_USER,
        dest: str = DEFAULT_PI_DEST,
        ssh_key: str | None = None,
        port: int = 22,
    ) -> None:
        self.host = host
        self.user = user
        self.dest = dest
        self.ssh_key = ssh_key
        self.port = port
        self._remote = f"{user}@{host}"

    def _ssh_args(self) -> list[str]:
        args = ["ssh", "-p", str(self.port), "-o", "StrictHostKeyChecking=no",
                "-o", "ConnectTimeout=5"]
        if self.ssh_key:
            args += ["-i", self.ssh_key]
        return args

    def probe(self) -> bool:
        try:
            result = subprocess.run(
                self._ssh_args() + [self._remote, "echo sagco-probe"],
                capture_output=True, timeout=8,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_manifest(self) -> OrganismManifest | None:
        try:
            result = subprocess.run(
                self._ssh_args() + [
                    self._remote,
                    f"cat {self.dest}/{MANIFEST_FILENAME} 2>/dev/null || echo __MISSING__"
                ],
                capture_output=True, text=True, timeout=10,
            )
            out = result.stdout.strip()
            if out == "__MISSING__" or not out:
                return None
            data = json.loads(out)
            m = OrganismManifest(cell_id=data["cell_id"])
            m.generation = data.get("generation", 1)
            m.parent_cell = data.get("parent_cell")
            return m
        except Exception:
            return None

    def replicate(
        self,
        source_root: Path,
        diff: DiffResult,
        source_manifest: OrganismManifest,
        dry_run: bool = False,
    ) -> ReplicateResult:
        t0 = time.time()
        errors: list[str] = []
        bytes_copied = 0
        files_copied = 0

        if not shutil.which("rsync"):
            # fallback: scp file by file
            return self._replicate_scp(source_root, diff, source_manifest, dry_run)

        # Build include list from diff.changes
        if not diff.changes and not diff.deleted:
            return ReplicateResult(
                target_name=self._remote,
                target_type="pi",
                success=True,
                files_copied=0,
                bytes_copied=0,
                skipped=len(diff.unchanged),
                errors=[],
                duration_s=time.time() - t0,
            )

        # Write include filter file
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
            for delta in diff.changes:
                # rsync include needs parent dirs too
                parts = Path(delta.path).parts
                for i in range(1, len(parts) + 1):
                    tf.write(f"+ /{'/'.join(parts[:i])}\n")
            tf.write("- *\n")
            filter_file = tf.name

        try:
            ssh_cmd = " ".join(self._ssh_args()[1:])  # drop leading 'ssh'
            cmd = [
                "rsync", "-avz", "--checksum",
                f"--filter=merge {filter_file}",
                "-e", f"ssh {ssh_cmd.replace(self._remote, '')}".strip(),
                f"{source_root}/",
                f"{self._remote}:{self.dest}/",
            ]
            if dry_run:
                cmd.insert(1, "--dry-run")

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                errors.append(result.stderr.strip()[:200])
            else:
                lines = [l for l in result.stdout.splitlines() if l and not l.startswith(">")]
                files_copied = len([l for l in lines if "/" in l])
                bytes_copied = sum(d.size for d in diff.changes)
        except Exception as e:
            errors.append(str(e))
        finally:
            os.unlink(filter_file)

        # Push manifest
        manifest_path = None
        if not dry_run and not errors:
            try:
                import tempfile, os
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tf:
                    source_manifest.save(tf.name)
                    tmp = tf.name
                subprocess.run(
                    self._ssh_args() + [self._remote, f"mkdir -p {self.dest}"],
                    timeout=10, capture_output=True,
                )
                subprocess.run(
                    ["scp", "-P", str(self.port)] +
                    (["-i", self.ssh_key] if self.ssh_key else []) +
                    [tmp, f"{self._remote}:{self.dest}/{MANIFEST_FILENAME}"],
                    timeout=30, capture_output=True,
                )
                os.unlink(tmp)
                manifest_path = f"{self.dest}/{MANIFEST_FILENAME}"
            except Exception as e:
                errors.append(f"manifest push: {e}")

        return ReplicateResult(
            target_name=self._remote,
            target_type="pi",
            success=not errors,
            files_copied=files_copied,
            bytes_copied=bytes_copied,
            skipped=len(diff.unchanged),
            errors=errors,
            manifest_path=manifest_path,
            duration_s=time.time() - t0,
        )

    def _replicate_scp(
        self, source_root: Path, diff: DiffResult,
        source_manifest: OrganismManifest, dry_run: bool
    ) -> ReplicateResult:
        t0 = time.time()
        errors: list[str] = []
        copied = 0
        for delta in diff.changes:
            src = source_root / delta.path
            remote_path = f"{self._remote}:{self.dest}/{delta.path}"
            if dry_run:
                print(f"  [dry] scp {delta.path}")
                copied += 1
                continue
            # ensure remote dir exists
            subprocess.run(
                self._ssh_args() + [self._remote,
                    f"mkdir -p {self.dest}/{str(Path(delta.path).parent)}"],
                capture_output=True, timeout=10,
            )
            r = subprocess.run(
                ["scp", "-P", str(self.port)] + (["-i", self.ssh_key] if self.ssh_key else [])
                + [str(src), remote_path],
                capture_output=True, timeout=30,
            )
            if r.returncode == 0:
                copied += 1
            else:
                errors.append(f"scp {delta.path}: {r.stderr.decode()[:80]}")

        return ReplicateResult(
            target_name=self._remote, target_type="pi",
            success=not errors, files_copied=copied,
            bytes_copied=sum(d.size for d in diff.changes),
            skipped=len(diff.unchanged), errors=errors,
            duration_s=time.time() - t0,
        )

    def verify(self, manifest: OrganismManifest):
        from sagco_true.replicator.integrity import IntegrityReport, IntegrityResult
        report = IntegrityReport(cell_id=manifest.cell_id, target_root=self._remote)
        try:
            checksums_cmd = "; ".join(
                f"sha256sum {self.dest}/{p} 2>/dev/null | cut -d' ' -f1"
                for p in list(manifest.files.keys())[:50]
            )
            result = subprocess.run(
                self._ssh_args() + [self._remote, checksums_cmd],
                capture_output=True, text=True, timeout=30,
            )
            lines = result.stdout.strip().splitlines()
            for (rel, rec), actual in zip(list(manifest.files.items())[:50], lines):
                actual = actual.strip()
                report.results.append(IntegrityResult(
                    path=rel, expected=rec.checksum, actual=actual,
                    passed=(actual == rec.checksum), component=rec.component,
                ))
        except Exception as e:
            pass
        return report
