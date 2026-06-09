"""
KHAOS Tri-Channel Phase Coherence Oscillator

Three channels map to three brainwave regions:
  RED    = gamma/high_beta  — alert, fight-flight, anomaly
  BLUE   = delta/theta      — deep, foundational, structural
  PURPLE = alpha/beta       — focused, operational, nominal

Each channel: A·sin(2πf·t + φ)
  f = carrier frequency from element
  φ = encoded PID hash or health score
  A = amplitude = health / 100.0

Phase coherence detection (from technical synthesis):
  resonance_score = std_dev(phase_differences(R, B, P))
  Low variance  → aligned → HEALTHY
  High variance → unstable → ANOMALY

This is NOT mysticism. It is:
  Real-time spectral encoding of system telemetry.
  Phase coherence detection.
  Cross-correlation of process channels.
"""

from __future__ import annotations

import hashlib
import math
import statistics
import time
from dataclasses import dataclass, field
from typing import Any

from .elements import Element, TABLE, BY_CHANNEL


# ── Channel oscillator ────────────────────────────────────────────────────

@dataclass
class ChannelState:
    name: str               # RED | BLUE | PURPLE
    element: Element
    amplitude: float = 1.0  # 0.0–1.0 (health score)
    phase: float = 0.0      # φ — encoded from PID/hash
    started: float = field(default_factory=time.time)

    def value_at(self, t: float | None = None) -> float:
        """A·sin(2πf·t + φ)"""
        if t is None:
            t = time.time() - self.started
        return self.amplitude * math.sin(self.element.omega * t + self.phase)

    def phase_at(self, t: float | None = None) -> float:
        """Current phase angle in radians (mod 2π)"""
        if t is None:
            t = time.time() - self.started
        return (self.element.omega * t + self.phase) % (2 * math.pi)


# ── Phase coherence metric ────────────────────────────────────────────────

@dataclass
class CoherenceResult:
    t: float
    red_val: float
    blue_val: float
    purple_val: float
    phase_red: float
    phase_blue: float
    phase_purple: float
    phase_diffs: list[float]
    resonance_score: float    # std_dev(phase_diffs); low = aligned
    status: str               # ALIGNED | DRIFTING | ANOMALY
    channel_mix: float        # R+B+P combined value

    @property
    def is_anomaly(self) -> bool:
        return self.status == "ANOMALY"

    def to_dict(self) -> dict:
        return {
            "t": round(self.t, 4),
            "channels": {"RED": round(self.red_val, 4),
                         "BLUE": round(self.blue_val, 4),
                         "PURPLE": round(self.purple_val, 4)},
            "phases": {"RED": round(self.phase_red, 4),
                       "BLUE": round(self.phase_blue, 4),
                       "PURPLE": round(self.phase_purple, 4)},
            "resonance_score": round(self.resonance_score, 6),
            "status": self.status,
            "channel_mix": round(self.channel_mix, 4),
        }


