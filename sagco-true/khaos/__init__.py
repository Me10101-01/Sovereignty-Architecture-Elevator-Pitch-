"""
KHAOS — Periodic Table of Process States
SAGCO vibrational layer / spectral anomaly detection system

Modules:
  elements   — 72-element registry (Hz, band, color, oxidation, note)
  oscillator — tri-channel phase coherence monitor (RED/BLUE/PURPLE)
  glyph      — 64-symbol visual language (poem glyphs → sheet music)
  hymn       — DNA strand → WAV encoder (pure stdlib, Termux-safe)
  bridge     — KHAOS ↔ SAGCO signal routing

Quick start:
  from sagco_true.khaos import elements, oscillator, hymn, bridge

  # List the table
  elements.print_table()

  # Encode a DNA strand as audio
  hymn.encode_strand("SAGCO-BOOT-IRREFUTABLE", "boot.wav")

  # Monitor live coherence
  osc = oscillator.KHAOSOscillator()
  osc.feed_metrics({"cpu": 42, "mem": 30, "err_count": 0})
  result = osc.measure()
  print(result.status)  # ALIGNED | DRIFTING | ANOMALY

  # Bridge to SAGCO signals
  br = bridge.KHAOSBridge()
  br.ingest_signal("boot_complete", {"world": "linux"})
  print(br.resonance_report())
"""

from .elements import (
    Element, TABLE, BY_NAME, BY_ID, BY_BAND, BY_CHANNEL,
    BANDS, OXIDATION_PRIVILEGES,
    get, oxidize, from_hash, print_table,
)
from .oscillator import KHAOSOscillator, ChannelState, CoherenceResult
from .glyph import GLYPHS, FAMILIES, encode as glyph_encode, decode as glyph_decode, to_score
from .hymn import encode_strand, encode_text, encode_elements, encode_table_hymn, print_strand_score
from .bridge import KHAOSBridge, ProcessClassification
from .monitor import KHAOSMonitor, MonitorSnapshot, read_procs, system_metrics
from .calendar import (
    gregorian_to_jdn, jdn_to_gregorian, today_jdn,
    compare_all, eru_burn_rate, calendar_date,
    primameria_day, today_vortex, daily_rite_wav,
    PrimameriaDay, CalendarComparison, EruBurnRate,
    print_full_report, print_primameria, print_calendar_table, print_eru_report,
)

__version__ = "1.0.0"
__all__ = [
    "Element", "TABLE", "BY_NAME", "BY_ID", "BY_BAND", "BY_CHANNEL",
    "get", "oxidize", "from_hash", "print_table",
    "KHAOSOscillator", "ChannelState", "CoherenceResult",
    "GLYPHS", "FAMILIES", "glyph_encode", "glyph_decode", "to_score",
    "encode_strand", "encode_text", "encode_elements", "encode_table_hymn",
    "print_strand_score", "KHAOSBridge",
    "gregorian_to_jdn", "jdn_to_gregorian", "today_jdn",
    "compare_all", "eru_burn_rate", "calendar_date",
    "primameria_day", "today_vortex", "daily_rite_wav",
    "PrimameriaDay", "CalendarComparison", "EruBurnRate",
    "print_full_report", "print_primameria", "print_calendar_table", "print_eru_report",
]
