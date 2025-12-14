/**
 * Audio synthesizer for AetherLingua
 */

import { Token, AudioConfig, StereoBuffer } from './types';
import { Oscillators } from './oscillators';
import { KemeticTokenizer } from './tokenizers/kemetic';

export class AudioSynthesizer {
  // A=110Hz fundamental series (line carriers)
  private static readonly LINE_CARRIERS = [110.0, 138.59, 174.61, 220.0, 277.18, 349.23];

  // Stereo panning patterns
  private static readonly PAN_PATTERNS = [
    [0.5, 0.5],
    [0.65, 0.35],
    [0.35, 0.65],
    [0.7, 0.3],
    [0.3, 0.7],
    [0.55, 0.45]
  ];

  /**
   * Render a single line of text to stereo buffer
   */
  static renderLine(text: string, carrier: number, config: AudioConfig): StereoBuffer {
    const n = Math.floor(config.duration * config.sampleRate);
    const left = new Float32Array(n);
    const right = new Float32Array(n);
    const tokens = KemeticTokenizer.tokenize(text);
    const step = 1.0 / config.sampleRate;

    for (let i = 0; i < n; i++) {
      const t = i * step;
      let signal = Oscillators.sine(carrier, t) * 0.9;

      // FM synthesis based on phoneme classification
      for (const token of tokens) {
        const { modulationFreq, modulationIndex } = KemeticTokenizer.getPhonemeMapping(token.classification);
        if (modulationFreq > 0.0) {
          const depth = carrier * 0.12 * modulationIndex;
          const modulator = Oscillators.sine(modulationFreq, t);
          signal += Oscillators.sine(carrier + depth * modulator, t) * 0.25;
        }
      }

      // Add harmonic enrichment
      signal += Oscillators.harmonics(carrier, t);

      // Special motifs
      if (text.includes('7%')) {
        signal += Oscillators.charityGliss(carrier, t);
      }
      if (text.includes('137')) {
        signal += Oscillators.node137Burst(carrier, t);
      }

      // Apply ADSR envelope
      signal *= Oscillators.adsr(t, config.duration);

      // Stereo panning
      const panIdx = Math.floor((carrier - 100.0) / 40.0) % 6;
      const [lpan, rpan] = this.PAN_PATTERNS[panIdx];
      left[i] = signal * lpan;
      right[i] = signal * rpan;
    }

    return { left, right };
  }

  /**
   * Apply algorithmic reverb (feedback delay network)
   */
  static applyReverb(buffer: Float32Array, sampleRate: number): Float32Array {
    const delays = [
      Math.floor(0.041 * sampleRate),
      Math.floor(0.077 * sampleRate),
      Math.floor(0.139 * sampleRate)
    ];
    const gains = [0.28, 0.18, 0.12];
    const out = new Float32Array(buffer.length);

    for (let i = 0; i < buffer.length; i++) {
      out[i] = buffer[i];
      for (let j = 0; j < 3; j++) {
        const d = delays[j];
        if (i >= d) {
          out[i] += buffer[i - d] * gains[j];
        }
      }
    }

    // Normalize
    let peak = 0.0;
    for (let i = 0; i < out.length; i++) {
      peak = Math.max(peak, Math.abs(out[i]));
    }
    if (peak > 1.0) {
      for (let i = 0; i < out.length; i++) {
        out[i] /= peak;
      }
    }

    return out;
  }

  /**
   * Get line carrier frequency by index
   */
  static getLineCarrier(index: number): number {
    return this.LINE_CARRIERS[index % this.LINE_CARRIERS.length];
  }

  /**
   * Get all line carriers
   */
  static getLineCarriers(): number[] {
    return [...this.LINE_CARRIERS];
  }
}
