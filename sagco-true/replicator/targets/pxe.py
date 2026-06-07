"""
SAGCO Target — PXE Netboot
Serves the organism over PXE so HP OmniDesk (or any bare-metal node)
can boot and receive the organism without USB or manual install.

Requires: dnsmasq, tftpd-hpa, nfs-kernel-server (or HTTP fallback)

sagco replicate --target pxe --ip 192.168.1.98 --mode full
sagco replicate --target pxe --via nfs --export /srv/pxe/sagco
"""

from __future__ import annotations
import os
import shutil
import subprocess
import time
from pathlib import Path

from sagco_true.replicator.manifest import OrganismManifest
from sagco_true.replicator.diff import DiffResult
from .base import BaseTarget, ReplicateResult


DEFAULT_PXE_ROOT    = "/srv/pxe/sagco-world"
DEFAULT_TFTP_ROOT   = "/srv/tftp"
DEFAULT_NFS_EXPORT  = "/srv/pxe"
GRUB_CFG_TEMPLATE = """\
set default=0
set timeout=5

menuentry "SAGCO Organism — netboot" {{
    linux   /sagco/vmlinuz net.ifnames=0 biosdevname=0 \\
            sagco.cell={cell_id} sagco.server={server_ip} \\
            sagco.root=nfs:{server_ip}:{nfs_export}
    initrd  /sagco/initrd.img
}}

menuentry "SAGCO Recovery Shell" {{
    linux   /sagco/vmlinuz init=/bin/sh sagco.recovery=1
    initrd  /sagco/initrd.img
}}
"""

DNSMASQ_SNIPPET = """\
# SAGCO PXE proxy-DHCP snippet — append to /etc/dnsmasq.conf
# (proxy mode: does NOT replace router DHCP, just adds boot options)
dhcp-range={iface},{server_ip},proxy
dhcp-boot=grubx64.efi
enable-tftp
tftp-root={tftp_root}
pxe-service=x86PC,"SAGCO Netboot",grubx64.efi
pxe-service=X86-64_EFI,"SAGCO EFI Netboot",grubx64.efi
"""


class PXETarget(BaseTarget):
    name = "pxe"
    description = "PXE netboot — serve organism to bare-metal nodes over TFTP/NFS"

    def __init__(
        self,
        server_ip: str = "192.168.1.98",   # Lyra LAN IP
        pxe_root: str = DEFAULT_PXE_ROOT,
        tftp_root: str = DEFAULT_TFTP_ROOT,
        nfs_export: str = DEFAULT_NFS_EXPORT,
        iface: str = "eth0",
    ) -> None:
        self.server_ip  = server_ip
        self.pxe_root   = Path(pxe_root)
        self.tftp_root  = Path(tftp_root)
        self.nfs_export = nfs_export
        self.iface      = iface

    def probe(self) -> bool:
        ok = True
        if not shutil.which("dnsmasq"):
            print("  ! dnsmasq not found — install: sudo apt install dnsmasq")
            ok = False
        if not shutil.which("tftpd-hpa") and not Path("/usr/sbin/in.tftpd").exists():
            print("  ! tftpd-hpa not found — install: sudo apt install tftpd-hpa")
            ok = False
        # Check NFS (optional — warn but don't fail)
        if not shutil.which("exportfs"):
            print("  ~ nfs-kernel-server not found (optional, HTTP fallback available)")
        return ok

    def get_manifest(self) -> OrganismManifest | None:
        mp = self.pxe_root / "SAGCO_MANIFEST.json"
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
        errors: list[str] = []
        copied = 0
        bytes_copied = 0

        if not dry_run:
            try:
                self.pxe_root.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                return ReplicateResult(
                    target_name=f"pxe:{self.server_ip}",
                    target_type="pxe",
                    success=False,
                    files_copied=0,
                    bytes_copied=0,
                    skipped=len(diff.unchanged),
                    errors=[f"Cannot create PXE root {self.pxe_root}: {e}"],
                    duration_s=time.time() - t0,
                )

        for delta in diff.changes:
            src = source_root / delta.path
            dst = self.pxe_root / delta.path
            if dry_run:
                print(f"  [dry] → pxe:{delta.path}")
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
            dst = self.pxe_root / delta.path
            if not dry_run and dst.exists():
                try:
                    dst.unlink()
                except Exception as e:
                    errors.append(f"delete {delta.path}: {e}")

        manifest_path = None
        if not dry_run and not errors:
            try:
                source_manifest.save(self.pxe_root / "SAGCO_MANIFEST.json")
                manifest_path = str(self.pxe_root / "SAGCO_MANIFEST.json")
            except Exception as e:
                errors.append(f"manifest: {e}")

            # Write GRUB config into TFTP root
            self._write_grub_config(source_manifest.cell_id)

            # Write dnsmasq snippet for operator reference
            self._write_dnsmasq_snippet()

            # Print NFS export hint
            self._print_nfs_hint()

        return ReplicateResult(
            target_name=f"pxe:{self.server_ip}",
            target_type="pxe",
            success=not errors,
            files_copied=copied,
            bytes_copied=bytes_copied,
            skipped=len(diff.unchanged),
            errors=errors,
            manifest_path=manifest_path,
            duration_s=time.time() - t0,
        )

    def _write_grub_config(self, cell_id: str) -> None:
        grub_dir = self.tftp_root / "grub"
        try:
            grub_dir.mkdir(parents=True, exist_ok=True)
            cfg = GRUB_CFG_TEMPLATE.format(
                cell_id=cell_id,
                server_ip=self.server_ip,
                nfs_export=self.nfs_export,
            )
            (grub_dir / "grub.cfg").write_text(cfg)
        except Exception as e:
            print(f"  ~ GRUB config not written: {e}")

    def _write_dnsmasq_snippet(self) -> None:
        snippet_path = self.pxe_root / "dnsmasq_pxe.conf"
        try:
            snippet = DNSMASQ_SNIPPET.format(
                iface=self.iface,
                server_ip=self.server_ip,
                tftp_root=str(self.tftp_root),
            )
            snippet_path.write_text(snippet)
            print(f"\n  PXE config written: {snippet_path}")
            print(f"  Append to /etc/dnsmasq.conf and: sudo systemctl restart dnsmasq")
        except Exception:
            pass

    def _print_nfs_hint(self) -> None:
        print(f"\n  NFS export hint:")
        print(f"    echo '{self.nfs_export} 192.168.1.0/24(ro,no_subtree_check)' >> /etc/exports")
        print(f"    sudo exportfs -ra")
        print(f"    sudo systemctl restart nfs-kernel-server")

    def verify(self, manifest: OrganismManifest):
        from sagco_true.replicator.integrity import verify
        return verify(manifest, self.pxe_root)

    def config_summary(self) -> str:
        lines = [
            f"PXE Target: {self.server_ip}",
            f"  Organism root : {self.pxe_root}",
            f"  TFTP root     : {self.tftp_root}",
            f"  NFS export    : {self.nfs_export}",
            f"  Interface     : {self.iface}",
            "",
            "Boot flow:",
            "  1. HP OmniDesk BIOS → boot from network",
            "  2. DHCP broadcast → dnsmasq proxy answers with TFTP/grubx64.efi",
            "  3. GRUB loads grub.cfg from TFTP root",
            "  4. Kernel + initrd pulled over TFTP",
            "  5. Kernel mounts NFS root → organism runs",
        ]
        return "\n".join(lines)
