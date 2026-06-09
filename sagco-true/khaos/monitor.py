"""
KHAOS Live Process Monitor

Reads actual system telemetry (/proc on Linux, fallbacks on other platforms).
Maps live PIDs to KHAOS elements via hash. Feeds real metrics into the oscillator.

No external dependencies. Pure stdlib.

This is the "INGEST" step in the domino chain:
  RAW WORLD → stepper → DISCOVERED → crawler → STRUCTURED
  → ticks → TIMESTAMPED → INGEST → IN MEMORY → CONCERT

The monitor brings raw world state IN MEMORY so CONCERT can harmonize it.

What "classifying a process as a KHAOS element" means:
  Process name + PID → SHA-256 → element index
  The element's band tells you what STATE the process is in:
    delta/theta → idle, sleeping, background
    alpha/beta  → active, working
    high_beta   → stressed, high CPU
    gamma       → critical, kernel, fight-or-flight
  CPU% sets the amplitude of that channel.
  Error spikes shift the RED channel phase.
"""

from __future__ import annotations

import os
import platform
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from .elements import Element, from_hash, TABLE
from .oscillator import KHAOSOscillator, CoherenceResult
from .bridge import KHAOSBridge, ProcessClassification


@dataclass
class ProcInfo:
    pid: int
    name: str
    state: str          # R=running S=sleeping D=disk Z=zombie T=stopped
    cpu_pct: float      # 0–100
    mem_kb: int
    threads: int
    user: str = ""


# ── /proc reader (Linux + Termux) ─────────────────────────────────────────

def _read_proc_linux() -> list[ProcInfo]:
    procs: list[ProcInfo] = []
    proc_dir = Path("/proc")
    if not proc_dir.exists():
        return procs

    # cpu total for cpu% calculation
    try:
        cpu_stat = (proc_dir / "stat").read_text().split("\n")[0].split()
        total_jiffies = sum(int(x) for x in cpu_stat[1:8])
    except Exception:
        total_jiffies = 1

    for pid_path in proc_dir.iterdir():
        try:
            if not pid_path.name.isdigit():
                continue
            pid = int(pid_path.name)

            # name + state from /proc/PID/stat
            stat_text = (pid_path / "stat").read_text()
            # format: pid (name) state ...
            paren_end = stat_text.rfind(")")
            name_start = stat_text.index("(") + 1
            name = stat_text[name_start:paren_end]
            rest = stat_text[paren_end + 2:].split()
            state = rest[0] if rest else "?"
            utime = int(rest[11]) if len(rest) > 11 else 0
            stime = int(rest[12]) if len(rest) > 12 else 0
            num_threads = int(rest[17]) if len(rest) > 17 else 1
            cpu_jiffies = utime + stime
            cpu_pct = min(100.0, (cpu_jiffies / total_jiffies) * 100 * os.cpu_count())

            # memory from /proc/PID/status
            mem_kb = 0
            try:
                for line in (pid_path / "status").read_text().split("\n"):
                    if line.startswith("VmRSS:"):
                        mem_kb = int(line.split()[1])
                        break
            except Exception:
                pass

            procs.append(ProcInfo(pid, name, state, cpu_pct, mem_kb, num_threads))
        except Exception:
            continue
    return procs


def _read_proc_fallback() -> list[ProcInfo]:
    """Return minimal self-process info on non-Linux platforms."""
    import os
    return [ProcInfo(
        pid=os.getpid(),
        name="python",
        state="R",
        cpu_pct=0.0,
        mem_kb=0,
        threads=1,
        user="",
    )]


def read_procs() -> list[ProcInfo]:
    if platform.system() == "Linux":
        procs = _read_proc_linux()
        return procs if procs else _read_proc_fallback()
    return _read_proc_fallback()


# ── System-level metrics ──────────────────────────────────────────────────

def system_metrics() -> dict:
    """
    Read aggregate CPU, memory, error-signal indicators from /proc.
    Returns dict suitable for KHAOSOscillator.feed_metrics().
    """
    metrics: dict = {}

    # CPU (idle from /proc/stat)
    try:
        stat = Path("/proc/stat").read_text().split("\n")[0].split()
        vals = [int(x) for x in stat[1:]]
        idle = vals[3] if len(vals) > 3 else 0
        total = sum(vals)
        cpu_used = (1.0 - idle / total) * 100 if total else 0
        metrics["cpu"] = round(cpu_used, 1)
    except Exception:
        metrics["cpu"] = 50.0

    # Memory
    try:
        meminfo: dict[str, int] = {}
        for line in Path("/proc/meminfo").read_text().split("\n"):
            parts = line.split()
            if len(parts) >= 2:
                meminfo[parts[0].rstrip(":")] = int(parts[1])
        total_mem = meminfo.get("MemTotal", 1)
        avail_mem = meminfo.get("MemAvailable", total_mem)
        mem_used_pct = (1.0 - avail_mem / total_mem) * 100
        metrics["mem"] = round(mem_used_pct, 1)
    except Exception:
        metrics["mem"] = 50.0

    # Error signals: count processes in D (uninterruptible) or Z (zombie) state
    err_count = 0
    try:
        for pid_path in Path("/proc").iterdir():
            if not pid_path.name.isdigit():
                continue
            try:
                stat_text = (pid_path / "stat").read_text()
                paren_end = stat_text.rfind(")")
                rest = stat_text[paren_end + 2:].split()
                state = rest[0] if rest else "?"
                if state in ("D", "Z"):
                    err_count += 1
            except Exception:
                continue
    except Exception:
        pass
    metrics["err_count"] = err_count

    # PID hash — hash of running PID set (changes when processes change)
    try:
        pids = sorted(int(p.name) for p in Path("/proc").iterdir()
                      if p.name.isdigit())
        metrics["pid_hash"] = str(hash(tuple(pids)) & 0xFFFFFFFF)
    except Exception:
        metrics["pid_hash"] = "0"

    return metrics


