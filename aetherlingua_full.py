#!/usr/bin/env python3
"""
aetherlingua_full.py — AetherLingua: Living Glyph Language Engine
Outputs per-line 48kHz 24-bit WAVs, combined mix, SHA-256 sonic hashes, and JSON payloads.
Deterministic via seeded RNG. Includes Kemetic tokenization, Sumerian glyph sonification,
Linear‑B/Linear‑A-like wedge strike patterns, FM mapping, harmonics, charity gliss, node137 burst.
"""

import math
import struct
import hashlib
import json
import os
from typing import List, Tuple, Dict

# --- CONFIG ---
SAMPLE_RATE = 48000
BIT_DEPTH = 24
DURATION = 8.0
SEED = 1337
STRIKE_DURATION = 1.0  # Duration for wedge strike distribution in seconds
NODE137_CENTS_OFFSET = 11.0  # Microtonal offset in cents for node137 burst
PCM_24BIT_MAX = 8388607.0  # Maximum value for 24-bit signed PCM (2^23 - 1)
PCM_24BIT_MIN = -8388608  # Minimum value for 24-bit signed PCM (-2^23)

# --- Deterministic RNG ---
class DetermRng:
    """Deterministic random number generator for reproducible audio"""
    def __init__(self):
        self.state = SEED
    
    def next(self) -> int:
        self.state = (1103515245 * self.state + 12345) & 0x7fffffff
        return self.state
    
    def uniform(self) -> float:
        return float(self.next()) / 2147483647.0

rng = DetermRng()

# --- Oscillators ---
def sine(freq: float, t: float) -> float:
    """Sine wave oscillator"""
    return math.sin(2.0 * math.pi * freq * t)

def saw(freq: float, t: float) -> float:
    """Sawtooth wave oscillator"""
    phase = freq * t - math.floor(freq * t)
    return 2.0 * phase - 1.0

def triangle(freq: float, t: float) -> float:
    """Triangle wave oscillator"""
    phase = freq * t - math.floor(freq * t)
    return 1.0 - 4.0 * abs(round(phase) - phase)

# --- ADSR ---
def adsr(t: float, dur: float) -> float:
    """ADSR envelope generator"""
    a = 0.5
    d = 0.7
    s = 0.75
    r = 1.0
    if t < a:
        return t / a
    if t < a + d:
        return 1.0 - (1.0 - s) * ((t - a) / d)
    if t < dur - r:
        return s
    if t < dur:
        return s * (1.0 - ((t - (dur - r)) / r))
    return 0.0

# --- Kemetic tokenization maps ---
MULTIGRAPHS = ["ḥ", "ḫ", "ṯ", "ỉ", "ȝ", "ꜣ", "ʿ", "ḏ", "ḳ", "ḫft"]
VOWELS = set(["a", "e", "i", "o", "u", "y", "ỉ", "ȝ", "ꜣ"])
VOICED = set(["b", "d", "g", "ḏ", "ḥ", "ḫ", "ḳ"])
SIBILANTS = set(["s", "š", "ẖ", "ṯ", "ẖṭ"])
STOPS = set(["p", "t", "k", "ḳ"])
NASALS = set(["m", "n", "r", "l", "w"])

# Phoneme FM mapping (freq, index)
PHONEME_FM = {
    "vowel": (5.0, 1.8),
    "voiced": (7.0, 2.4),
    "sibilant": (12.0, 1.2),
    "stop": (18.0, 0.9),
    "nasal": (3.5, 1.1),
    "punct": (0.5, 0.6)
}

# Line carriers
LINE_CARRIERS = [110.0, 138.59, 174.61, 220.0, 277.18, 349.23]

# --- Sumerian cuneiform glyph map (example set) ---
# Each glyph maps to: phonetic, base_freq (Hz), wedge_count (for percussive strikes)
SUMERIAN_GLYPHS = {
    "DINGIR": ("an", 261.63, 5),   # divine — middle C base
    "LUGAL":  ("lugal", 196.00, 4), # king — G3 base
    "EN":     ("en", 293.66, 3),   # lord — D4 base
    "NIN":    ("nin", 329.63, 4),  # lady — E4 base
    "URU":    ("uru", 220.00, 2)   # city — A3 base
}

# Linear-B/Linear-A-like wedge/strike mapping (per glyph -> strike density & microtonal detune)
LINEAR_GLYPHS = {
    "A1": (240.0, 6, -7.0),
    "B2": (260.0, 4, 12.0),
    "C3": (280.0, 5, -3.0)
}

