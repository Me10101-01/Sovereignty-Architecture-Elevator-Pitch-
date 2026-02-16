/**
 * Audio oscillators for waveform generation
 */

export class Oscillators {
  /**
   * Sine wave oscillator
   */
  static sine(frequency: number, time: number): number {
    return Math.sin(2.0 * Math.PI * frequency * time);
  }

  /**
   * Sawtooth wave oscillator
   */
  static saw(frequency: number, time: number): number {
    const phase = frequency * time - Math.floor(frequency * time);
    return 2.0 * phase - 1.0;
  }

  /**
   * Triangle wave oscillator
   */
  static triangle(frequency: number, time: number): number {
    const phase = frequency * time - Math.floor(frequency * time);
    return 2.0 * Math.abs(2.0 * (phase - Math.floor(phase + 0.5))) - 1.0;
  }

  /**
   * ADSR Envelope generator
   */
  static adsr(time: number, duration: number): number {
    const attack = 0.5;
    const decay = 0.7;
    const sustain = 0.75;
    const release = 1.0;

    if (time < attack) {
      return time / attack;
    }
    if (time < attack + decay) {
      return 1.0 - (1.0 - sustain) * ((time - attack) / decay);
    }
    if (time < duration - release) {
      return sustain;
    }
    if (time < duration) {
      return sustain * (1.0 - ((time - (duration - release)) / release));
    }
    return 0.0;
  }

  /**
   * Harmonic enrichment - adds subharmonic, overtone, and bronze bell harmonics
   */
  static harmonics(carrier: number, time: number): number {
    const sub = this.sine(carrier / 2.0, time) * 0.25;
    const overtone = this.sine(carrier * 2.0, time) * 0.15;
    const bronze = 
      this.sine(carrier * 2.87, time) * 0.06 +
      this.sine(carrier * 3.13, time) * 0.06 +
      this.sine(carrier * 3.41, time) * 0.06;
    return sub + overtone + bronze;
  }

  /**
   * 7% charity glissando motif
   */
  static charityGliss(carrier: number, time: number): number {
    if (time < 1.2) {
      const start = carrier * 1.5;
      const end = carrier * 2.2;
      const freq = start + (time / 1.2) * (end - start);
      return this.triangle(freq, time) * 0.35;
    }
    return 0.0;
  }

  /**
   * Node 137 burst motif
   * Digits 1, 3, 7 → microtonal offsets: 1→+5¢, 3→+18¢, 7→-12¢
   * Combined offset: 5 + 18 - 12 = +11 cents
   */
  static node137Burst(carrier: number, time: number): number {
    if (time < 0.8) {
      const DIGIT_1_CENTS = 5.0;
      const DIGIT_3_CENTS = 18.0;
      const DIGIT_7_CENTS = -12.0;
      const offsetCents = DIGIT_1_CENTS + DIGIT_3_CENTS + DIGIT_7_CENTS;
      const freq = carrier * Math.pow(2.0, offsetCents / 1200.0);
      return this.saw(freq, time) * Math.exp(-time * 6.0) * 0.45;
    }
    return 0.0;
  }
}