# ── KHAOS Process Monitor ─────────────────────────────────────────────────

class KHAOSMonitor:
    """
    Live organism monitor.
    Reads /proc → classifies PIDs → feeds oscillator → measures coherence.

    Usage:
        mon = KHAOSMonitor()
        snapshot = mon.snapshot()
        print(snapshot.coherence.status)

        for snap in mon.stream(interval=1.0):
            print(snap.coherence.status, snap.top_element.name)
    """

    def __init__(self, bridge: KHAOSBridge | None = None) -> None:
        self.bridge = bridge or KHAOSBridge()
        self._snapshots: list["MonitorSnapshot"] = []

    def snapshot(self) -> "MonitorSnapshot":
        procs = read_procs()
        sys_m = system_metrics()
        self.bridge.oscillator.feed_metrics(sys_m)

        classifications: list[ProcessClassification] = []
        for p in procs[:32]:  # top 32 by PID order (fast)
            cl = self.bridge.classify_process(p.pid, p.name, p.cpu_pct,
                                              p.mem_kb / 1024.0)
            classifications.append(cl)

        coherence = self.bridge.measure()

        # Top element: highest CPU process
        top_proc = max(procs, key=lambda p: p.cpu_pct) if procs else None
        top_cl = next((c for c in classifications
                       if top_proc and c.pid == top_proc.pid), None)

        snap = MonitorSnapshot(
            ts=time.time(),
            procs=procs[:32],
            classifications=classifications,
            coherence=coherence,
            sys_metrics=sys_m,
            top_proc=top_proc,
            top_classification=top_cl,
        )
        self._snapshots.append(snap)
        return snap

    def stream(self, interval: float = 1.0, count: int | None = None) -> Iterator["MonitorSnapshot"]:
        """Yield snapshots at regular intervals. count=None → infinite."""
        i = 0
        while count is None or i < count:
            snap = self.snapshot()
            yield snap
            i += 1
            if count is None or i < count:
                time.sleep(interval)

    def print_snapshot(self, snap: "MonitorSnapshot") -> None:
        coh = snap.coherence
        icon = {"ALIGNED": "●", "DRIFTING": "~", "ANOMALY": "✗"}.get(coh.status, "?")
        ts = time.strftime("%H:%M:%S", time.localtime(snap.ts))
        print(f"\n  [{ts}] KHAOS Monitor Snapshot")
        print(f"  CPU: {snap.sys_metrics.get('cpu', 0):.1f}%  "
              f"MEM: {snap.sys_metrics.get('mem', 0):.1f}%  "
              f"ERR-PIDs: {snap.sys_metrics.get('err_count', 0)}")
        print(f"  Coherence: {icon} {coh.status}  score={coh.resonance_score:.4f}  "
              f"mix={coh.channel_mix:.4f}")
        if snap.top_proc and snap.top_classification:
            el = snap.top_classification.element
            print(f"  Top proc:  [{snap.top_proc.pid}] {snap.top_proc.name} "
                  f"→ {el.name} ({el.band}) {el.note}")
        print(f"  Procs classified: {len(snap.classifications)}")
        # Band distribution
        bands: dict[str, int] = {}
        for cl in snap.classifications:
            bands[cl.band] = bands.get(cl.band, 0) + 1
        band_str = "  ".join(f"{b}:{n}" for b, n in sorted(bands.items()))
        print(f"  Band dist: {band_str}")


@dataclass
class MonitorSnapshot:
    ts: float
    procs: list[ProcInfo]
    classifications: list[ProcessClassification]
    coherence: CoherenceResult
    sys_metrics: dict
    top_proc: ProcInfo | None
    top_classification: ProcessClassification | None

    def to_dict(self) -> dict:
        return {
            "ts": self.ts,
            "sys": self.sys_metrics,
            "coherence": self.coherence.to_dict(),
            "proc_count": len(self.procs),
            "top_proc": {
                "pid": self.top_proc.pid,
                "name": self.top_proc.name,
                "cpu": self.top_proc.cpu_pct,
                "element": self.top_classification.element.name if self.top_classification else None,
                "band": self.top_classification.band if self.top_classification else None,
            } if self.top_proc else None,
            "band_distribution": {
                band: sum(1 for c in self.classifications if c.band == band)
                for band in ["delta", "theta", "alpha", "beta", "high_beta", "gamma"]
            },
        }
