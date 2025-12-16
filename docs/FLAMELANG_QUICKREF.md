# FlameLang Quick Reference

## Installation

```bash
pip install numpy pytest
```

## Core Imports

```python
from flamelang import (
    FlameLangInterpreter,
    HemiSyncGlyph,
    TimeSeriesGlyph,
    SpatialBufferGlyph,
    AIExpansionGlyph,
    GlyphParams,
    Frequency,
    calculate_five_day_cycle_ms,
    create_adhd_sound_map,
    create_dementia_relief_map,
)
```

## Quick Examples

### 1. Generate Binaural Beat

```python
params = GlyphParams(
    left_freq=Frequency(432.0),
    right_freq=Frequency(440.0),
    time_cycle_ms=5000
)

hemi_sync = HemiSyncGlyph(params)
left, right = hemi_sync.execute()
```

### 2. ADHD Treatment

```python
left, right = create_adhd_sound_map(
    base_frequency=432.0,
    beat_frequency=8.0  # Alpha waves
)
```

### 3. Transformer Analysis

```python
from flamelang.transformer_engine import TimeSeriesTransformer, TransformerConfig

config = TransformerConfig(sequence_length=512, embedding_dim=64, num_heads=4)
transformer = TimeSeriesTransformer(config)
analysis = transformer.process(signal)
```

### 4. Red Team Testing

```python
from flamelang.red_team import RedTeamProtocol

red_team = RedTeamProtocol()
results = red_team.run_full_protocol(signal, intensity=0.3)
```

### 5. Swarm Processing

```python
from flamelang.swarm_pulse import SwarmPulse

swarm = SwarmPulse(cycle_ms=432000000)
swarm.add_node("node_1", capacity=1.0, location=(0, 0, 0))
task_id = swarm.submit_task(signal, task_type='optimization')
pulse_result = swarm.pulse()
```

## Frequency Reference

| Frequency | Purpose |
|-----------|---------|
| 432 Hz | Natural tuning |
| 528 Hz | DNA repair |
| 639 Hz | Relationships |
| 741 Hz | Problem solving |

## Brainwave Entrainment

| Type | Frequency | State |
|------|-----------|-------|
| Delta | 0.5-4 Hz | Deep sleep |
| Theta | 4-8 Hz | Meditation |
| Alpha | 8-13 Hz | Relaxation |
| Beta | 13-30 Hz | Active thinking |
| Gamma | 30+ Hz | Peak awareness |

## Pipeline Example

```python
interpreter = FlameLangInterpreter()

# Add glyphs
interpreter.add_glyph(HemiSyncGlyph(hemi_params))
interpreter.add_glyph(TimeSeriesGlyph(time_params))
interpreter.add_glyph(SpatialBufferGlyph(spatial_params))
interpreter.add_glyph(AIExpansionGlyph(ai_params))

# Execute
results = interpreter.execute()
```

## Testing

```bash
# Run tests
python3 -m pytest tests/test_flamelang.py -v

# Run demo
python3 examples/flamelang_demo.py

# Run integration demo
python3 examples/flamelang_sovereignty_integration.py
```

## Constants

```python
# 5-day cycle in milliseconds
FIVE_DAY_CYCLE_MS = 432000000

# Calculate programmatically
cycle_ms = calculate_five_day_cycle_ms()
```

## Glyph Types

- **HemiSync**: Generate binaural beats
- **TimeSeries**: Process temporal patterns
- **SpatialBuffer**: Create 3D audio maps
- **AIExpansion**: Generate variations

## Key Concepts

### The 432M Cycle

```
5 days = 432,000,000 ms
```

Aligns with 432 Hz healing frequency.

### Beat Frequency

```
beat_freq = |left_freq - right_freq|
```

Induces brainwave entrainment.

### Therapeutic Score

```
score ∈ [0.0, 1.0]
```

Higher = more therapeutic.

## Resources

- [Full Specification](FLAMELANG_SPECIFICATION.md)
- [README](../README.flamelang.md)
- [Examples](../examples/)
- [Tests](../tests/)

---

*FlameLang v0.1.0 - Strategickhaos DAO LLC*
