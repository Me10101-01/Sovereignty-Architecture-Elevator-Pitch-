"""
KHAOS Hymn — DNA strand → WAV encoder
Pure Python stdlib. No dependencies. Runs on Termux.

Encodes a SAGCO DNA strand or arbitrary text as a WAV audio file.

Audio model:
  Left  channel: carrier frequency (hz) with binaural beat subtracted
  Right channel: carrier frequency (hz) with binaural beat added
  → brain hears the beat (difference frequency) as AM envelope

  Each codon/character → element lookup → carrier + beat + oxidation harmonics

Format: 16-bit PCM, 44100 Hz, stereo

Usage:
  from sagco_true.khaos.hymn import encode_strand, encode_text
  encode_strand("SAGCO-ATG-FLM2-KERNEL", "khaos_hymn.wav")
  encode_text("Hello SAGCO", "hello.wav")
"""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Any

from .elements import Element, TABLE, from_hash

SAMPLE_RATE = 44100
CHANNELS    = 2
SAMPLE_WIDTH = 2  # 16-bit


# ── WAV utilities ─────────────────────────────────────────────────────────

def _pack_sample(val: float) -> bytes:
    """Clamp to [-1,1], scale to int16, pack as little-endian."""
    clamped = max(-1.0, min(1.0, val))
    return struct.pack("<h", int(clamped * 32767))


def _write_wav(path: str | Path, frames: list[bytes], sample_rate: int = SAMPLE_RATE) -> None:
    with wave.open(str(path), "wb") as w:
        w.setnchannels(CHANNELS)
        w.setsampwidth(SAMPLE_WIDTH)
        w.setframerate(sample_rate)
        w.writeframes(b"".join(frames))


# ── Single-element tone generator ─────────────────────────────────────────

def element_tone(
    element: Element,
    duration_s: float = 0.5,
    amplitude: float = 0.6,
    sample_rate: int = SAMPLE_RATE,
    fade_ms: float = 10.0,
) -> list[bytes]:
    """
    Generate stereo PCM frames for one KHAOS element.

    Left:  A·sin(2π(hz)·t)         — base carrier
    Right: A·sin(2π(hz+beat)·t)    — binaural offset

    If oxidation > 0: add harmonics at hz*2, hz*3 (privilege harmonics)
    If oxidation < 0: add undertone at hz/2 (isolation sub-harmonic)
    """
    hz    = element.hz
    beat  = element.beat
    ox    = element.oxidation
    n_samples = int(duration_s * sample_rate)
    fade_n    = int(fade_ms * sample_rate / 1000)
    frames: list[bytes] = []

    for i in range(n_samples):
        t = i / sample_rate

        # Binaural pair
        left  = amplitude * math.sin(2 * math.pi * hz * t)
        right = amplitude * math.sin(2 * math.pi * (hz + beat) * t)

        # Oxidation harmonics (privilege encoding)
        if ox > 0:
            for h in range(2, ox + 2):
                harmonic_amp = amplitude * 0.15 / h
                left  += harmonic_amp * math.sin(2 * math.pi * hz * h * t)
                right += harmonic_amp * math.sin(2 * math.pi * (hz + beat) * h * t)

        # Isolation sub-harmonic
        if ox < 0:
            sub_amp = amplitude * 0.1 * abs(ox)
            left  += sub_amp * math.sin(2 * math.pi * (hz / 2) * t)
            right += sub_amp * math.sin(2 * math.pi * ((hz + beat) / 2) * t)

        # Fade in/out
        fade = 1.0
        if i < fade_n:
            fade = i / fade_n
        elif i > n_samples - fade_n:
            fade = (n_samples - i) / fade_n

        left  *= fade
        right *= fade

        frames.append(_pack_sample(left) + _pack_sample(right))

    return frames


# ── Strand encoder ────────────────────────────────────────────────────────

