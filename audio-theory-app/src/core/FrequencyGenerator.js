import { CHROMATIC_SCALE } from '../constants/notes.js';

export class FrequencyGenerator {
  /**
   * 12-TET equal temperament: f(n) = 440 * 2^((n - 49) / 12)
   * @param {number} keyNumber  1..88
   */
  static computeFrequency(keyNumber) {
    if (keyNumber < 1 || keyNumber > 88) {
      throw new RangeError(`Key ${keyNumber} out of range [1..88]`);
    }
    return parseFloat((440 * Math.pow(2, (keyNumber - 49) / 12)).toFixed(3));
  }

  /**
   * Generates the complete 88-key manifest.
   * @returns {Array<{keyNumber, midiNumber, note, octave, frequencyHz, isWhite}>}
   */
  static generate88KeyManifest() {
    const manifest = [];
    let chromaticIndex = CHROMATIC_SCALE.indexOf('A');  // A0 = key 1
    let currentOctave = 0;
    const WHITE_NOTES = new Set(['C', 'D', 'E', 'F', 'G', 'A', 'B']);

    for (let n = 1; n <= 88; n++) {
      const noteName = CHROMATIC_SCALE[chromaticIndex];
      manifest.push({
        keyNumber:    n,
        midiNumber:   n + 20,          // A0 = MIDI 21
        note:         noteName,
        octave:       currentOctave,
        label:        `${noteName}${currentOctave}`,
        frequencyHz:  this.computeFrequency(n),
        isWhite:      WHITE_NOTES.has(noteName)
      });

      if (noteName === 'B') currentOctave++;
      chromaticIndex = (chromaticIndex + 1) % 12;
    }
    return manifest;
  }

  /**
   * Looks up a specific note+octave in the manifest.
   * @param {string} note   e.g. 'A'
   * @param {number} octave e.g. 4
   */
  static getKey(note, octave) {
    // Lazy-init cache
    if (!this._manifest) this._manifest = this.generate88KeyManifest();
    return this._manifest.find(k => k.note === note && k.octave === octave) ?? null;
  }

  /**
   * Returns all 12 keys in one octave (C-to-B) for the given octave number.
   */
  static getOctave(octave) {
    if (!this._manifest) this._manifest = this.generate88KeyManifest();
    return this._manifest.filter(k => k.octave === octave);
  }
}
