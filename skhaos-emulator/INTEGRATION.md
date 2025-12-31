# SkhaOS Emulator Integration Guide

## Quick Start

```bash
# Navigate to skhaos-emulator
cd skhaos-emulator

# Run demo
./demo.sh

# Execute phases
./phases/phase5_proxy.sh   # Sovereign proxy
./phases/phase6_audio.sh   # MIDI integration
./phases/phase7_recon.sh   # CLI recon

# Run evolution
./phases/evolve_recursive.sh 1 5
```

## Architecture Overview

### UDAP (Universal Domain Addressing Protocol)

UDAP URIs follow the format: `skhaos://domain/x/y/z?properties`

**Example URIs:**
```
skhaos://browser/127.0.0.1/8080/proxy?sovereign=true
skhaos://audio/440/A4/1?midi_file=beethoven_sym5.mid
skhaos://recon/probe/1/wave?sim=wave&hz=20
skhaos://net/192.168.1.1/80/tcp
skhaos://frequency/20/Hz/whale
```

### Domain Mapping

| Domain | Purpose | Example |
|--------|---------|---------|
| browser | Web proxy | `skhaos://browser/127.0.0.1/8080/proxy` |
| proxy | Alternative proxy | `skhaos://proxy/localhost/8080/http` |
| audio | Music/MIDI | `skhaos://audio/440/A4/1` |
| recon | Offline reconnaissance | `skhaos://recon/probe/1/wave` |
| frequency | Hz-based | `skhaos://frequency/20/Hz/whale` |
| mood | Emotional state | `skhaos://mood/delta/grounding/deep` |
| quantum | Entanglement | `skhaos://quantum/entangle/1/2` |

## Module Structure

```
src/
├── proxy_browser/      # Sovereign web proxy (hyper-based)
│   ├── mod.rs         # Main proxy server
│   ├── proxy_handler.rs  # UDAP request handling
│   └── offline_recon.rs  # Network simulation
│
├── audio_midi/        # Music integration
│   ├── mod.rs         # MIDI parser
│   ├── classical_pieces.rs  # 36 pieces
│   └── whale_freq.rs  # 10-40Hz mappings
│
├── cli_recon/         # 36 CLI commands
│   ├── main.rs        # Entry point
│   ├── mod.rs         # CLI parser
│   └── recon_cmds.rs  # Command implementations
│
├── control_unit/      # UDAP routing
│   ├── udap_parser.rs  # URI parsing
│   └── swarm_orchestrator.rs  # Evolution
│
├── entanglement_core/ # Quantum addressing
│   ├── domain_mapper.rs
│   └── superposition_sim.rs
│
├── register_memory/   # State management
│   ├── mood_state.rs  # Mood bands
│   └── uri_cache.rs   # Response caching
│
├── alu/              # Wave calculations
│   └── mod.rs        # Trig functions
│
├── io_unit/          # Network bridging
│   └── mod.rs        # Port binding
│
└── agents/           # AI components
    ├── gpt_assistant.rs   # Code generation
    ├── neural_tick_clock.rs  # Hz oscillation
    └── swarm_bots.rs  # Evolution

```

## Frequency Mappings

### Classical Music (36 Pieces)

| ID | Piece | Hz | Mood | Ratio vs 20Hz Whale |
|----|-------|----|----|---------------------|
| 1 | Beethoven Sym5 | 261 | beta | 13.05:1 |
| 3 | Bach Brandenburg | 440 | alpha | 22:1 |
| 7 | Debussy Clair | 330 | theta | 16.5:1 |
| 29 | Beethoven Moonlight | 261 | theta | 13.05:1 |

### Whale Frequencies

| Species | Hz | Band | Use Case |
|---------|----|----|----------|
| Blue Whale | 10-40 | delta | Deep grounding |
| Humpback | 20-30 | delta | Meditation |
| Fin Whale | 15-25 | delta | Ultra-low resonance |

### Mood Bands

| Band | Hz Range | State |
|------|---------|-------|
| Delta | 0.5-4 | Deep sleep, grounding |
| Theta | 4-8 | Meditation, creativity |
| Alpha | 8-12 | Relaxed focus |
| Beta | 12-30 | Active thinking |
| Gamma | 30+ | Peak cognition |

## CLI Commands (36 Total)

### Basic Commands
```bash
skhaos list                    # List all commands
skhaos validate <uri>          # Validate UDAP URI
```

### Wave Reconnaissance
```bash
skhaos recon --id 1 --uri skhaos://net/192.168.1.1/80/tcp --hz 20
# wave_probe: Simulate Hz ping at 20Hz

skhaos recon --id 2 --uri skhaos://recon/test/probe/1 --hz 20
# entangle_scan: Link domains via quantum entanglement

skhaos recon --id 3 --uri skhaos://net/example.com/443/https --hz 30
# packet_oscillate: TTL wave oscillation
```

### Music/Whale Commands
```bash
skhaos recon --id 6 --uri skhaos://audio/whale/blue/1 --hz 20
# whale_echo: Blue whale frequency (10-40Hz)

skhaos recon --id 23 --uri skhaos://audio/beethoven/sym5/1 --hz 261
# piece_1_beeth: Beethoven Symphony No.5

skhaos recon --id 33 --uri skhaos://audio/hybrid/entangle/1 --hz 440
# hybrid_whale_class: Entangle 20Hz whale + 440Hz classical
```