def _strand_to_elements(strand: str) -> list[tuple[Element, float]]:
    """
    Convert a SAGCO DNA strand string to (element, duration) pairs.

    Strand format: "SAGCO-ATG-FLM2-KERNEL"
    Codons split by "-". Each codon hashes to an element.
    Duration = codon length * 0.1s (longer codons = longer notes)
    """
    codons = strand.strip().split("-")
    pairs: list[tuple[Element, float]] = []
    for codon in codons:
        if not codon:
            continue
        el = from_hash(codon)
        dur = max(0.1, len(codon) * 0.08)
        pairs.append((el, dur))
    return pairs


def encode_strand(
    strand: str,
    output_path: str | Path = "khaos_hymn.wav",
    amplitude: float = 0.6,
) -> Path:
    """
    Encode a SAGCO DNA strand as a KHAOS WAV hymn.

    Example strand: "SAGCO-ATG-FLM2-KERNEL-BOOT-TICK-IRREFUTABLE"
    """
    pairs = _strand_to_elements(strand)
    all_frames: list[bytes] = []
    for el, dur in pairs:
        all_frames.extend(element_tone(el, dur, amplitude))
    output_path = Path(output_path)
    _write_wav(output_path, all_frames)
    return output_path


def encode_text(
    text: str,
    output_path: str | Path = "khaos_text.wav",
    note_duration: float = 0.15,
    amplitude: float = 0.5,
) -> Path:
    """
    Encode arbitrary text as a KHAOS WAV.
    Each character → element via hash → tone.
    """
    all_frames: list[bytes] = []
    for char in text:
        el = from_hash(char.encode())
        all_frames.extend(element_tone(el, note_duration, amplitude))
    output_path = Path(output_path)
    _write_wav(output_path, all_frames)
    return output_path


def encode_elements(
    elements: list[Element],
    output_path: str | Path = "khaos_sequence.wav",
    note_duration: float = 0.4,
    amplitude: float = 0.6,
) -> Path:
    """Encode a list of elements directly to WAV."""
    all_frames: list[bytes] = []
    for el in elements:
        all_frames.extend(element_tone(el, note_duration, amplitude))
    output_path = Path(output_path)
    _write_wav(output_path, all_frames)
    return output_path


def encode_table_hymn(
    output_path: str | Path = "khaos_table_hymn.wav",
    note_duration: float = 0.3,
    amplitude: float = 0.5,
) -> Path:
    """
    Encode the full 72-element table as the KHAOS Hymn.
    Silence at origin (element 0, delta, deep rest).
    Crescendo at gamma (elements 60–71, alert).
    Closes the circle by returning to delta.
    """
    all_frames: list[bytes] = []
    # Forward: delta → theta → alpha → beta → high_beta → gamma (crescendo)
    for el in TABLE:
        amp = amplitude * (0.3 + 0.7 * (el.id / 71.0))  # volume rises
        all_frames.extend(element_tone(el, note_duration, amp))
    # Closing: brief silence then return to element 0
    silence = [_pack_sample(0.0) + _pack_sample(0.0)] * int(0.3 * SAMPLE_RATE)
    all_frames.extend(silence)
    all_frames.extend(element_tone(TABLE[0], 0.8, amplitude * 0.4))
    output_path = Path(output_path)
    _write_wav(output_path, all_frames)
    return output_path


# ── Score display ─────────────────────────────────────────────────────────

def print_strand_score(strand: str) -> None:
    pairs = _strand_to_elements(strand)
    print(f"\n  KHAOS Strand Score: {strand}")
    print(f"  {'#':>3}  {'Codon':<16}  {'Element':<20}  {'Hz':>8}  {'Band':<10}  {'Note':<6}  {'Dur':>5}s")
    print("  " + "─" * 72)
    for i, (el, dur) in enumerate(pairs):
        codon = strand.split("-")[i] if i < len(strand.split("-")) else "?"
        print(f"  {i:>3}  {codon:<16}  {el.name:<20}  {el.hz:>8.1f}  {el.band:<10}  {el.note:<6}  {dur:>5.2f}")
    total = sum(d for _, d in pairs)
    print(f"\n  Total duration: {total:.2f}s  |  {len(pairs)} codons")
