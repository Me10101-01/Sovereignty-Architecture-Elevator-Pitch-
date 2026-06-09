"""
KHAOS ↔ SAGCO Bridge

Maps KHAOS elements to SAGCO wafers, ticks, and bonds.
When a SAGCO process emits a signal, the bridge classifies it
as a KHAOS element, triggering appropriate sonification/monitoring.

The bridge makes KHAOS the SAGCO organism's nervous system:
  - Process health → oscillator amplitude
  - Error count → phase shift on RED channel
  - Boot sequence → BLUE channel tick
  - Kernel operations → PURPLE channel tick
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any

from .elements import Element, TABLE, from_hash, BY_BAND
from .oscillator import KHAOSOscillator, CoherenceResult


@dataclass
class ProcessClassification:
    pid: Any
    element: Element
    channel: str     # RED | BLUE | PURPLE
    health: float    # 0.0–1.0
    anomaly: bool
    band: str
    note: str


class KHAOSBridge:
    """
    Routes SAGCO organism signals through KHAOS.

    Usage:
        bridge = KHAOSBridge()
        bridge.ingest_signal("boot_complete", {"world": "linux"})
        result = bridge.measure()
        print(result.status)
    """

    def __init__(self) -> None:
        self.oscillator = KHAOSOscillator()
        self._log: list[dict] = []
        self._process_map: dict[str, ProcessClassification] = {}

    def ingest_signal(self, signal_name: str, payload: dict = None) -> Element:
        """
        Ingest a SAGCO bus signal. Returns the KHAOS element it maps to.
        Updates oscillator metrics based on signal type.
        """
        payload = payload or {}
        el = from_hash(f"{signal_name}:{str(sorted(payload.items()))}")

        metrics: dict[str, Any] = {}

        # Map signal names to metric channels
        signal_lower = signal_name.lower()
        if any(w in signal_lower for w in ("error", "fail", "critical", "violation")):
            metrics["err_count"] = self._log_count("errors") + 1
            metrics["cpu"] = min(100, 70 + len(self._log) * 2)
        elif any(w in signal_lower for w in ("boot", "init", "start", "genesis")):
            metrics["mem"] = 20.0
            metrics["health"] = 90.0
        elif any(w in signal_lower for w in ("tick", "seal", "qed")):
            metrics["pid_hash"] = signal_name
            metrics["health"] = 95.0
        elif any(w in signal_lower for w in ("measure", "wafer", "truth")):
            metrics["health"] = payload.get("passed", True) and 80.0 or 30.0
        else:
            metrics["health"] = 75.0

        self.oscillator.feed_metrics(metrics)
        self._log.append({
            "ts": time.time(),
            "signal": signal_name,
            "element": el.name,
            "band": el.band,
            "channel": el.channel,
        })
        return el

    def classify_process(self, pid: Any, name: str, cpu: float = 0, mem: float = 0) -> ProcessClassification:
        """Classify a system process as a KHAOS element."""
        sig = f"{name}:{pid}:{int(cpu)}:{int(mem)}"
        el = from_hash(sig)
        health = max(0.0, 1.0 - (cpu / 100) * 0.5 - (mem / 100) * 0.3)
        cl = ProcessClassification(
            pid=pid, element=el, channel=el.channel,
            health=health, anomaly=(cpu > 80 or mem > 85),
            band=el.band, note=el.note,
        )
        self._process_map[str(pid)] = cl
        return cl

    def measure(self) -> CoherenceResult:
        return self.oscillator.measure()

    def resonance_report(self) -> dict:
        result = self.measure()
        anomalies = [e for e in self._log if self._is_anomaly_signal(e["signal"])]
        return {
            "status": result.status,
            "resonance_score": round(result.resonance_score, 6),
            "channels": {
                "RED":    {"element": self.oscillator.red.element.name,
                           "hz": self.oscillator.red.element.hz,
                           "amplitude": round(self.oscillator.red.amplitude, 3)},
                "BLUE":   {"element": self.oscillator.blue.element.name,
                           "hz": self.oscillator.blue.element.hz,
                           "amplitude": round(self.oscillator.blue.amplitude, 3)},
                "PURPLE": {"element": self.oscillator.purple.element.name,
                           "hz": self.oscillator.purple.element.hz,
                           "amplitude": round(self.oscillator.purple.amplitude, 3)},
            },
            "signals_ingested": len(self._log),
            "anomaly_signals": len(anomalies),
            "last_signal": self._log[-1]["signal"] if self._log else None,
        }

    def _is_anomaly_signal(self, name: str) -> bool:
        return any(w in name.lower() for w in ("error", "fail", "critical", "violation"))

    def _log_count(self, kind: str) -> int:
        if kind == "errors":
            return sum(1 for e in self._log if self._is_anomaly_signal(e["signal"]))
        return len(self._log)

    def print_log(self, n: int = 20) -> None:
        print(f"\n  KHAOS Bridge Log ({len(self._log)} signals)")
        print(f"  {'Signal':<30}  {'Element':<20}  {'Band':<10}  Channel")
        print("  " + "─" * 70)
        for entry in self._log[-n:]:
            print(f"  {entry['signal']:<30}  {entry['element']:<20}  {entry['band']:<10}  {entry['channel']}")
