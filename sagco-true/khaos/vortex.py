"""
KHAOS Vortex — 3-6-9 Module

The 3-6-9 are not arbitrary. They are the three axes that the
doubling sequence (1,2,4,8,7,5,1,2,...) never touches.

Starting from the prime 3:
  three = prime(3)          → the generator
  six   = double(three)     → the amplifier
  nine  = three + six       → the fixed point

Vortex properties (in digital root space):
  double(three) = six       → 3 oscillates to 6
  double(six)   = three     → 6 oscillates back to 3
  double(nine)  = nine      → 9 is the fixed point (attractor)

The KHAOS table (72 elements) encodes this structure without knowing it:
  Track-3 elements (position DR=3) → Hz frequencies always DR=3
  Track-6 elements (position DR=6) → Hz frequencies always DR=9 (INVERTED)
  Track-9 elements (position DR=9) → Hz frequencies always DR=6 (INVERTED)

The 6 and 9 are mirrors of each other.
The 3 is aligned with itself.
The 72-element table has DR(72)=9 — the table itself IS a 9.

In SAGCO:
  3 = three channels (RED, BLUE, PURPLE)
  6 = six brainwave bands
  9 = DR(72) = the closing note (Mumiah, 555hz, the last element)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterator

from .elements import Element, TABLE, BANDS


# ── Core 3-6-9 mathematics ────────────────────────────────────────────────

def digital_root(n: int) -> int:
    """Digital root of n. DR(9k) = 9 for k > 0. DR(0) = 0."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9


def derive_369(prime: int = 3) -> tuple[int, int, int]:
    """
    Derive the Tesla triad from a prime seed using doubling.

    three = prime
    six   = double(prime)      ← doubling operation
    nine  = three + six        ← completion / summation

    Returns (three, six, nine).
    """
    three = prime
    six   = prime * 2
    nine  = three + six
    return three, six, nine


def vortex_sequence(seed: int, steps: int = 12) -> list[int]:
    """
    Apply doubling repeatedly, recording digital roots.
    Shows whether a seed falls on the 3-6 oscillation, the 9 fixed-point,
    or the 1-2-4-8-7-5 main sequence.
    """
    result = []
    n = seed
    for _ in range(steps):
        result.append(digital_root(n))
        n *= 2
    return result


def classify_vortex(n: int) -> str:
    """Classify a number by its vortex track."""
    dr = digital_root(n)
    if dr == 3:
        return "3-track"    # oscillates 3↔6
    if dr == 6:
        return "6-track"    # oscillates 6↔3
    if dr == 9:
        return "9-track"    # fixed point, stays at 9
    return f"main-track ({dr})"   # on the 1-2-4-8-7-5 sequence


def complement(n: int) -> int:
    """
    9's complement. n + complement(n) = 9 (or 18 for two-digit).
    3 ↔ 6: complement(3) = 6, complement(6) = 3.
    9 ↔ 9: complement(9) = 9 (self-complementary).
    """
    dr = digital_root(n)
    if dr == 0 or dr == 9:
        return 9
    return 9 - dr


# ── KHAOS table vortex structure ──────────────────────────────────────────

@dataclass
class VortexTrack:
    number: int              # 3, 6, or 9
    elements: list[Element]  # KHAOS elements on this track
    hz_dr: int               # digital root of all hz values on this track


def extract_vortex_tracks() -> dict[int, VortexTrack]:
    """
    Reveal the hidden 3-6-9 structure embedded in the KHAOS 72-element table.

    Every element whose 1-indexed position has DR=3 has Hz with DR=3.
    Every element whose 1-indexed position has DR=6 has Hz with DR=9. (inverted)
    Every element whose 1-indexed position has DR=9 has Hz with DR=6. (inverted)

    The 6 and 9 tracks are mirrors. The 3 track is self-aligned.
    """
    tracks: dict[int, list[Element]] = {3: [], 6: [], 9: []}
    for el in TABLE:
        pos_dr = digital_root(el.id + 1)
        if pos_dr in tracks:
            tracks[pos_dr].append(el)

    result: dict[int, VortexTrack] = {}
    for num, elements in tracks.items():
        hz_drs = {digital_root(int(el.hz)) for el in elements}
        assert len(hz_drs) == 1, f"track-{num} hz DRs not uniform: {hz_drs}"
        result[num] = VortexTrack(num, elements, hz_drs.pop())
    return result


