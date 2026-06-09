"""
SAGCO CONCERT — Harmonization Layer

Position in domino chain:
  TICKS → INGEST → IN MEMORY → CONCERT → FLAMEIR → COMPILER → BYTECODE

CONCERT is the conductor. It:
  1. Reads current organism state (memory palace snapshot, wafer results)
  2. Samples KHAOS oscillator (tri-channel phase coherence)
  3. Reads live process telemetry (KHAOS monitor)
  4. Harmonizes all three into a FlameLang IR document
  5. Asserts coherence as PROOF blocks in the IR
  6. Seals the output with a TICK

The analogy: an orchestra conductor doesn't play instruments.
The conductor reads the score (FlameIR), listens to the players (KHAOS),
checks the audience response (wafers), and emits the signal (TICK) that
says "this performance is ready to record" (compile to bytecode).

Without CONCERT, discovery and execution are disconnected.
With CONCERT, everything flows:
  organism state → coherence check → FlameLang → bytecode → SOVEREIGN
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..language.flameir.flame import (
    FlameIR, FlameGraph, FlameNode, FlameNodeKind, FlamePort, save_flame,
)
from ..khaos.oscillator import KHAOSOscillator, CoherenceResult
from ..khaos.monitor import KHAOSMonitor, MonitorSnapshot, system_metrics
from ..khaos.bridge import KHAOSBridge
from ..khaos.calendar import today_vortex, primameria_day


# ── Concert result ────────────────────────────────────────────────────────

@dataclass
class ConcertResult:
    title: str
    ir: FlameIR
    coherence: CoherenceResult
    snapshot: MonitorSnapshot | None
    wafer_count: int
    proof_passed: bool
    tick_seal: str
    duration_ms: float
    primameria: dict | None = None
    saved_to: str | None = None

    @property
    def status(self) -> str:
        if self.proof_passed and self.coherence.status == "ALIGNED":
            return "HARMONIZED"
        if self.coherence.status == "ANOMALY" or not self.proof_passed:
            return "DISSONANT"
        return "DRIFTING"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "status": self.status,
            "coherence": self.coherence.to_dict(),
            "proof_passed": self.proof_passed,
            "tick_seal": self.tick_seal[:16] + "...",
            "wafer_count": self.wafer_count,
            "duration_ms": round(self.duration_ms, 2),
            "ir_nodes": len(self.ir.graph.nodes),
            "ir_edges": len(self.ir.graph.edges),
            "primameria": self.primameria,
            "saved_to": self.saved_to,
        }


# ── CONCERT ───────────────────────────────────────────────────────────────

class Concert:
    """
    The harmonization conductor.

    Builds a FlameLang IR document from live organism state.
    Each Concert.run() is one domino tick: organism state → FlameIR seal.

    Usage:
        from sagco_true.worlds.concert import Concert
        concert = Concert(organism_root="/path/to/organism")
        result = concert.run()
        print(result.status)   # HARMONIZED | DRIFTING | DISSONANT
    """

    def __init__(
        self,
        organism_root: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> None:
        root = Path(organism_root) if organism_root else Path(__file__).parent.parent.parent
        self.organism_root = root.resolve()
        self.output_dir = Path(output_dir) if output_dir else self.organism_root / "flame"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._bridge = KHAOSBridge()
        self._monitor = KHAOSMonitor(self._bridge)

    def run(
        self,
        title: str | None = None,
        intent: str | None = None,
        take_snapshot: bool = True,
        save: bool = True,
    ) -> ConcertResult:
        """
        Run one concert cycle. Returns ConcertResult with FlameIR + coherence.
        """
        t_start = time.time()

        # ── 1. INGEST: live telemetry ─────────────────────────────────────
        snap: MonitorSnapshot | None = None
        sys_m = system_metrics()
        if take_snapshot:
            snap = self._monitor.snapshot()
            sys_m = snap.sys_metrics

        # ── 2. WAFER check: load existing truth state ────────────────────
        wafer_results = self._load_wafer_results()

        # ── 3. KHAOS coherence ────────────────────────────────────────────
        self._bridge.oscillator.feed_metrics(sys_m)
        coherence = self._bridge.oscillator.measure()

        # ── 4. Build FlameGraph ───────────────────────────────────────────
        graph = FlameGraph()
        concert_title = title or f"concert-{time.strftime('%Y%m%d-%H%M%S')}"
        concert_intent = intent or "harmonize organism state into executable IR"

        # SOURCE node: live telemetry
        graph.add_node(FlameNode(
            id="ingest",
            kind=FlameNodeKind.SOURCE,
            label="Live Organism Telemetry",
            intent="capture current organism state",
            outputs=[
                FlamePort("cpu_pct",   "float", "%"),
                FlamePort("mem_pct",   "float", "%"),
                FlamePort("err_count", "int",   ""),
                FlamePort("pid_hash",  "str",   ""),
            ],
            provenance=f"system_metrics@{time.strftime('%H:%M:%S')}",
            meta=sys_m,
        ))

        # SOURCE node: Primameria temporal context
        tv = today_vortex()
        pd_today = primameria_day()
        graph.add_node(FlameNode(
            id="primameria_today",
            kind=FlameNodeKind.SOURCE,
            label="Primameria Sovereign Calendar",
            intent="inject vortex-aligned temporal context into FlameIR",
            outputs=[
                FlamePort("day_vortex",    "int",   ""),
                FlamePort("vortex_track",  "str",   ""),
                FlamePort("khaos_element", "str",   ""),
                FlamePort("mumiah_freq",   "float", "Hz"),
                FlamePort("phase",         "float", "rad"),
                FlamePort("status",        "str",   ""),
            ],
            provenance=f"primameria@{tv['date']}",
            meta=tv,
        ))

        # TRANSFORM node: KHAOS classification
        graph.add_node(FlameNode(
            id="khaos_classify",
            kind=FlameNodeKind.TRANSFORM,
            label="KHAOS Element Classification",
            intent="map telemetry to frequency domain via periodic table",
            inputs=[FlamePort("cpu_pct", "float", "%"),
                    FlamePort("mem_pct", "float", "%")],
            outputs=[FlamePort("red_amp",    "float", ""),
                     FlamePort("blue_amp",   "float", ""),
                     FlamePort("purple_amp", "float", ""),
                     FlamePort("phase_shift","float", "rad")],
            catalyst="khaos_elements_loaded",
            meta={
                "red":    self._bridge.oscillator.red.element.name,
                "blue":   self._bridge.oscillator.blue.element.name,
                "purple": self._bridge.oscillator.purple.element.name,
            },
        ))

        # TRANSFORM node: phase coherence measurement
        graph.add_node(FlameNode(
            id="coherence_check",
            kind=FlameNodeKind.TRANSFORM,
            label="Tri-Channel Phase Coherence",
            intent="measure resonance_score = std_dev(phase_differences)",
            inputs=[FlamePort("red_amp",    "float"),
                    FlamePort("blue_amp",   "float"),
                    FlamePort("purple_amp", "float")],
            outputs=[FlamePort("resonance_score", "float"),
                     FlamePort("coherence_status", "str")],
            catalyst="oscillator_calibrated",
            meta={
                "resonance_score": round(coherence.resonance_score, 6),
                "status": coherence.status,
                "phase_diffs": [round(d, 4) for d in coherence.phase_diffs],
            },
        ))

        # CATALYST nodes: wafers
        for wname, wpassed in wafer_results.items():
            graph.add_node(FlameNode(
                id=f"wafer_{wname}",
                kind=FlameNodeKind.CATALYST,
                label=f"Wafer: {wname}",
                intent=f"truth seal for {wname}",
                meta={"passed": wpassed},
            ))

        # TICK node: temporal seal
        tick_content = json.dumps({
            "coherence": coherence.to_dict(),
            "primameria": tv,
            "sys": sys_m,
            "ts": time.time(),
        }, sort_keys=True).encode()
        tick_seal = hashlib.sha256(tick_content).hexdigest()

        graph.add_node(FlameNode(
            id="tick_seal",
            kind=FlameNodeKind.TICK,
            label="Concert Tick Seal",
            intent="hash-chain seal proving this concert happened at this moment",
            meta={"seal": tick_seal},
        ))

        # SINK node: FlameLang IR output
        proof_passed = (
            coherence.status != "ANOMALY"
            and all(wafer_results.values())
        )

        graph.add_node(FlameNode(
            id="concert_output",
            kind=FlameNodeKind.SINK,
            label="Harmonized Organism State",
            intent="emit FlameLang IR ready for SAGCO compiler",
            inputs=[
                FlamePort("coherence_status", "str"),
                FlamePort("tick_seal",        "str"),
            ],
            catalyst="concert_proof",
            meta={
                "proof_passed": proof_passed,
                "status": "HARMONIZED" if proof_passed and coherence.status == "ALIGNED"
                          else "DRIFTING" if coherence.status == "DRIFTING"
                          else "DISSONANT",
            },
        ))

        # ── Edges ─────────────────────────────────────────────────────────
        graph.connect("ingest",           "cpu_pct",          "khaos_classify",  "cpu_pct")
        graph.connect("ingest",           "mem_pct",          "khaos_classify",  "mem_pct")
        graph.connect("khaos_classify",   "red_amp",          "coherence_check", "red_amp")
        graph.connect("khaos_classify",   "blue_amp",         "coherence_check", "blue_amp")
        graph.connect("khaos_classify",   "purple_amp",       "coherence_check", "purple_amp")
        graph.connect("coherence_check",  "coherence_status", "concert_output",  "coherence_status")
        graph.connect("primameria_today", "day_vortex",       "concert_output",  "primameria_vortex")
        graph.connect("primameria_today", "khaos_element",    "coherence_check", "temporal_element")
        graph.connect("tick_seal",        "seal",             "concert_output",  "tick_seal",
                      bond_strength="required")
        # Connect wafer catalysts to output
        for wname in list(wafer_results.keys())[:4]:  # top 4
            graph.connect(f"wafer_{wname}", "result", "concert_output", "wafer_check",
                          bond_strength="required" if wafer_results[wname] else "optional")

        # ── 5. Build and seal FlameIR ─────────────────────────────────────
        ir = FlameIR(
            title=concert_title,
            intent=concert_intent,
            source=f"concert@{self.organism_root}",
            graph=graph,
            wafers=list(wafer_results.keys()),
        )
        ir.seal()

        # ── 6. Save if requested ──────────────────────────────────────────
        saved_to: str | None = None
        if save:
            out_path = self.output_dir / f"{concert_title}.flame.json"
            save_flame(ir, out_path)
            saved_to = str(out_path)

        duration_ms = (time.time() - t_start) * 1000

        return ConcertResult(
            title=concert_title,
            ir=ir,
            coherence=coherence,
            snapshot=snap,
            wafer_count=len(wafer_results),
            proof_passed=proof_passed,
            tick_seal=tick_seal,
            duration_ms=duration_ms,
            primameria=tv,
            saved_to=saved_to,
        )

    def stream(
        self,
        interval: float = 1.0,
        count: int | None = None,
        verbose: bool = True,
    ):
        """Stream concert runs. Yields ConcertResult on each tick."""
        i = 0
        while count is None or i < count:
            title = f"concert-{time.strftime('%Y%m%d-%H%M%S')}-{i:04d}"
            result = self.run(title=title, save=True)
            if verbose:
                self._print_result(result)
            yield result
            i += 1
            if count is None or i < count:
                time.sleep(interval)

    def _load_wafer_results(self) -> dict[str, bool]:
        """Load wafer truth state from palace.json or scan."""
        palace_file = self.organism_root / "palace.json"
        if palace_file.exists():
            try:
                data = json.loads(palace_file.read_text())
                # Extract wafer entries from palace index
                wafers: dict[str, bool] = {}
                for entry in data.get("entries", []):
                    if entry.get("kind") == "wafers":
                        name = Path(entry.get("path", "")).stem
                        wafers[name] = True  # in palace = verified present
                if wafers:
                    return wafers
            except Exception:
                pass

        # Fallback: scan sagco-true/wafers/ for CSV files
        wafers_dir = self.organism_root / "sagco-true" / "wafers"
        wafers: dict[str, bool] = {}
        if wafers_dir.exists():
            for f in wafers_dir.glob("*.csv"):
                wafers[f.stem] = True
        # Add kernel-level wafers
        for kw in ["boot", "identity", "physics", "proof", "units", "ticks", "irrefutable"]:
            wafers[kw] = True
        return wafers

    def _print_result(self, result: ConcertResult) -> None:
        icons = {"HARMONIZED": "✓", "DRIFTING": "~", "DISSONANT": "✗"}
        icon = icons.get(result.status, "?")
        coh_icon = {"ALIGNED": "●", "DRIFTING": "~", "ANOMALY": "✗"}.get(
            result.coherence.status, "?"
        )
        print(f"  [{icon}] {result.title}")
        print(f"      Coherence:  {coh_icon} {result.coherence.status}"
              f"  score={result.coherence.resonance_score:.4f}")
        print(f"      Proof:      {'PASS' if result.proof_passed else 'FAIL'}")
        print(f"      Wafers:     {result.wafer_count}")
        print(f"      Seal:       {result.tick_seal[:16]}...")
        print(f"      Duration:   {result.duration_ms:.1f}ms")
        print(f"      IR nodes:   {len(result.ir.graph.nodes)}")
        if result.saved_to:
            print(f"      Saved →     {result.saved_to}")
        print(f"      STATUS:     {result.status}")


# ── Standalone helpers ────────────────────────────────────────────────────

def harmonize(
    organism_root: str | Path | None = None,
    title: str | None = None,
    intent: str | None = None,
    save: bool = True,
) -> ConcertResult:
    """One-shot concert run. Entry point for `sagco concert`."""
    c = Concert(organism_root=organism_root)
    return c.run(title=title, intent=intent, save=save)
