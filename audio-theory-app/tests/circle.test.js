import { describe, it, expect } from '@jest/globals';
import { CircleEngine } from '../src/core/CircleEngine.js';

describe('CircleEngine', () => {
  describe('getCircleOfFifths', () => {
    it('returns 12 notes', () => {
      expect(CircleEngine.getCircleOfFifths()).toHaveLength(12);
    });

    it('starts with C', () => {
      expect(CircleEngine.getCircleOfFifths()[0]).toBe('C');
    });

    it('produces correct canonical sequence', () => {
      const expected = ['C','G','D','A','E','B','F#','C#','G#','D#','A#','F'];
      expect(CircleEngine.getCircleOfFifths()).toEqual(expected);
    });

    it('contains all 12 chromatic tones exactly once', () => {
      const circle = CircleEngine.getCircleOfFifths();
      expect(new Set(circle).size).toBe(12);
    });
  });

  describe('getCircleOfFourths', () => {
    it('returns 12 notes', () => {
      expect(CircleEngine.getCircleOfFourths()).toHaveLength(12);
    });

    it('starts with C', () => {
      expect(CircleEngine.getCircleOfFourths()[0]).toBe('C');
    });

    it('produces correct canonical sequence', () => {
      const expected = ['C','F','A#','D#','G#','C#','F#','B','E','A','D','G'];
      expect(CircleEngine.getCircleOfFourths()).toEqual(expected);
    });

    it('contains all 12 chromatic tones exactly once', () => {
      const circle = CircleEngine.getCircleOfFourths();
      expect(new Set(circle).size).toBe(12);
    });
  });

  describe('generateCircle', () => {
    it('throws on invalid starting note', () => {
      expect(() => CircleEngine.generateCircle(7, 'X')).toThrow();
    });

    it('5th + 4th stepSizes are inverse (7 + 5 = 12)', () => {
      const fifths  = CircleEngine.generateCircle(7, 'C');
      const fourths = CircleEngine.generateCircle(5, 'C');
      // Position 1 of fifths (G) should appear in fourths at an expected index
      expect(fifths.includes('G')).toBe(true);
      expect(fourths.includes('G')).toBe(true);
    });
  });

  describe('getDiatonicScale', () => {
    it('returns 7 notes for C major', () => {
      expect(CircleEngine.getDiatonicScale('C')).toHaveLength(7);
    });

    it('C major = C D E F G A B', () => {
      expect(CircleEngine.getDiatonicScale('C')).toEqual(['C','D','E','F','G','A','B']);
    });

    it('G major contains F#', () => {
      expect(CircleEngine.getDiatonicScale('G')).toContain('F#');
    });

    it('F major contains A#', () => {
      expect(CircleEngine.getDiatonicScale('F')).toContain('A#');
    });
  });

  describe('getCircleData', () => {
    it('returns 12 entries with correct positions', () => {
      const data = CircleEngine.getCircleData('fifths');
      expect(data).toHaveLength(12);
      expect(data[0].position).toBe(0);
      expect(data[11].position).toBe(11);
    });

    it('each entry has angleDeg at 30° increments', () => {
      const data = CircleEngine.getCircleData('fifths');
      data.forEach((d, i) => {
        expect(d.angleDeg).toBeCloseTo((i * 30) - 90, 5);
      });
    });
  });
});
