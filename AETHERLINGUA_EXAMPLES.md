# AetherLingua Usage Examples

## Quick Start

```bash
# Generate audio files from default Kemetic text
python3 aetherlingua_full.py

# Run test suite
python3 test_aetherlingua.py
```

## Output Files

After running `aetherlingua_full.py`, you'll get:

```
aetherlingua_line_1.wav          # First line rendering (110 Hz carrier)
aetherlingua_line_2.wav          # Second line rendering (138.59 Hz carrier)
aetherlingua_line_3.wav          # Third line rendering (174.61 Hz carrier)
aetherlingua_line_4.wav          # Fourth line rendering (220 Hz carrier) - includes node137 burst
aetherlingua_line_5.wav          # Fifth line rendering (277.18 Hz carrier) - includes charity gliss
aetherlingua_line_6.wav          # Sixth line rendering (349.23 Hz carrier)
aetherlingua_combined_mix.wav    # Layered mix of all lines
aetherlingua_payload.json        # On-chain metadata with SHA-256 hashes
```

## Source Text Examples

### Basic Kemetic Transliteration
```
Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
(Mayor of Kemet: Power-holder of Horus-Reckoning)
```

**Audio features:**
- Base carrier: 110 Hz
- Phoneme-based FM modulation from Kemetic characters
- Harmonic enrichment layers

### With Sumerian Glyph
```
ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ [DINGIR]
(Calculate 7% given from good heart on the path of life [DIVINE])
```

**Audio features:**
- Base carrier: 277.18 Hz
- **7% trigger** → Charity glissando effect (sweeps from carrier * 1.5 to carrier * 2.2)
- **[DINGIR] glyph** → Bronze-bell wedge strikes (5 strikes at 261.63 Hz base with inharmonic shimmer)
- Phoneme FM + harmonics

### With Linear B Glyph
```
smn nṯrwy nfr <A1> ḥr wḥw
(Establish the good gods <A1> on the altar)
```

**Audio features:**
- Base carrier: varies by line
- **<A1> glyph** → Sawtooth wedge strikes (6 strikes at 240 Hz with -7 cents detune)
- Exponential decay envelopes
- Phoneme FM + harmonics

### With Node137 Spawn
```
ṯs‑ỉt 137 m ḫnt iwf
(Raise up 137 in the vanguard of flesh)
```

**Audio features:**
- Base carrier: 220 Hz
- **137 trigger** → Node spawn burst effect (sawtooth burst with +11 cents detune, exponential decay)
- Phoneme FM + harmonics

## JSON Payload Example

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
      "line_index": 4,
      "text": "ṯs‑ỉt 137 m ḫnt iwf",
      "carrier": 220.0,
      "duration": 8.0,
      "sha256": "ef0f5961d1041a75dc5d7153204af4a6821b90a03a13b79c857ce08557eff741",
      "triggers": ["node137_spawn"]
    },
    {
      "line_index": 5,
      "text": "ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ [DINGIR]",
      "carrier": 277.18,
      "duration": 8.0,
      "sha256": "dd0c82592efd6bab29c615139a2b3fc2caec4b60f5de6390c4e421e6163709cf",
      "triggers": ["charity_7pct"]
    }
  ]
}
```

## Customization

### Modify Source Text

Edit the `SOURCE_LINES` array in `aetherlingua_full.py`:

```python
SOURCE_LINES = [
    "Your custom Kemetic text here",
    "Add [DINGIR] for Sumerian glyphs",
    "Include 137 for node spawn",
    "Include 7% for charity trigger"
]
```

### Adjust Audio Parameters

```python
SAMPLE_RATE = 48000     # Hz - higher = better quality, larger files
BIT_DEPTH = 24          # bits - 16 or 24 recommended
DURATION = 8.0          # seconds per line
SEED = 1337             # RNG seed - change for different variations
```

### Add Custom Sumerian Glyphs

```python
SUMERIAN_GLYPHS = {
    "YOUR_GLYPH": ("phonetic", base_freq_hz, wedge_count),
    "DINGIR": ("an", 261.63, 5),
    # Add more glyphs...
}
```

### Adjust Carrier Frequencies

```python
LINE_CARRIERS = [
    110.0,   # A2
    138.59,  # C#3
    174.61,  # F3
    220.0,   # A3
    277.18,  # C#4
    349.23   # F4
]
```

## Phoneme Categories

| Category | Example Characters | Sonification |
|----------|-------------------|--------------|
| Vowel    | a, e, i, o, u, ỉ, ȝ, ꜣ | 5.0 Hz FM, index 1.8 |
| Voiced   | b, d, g, ḏ, ḥ, ḫ, ḳ | 7.0 Hz FM, index 2.4 |
| Sibilant | s, š, ẖ, ṯ | 12.0 Hz FM, index 1.2 |
| Stop     | p, t, k, ḳ | 18.0 Hz FM, index 0.9 |
| Nasal    | m, n, r, l, w | 3.5 Hz FM, index 1.1 |
| Punct    | punctuation | 0.5 Hz FM, index 0.6 |

## Special Effects

### Charity Gliss (7% Trigger)
- Activates when text contains "7%"
- Triangle wave glissando
- Sweeps from carrier × 1.5 to carrier × 2.2 over 1.2 seconds
- Amplitude: 0.38

### Node137 Burst
- Activates when text contains "137"
- Sawtooth burst with +11 cents microtonal offset
- Exponential decay (tau = 6.0)
- Duration: 0.8 seconds
- Amplitude: 0.48

### Sumerian Wedge Strikes
- Activates for glyphs in brackets like [DINGIR]
- Percussive bronze-bell sonification
- Multiple strikes distributed over 1.0 seconds
- Inharmonic shimmer at 2.87× overtone
- Each strike has 0.6 second envelope

## Audio Analysis

Use standard tools to analyze the generated WAV files:

```bash
# View file info
file aetherlingua_line_1.wav

