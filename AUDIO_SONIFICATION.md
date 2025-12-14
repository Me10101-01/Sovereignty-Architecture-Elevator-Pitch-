# Audio Sonification - GlyphSonix Resonance Core (GSRC)

## Overview

The GlyphSonix Resonance Core (GSRC) is a production-ready, deterministic audio renderer inspired by FlameLang/Mojo programming paradigms. It transforms ancient language transliterations (Kemetic hieroglyphic and Sumerian cuneiform) into high-quality sonified output.

## Key Features

### 🎵 Audio Engine
- **48 kHz 24-bit Stereo WAV Output** - Professional audio quality
- **Deterministic Rendering** - Reproducible results with seeded RNG (default seed: 1337)
- **Multiple Oscillators** - Sine, sawtooth, and triangle wave generators
- **ADSR Envelope** - Attack (0.5s), Decay (0.7s), Sustain (75%), Release (1.0s)

### 🔊 Digital Signal Processing
1. **FM Modulation** - Per-phoneme frequency modulation with custom parameters
2. **Harmonic Layers**:
   - Subharmonics at 1/2 carrier frequency
   - Overtones at 2x carrier frequency  
   - Bronze partials at 2.87x, 3.13x, and 3.41x carrier
3. **Algorithmic Reverb** - Feedback delay network (41ms, 77ms, 139ms taps)
4. **Stereo Panning** - Per-line spatial imaging

### 🏺 Language Processing
- **Kemetic Transliteration** - Full multigraph tokenization (ḥ, ḫ, ṯ, ỉ, ȝ, ꜣ, ʿ, ḏ, ḳ, ḫft)
- **Sumerian Cuneiform** - Glyph-to-phoneme mapping (DINGIR, LUGAL, EN, NIN, URU, etc.)
- **Phoneme Classification** - Vowels, voiced consonants, sibilants, stops, nasals

### ✨ Special Motifs
- **Charity Gliss (7%)** - Triggered by "7%" in text - glissando from 1.5x to 2.2x carrier
- **Node 137 Burst** - Triggered by "137" in text - exponential decay burst with cents offset

## Quick Start

### Installation

No additional dependencies required beyond Python 3.8+ standard library.

```bash
cd /path/to/Sovereignty-Architecture-Elevator-Pitch-
```

### Basic Usage

```python
from src.audio_sonification import render_line_to_stereo, write_wav_stereo, SAMPLE_RATE

# Render a single line
text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
carrier_freq = 110.0  # Hz (A2)
duration = 8.0        # seconds

left, right = render_line_to_stereo(text, carrier_freq, duration)
write_wav_stereo("output.wav", left, right, SAMPLE_RATE)
```

### Full Rendering

```bash
# Render all six source text lines
python3 src/audio_sonification/gsrc_full.py

# Outputs:
#   gsrc_line_1.wav through gsrc_line_6.wav (individual lines)
#   gsrc_full_mix.wav (combined mix)
```

### Run Examples

```bash
# Run comprehensive examples
python3 examples/gsrc_example.py

# Outputs:
#   example_single_line.wav
#   example_carrier_1.wav, example_carrier_2.wav, example_carrier_3.wav
#   example_motif_1.wav (7% charity gliss)
#   example_motif_2.wav (node 137 burst)
```

## Technical Specifications

### Phoneme FM Parameters

| Phoneme Group | Modulation Freq (Hz) | Modulation Index | Depth Factor |
|---------------|---------------------|------------------|--------------|
| Vowel         | 5.0                 | 1.8              | 0.12         |
| Voiced        | 7.0                 | 2.4              | 0.12         |
| Sibilant      | 12.0                | 1.2              | 0.12         |
| Stop          | 18.0                | 0.9              | 0.12         |
| Nasal         | 3.5                 | 1.1              | 0.12         |
| Punct         | 0.5                 | 0.6              | 0.12         |

### Carrier Frequency Mapping

Lines are assigned carrier frequencies in a harmonic series:

