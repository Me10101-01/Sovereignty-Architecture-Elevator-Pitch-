# Quick Start Guide - Sovereignty Architecture Phases 5-7

## Overview

This implementation provides Phases 5-7 of the Sovereignty Architecture emulator with swarm bot recursive evolution, superposition expansion, and Ripley gate optimization.

## Prerequisites

- Python 3.11+
- Docker or Podman (for containerized deployment)
- Dependencies: `pyyaml`, `numpy`, `sympy`, `networkx`

## Quick Test

Run all phases locally:

```bash
./test_phases.sh
```

This will execute all 7 phases in sequence and generate output files.

## Phase-by-Phase Execution

### Phase 5: Full Integration & Swarm Activation

```bash
python phase5/integrate.py
```

**Output:**
- Swarm bot activation
- Neural tick emulation
- GSCH drift detection
- Memory evolution (DNA register)

**Key Metrics:**
- Drift threshold: >0.05
- Novelty gate: >0.7
- Wave frequency: 40Hz

### Phase 6: Superposition Expansion

```bash
python phase6/expand_claim8.py
```

**Output:**
- `feps/novel_table.yaml` - Refined claims table
- BellState superposition simulation
- Ripley 12 gates exploration

**Novel Claims:**
- True Firsts: 5, 6, 8
- Variants: 2, 3
- Prior Art: 1, 4, 7

### Phase 7: Ripley Gates Deepening & Benchmarks

```bash
python phase7/deepen_ripley_explore_sagco.py
```

**Output:**
- `benchmarks/ripley_sagco.yaml` - Benchmark results
- Paracelsus three principles integration
- SAGCO → SHAGCO evolution path

**Benchmark Results:**
- Speed: ~25-27M ops/sec
- Stability: True (max amplitude ≤ 1.0)
- Drift handling: <0.05

## Container Deployment

### Using Docker Compose

```bash
# Build all services
docker-compose -f compose.yaml build

# Run all phases
docker-compose -f compose.yaml up

# Run specific phase
docker-compose -f compose.yaml up integration

# View logs
docker-compose -f compose.yaml logs -f integration
```

### Using Podman Compose

```bash
# Build all services
podman-compose -f compose.yaml build

# Run all phases
podman-compose -f compose.yaml up

# Run specific phase
podman-compose -f compose.yaml up integration

# View logs
podman-compose -f compose.yaml logs -f integration
```

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Phase 1-4  │────▶│   Phase 5   │────▶│   Phase 6   │
│  Bootstrap  │     │ Integration │     │Superposition│
└─────────────┘     └─────────────┘     └─────────────┘
                           │                     │
                           │                     ▼
                           │            ┌─────────────┐
                           └───────────▶│   Phase 7   │
                                        │Ripley/SAGCO │
                                        └─────────────┘
```

## Key Components

### QuantumAIEmulator (Phase 5)
- **Symbolic ALU**: Trigonometric wave operations
- **Entanglement Core**: NetworkX graph simulation
- **DNA Register**: Novelty-gated evolution
- **Swarm Bots**: Recursive monitoring and evolution

### GSCH Superposition (Phase 6)
- **BellState Primitives**: Quantum-inspired gradient states
- **Observation Collapse**: Drift-triggered stabilization
- **Ripley Gates**: 12 alchemical optimization passes

### Paracelsus Principles (Phase 7)
- **Salt**: Clamp, stabilize, emit (gates: Calcination, Congelation, Projection)
- **Mercury**: Feedback, transform, optimize (gates: Dissolution, Conjunction, Sublimation, Exaltation)
- **Sulfur**: Buffer, repair, cross-domain (gates: Separation, Putrefaction, Fermentation)

## Generated Files

After running all phases, you'll have:

```
feps/
  └── novel_table.yaml          # Refined novel claims table

benchmarks/
  └── ripley_sagco.yaml         # Performance benchmarks

docs/
  └── prior_art.pdf.yaml        # Claims database

src/swarm_bots/
  └── bots.yaml                 # Swarm bot configuration
```

## Environment Variables

Create a `.env` file (optional):

```bash
GITHUB_TOKEN=your_token_here    # For swarm bot git operations (disabled by default)
```

## Validation

Verify successful execution:

1. **Phase 5 Output**: Swarm bots activated, drift detected
2. **Phase 6 Output**: Novel table written, superposition collapsed/maintained
3. **Phase 7 Output**: Benchmark speedup >20M ops/sec, stability: True

## Troubleshooting

### Import Errors

```bash
pip install pyyaml numpy sympy networkx
```

### File Not Found

Ensure you're running from the repository root:
```bash
cd /path/to/Sovereignty-Architecture-Elevator-Pitch-
python phase5/integrate.py  # Correct
```

### Docker Build Failures

Check Docker is running:
```bash
docker --version
docker ps
```

## Next Steps

1. **Review Generated Files**: Check `feps/novel_table.yaml` and `benchmarks/ripley_sagco.yaml`
2. **Customize Swarm Bots**: Edit `src/swarm_bots/bots.yaml`
3. **Adjust Claims**: Modify `docs/prior_art.pdf.yaml`
4. **Tune Parameters**: Edit phase scripts for different thresholds

## Documentation

- **PHASES_README.md**: Detailed architecture documentation
- **compose.yaml**: Container orchestration
- **Dockerfiles**: Phase-specific container definitions

## Support

For issues or questions, refer to the main README.md or open an issue on GitHub.
