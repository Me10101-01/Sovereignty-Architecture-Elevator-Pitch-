#!/usr/bin/env python3
"""
GlyphSonix Resonance Core (GSRC) - FlameLang-inspired Audio Renderer

This module implements a deterministic audio renderer that transforms Kemetic
transliteration and Sumerian cuneiform into sonified output with FM modulation,
subharmonics, overtones, charity gliss, node-137 burst, ADSR envelope, reverb,
and stereo panning.

Produces 48 kHz 24-bit WAV files per line and a combined mix.
"""

import math
import struct
import wave
import sys
from typing import List, Tuple, Set, Dict

# Constants
SAMPLE_RATE = 48000
BIT_DEPTH = 24
SEED = 1337

# Reverb mix constants
REVERB_WET_MIX = 0.3
REVERB_DRY_MIX = 0.7

# Node 137 burst cents offset components
NODE_137_CENTS_A = 5.0
NODE_137_CENTS_B = 18.0
NODE_137_CENTS_C = 12.0


class DetermRng:
    """Deterministic random number generator for reproducible renders."""
    
    def __init__(self, seed: int = SEED):
        self.state = seed
    
    def next(self) -> int:
        """Generate next random integer."""
        self.state = (1103515245 * self.state + 12345) & 0x7fffffff
        return self.state
    
    def uniform(self) -> float:
        """Generate uniform random float between 0 and 1."""
        return self.next() / 0x7fffffff


# Global RNG instance (reserved for future use in stochastic effects)
# Note: Currently not used in deterministic rendering pipeline
RNG = DetermRng()


# Oscillator functions
def sine(freq: float, t: float) -> float:
    """Pure sine wave oscillator."""
    return math.sin(2.0 * math.pi * freq * t)


def saw(freq: float, t: float) -> float:
    """Sawtooth wave oscillator."""
    x = (freq * t) % 1.0
    return 2.0 * x - 1.0


def triangle(freq: float, t: float) -> float:
    """Triangle wave oscillator."""
    x = (freq * t) % 1.0
    return 1.0 - 4.0 * abs(x - 0.5)


# ADSR envelope
def adsr(t: float, dur: float, a: float, d: float, s: float, r: float) -> float:
    """
    ADSR envelope generator.
    
    Args:
        t: Current time
        dur: Total duration
        a: Attack time
        d: Decay time
        s: Sustain level
        r: Release time
    """
    if t < a:
        return t / a
    if t < a + d:
        return 1.0 - (1.0 - s) * ((t - a) / d)
    if t < dur - r:
        return s
    if t < dur:
        return s * (1.0 - ((t - (dur - r)) / r))
    return 0.0


# Tokenization and phoneme classification
KEMETIC_MULTIGRAPHS = ["ḥ", "ḫ", "ṯ", "ỉ", "ȝ", "ꜣ", "ʿ", "ḏ", "ḳ", "ḫft"]
VOWELS: Set[str] = {"a", "e", "i", "o", "u", "y", "ỉ", "ȝ", "ꜣ"}
VOICED: Set[str] = {"b", "d", "g", "ḏ", "ḥ", "ḫ", "ḳ"}
SIBILANTS: Set[str] = {"s", "š", "ẖ", "ṯ", "ẖṭ"}
STOPS: Set[str] = {"p", "t", "k", "ḳ"}
NASALS: Set[str] = {"m", "n", "r", "l", "w"}

# Sumerian cuneiform basic glyph-to-phoneme map (illustrative)
SUMERIAN_MAP: Dict[str, str] = {
    "DINGIR": "an",
    "LUGAL": "lugal",
    "EN": "en",
    "NIN": "nin",
    "URU": "uru",
    "KI": "ki",
    "AN": "an",
    "DUB": "dub",
    "SAR": "sar",
}

# Frequencies for phoneme groups (Hz) - (modulation_freq, modulation_index)
PHONEME_FM: Dict[str, Tuple[float, float]] = {
    "vowel": (5.0, 1.8),
    "voiced": (7.0, 2.4),
    "sibilant": (12.0, 1.2),
    "stop": (18.0, 0.9),
    "nasal": (3.5, 1.1),
    "punct": (0.5, 0.6),
}

# Line to carrier mapping (Hz)
LINE_CARRIERS = [110.00, 138.59, 174.61, 220.00, 277.18, 349.23]


def cents_to_mult(c: float) -> float:
    """Convert cents to frequency multiplier."""
    return math.pow(2.0, c / 1200.0)