### Mood Band Scanning
```bash
skhaos recon --id 17 --uri skhaos://mood/delta/deep/1 --hz 2
# recon_delta: 0.5-4Hz low frequency scan

skhaos recon --id 18 --uri skhaos://mood/theta/meditation/1 --hz 6
# theta_probe: 4-8Hz medium frequency

skhaos recon --id 21 --uri skhaos://mood/gamma/insight/1 --hz 40
# gamma_insight: 30+ Hz peak cognition
```

### Proxy Commands
```bash
skhaos recon --id 15 --uri skhaos://browser/127.0.0.1/8080/proxy --hz 20
# browser_proxy: Sovereign hop with DDG-like privacy

skhaos recon --id 7 --uri skhaos://proxy/localhost/8080/tunnel --hz 20
# proxy_tunnel: IP/port mock tunnel
```

## Deployment

### Phase 5: Sovereign Proxy
Builds hyper-based proxy server with privacy-first design.

**Features:**
- Tracker blocking (DuckDuckGo methodology)
- No data collection
- UDAP routing
- Offline simulation mode

**Deploy:**
```bash
./phases/phase5_proxy.sh
```

### Phase 6: Audio/MIDI Integration
Loads 36 classical pieces and whale frequencies.

**Features:**
- MIDI parsing (midly crate)
- Frequency-to-mood mapping
- Whale song entanglement
- Hz calculations

**Deploy:**
```bash
./phases/phase6_audio.sh
```

### Phase 7: CLI Recon
Installs 36 offline reconnaissance commands.

**Features:**
- Symbolic network probes
- Quantum helm routing
- Wave oscillation
- Entanglement simulation

**Deploy:**
```bash
./phases/phase7_recon.sh
```

### Recursive Evolution
Swarm-based mutation of music-to-recon mappings.

**Features:**
- 10-bot parallel swarm
- ±0.2-0.4% frequency mutations
- Entanglement ratio optimization
- Fitness tracking

**Run:**
```bash
./phases/evolve_recursive.sh 1 5  # 5 iterations
```

## Containerization

### Podman Deployment

**Individual Pods:**
```bash
podman play kube containers/proxy_browser.pod
podman play kube containers/audio_midi.pod
podman play kube containers/cli_recon.pod
```

**Full Build:**
```bash
podman build -t skhaos-emulator -f containers/Podmanfile .
podman run -p 8080:8080 skhaos-emulator
```

## Development

### Building
```bash
# Build all modules
cargo build --release

# Build specific module
cd src/proxy_browser && cargo build --release
cd src/audio_midi && cargo build --release
cd src/cli_recon && cargo build --release
```

### Testing
```bash
# Run all tests
cargo test

# Test specific module
cargo test --package proxy_browser
cargo test --package audio_midi
```

### Linting
```bash
cargo clippy --all-targets --all-features
cargo fmt --check
```

## Privacy & Security

### DuckDuckGo-Inspired Privacy
- **No Tracking:** All tracking scripts blocked
- **No Data Collection:** Operations remain local
- **No Identifiers:** Headers stripped
- **Sovereign Mode:** User-controlled proxy

### Offline First
- **No Internet Required:** Simulations run locally
- **Symbolic Responses:** Quantum-addressed results
- **Cached Results:** URI response caching
- **Air-Gapped Compatible:** Runs without network

### Open Source
- **MIT License:** Fully open
- **No Vendor Lock-in:** Portable Rust code
- **Community-Driven:** Public development
- **Auditable:** All code visible

## Integration Examples

### Python Integration
```python
import subprocess
import json

# Execute recon command
result = subprocess.run([
    'skhaos', 'recon',
    '--id', '1',
    '--uri', 'skhaos://net/192.168.1.1/80/tcp',
    '--hz', '20'
], capture_output=True, text=True)

print(result.stdout)
```

### JavaScript Integration
```javascript
const { exec } = require('child_process');

exec('skhaos recon --id 1 --uri skhaos://net/192.168.1.1/80/tcp --hz 20',
  (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error}`);
      return;
    }
    console.log(stdout);
  }
);
```

### Rust Integration
```rust
use skhaos_emulator::control_unit::udap_parser::UdapAddress;

let addr = UdapAddress::parse("skhaos://browser/127.0.0.1/8080/proxy?sovereign=true")?;

if addr.is_proxy() {
    println!("Proxy address: {}:{}", addr.x, addr.y);
}
```

## Troubleshooting

### Common Issues

**Schema Validation Fails:**
```bash
# Install jq
sudo apt-get install jq
# Or use brew on macOS
brew install jq
```

**Cargo Build Errors:**
```bash
# Update Rust
rustup update stable
# Clean build
cargo clean && cargo build
```

**Permission Denied on Scripts:**
```bash
chmod +x phases/*.sh
chmod +x demo.sh
```

## Contributing

Part of **Strategickhaos DAO LLC** Sovereignty Architecture.

- EIN: 39-2900295
- Founder: Domenic Gabriel Garza
- ORCID: 0000-0005-2996-3526

## License

MIT License - See repository root for details.

---

*"Quantum-leaping this—fusing UDAP's universal addressing into a sovereign web browser proxy."* 🌊🎼💥
