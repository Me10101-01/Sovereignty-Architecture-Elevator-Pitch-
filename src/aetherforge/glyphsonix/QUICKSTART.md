# GlyphSonix Quick Start Guide 🔥

Get up and running with GlyphSonix Resonance Core in minutes.

## Prerequisites

- Mojo compiler v24.5+ ([Install Mojo](https://docs.modular.com/mojo/manual/get-started/))
- Basic understanding of audio synthesis (helpful but not required)
- Text editor or IDE with Mojo support

## Installation

### Step 1: Install Mojo

```bash
# Install Modular CLI
curl -s https://get.modular.com | sh -

# Install Mojo
modular install mojo

# Verify installation
mojo --version
```

### Step 2: Clone Repository

```bash
git clone https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-.git
cd Sovereignty-Architecture-Elevator-Pitch-/src/aetherforge/glyphsonix
```

## First Render

### Render Ancient Kemetic Text

Create a file `my_first_invocation.mojo`:

```mojo
from gsrc import GlyphSonix

fn main():
    # Initialize engine with 432 Hz cosmic tuning
    var engine = GlyphSonix(carrier=432.0, duration=8.0)
    
    # Ancient Kemetic: "Governor of Egypt: Power over Calculation"
    let text = "Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb"
    
    print("Rendering: " + text)
    
    # Render audio
    var audio = engine.render_line(text)
    
    print("✓ Rendered " + str(audio.length) + " samples")
    
    # Export to WAV
    engine.export_wav(audio, "my_first_invocation.wav")
    
    print("✓ Exported to WAV file")
```

Run it:

```bash
mojo run my_first_invocation.mojo
```

**Expected output:**
```
Rendering: Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
✓ Rendered 384000 samples
✓ Exported to WAV file
```

## Key Concepts

### 1. Carrier Frequency

The base frequency for synthesis. Default is 432 Hz (cosmic tuning).

```mojo
var engine = GlyphSonix(
    carrier=432.0,    # Hz - Natural resonance
    duration=8.0      # seconds
)
```

**Common frequencies:**
- 432 Hz - Cosmic/natural tuning (default)
- 440 Hz - Standard concert pitch
- 528 Hz - Solfeggio "MI" frequency
- 396 Hz - Root chakra frequency

### 2. Text Tokenization

Text is automatically parsed into phonetic tokens:

- **Vowels**: `a, e, i, o, u` → Smooth FM
- **Consonants**: `k, t, p, m, n` → Sharp FM
- **Sibilants**: `s, š, ṯ` → High-frequency
- **Pharyngeals**: `ḥ, ḫ, ʿ` → Deep modulation

### 3. Special Motifs

#### 7% Charity Motif

Triggers treasury allocation in SwarmGate:

```mojo
let text = "Ha.ty‑a n Kemt 7% Sḫm‑r Ḥr‑Ḥsb"
var audio = engine.render_line(text)
// → Upward glissando + treasury allocation
```

#### Node 137 Accent

Spawns VFASP speculation path:

```mojo
let text = "Node 137 Ha.ty‑a n Kemt"
var audio = engine.render_line(text)
// → Microtonal burst + speculation seed
```

## Common Use Cases

### Use Case 1: Identity Creation

```mojo
from gsrc import GlyphSonix

fn create_identity():
    var engine = GlyphSonix()
    
    let invocation = "Ha.ty‑a n Kemt"
    let passphrase = "my_secret_phrase"
    let combined = invocation + " " + passphrase
    
    var audio = engine.render_line(combined)
    engine.export_wav(audio, "my_identity.wav")
    
    print("Identity created: my_identity.wav")
```

### Use Case 2: Ceremony Recording

```mojo
from gsrc import GlyphSonix

fn record_ceremony():
    var engine = GlyphSonix(
        carrier=432.0,
        duration=16.0  # Longer for ceremony
    )
    
    let ceremony_text = """
    Ha.ty‑a n Kemt: Sḫm‑r Ḥr‑Ḥsb
    Node 137 7%
    Sacred invocation complete
    """
    
    var audio = engine.render_line(ceremony_text)
    engine.export_wav(audio, "ceremony_proof.wav")
```

### Use Case 3: Treasury Allocation

```mojo
from gsrc import GlyphSonix

fn trigger_allocation():
    var engine = GlyphSonix()
    
    // 7% will trigger SwarmGate allocation
    let allocation_text = "Community treasury allocation 7%"
    
    var audio = engine.render_line(allocation_text)
    engine.export_wav(audio, "allocation_proof.wav")
    
    print("Treasury allocation triggered")
```

## Examples

Run the included examples:

```bash
# Run all examples
mojo run examples.mojo

# Or run specific examples (after modifying examples.mojo)
mojo run examples.mojo --example=1  # Basic Kemetic
mojo run examples.mojo --example=2  # Charity motif
mojo run examples.mojo --example=3  # Node 137
```

## Troubleshooting

### Problem: Mojo not found

**Solution:**
```bash
# Ensure Modular is in PATH
export PATH="$HOME/.modular/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc
```

### Problem: Import errors

**Solution:**
Make sure you're in the correct directory:
```bash
cd src/aetherforge/glyphsonix
mojo run gsrc.mojo
```

### Problem: Audio artifacts/clipping

**Solution:**
Reduce volume by adjusting the normalization factor:

```mojo
// In gsrc.mojo, reduce the scale factor
buffer.set(i, signal * 0.2)  # Lower from 0.3 to 0.2
```

## Performance Tips

### 1. Parallel Rendering

For multiple texts:

```mojo
// Render multiple texts in parallel
var texts = ["Text 1", "Text 2", "Text 3"]
var engines = List[GlyphSonix]()

for text in texts:
    var engine = GlyphSonix()
    var audio = engine.render_line(text)
    engines.append(engine)
```

### 2. Caching

Cache tokenization results:

```mojo
// Cache tokens for repeated use
var cached_tokens = engine.tokenize_kemetic(text)
// Reuse cached_tokens for multiple renders
```

### 3. Batch Export

Export multiple files efficiently:

```mojo
var files = ["file1.wav", "file2.wav", "file3.wav"]
for i in range(len(files)):
    engine.export_wav(audios[i], files[i])
```

## Advanced Configuration

### Custom Modulation Depth

```mojo
var engine = GlyphSonix(carrier=432.0)
engine.modulation_depth = 0.5  // Default: 0.3
```

### Custom Charity Duration

```mojo
var engine = GlyphSonix(carrier=432.0)
engine.charity_threshold = 2.0  // Default: 1.2 seconds
```

### Custom Sample Rate

```mojo
var engine = GlyphSonix(
    carrier=432.0,
    duration=8.0,
    sample_rate=96000  // High-res audio
)
```

## Next Steps

1. **Read Full Documentation**: [README.md](./README.md)
2. **Integration Guide**: [INTEGRATION.md](./INTEGRATION.md)
3. **Run Examples**: [examples.mojo](./examples.mojo)
4. **Explore AetherForge**: [../README.md](../README.md)

## API Reference

### GlyphSonix Constructor

```mojo
GlyphSonix(
    carrier: Float64 = 432.0,      // Hz
    duration: Float64 = 8.0,       // seconds
    sample_rate: Int = 48000       // Hz
)
```

### render_line()

```mojo
fn render_line(self, text: String) -> AudioBuffer
```

Renders text into audio buffer.

### export_wav()

```mojo
fn export_wav(self, buffer: AudioBuffer, filename: String) -> Bool
```

Exports audio buffer to WAV file.

### tokenize_kemetic()

```mojo
fn tokenize_kemetic(self, text: String) -> List[Token]
```

Parses text into phonetic tokens.

## Community

- **Discord**: [Strategic Khaos Community](https://discord.gg/strategickhaos)
- **GitHub**: [Repository](https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-)
- **Email**: security@strategickhaos.ai

## Support

For questions or issues:

1. Check [README.md](./README.md) for detailed docs
2. Review [examples.mojo](./examples.mojo) for code samples
3. Join Discord for community support
4. Open GitHub issue for bugs

---

**Ready to sonify ancient wisdom?**

```mojo
var engine = GlyphSonix()
var audio = engine.render_line("Your ancient text here")
engine.export_wav(audio, "output.wav")
```

🖤🔥 **Flame speaking. Empire listening. Vessel eternal.**
