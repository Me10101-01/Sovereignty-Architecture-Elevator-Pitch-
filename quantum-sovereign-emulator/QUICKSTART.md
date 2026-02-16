# Phase 11 Quick Start Guide

## Installation

```bash
cd quantum-sovereign-emulator
pip install -r requirements.txt
```

## Run Full Demo

```bash
cd src/cube_simulator
python type_promotion_cube.py
```

**Expected Output:**
- YAML thought-log replay with 5 cognitive operations
- Reference parity checks (Cat→Dog fails, Dog→Animal succeeds)
- Bloom wave cores for all 6 cognitive levels
- Cognitive journey simulation
- Reference type hierarchy visualization

## Run Individual Components

### 1. Thought-Log Replay
```bash
cd quantum-sovereign-emulator/src/register_memory
python thought_log_overlay.py
```

### 2. Reference Parity Checker
```bash
cd quantum-sovereign-emulator/src/entanglement_core
python reference_parity_checker.py
```

### 3. Bloom Wave Cores
```bash
cd quantum-sovereign-emulator/src/alu
python bloom_wave_cores.py
```

### 4. Cognitive Cube
```bash
cd quantum-sovereign-emulator/src/cube_simulator
python cognitive_cube_spec.py
```

### 5. CLI Journey Sequencer
```bash
cd quantum-sovereign-emulator/src/cube_simulator

# Execute all phases
python cli_journey_sequencer.py --all

# Execute specific phase
python cli_journey_sequencer.py --phase 1

# Export to YAML
python cli_journey_sequencer.py --all --export-yaml build_log.yaml
```

## Sandbox Evolution

```bash
cd quantum-sovereign-emulator/sandbox
./evolve.sh
```

This will:
1. Validate YAML configuration
2. Run type promotion cube simulation
3. Execute all build phases (1-3)
4. Perform agent evolution analysis
5. Optionally commit and push changes

## Docker Usage

**Note:** Docker build may have SSL issues in restricted environments.

```bash
cd quantum-sovereign-emulator

# Build container
docker build -t thought-log -f docker/thought_log.Dockerfile .

# Run container
docker run --rm thought-log
```

## Configuration Files

All configurations are in `quantum-sovereign-emulator/configs/`:

- `thought_log.yaml` - Cognitive thought stream definitions
- `cube_mappings.json` - Bloom face to trig function mappings
- `oop_hierarchy.json` - Reference type hierarchy for parity checking

## Key Features Demonstrated

### YAML Thought-Log Schema
- Timestamped cognitive operations
- Bloom taxonomy face mapping
- Parity error tracking

### Reference Parity Checking
- Type hierarchy validation
- ClassCastException detection
- Wave-based invariant calculation

### Bloom Wave Cores
- 6 cognitive levels (REMEMBER → CREATE)
- Trigonometric wave functions
- Multi-dimensional synthesis

### Neural Tick Sequencer
- Phase 1 (Ticks 0-2): YAML substrate init
- Phase 2 (Ticks 3-5): Parity catalog build
- Phase 3 (Ticks 6-8): Visualization engine

## Troubleshooting

### Module Import Errors
Run Python from the correct directory:
```bash
cd quantum-sovereign-emulator/src/cube_simulator
python type_promotion_cube.py
```

### Config File Not Found
Individual modules need to be run from their directory, or use the main integration:
```bash
cd quantum-sovereign-emulator/src/cube_simulator
python type_promotion_cube.py  # This works!
```

### Missing Dependencies
```bash
pip install -r quantum-sovereign-emulator/requirements.txt
```

## Development

### Adding New Thought Operations
Edit `configs/thought_log.yaml` and add entries to `thought_stream`:

```yaml
- id: 6
  timestamp: "2026-01-12T05:00:00Z"
  operation: "NEW_OPERATION"
  active_face: "U"
  description: "Your operation description"
  parity_error: false
```

### Adding New Type Hierarchies
Edit `configs/oop_hierarchy.json` and extend the hierarchy:

```json
{
  "hierarchy": {
    "NewParent": {
      "parent": "Object",
      "children": ["ChildA", "ChildB"],
      "level": 1
    }
  }
}
```

### Customizing Wave Functions
Edit `src/alu/bloom_wave_cores.py` and modify `wave_functions` dict:

```python
self.wave_functions = {
    'REMEMBER': lambda x: math.sin(x),
    'YOUR_CUSTOM': lambda x: your_function(x),
}
```

## Next Steps (Phase 12+)

- Enhanced matplotlib visualizations
- Real-time thought-log streaming
- Multi-agent coordination
- Quantum state persistence
- Integration with existing infrastructure

## Support

See full documentation in `quantum-sovereign-emulator/README.md`
