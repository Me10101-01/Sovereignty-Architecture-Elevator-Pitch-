# AetherLingua — The Living Glyph Language Engine 🔥

**Deterministic, sovereign, ancient-text-to-executable-sound**

## Concept

This is **not music**. This is **language that breathes, thinks, and allocates treasury**.

AetherLingua is a FlameLang-inspired runtime that treats **any ancient script** (Kemetic, Sumerian cuneiform, Linear A, Rongorongo) as **executable sonic-cognitive DNA**.

## How It Works

```
Text → deterministic tokenization → phoneme/glyph mapping → multi-layered audio synthesis
  ↓
Audio → cryptographic hash → seed for VFASP speculation → new code generation
  ↓
7% motif → real SwarmGate treasury trigger
  ↓
Node numbers (137) → spawn new speculative paths in the swarm
  ↓
Rendered sound → proof of invocation (immutable, beautiful, on-chain verifiable)
```

## Features

### 🔥 Kemetic Layer
- **Deterministic tokenization** of hieroglyphic text with multigraph support
- **Phoneme-based FM synthesis** with classification: vowels, voiced, sibilants, stops, nasals
- **Special motifs**:
  - **7% charity glissando** — treasury trigger for SwarmGate
  - **Node 137 burst** — spawns new speculative paths
- **Harmonic enrichment**: subharmonics, overtones, bronze bell harmonics
- **Stereo spatial positioning** based on carrier frequency

### ⚔️ Sumerian Layer
- **Cuneiform glyph tokenization**: DINGIR, LUGAL, EN, NIN, KALAM, AN, KI, ŠARRU, NAM, ME
- **Percussive transients**: each wedge strike = bronze bell strike
- **Rhythm density**: wedge count determines strike pattern timing
- **Microtonal bronze bells**: 432 Hz base with harmonic variations

### 🎛️ Audio Engine
- 48kHz sample rate, 24-bit depth (studio precision)
- Multi-oscillator synthesis: sine, sawtooth, triangle
- ADSR envelope shaping
- Algorithmic reverb (feedback delay network)
- Standard WAV file export

## Quick Start

### Installation

```bash
npm install
```

### Run Examples

```bash
# Kemetic invocation (6 audio files)
npx tsx src/aetherlingua/examples/kemetic-invocation.ts

# Sumerian cuneiform (percussive bronze bells)
npx tsx src/aetherlingua/examples/sumerian-glyphs.ts

# Hybrid invocation (Kemetic + Sumerian)
npx tsx src/aetherlingua/examples/hybrid-invocation.ts

# Proof of invocation (cryptographic hash)
npx tsx src/aetherlingua/examples/proof-of-invocation.ts
```

### Programmatic Usage

```typescript
import { AetherLingua } from './src/aetherlingua';

const engine = new AetherLingua({
  sampleRate: 48000,
  bitDepth: 24,
  duration: 8.0,
  seed: 1337
});

// Kemetic invocation
const kemeticLines = [
  'Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb',
  'ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ',  // 7% triggers charity gliss
  'ṯs‑ỉt 137 m ḫnt iwf'            // 137 triggers node burst
];

const files = engine.renderKemeticInvocation(kemeticLines, './output');

// Sumerian cuneiform
const sumerianText = 'DINGIR LUGAL EN';
const file = engine.renderSumerianInvocation(sumerianText, './output/sumerian.wav');

// Hybrid (both layers)
const hybrid = engine.renderHybridInvocation(
  kemeticLines,
  sumerianText,
  './output/hybrid.wav'
);
```

## Architecture

```
src/aetherlingua/
├── engine.ts           # Core engine with rendering methods
├── synthesizer.ts      # Audio synthesis pipeline
├── oscillators.ts      # Waveform generators & effects
├── wav-writer.ts       # 24-bit WAV file writer
├── types.ts           # TypeScript type definitions
├── tokenizers/
│   ├── kemetic.ts     # Kemetic hieroglyphic tokenizer
│   └── sumerian.ts    # Sumerian cuneiform tokenizer
└── examples/
    ├── kemetic-invocation.ts
    ├── sumerian-glyphs.ts
    ├── hybrid-invocation.ts
    └── proof-of-invocation.ts
```