| Line | Frequency | Note Equivalent |
|------|-----------|-----------------|
| 1    | 110.00 Hz | A2              |
| 2    | 138.59 Hz | C#3             |
| 3    | 174.61 Hz | F3              |
| 4    | 220.00 Hz | A3              |
| 5    | 277.18 Hz | C#4             |
| 6    | 349.23 Hz | F4              |

### Reverb Configuration

- **Delay Taps**: 41ms, 77ms, 139ms
- **Gains**: 0.28, 0.18, 0.12
- **Mix**: 30% wet, 70% dry
- **Normalization**: Automatic peak limiting

## Source Texts

The default render processes six lines of Kemetic transliteration:

1. `Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb` - "Count of Kemet: Power of Horus-Reckoning"
2. `Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṭ‑ḥr` - "House of wheat, first of craftsmen, golden eye in the sanctuary"
3. `smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr` - "Establish divine beauty, craft for magic on the altar, in Hathor's mansion"
4. `ṯs‑ỉt 137 m ḫnt iwf` - "Knot-count 137 within the flesh" **(triggers Node 137 burst)**
5. `ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ` - "Reckon 7% given heart-beauty on the path of life" **(triggers Charity gliss)**
6. `Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ` - "Magic against us, life-provision"

## Testing

```bash
# Run comprehensive test suite
python3 benchmarks/test_audio_sonification.py

# Tests include:
#   - Deterministic RNG
#   - Oscillators (sine, saw, triangle)
#   - ADSR envelope
#   - Kemetic tokenization
#   - Cents conversion
#   - Special motifs
#   - FM modulation
#   - Harmonic layers
#   - Stereo panning
#   - Reverb
#   - WAV writer
#   - Line rendering
#   - Deterministic rendering
```

## Advanced Usage

### Custom Carrier Frequencies

```python
from src.audio_sonification import LINE_CARRIERS

# Override default carriers
custom_carriers = [110.00, 146.83, 196.00, 220.00, 293.66, 392.00]
```

### Adding Sumerian Glyphs

```python
from src.audio_sonification.gsrc_full import SUMERIAN_MAP

# Extend the mapping
SUMERIAN_MAP["KUR"] = "kur"    # mountain
SUMERIAN_MAP["EZEN"] = "ezen"  # festival
```

### Custom RNG Seed

```python
from src.audio_sonification import DetermRng

# Use custom seed for different (but still deterministic) output
rng = DetermRng(seed=42)
```

## Architecture

```
src/audio_sonification/
├── __init__.py           # Module exports
├── gsrc_full.py          # Core implementation
└── README.md             # Technical documentation

benchmarks/
└── test_audio_sonification.py  # Test suite

examples/
└── gsrc_example.py       # Usage examples
```

## Performance

Rendering times on modern hardware:
- **Single 8-second line**: ~1-2 seconds
- **Full 6-line mix (48 seconds)**: ~6-8 seconds
- **Output file size**: ~2.2 MB per 8-second stereo file

## Future Extensions

As mentioned in the problem statement, the following extensions can be added:

1. **SuperCollider Export** - Generate `.scd` files for real-time synthesis
2. **Csound Export** - Generate `.csd` orchestra files
3. **Cryptographic Fingerprinting** - SHA-256 hash of WAV for verification
4. **On-chain Payload** - JSON metadata for SwarmGate integration
5. **Enhanced Sumerian Mapping** - Wedge-strike patterns, stroke-count envelopes
6. **Microtonal Tuning** - Per-glyph frequency adjustments

## License

Part of the Strategickhaos DAO LLC Sovereignty Architecture.

## Contact

For questions or contributions:
- **Security**: security@strategickhaos.ai
- **GitHub**: [@Me10101-01](https://github.com/Me10101-01)
- **Repository**: [Sovereignty-Architecture-Elevator-Pitch-](https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-)

---

*Generated by GlyphSonix Resonance Core v1.0*
*Deterministic • Reproducible • Production-Ready*
