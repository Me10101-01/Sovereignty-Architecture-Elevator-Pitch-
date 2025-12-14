# AetherLingua - Living Glyph Language Engine 🔥

**Deterministic, sovereign, ancient-text-to-executable-sound**

AetherLingua is a FlameLang-inspired runtime that treats **any ancient script** (Kemetic, Sumerian cuneiform, Linear A, Rongorongo) as **executable sonic-cognitive DNA**.

## Concept

This is **not music**. This is **language that breathes, thinks, and allocates treasury**.

- Text → deterministic tokenization → phoneme/glyph mapping → multi-layered audio synthesis
- Audio → cryptographic hash → seed for VFASP speculation → new code generation
- 7% motif → real SwarmGate treasury trigger
- Node numbers (137) → spawn new speculative paths in the swarm
- The rendered sound becomes **proof of invocation** — immutable, beautiful, and on-chain verifiable

## Features

### Kemetic Layer
- **Deterministic tokenization** of Kemetic hieroglyphic text
- **Phoneme classification**: vowels, voiced, sibilants, stops, nasals
- **FM synthesis** with phoneme-specific modulation parameters
- **Special motifs**:
  - 7% charity glissando (treasury trigger)
  - Node 137 burst (speculative path spawner)
- **Harmonic enrichment**: subharmonics, overtones, bronze bell harmonics
- **ADSR envelope** shaping
- **Stereo panning** with carrier-based positioning

### Sumerian Layer
- **Cuneiform glyph tokenization**: DINGIR, LUGAL, EN, NIN, KALAM, AN, KI, ŠARRU, NAM, ME
- **Percussive transients**: each wedge strike = bronze bell strike
- **Rhythm density**: wedge count determines strike pattern
- **Bronze bell harmonics**: 432 Hz and microtonal variations
- **Spatial positioning**: dynamic panning based on timing

### Audio Engine
- **48kHz sample rate** (professional quality)
- **24-bit depth** (studio precision)
- **Multi-oscillator synthesis**: sine, sawtooth, triangle
- **Algorithmic reverb**: feedback delay network
- **WAV file export**: standard format for maximum compatibility

## Architecture

```
src/aetherlingua/
├── index.ts                 # Main exports
├── engine.ts               # Core AetherLingua engine
├── types.ts                # TypeScript type definitions
├── oscillators.ts          # Waveform generators & effects
├── synthesizer.ts          # Audio synthesis engine
├── wav-writer.ts           # 24-bit WAV file writer
├── tokenizers/
│   ├── kemetic.ts         # Kemetic hieroglyphic tokenizer
│   └── sumerian.ts        # Sumerian cuneiform tokenizer
├── examples/
│   ├── kemetic-invocation.ts    # Kemetic example
│   ├── sumerian-glyphs.ts       # Sumerian example
│   └── hybrid-invocation.ts     # Hybrid example
└── README.md              # This file
```

## Usage

### Kemetic Invocation

```typescript
import { AetherLingua } from './aetherlingua';

const engine = new AetherLingua({
  sampleRate: 48000,
  bitDepth: 24,
  duration: 8.0,
  seed: 1337
});

const kemeticLines = [
  'Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb',
  'Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṯ‑ḥr',
  'smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr',
  'ṯs‑ỉt 137 m ḫnt iwf',
  'ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ',
  'Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ ⚔️'
];

const files = engine.renderKemeticInvocation(kemeticLines, './output');
// Generates: aetherlingua_kemetic_1.wav ... aetherlingua_kemetic_6.wav
```

### Sumerian Cuneiform

```typescript
import { AetherLingua } from './aetherlingua';

const engine = new AetherLingua();

// Each glyph becomes percussive bronze bell strikes
const sumerianText = 'DINGIR LUGAL EN NIN AN KI';

const file = engine.renderSumerianInvocation(
  sumerianText,
  './output/sumerian_invocation.wav'
);
```

### Hybrid Invocation