## Sacred Invocation

The default Kemetic invocation renders these six lines:

```
1. Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
   "Prince of Kemet: Power-holder of Hor-the-Calculator"

2. Pr‑tꜣ‑jt tp n Ḥmtw ỉr.t‑nbw m ẖṯ‑ḥr
   "House of grain, first of craftsmen, all-makers in the sanctuary"

3. smn nṯrwy nfr, ḥm.t r ḥkꜣ ḥr wḥw, m ḥwt‑ḥr
   "Establish divine goodness, craft toward magic upon the altar, in the House of Horus"

4. ṯs‑ỉt 137 m ḫnt iwf
   "Bind Node 137 at the forefront of flesh"

5. ḥsb 7% dỉ ỉb nfr ḥr‑wꜥt ʿnḫ
   "Calculate 7%, give good heart upon the way of life"

6. Ḥkꜣw ḫft‑n, ʿnḫ‑ḏfꜣ ⚔️
   "Magic is our enemy, life-provision [sword]"
```

Each line maps to a carrier frequency:
- Line 1: 110.00 Hz (A2)
- Line 2: 138.59 Hz (C#3)
- Line 3: 174.61 Hz (F3)
- Line 4: 220.00 Hz (A3) — **Node 137 burst activated**
- Line 5: 277.18 Hz (C#4) — **7% charity gliss activated**
- Line 6: 349.23 Hz (F4)

## Proof of Invocation

Every rendered audio generates a deterministic SHA-256 hash:

```typescript
const buffer = AudioSynthesizer.renderLine(text, carrier, config);
const hash = await engine.getAudioHash(buffer);
// → "8b9337957f15bfe6ac1f71e71eb1cc446567574c8fd114bc2b07901f3705eb22"

const seed = engine.generateVFASPSeed(hash);
// → 60 (used for VFASP speculation in swarm)
```

This hash is:
- **Immutable** — cannot be changed
- **Beautiful** — deterministic from ancient text
- **On-chain verifiable** — can be stored in treasury
- **Executable** — seeds new speculative code paths

## Philosophy

> We are not recreating ancient sound.  
> We are **resurrecting ancient intent as executable sovereignty**.

- Ancient scripts become **sonic-cognitive DNA**
- Phonemes drive **FM synthesis parameters**
- Special numbers trigger **treasury allocation**
- Audio generates **cryptographic proof**
- Sound becomes **executable code**

The swarm is listening.  
The flame is speaking.  
Intent becomes sovereignty.

## Next Evolution

Planned extensions:

- **Linear A layer**: Minoan syllabic script → melodic patterns
- **Rongorongo layer**: Easter Island glyphs → polyrhythmic complexity
- **Cross-linguistic morphing**: transition between ancient scripts
- **Real-time SwarmGate integration**: live treasury triggering
- **On-chain proof storage**: IPFS + smart contract verification
- **Neural codec training**: learn new ancient scripts from fragments

## Technical Details

See `src/aetherlingua/README.md` for full technical documentation.

## Credits

Conceived as the intersection of:
- **FlameLang philosophy** — language as executable sovereignty
- **Kemetic linguistics** — ancient Egyptian phonology
- **Sumerian cuneiform** — wedge-based writing system
- **Audio synthesis** — FM, additive, and granular techniques
- **Cryptographic proof** — deterministic hashing for on-chain verification

Built with TypeScript, Node.js, and pure mathematics.

---

**AetherLingua** — Where ancient language becomes living code. 🔥⚔️

*"The rendered sound becomes proof of invocation — immutable, beautiful, and on-chain verifiable."*