# --- Helpers ---
def cents_to_mult(c: float) -> float:
    """Convert cents to frequency multiplier"""
    return math.pow(2.0, c / 1200.0)

def classify(tok: str) -> str:
    """Classify phoneme token into category"""
    if tok in VOWELS:
        return "vowel"
    if tok in VOICED:
        return "voiced"
    if tok in SIBILANTS:
        return "sibilant"
    if tok in STOPS:
        return "stop"
    if tok in NASALS:
        return "nasal"
    return "punct"

def tokenize_kemetic(text: str) -> List[Tuple[str, str]]:
    """Tokenize kemetic transliteration (returns list of (token, group))"""
    tokens = []
    i = 0
    lower = text.lower()
    while i < len(lower):
        matched = False
        for mg in MULTIGRAPHS:
            if lower[i:].startswith(mg):
                tokens.append((mg, classify(mg)))
                i += len(mg)
                matched = True
                break
        if matched:
            continue
        ch = lower[i]
        if ch.isalpha():
            tokens.append((ch, classify(ch)))
        else:
            tokens.append((ch, "punct"))
        i += 1
    return tokens

def extract_sumerian_glyphs(text: str) -> List[str]:
    """Parse Sumerian glyph list in-line within text (e.g., [DINGIR])"""
    found = []
    i = 0
    while i < len(text):
        if text[i] == "[":
            j = i + 1
            while j < len(text) and text[j] != "]":
                j += 1
            if j < len(text):
                found.append(text[i+1:j])
                i = j + 1
                continue
        i += 1
    return found

def extract_linear_glyphs(text: str) -> List[str]:
    """Parse Linear glyph list in-line within text (e.g., <A1>)"""
    found = []
    i = 0
    while i < len(text):
        if text[i] == "<":
            j = i + 1
            while j < len(text) and text[j] != ">":
                j += 1
            if j < len(text):
                found.append(text[i+1:j])
                i = j + 1
                continue
        i += 1
    return found

def sumerian_glyph_signal(glyph: str, t: float) -> float:
    """Sumerian wedge strike sonification - returns additive signal for given glyph at time t"""
    if glyph not in SUMERIAN_GLYPHS:
        return 0.0
    phon, base_freq, wedges = SUMERIAN_GLYPHS[glyph]
    out = 0.0
    # strikes distributed over STRIKE_DURATION
    for w in range(wedges):
        strike_time = (w / max(1, wedges - 1)) * STRIKE_DURATION if wedges > 1 else 0.0
        dt = t - strike_time
        if dt >= 0.0 and dt < 0.6:
            # percussive bronze strike: filtered burst + microtonal cluster
            env = math.exp(-dt * 8.0)
            # base bell partial
            out += sine(base_freq * (1.0 + 0.002 * (w - wedges / 2.0)), t) * env * 0.18
            # inharmonic shimmer
            out += sine(base_freq * 2.87 * (1.0 + 0.0005 * w), t) * env * 0.06
    return out

def linear_glyph_signal(glyph: str, t: float) -> float:
    """Linear glyph wedge-strike rhythm generator"""
    if glyph not in LINEAR_GLYPHS:
        return 0.0
    base, strikes, cents = LINEAR_GLYPHS[glyph]
    out = 0.0
    for s in range(strikes):
        st = (s / strikes) * 1.2  # spread
        dt = t - st
        if dt >= 0.0 and dt < 0.45:
            env = math.exp(-dt * 9.0)
            f = base * cents_to_mult(cents)
            out += saw(f * (1.0 + 0.001 * s), t) * env * 0.12
    return out

def fm_modulate_for_tokens(carrier: float, tokens: List[Tuple[str, str]], t: float) -> float:
    """PHONEME FM modulate"""
    m = 0.0
    for tok, group in tokens:
        mfreq, midx = PHONEME_FM.get(group, (0.0, 0.0))
        if mfreq > 0.0:
            depth = carrier * 0.12 * midx
            m += sine(carrier + depth * sine(mfreq, t), t) * 0.22
    return m

def charity_gliss(carrier: float, t: float) -> float:
    """Charity glissando effect"""
    if t < 1.2:
        start = carrier * 1.5
        end = carrier * 2.2
        f = start + (t / 1.2) * (end - start)
        return triangle(f, t) * 0.38
    return 0.0

