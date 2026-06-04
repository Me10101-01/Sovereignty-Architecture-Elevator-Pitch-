import { describe, it, expect } from '@jest/globals';
import { FrequencyGenerator } from '../src/core/FrequencyGenerator.js';

describe('FrequencyGenerator', () => {
  describe('computeFrequency', () => {
    it('key 49 (A4) = 440 Hz', () => {
      expect(FrequencyGenerator.computeFrequency(49)).toBe(440.000);
    });

    it('key 1 (A0) ≈ 27.5 Hz', () => {
      expect(FrequencyGenerator.computeFrequency(1)).toBeCloseTo(27.5, 1);
    });

    it('key 40 (Middle C / C4) ≈ 261.626 Hz', () => {
      expect(FrequencyGenerator.computeFrequency(40)).toBeCloseTo(261.626, 2);
    });

    it('key 88 (C8) ≈ 4186.009 Hz', () => {
      expect(FrequencyGenerator.computeFrequency(88)).toBeCloseTo(4186.009, 1);
    });

    it('each octave doubles the frequency (A4 → A5)', () => {
      const a4 = FrequencyGenerator.computeFrequency(49);   // A4
      const a5 = FrequencyGenerator.computeFrequency(61);   // A5
      expect(a5 / a4).toBeCloseTo(2.0, 4);
    });

    it('throws RangeError for key 0', () => {
      expect(() => FrequencyGenerator.computeFrequency(0)).toThrow(RangeError);
    });

    it('throws RangeError for key 89', () => {
      expect(() => FrequencyGenerator.computeFrequency(89)).toThrow(RangeError);
    });

    it('semitone ratio is 2^(1/12)', () => {
      const f1 = FrequencyGenerator.computeFrequency(49);
      const f2 = FrequencyGenerator.computeFrequency(50);
      expect(f2 / f1).toBeCloseTo(Math.pow(2, 1 / 12), 4);
    });
  });

  describe('generate88KeyManifest', () => {
    const manifest = FrequencyGenerator.generate88KeyManifest();

    it('generates exactly 88 entries', () => {
      expect(manifest).toHaveLength(88);
    });

    it('first key is A0', () => {
      expect(manifest[0].note).toBe('A');
      expect(manifest[0].octave).toBe(0);
      expect(manifest[0].label).toBe('A0');
    });

    it('last key is C8', () => {
      expect(manifest[87].note).toBe('C');
      expect(manifest[87].octave).toBe(8);
      expect(manifest[87].label).toBe('C8');
    });

    it('key 49 is A4 at 440 Hz', () => {
      const k = manifest[48];   // 0-indexed
      expect(k.note).toBe('A');
      expect(k.octave).toBe(4);
      expect(k.frequencyHz).toBe(440.000);
    });

    it('MIDI numbers start at 21 (A0 = MIDI 21)', () => {
      expect(manifest[0].midiNumber).toBe(21);
    });

    it('MIDI numbers increment by 1 per key', () => {
      for (let i = 1; i < manifest.length; i++) {
        expect(manifest[i].midiNumber).toBe(manifest[i - 1].midiNumber + 1);
      }
    });

    it('has correct count of white and black keys', () => {
      const whites = manifest.filter(k => k.isWhite).length;
      const blacks = manifest.filter(k => !k.isWhite).length;
      expect(whites).toBe(52);
      expect(blacks).toBe(36);
    });

    it('frequencies are strictly increasing', () => {
      for (let i = 1; i < manifest.length; i++) {
        expect(manifest[i].frequencyHz).toBeGreaterThan(manifest[i - 1].frequencyHz);
      }
    });
  });

  describe('getKey', () => {
    it('returns A4 by note and octave', () => {
      const key = FrequencyGenerator.getKey('A', 4);
      expect(key).not.toBeNull();
      expect(key.frequencyHz).toBe(440.000);
      expect(key.keyNumber).toBe(49);
    });

    it('returns null for out-of-range note/octave combo', () => {
      expect(FrequencyGenerator.getKey('C', 9)).toBeNull();
    });
  });
});
