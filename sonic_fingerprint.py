#!/usr/bin/env python3
# sonic_fingerprint.py
# Sonic fingerprint generation using signal processing and cryptographic hashing
# Strategickhaos DAO LLC - Sovereignty Architecture

import math
import hashlib
import struct  # added

def sine(freq, t):
    return math.sin(2.0 * math.pi * freq * t)

def saw(freq, t):
    phase = freq * t - math.floor(freq * t)
    return 2.0 * phase - 1.0

def triangle(freq, t):
    phase = freq * t - math.floor(freq * t)
    return 1.0 - 4.0 * abs(round(phase) - phase)

def adsr(t, dur):
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

def charity_gliss(carrier, t):
    if t < 1.2:
        start = carrier * 1.5
        end = carrier * 2.2
        f = start + (t / 1.2) * (end - start)
        return triangle(f, t) * 0.35
    return 0.0

def node137_burst(carrier, t):
    if t < 0.8:
        offset_cents = 5.0 + 18.0 - 12.0
        freq = carrier * math.pow(2.0, offset_cents / 1200.0)
        return saw(freq, t) * math.exp(-t * 6.0) * 0.45
    return 0.0

def harmonic_layers(carrier, t):
    sub = sine(carrier / 2.0, t) * 0.25
    overt = sine(carrier * 2.0, t) * 0.15
    b1 = sine(carrier * 2.87, t) * 0.06
    b2 = sine(carrier * 3.13, t) * 0.06
    b3 = sine(carrier * 3.41, t) * 0.06
    return sub + overt + b1 + b2 + b3

SAMPLE_RATE = 48000
DURATION = 8.0
LINE_CARRIERS = [110.00, 138.59, 174.61, 220.00, 277.18, 349.23]

SOURCE_LINES = [
  "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb",
  "Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṭ‑ḥr",
  "smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr",
  "ṯs‑ỉt 137 m ḫnt iwf",
  "ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ",
  "Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ"
]

# Render one line to mono signal (simplified, no FM/token for brevity)
def render_line(carrier, text):
    n = int(DURATION * SAMPLE_RATE)
    signal = []
    t = 0.0
    step = 1.0 / SAMPLE_RATE
    for i in range(n):
        sig = sine(carrier, t) * 0.9
        sig += harmonic_layers(carrier, t)
        if "7%" in text:
            sig += charity_gliss(carrier, t)
        if "137" in text:
            sig += node137_burst(carrier, t)
        sig *= adsr(t, DURATION)
        signal.append(sig)
        t += step
    return signal

# Compute SHA256 of signal (as float bytes)
def sha256_signal(sig):
    h = hashlib.sha256()
    for s in sig:
        h.update(struct.pack('<f', s))
    return h.hexdigest()

# Render all lines and print hashes
hashes = []
for i, line in enumerate(SOURCE_LINES):
    carrier = LINE_CARRIERS[i]
    sig = render_line(carrier, line)
    sh = sha256_signal(sig)
    hashes.append(sh)
    print(f"Line {i+1}: {sh[:16]}... (carrier {carrier} Hz)")

print("\nFull invocation sonic fingerprint (combined hash):")
combined_h = hashlib.sha256()
for h in hashes:
    combined_h.update(bytes.fromhex(h))
print(combined_h.hexdigest())