```typescript
import { AetherLingua } from './aetherlingua';

const engine = new AetherLingua({ duration: 12.0 });

const kemetic = ['ḥsb 7% dỉ ỉb nfr', 'ṯs‑ỉt 137 m ḫnt iwf'];
const sumerian = 'DINGIR LUGAL ŠARRU';

const file = engine.renderHybridInvocation(
  kemetic,
  sumerian,
  './output/hybrid.wav'
);
```

## Phoneme Classification

### Kemetic Phonemes

| Class | Characters | FM Params |
|-------|-----------|-----------|
| Vowel | a, e, i, o, u, y, ỉ, ȝ, ꜣ | 5.0 Hz @ 1.8 idx |
| Voiced | b, d, g, ḏ, ḥ, ḫ, ḳ | 7.0 Hz @ 2.4 idx |
| Sibilant | s, š, ẖ, ṯ | 12.0 Hz @ 1.2 idx |
| Stop | p, t, k, ḳ | 18.0 Hz @ 0.9 idx |
| Nasal | m, n, r, l, w | 3.5 Hz @ 1.1 idx |

### Sumerian Glyphs

| Glyph | Wedges | Intensity | Bronze Bell |
|-------|--------|-----------|-------------|
| DINGIR | 8 | 0.95 | 432 Hz |
| LUGAL | 6 | 0.88 | 384 Hz |
| EN | 4 | 0.75 | 288 Hz |
| NIN | 5 | 0.80 | 324 Hz |
| ŠARRU | 9 | 0.92 | 486 Hz |

## Carrier Frequencies

Line carriers based on A=110Hz fundamental series:

1. 110.00 Hz (A2)
2. 138.59 Hz (C#3)
3. 174.61 Hz (F3)
4. 220.00 Hz (A3)
5. 277.18 Hz (C#4)
6. 349.23 Hz (F4)

## Special Motifs

### 7% Charity Glissando
When text contains "7%", triggers:
- Triangle wave glissando from 1.5× to 2.2× carrier
- Duration: 1.2 seconds
- Amplitude: 0.35
- **SwarmGate treasury trigger**

### Node 137 Burst
When text contains "137", triggers:
- Sawtooth burst with microtonal offset (+11¢)
- Exponential decay (τ = 6.0)
- Duration: 0.8 seconds
- Amplitude: 0.45
- **Spawns new speculative paths**

## Proof of Invocation

```typescript
import { AetherLingua, AudioSynthesizer } from './aetherlingua';

const engine = new AetherLingua();
const buffer = AudioSynthesizer.renderLine(
  'ḥsb 7% dỉ ỉb nfr',
  220.0,
  engine.config
);

// Get cryptographic hash (on-chain verifiable)
const hash = await engine.getAudioHash(buffer);

// Generate VFASP seed for new code generation
const seed = engine.generateVFASPSeed(hash);
```

## Running Examples

```bash
# Kemetic invocation
tsx src/aetherlingua/examples/kemetic-invocation.ts

# Sumerian glyphs
tsx src/aetherlingua/examples/sumerian-glyphs.ts

# Hybrid invocation
tsx src/aetherlingua/examples/hybrid-invocation.ts
```

## Technical Details

### Audio Synthesis Pipeline

1. **Tokenization**: Text → classified tokens
2. **Carrier selection**: Line index → frequency
3. **FM synthesis**: Phoneme → modulation params
4. **Oscillator**: Generate waveform
5. **Harmonics**: Add subharmonic + overtones + bronze bells
6. **Motifs**: Apply special patterns (7%, 137)
7. **Envelope**: Shape with ADSR
8. **Stereo**: Apply panning pattern
9. **Reverb**: Feedback delay network
10. **Export**: Write 24-bit WAV

### Determinism

All operations are deterministic given the same seed:
- RNG (if needed) uses fixed seed (1337)
- No external time dependencies
- Pure mathematical operations
- Same input = same output = same hash

## Philosophy

> We are not recreating ancient sound.  
> We are **resurrecting ancient intent as executable sovereignty**.

The swarm is listening.  
The flame is speaking.

---

**AetherLingua** - Where ancient language becomes living code. 🔥
