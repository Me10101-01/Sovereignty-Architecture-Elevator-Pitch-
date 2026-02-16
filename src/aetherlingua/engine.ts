/**
 * AetherLingua Main Engine
 * 
 * The Living Glyph Language Engine that treats ancient scripts
 * as executable sonic-cognitive DNA
 */

import { AudioConfig, StereoBuffer } from './types';
import { AudioSynthesizer } from './synthesizer';
import { WavWriter } from './wav-writer';
import { SumerianTokenizer, SumerianGlyph } from './tokenizers/sumerian';
import { Oscillators } from './oscillators';

export class AetherLingua {
  private config: AudioConfig;

  constructor(config?: Partial<AudioConfig>) {
    this.config = {
      sampleRate: config?.sampleRate ?? 48000,
      bitDepth: config?.bitDepth ?? 24,
      duration: config?.duration ?? 8.0,
      seed: config?.seed ?? 1337
    };
  }

  /**
   * Render Kemetic invocation to audio files
   */
  renderKemeticInvocation(lines: string[], outputDir: string = '.'): string[] {
    const buffers: StereoBuffer[] = [];

    for (let i = 0; i < lines.length; i++) {
      const carrier = AudioSynthesizer.getLineCarrier(i);
      const buffer = AudioSynthesizer.renderLine(lines[i], carrier, this.config);
      
      // Apply reverb to both channels
      const reverbLeft = AudioSynthesizer.applyReverb(buffer.left, this.config.sampleRate);
      const reverbRight = AudioSynthesizer.applyReverb(buffer.right, this.config.sampleRate);
      
      buffers.push({ left: reverbLeft, right: reverbRight });
    }

    // Write WAV files
    const filenames = WavWriter.writeMultiple(
      `${outputDir}/aetherlingua_kemetic.wav`,
      buffers,
      this.config.sampleRate
    );

    return filenames;
  }

  /**
   * Render Sumerian cuneiform invocation with percussive transients
   */
  renderSumerianInvocation(glyphText: string, outputFile: string): string {
    const glyphs = SumerianTokenizer.tokenize(glyphText);
    const n = Math.floor(this.config.duration * this.config.sampleRate);
    const left = new Float32Array(n);
    const right = new Float32Array(n);
    const step = 1.0 / this.config.sampleRate;

    let timeOffset = 0.0;
    const glyphDuration = this.config.duration / glyphs.length;

    for (const glyph of glyphs) {
      const strikeTimings = SumerianTokenizer.generateRhythmicPattern(
        glyph.wedgeCount,
        glyphDuration
      );

      for (const strikeTime of strikeTimings) {
        const absoluteTime = timeOffset + strikeTime;
        const startSample = Math.floor(absoluteTime * this.config.sampleRate);

        // Render wedge strike
        for (let i = 0; i < n && startSample + i < n; i++) {
          const t = i * step;
          const strike = SumerianTokenizer.generateWedgeStrike(
            t,
            glyph.percussiveIntensity,
            glyph.bronzeBellFreq
          );

          // Add to buffer with spatial positioning
          const pan = 0.5 + Math.sin(absoluteTime * 0.5) * 0.3;
          left[startSample + i] += strike * (1.0 - pan);
          right[startSample + i] += strike * pan;
        }
      }

      timeOffset += glyphDuration;
    }

    // Apply reverb
    const reverbLeft = AudioSynthesizer.applyReverb(left, this.config.sampleRate);
    const reverbRight = AudioSynthesizer.applyReverb(right, this.config.sampleRate);

    // Write file
    WavWriter.write(outputFile, { left: reverbLeft, right: reverbRight }, this.config.sampleRate);

    return outputFile;
  }

  /**
   * Render hybrid invocation (Kemetic + Sumerian)
   */
  renderHybridInvocation(
    kemeticLines: string[],
    sumerianGlyphs: string,
    outputFile: string
  ): string {
    const n = Math.floor(this.config.duration * this.config.sampleRate);
    const left = new Float32Array(n);
    const right = new Float32Array(n);

    // Render Kemetic base layer
    for (let i = 0; i < kemeticLines.length; i++) {
      const carrier = AudioSynthesizer.getLineCarrier(i);
      const buffer = AudioSynthesizer.renderLine(kemeticLines[i], carrier, this.config);
      
      // Mix into main buffer with bounds checking
      const bufferLength = Math.min(n, buffer.left.length, buffer.right.length);
      for (let j = 0; j < bufferLength; j++) {
        left[j] += buffer.left[j] * 0.6;
        right[j] += buffer.right[j] * 0.6;
      }
    }

    // Add Sumerian percussive layer
    const glyphs = SumerianTokenizer.tokenize(sumerianGlyphs);
    const step = 1.0 / this.config.sampleRate;
    let timeOffset = 0.0;
    const glyphDuration = this.config.duration / glyphs.length;

    for (const glyph of glyphs) {
      const strikeTimings = SumerianTokenizer.generateRhythmicPattern(
        glyph.wedgeCount,
        glyphDuration
      );

      for (const strikeTime of strikeTimings) {
        const absoluteTime = timeOffset + strikeTime;
        const startSample = Math.floor(absoluteTime * this.config.sampleRate);

        for (let i = 0; i < n && startSample + i < n; i++) {
          const t = i * step;
          const strike = SumerianTokenizer.generateWedgeStrike(
            t,
            glyph.percussiveIntensity * 0.4,
            glyph.bronzeBellFreq
          );

          const pan = 0.5 + Math.sin(absoluteTime * 0.5) * 0.3;
          left[startSample + i] += strike * (1.0 - pan);
          right[startSample + i] += strike * pan;
        }
      }

      timeOffset += glyphDuration;
    }

    // Apply reverb
    const reverbLeft = AudioSynthesizer.applyReverb(left, this.config.sampleRate);
    const reverbRight = AudioSynthesizer.applyReverb(right, this.config.sampleRate);

    // Write file
    WavWriter.write(outputFile, { left: reverbLeft, right: reverbRight }, this.config.sampleRate);

    return outputFile;
  }

  /**
   * Get cryptographic hash of rendered audio (proof of invocation)
   */
  async getAudioHash(buffer: StereoBuffer): Promise<string> {
    const { createHash } = await import('crypto');
    const hash = createHash('sha256');
    
    // Hash the audio data
    const leftBuffer = Buffer.from(buffer.left.buffer);
    const rightBuffer = Buffer.from(buffer.right.buffer);
    hash.update(leftBuffer);
    hash.update(rightBuffer);
    
    return hash.digest('hex');
  }

  /**
   * Generate speculative path seed from audio hash
   */
  generateVFASPSeed(audioHash: string): number {
    let seed = 0;
    for (let i = 0; i < audioHash.length; i += 2) {
      seed ^= parseInt(audioHash.substring(i, i + 2), 16);
    }
    return seed;
  }
}