def vortex_summary() -> dict:
    """Return the full 3-6-9 vortex analysis as a dict."""
    three, six, nine = derive_369(prime=3)
    tracks = extract_vortex_tracks()
    return {
        "derivation": {
            "prime": 3,
            "three": three,
            "six":   six,
            "nine":  nine,
            "method": "three=prime, six=double(prime), nine=three+six",
        },
        "vortex_properties": {
            "dr_double_3":  digital_root(3 * 2),   # 6
            "dr_double_6":  digital_root(6 * 2),   # 3  ← oscillates back
            "dr_double_9":  digital_root(9 * 2),   # 9  ← fixed point
            "dr_72_table":  digital_root(72),       # 9  ← the whole table is 9
            "complement_3": complement(3),           # 6
            "complement_6": complement(6),           # 3
            "complement_9": complement(9),           # 9
        },
        "khaos_table_encoding": {
            t: {
                "position_dr": t,
                "hz_dr":       vt.hz_dr,
                "alignment":   "aligned" if t == vt.hz_dr else "inverted",
                "element_ids": [e.id for e in vt.elements],
                "hz_range":    (vt.elements[0].hz, vt.elements[-1].hz),
                "bands":       list({e.band for e in vt.elements}),
                "first":       vt.elements[0].name,
                "last":        vt.elements[-1].name,
            }
            for t, vt in tracks.items()
        },
        "sagco_mapping": {
            "3": "three channels (RED / BLUE / PURPLE)",
            "6": "six brainwave bands",
            "9": "digital root of 72 — the table closes at 9 (Mumiah, 555hz)",
        },
        "closing_element": {
            "id": TABLE[-1].id,
            "name": TABLE[-1].name,
            "hz": TABLE[-1].hz,
            "dr_position": digital_root(TABLE[-1].id + 1),
            "dr_hz": digital_root(int(TABLE[-1].hz)),
        },
    }


# ── Vortex oscillator: generate wave pattern from 3-6-9 ──────────────────

def vortex_wave(
    t: float,
    amplitude_3: float = 1.0,
    amplitude_6: float = 1.0,
    amplitude_9: float = 1.0,
) -> tuple[float, float, float]:
    """
    Three-voice vortex wave.

    Voice-3: sine at 3hz (the generator, oscillates with 6)
    Voice-6: sine at 6hz (the double, oscillates with 3)
    Voice-9: sine at 9hz (the fixed point, self-sustaining)

    At t where all three align (phase coherence):
      voice_3(t) + voice_6(t) + voice_9(t) → constructive interference
    This is the 3-6-9 resonance moment.
    """
    v3 = amplitude_3 * math.sin(2 * math.pi * 3 * t)
    v6 = amplitude_6 * math.sin(2 * math.pi * 6 * t)
    v9 = amplitude_9 * math.sin(2 * math.pi * 9 * t)
    return v3, v6, v9


def resonance_moments(duration: float = 3.0, sample_rate: int = 1000) -> list[float]:
    """
    Find times when all three voices are in constructive interference.
    These are the 3-6-9 resonance moments.
    """
    moments = []
    threshold = 2.5  # sum of three voices must exceed this
    for i in range(int(duration * sample_rate)):
        t = i / sample_rate
        v3, v6, v9 = vortex_wave(t)
        total = v3 + v6 + v9
        if total > threshold:
            moments.append(t)
    return moments


