"""
KHAOS Glyph System — 64-symbol visual language
Source: Poem_glyphs_periodic_table_proof_of_concept

32 unique glyphs extracted from the KHAOS poem.
Padded to 64 with variant suffixes.
Each glyph maps to a KHAOS element (ID % 64 → glyph).

Base strokes: /  —  ╱  |  ]  ╲
Modifiers:    none  •  ••  +  ○  ̄  _  ⌐  ∧  ◇  ∨  ~  ⌐⌐  ◉

Musical mapping (from sheet music doc):
  Key: C major
  Tempo: 120 BPM
  Note: MIDI 60 (C4) + glyph_id % 12
  Octave: +1 every 12 glyphs
  Families: by base stroke → modulate instrument/timbre
"""

from __future__ import annotations
from dataclasses import dataclass


# ── 64 glyphs ─────────────────────────────────────────────────────────────
# From poem extraction + variant padding. Exactly as documented.

GLYPHS: list[str] = [
    # 0–11: / family (base stroke = /)
    "/",    "/•",   "/••",  "/+",   "/○",  "/̄",   "/_",   "/⌐",
    "/◉",   "/⌐⌐",  "/~",   "/∧",
    # 12–21: — family (base stroke = —)
    "—",    "—•",   "—••",  "—⌐",   "—∧",  "—◇",  "—○",   "—+",
    "—~",   "—∨",
    # 22: extra — family
    "—_",
    # 23–32: ╱ family
    "╱",    "╱•",   "╱••",  "╱+",   "╱○",  "╱̄",   "╱_",   "╱⌐",
    "╱∧",   "╱◇",
    # 33–43: | family
    "|",    "|•",   "|••",  "|+",   "|○",  "|̄",   "|_",   "|⌐",
    "|∧",   "|~",   "|∨",
    # 44–54: ] family
    "]",    "]•",   "]••",  "]+",   "]○",  "]◇",  "]̄",   "]_",
    "]⌐",   "]∧",   "]~",
    # 55–63: ╲ family
    "╲",    "╲•",   "╲••",  "╲+",   "╲○",  "╲̄",   "╲_",   "╲⌐",
    "╲∧",
]

# Pad to exactly 64
while len(GLYPHS) < 64:
    GLYPHS.append(f"variant_{len(GLYPHS)}")


# ── Glyph families ────────────────────────────────────────────────────────

FAMILIES: dict[str, list[int]] = {
    "/":  list(range(0,  12)),
    "—":  list(range(12, 23)),
    "╱":  list(range(23, 33)),
    "|":  list(range(33, 44)),
    "]":  list(range(44, 55)),
    "╲":  list(range(55, 64)),
}

FAMILY_INSTRUMENTS = {
    "/":  "flute",      # ascending, bright
    "—":  "strings",    # sustained, horizontal
    "╱":  "piano",      # diagonal, versatile
    "|":  "organ",      # vertical, sustained
    "]":  "bell",       # angular, sharp attack
    "╲":  "bass",       # descending, dark
}


# ── Musical mapping ───────────────────────────────────────────────────────

BASE_MIDI = 60   # C4
TEMPO_BPM = 120

def glyph_to_midi(glyph_id: int) -> int:
    """MIDI note = 60 (C4) + id % 12; octave +1 every 12 glyphs."""
    octave_shift = (glyph_id // 12) * 12
    return BASE_MIDI + octave_shift + (glyph_id % 12)

def glyph_to_note(glyph_id: int) -> str:
    """Return note name (e.g. C4, D#5)."""
    notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    midi = glyph_to_midi(glyph_id)
    octave = (midi // 12) - 1
    note = notes[midi % 12]
    return f"{note}{octave}"

def glyph_family(glyph_id: int) -> str:
    for fam, ids in FAMILIES.items():
        if glyph_id in ids:
            return fam
    return "?"

def glyph_instrument(glyph_id: int) -> str:
    return FAMILY_INSTRUMENTS.get(glyph_family(glyph_id), "unknown")


# ── Encoding/decoding ─────────────────────────────────────────────────────

def encode(data: str | bytes) -> list[str]:
    """Encode bytes as a sequence of glyphs (each byte → glyph via id % 64)."""
    if isinstance(data, str):
        data = data.encode()
    return [GLYPHS[b % 64] for b in data]

def decode(glyphs: list[str]) -> bytes:
    """Decode glyph sequence back to bytes (reverse of encode)."""
    glyph_index = {g: i for i, g in enumerate(GLYPHS)}
    result = []
    for g in glyphs:
        idx = glyph_index.get(g, 0)
        result.append(idx % 256)
    return bytes(result)

def to_score(glyphs: list[str]) -> list[dict]:
    """Convert glyph sequence to sheet music score entries."""
    score = []
    beat_duration = 60.0 / TEMPO_BPM  # seconds per beat
    for i, g in enumerate(glyphs):
        gid = GLYPHS.index(g) if g in GLYPHS else 0
        score.append({
            "beat":       i,
            "time_s":     i * beat_duration,
            "glyph":      g,
            "glyph_id":   gid,
            "midi":       glyph_to_midi(gid),
            "note":       glyph_to_note(gid),
            "family":     glyph_family(gid),
            "instrument": glyph_instrument(gid),
            "duration_s": beat_duration,
        })
    return score

def print_table() -> None:
    print(f"\n  KHAOS Glyph System — 64 Symbols")
    print(f"  Key: C major  Tempo: {TEMPO_BPM} BPM  Base MIDI: {BASE_MIDI}")
    print("  " + "─" * 60)
    print(f"  {'ID':>4}  {'Glyph':<8}  {'Family':<6}  {'Note':<5}  {'MIDI':>4}  Instrument")
    print("  " + "─" * 60)
    for i, g in enumerate(GLYPHS):
        fam = glyph_family(i)
        note = glyph_to_note(i)
        midi = glyph_to_midi(i)
        inst = glyph_instrument(i)
        print(f"  {i:>4}  {g:<8}  {fam:<6}  {note:<5}  {midi:>4}  {inst}")