# Check audio properties with ffprobe (if installed)
ffprobe aetherlingua_line_1.wav

# Play audio (requires audio player)
aplay aetherlingua_line_1.wav  # Linux
afplay aetherlingua_line_1.wav # macOS
```

## SHA-256 Verification

Verify audio integrity using the SHA-256 hashes in the JSON payload:

```python
import json
import aetherlingua_full as al

# Load payload
with open('aetherlingua_payload.json') as f:
    data = json.load(f)

# Verify a specific line
line_data = data['renders'][0]
print(f"Line {line_data['line_index']}: {line_data['sha256']}")

# Re-render and verify hash matches
text = line_data['text']
carrier = line_data['carrier']
duration = line_data['duration']
left, right = al.render_line_to_buffers(text, carrier, duration)
computed_hash = al.sha256_bytes_from_wav(left, right)

assert computed_hash == line_data['sha256'], "Hash mismatch!"
print("✓ Hash verified!")
```

## SwarmGate Integration

The JSON payload is designed for blockchain integration:

1. **Trigger Detection**: Automatically identifies 7% and 137 triggers
2. **Deterministic Hashing**: SHA-256 ensures verifiable audio identity
3. **Metadata Structure**: Ready for smart contract ingestion
4. **Node Spawning**: 137 triggers can activate swarm node creation
5. **Charity Distribution**: 7% triggers can activate fund allocation

Example smart contract integration:

```javascript
// Pseudo-code for on-chain verification
function verifyAudio(audioData, metadata) {
    const computed_hash = sha256(audioData);
    require(computed_hash == metadata.sha256, "Invalid audio");
    
    if (metadata.triggers.includes("charity_7pct")) {
        distributeCharity(0.07);
    }
    
    if (metadata.triggers.includes("node137_spawn")) {
        spawnSwarmNode(137);
    }
}
```

## Performance Notes

- Each 8-second line generates ~2.2 MB WAV file (48kHz, 24-bit stereo)
- Rendering is CPU-intensive (pure Python signal processing)
- Expected render time: ~40-60 seconds for 6 lines on modern CPU
- Memory usage: ~50 MB during rendering

## Tips

1. **Determinism**: Same input + same seed = identical audio + identical hash
2. **Unicode**: Ensure terminal/editor supports Kemetic Unicode characters
3. **Audio Quality**: 24-bit @ 48kHz provides professional quality
4. **File Size**: Consider 16-bit for smaller files if 24-bit not needed
5. **Batch Processing**: Modify `main()` to load texts from external file

---

*For more details, see [AETHERLINGUA_README.md](AETHERLINGUA_README.md)*
