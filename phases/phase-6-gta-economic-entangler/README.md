# Phase 6: GTA Online Passive Income Entanglement Core

## Overview

Phase 6 implements a **Quantum-Symbolic AI Emulator** for GTA Online passive income optimization using trigonometric wave modulation, particle swarm optimization, and recursive genetic algorithms.

## Architecture

### Components

1. **Neural Tick Clock** (`neural_tick_clock.py`)
   - Trigonometric wave-based time modulation
   - Popularity decay: `cos(2π * t / decay_period)`
   - Integration with Phase 5 scheduler

2. **Trig Wave Core** (`trig_wave_core.py`)
   - Production rate calculation with wave modulation
   - Base rate: `sin(2π * t / 48min)` for game day cycles
   - Dependency-aware rate adjustments

3. **Entanglement Core** (`entanglement_core.py`)
   - Quantum-inspired business dependency linking
   - Bunker→Nightclub warehouse passive accrual
   - Entanglement boost: up to 1.5x multiplier

4. **Strategickhaos Swarm** (`strategickhaos_swarm.py`)
   - Particle Swarm Optimization for sell timing
   - 50-particle swarm with cognitive/social parameters
   - Fitness function: total 24h yield

5. **GTA Economy Simulator** (`gta_economy_sim.py`)
   - Master orchestrator integrating all components
   - Quantum states mapped to income qubits
   - Auto-collection with cap enforcement

6. **Sandbox Evolver** (`sandbox_evolver.py`)
   - Recursive Genetic Algorithm
   - Population: 20 strategies, mutation rate: 0.01
   - Self-modifying strategy evolution

## Income Sources

### Truly Passive (No action required)
- **Nightclub Safe**: $250k cap, $50k/48min (max)
- **Agency Safe**: $250k cap, $20k/48min
- **Arcade Safe**: $100k cap, $5k/48min
- **Salvage Yard Safe**: $250k cap, $24k/48min
- **Garment Factory**: $50k cap, $1.75k/48min
- **Car Wash (x3)**: $100k cap, $4.5k/48min (boosted)

### Semi-Passive (Minimal action)
- **Acid Lab**: $300k cap, 0.25 units/min
- **Auto Shop Cars**: $20k-50k per car, ~1/15min
- **Payphone Hits**: $45k per hit, 10min cooldown

## Deployment

### Docker Compose
```bash
cd phases/phase-6-gta-economic-entangler
docker compose up --build
```

### Podman (Rootless)
```bash
podman build -t gta-economic-entangler -f Podmanfile .
podman run -v ./config:/app/config:ro gta-economic-entangler
```

### Codespaces
```bash
gh codespace create --repo Me10101-01/Sovereignty-Architecture-Elevator-Pitch- --branch main
cd phases/phase-6-gta-economic-entangler
python src/sandbox_evolver.py --iterations 1000 --mutate-rate 0.01
```

## Testing

Run full test suite:
```bash
cd phases/phase-6-gta-economic-entangler
python -m pytest tests/test_passive_loop.py -v
```

Run specific test:
```bash
pytest tests/test_passive_loop.py::TestGTAEconomySim::test_24hour_simulation -v
```

## Usage Examples

### Basic Simulation
```python
from gta_economy_sim import GTAEconomySim

sim = GTAEconomySim('config/income_sources.yaml')
sim.activate_all_dependencies()

results = sim.run(duration_hours=24, dt=1.0)
print(f"Total income: ${results['total_income']:,.0f}")
```

### Swarm Optimization
```python
sim = GTAEconomySim('config/income_sources.yaml')
sim.activate_all_dependencies()

opt_results = sim.optimize_with_swarm(duration_hours=24)
print(f"Best thresholds: {opt_results['best_thresholds']}")
```

### Recursive Evolution
```python
from sandbox_evolver import SandboxEvolver

evolver = SandboxEvolver('config/income_sources.yaml')
results = evolver.run(iterations=100, mutation_rate=0.01)
evolver.save_results('evolution_results.json')
```

## Performance Targets

- **24-hour simulation**: $2.5M+ optimized passive yield
- **Test execution**: <30 seconds for full suite
- **Evolution convergence**: <100 generations typical
- **Swarm optimization**: 100 iterations in ~10 seconds

## Configuration

Edit `config/income_sources.yaml` to modify:
- Income source rates and caps
- Dependency requirements
- Neural tick parameters
- Evolution/swarm settings

## Visualization

View flowchart in VSCode or Codespaces:
```bash
code docs/phase6-flowchart.mmd
```

Or render with Mermaid CLI:
```bash
mmdc -i docs/phase6-flowchart.mmd -o docs/phase6-flowchart.svg
```

## Next Phase

**Phase 7: Session Planner Agent**
- AI-generated session checklists
- GTA+ Vinewood boost integration
- Route optimization (Dijkstra)
- Auto-queue mission sequencing

See `prompts/gpt_phase6_contrib.md` for Phase 7 proposal.

## Commit Message Format

```
Phase6: <description>. <neural-component>. <swarm-component>. 
<dockerization>. <gpt-scaffold>. Ready for Phase7.
```

Example:
```
Phase6: Entangle GTA passive income flows into quantum symbolic ALU. 
Neural ticks drive trig-modulated production waves. Swarm bots evolve 
sell thresholds recursively. Dockerized per-module deploy via Codespaces. 
GPT scaffolding primed for Phase7 contrib.
```

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b phase6-enhancement`
3. Make changes and test: `pytest tests/`
4. Commit: `git commit -m "Phase6: Enhancement description"`
5. Push: `git push origin phase6-enhancement`
6. Create Pull Request

## License

Copyright © 2026 Strategickhaos DAO LLC. All rights reserved.

## Contact

- **Repository**: https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-
- **Issues**: https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-/issues
- **Security**: security@strategickhaos.ai