def encode_to_wav_vortex(output_path: str, duration: float = 9.0) -> str:
    """
    Encode the 3-6-9 vortex as a stereo WAV.

    Left:  voice-3 (hz=3 * 100 = 300hz) + voice-9 (hz=9 * 100 = 900... too high)
    Right: voice-6 (hz=6 * 100 = 600hz)

    Scale to audible range using KHAOS track frequencies:
      3-track carrier: 300hz (Nelchael, theta, DR-of-hz = 3)
      6-track carrier: 360hz (Iehuiah, alpha, DR-of-hz = 9 — the inversion)
      9-track carrier: 240hz (Haziel, delta, DR-of-hz = 6 — the inversion)

    Left  channel = 3-track (300hz) + 9-track (240hz)
    Right channel = 6-track (360hz) + 9-track (240hz)
    The brain hears: (360-300)=60hz beat on L/R difference
    """
    import struct, wave
    SAMPLE_RATE = 44100
    f3  = 300.0   # Nelchael  — 3-track anchor
    f6  = 360.0   # Iehuiah   — 6-track anchor (DR=9, inverted)
    f9  = 240.0   # Haziel    — 9-track anchor (DR=6, inverted)
    amp = 0.4

    frames = []
    n_samples = int(duration * SAMPLE_RATE)
    fade = int(0.02 * SAMPLE_RATE)

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # 3-voice vortex oscillation (scaled to audio range)
        v3 = amp * math.sin(2 * math.pi * f3 * t)
        v6 = amp * math.sin(2 * math.pi * f6 * t)
        v9 = amp * math.sin(2 * math.pi * f9 * t) * 0.7

        left  = v3 + v9        # 3-track + 9-track
        right = v6 + v9        # 6-track + 9-track
        # 60hz beat between left and right — the oscillation of 3↔6

        # fade
        fv = min(1.0, i / fade, (n_samples - i) / fade)
        left  *= fv
        right *= fv

        left  = max(-1.0, min(1.0, left))
        right = max(-1.0, min(1.0, right))
        frames.append(struct.pack("<h", int(left * 32767)))
        frames.append(struct.pack("<h", int(right * 32767)))

    with wave.open(output_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(b"".join(frames))
    return output_path


# ── Print helpers ─────────────────────────────────────────────────────────

def print_vortex() -> None:
    three, six, nine = derive_369(prime=3)
    tracks = extract_vortex_tracks()

    print("\n  ═══════════════════════════════════════════════════")
    print("  KHAOS VORTEX — 3·6·9 Derivation from Prime 3")
    print("  ═══════════════════════════════════════════════════")
    print()
    print(f"  prime = 3  (axiom: smallest odd prime)")
    print(f"  three = prime            = {three}")
    print(f"  six   = double(prime)    = {six}   (3 × 2)")
    print(f"  nine  = three + six      = {nine}   (3 + 6)")
    print()
    print("  Vortex properties (digital root space):")
    print(f"    dr(double(3))  = dr(6)  = {digital_root(6)}  ← 3 oscillates to 6")
    print(f"    dr(double(6))  = dr(12) = {digital_root(12)}  ← 6 oscillates back to 3")
    print(f"    dr(double(9))  = dr(18) = {digital_root(18)}  ← 9 is the fixed point")
    print()
    print("  Complements (n + complement(n) = 9):")
    print(f"    complement(3) = {complement(3)}  ← 3+6=9")
    print(f"    complement(6) = {complement(6)}  ← 6+3=9")
    print(f"    complement(9) = {complement(9)}  ← 9+9=18 → 9")
    print()
    print(f"  KHAOS table: 72 elements,  DR(72) = {digital_root(72)}  ← the table IS a 9")
    print()
    print("  Hidden structure (position DR → Hz DR):")
    labels = {3: "ALIGNED", 6: "INVERTED→9", 9: "INVERTED→6"}
    for tnum, vt in sorted(tracks.items()):
        print(f"    Track-{tnum}: pos_DR={tnum} → hz_DR={vt.hz_dr}  {labels[tnum]}"
              f"  [{vt.elements[0].name} … {vt.elements[-1].name}]")
    print()
    print(f"  Closing element: [{TABLE[-1].id}] {TABLE[-1].name}")
    print(f"    Position DR = {digital_root(TABLE[-1].id+1)}  Hz DR = {digital_root(int(TABLE[-1].hz))}")
    print(f"    Band: {TABLE[-1].band}  Hz: {TABLE[-1].hz}  Note: {TABLE[-1].note}")
    print()
    print("  Main doubling sequence (from 1): never touches 3, 6, or 9")
    seq1 = vortex_sequence(1, 12)
    print(f"    {' '.join(str(x) for x in seq1)}")
    print("  Vortex sequence from 3: oscillates 3↔6 forever")
    seq3 = vortex_sequence(3, 12)
    print(f"    {' '.join(str(x) for x in seq3)}")
    print("  Vortex sequence from 9: fixed point, never moves")
    seq9 = vortex_sequence(9, 12)
    print(f"    {' '.join(str(x) for x in seq9)}")
    print()
    print("  SAGCO organism mapping:")
    print("    3 → three channels  (RED / BLUE / PURPLE)")
    print("    6 → six brainwave bands")
    print("    9 → DR(72) = the organism's structural constant")
    print("  ═══════════════════════════════════════════════════")
