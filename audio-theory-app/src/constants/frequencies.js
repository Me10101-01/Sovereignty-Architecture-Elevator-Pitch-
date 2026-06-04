// Pre-computed 88-key equal temperament frequency lookup table
// Formula: f(n) = 440 * 2^((n - 49) / 12)  where n = key number 1..88
// Key 49 = A4 = 440 Hz (ISO 16)

export const PIANO_FREQUENCIES = Object.freeze(
  Array.from({ length: 88 }, (_, i) => {
    const n = i + 1;
    return parseFloat((440 * Math.pow(2, (n - 49) / 12)).toFixed(3));
  })
);

// Named anchors
export const A4_FREQUENCY   = 440.000;    // Key 49
export const MIDDLE_C_FREQ  = 261.626;    // Key 40  (C4)
export const LOW_A_FREQ     = 27.500;     // Key 1   (A0)
export const HIGH_C_FREQ    = 4186.009;   // Key 88  (C8)
export const MIDI_OFFSET    = 20;         // Key 1 (A0) = MIDI 21

// Octave multipliers for quick transposition
export const OCTAVE_RATIO   = 2.0;
export const SEMITONE_RATIO = Math.pow(2, 1 / 12); // ≈ 1.05946
