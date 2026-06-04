/**
 * SAGCO SynthEngine — Web Audio API ADSR synthesizer
 * Supports up to maxPolyphony simultaneous voices.
 * Each voice: OscillatorNode → GainNode (ADSR) → MasterGain → Destination
 */

const DEFAULTS = {
  attack:      0.012,
  decay:       0.15,
  sustain:     0.65,
  release:     0.35,
  masterVolume: 0.5,
  maxPolyphony: 10,
  waveType:    'sine'
};

export class SynthEngine {
  constructor(settings = {}) {
    this.cfg = { ...DEFAULTS, ...settings };
    this.ctx         = null;
    this.masterGain  = null;
    this._voices     = new Map();  // keyNumber → { osc, gain, startTime }
    this.waveType    = this.cfg.waveType;
  }

  // ── Lifecycle ──────────────────────────────────────────────────────────────

  init() {
    if (this.ctx) return;
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.setValueAtTime(this.cfg.masterVolume, this.ctx.currentTime);
    this.masterGain.connect(this.ctx.destination);
  }

  _resume() {
    if (this.ctx.state === 'suspended') this.ctx.resume();
  }

  // ── Playback ───────────────────────────────────────────────────────────────

  /**
   * Triggers a note on with full ADSR envelope.
   * @param {number} keyNumber  1..88
   * @param {number} frequency  Hz
   * @param {string} [wave]     oscillator type override
   */
  noteOn(keyNumber, frequency, wave = this.waveType) {
    if (!this.ctx) this.init();
    this._resume();
    this.noteOff(keyNumber);   // retrigger if held

    // Polyphony cap: evict oldest voice
    if (this._voices.size >= this.cfg.maxPolyphony) {
      const oldest = this._voices.keys().next().value;
      this.noteOff(oldest);
    }

    const now = this.ctx.currentTime;
    const { attack, decay, sustain } = this.cfg;

    const osc  = this.ctx.createOscillator();
    const gain = this.ctx.createGain();

    osc.type = wave;
    osc.frequency.setValueAtTime(frequency, now);

    // ADSR: 0 → peak (attack) → sustain level (decay)
    gain.gain.setValueAtTime(0, now);
    gain.gain.linearRampToValueAtTime(1.0, now + attack);
    gain.gain.linearRampToValueAtTime(sustain, now + attack + decay);

    osc.connect(gain);
    gain.connect(this.masterGain);
    osc.start(now);

    this._voices.set(keyNumber, { osc, gain, startTime: now });
  }

  /**
   * Triggers note off — applies release envelope then cleans up.
   * @param {number} keyNumber
   */
  noteOff(keyNumber) {
    const voice = this._voices.get(keyNumber);
    if (!voice) return;

    const now     = this.ctx.currentTime;
    const release = this.cfg.release;
    const { osc, gain } = voice;

    gain.gain.cancelScheduledValues(now);
    gain.gain.setValueAtTime(gain.gain.value, now);
    gain.gain.linearRampToValueAtTime(0, now + release);
    osc.stop(now + release + 0.01);

    this._voices.delete(keyNumber);
  }

  /** Silence all voices immediately. */
  allNotesOff() {
    for (const key of [...this._voices.keys()]) this.noteOff(key);
  }

  // ── Controls ───────────────────────────────────────────────────────────────

  setWaveType(type) {
    const valid = ['sine', 'square', 'sawtooth', 'triangle'];
    if (!valid.includes(type)) throw new Error(`Unknown wave type: ${type}`);
    this.waveType = type;
  }

  setMasterVolume(value) {
    const v = Math.max(0, Math.min(1, value));
    if (this.masterGain) {
      this.masterGain.gain.setValueAtTime(v, this.ctx.currentTime);
    }
    this.cfg.masterVolume = v;
  }

  setADSR({ attack, decay, sustain, release } = {}) {
    if (attack  !== undefined) this.cfg.attack  = Math.max(0.001, attack);
    if (decay   !== undefined) this.cfg.decay   = Math.max(0.001, decay);
    if (sustain !== undefined) this.cfg.sustain = Math.max(0, Math.min(1, sustain));
    if (release !== undefined) this.cfg.release = Math.max(0.001, release);
  }

  getADSR() {
    const { attack, decay, sustain, release } = this.cfg;
    return { attack, decay, sustain, release };
  }

  isPlaying(keyNumber) {
    return this._voices.has(keyNumber);
  }
}

// Singleton instance used by UI components
export const synth = new SynthEngine();