def classify_token(tok: str) -> str:
    """Classify a token into a phoneme group."""
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
    """
    Tokenize Kemetic transliteration into phoneme tokens.
    
    Args:
        text: Input Kemetic transliteration string
    
    Returns:
        List of (token, classification) tuples
    """
    tokens: List[Tuple[str, str]] = []
    i = 0
    text = text.lower()
    
    while i < len(text):
        # Check multigraphs
        matched = False
        for mg in KEMETIC_MULTIGRAPHS:
            if text[i:].startswith(mg):
                tokens.append((mg, classify_token(mg)))
                i += len(mg)
                matched = True
                break
        
        if matched:
            continue
        
        ch = text[i]
        if ch.isalpha():
            tokens.append((ch, classify_token(ch)))
        else:
            tokens.append((ch, "punct"))
        i += 1
    
    return tokens


def charity_gliss(carrier: float, t: float) -> float:
    """
    Charity gliss (7%) special motif.
    
    Args:
        carrier: Base carrier frequency
        t: Current time
    """
    if t < 1.2:
        start = carrier * 1.5
        end = carrier * 2.2
        f = start + (t / 1.2) * (end - start)
        return triangle(f, t) * 0.35 * math.exp(-t * 1.2)
    return 0.0


def node137_burst(carrier: float, t: float) -> float:
    """
    Node 137 burst special motif.
    
    Args:
        carrier: Base carrier frequency
        t: Current time
    """
    if t < 0.8:
        offset_cents = NODE_137_CENTS_A + NODE_137_CENTS_B - NODE_137_CENTS_C
        freq = carrier * cents_to_mult(offset_cents)
        return saw(freq, t) * math.exp(-t * 6.0) * 0.45
    return 0.0


def fm_modulate(carrier: float, token_group: str, t: float) -> float:
    """
    FM modulation per token group.
    
    Args:
        carrier: Base carrier frequency
        token_group: Phoneme group classification
        t: Current time
    """
    mfreq, midx = PHONEME_FM.get(token_group, (0.0, 0.0))
    if mfreq <= 0.0:
        return 0.0
    depth = carrier * 0.12 * midx
    return math.sin(2.0 * math.pi * (carrier + depth * math.sin(2.0 * math.pi * mfreq * t)) * t) * 0.25


def harmonic_layers(carrier: float, t: float) -> float:
    """
    Subharmonic and overtone layers with bronze partials.
    
    Args:
        carrier: Base carrier frequency
        t: Current time
    """
    sub = sine(carrier / 2.0, t) * 0.25
    overt = sine(carrier * 2.0, t) * 0.15
    # Bronze partials
    p1 = sine(carrier * 2.87, t) * 0.06
    p2 = sine(carrier * 3.13, t) * 0.06
    p3 = sine(carrier * 3.41, t) * 0.06
    return sub + overt + p1 + p2 + p3


def pan(stereo: Tuple[float, float], signal: float) -> Tuple[float, float]:
    """
    Simple stereo panner.
    
    Args:
        stereo: (left_gain, right_gain) tuple
        signal: Mono signal to pan
    """
    return (stereo[0] * signal, stereo[1] * signal)


def simple_reverb(mono_buffer: List[float], sample_rate: int) -> List[float]:
    """
    Algorithmic reverb using feedback delays.
    
    Args:
        mono_buffer: Input mono audio buffer
        sample_rate: Sample rate in Hz
    """
    out = mono_buffer[:]  # Copy
    delays = [int(0.041 * sample_rate), int(0.077 * sample_rate), int(0.139 * sample_rate)]
    gains = [0.28, 0.18, 0.12]
    
    for i in range(len(mono_buffer)):
        for j in range(len(delays)):
            d = delays[j]
            if i - d >= 0:
                out[i] += mono_buffer[i - d] * gains[j]
    
    # Normalize mild
    peak = max(1e-9, max(abs(x) for x in out))
    if peak > 1.0:
        for i in range(len(out)):
            out[i] /= peak
    
    return out


