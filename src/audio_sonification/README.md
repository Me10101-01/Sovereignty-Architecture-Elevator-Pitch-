# GlyphSonix Resonance Core (GSRC)

## Overview

The GlyphSonix Resonance Core is a FlameLang (Mojo-style) inspired deterministic audio renderer that transforms ancient language transliterations into sonified output. It implements advanced digital signal processing techniques to create reproducible, high-quality audio renders.

## Features

### Core Audio Processing
- **Deterministic RNG**: Seeded random number generation ensures reproducible renders
- **48 kHz 24-bit WAV Output**: Professional audio quality with stereo output
- **Multiple Oscillators**: Sine, sawtooth, and triangle wave generators
- **ADSR Envelope**: Attack, Decay, Sustain, Release envelope shaping

### Language Support
- **Kemetic Transliteration**: Full tokenization with multigraph support (ḥ, ḫ, ṯ, ỉ, ȝ, ꜣ, ʿ, ḏ, ḳ, ḫft)
- **Sumerian Cuneiform**: Glyph-to-phoneme mapping (DINGIR, LUGAL, EN, NIN, URU, etc.)
- **Phoneme Classification**: Vowels, voiced consonants, sibilants, stops, nasals

### Audio Effects
1. **FM Modulation**: Frequency modulation per phoneme group with custom parameters
2. **Harmonic Layers**:
   - Subharmonics (1/2 carrier frequency)
   - Overtones (2x carrier frequency)
   - Bronze partials (2.87x, 3.13x, 3.41x carrier)
3. **Charity Gliss (7%)**: Special glissando motif triggered by "7%" in text
4. **Node 137 Burst**: Special burst motif triggered by "137" in text
5. **Stereo Panning**: Per-line panning patterns for spatial imaging
6. **Algorithmic Reverb**: Feedback delay-based reverb with multiple taps

## Usage

### Basic Usage

```python
from audio_sonification import render_line_to_stereo, write_wav_stereo, SAMPLE_RATE

# Render a single line
text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
carrier_freq = 110.0  # Hz
duration = 8.0  # seconds

left, right = render_line_to_stereo(text, carrier_freq, duration)
write_wav_stereo("output.wav", left, right, SAMPLE_RATE)
```

### Full Rendering

```python
from audio_sonification.gsrc_full import main

# Renders all six source text lines and produces:
# - gsrc_line_1.wav through gsrc_line_6.wav (individual lines)
# - gsrc_full_mix.wav (combined mix)
main()
```

### Command Line

```bash
# Run the full renderer
python3 -m src.audio_sonification.gsrc_full

# Or directly
cd src/audio_sonification
python3 gsrc_full.py
```

## Technical Details

### Phoneme FM Parameters

| Phoneme Group | Modulation Freq (Hz) | Modulation Index |
|---------------|---------------------|------------------|
| Vowel         | 5.0                 | 1.8              |
| Voiced        | 7.0                 | 2.4              |
| Sibilant      | 12.0                | 1.2              |
| Stop          | 18.0                | 0.9              |
| Nasal         | 3.5                 | 1.1              |
| Punct         | 0.5                 | 0.6              |

### Line Carrier Frequencies

Lines are mapped to the following carrier frequencies:
- Line 1: 110.00 Hz (A2)
- Line 2: 138.59 Hz (C#3)
- Line 3: 174.61 Hz (F3)
- Line 4: 220.00 Hz (A3)
- Line 5: 277.18 Hz (C#4)
- Line 6: 349.23 Hz (F4)

### ADSR Envelope Parameters

- Attack: 0.5 seconds
- Decay: 0.7 seconds
- Sustain Level: 0.75 (75%)
- Release: 1.0 second

### Reverb Parameters

- Delay Taps: 41ms, 77ms, 139ms
- Gains: 0.28, 0.18, 0.12
- Wet/Dry Mix: 30% wet, 70% dry

## Source Text

The default rendering processes six lines of Kemetic transliteration:

1. "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
2. "Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṭ‑ḥr"
3. "smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr"
4. "ṯs‑ỉt 137 m ḫnt iwf" (triggers Node 137 burst)
5. "ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ" (triggers Charity gliss)
6. "Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ"

## Deterministic Rendering

All renders are deterministic and reproducible when using the same seed (default: 1337). This ensures:
- Identical output across different runs
- Version control for audio assets
- Cryptographic verification of renders
- Blockchain-compatible sonic fingerprints

## Extension Points

### Adding Sumerian Glyphs

To add more Sumerian cuneiform glyphs, update the `SUMERIAN_MAP` dictionary:

```python
SUMERIAN_MAP = {
    "DINGIR": "an",
    "LUGAL": "lugal",
    "EN": "en",
    "NIN": "nin",
    "URU": "uru",
    # Add your glyphs here
    "KUR": "kur",
    "EZEN": "ezen",
}
```

### Custom Carrier Frequencies

Modify `LINE_CARRIERS` for different frequency mappings:

```python
LINE_CARRIERS = [110.00, 146.83, 196.00, 220.00, 293.66, 392.00]
```

### Export Options

The renderer can be extended to support:
- SuperCollider export (`.scd` files)
- Csound export (`.csd` files)
- JSON metadata with SHA-256 hash
- On-chain payload generation for SwarmGate

## License

Part of the Strategickhaos DAO LLC Sovereignty Architecture.
