# Whale Song Frequency Samples

This directory contains synthesized whale song frequency samples (10-40 Hz).

## Samples

- `blue_whale_20hz.wav` - Blue whale call at 20Hz (deep delta)
- `humpback_25hz.wav` - Humpback whale song at 25Hz (delta)
- `fin_whale_18hz.wav` - Fin whale pulse at 18Hz (ultra-low)
- `bowhead_30hz.wav` - Bowhead whale at 30Hz (delta-theta transition)
- `gray_whale_35hz.wav` - Gray whale at 35Hz (theta)

## Generation

Whale frequencies are synthesized using the ALU trigonometric wave functions:
- `alu::sine_wave(hz, time)` - Pure sine wave at target Hz
- `alu::oscillate(hz, duration, samples)` - Full waveform

Example:
```rust
use skhaos_emulator::alu;

// Generate 1 second of 20Hz blue whale frequency
let samples = alu::oscillate(20.0, 1.0, 44100);
```

## Mood Band Correlation

| Frequency Range | Mood Band | Mental State |
|----------------|-----------|--------------|
| 0.5-4 Hz | Delta | Deep sleep, grounding |
| 4-8 Hz | Theta | Meditation, creativity |
| 8-12 Hz | Alpha | Relaxed focus |
| 12-30 Hz | Beta | Active thinking |
| 30+ Hz | Gamma | Peak cognition |

Whale frequencies (10-40 Hz) overlap with delta and theta bands, 
promoting deep grounding and meditative states.

## Entanglement with Classical Music

Whale frequencies can be entangled with classical piece fundamentals:
- 20Hz whale + 440Hz A4 = 22:1 ratio
- 30Hz whale + 261Hz C = 8.7:1 ratio

See `audio_midi::whale_freq::entangle_frequencies()` for implementation.

**Note**: Actual audio files not included. Generate using ALU wave functions 
or source from scientific whale song databases.
