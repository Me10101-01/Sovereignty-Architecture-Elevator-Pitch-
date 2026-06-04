import { CHROMATIC_SCALE, RELATIVE_MINORS, KEY_SIGNATURES } from '../constants/notes.js';

export class CircleEngine {
  /**
   * Generates a 12-note circle via modular semitone stepping.
   * Circle of 5ths  → stepSize = 7  (perfect fifth = 7 semitones)
   * Circle of 4ths  → stepSize = 5  (perfect fourth = 5 semitones)
   */
  static generateCircle(stepSize = 7, startNote = 'C') {
    const circle = [];
    let idx = CHROMATIC_SCALE.indexOf(startNote);
    if (idx === -1) throw new Error(`Invalid starting pitch: "${startNote}"`);

    for (let i = 0; i < 12; i++) {
      circle.push(CHROMATIC_SCALE[idx]);
      idx = (idx + stepSize) % 12;
    }
    return circle;
  }

  static getCircleOfFifths() {
    // C G D A E B F# C# G# D# A# F
    return this.generateCircle(7, 'C');
  }

  static getCircleOfFourths() {
    // C F A# D# G# C# F# B E A D G
    return this.generateCircle(5, 'C');
  }

  /**
   * Returns rich data for each position in the circle, used by CircleVisualizer.
   * @param {'fifths'|'fourths'} type
   */
  static getCircleData(type = 'fifths') {
    const notes = type === 'fifths'
      ? this.getCircleOfFifths()
      : this.getCircleOfFourths();

    return notes.map((note, position) => ({
      position,           // 0-11, clockwise from top
      note,
      relativeMinor: RELATIVE_MINORS[note] ?? null,
      keySignature: KEY_SIGNATURES[note] ?? 0,
      angleDeg: (position * 30) - 90,  // 0° = top (C), clockwise
      angleRad: ((position * 30) - 90) * (Math.PI / 180)
    }));
  }

  /**
   * Returns the notes common to two given circles (intersection).
   */
  static intersection(circleA, circleB) {
    const setB = new Set(circleB);
    return circleA.filter(n => setB.has(n));
  }

  /**
   * Returns the diatonic scale for a given root note (Ionian / major).
   * Steps: W W H W W W H  →  semitone intervals [2,2,1,2,2,2,1]
   */
  static getDiatonicScale(root) {
    const idx = CHROMATIC_SCALE.indexOf(root);
    if (idx === -1) throw new Error(`Invalid root: "${root}"`);
    const intervals = [0, 2, 4, 5, 7, 9, 11];
    return intervals.map(i => CHROMATIC_SCALE[(idx + i) % 12]);
  }
}