def write_wav_stereo(filename: str, left: List[float], right: List[float], sample_rate: int):
    """
    Write WAV 24-bit PCM (interleaved stereo).
    
    Args:
        filename: Output filename
        left: Left channel samples (normalized -1.0 to 1.0)
        right: Right channel samples (normalized -1.0 to 1.0)
        sample_rate: Sample rate in Hz
    """
    n = len(left)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(3)  # 24-bit packed in 3 bytes
        wf.setframerate(sample_rate)
        frames = bytearray()
        
        for i in range(n):
            # Clamp to [-1.0, 1.0] and convert to 24-bit integer
            l = int(max(-1.0, min(1.0, left[i])) * (2**23 - 1))
            r = int(max(-1.0, min(1.0, right[i])) * (2**23 - 1))
            # Pack 24-bit little endian (take first 3 bytes of 32-bit int)
            frames += struct.pack('<i', l)[:3]
            frames += struct.pack('<i', r)[:3]
        
        wf.writeframes(bytes(frames))


def render_line_to_stereo(text: str, carrier: float, duration: float) -> Tuple[List[float], List[float]]:
    """
    Render a single line to stereo audio.
    
    Args:
        text: Input text (Kemetic transliteration)
        carrier: Base carrier frequency
        duration: Duration in seconds
    
    Returns:
        (left_channel, right_channel) tuple of sample lists
    """
    n = int(duration * SAMPLE_RATE)
    left = [0.0] * n
    right = [0.0] * n
    tokens = tokenize_kemetic(text)
    
    for i in range(n):
        t = i / SAMPLE_RATE
        
        # Main carrier
        sig = sine(carrier, t) * 0.9
        
        # FM per token
        for tok, group in tokens:
            sig += fm_modulate(carrier, group, t)
        
        # Layers
        sig += harmonic_layers(carrier, t)
        
        # Special motifs
        if "7%" in text:
            sig += charity_gliss(carrier, t)
        if "137" in text:
            sig += node137_burst(carrier, t)
        
        # ADSR envelope
        env = adsr(t, duration, 0.5, 0.7, 0.75, 1.0)
        sig *= env
        
        # Simple per-line panning pattern
        idx = int((carrier - 100.0) / 40.0)  # Maps to 0..5 roughly
        pans = [
            (0.5, 0.5),   # center
            (0.65, 0.35), # left
            (0.35, 0.65), # right
            (0.7, 0.3),   # left more
            (0.3, 0.7),   # right more
            (0.55, 0.45)  # center slight left
        ]
        p = pans[idx % len(pans)]
        L, R = pan(p, sig)
        
        left[i] = L
        right[i] = R
    
    # Reverb on mono mix then re-spread
    mono = [(l + r) * 0.5 for l, r in zip(left, right)]
    wet = simple_reverb(mono, SAMPLE_RATE)
    
    # Mix wet back
    for i in range(n):
        left[i] = left[i] * REVERB_DRY_MIX + wet[i] * REVERB_WET_MIX
        right[i] = right[i] * REVERB_DRY_MIX + wet[i] * REVERB_WET_MIX
    
    return (left, right)


def main():
    """Main render procedure."""
    SOURCE_TEXT_LINES = [
        "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb",
        "Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṭ‑ḥr",
        "smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr",
        "ṯs‑ỉt 137 m ḫnt iwf",
        "ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ",
        "Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ"
    ]
    durations = [8.0, 8.0, 8.0, 8.0, 8.0, 8.0]
    per_line_files = []
    mix_left = []
    mix_right = []
    
    # Render each line
    for i in range(len(SOURCE_TEXT_LINES)):
        carrier = LINE_CARRIERS[i % len(LINE_CARRIERS)]
        L, R = render_line_to_stereo(SOURCE_TEXT_LINES[i], carrier, durations[i])
        fname = f"gsrc_line_{i+1}.wav"
        write_wav_stereo(fname, L, R, SAMPLE_RATE)
        per_line_files.append(fname)
        
        # Append to mix (pad both buffers to the same length)
        max_len = max(len(mix_left), len(L))
        if len(mix_left) < max_len:
            mix_left = mix_left + [0.0] * (max_len - len(mix_left))
            mix_right = mix_right + [0.0] * (max_len - len(mix_right))
        
        for j in range(len(L)):
            mix_left[j] += L[j]
            mix_right[j] += R[j]
    
    # Normalize final mix
    peak = max(1e-9, max(max(abs(x) for x in mix_left), max(abs(x) for x in mix_right)))
    if peak > 1.0:
        for i in range(len(mix_left)):
            mix_left[i] /= peak
            mix_right[i] /= peak
    
    write_wav_stereo("gsrc_full_mix.wav", mix_left, mix_right, SAMPLE_RATE)
    
    print("Rendered per-line files:", per_line_files)
    print("Rendered full mix: gsrc_full_mix.wav")


if __name__ == "__main__":
    main()
