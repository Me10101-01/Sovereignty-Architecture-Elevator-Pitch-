// Chromatic scale starting at C
export const CHROMATIC_SCALE = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

// Enharmonic flat equivalents for display
export const ENHARMONIC_FLATS = {
  'C#': 'Db', 'D#': 'Eb', 'F#': 'Gb', 'G#': 'Ab', 'A#': 'Bb'
};

// White key membership (used by keyboard renderer)
export const WHITE_NOTES = new Set(['C', 'D', 'E', 'F', 'G', 'A', 'B']);

// Solfège labels for Circle of Fifths display
export const SOLFEGE = {
  'C': 'Do', 'D': 'Re', 'E': 'Mi', 'F': 'Fa',
  'G': 'Sol', 'A': 'La', 'B': 'Si',
  'C#': 'Di', 'D#': 'Ri', 'F#': 'Fi', 'G#': 'Si', 'A#': 'Li'
};

// Major key signatures: number of sharps (+) or flats (-)
export const KEY_SIGNATURES = {
  'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5,
  'F#': 6, 'C#': 7, 'F': -1, 'A#': -2, 'D#': -3,
  'G#': -4, 'C#': -5, 'F#': -6, 'B': -7
};

// Relative minor for each major key
export const RELATIVE_MINORS = {
  'C': 'Am', 'G': 'Em', 'D': 'Bm', 'A': 'F#m', 'E': 'C#m',
  'B': 'G#m', 'F#': 'D#m', 'C#': 'A#m', 'F': 'Dm',
  'A#': 'Gm', 'D#': 'Cm', 'G#': 'Fm'
};
