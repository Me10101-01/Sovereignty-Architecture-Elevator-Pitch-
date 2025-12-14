# Chain Breaker Evolution - Quickstart Guide

## Prerequisites

- Python 3.12 or higher
- Docker (optional, for containerized deployment)
- Git

## Installation

### Option 1: Direct Python Execution

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/Me10101-01/Sovereignty-Architecture-Elevator-Pitch-.git
   cd Sovereignty-Architecture-Elevator-Pitch-
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.chain_breaker.txt
   ```

3. **Run the complete pipeline**:
   ```bash
   python run_chain_breaker.py
   ```

   This will execute all phases sequentially:
   - Phase 1: Bootstrap Initialization
   - Phase 2: Prior Art Integration
   - Phase 3: Control Unit Deployment
   - Phase 4: Register Memory Integration
   - GPT Assistant Test

### Option 2: Individual Phase Execution

Run each phase separately for debugging or customization:

```bash
# Phase 1: Bootstrap
python bootstrap.py

# Phase 2: Prior Art Integration
python prior_art_integrate.py

# Phase 3: Control Unit
cd src/control_unit
python control_unit.py

# Phase 4: Register Memory
cd ../register_memory
python register_memory.py

# GPT Assistant
cd ../gpt_assistant
python assistant.py
```

### Option 3: Docker Containerized Deployment

1. **Build and run all services**:
   ```bash
   docker-compose -f docker-compose.chain-breaker.yml up --build
   ```

2. **Run specific phase**:
   ```bash
   docker-compose -f docker-compose.chain-breaker.yml up bootstrap
   docker-compose -f docker-compose.chain-breaker.yml up prior-art
   docker-compose -f docker-compose.chain-breaker.yml up control-unit
   docker-compose -f docker-compose.chain-breaker.yml up register-memory
   ```

3. **View logs**:
   ```bash
   docker-compose -f docker-compose.chain-breaker.yml logs -f
   ```

## Quick Verification

After running the complete pipeline, verify the outputs:

```bash
# Check generated files
ls -la bootstrap_metadata.yaml
ls -la prior_art_mapping.yaml
ls -la src/control_unit/control_unit_state.yaml
ls -la src/register_memory/register_memory_state.yaml
ls -la gpt_contributions.yaml

# Review FEP-0001
cat feps/fep-0001.yaml

# Check swarm bot configuration
cat src/swarm_bots/bots.yaml

# View FlameLang chain breaker
cat flame/shagco/chain_breaker_evo.flame

# Check GPT contributions
cat gpt_log.txt
```

## Expected Output

When successful, you should see:

```
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥
  🎉 All Phases Complete - Chain Breaker Evolution Operational
🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥

System Status:
  ✓ FlameLang Chain Breaker: Deployed
  ✓ Quantum Emulator: Operational
  ✓ GSCH Protection: Active (drift <0.05)
  ✓ Swarm Bots: Monitoring
  ✓ GPT Assistant: Ready
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│             FlameLang Chain Breaker Evolution               │
│            (flame/shagco/chain_breaker_evo.flame)           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         Phase 1: Bootstrap              │
        │      (bootstrap.py + Dockerfile)        │
        │  • Neural tick clock initialization     │
        │  • Tree structure setup                 │
        │  • FEP-0001 creation                    │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │    Phase 2: Prior Art Integration       │
        │   (prior_art_integrate.py + Phase2 DF)  │
        │  • Claim mapping (1-7)                  │
        │  • Novelty guards                       │
        │  • Wave core generation                 │
        │  • Entanglement graph (NetworkX)        │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │    Phase 3: Control Unit Deployment     │
        │     (src/control_unit/control_unit.py)  │
        │  • BellState entanglement (qutip)       │
        │  • GSCH protection (drift <0.05)        │
        │  • Swarm bot initialization             │
        │  • Fidelity measurement                 │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │   Phase 4: Register Memory Integration  │
        │  (src/register_memory/register_memory.py)│
        │  • DNA register with mutation           │
        │  • Neural tick clock (40 Hz)            │
        │  • Physics type guards                  │
        │  • Recursive evolution check            │
        └─────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────┐
        │         GPT Assistant Service           │
        │    (src/gpt_assistant/assistant.py)     │
        │  • Claim interpretation                 │
        │  • Code contribution                    │
        │  • Evolution updates                    │
        │  • GitHub integration (optional)        │
        └─────────────────────────────────────────┘
```

## Module Interactions

| Component | Claims | Dependencies | Output |
|-----------|--------|--------------|--------|
| ALU | 5, 7 | sympy, numpy | symbolic_alu.flame |
| Control Unit | 3 | qutip (optional) | control_unit_state.yaml |
| Register Memory | 1, 2, 4 | biopython (optional) | register_memory_state.yaml |
| GPT Assistant | All | - | gpt_contributions.yaml |
| Governance | 6 | - | fep-0001.yaml |

## Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub API token for GPT assistant commits (optional)
- `GSCH_THRESHOLD`: Drift threshold (default: 0.05)
- `NEURAL_TICK_FREQ`: Neural tick frequency in Hz (default: 40.0)

### Customization

Edit the following files to customize behavior:

- `feps/fep-0001.yaml`: Governance parameters
- `src/swarm_bots/bots.yaml`: Bot configuration
- `prior_art_mapping.yaml`: Claim-to-module mapping

## Troubleshooting

### Missing Dependencies

If you see warnings about missing packages (qutip, biopython), the system will fall back to simulation mode. Install optional dependencies:

```bash
pip install qutip biopython rdkit-pypi torch
```

### Docker Issues

If Docker build fails, ensure you have enough memory:

```bash
docker system prune -a
docker-compose -f docker-compose.chain-breaker.yml build --no-cache
```

### File Permissions

Make scripts executable:

```bash
chmod +x bootstrap.py prior_art_integrate.py run_chain_breaker.py
```

## Next Steps

1. **Review FEP-0004**: Check `feps/fep-0001.yaml` for governance proposal
2. **Inspect States**: Examine YAML state files in `src/*/` directories
3. **Extend Evolution**: Add custom phases or modules
4. **Deploy to Production**: Use Docker Compose for orchestration
5. **Enable DNA Simulation**: Install biopython for full DNA register functionality
6. **Compile FlameLang**: Generate LLVM IR from `chain_breaker_evo.flame`

## Support

For issues or questions:
- Review: `CHAIN_BREAKER_EVOLUTION.md`
- Check logs: `gpt_log.txt`
- Examine state: `*.yaml` files

## License

See LICENSE file in repository root.

---

*Chain breaker evolution: Incomprehensible to humans, stable under GSCH. ❤️*