class KHAOSOscillator:
    """
    Tri-channel phase coherence oscillator.
    Maps system metrics → frequencies → phase coherence.

    Usage:
        osc = KHAOSOscillator()
        osc.feed_metrics({"cpu": 42.0, "mem": 67.0, "err_count": 0})
        result = osc.measure()
        print(result.status)  # ALIGNED | DRIFTING | ANOMALY
    """

    # Thresholds (tunable)
    DRIFT_THRESHOLD:  float = 0.3   # resonance_score > this = DRIFTING
    ANOMALY_THRESHOLD: float = 0.8  # resonance_score > this = ANOMALY

    def __init__(self) -> None:
        self._started = time.time()
        self._history: list[CoherenceResult] = []
        self._metrics: dict[str, float] = {}

        # Default channels — pick representative elements from each band
        # RED = gamma (element 60, Umabel, 500hz) — alert channel
        # BLUE = delta (element 0, Vehuiah, 200hz) — foundational channel
        # PURPLE = beta (element 41, Michael, 405hz) — operational channel
        from .elements import BY_ID
        self.red    = ChannelState("RED",    BY_ID[60], amplitude=1.0, phase=0.0)
        self.blue   = ChannelState("BLUE",   BY_ID[0],  amplitude=1.0, phase=0.0)
        self.purple = ChannelState("PURPLE", BY_ID[41], amplitude=1.0, phase=0.0)

    def feed_metrics(self, metrics: dict[str, Any]) -> None:
        """
        Ingest live telemetry. Maps metrics to channel parameters.

        Standard metric keys:
          cpu      : 0–100 float → RED amplitude
          mem      : 0–100 float → BLUE amplitude
          err_count: int   → phase shift on RED (anomaly encoding)
          pid_hash : str   → phase on PURPLE via SHA-256 mod
        """
        self._metrics = {k: float(v) if not isinstance(v, str) else v
                         for k, v in metrics.items()}

        if "cpu" in metrics:
            self.red.amplitude = min(1.0, float(metrics["cpu"]) / 100.0)
        if "mem" in metrics:
            self.blue.amplitude = min(1.0, float(metrics["mem"]) / 100.0)
        if "health" in metrics:
            self.purple.amplitude = min(1.0, float(metrics["health"]) / 100.0)

        # Encode error count as phase shift on RED
        if "err_count" in metrics:
            err = int(float(metrics["err_count"]))
            # Each error shifts phase by π/16 (detectable but subtle)
            self.red.phase = (err * math.pi / 16) % (2 * math.pi)

        # Encode pid_hash or process signature as PURPLE phase
        if "pid_hash" in metrics:
            h = hashlib.sha256(str(metrics["pid_hash"]).encode()).digest()
            self.purple.phase = (int.from_bytes(h[:4], "big") % 628) / 100.0  # 0–2π

    def set_element(self, channel: str, element_id: int) -> None:
        """Override the element (frequency) for a channel."""
        from .elements import BY_ID
        el = BY_ID.get(element_id)
        if not el:
            return
        if channel.upper() == "RED":
            self.red.element = el
        elif channel.upper() == "BLUE":
            self.blue.element = el
        elif channel.upper() == "PURPLE":
            self.purple.element = el

    def measure(self, t: float | None = None) -> CoherenceResult:
        """
        Take a coherence measurement at time t (default: elapsed since start).

        resonance_score = std_dev(phase_differences)
        Low  = aligned  = ALIGNED
        Mid  = drifting  = DRIFTING
        High = unstable  = ANOMALY
        """
        if t is None:
            t = time.time() - self._started

        rv = self.red.value_at(t)
        bv = self.blue.value_at(t)
        pv = self.purple.value_at(t)

        rp = self.red.phase_at(t)
        bp = self.blue.phase_at(t)
        pp = self.purple.phase_at(t)

        # Phase differences (normalized to 0–π)
        diffs = [
            abs(rp - bp) % math.pi,
            abs(bp - pp) % math.pi,
            abs(rp - pp) % math.pi,
        ]
        score = statistics.stdev(diffs) if len(diffs) > 1 else 0.0

        if score > self.ANOMALY_THRESHOLD:
            status = "ANOMALY"
        elif score > self.DRIFT_THRESHOLD:
            status = "DRIFTING"
        else:
            status = "ALIGNED"

        result = CoherenceResult(
            t=t, red_val=rv, blue_val=bv, purple_val=pv,
            phase_red=rp, phase_blue=bp, phase_purple=pp,
            phase_diffs=diffs, resonance_score=score,
            status=status, channel_mix=(rv + bv + pv) / 3.0,
        )
        self._history.append(result)
        return result

    def scan(self, duration: float = 1.0, samples: int = 10) -> list[CoherenceResult]:
        """Sample the oscillator over a time window. Returns list of measurements."""
        results = []
        for i in range(samples):
            t = (i / (samples - 1)) * duration if samples > 1 else 0.0
            results.append(self.measure(t))
        return results

    def anomaly_windows(self, results: list[CoherenceResult]) -> list[tuple[float, float]]:
        """Find contiguous anomaly windows in a scan result."""
        windows: list[tuple[float, float]] = []
        start: float | None = None
        for r in results:
            if r.is_anomaly and start is None:
                start = r.t
            elif not r.is_anomaly and start is not None:
                windows.append((start, r.t))
                start = None
        if start is not None:
            windows.append((start, results[-1].t))
        return windows

    def print_scan(self, results: list[CoherenceResult]) -> None:
        print(f"\n  KHAOS Tri-Channel Coherence Scan")
        print(f"  RED  element: {self.red.element.name}  ({self.red.element.hz}hz {self.red.element.band})")
        print(f"  BLUE element: {self.blue.element.name}  ({self.blue.element.hz}hz {self.blue.element.band})")
        print(f"  PURP element: {self.purple.element.name}  ({self.purple.element.hz}hz {self.purple.element.band})")
        print(f"  {'t':>6}  {'R':>8}  {'B':>8}  {'P':>8}  {'score':>8}  status")
        print("  " + "─" * 60)
        for r in results:
            bar = "■" * int(r.resonance_score * 20)
            print(f"  {r.t:>6.3f}  {r.red_val:>8.4f}  {r.blue_val:>8.4f}  {r.purple_val:>8.4f}  {r.resonance_score:>8.4f}  {r.status}  {bar}")
        anomalies = self.anomaly_windows(results)
        print(f"\n  Anomaly windows: {len(anomalies)}")
        for a, b in anomalies:
            print(f"    [{a:.3f}s — {b:.3f}s]")
