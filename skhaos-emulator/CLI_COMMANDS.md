# 42 Recon Commands: Bio-Physics CLI Reference

## Overview

The SkhaOS BPEC system provides 42 recon commands organized into three groups:
1. **Zipf Whale Group** (1-18): Humpback whale song patterns
2. **Dolphin Group** (19-21): Dolphin communication patterns  
3. **Physics DOM Group** (37-42): Musical forms with physics constraints

## Complete Command Table

### Zipf Whale Group (Commands 1-18)

Commands 1-18 analyze humpback whale songs using Zipf's law (frequency ~ 1/rank).

| ID | Command | Freq (Hz) | Bio Type | Pattern | Physics Law | UDAP URI |
|----|---------|-----------|----------|---------|-------------|----------|
| 1 | wave_probe | 20.0 | Humpback Zipf | High-rank short unit | Entropy minimization | `skhaos://bio/zipf/unit/1?law=entropy&hz=20` |
| 2 | entangle_scan | 500.0 | Humpback Zipf | Phrase distribution | Uncertainty branching | `skhaos://bio/zipf/phrase/rank?hz=500` |
| 3 | packet_oscillate | 1000.0 | Humpback Zipf | Menzerath brevity | Conservation of energy | `skhaos://bio/zipf/moan?brevity=true&hz=1000` |
| 4-18 | (extended) | Various | Humpback Zipf | Hierarchical units | Various laws | `skhaos://bio/zipf/*` |

**Key Concepts:**
- **Zipf's Law**: Most frequent units are shortest (efficiency)
- **Menzerath's Law**: Short units = high learnability
- **Cultural Evolution**: Patterns transmitted between populations
- **Entropy**: Zipf distribution minimizes communication entropy

### Dolphin Group (Commands 19-21)

Commands 19-21 model dolphin communication: whistles, clicks, and dialects.

| ID | Command | Freq (Hz) | Bio Type | Pattern | Physics Law | UDAP URI |
|----|---------|-----------|----------|---------|-------------|----------|
| 19 | dolphin_whistle | 10.0 | Dolphin | Signature name whistle | Relativity ID persistence | `skhaos://bio/dolphin/whistle?signature=true&hz=10` |
| 20 | echo_burst | 120.0 | Dolphin | Echolocation click burst | Quantum measurement collapse | `skhaos://bio/dolphin/click?burst=200&hz=120` |
| 21 | dialect_dialogue | 200.0 | Dolphin | Pod-specific chirp/scream | Entropy in learning | `skhaos://bio/dolphin/dialect?pod=alpha&hz=200` |

**Key Concepts:**
- **Signature Whistles** (1-20 kHz): Unique ID per individual
- **Echolocation Bursts** (120-200 kHz): Navigation and prey detection
- **Pod Dialects**: Matrilineal cultural transmission (like orcas)
- **Quantum Mapping**: Whistles → observer IDs, clicks → measurement operators

**Evolvability**: High (matrilineal inheritance + Zipf learning efficiency)

### Physics DOM Group (Commands 37-42)

