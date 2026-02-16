/**
 * Type definitions for AetherLingua
 */

export type PhonemeClass = 'vowel' | 'voiced' | 'sibilant' | 'stop' | 'nasal' | 'punct';

export interface Token {
  glyph: string;
  classification: PhonemeClass;
}

export interface PhonemeMapping {
  modulationFreq: number;
  modulationIndex: number;
}

export interface AudioConfig {
  sampleRate: number;
  bitDepth: number;
  duration: number;
  seed: number;
}

export interface SynthesizerParams {
  carrier: number;
  time: number;
  tokens: Token[];
  config: AudioConfig;
}

export interface StereoBuffer {
  left: Float32Array;
  right: Float32Array;
}

export interface WaveformGenerator {
  (frequency: number, time: number): number;
}

export type OscillatorType = 'sine' | 'saw' | 'triangle';
