# AetherLingua: Living Glyph Language Engine

## Overview

AetherLingua is a sonic language engine that transforms ancient scripts (Kemetic hieroglyphics, Sumerian cuneiform, Linear B) into deterministic audio representations. Each text generates unique 48kHz 24-bit WAV files with SHA-256 fingerprints for verifiable "sonic genomes."

## Features

- **Multi-Script Support**: Kemetic transliteration, Sumerian cuneiform glyphs, Linear B-like wedge patterns
- **Deterministic Generation**: Seeded RNG ensures reproducible audio for the same input
- **Rich Sonification**: FM synthesis, harmonic layers, ADSR envelopes, reverb
- **Special Motifs**: 
  - 7% trigger → charity glissando effect
  - 137 node → burst synthesis for SwarmGate node spawning
- **Blockchain Ready**: SHA-256 fingerprints and JSON payloads for on-chain verification

## Quick Start

```bash
python3 aetherlingua_full.py
```

## Output Files

The engine generates:
- `aetherlingua_line_1.wav` through `aetherlingua_line_6.wav` - Individual line renderings
- `aetherlingua_combined_mix.wav` - Layered mix of all lines
- `aetherlingua_payload.json` - Metadata with SHA-256 hashes and trigger information

## Architecture

### Audio Pipeline
1. **Tokenization**: Kemetic transliteration → phoneme tokens
2. **Glyph Extraction**: Parse Sumerian glyphs (e.g., `[DINGIR]`)
3. **Signal Generation**: 
   - Base carrier oscillators (110Hz - 349Hz)
   - FM modulation based on phoneme categories
   - Harmonic enrichment (sub-bass, overtones, bells)
   - Wedge strike patterns for cuneiform glyphs
4. **Special Effects**: Charity gliss, Node137 burst, algorithmic reverb
5. **Rendering**: 24-bit stereo WAV @ 48kHz with panning

### Phoneme Mapping

| Category | FM Frequency | Modulation Index | Examples |
|----------|--------------|------------------|----------|
| Vowel    | 5.0 Hz      | 1.8              | a, e, i, ỉ, ȝ |
| Voiced   | 7.0 Hz      | 2.4              | b, d, ḏ, ḥ |
| Sibilant | 12.0 Hz     | 1.2              | s, š, ṯ |
| Stop     | 18.0 Hz     | 0.9              | p, t, k |
| Nasal    | 3.5 Hz      | 1.1              | m, n, r, l |

### Sumerian Glyph Map

Sumerian glyphs are marked with square brackets: `[GLYPH]`

| Glyph   | Phonetic | Base Freq | Wedges | Meaning |
|---------|----------|-----------|--------|---------|
| DINGIR  | an       | 261.63 Hz | 5      | Divine  |
| LUGAL   | lugal    | 196.00 Hz | 4      | King    |
| EN      | en       | 293.66 Hz | 3      | Lord    |
| NIN     | nin      | 329.63 Hz | 4      | Lady    |
| URU     | uru      | 220.00 Hz | 2      | City    |

### Linear B Glyph Map

Linear glyphs are marked with angle brackets: `<GLYPH>`

| Glyph | Base Freq | Strikes | Cents Offset |
|-------|-----------|---------|--------------|
| A1    | 240.0 Hz  | 6       | -7.0         |
| B2    | 260.0 Hz  | 4       | +12.0        |
| C3    | 280.0 Hz  | 5       | -3.0         |

## Configuration

Edit constants in `aetherlingua_full.py`:

```python
SAMPLE_RATE = 48000  # Audio sample rate
BIT_DEPTH = 24       # Bit depth for WAV files
DURATION = 8.0       # Length of each line in seconds
SEED = 1337          # RNG seed for deterministic output
```

## JSON Payload Structure

```json
{
  "version": "1.0.0",
  "engine": "AetherLingua",
  "sample_rate": 48000,
  "bit_depth": 24,
  "seed": 1337,
  "swarmgate_config": {
    "trigger_threshold": 0.07,
    "node137_enabled": true
  },
  "renders": [
    {
      "line_index": 1,
      "text": "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb",
      "carrier": 110.0,
      "duration": 8.0,
      "sha256": "fa082578db41887a1fbbb975ea8f4796d2bef3c5369a55e0f7bf4d9817baedec",
      "triggers": []
    }
  ]
}
```

## SwarmGate Integration

The JSON payload includes SwarmGate metadata:
- **7% Trigger**: Lines containing "7%" activate charity distribution mechanics
- **Node137 Spawn**: Lines containing "137" trigger node spawning in the swarm network
- **SHA-256 Hashes**: Enable on-chain verification of audio integrity

## Technical Details

### WAV File Format
- **Format**: RIFF/WAVE
- **Encoding**: PCM (uncompressed)
- **Bit Depth**: 24-bit (3 bytes per sample)
- **Channels**: 2 (stereo)
- **Sample Rate**: 48000 Hz
- **Byte Order**: Little-endian

### Deterministic Hash Generation
SHA-256 hashes are computed from the canonical PCM representation (24-bit little-endian interleaved stereo), ensuring identical hashes for identical audio regardless of metadata or file format variations.

## Examples

### Source Text (Kemetic)
```
Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
(Mayor of Kemet: Power-holder of Horus-Reckoning)
```

### With Sumerian Glyph
```
ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ [DINGIR]
(Calculate 7% given from good heart on the path of life [DIVINE])
```

## Dependencies

Standard Python 3 libraries only:
- `math` - Trigonometric functions and mathematical operations
- `struct` - Binary data packing for WAV files
- `hashlib` - SHA-256 fingerprinting
- `json` - JSON payload generation
- `os` - File system operations

## License

Part of the Sovereignty Architecture project. See main LICENSE file.

## See Also

- [Sovereignty Architecture](README.md)
- [Trust Declaration](TRUST_DECLARATION.md)
- [SwarmGate Documentation](docs/swarmgate.md) (if available)

---

*"Sound as signature, voice as proof, language as living protocol."*