Commands 37-42 apply physics laws to musical forms (Mozart's Rondo, Sonata, etc.).

| ID | Command | Freq (Hz) | Physics | Musical Form | Law Applied | UDAP URI |
|----|---------|-----------|---------|--------------|-------------|----------|
| 37 | rondo_cycle | 10.0 | Physics | ABACA with entropy reset | Conservation loop | `skhaos://physics/rondo?law=conservation&hz=10` |
| 38 | sonata_transform | 22.0 | Physics | Development with uncertainty | Heisenberg branching | `skhaos://physics/sonata?law=uncertainty&hz=22` |
| 39 | fugue_parallel | 28.0 | Physics | Threads with relativity sync | Spacetime coordination | `skhaos://physics/fugue?law=relativity&hz=28` |
| 40 | canon_delay | 33.0 | Physics | Replica with entropy decay | Thermodynamic replication | `skhaos://physics/canon?law=entropy&hz=33` |
| 41 | variation_mutate | 37.0 | Physics | Mutations with conservation | Energy-balanced evolution | `skhaos://physics/variation?law=conservation&hz=37` |
| 42 | coda_terminate | 40.0 | Physics | Collapse with uncertainty peak | Quantum final state | `skhaos://physics/coda?law=uncertainty&hz=40` |

**Key Concepts:**
- **Rondo (ABACA)**: Mozart's Rondo alla Turca - cyclic return with conservation
- **Sonata**: Development section with quantum uncertainty
- **Fugue**: Multiple voices (threads) coordinated via relativity
- **Canon**: Delayed replication with entropy increase
- **Variation**: Theme mutations with energy balance
- **Coda**: Final collapse with maximum uncertainty

## Physics Laws Explained

### 1. Entropy (Thermodynamics)
```
ΔS ≥ 0 (Second Law)
S = -Σ p_i * ln(p_i) (Shannon Entropy)
```
- Swarm mutations increase disorder
- Zipf distribution minimizes entropy (optimal efficiency)
- Applied in: Commands 1, 21, 40

### 2. Uncertainty (Quantum Mechanics)
```
Δx * Δp ≥ ℏ/2 (Heisenberg)
ℏ = 1.054571817 × 10^-34 J·s
```
- Superposition of states (multiple possibilities)
- Measurement collapses wave function
- Applied in: Commands 2, 38, 42

### 3. Conservation (Energy/Momentum)
```
E_total = constant
Σ |ψ_i|² = 1 (Probability normalization)
```
- Energy balanced in state transitions
- Momentum conserved in replication
- Applied in: Commands 3, 37, 41

### 4. Relativity (Spacetime)
```
ds² = -c²dt² + dx² + dy² + dz²
Spacetime interval invariant
```
- Observer-independent coordinates
- Dolphin signatures as persistent IDs
- Applied in: Commands 19, 39

## Usage Examples

### Command 1: wave_probe (Zipf High-Rank Unit)
```bash
# Analyze high-frequency whale moan (Zipf rank 1)
bpec-cli wave_probe --freq 20 --law entropy

# Output:
# Zipf Rank: 1
# Frequency: 20 Hz
# Entropy: 0.0 J/K (single unit, maximum order)
# UDAP: skhaos://bio/zipf/unit/1?law=entropy&hz=20
```

### Command 19: dolphin_whistle (Signature ID)
```bash
# Generate dolphin signature whistle
bpec-cli dolphin_whistle --dolphin alpha --freq 10000

# Output:
# Dolphin ID: alpha
# Base Frequency: 10000 Hz
# Contour: [10000, 12000, 15000, 12000, 10000]
# Quantum Probe: q_10 (coherence: 0.95)
# UDAP: skhaos://bio/dolphin/whistle?signature=true&hz=10
```

### Command 37: rondo_cycle (Mozart ABACA)
```bash
# Compile Mozart's Rondo with conservation law
bpec-cli rondo_cycle --form ABACA --law conservation

# Output:
# Form: A-B-A-C-A (cyclic return)
# Zipf Ranks: [5, 3, 5, 2, 5] (A most frequent)
# Energy: Conserved (normalized)
# Entropy: Resets at each A return
# UDAP: skhaos://physics/rondo?law=conservation&hz=10
```

### Command 20: echo_burst (Echolocation)
```bash
# Simulate dolphin echolocation burst
bpec-cli echo_burst --freq 150000 --clicks 20

# Output:
# Purpose: Navigation
# Center Frequency: 150000 Hz (150 kHz)
# Click Count: 20
# Inter-Click Interval: 50 μs
# Range: 100 m
# Quantum Mapping: Measurement collapse
# UDAP: skhaos://bio/dolphin/click?burst=20&hz=120
```

## Integration with MSMC (Music State Machine Compiler)

Commands compile to MSMC-executable states:

```
Zipf Pattern → MSMC State
- High-rank units → Priority registers
- Entropy → State transition costs

Dolphin Pattern → MSMC State
- Whistles → Recon wave operators
- Bursts → Measurement gates

Physics Law → MSMC Constraint
- Conservation → Normalization checks
- Entropy → Mutation acceptance
```

## FlameLang DSL Compilation

Commands can be compiled using FlameLang:

```flame
FLAME ZIPF("moan", "cry", "grumble") RANKED BY 1.0
  WITH ENTROPY INCREASES AND FREQUENCY IN [20, 4000]
  EMIT RUST MODULE bio_zipf;

FLAME DOLPHIN(WHISTLE) AT 10000 HZ
  WITH UNCERTAINTY <= 5.27e-35 AND ENERGY CONSERVED
  EMIT UDAP "skhaos://bio/dolphin/whistle?signature=true&hz=10000";
```

## Performance Metrics

| Command Group | Avg Execution Time | Memory Usage | Evolvability |
|---------------|-------------------|--------------|--------------|
| Zipf Whale | 50-100 ms | 10-20 MB | High (cultural) |
| Dolphin | 30-60 ms | 5-15 MB | High (matrilineal) |
| Physics DOM | 100-200 ms | 20-50 MB | Ecosystem-Complete |

## Total System Evolvability

**42 Commands, Overall Evolvability: Ecosystem-Complete**

- Zipf + Dolphin: Bio-pattern swarms
- Physics DOM: Universal constraints
- UDAP: Everything addressable
- BPEC: Symbolic quantum compilation

## API Reference

### Python API
```python
from bio_physics import BPECCompiler

# Initialize compiler
bpec = BPECCompiler()

# Compile pattern
state = bpec.compile("whale moan")
print(f"Zipf Rank: {state.zipf_rank}")
print(f"Entropy: {state.entropy}")
```

### Rust API (Conceptual)
```rust
use bio_physics::BPECCompiler;

let mut compiler = BPECCompiler::new();
let state = compiler.compile("whale moan").unwrap();
println!("Zipf Rank: {}", state.zipf_rank);
```

## References

See main README.md for scientific references on Zipf's law, dolphin communication, and physics applications.

---

**Version**: 1.0.0  
**Last Updated**: December 31, 2025  
**Invention**: INVENTION_074 - Bio-Physics Entanglement Compiler
