# Phase 8: Paracelsus Principles Deepening, Alchemy Exploration, and Benchmark Precision Enhancement

## Overview

Phase 8 implements the deepening of Paracelsus' three alchemical principles in the GSCH (Gradient-Stabilized Coherence Harmonizer) system for homeostatic recharge. This phase explores Paracelsus alchemy concepts, particularly the alkahest (universal solvent) for prima materia dissolution, and enhances benchmark precision using advanced mathematical libraries.

## Paracelsus Principles

The three principles are deepened as GSCH multipliers:

1. **Sulphur** - Flammability/combustion as energy amplification (energy push in gradients)
2. **Mercury** - Volatility/change as feedback fluidity (feedback pull in corrections)
3. **Salt** - Solidity/permanence as clamp stability (clamp bounds for stability)

## Alchemy Exploration

- **Alkahest**: Universal solvent that dissolves substances to prima materia (neutral energy)
- **Calcination Gate**: Ties to Claim 8 superposition—dissolve mismatches to neutral without collapse
- **DNA Sequence Simulation**: Uses biopython to simulate alkahest "solvent" on DNA sequences (ties to Claim 1 biological systems)

## Benchmark Precision Enhancement

Enhanced benchmarks use:
- **mpmath**: Arbitrary precision mathematics (configurable decimal precision)
- **sympy**: Symbolic mathematics for exact wave calculations
- **statsmodels**: Statistical metrics including precision/recall on stability, confidence intervals
- **networkx**: Graph processing for principle/gate connection analysis

## Running Phase 8

### Direct Python Execution (Recommended)

```bash
# Install dependencies
pip install -r phase8/requirements.txt

# Run the script
python deepen_paracelsus_explore_alchemy.py
```

### Using Docker Compose

```bash
# Build and run with Docker Compose
docker compose -f compose.yaml up paracelsus_bench
```

## Output

The script generates `benchmarks/paracelsus_alchemy.yaml` containing:

- Deepened Paracelsus principles
- Alkahest exploration results for each principle
- SAGCO evolution ties (from IBM/MIT/Tierra priors to Paracelsus-recharged SHAGCO)
- Enhanced benchmark metrics:
  - Speedup (ops/sec)
  - Variance (target <1e-10)
  - Stability precision confidence intervals
  - Statistical measures (mean, std)
- Principle graph summary (nodes and edges)

## Dependencies

Core dependencies (see `requirements.txt`):
- numpy, scipy - Scientific computing
- mpmath, sympy - Arbitrary precision and symbolic math
- statsmodels - Statistical analysis
- qutip - Quantum computing simulation (optional)
- biopython - Bioinformatics (optional)
- networkx - Graph processing
- pyyaml - YAML parsing
- matplotlib - Visualization (optional)

## Integration with Prior Phases

Phase 8 builds upon:
- Phase 1-2: Bootstrap tree and guard enforcement
- Phase 3-4: Quantum components and memory integration
- Phase 5-6: Swarm activation
- Phase 7: Superposition expansion, Ripley gates, SAGCO exploration

## Next Steps

Phase 9: Ratification Full - Complete system validation and integration