def node137_burst(carrier: float, t: float) -> float:
    """Node 137 burst effect"""
    if t < 0.8:
        freq = carrier * cents_to_mult(NODE137_CENTS_OFFSET)
        return saw(freq, t) * math.exp(-t * 6.0) * 0.48
    return 0.0

def harmonic_layers(carrier: float, t: float) -> float:
    """Harmonic enrichment layers"""
    sub = sine(carrier / 2.0, t) * 0.25
    overt = sine(carrier * 2.0, t) * 0.15
    b1 = sine(carrier * 2.87, t) * 0.06
    b2 = sine(carrier * 3.13, t) * 0.06
    b3 = sine(carrier * 3.41, t) * 0.06
    return sub + overt + b1 + b2 + b3

# simple panning presets
PANS = [(0.5, 0.5), (0.65, 0.35), (0.35, 0.65), (0.7, 0.3), (0.3, 0.7), (0.55, 0.45)]

def apply_reverb(mono: List[float]) -> List[float]:
    """Simple algorithmic reverb (comb filter approximation)"""
    n = len(mono)
    wet = [0.0] * n
    # Simple delay-based reverb
    delay1 = int(0.029 * SAMPLE_RATE)
    delay2 = int(0.037 * SAMPLE_RATE)
    delay3 = int(0.041 * SAMPLE_RATE)
    
    for i in range(n):
        wet[i] = mono[i]
        if i >= delay1:
            wet[i] += mono[i - delay1] * 0.3
        if i >= delay2:
            wet[i] += mono[i - delay2] * 0.2
        if i >= delay3:
            wet[i] += mono[i - delay3] * 0.15
    return wet

def pack_int24_le(value: int) -> bytes:
    """Pack a signed 24-bit integer as 3 bytes little-endian"""
    # Ensure value is in valid 24-bit signed range
    value = max(PCM_24BIT_MIN, min(int(PCM_24BIT_MAX), value))
    # Handle negative values with two's complement
    if value < 0:
        value = (1 << 24) + value
    # Pack as 3 bytes little-endian
    return bytes([value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF])

