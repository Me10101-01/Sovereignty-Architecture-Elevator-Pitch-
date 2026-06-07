"""
SAGCO Organism Cell Replicator — Main Orchestrator
Wires manifest + diff + target driver + integrity into one clean operation.

sagco replicate --target usb   --mount /Volumes/SAGCO
sagco replicate --target pi    --ip 192.168.1.42
sagco replicate --target phone --via termux
sagco replicate --target phone --via adb
sagco replicate --target pxe   --ip 192.168.1.98
sagco replicate --target local --mount /tmp/sagco-clone
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .manifest import OrganismManifest, build_manifest
from .diff import diff, diff_from_disk, DiffResult
from .integrity import verify as integrity_verify, IntegrityReport
from .targets.base import BaseTarget, ReplicateResult


# ──────────────────────────────────────────────────────────────
# Target factory
# ──────────────────────────────────────────────────────────────

def build_target(
    target: str,
    *,
    ip: str | None = None,
    mount: str | None = None,
    device: str | None = None,
    via: str = "ssh",
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    ssh_key: str | None = None,
    pxe_root: str | None = None,
    tftp_root: str | None = None,
    iface: str = "eth0",
) -> BaseTarget:
    t = target.lower().strip()

    if t in ("usb", "local"):
        from .targets.local import LocalTarget
        if not mount:
            raise ValueError("--mount required for local/usb target")
        return LocalTarget(mount_point=mount)

    if t == "pi":
        from .targets.pi import PiTarget
        h = host or ip
        if not h:
            raise ValueError("--ip or --host required for pi target")
        kwargs: dict[str, Any] = {"host": h}
        if user:     kwargs["user"]    = user
        if port:     kwargs["port"]    = port
        if ssh_key:  kwargs["ssh_key"] = ssh_key
        return PiTarget(**kwargs)

    if t in ("phone", "termux", "zfold"):
        from .targets.termux import TermuxTarget
        kwargs = {"via": via}
        if ip:   kwargs["ip"]   = ip
        if port: kwargs["port"] = port
        if user: kwargs["user"] = user
        return TermuxTarget(**kwargs)

    if t in ("pxe", "hp", "hp-omnidesk", "netboot"):
        from .targets.pxe import PXETarget
        kwargs = {}
        if ip:        kwargs["server_ip"] = ip
        if pxe_root:  kwargs["pxe_root"]  = pxe_root
        if tftp_root: kwargs["tftp_root"] = tftp_root
        kwargs["iface"] = iface
        return PXETarget(**kwargs)

    raise ValueError(
        f"Unknown target '{target}'. "
        "Known: usb, local, pi, phone, termux, zfold, pxe, hp, hp-omnidesk, netboot"
    )


# ──────────────────────────────────────────────────────────────
# Replication modes
# ──────────────────────────────────────────────────────────────

@dataclass
class ReplicationPlan:
    source_root: Path
    target: BaseTarget
    mode: str           # full | smart | minimal | verify
    dry_run: bool
    source_manifest: OrganismManifest
    target_manifest: OrganismManifest | None
    diff: DiffResult


@dataclass
class ReplicationSession:
    plan: ReplicationPlan
    result: ReplicateResult | None = None
    integrity: IntegrityReport | None = None
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    @property
    def duration_s(self) -> float:
        if self.finished_at:
            return self.finished_at - self.started_at
        return time.time() - self.started_at

    def print_summary(self) -> None:
        print(f"\n{'─'*56}")
        print(f"  SAGCO Replication Report")
        print(f"{'─'*56}")
        print(f"  Source  : {self.plan.source_root}")
        print(f"  Target  : {self.plan.target.name}")
        print(f"  Mode    : {self.plan.mode}")
        print(f"  Dry run : {self.plan.dry_run}")

        diff = self.plan.diff
        print(f"\n  Diff summary:")
        print(f"    New      : {len(diff.new)}")
        print(f"    Modified : {len(diff.modified)}")
        print(f"    Deleted  : {len(diff.deleted)}")
        print(f"    Unchanged: {len(diff.unchanged)}")

        if self.result:
            self.result.print_summary()

        if self.integrity:
            print(f"\n  Integrity: {self.integrity.status}")
            if self.integrity.failures:
                for f in self.integrity.failures[:5]:
                    print(f"    ✗ {f.path}")

        print(f"{'─'*56}\n")


# ──────────────────────────────────────────────────────────────
# Core replicate function
# ──────────────────────────────────────────────────────────────

def replicate(
    source_root: str | Path,
    target: BaseTarget,
    *,
    mode: str = "smart",
    dry_run: bool = False,
    verify: bool = True,
) -> ReplicationSession:
    source_root = Path(source_root).resolve()
    t0 = time.time()

    # 1. Probe target
    if not dry_run:
        reachable = target.probe()
        if not reachable:
            result = ReplicateResult(
                target_name=target.name,
                target_type=target.name,
                success=False,
                files_copied=0,
                bytes_copied=0,
                skipped=0,
                errors=["Target not reachable — probe() returned False"],
                duration_s=time.time() - t0,
            )
            plan = _make_plan(source_root, target, mode, dry_run)
            session = ReplicationSession(plan=plan, result=result)
            session.finished_at = time.time()
            return session

    # 2. Build source manifest
    print(f"  Building source manifest...")
    source_manifest = build_manifest(
        source_root,
        mode="full" if mode == "full" else "smart",
    )

    # 3. Get target manifest (for diff)
    print(f"  Checking target manifest...")
    target_manifest = target.get_manifest()

    # 4. Build diff
    diff_result = diff(source_manifest, target_manifest, include_deletes=(mode in ("smart", "full")))

    plan = ReplicationPlan(
        source_root=source_root,
        target=target,
        mode=mode,
        dry_run=dry_run,
        source_manifest=source_manifest,
        target_manifest=target_manifest,
        diff=diff_result,
    )

    # 5. Mode gates
    if mode == "verify":
        # verify-only: no copy, just check integrity
        report = target.verify(source_manifest)
        session = ReplicationSession(plan=plan, integrity=report)
        session.finished_at = time.time()
        return session

    if mode == "minimal" and diff_result.is_clean:
        print(f"  Target is up-to-date, nothing to do.")
        result = ReplicateResult(
            target_name=target.name,
            target_type=target.name,
            success=True,
            files_copied=0,
            bytes_copied=0,
            skipped=len(diff_result.unchanged),
            errors=[],
            duration_s=time.time() - t0,
        )
        session = ReplicationSession(plan=plan, result=result)
        session.finished_at = time.time()
        return session

    # 6. Execute replication
    total_changes = len(diff_result.changes)
    print(f"  Replicating {total_changes} file(s) to {target.name}...")
    result = target.replicate(source_root, diff_result, source_manifest, dry_run=dry_run)

    # 7. Post-replication integrity check
    integrity: IntegrityReport | None = None
    if verify and result.success and not dry_run:
        print(f"  Running integrity check...")
        try:
            integrity = target.verify(source_manifest)
        except NotImplementedError:
            pass

    session = ReplicationSession(plan=plan, result=result, integrity=integrity)
    session.finished_at = time.time()
    return session


def _make_plan(
    source_root: Path, target: BaseTarget, mode: str, dry_run: bool
) -> ReplicationPlan:
    sm = build_manifest(source_root, mode="smart")
    dr = diff(sm, None, include_deletes=False)
    return ReplicationPlan(
        source_root=source_root,
        target=target,
        mode=mode,
        dry_run=dry_run,
        source_manifest=sm,
        target_manifest=None,
        diff=dr,
    )


# ──────────────────────────────────────────────────────────────
# CLI-friendly entry point
# ──────────────────────────────────────────────────────────────

def replicate_cli(
    target_name: str,
    source_root: str | Path | None = None,
    *,
    ip: str | None = None,
    mount: str | None = None,
    device: str | None = None,
    via: str = "ssh",
    host: str | None = None,
    user: str | None = None,
    port: int | None = None,
    ssh_key: str | None = None,
    pxe_root: str | None = None,
    tftp_root: str | None = None,
    iface: str = "eth0",
    mode: str = "smart",
    dry_run: bool = False,
    verify_after: bool = True,
    print_summary: bool = True,
) -> ReplicationSession:
    if source_root is None:
        # default: two levels up from this file (sagco-true root)
        source_root = Path(__file__).parent.parent.resolve()

    target = build_target(
        target_name,
        ip=ip, mount=mount, device=device, via=via,
        host=host, user=user, port=port, ssh_key=ssh_key,
        pxe_root=pxe_root, tftp_root=tftp_root, iface=iface,
    )

    print(f"\nSAGCO Replicator")
    print(f"  Target  : {target_name}")
    print(f"  Mode    : {mode}")
    if dry_run:
        print(f"  *** DRY RUN — no files will be written ***")

    session = replicate(source_root, target, mode=mode, dry_run=dry_run, verify=verify_after)

    if print_summary:
        session.print_summary()

    return session