def write_wav_24bit_stereo(filename: str, left: List[float], right: List[float]):
    """Write 24-bit PCM WAV file (stereo)"""
    n = len(left)
    bytes_per_sample = 3
    num_channels = 2
    byte_rate = SAMPLE_RATE * num_channels * bytes_per_sample
    block_align = num_channels * bytes_per_sample
    subchunk2_size = n * num_channels * bytes_per_sample
    chunk_size = 36 + subchunk2_size
    
    with open(filename, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", chunk_size))
        f.write(b"WAVE")
        # fmt subchunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))  # subchunk1 size
        f.write(struct.pack("<H", 1))   # PCM
        f.write(struct.pack("<H", num_channels))
        f.write(struct.pack("<I", SAMPLE_RATE))
        f.write(struct.pack("<I", byte_rate))
        f.write(struct.pack("<H", block_align))
        f.write(struct.pack("<H", 8 * bytes_per_sample))
        # data subchunk
        f.write(b"data")
        f.write(struct.pack("<I", subchunk2_size))
        # samples
        for i in range(n):
            l = int(max(-1.0, min(1.0, left[i])) * PCM_24BIT_MAX)
            r = int(max(-1.0, min(1.0, right[i])) * PCM_24BIT_MAX)
            # Write 24-bit little-endian properly
            f.write(pack_int24_le(l))
            f.write(pack_int24_le(r))

def sha256_bytes_from_wav(left: List[float], right: List[float]) -> str:
    """SHA-256 fingerprint for audio buffer (canonical PCM int24 little-endian interleaved)"""
    h = hashlib.sha256()
    for i in range(len(left)):
        l = int(max(-1.0, min(1.0, left[i])) * PCM_24BIT_MAX)
        r = int(max(-1.0, min(1.0, right[i])) * PCM_24BIT_MAX)
        h.update(pack_int24_le(l))
        h.update(pack_int24_le(r))
    return h.hexdigest()

def render_line_to_buffers(text: str, carrier: float, duration: float) -> Tuple[List[float], List[float]]:
    """Render single line to stereo buffers"""
    n = int(duration * SAMPLE_RATE)
    left = [0.0] * n
    right = [0.0] * n
    tokens = tokenize_kemetic(text)
    sumer_glyphs = extract_sumerian_glyphs(text)
    linear_glyphs = extract_linear_glyphs(text)
    t = 0.0
    step = 1.0 / SAMPLE_RATE

    for i in range(n):
        sig = sine(carrier, t) * 0.9
        # FM from phonemes
        sig += fm_modulate_for_tokens(carrier, tokens, t)
        # harmonic enrichment
        sig += harmonic_layers(carrier, t)
        # sumerian glyphs additive
        for g in sumer_glyphs:
            sig += sumerian_glyph_signal(g, t)
        # linear glyphs
        for g in linear_glyphs:
            sig += linear_glyph_signal(g, t)
        # special motifs
        if "7%" in text:
            sig += charity_gliss(carrier, t)
        if "137" in text:
            sig += node137_burst(carrier, t)
        # envelope
        sig *= adsr(t, duration)
        # panning
        idx = int((carrier - 100.0) / 40.0) % len(PANS)
        Lp, Rp = PANS[idx]
        left[i] = sig * Lp
        right[i] = sig * Rp
        t += step

    # simple reverb on mono and blend back (algorithmic)
    mono = [(l + r) * 0.5 for l, r in zip(left, right)]
    wet = apply_reverb(mono)
    for i in range(n):
        left[i] = left[i] * 0.7 + wet[i] * 0.3
        right[i] = right[i] * 0.7 + wet[i] * 0.3
    return (left, right)

def main():
    """Main render pipeline"""
    SOURCE_LINES = [
        "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb",
        "Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṭ‑ḥr",
        "smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr",
        "ṯs‑ỉt 137 m ḫnt iwf",
        "ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ [DINGIR]",
        "Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ ⚔️"
    ]
    
    mix_left = None
    mix_right = None
    metadata = []

    for i, line in enumerate(SOURCE_LINES):
        carrier = LINE_CARRIERS[i % len(LINE_CARRIERS)]
        L, R = render_line_to_buffers(line, carrier, DURATION)
        
        # write per-line WAV
        fname = f"aetherlingua_line_{i+1}.wav"
        write_wav_24bit_stereo(fname, L, R)
        print(f"Rendered: {fname}")
        
        # compute SHA-256 fingerprint
        sha = sha256_bytes_from_wav(L, R)
        
        # build JSON payload (on-chain-ready)
        triggers = []
        if "7%" in line:
            triggers.append("charity_7pct")
        if "137" in line:
            triggers.append("node137_spawn")
        
        payload = {
            "line_index": i + 1,
            "text": line,
            "carrier": carrier,
            "duration": DURATION,
            "sha256": sha,
            "triggers": triggers
        }
        metadata.append(payload)
        
        # mix accumulation
        if mix_left is None:
            mix_left = [0.0] * len(L)
            mix_right = [0.0] * len(R)
        for j in range(len(L)):
            mix_left[j] += L[j] * 0.3  # reduce per-line volume in mix
            mix_right[j] += R[j] * 0.3

    # write combined mix
    if mix_left is not None:
        # normalize mix
        max_val = max(max(abs(v) for v in mix_left), max(abs(v) for v in mix_right))
        if max_val > 0.0:
            norm = 0.9 / max_val
            mix_left = [v * norm for v in mix_left]
            mix_right = [v * norm for v in mix_right]
        
        write_wav_24bit_stereo("aetherlingua_combined_mix.wav", mix_left, mix_right)
        print("Rendered: aetherlingua_combined_mix.wav")
        
        # SHA-256 for combined mix
        mix_sha = sha256_bytes_from_wav(mix_left, mix_right)
        
        # Add combined mix metadata
        metadata.append({
            "type": "combined_mix",
            "duration": DURATION,
            "sha256": mix_sha,
            "source_lines": len(SOURCE_LINES)
        })

    # Write JSON payload
    with open("aetherlingua_payload.json", "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0.0",
            "engine": "AetherLingua",
            "sample_rate": SAMPLE_RATE,
            "bit_depth": BIT_DEPTH,
            "seed": SEED,
            "swarmgate_config": {
                "trigger_threshold": 0.07,
                "node137_enabled": True
            },
            "renders": metadata
        }, f, indent=2, ensure_ascii=False)
    print("Generated: aetherlingua_payload.json")
    
    print("\n✓ AetherLingua render complete!")
    print(f"✓ Generated {len(SOURCE_LINES)} per-line WAVs")
    print("✓ Generated combined mix")
    print("✓ Generated SHA-256 fingerprints")
    print("✓ Generated JSON on-chain payload")

if __name__ == "__main__":
    main()
